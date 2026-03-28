// 분석 결과 페이지
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Pillars } from "@/components/saju/Pillars";
import { OhaengChart } from "@/components/saju/OhaengChart";
import { DaewoonBar } from "@/components/saju/DaewoonBar";
import { Loader2, Home, History, Star } from "lucide-react";
import { getAnalysisResult } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { SajuResult } from "@/types/saju";

export function ResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<SajuResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    getAnalysisResult(sessionId)
      .then(setResult)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-lg mx-auto py-12 px-4 text-center">
        <p className="text-destructive mb-4">{error || "결과를 불러올 수 없습니다."}</p>
        <Button onClick={() => navigate("/")}>처음으로</Button>
      </div>
    );
  }

  const ohaengVariantMap: Record<string, "mok" | "hwa" | "to" | "geum" | "su"> = {
    목: "mok", 화: "hwa", 토: "to", 금: "geum", 수: "su",
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 space-y-6 animate-fade-in">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gradient">{result.name}님의 사주 분석</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {result.birth.year}년 {result.birth.month}월 {result.birth.day}일{" "}
            {result.birth.hour}시 · {result.gender}성 · {result.animal}띠
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate("/")}>
            <Home className="w-4 h-4" />
            새 분석
          </Button>
          <Button variant="outline" size="sm" onClick={() => navigate("/history")}>
            <History className="w-4 h-4" />
            이력
          </Button>
        </div>
      </div>

      {/* 일간 요약 카드 */}
      <Card className="card-glow">
        <CardContent className="pt-5">
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center">
                <Star className="w-7 h-7 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">일간 (나 자신)</p>
                <div className="flex items-center gap-2">
                  <span className="hanja text-3xl font-bold text-foreground">
                    {result.pillars.day.gan_hanja}
                  </span>
                  <div>
                    <p className="text-sm font-medium">{result.ilgan}({result.ilgan_ohaeng})</p>
                    <p className="text-xs text-muted-foreground">{result.pillars.day.gan_yangeum}간</p>
                  </div>
                </div>
              </div>
            </div>

            <Separator orientation="vertical" className="h-14 hidden md:block" />

            <div className="flex gap-3 flex-wrap">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">오행</p>
                <Badge variant={ohaengVariantMap[result.ilgan_ohaeng] || "default"} className="mt-1">
                  {result.ilgan_ohaeng}(
                  {result.ohaeng[result.ilgan_ohaeng as keyof typeof result.ohaeng]?.hanja})
                </Badge>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">띠</p>
                <p className="font-bold mt-1">{result.animal}띠</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">분석 완료</p>
                <p className="text-xs mt-1">{formatDate(result.completed_at)}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 탭 콘텐츠 */}
      <Tabs defaultValue="pillars">
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="pillars">사주 8자</TabsTrigger>
          <TabsTrigger value="ohaeng">오행 분석</TabsTrigger>
          <TabsTrigger value="daewoon">대운/세운</TabsTrigger>
          <TabsTrigger value="interpretation">AI 해설</TabsTrigger>
        </TabsList>

        {/* 사주 8자 탭 */}
        <TabsContent value="pillars">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">사주 4주 8자</CardTitle>
            </CardHeader>
            <CardContent>
              <Pillars pillars={result.pillars} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* 오행 분석 탭 */}
        <TabsContent value="ohaeng">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">오행(五行) 분포 분석</CardTitle>
            </CardHeader>
            <CardContent>
              <OhaengChart ohaeng={result.ohaeng} yangeum={result.yangeum} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* 대운/세운 탭 */}
        <TabsContent value="daewoon">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">대운(大運) / 세운(歲運)</CardTitle>
            </CardHeader>
            <CardContent>
              <DaewoonBar
                daewoon={result.daewoon}
                seun={result.seun}
                birthYear={result.birth.year}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI 해설 탭 */}
        <TabsContent value="interpretation">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">AI 사주 해설</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-invert prose-sm max-w-none">
                <div className="text-sm text-foreground leading-7 whitespace-pre-wrap">
                  {result.interpretation}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
