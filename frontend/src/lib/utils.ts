import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// shadcn/ui 스타일 병합 유틸리티
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 오행 색상 반환
export const OHAENG_COLORS: Record<string, string> = {
  목: "#4CAF50",
  화: "#F44336",
  토: "#FF9800",
  금: "#9E9E9E",
  수: "#2196F3",
};

// 오행 한자 반환
export const OHAENG_HANJA: Record<string, string> = {
  목: "木",
  화: "火",
  토: "土",
  금: "金",
  수: "水",
};

// 타임스탬프를 날짜 문자열로 변환
export function formatDate(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// 시간(0~23)을 한국식 시간 표기로 변환
export function formatHour(hour: number): string {
  if (hour === 0 || hour === 23) return "자시(子時)";
  if (hour <= 2) return "축시(丑時)";
  if (hour <= 4) return "인시(寅時)";
  if (hour <= 6) return "묘시(卯時)";
  if (hour <= 8) return "진시(辰時)";
  if (hour <= 10) return "사시(巳時)";
  if (hour <= 12) return "오시(午時)";
  if (hour <= 14) return "미시(未時)";
  if (hour <= 16) return "신시(申時)";
  if (hour <= 18) return "유시(酉時)";
  if (hour <= 20) return "술시(戌時)";
  return "해시(亥時)";
}
