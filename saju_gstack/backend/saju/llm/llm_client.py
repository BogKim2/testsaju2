# LM Studio OpenAI 호환 — JSON만 해석 (사주 계산 금지)

import json
import os
import time
import urllib.request
from typing import Any, Optional

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
PROMPT_VERSION = "v2"

# 기본 HTTP 타임아웃(초). 생성 토큰이 크면 응답이 길어질 수 있음
_DEFAULT_LLM_TIMEOUT_SEC = 300
# 기본 생성 토큰 (LLM_MAX_TOKENS 미설정 시). 추론+본문이 길어질 수 있어 넉넉히 둠
_DEFAULT_MAX_TOKENS = 20000
# env 로 LLM_MAX_TOKENS 를 줄 때 이 값 미만이면 경고(한 번만)
_RECOMMENDED_MIN_MAX_TOKENS = 2048

# LLM_MAX_TOKENS 가 비정상적으로 낮을 때 경고 중복 방지
_low_max_tokens_warned = False

# LM Studio에 로드한 모델 id (OpenAI 호환 요청의 "model" 필드)
_DEFAULT_MODEL_NAME = "nvidia/nemotron-3-nano-4b"


def _env_trim(name: str, default: str) -> str:
    # 환경변수 읽기: 앞뒤 공백 제거
    raw = os.getenv(name, default)
    return raw.strip() if raw else default


def get_model_name() -> str:
    # 환경변수 LLM_MODEL_NAME 으로 다른 모델을 쓸 수 있음
    m = _env_trim("LLM_MODEL_NAME", _DEFAULT_MODEL_NAME)
    return m if m else _DEFAULT_MODEL_NAME


def _use_qwen_thinking_controls() -> bool:
    # Qwen 전용: /no_think, chat_template_kwargs — 다른 모델에는 보내지 않음
    return "qwen" in get_model_name().lower()


def _should_skip_llm() -> bool:
    # SAJU_SKIP_LLM=1 이면 LM 호출 없이 규칙 기반 해설만 사용
    v = _env_trim("SAJU_SKIP_LLM", "").lower()
    return v in ("1", "true", "yes", "on")


def _llm_timeout_sec() -> int:
    # LLM HTTP 읽기 제한(초). 너무 짧거나 길면 클램프
    raw = _env_trim("LLM_TIMEOUT_SEC", str(_DEFAULT_LLM_TIMEOUT_SEC))
    try:
        n = int(raw)
    except ValueError:
        return _DEFAULT_LLM_TIMEOUT_SEC
    if n < 5:
        return 5
    if n > 900:
        return 900
    return n


def _default_max_tokens_for_model() -> int:
    # LLM_MAX_TOKENS 를 안 주면 동일 기본값 (Qwen 추론+한국어 본문 여유)
    return _DEFAULT_MAX_TOKENS


def get_llm_max_tokens_env_raw() -> str:
    # uvicorn 프로세스가 실제로 보는 값(진단용). 비어 있으면 기본값이 적용됨
    v = os.getenv("LLM_MAX_TOKENS", "")
    return str(v).strip() if v is not None else ""


def get_effective_max_tokens() -> int:
    # 요청 JSON 의 max_tokens 와 동일
    return _max_tokens()


def _max_tokens() -> int:
    # 생성 토큰 상한 (환경변수 LLM_MAX_TOKENS 가 있으면 우선)
    global _low_max_tokens_warned
    raw = os.getenv("LLM_MAX_TOKENS", "")
    if raw is None or not str(raw).strip():
        return _default_max_tokens_for_model()
    try:
        n = int(str(raw).strip())
    except ValueError:
        return _default_max_tokens_for_model()
    if n < 128:
        n = 128
    if n > 262144:
        n = 262144
    # 로그에 768 이 찍히면 대부분 여기서 env 가 설정된 경우임
    if n < _RECOMMENDED_MIN_MAX_TOKENS and not _low_max_tokens_warned:
        print(
            f"[saju-gstack] 경고: LLM_MAX_TOKENS={n} (env raw={raw!r}) — "
            f"추론+한국어 본문에 부족할 수 있습니다. "
            f"unset 하면 기본 {_DEFAULT_MAX_TOKENS} 또는 env 를 {_RECOMMENDED_MIN_MAX_TOKENS} 이상 권장."
        )
        _low_max_tokens_warned = True
    return n


