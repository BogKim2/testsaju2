import { BrowserRouter, Routes, Route, Navigate, Outlet, useNavigate } from "react-router-dom";
import { Toaster } from "sonner";
import { LoginPage } from "@/pages/LoginPage";
import { HomePage } from "@/pages/HomePage";
import { AnalyzePage } from "@/pages/AnalyzePage";
import { ResultPage } from "@/pages/ResultPage";
import { HistoryPage } from "@/pages/HistoryPage";
import { isLoggedIn, removeToken, getEmail } from "@/lib/auth";
import { Star, LogOut, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate as useNav } from "react-router-dom";

// 인증 가드
function RequireAuth() {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container max-w-5xl mx-auto px-4 py-4">
        <Outlet />
      </main>
      <footer className="border-t border-border py-4 text-center text-xs text-muted-foreground">
        사주 분석 © 2026 — AI 기반 사주 명리 풀이 서비스
      </footer>
    </div>
  );
}

function Header() {
  const nav = useNav();

  const handleLogout = () => {
    removeToken();
    nav("/login");
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="container max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* 로고 */}
        <button
          onClick={() => nav("/")}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <Star className="w-6 h-6 text-primary" />
          <span className="font-bold text-lg text-gradient">사주 분석</span>
          <span className="text-xs text-muted-foreground hidden sm:block">四柱分析</span>
        </button>

        {/* 네비게이션 */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => nav("/history")}
            className="gap-1.5"
          >
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">이력</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">로그아웃</span>
          </Button>
        </div>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster theme="dark" position="top-right" richColors />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<RequireAuth />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze/:sessionId" element={<AnalyzePage />} />
          <Route path="/result/:sessionId" element={<ResultPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
