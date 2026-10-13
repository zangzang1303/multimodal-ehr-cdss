"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  HeartPulse,
  Moon,
  RefreshCw,
  Server,
  Sun,
} from "lucide-react";
import { getHealth, HealthResponse } from "@/lib/api";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [isDark, setIsDark] = useState<boolean>(true);

  // Synchronize component state with document theme applied prior to render
  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  const checkBackendHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err: unknown) {
      setHealth(null);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to connect to FastAPI backend");
      }
    } finally {
      setLastChecked(new Date());
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800/80 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & System Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-emerald-400 p-[2px] shadow-lg shadow-sky-500/20">
              <div className="w-full h-full bg-white dark:bg-slate-950 rounded-[10px] flex items-center justify-center transition-colors">
                <HeartPulse className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
              </div>
            </div>
            <div>
              <span className="font-heading text-lg font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                M-CDSS{" "}
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/30">
                  Phase 1
                </span>
              </span>
              <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
                Clinical Decision Support System
              </p>
            </div>
          </div>

          {/* Header Action: Dark/Light Mode Toggle */}
          <div className="flex items-center space-x-3">
            <button
              onClick={toggleTheme}
              aria-label="Toggle Theme"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs font-medium"
            >
              {isDark ? (
                <>
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span className="hidden sm:inline">Chế độ sáng</span>
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 text-sky-500" />
                  <span className="hidden sm:inline">Chế độ tối</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full flex flex-col justify-center">
        {/* Hero Section */}
        <div className="text-center mx-auto mb-12">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-heading font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight mb-4">
            Multimodal Clinical Decision Support System
          </h1>
          <p className="text-lg sm:text-xl text-sky-600 dark:text-sky-400 font-medium mb-3">
            Phase 1: Baselines & Research Benchmark
          </p>
          <p className="text-slate-600 dark:text-slate-400 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto">
            Khung ứng dụng lâm sàng giai đoạn 1 hỗ trợ kết nối dữ liệu bệnh án điện tử đa phương thức
            và đánh giá các mô hình nền tảng đối chứng.
          </p>
        </div>

        {/* Backend Health Check Card with Online Status Dot */}
        <div className="p-6 sm:p-8 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 shadow-sm backdrop-blur-sm relative overflow-hidden transition-colors">
          <div className="absolute top-0 right-0 w-80 h-80 bg-sky-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center flex-shrink-0">
                <Server className="w-6 h-6 text-sky-600 dark:text-sky-400" />
              </div>
              <div>
                {/* Backend Status with Online Green Dot */}
                {loading ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                    <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                    Đang kết nối...
                  </span>
                ) : health?.status === "healthy" ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    Online
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                    <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                    Offline
                  </span>
                )}

                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    FastAPI Backend Core
                  </h2>
                </div>
              </div>
            </div>

            {/* Actions & Details */}
            <div className="flex sm:flex-row items-center sm:items-center justify-between w-full sm:w-auto gap-3">
              <div className="text-left sm:text-right text-xs text-slate-500 dark:text-slate-400">
                <div>
                  Phiên bản:{" "}
                  <span className="font-mono text-slate-700 dark:text-slate-200">
                    {health ? health.version : "N/A"}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Cập nhật: {lastChecked ? lastChecked.toLocaleTimeString() : "N/A"}
                </div>
              </div>

              <button
                onClick={checkBackendHealth}
                disabled={loading}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 text-white text-xs font-semibold shadow-md shadow-sky-600/20 flex items-center gap-2 transition-all disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                Kiểm tra kết nối
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-500 flex-shrink-0" />
              <span>
                {error}. Đảm bảo dịch vụ FastAPI đang khởi chạy tại{" "}
                <code className="font-mono bg-rose-950/20 px-1 py-0.5 rounded">
                  http://localhost:8000
                </code>
                .
              </span>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-950 py-6 text-center text-xs text-slate-500 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Multimodal Clinical Decision Support System - Phase 1</span>
          </div>
          <div>M-CDSS Research Consortium © 2026. Next.js 14 & FastAPI.</div>
        </div>
      </footer>
    </div>
  );
}
