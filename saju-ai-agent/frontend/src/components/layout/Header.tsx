import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { LogOut, History, Zap } from "lucide-react";
import { isLoggedIn, clearToken } from "@/lib/auth";

// 상단 헤더 내비게이션
export function Header() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();

  function handleLogout() {
    clearToken();
    navigate("/login");
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur">
      <div className="container mx-auto flex h-14 items-center px-4">
        {/* 로고 */}
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Zap className="h-5 w-5 text-primary" />
          <span>Harness Eng AI</span>
        </Link>

        <Separator orientation="vertical" className="mx-4 h-5" />

        {/* 내비게이션 */}
        <nav className="flex items-center gap-1 flex-1">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/">분석 시작</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/history">
              <History className="h-4 w-4 mr-1" />
              이력
            </Link>
          </Button>
        </nav>

        {/* 로그인/로그아웃 */}
        {loggedIn ? (
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="h-4 w-4 mr-1" />
            로그아웃
          </Button>
        ) : (
          <Button size="sm" asChild>
            <Link to="/login">로그인</Link>
          </Button>
        )}
      </div>
    </header>
  );
}
