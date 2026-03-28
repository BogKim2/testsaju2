import { useState } from "react";

type ApiRes = {
  ok: boolean;
  saju: Record<string, { stem: string; branch: string }>;
  elements: Record<string, number>;
  ten_gods: string[];
  day_master: string;
  strength: string;
  year_fortune: {
    target_year: number;
    annual_pillar: { stem: string; branch: string };
    year_stem_ten_god_vs_day_master: string;
  };
  interpretation: { markdown: string; model: string; prompt_version: string };
  meta: {
    warnings?: string[];
    timezone?: string;
    location?: string | null;
    target_year?: number;
    datetime_policy?: string;
  };
};

const EL_KEYS = ["wood", "fire", "earth", "metal", "water"] as const;
const EL_LABEL: Record<(typeof EL_KEYS)[number], string> = {
  wood: "목",
  fire: "화",
  earth: "토",
  metal: "금",
  water: "수",
};
const EL_COLOR: Record<(typeof EL_KEYS)[number], string> = {
  wood: "#22c55e",
  fire: "#f97316",
  earth: "#ca8a04",
  metal: "#94a3b8",
  water: "#3b82f6",
};

/** 백엔드 LLM 대기가 길어도 브라우저가 무한 로딩처럼 보이지 않게 상한(max_tokens 크면 응답이 매우 길어질 수 있음) */
const ANALYZE_FETCH_TIMEOUT_MS = 600_000;

