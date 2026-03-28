import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { getAgentResult } from "@/lib/api";

// 설계 분석 결과 페이지
export default function DesignPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getAgentResult(id, "design")
      .then(setData)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  if (error) return <p className="text-destructive">{error}</p>;

  return (
    <Card>
      <CardHeader><CardTitle>설계 분석 결과</CardTitle></CardHeader>
      <CardContent>
        <pre className="text-xs text-muted-foreground overflow-auto max-h-96 rounded bg-muted p-4">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}
