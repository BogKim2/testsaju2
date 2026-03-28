import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, ArrowRight } from "lucide-react";
import { getHistory } from "@/lib/api";
import type { HistoryItem } from "@/types/harness";

function statusColor(status: string) {
  if (status === "done") return "success" as const;
  if (status === "error") return "destructive" as const;
  return "secondary" as const;
}

// 분석 이력 페이지
export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory()
      .then(setItems)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      <h2 className="text-2xl font-bold">분석 이력</h2>

      {loading && (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}

      {error && <p className="text-destructive">{error}</p>}

      {!loading && !error && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">총 {items.length}건</CardTitle>
          </CardHeader>
          <CardContent>
            {items.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">분석 이력이 없습니다</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>프로젝트명</TableHead>
                    <TableHead>일시</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>요약</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.session_id}>
                      <TableCell className="font-medium">{item.project_name}</TableCell>
                      <TableCell className="text-muted-foreground text-xs">
                        {new Date(item.created_at).toLocaleString("ko-KR")}
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusColor(item.status)}>{item.status}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs max-w-[200px] truncate">
                        {item.summary}
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="ghost" asChild>
                          <Link to={`/result/${item.session_id}`}>
                            <ArrowRight className="h-4 w-4" />
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
