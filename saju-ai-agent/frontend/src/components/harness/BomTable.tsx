import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { BomItem } from "@/types/harness";

function bomStatusVariant(status: BomItem["status"]) {
  if (status === "OK") return "success" as const;
  if (status === "WARNING") return "warning" as const;
  return "destructive" as const;
}

interface BomTableProps {
  items: BomItem[];
}

// BOM 검증 테이블
export function BomTable({ items }: BomTableProps) {
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground text-center py-4">BOM 항목이 없습니다</p>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>부품번호</TableHead>
          <TableHead>설명</TableHead>
          <TableHead>수량</TableHead>
          <TableHead>단위</TableHead>
          <TableHead>규격</TableHead>
          <TableHead>상태</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) => (
          <TableRow key={item.partNumber}>
            <TableCell className="font-mono text-sm">{item.partNumber}</TableCell>
            <TableCell>{item.description}</TableCell>
            <TableCell>{item.quantity}</TableCell>
            <TableCell>{item.unit}</TableCell>
            <TableCell className="text-muted-foreground">{item.standard}</TableCell>
            <TableCell><Badge variant={bomStatusVariant(item.status)}>{item.status}</Badge></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
