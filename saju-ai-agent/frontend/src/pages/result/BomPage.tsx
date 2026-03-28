import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BomTable } from "@/components/harness/BomTable";
import { Loader2 } from "lucide-react";
import { getAgentResult } from "@/lib/api";
import type { BomResult } from "@/types/harness";

// BOM 검증 결과 페이지
export default function BomPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<BomResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getAgentResult(id, "bom")
      .then((res) => setData(res as unknown as BomResult))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (!data) return <p className="text-muted-foreground">결과 없음</p>;

  const passRate = data.totalItems > 0 ? Math.round((data.passItems / data.totalItems) * 100) : 0;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>BOM 검증 결과</span>
            <Badge variant={passRate >= 80 ? "success" : "warning"}>통과율 {passRate}%</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">전체 {data.totalItems}개 중 {data.passItems}개 통과</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">BOM 상세 목록</CardTitle></CardHeader>
        <CardContent><BomTable items={data.items} /></CardContent>
      </Card>
    </div>
  );
}
