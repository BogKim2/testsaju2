// 분석 이력 페이지
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Home, ChevronRight } from "lucide-react";
import { getHistory } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { HistoryItem } from "@/types/saju";

export function HistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory()
      .then((res) => setItems(res.items))
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gradient">분석 이력</h1>
        <Button variant="outline" size="sm" onClick={() => navigate("/")}>
          <Home className="w-4 h-4" />
          새 분석
        </Button>
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      )}

      {error && (
        <div className="p-3 rounded-md bg-destructive/10 border border-destructive/30 text-destructive text-sm">
          {error}
        </div>
      )}

      {!isLoading && items.length === 0 && !error && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">아직 분석 이력이 없습니다.</p>
            <Button onClick={() => navigate("/")}>첫 사주 분석 시작하기</Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {items.map((item) => (
          <Card
            key={item.session_id}
            className="cursor-pointer hover:border-primary/50 transition-all hover:card-glow"
            onClick={() => navigate(`/result/${item.session_id}`)}
          >
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {/* 이름/성별 */}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{item.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {item.gender}성
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {item.birth_year}년 {item.birth_month}월 {item.birth_day}일
                    </p>
                  </div>

                  {/* 일간/띠 */}
                  <div className="hidden sm:flex items-center gap-3">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">일간</p>
                      <p className="font-bold text-primary">{item.ilgan}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground">띠</p>
                      <p className="font-bold">{item.animal}띠</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <p className="text-xs text-muted-foreground hidden sm:block">
                    {formatDate(item.created_at)}
                  </p>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
