import { useEffect, useState } from "react";
import { useParams, Outlet } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { QualityBadge } from "@/components/harness/QualityBadge";
import { ResultTabs } from "@/components/harness/ResultTabs";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";
import { getResult } from "@/lib/api";
import type { FullResultResponse } from "@/types/harness";

// 결과 레이아웃 (탭 + 종합/상세 페이지 공유)
export default function ResultPage() {
  const { id } = useParams<{ id: string }>();
  const [result, setResult] = useState<FullResultResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getResult(id)
      .then(setResult)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (error) return <p className="text-destructive">{error}</p>;
  if (!result || !id) return null;

  const qualityVerdict = result.agents.quality?.overallResult;

  return (
    <div className="space-y-6 max-w-4xl">
      {/* 프로젝트 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{result.project_name}</h2>
          <p className="text-sm text-muted-foreground">세션 ID: {result.session_id}</p>
        </div>
        {qualityVerdict && <QualityBadge result={qualityVerdict} />}
      </div>

      {/* 탭 내비게이션 */}
      <ResultTabs sessionId={id} />

      {/* AI 요약 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">AI 분석 요약</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {result.summary || "요약 정보가 없습니다."}
          </p>
        </CardContent>
      </Card>

      <Separator />

      {/* 에이전트별 결과 요약 카드 */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {(["design", "bom", "spec", "quality", "routing"] as const).map((agent) => {
          const labels: Record<string, string> = {
            design: "설계 분석", bom: "BOM 검증", spec: "전기 스펙",
            quality: "품질 검사", routing: "경로 최적화",
          };
          return (
            <Card key={agent}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">{labels[agent]}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {result.agents[agent] ? "완료" : "결과 없음"}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 중첩 라우트용 Outlet */}
      <Outlet />
    </div>
  );
}
