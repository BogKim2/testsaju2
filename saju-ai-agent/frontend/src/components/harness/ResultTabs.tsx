import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

interface ResultTabsProps {
  sessionId: string;
}

const TABS = [
  { path: "", label: "종합" },
  { path: "/design", label: "설계 분석" },
  { path: "/bom", label: "BOM 검증" },
  { path: "/spec", label: "전기 스펙" },
  { path: "/quality", label: "품질 검사" },
  { path: "/routing", label: "경로 최적화" },
] as const;

// 에이전트별 결과 탭 (React Router NavLink)
export function ResultTabs({ sessionId }: ResultTabsProps) {
  const base = `/result/${sessionId}`;

  return (
    <nav className="flex gap-1 border-b border-border">
      {TABS.map((tab) => (
        <NavLink
          key={tab.path}
          to={`${base}${tab.path}`}
          end={tab.path === ""}
          className={({ isActive }) =>
            cn(
              "px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
              isActive
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
