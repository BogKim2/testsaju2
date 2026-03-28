import { Badge } from "@/components/ui/badge";
import type { QualityVerdict } from "@/types/harness";

interface QualityBadgeProps {
  result: QualityVerdict;
}

// PASS / CONDITIONAL_PASS / FAIL 배지
export function QualityBadge({ result }: QualityBadgeProps) {
  if (result === "PASS") return <Badge variant="success">PASS</Badge>;
  if (result === "CONDITIONAL_PASS") return <Badge variant="warning">조건부 통과</Badge>;
  return <Badge variant="destructive">FAIL</Badge>;
}