def _enable_thinking() -> bool:
    # Qwen3 추론(thinking) 채널. 기본은 끔 — 한국어 본문이 message.content에 오도록 함
    v = _env_trim("LLM_ENABLE_THINKING", "0").lower()
    return v in ("1", "true", "yes", "on")


def _assistant_text_from_message(msg: dict[str, Any]) -> Optional[str]:
    # 사용자에게 보이는 것은 OpenAI 호환 message.content 뿐이다.
    # reasoning_content는 영어 "Thinking Process"일 수 있어 화면에 쓰지 않는다(비면 규칙 기반 폴백).
    c = msg.get("content")
    if c is None:
        return None
    text = str(c).strip()
    return text if text else None


def _is_english_thinking_in_content(text: str) -> bool:
    # Qwen이 content에 영어 추론만 넣는 경우 — 한국어 섹션이 없으면 폴백한다
    if "### 1." in text and ("한줄" in text or "요약" in text):
        return False
    if "### 2." in text and "전체" in text:
        return False
    head = text.lstrip()[:800].lower()
    if head.startswith("thinking process"):
        return True
    if "thinking process:" in head[:250]:
        return True
    if "**analyze the request**" in head:
        return True
    if "**analyze the input json**" in head:
        return True
    if "**drafting content**" in head:
        return True
    return False


def _refine_llm_markdown(text: str) -> Optional[str]:
    # LLM 원문에서 앞부분 영어 추론을 잘라내고, 첫 정식 섹션(### 1. …)부터만 남긴다
    t = text.strip()
    if not t:
        return None
    needles = (
        "### 1. 한줄",
        "### 1.",
        "### 1 ",
        "## 1. 한줄",
        "## 1.",
    )
    best = -1
    for n in needles:
        i = t.find(n)
        if i >= 0 and (best < 0 or i < best):
            best = i
    if best > 0:
        t = t[best:].strip()
        print("[saju-gstack] Refined LLM: removed prefix before first section header")
    if best < 0 and len(t) < 30:
        return None
    if len(t) < 25:
        return None
    return t


SYSTEM_PROMPT_STRICT_JSON = """You are a Korean saju interpretation expert.

IMPORTANT RULES:
- You MUST NOT calculate saju or stems/branches.
- You ONLY interpret the given JSON.
- Do NOT invent missing data.
- Be consistent and structured.
- Section 6 MUST match year_fortune: use annual_pillar and year_stem_ten_god_vs_day_master exactly as given. Do not contradict target_year.
- Write the FINAL answer in Korean in the normal assistant message body (the user-visible reply). Do not leave the main reply empty.
- NEVER write "Thinking Process", "Analyze the Request", or English step-by-step drafts. Start directly with section ### 1. 한줄 요약 in Korean.

Output in KOREAN with these sections:
### 1. 한줄 요약
### 2. 전체 성향
### 3. 오행 분석
- 부족한 요소
- 과한 요소
- 균형 평가
### 4. 십성 해석
### 5. 영역별 운세
- 연애 / 재물 / 직업 / 건강
### 6. (NNNN년 운세 요약 — NNNN is year_fortune.target_year from JSON)

Tone: professional, soft Korean, no exaggeration, prefer \"경향\" over absolute claims.
Keep under 800 words."""


def call_llm_strict(system: str, user: str) -> Optional[str]:
    # LM Studio에 POST 요청을 보내고 assistant 텍스트만 반환한다
    timeout_sec = _llm_timeout_sec()
    max_tokens = _max_tokens()
    model_id = get_model_name()
    # 추론 끄기: Qwen 전용(LM Studio chat_template_kwargs + /no_think). Nemotron 등에는 보내지 않음
    system_for_request = system
    if not _enable_thinking() and _use_qwen_thinking_controls():
        system_for_request = "/no_think\n\n" + system
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_for_request},
            {"role": "user", "content": user},
        ],
        "temperature": 0.45,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if not _enable_thinking() and _use_qwen_thinking_controls():
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    t0 = time.time()
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LM_STUDIO_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            ch0 = result["choices"][0]
            msg = ch0["message"]
            finish = ch0.get("finish_reason")
            if finish == "length":
                print(
                    "[saju-gstack] LLM finish_reason=length (max_tokens 소진). "
                    "추론만 길면 content가 비고 잘립니다. LLM_MAX_TOKENS 를 늘리거나 LM Studio에서 thinking 끄기."
                )
            raw = _assistant_text_from_message(msg)
    except Exception:
        elapsed = time.time() - t0
        print(f"[saju-gstack] LLM call failed after {elapsed:.2f}s (timeout={timeout_sec}s)")
        return None
    elapsed = time.time() - t0
    print(
        f"[saju-gstack] LLM call ok in {elapsed:.2f}s "
        f"(model={model_id}, timeout={timeout_sec}s, max_tokens={max_tokens})"
    )
    if not raw:
        return None
    refined = _refine_llm_markdown(raw)
    if not refined:
        print("[saju-gstack] LLM refine yielded empty; using rule-based Korean fallback")
        return None
    if _is_english_thinking_in_content(refined):
        print("[saju-gstack] LLM text still looks like English thinking; using rule-based Korean fallback")
        return None
    return refined


