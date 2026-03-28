# LM Studio (Qwen3.5-9B) LLM 클라이언트
# LM Studio가 없으면 기본 해설로 대체

import urllib.request
import urllib.error
import json
from typing import Optional

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen3.5-9b"
TIMEOUT = 30


def call_llm(prompt: str) -> Optional[str]:
    """
    LM Studio API 호출 (OpenAI 호환 형식)
    실패 시 None 반환
    """
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "당신은 사주명리학(四柱命理學) 전문가입니다. "
                    "사용자의 사주 8자를 분석하여 한국어로 친절하고 자세하게 해설해주세요. "
                    "긍정적이고 건설적인 관점으로 해설하되, 주의할 점도 알려주세요."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": False,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LM_STUDIO_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception:
        return None


def generate_saju_interpretation(saju_data: dict, name: str) -> str:
    """
    사주 데이터를 기반으로 LLM 해설 생성
    LLM 호출 실패 시 기본 해설 반환
    """
    pillars = saju_data["pillars"]
    ohaeng = saju_data["ohaeng"]
    ilgan = saju_data["ilgan"]
    ilgan_ohaeng = saju_data["ilgan_ohaeng"]
    animal = saju_data["animal"]

    # 오행 분포 문자열
    ohaeng_str = ", ".join(
        f"{k}({OHAENG_NAMES[k]}): {v['count']}개"
        for k, v in ohaeng.items()
        if v["count"] > 0
    )

    # 사주 표기
    saju_str = " ".join([
        f"{pillars['year']['gan_hanja']}{pillars['year']['ji_hanja']}",
        f"{pillars['month']['gan_hanja']}{pillars['month']['ji_hanja']}",
        f"{pillars['day']['gan_hanja']}{pillars['day']['ji_hanja']}",
        f"{pillars['hour']['gan_hanja']}{pillars['hour']['ji_hanja']}",
    ])

    prompt = f"""
{name}님의 사주 8자: {saju_str}

- 연주(年柱): {pillars['year']['gan_hanja']}{pillars['year']['ji_hanja']} ({pillars['year']['gan']}{pillars['year']['ji']})
- 월주(月柱): {pillars['month']['gan_hanja']}{pillars['month']['ji_hanja']} ({pillars['month']['gan']}{pillars['month']['ji']})
- 일주(日柱): {pillars['day']['gan_hanja']}{pillars['day']['ji_hanja']} ({pillars['day']['gan']}{pillars['day']['ji']}) ← 일간(나 자신)
- 시주(時柱): {pillars['hour']['gan_hanja']}{pillars['hour']['ji_hanja']} ({pillars['hour']['gan']}{pillars['hour']['ji']})

오행 분포: {ohaeng_str}
일간 오행: {ilgan_ohaeng}({ilgan})
띠: {animal}띠

위 사주를 분석하여 다음 항목으로 해설해주세요:
1. 전체적인 사주 특성 (3~4문장)
2. 성격과 적성 (2~3문장)
3. 오행 균형과 용신(用神) 제안 (2~3문장)
4. 올해 운세 (2~3문장)
5. 주의할 점 (1~2문장)
"""

    result = call_llm(prompt)
    if result:
        return result

    # LLM 실패 시 기본 해설 생성
    return _default_interpretation(name, saju_data)


def _default_interpretation(name: str, saju_data: dict) -> str:
    """LLM 없이 기본 해설 생성"""
    ilgan = saju_data["ilgan"]
    ilgan_ohaeng = saju_data["ilgan_ohaeng"]
    animal = saju_data["animal"]
    ohaeng = saju_data["ohaeng"]

    # 가장 많은 오행
    max_ohaeng = max(ohaeng.items(), key=lambda x: x[1]["count"])[0]
    # 가장 적은 오행
    min_ohaeng = min(ohaeng.items(), key=lambda x: x[1]["count"])[0]

    ohaeng_traits = {
        "목": "성장과 발전을 추구하며, 창의적이고 진취적인 성향",
        "화": "열정적이고 밝은 에너지를 가지며, 사교적이고 표현력이 풍부한 성향",
        "토": "안정적이고 신중하며, 신뢰감을 주는 든든한 성향",
        "금": "원칙을 중시하고 결단력이 강하며, 완벽을 추구하는 성향",
        "수": "지혜롭고 유연하며, 깊은 사고력과 적응력을 가진 성향",
    }

    return f"""
{name}님의 사주 분석 결과입니다.

**전체적인 사주 특성**
일간이 {ilgan}({ilgan_ohaeng})인 {name}님은 {ohaeng_traits.get(ilgan_ohaeng, '다재다능한')}을 보입니다. {animal}띠로 태어나 그 특성이 사주에 잘 녹아있습니다.

**성격과 적성**
{max_ohaeng} 기운이 강하여 관련 분야에서 두각을 나타낼 수 있습니다. 타인과의 협력을 통해 더 큰 성과를 이룰 수 있는 기질을 가지고 있습니다.

**오행 균형**
{max_ohaeng} 기운이 상대적으로 강하고, {min_ohaeng} 기운이 약합니다. {min_ohaeng}에 해당하는 색상이나 방향을 생활에 활용하면 균형을 맞추는 데 도움이 됩니다.

**올해 운세**
전반적으로 자신의 강점을 살리는 한 해가 될 것입니다. 새로운 도전을 두려워하지 말고, 꾸준한 노력으로 목표를 향해 나아가세요.

**주의할 점**
너무 서두르지 말고 단계적으로 계획을 실행하는 것이 중요합니다. 건강 관리에도 주의를 기울이세요.

※ 이 해설은 LM Studio(Qwen3.5-9B)가 연결되지 않아 기본 해설로 제공됩니다.
"""


OHAENG_NAMES = {"목": "木", "화": "火", "토": "土", "금": "金", "수": "水"}
