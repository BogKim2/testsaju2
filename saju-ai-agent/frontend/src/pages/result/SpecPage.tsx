import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SpecCard } from "@/components/harness/SpecCard";
import { Loader2 } from "lucide-react";
import { getAgentResult } from "@/lib/api";
import type { SpecResult } from "@/types/harness";

// 전기 스펙 검증 페이지
export default function SpecPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<SpecResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getAgentResult(id, "spec")
      .then((res) => setData(res as unknown as SpecResult))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (!data) return <p className="text-muted-foreground">결과 없음</p>;

  return (
    <Card>
      <CardHeader><CardTitle>전기 스펙 검증 결과</CardTitle></CardHeader>
      <CardContent>
        <SpecCard items={data.items} summary={data.summary} />
      </CardContent>
    </Card>
  );
}
