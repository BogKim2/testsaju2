import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Loader2, Clock, XCircle } from "lucide-react";
import type { AgentProgress, AgentStatus } from "@/types/harness";

const AGENT_LABELS: Record<string, string> = {
  design: "설계 분석",
  bom: "BOM 검증",
  spec: "전기 스펙",
  quality: "품질 검사",
  routing: "경로 최적화",
};

function StatusIcon({ status }: { status: AgentStatus }) {
  if (status === "done") return <CheckCircle className="h-4 w-4 text-green-500" />;
  if (status === "running") return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
  if (status === "error") return <XCircle className="h-4 w-4 text-red-500" />;
  return <Clock className="h-4 w-4 text-muted-foreground" />;
}

function statusVariant(status: AgentStatus) {
  if (status === "done") return "success" as const;
  if (status === "running") return "default" as const;
  if (status === "error") return "destructive" as const;
  return "secondary" as const;
}

function statusLabel(status: AgentStatus): string {
  if (status === "pending") return "대기 중";
  if (status === "running") return "분석 중";
  if (status === "done") return "완료";
  return "오류";
}

interface AgentStatusBarProps {
  agents: AgentProgress[];
}

// 에이전트 진행 상태 표시
export function AgentStatusBar({ agents }: AgentStatusBarProps) {
  const doneCount = agents.filter((a) => a.status === "done").length;
  const progress = agents.length > 0 ? (doneCount / agents.length) * 100 : 0;

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>전체 진행률</span>
          <span>{doneCount}/{agents.length} 완료</span>
        </div>
        <Progress value={progress} />
      </div>
      <div className="space-y-2">
        {agents.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between rounded-lg border border-border p-3">
            <div className="flex items-center gap-2">
              <StatusIcon status={agent.status} />
              <span className="text-sm font-medium">{AGENT_LABELS[agent.name] ?? agent.name}</span>
            </div>
            <Badge variant={statusVariant(agent.status)}>{statusLabel(agent.status)}</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
