import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AgentStatusBar } from "@/components/harness/AgentStatusBar";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { getAnalyzeStatus } from "@/lib/api";
import type { AgentProgress } from "@/types/harness";

// 분석 진행 화면 - 에이전트 상태 폴링
export default function AnalyzePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get("id") ?? "";

  const [agents, setAgents] = useState<AgentProgress[]>([]);
  const [isDone, setIsDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;

    // 1.5초마다 상태 폴링
    const poll = async () => {
      try {
        const res = await getAnalyzeStatus(sessionId);
        setAgents(res.agents);
        const allFinished = res.agents.every(
          (a) => a.status === "done" || a.status === "error"
        );
        if (allFinished || res.status === "done") {
          setIsDone(true);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "상태 조회 실패");
      }
    };

    poll();
    const timer = setInterval(poll, 1500);
    return () => clearInterval(timer);
  }, [sessionId]);

  if (!sessionId) {
    return <p className="text-muted-foreground text-center py-12">잘못된 접근입니다.</p>;
  }

  return (
    <div className="flex justify-center min-h-[60vh] pt-12">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {!isDone && <Loader2 className="h-5 w-5 animate-spin text-primary" />}
            {isDone ? "분석 완료" : "AI 에이전트 분석 중"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error ? (
            <p className="text-sm text-destructive">{error}</p>
          ) : (
            <AgentStatusBar agents={agents} />
          )}
          {isDone && (
            <Button className="w-full" onClick={() => navigate(`/result/${sessionId}`)}>
              분석 결과 보기
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
