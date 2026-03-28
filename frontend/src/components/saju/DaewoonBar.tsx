// 대운 흐름 타임라인 컴포넌트
import { OHAENG_COLORS } from "@/lib/utils";
import type { Daewoon, Seun } from "@/types/saju";

interface DaewoonBarProps {
  daewoon: Daewoon[];
  seun?: Seun[];
  birthYear: number;
}

export function DaewoonBar({ daewoon, seun, birthYear }: DaewoonBarProps) {
  const currentYear = new Date().getFullYear();
  const currentAge = currentYear - birthYear;

  return (
    <div className="space-y-6">
      {/* 대운 타임라인 */}
      <div>
        <h4 className="text-sm text-muted-foreground mb-3">
          대운(大運) — 10년 단위 운세 흐름
          <span className="ml-2 text-xs">({daewoon[0]?.direction})</span>
        </h4>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {daewoon.map((dw, idx) => {
            const ganColor = OHAENG_COLORS[dw.gan_ohaeng] || "#888";
            const jiColor = OHAENG_COLORS[dw.ji_ohaeng] || "#888";
            const isCurrentDaewoon =
              currentAge >= dw.age && currentAge < dw.age + 10;

            return (
              <div
                key={idx}
                className={`flex-shrink-0 w-20 flex flex-col items-center rounded-lg border p-2 transition-all ${
                  isCurrentDaewoon
                    ? "border-primary bg-primary/10 shadow-md"
                    : "border-border bg-card"
                }`}
              >
                {/* 나이 */}
                <div className={`text-xs font-medium mb-1.5 ${isCurrentDaewoon ? "text-primary" : "text-muted-foreground"}`}>
                  {dw.age}세~
                  {isCurrentDaewoon && (
                    <span className="ml-1 text-primary">●</span>
                  )}
                </div>

                {/* 천간 */}
                <div className="hanja text-xl font-bold" style={{ color: ganColor }}>
                  {dw.gan_hanja}
                </div>
                <div className="text-xs" style={{ color: ganColor }}>
                  {dw.gan_ohaeng}
                </div>

                {/* 구분선 */}
                <div className="w-full h-px bg-border my-1.5" />

                {/* 지지 */}
                <div className="hanja text-xl font-bold" style={{ color: jiColor }}>
                  {dw.ji_hanja}
                </div>
                <div className="text-xs" style={{ color: jiColor }}>
                  {dw.ji_ohaeng}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 세운 */}
      {seun && seun.length > 0 && (
        <div>
          <h4 className="text-sm text-muted-foreground mb-3">
            세운(歲運) — 올해부터 10년간 연간 운세
          </h4>
          <div className="grid grid-cols-5 gap-2 md:grid-cols-10">
            {seun.slice(0, 10).map((sw, idx) => {
              const ganColor = OHAENG_COLORS[sw.gan_ohaeng] || "#888";
              const jiColor = OHAENG_COLORS[sw.ji_ohaeng] || "#888";
              const isCurrentYear = sw.year === currentYear;

              return (
                <div
                  key={idx}
                  className={`flex flex-col items-center rounded-lg border p-2 text-center ${
                    isCurrentYear
                      ? "border-primary bg-primary/10"
                      : "border-border bg-card"
                  }`}
                >
                  <div className={`text-xs font-medium mb-1 ${isCurrentYear ? "text-primary" : "text-muted-foreground"}`}>
                    {sw.year}
                  </div>
                  <div className="hanja text-base font-bold" style={{ color: ganColor }}>
                    {sw.gan_hanja}
                  </div>
                  <div className="hanja text-base font-bold" style={{ color: jiColor }}>
                    {sw.ji_hanja}
                  </div>
                  <div className="text-xs text-muted-foreground">{sw.age}세</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
