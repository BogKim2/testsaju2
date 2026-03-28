// 오행 분포 차트 컴포넌트 (Recharts 레이더/파이 차트)
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { OhaengDistribution } from "@/types/saju";

interface OhaengChartProps {
  ohaeng: OhaengDistribution;
  yangeum: { 양: number; 음: number };
}

const OHAENG_ORDER = ["목", "화", "토", "금", "수"] as const;

export function OhaengChart({ ohaeng, yangeum }: OhaengChartProps) {
  // 레이더 차트 데이터
  const radarData = OHAENG_ORDER.map((key) => ({
    subject: `${ohaeng[key].hanja}(${key})`,
    count: ohaeng[key].count,
    fullMark: 8,
  }));

  // 파이 차트 데이터 (오행)
  const pieData = OHAENG_ORDER
    .filter((key) => ohaeng[key].count > 0)
    .map((key) => ({
      name: `${key}(${ohaeng[key].hanja})`,
      value: ohaeng[key].count,
      color: ohaeng[key].color,
    }));

  // 음양 파이 데이터
  const yangeumData = [
    { name: "양(陽)", value: yangeum["양"], color: "#F59E0B" },
    { name: "음(陰)", value: yangeum["음"], color: "#6366F1" },
  ];

  return (
    <div className="space-y-6">
      {/* 오행 카운트 배지 */}
      <div className="flex justify-center gap-3 flex-wrap">
        {OHAENG_ORDER.map((key) => (
          <div
            key={key}
            className="flex flex-col items-center px-4 py-2 rounded-lg border"
            style={{
              borderColor: ohaeng[key].color + "60",
              backgroundColor: ohaeng[key].color + "15",
            }}
          >
            <span
              className="hanja text-xl font-bold"
              style={{ color: ohaeng[key].color }}
            >
              {ohaeng[key].hanja}
            </span>
            <span className="text-xs" style={{ color: ohaeng[key].color }}>
              {key}
            </span>
            <span
              className="text-lg font-bold"
              style={{ color: ohaeng[key].color }}
            >
              {ohaeng[key].count}개
            </span>
          </div>
        ))}
      </div>

      {/* 차트 영역 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 레이더 차트 */}
        <div>
          <h4 className="text-sm text-muted-foreground text-center mb-2">오행 분포 (레이더)</h4>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: "#94a3b8", fontSize: 12 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 4]}
                tick={{ fill: "#64748b", fontSize: 10 }}
              />
              <Radar
                name="오행"
                dataKey="count"
                stroke="#F59E0B"
                fill="#F59E0B"
                fillOpacity={0.3}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* 파이 차트 (오행) */}
        <div>
          <h4 className="text-sm text-muted-foreground text-center mb-2">오행 비율</h4>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
                labelLine={false}
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`${value}개`, "개수"]}
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                  color: "#e2e8f0",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 음양 분포 */}
      <div className="flex items-center gap-6 justify-center">
        <h4 className="text-sm text-muted-foreground">음양 분포</h4>
        <div className="flex gap-4">
          {yangeumData.map((item) => (
            <div key={item.name} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm">
                {item.name}: <span className="font-bold">{item.value}개</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
