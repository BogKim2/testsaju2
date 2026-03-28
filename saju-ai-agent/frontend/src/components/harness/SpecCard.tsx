import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { SpecItem } from "@/types/harness";

interface SpecCardProps {
  items: SpecItem[];
  summary: string;
}

// 전기 스펙 검증 결과
export function SpecCard({ items, summary }: SpecCardProps) {
  return (
    <div className="space-y-4">
      {summary && (
        <p className="text-sm text-muted-foreground">{summary}</p>
      )}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>와이어명</TableHead>
            <TableHead>전류 (A)</TableHead>
            <TableHead>전압 (V)</TableHead>
            <TableHead>전압강하 (V)</TableHead>
            <TableHead>적합 여부</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item, i) => (
            <TableRow key={i}>
              <TableCell className="font-mono text-sm">{item.wireName}</TableCell>
              <TableCell>{item.current.toFixed(2)}</TableCell>
              <TableCell>{item.voltage.toFixed(2)}</TableCell>
              <TableCell>{item.voltageDrop.toFixed(3)}</TableCell>
              <TableCell>
                <Badge variant={item.isAcceptable ? "success" : "destructive"}>
                  {item.isAcceptable ? "적합" : "초과"}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
