// 분석 진행 페이지 - 상태 폴링
import { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle, XCircle, Star } from "lucide-react";
import { getAnalysisStatus } from "@/lib/api";
import type { AnalysisStatus } from "@/types/saju";

const STEPS = [
  { label: "사주 8자 계산", range: [0, 30] },
  { label: "대운/세운 계산", range: [30, 60] },
  { label: "오행 균형 분석", range: [60, 80] },
  { label: "AI 해설 생성", range: [80, 100] },
];

export function AnalyzePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [error, setError] = useState("");

  const poll = useCallback(async () => {
    if (!sessionId) return;
    try {
      const s = await getAnalysisStatus(sessionId);
      setStatus(s);

      if (s.status === "done") {
        setTimeout(() => navigate(`/result/${sessionId}`), 800);
      } else if (s.status === "error") {
        setError(s.error || "분석 중 오류가 발생했습니다.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "상태 조회 실패");
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    poll();
    const interval = setInterval(() => {
      if (status?.status === "done" || status?.status === "error") return;
      poll();
    }, 1500);
    return () => clearInterval(interval);
  }, [poll, status?.status]);

  const progress = status?.progress ?? 0;
  const isDone = status?.status === "done";
  const isError = status?.status === "error" || !!error;

  // 현재 단계 판별
  const currentStep = STEPS.findIndex(
    (s) => progress >= s.range[0] && progress < s.range[1]
  );

  return (
    <div className="max-w-lg mx-auto py-12 px-4">
      <Card className="card-glow">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-3">
            {isDone ? (
              <CheckCircle className="w-12 h-12 text-green-500" />
            ) : isError ? (
              <XCircle className="w-12 h-12 text-destructive" />
            ) : (
              <div className="relative">
                <Star className="w-12 h-12 text-primary animate-pulse" />
                <Loader2 className="w-6 h-6 text-primary animate-spin absolute -bottom-1 -right-1" />
              </div>
            )}
          </div>
          <CardTitle className="text-xl">
            {isDone
              ? "분석 완료!"
              : isError
              ? "분석 실패"
              : "사주 분석 중..."}
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          {!isError && (
            <>
              {/* 진행률 바 */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">진행률</span>
                  <span className="text-primary font-bold">{progress}%</span>
                </div>
                <Progress value={progress} className="h-3" />
              </div>

              {/* 단계별 상태 */}
              <div className="space-y-3">
                {STEPS.map((step, idx) => {
                  const isCompleted = progress >= step.range[1];
                  const isActive = idx === currentStep;

                  return (
                    <div
                      key={idx}
                      className={`flex items-center gap-3 p-3 rounded-md transition-all ${
                        isActive ? "bg-primary/10 border border-primary/30" : ""
                      }`}
                    >
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                          isCompleted
                            ? "bg-green-500/20 text-green-500"
                            : isActive
                            ? "bg-primary/20 text-primary"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {isCompleted ? "✓" : idx + 1}
                      </div>
                      <span
                        className={`text-sm ${
                          isCompleted
                            ? "text-green-500"
                            : isActive
                            ? "text-foreground font-medium"
                            : "text-muted-foreground"
                        }`}
                      >
                        {step.label}
                        {isActive && (
                          <span className="ml-2 text-xs text-primary animate-pulse">
                            처리 중...
                          </span>
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {isError && (
            <div className="space-y-4">
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/30 text-destructive text-sm">
                {error}
              </div>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate("/")}
              >
                처음으로 돌아가기
              </Button>
            </div>
          )}

          {isDone && (
            <div className="text-center text-sm text-muted-foreground">
              결과 페이지로 이동 중...
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
