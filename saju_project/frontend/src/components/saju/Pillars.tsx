// 사주 4주 8자 시각화 컴포넌트
import { cn } from "@/lib/utils";
import { OHAENG_COLORS } from "@/lib/utils";
import type { Pillars as PillarsType } from "@/types/saju";

interface PillarsProps {
  pillars: PillarsType;
  highlightDay?: boolean;
}

const PILLAR_LABELS = ["시주(時柱)", "일주(日柱)", "월주(月柱)", "연주(年柱)"];
const PILLAR_KEYS = ["hour", "day", "month", "year"] as const;

export function Pillars({ pillars, highlightDay = true }: PillarsProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground text-center">사주 4주 8자</h3>

      {/* 4주 배치 (시일월연 순서로 오른쪽부터) */}
      <div className="grid grid-cols-4 gap-3">
        {PILLAR_KEYS.map((key, idx) => {
          const pillar = pillars[key];
          const isDay = key === "day";
          const ganColor = OHAENG_COLORS[pillar.gan_ohaeng] || "#888";
          const jiColor = OHAENG_COLORS[pillar.ji_ohaeng] || "#888";

          return (
            <div
              key={key}
              className={cn(
                "flex flex-col items-center rounded-lg border p-3 transition-all",
                isDay && highlightDay
                  ? "border-primary bg-primary/10 shadow-md"
                  : "border-border bg-card hover:border-primary/40"
              )}
            >
              {/* 주 이름 */}
              <p className="text-xs text-muted-foreground mb-2">{PILLAR_LABELS[idx]}</p>

              {/* 천간 */}
              <div className="text-center mb-1">
                <div
                  className="hanja text-3xl font-bold"
                  style={{ color: ganColor }}
                >
                  {pillar.gan_hanja}
                </div>
                <div className="text-xs mt-0.5" style={{ color: ganColor }}>
                  {pillar.gan} · {pillar.gan_ohaeng}({pillar.gan_yangeum})
                </div>
              </div>

              {/* 구분선 */}
              <div className="w-full h-px bg-border my-2" />

              {/* 지지 */}
              <div className="text-center">
                <div
                  className="hanja text-3xl font-bold"
                  style={{ color: jiColor }}
                >
                  {pillar.ji_hanja}
                </div>
                <div className="text-xs mt-0.5" style={{ color: jiColor }}>
                  {pillar.ji} · {pillar.ji_ohaeng}({pillar.ji_yangeum})
                </div>
              </div>

              {/* 일주 표시 */}
              {isDay && highlightDay && (
                <div className="mt-2 text-xs text-primary font-medium">일간(나)</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
