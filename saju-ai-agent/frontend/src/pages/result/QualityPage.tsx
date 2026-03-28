import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { QualityBadge } from "@/components/harness/QualityBadge";
import { IssueTable } from "@/components/harness/IssueTable";
import { Loader2 } from "lucide-react";
import { getAgentResult } from "@/lib/api";
import type { QualityResult } from "@/types/harness";

// 품질 검사 결과 페이지
export default function QualityPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<QualityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getAgentResult(id, "quality")
      .then((res) => setData(res as unknown as QualityResult))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (!data) return <p className="text-muted-foreground">결과 없음</p>;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>품질 검사 결과</span>
            <QualityBadge result={data.overallResult} />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            통과율: <span className="font-medium text-foreground">{data.passRate}%</span>
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">이슈 목록 ({data.issues.length}건)</CardTitle>
        </CardHeader>
        <CardContent><IssueTable issues={data.issues} /></CardContent>
      </Card>
    </div>
  );
}
