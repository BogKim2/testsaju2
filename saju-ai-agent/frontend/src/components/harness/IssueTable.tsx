import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { QualityIssue, IssueSeverity } from "@/types/harness";

function severityVariant(severity: IssueSeverity) {
  if (severity === "FAIL") return "destructive" as const;
  if (severity === "WARNING") return "warning" as const;
  return "secondary" as const;
}

interface IssueTableProps {
  issues: QualityIssue[];
}

// 품질 이슈 테이블
export function IssueTable({ issues }: IssueTableProps) {
  if (issues.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-4">이슈가 없습니다</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>심각도</TableHead>
          <TableHead>항목</TableHead>
          <TableHead>내용</TableHead>
          <TableHead>조치</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {issues.map((issue) => (
          <TableRow key={issue.id}>
            <TableCell><Badge variant={severityVariant(issue.severity)}>{issue.severity}</Badge></TableCell>
            <TableCell className="font-medium">{issue.item}</TableCell>
            <TableCell className="text-muted-foreground">{issue.detail}</TableCell>
            <TableCell className="text-muted-foreground">{issue.action}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
