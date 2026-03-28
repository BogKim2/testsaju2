import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FileUploadCard } from "@/components/harness/FileUploadCard";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";
import { isLoggedIn } from "@/lib/auth";
import { analyzeHarness } from "@/lib/api";
import { toast } from "sonner";

// 메인 페이지 - 파일 업로드 및 분석 시작
export default function HomePage() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(file: File, projectName: string) {
    setIsLoading(true);
    try {
      const res = await analyzeHarness(file, projectName);
      toast.success("분석을 시작했습니다");
      navigate(`/analyze?id=${res.session_id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "분석 요청 실패");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">하네스 엔지니어링 AI 분석</h1>
        <p className="text-muted-foreground">
          도면 파일을 업로드하면 5개 AI 에이전트가 자동으로 분석합니다
        </p>
        <p className="text-xs text-muted-foreground">LM Studio + Qwen3.5-9B</p>
      </div>

      {!loggedIn && (
        <Alert className="max-w-lg">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>분석하려면 로그인이 필요합니다</span>
            <Button size="sm" asChild className="ml-4">
              <Link to="/login">로그인</Link>
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {loggedIn && <FileUploadCard onSubmit={handleSubmit} isLoading={isLoading} />}
    </div>
  );
}