def generate_interpretation_from_strict_json(
    strict_payload: dict, display_name: str = ""
) -> str:
    # 엄격 JSON을 사용자 메시지로 넣어 해석을 요청한다
    if _should_skip_llm():
        print("[saju-gstack] SAJU_SKIP_LLM set: using rule-based interpretation only")
        return _default_interpretation_strict(strict_payload, display_name)

    user_text = (
        "The following JSON is the only source of truth. "
        "Do not add stems, branches, or counts not present in it.\n\n"
        + json.dumps(strict_payload, ensure_ascii=False, indent=2)
    )
    if display_name:
        user_text = f"이름(참고만): {display_name}\n\n" + user_text

    result = call_llm_strict(SYSTEM_PROMPT_STRICT_JSON, user_text)
    if result:
        return result
    return _default_interpretation_strict(strict_payload, display_name)


def _default_interpretation_strict(strict_payload: dict, display_name: str) -> str:
    s = strict_payload.get("saju", {})
    el = strict_payload.get("elements", {})
    tg = strict_payload.get("ten_gods", [])
    dm = strict_payload.get("day_master", "")
    strength = strict_payload.get("strength", "")
    yf = strict_payload.get("year_fortune") or {}
    ty = yf.get("target_year", 0)
    ap = yf.get("annual_pillar") or {}
    yg = yf.get("year_stem_ten_god_vs_day_master", "")
    label = display_name.strip() if display_name else "사용자"
    pairs = " / ".join(
        [
            f"연 {s.get('year', {}).get('stem', '')}{s.get('year', {}).get('branch', '')}",
            f"월 {s.get('month', {}).get('stem', '')}{s.get('month', {}).get('branch', '')}",
            f"일 {s.get('day', {}).get('stem', '')}{s.get('day', {}).get('branch', '')}",
            f"시 {s.get('hour', {}).get('stem', '')}{s.get('hour', {}).get('branch', '')}",
        ]
    )
    return f"""### 1. 한줄 요약
{label}님의 일간은 **{dm}**이며, 전체적으로 **{strength}** 흐름으로 볼 수 있습니다.

### 2. 전체 성향
제공된 사주 구조({pairs})를 바탕으로, 성향은 경향적으로 해석할 수 있습니다. 단정적 판단은 피합니다.

### 3. 오행 분석
- 목/화/토/금/수 개수: wood={el.get('wood', 0)}, fire={el.get('fire', 0)}, earth={el.get('earth', 0)}, metal={el.get('metal', 0)}, water={el.get('water', 0)}
- 부족·과다는 위 숫자 비교로 생활 균형을 참고하세요.

### 4. 십성 해석
천간 십성(연·월·일·시): {', '.join(tg)}

### 5. 영역별 운세
- 연애: 관계는 소통과 리듬 조절이 경향에 영향을 줍니다.
- 재물: 수입·지출의 균형을 주기적으로 점검하는 것이 좋습니다.
- 직업: 강점을 살리는 역할에서 만족도가 높아지는 경향이 있습니다.
- 건강: 생활 패턴과 휴식의 균형을 유지하세요.

### 6. {ty}년 운세 요약
엔진 규칙: 해당 연도 연주는 **{ap.get("stem", "")}{ap.get("branch", "")}**, 일간 대비 연간 십성은 **{yg}** 입니다. 이 수치와 모순되지 않게 경향만 서술합니다.

※ LM Studio에 연결할 수 없거나, 모델이 본문(content)을 비운 경우 엔진 JSON만으로 기본 해설을 제공합니다.
"""
