// 사주 입력 폼 컴포넌트
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Star } from "lucide-react";
import type { AnalyzeRequest } from "@/types/saju";

interface SajuInputFormProps {
  onSubmit: (data: AnalyzeRequest) => void;
  isLoading?: boolean;
}

const CURRENT_YEAR = new Date().getFullYear();

export function SajuInputForm({ onSubmit, isLoading = false }: SajuInputFormProps) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState<"남" | "여">("남");
  const [birthYear, setBirthYear] = useState("");
  const [birthMonth, setBirthMonth] = useState("");
  const [birthDay, setBirthDay] = useState("");
  const [birthHour, setBirthHour] = useState("12");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !birthYear || !birthMonth || !birthDay) return;

    onSubmit({
      name: name.trim(),
      gender,
      birth_year: parseInt(birthYear),
      birth_month: parseInt(birthMonth),
      birth_day: parseInt(birthDay),
      birth_hour: parseInt(birthHour),
    });
  };

  return (
    <Card className="w-full max-w-lg mx-auto card-glow">
      <CardHeader className="text-center pb-2">
        <div className="flex justify-center mb-3">
          <div className="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center">
            <Star className="w-7 h-7 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl text-gradient">사주 분석 시작</CardTitle>
        <CardDescription>
          생년월일시를 입력하면 AI가 사주 8자를 분석해 드립니다.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* 이름 */}
          <div className="space-y-2">
            <Label htmlFor="name">이름</Label>
            <Input
              id="name"
              placeholder="홍길동"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          {/* 성별 */}
          <div className="space-y-2">
            <Label>성별</Label>
            <div className="flex gap-3">
              {(["남", "여"] as const).map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGender(g)}
                  className={`flex-1 py-2.5 rounded-md border text-sm font-medium transition-all ${
                    gender === g
                      ? "border-primary bg-primary/20 text-primary"
                      : "border-border bg-secondary/50 text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  {g === "남" ? "남성 (♂)" : "여성 (♀)"}
                </button>
              ))}
            </div>
          </div>

          {/* 생년월일 */}
          <div className="space-y-2">
            <Label>생년월일 (양력)</Label>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <Input
                  type="number"
                  placeholder="연도"
                  min={1900}
                  max={CURRENT_YEAR}
                  value={birthYear}
                  onChange={(e) => setBirthYear(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1 text-center">연도</p>
              </div>
              <div>
                <Input
                  type="number"
                  placeholder="월"
                  min={1}
                  max={12}
                  value={birthMonth}
                  onChange={(e) => setBirthMonth(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1 text-center">월</p>
              </div>
              <div>
                <Input
                  type="number"
                  placeholder="일"
                  min={1}
                  max={31}
                  value={birthDay}
                  onChange={(e) => setBirthDay(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1 text-center">일</p>
              </div>
            </div>
          </div>

          {/* 출생 시간 */}
          <div className="space-y-2">
            <Label htmlFor="hour">
              출생 시간
              <span className="text-xs text-muted-foreground ml-2">(24시간 기준, 모르면 12 입력)</span>
            </Label>
            <div className="flex items-center gap-3">
              <Input
                id="hour"
                type="number"
                min={0}
                max={23}
                value={birthHour}
                onChange={(e) => setBirthHour(e.target.value)}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">시</span>
              <span className="text-xs text-muted-foreground">
                ({getShiName(parseInt(birthHour || "12"))})
              </span>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full h-12 text-base"
            disabled={isLoading || !name.trim() || !birthYear || !birthMonth || !birthDay}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                분석 시작 중...
              </>
            ) : (
              "사주 분석하기"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function getShiName(hour: number): string {
  const shi = [
    "자시(子時)", "자시(子時)",
    "축시(丑時)", "축시(丑時)",
    "인시(寅時)", "인시(寅時)",
    "묘시(卯時)", "묘시(卯時)",
    "진시(辰時)", "진시(辰時)",
    "사시(巳時)", "사시(巳時)",
    "오시(午時)", "오시(午時)",
    "미시(未時)", "미시(未時)",
    "신시(申時)", "신시(申時)",
    "유시(酉時)", "유시(酉時)",
    "술시(戌時)", "술시(戌時)",
    "해시(亥時)", "해시(亥時)",
  ];
  return shi[hour] || "오시(午時)";
}
