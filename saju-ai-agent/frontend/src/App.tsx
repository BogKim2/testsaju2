import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/layout/Header";
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import AnalyzePage from "@/pages/AnalyzePage";
import ResultPage from "@/pages/ResultPage";
import HistoryPage from "@/pages/HistoryPage";
import DesignPage from "@/pages/result/DesignPage";
import BomPage from "@/pages/result/BomPage";
import SpecPage from "@/pages/result/SpecPage";
import QualityPage from "@/pages/result/QualityPage";
import RoutingPage from "@/pages/result/RoutingPage";

// 앱 라우팅 설정
export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/result/:id" element={<ResultPage />} />
            <Route path="/result/:id/design" element={<DesignPage />} />
            <Route path="/result/:id/bom" element={<BomPage />} />
            <Route path="/result/:id/spec" element={<SpecPage />} />
            <Route path="/result/:id/quality" element={<QualityPage />} />
            <Route path="/result/:id/routing" element={<RoutingPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </BrowserRouter>
  );
}
