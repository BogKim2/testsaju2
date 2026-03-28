import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, FileText } from "lucide-react";

interface FileUploadCardProps {
  onSubmit: (file: File, projectName: string) => Promise<void>;
  isLoading?: boolean;
}

// 파일 업로드 + 분석 시작 카드
export function FileUploadCard({ onSubmit, isLoading = false }: FileUploadCardProps) {
  const [file, setFile] = useState<File | null>(null);
  const [projectName, setProjectName] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) setFile(dropped);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !projectName.trim()) return;
    await onSubmit(file, projectName.trim());
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          하네스 도면 분석
        </CardTitle>
        <CardDescription>DXF, Excel, PDF 파일을 업로드하면 AI 에이전트가 자동 분석합니다</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 드래그앤드롭 업로드 영역 */}
          <div
            className={`rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
              dragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
            {file ? (
              <p className="text-sm font-medium">{file.name}</p>
            ) : (
              <>
                <p className="text-sm font-medium">파일을 드래그하거나 클릭하여 선택</p>
                <p className="text-xs text-muted-foreground mt-1">DXF · Excel · PDF 지원</p>
              </>
            )}
            <input
              ref={fileRef}
              type="file"
              accept=".dxf,.xlsx,.xls,.pdf"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="project-name">프로젝트명</Label>
            <Input
              id="project-name"
              placeholder="예: HRN-2024-001"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
            />
          </div>

          <Button type="submit" className="w-full" disabled={!file || !projectName.trim() || isLoading}>
            {isLoading ? "분석 중..." : "AI 분석 시작"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
