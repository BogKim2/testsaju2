// 사주 분석 TypeScript 타입 정의

export interface Pillar {
  gan: string;
  ji: string;
  gan_hanja: string;
  ji_hanja: string;
  gan_ohaeng: string;
  ji_ohaeng: string;
  gan_yangeum: string;
  ji_yangeum: string;
}

export interface Pillars {
  year: Pillar;
  month: Pillar;
  day: Pillar;
  hour: Pillar;
}

export interface OhaengItem {
  count: number;
  hanja: string;
  color: string;
}

export interface OhaengDistribution {
  목: OhaengItem;
  화: OhaengItem;
  토: OhaengItem;
  금: OhaengItem;
  수: OhaengItem;
}

export interface Daewoon {
  age: number;
  gan: string;
  ji: string;
  gan_hanja: string;
  ji_hanja: string;
  gan_ohaeng: string;
  ji_ohaeng: string;
  direction: string;
}

export interface Seun {
  year: number;
  age: number;
  gan: string;
  ji: string;
  gan_hanja: string;
  ji_hanja: string;
  gan_ohaeng: string;
  ji_ohaeng: string;
}

export interface SajuResult {
  session_id: string;
  name: string;
  gender: string;
  birth: {
    year: number;
    month: number;
    day: number;
    hour: number;
  };
  pillars: Pillars;
  ohaeng: OhaengDistribution;
  yangeum: { 양: number; 음: number };
  ilgan: string;
  ilgan_ohaeng: string;
  animal: string;
  daewoon: Daewoon[];
  seun: Seun[];
  interpretation: string;
  created_at: number;
  completed_at: number;
}

export interface AnalysisStatus {
  session_id: string;
  status: "pending" | "running" | "done" | "error";
  progress: number;
  error?: string;
}

export interface HistoryItem {
  session_id: string;
  name: string;
  gender: string;
  birth_year: number;
  birth_month: number;
  birth_day: number;
  animal: string;
  ilgan: string;
  created_at: number;
}

export interface AnalyzeRequest {
  name: string;
  gender: string;
  birth_year: number;
  birth_month: number;
  birth_day: number;
  birth_hour: number;
}