function extractSummaryLine(md: string): string {
  const m = md.match(/###\s*1\.\s*한줄 요약\s*\r?\n+([\s\S]*?)(?=\r?\n###|\r?\n*$)/);
  if (!m) return "";
  const line = m[1].trim().split(/\r?\n/)[0] ?? "";
  return line.replace(/\*\*/g, "").slice(0, 400);
}

function ElementBars({ el }: { el: ApiRes["elements"] }) {
  const total = EL_KEYS.reduce((s, k) => s + el[k], 0) || 1;
  return (
    <div style={{ marginTop: "0.5rem" }}>
      {EL_KEYS.map((k) => {
        const pct = Math.round((el[k] / total) * 100);
        return (
          <div key={k} style={{ marginBottom: "0.5rem" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "0.8rem",
                marginBottom: 4,
                color: "#cbd5e1",
              }}
            >
              <span>{EL_LABEL[k]}</span>
              <span>
                {el[k]} ({pct}%)
              </span>
            </div>
            <div
              style={{
                height: 14,
                background: "#1e293b",
                borderRadius: 4,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${pct}%`,
                  height: "100%",
                  background: EL_COLOR[k],
                  transition: "width 0.2s ease",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function App() {
  const [name, setName] = useState("");
  const [gender, setGender] = useState<"male" | "female">("male");
  const [birthDate, setBirthDate] = useState("1990-01-15");
  const [birthTime, setBirthTime] = useState("12:00");
  const [timezone, setTimezone] = useState("Asia/Seoul");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [res, setRes] = useState<ApiRes | null>(null);
  const [inputOpen, setInputOpen] = useState(true);
  const [copyOk, setCopyOk] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    setLoading(true);
    setRes(null);
    try {
      const loc = location.trim();
      const body = {
        name: name.trim() || null,
        gender,
        birth_date: birthDate,
        calendar: "solar",
        birth_time: birthTime.trim() || null,
        timezone: timezone.trim() || "Asia/Seoul",
        location: loc ? loc : null,
      };
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), ANALYZE_FETCH_TIMEOUT_MS);
      let r: Response;
      try {
        r = await fetch("/api/saju/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: controller.signal,
        });
      } finally {
        window.clearTimeout(timeoutId);
      }
      const data = await r.json();
      if (!r.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail ?? r.status),
        );
      }
      setRes(data as ApiRes);
      setInputOpen(false);
    } catch (x) {
      if (x instanceof Error && x.name === "AbortError") {
        setErr(
          `요청이 ${ANALYZE_FETCH_TIMEOUT_MS / 1000}초 안에 끝나지 않았습니다. LM Studio가 느리거나 응답이 없을 수 있습니다. 서버에서 SAJU_SKIP_LLM=1 로 실행하면 규칙 기반 해설만 빠르게 받을 수 있습니다.`,
        );
      } else {
        setErr(x instanceof Error ? x.message : "요청 실패");
      }
    } finally {
      setLoading(false);
    }
  };

  const copyShareText = async () => {
    if (!res) return;
    const one = extractSummaryLine(res.interpretation.markdown);
    const parts = [
      "[saju-gstack]",
      `일간: ${res.day_master} · ${res.strength}`,
      `십성(천간): ${res.ten_gods.join(", ")}`,
      `${res.year_fortune.target_year}년 연주: ${res.year_fortune.annual_pillar.stem}${res.year_fortune.annual_pillar.branch} · 연간 십성(일간 기준): ${res.year_fortune.year_stem_ten_god_vs_day_master}`,
    ];
    if (one) parts.push(`한줄 요약: ${one}`);
    parts.push("---", res.interpretation.markdown.slice(0, 4500));
    const text = parts.join("\n");
    try {
      await navigator.clipboard.writeText(text);
      setCopyOk(true);
      window.setTimeout(() => setCopyOk(false), 2000);
    } catch {
      setErr("클립보드 복사에 실패했습니다.");
    }
  };

  const summaryLine = res ? extractSummaryLine(res.interpretation.markdown) : "";

  return (
    <div style={{ maxWidth: 1008, margin: "0 auto", padding: "2rem 1rem" }}>
      {(!res || inputOpen) && (
        <>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            saju-gstack
          </h1>
          <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
            사주는 Python으로만 계산하고, LLM은 JSON만 해석합니다. (양력 MVP) 로컬 LM Studio 사용 시
            외부로 원문이 나가지 않게 구성할 수 있습니다.
          </p>
        </>
      )}

      {res && !inputOpen && (
        <div
          style={{
            marginBottom: "1rem",
            padding: "0.75rem 1rem",
            background: "#12151c",
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.08)",
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <span style={{ color: "#94a3b8", fontSize: "0.9rem" }}>분석 완료 · 입력을 바꾸려면 버튼을 누르세요.</span>
          <button
            type="button"
            onClick={() => setInputOpen(true)}
            style={{
              padding: "0.4rem 0.75rem",
              borderRadius: 6,
              border: "1px solid #475569",
              background: "#1e293b",
              color: "#e2e8f0",
              cursor: "pointer",
              fontSize: "0.85rem",
            }}
          >
            입력 수정
          </button>
        </div>
      )}

      {(!res || inputOpen) && (
        <form
          onSubmit={submit}
          style={{
            display: "grid",
            gap: "0.75rem",
            padding: "1rem",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 8,
            background: "#12151c",
          }}
        >
          <label>
            이름 (선택)
            <input
              style={inp}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="닉네임"
            />
          </label>
          <label>
            성별
            <select
              style={inp}
              value={gender}
              onChange={(e) => setGender(e.target.value as "male" | "female")}
            >
              <option value="male">male</option>
              <option value="female">female</option>
            </select>
          </label>
          <label>
            생년월일 (YYYY-MM-DD)
            <input
              style={inp}
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              required
            />
          </label>
          <label>
            시각 (HH:mm, 비우면 12시 기본)
            <input
              style={inp}
              type="time"
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
            />
          </label>
          <label>
            타임존 (IANA, 예: Asia/Seoul)
            <input
              style={inp}
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              placeholder="Asia/Seoul"
              required
            />
          </label>
          <label>
            출생지 (선택, 참고용)
            <input
              style={inp}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="도시명 등"
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "0.65rem 1rem",
              borderRadius: 6,
              border: "none",
              background: "#334155",
              color: "#f8fafc",
              cursor: loading ? "wait" : "pointer",
              fontWeight: 600,
            }}
          >
            {loading ? "분석 중…" : "사주 보기 (POST /api/saju/analyze)"}
          </button>
        </form>
      )}

      {err && (
        <p style={{ color: "#f87171", marginTop: "1rem" }} role="alert">
          {err}
        </p>
      )}

      {res && (
        <div style={{ marginTop: "1.5rem" }} id="result-dashboard">
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem" }}>
            <h2 style={{ fontSize: "1.1rem", margin: 0 }}>결과</h2>
            <button
              type="button"
              onClick={copyShareText}
              style={{
                padding: "0.35rem 0.65rem",
                borderRadius: 6,
                border: "1px solid #475569",
                background: "#1e293b",
                color: "#e2e8f0",
                fontSize: "0.8rem",
                cursor: "pointer",
              }}
            >
              {copyOk ? "복사됨" : "요약·해석 복사"}
            </button>
          </div>

          {summaryLine && (
            <div
              style={{
                marginTop: "0.75rem",
                padding: "0.75rem 1rem",
                background: "#1a1f2e",
                borderRadius: 8,
                fontSize: "0.9rem",
                lineHeight: 1.5,
                borderLeft: "3px solid #64748b",
              }}
            >
              <strong style={{ color: "#94a3b8", fontSize: "0.75rem" }}>
                한줄 요약 (해석에서 발췌)
              </strong>
              <p style={{ margin: "0.35rem 0 0", color: "#e2e8f0" }}>{summaryLine}</p>
            </div>
          )}

          <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginTop: "0.75rem" }}>
            일간 {res.day_master} · {res.strength} · 십성(천간) {res.ten_gods.join(", ")}
          </p>

          <table
            style={{
              marginTop: "0.75rem",
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "0.85rem",
              background: "#0f1218",
              borderRadius: 8,
              overflow: "hidden",
            }}
          >
            <thead>
              <tr style={{ background: "#1a1f2a" }}>
                <th style={th}>기둥</th>
                <th style={th}>천간</th>
                <th style={th}>지지</th>
              </tr>
            </thead>
            <tbody>
              {(["year", "month", "day", "hour"] as const).map((k) => (
                <tr key={k}>
                  <td style={td}>{k === "year" ? "연" : k === "month" ? "월" : k === "day" ? "일" : "시"}</td>
                  <td style={td}>{res.saju[k].stem}</td>
                  <td style={td}>{res.saju[k].branch}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div
            style={{
              marginTop: "0.75rem",
              padding: "0.75rem 1rem",
              background: "#0f1218",
              borderRadius: 8,
              fontSize: "0.85rem",
            }}
          >
            <strong>오행 비율</strong>
            <ElementBars el={res.elements} />
          </div>

          <div
            style={{
              marginTop: "0.75rem",
              padding: "0.75rem 1rem",
              background: "#121a14",
              borderRadius: 8,
              fontSize: "0.85rem",
              border: "1px solid rgba(74, 222, 128, 0.2)",
            }}
          >
            <strong>
              {res.year_fortune.target_year}년 연주 (규칙 기반)
            </strong>
            <br />
            {res.year_fortune.annual_pillar.stem}
            {res.year_fortune.annual_pillar.branch} · 일간 대비 연간 십성:{" "}
            {res.year_fortune.year_stem_ten_god_vs_day_master}
          </div>

          {(res.meta?.warnings?.length ?? 0) > 0 && (
            <p style={{ color: "#fbbf24", fontSize: "0.85rem", marginTop: "0.5rem" }}>
              경고: {res.meta!.warnings!.join(", ")}
            </p>
          )}
          {res.meta?.datetime_policy && (
            <p style={{ color: "#64748b", fontSize: "0.75rem", marginTop: "0.35rem" }}>
              정책: {res.meta.datetime_policy}
            </p>
          )}

          <h3 style={{ fontSize: "1rem", marginTop: "1.25rem", marginBottom: "0.5rem" }}>
            해석 (LLM)
          </h3>
          <div
            style={{
              padding: "1rem",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 8,
              whiteSpace: "pre-wrap",
              lineHeight: 1.65,
              fontSize: "1rem",
            }}
          >
            {res.interpretation.markdown}
          </div>
          <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.5rem" }}>
            model={res.interpretation.model} · {res.interpretation.prompt_version}
          </p>
        </div>
      )}
    </div>
  );
}

const th: React.CSSProperties = {
  textAlign: "left",
  padding: "0.5rem 0.75rem",
  borderBottom: "1px solid #334155",
  color: "#cbd5e1",
};
const td: React.CSSProperties = {
  padding: "0.45rem 0.75rem",
  borderBottom: "1px solid #1e293b",
};

const inp: React.CSSProperties = {
  display: "block",
  width: "100%",
  marginTop: 4,
  padding: "0.5rem 0.6rem",
  borderRadius: 6,
  border: "1px solid #334155",
  background: "#0c0e12",
  color: "#e2e8f0",
};
