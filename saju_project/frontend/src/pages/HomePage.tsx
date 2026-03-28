// 홈 페이지 - 사주 입력 폼
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { SajuInputForm } from "@/components/saju/SajuInputForm";
import { startAnalysis } from "@/lib/api";
import type { AnalyzeRequest } from "@/types/saju";

export function HomePage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async (data: AnalyzeRequest) => {
    setError("");
    setIsLoading(true);

    try {
      const result = await startAnalysis(data);
      navigate(`/analyze/${result.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "분석 시작 실패");
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      {/* 안내 문구 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gradient mb-2">나의 사주 분석</h1>
        <p className="text-muted-foreground">
          생년월일시를 입력하면 AI가 사주 8자를 계산하고
          <br />
          한국어로 상세하게 해설해 드립니다.
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-md bg-destructive/10 border border-destructive/30 text-destructive text-sm text-center">
          {error}
        </div>
      )}

      <SajuInputForm onSubmit={handleAnalyze} isLoading={isLoading} />

      {/* 설명 카드들 */}
      <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { icon: "🏯", title: "사주 8자", desc: "연월일시 4주의 천간지지" },
          { icon: "🌿", title: "오행 분석", desc: "木火土金水 기운 분포" },
          { icon: "📅", title: "대운/세운", desc: "10년 단위 운세 흐름" },
          { icon: "🤖", title: "AI 해설", desc: "LLM 기반 한국어 풀이" },
        ].map((item) => (
          <div
            key={item.title}
            className="flex flex-col items-center text-center p-4 rounded-lg border border-border bg-card hover:border-primary/40 transition-all"
          >
            <span className="text-2xl mb-2">{item.icon}</span>
            <p className="text-sm font-medium">{item.title}</p>
            <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
