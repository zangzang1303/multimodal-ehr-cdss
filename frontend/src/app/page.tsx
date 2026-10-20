"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  HeartPulse,
  Moon,
  RefreshCw,
  Sun,
} from "lucide-react";
import { getHealth, HealthResponse } from "@/lib/api";
import PatientDataForm from "@/components/PatientDataForm";

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
        setError("Không thể kết nối tới FastAPI Backend");
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

          {/* Header Action: Ultra-Compact Backend Status Pill & Dark/Light Mode Toggle */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Ultra-compact Backend Status Pill */}
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100/90 dark:bg-slate-900/90 text-xs shadow-sm">
              {loading ? (
                <span className="inline-flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-medium">
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                  <span className="hidden sm:inline">Backend:</span> Kết nối...
                </span>
              ) : health?.status === "healthy" ? (
                <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                  </span>
                  <span className="hidden sm:inline">Backend:</span> Online
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-rose-600 dark:text-rose-400 font-medium">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span className="hidden sm:inline">Backend:</span> Offline
                </span>
              )}

              <button
                onClick={checkBackendHealth}
                disabled={loading}
                title={lastChecked ? `Kiểm tra lại kết nối (Lần cuối: ${lastChecked.toLocaleTimeString()})` : "Kiểm tra kết nối"}
                className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors disabled:opacity-50 ml-0.5"
                aria-label="Kiểm tra lại kết nối backend"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
              </button>
            </div>

            {/* Dark/Light Theme Toggle */}
            <button
              onClick={toggleTheme}
              aria-label="Toggle Theme"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs font-medium"
            >
              {isDark ? (
                <>
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span className="hidden sm:inline">Sáng</span>
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 text-sky-500" />
                  <span className="hidden sm:inline">Tối</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 w-full flex flex-col justify-center">
        {/* Hero Section */}
        <div className="text-center mx-auto mb-6">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-heading font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight mb-2">
            Multimodal Clinical Decision Support System
          </h1>
          <p className="text-base sm:text-lg text-sky-600 dark:text-sky-400 font-medium mb-2">
            Phase 1: Baselines & Research Benchmark
          </p>
          <p className="text-slate-600 dark:text-slate-400 text-xs sm:text-sm leading-relaxed max-w-2xl mx-auto">
            Khung ứng dụng lâm sàng giai đoạn 1 hỗ trợ kết nối dữ liệu bệnh án điện tử đa phương thức
            và đánh giá các mô hình nền tảng đối chứng.
          </p>
        </div>

        {/* Offline Warning Banner if Backend Is Offline */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-300 text-xs flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-500 flex-shrink-0" />
              <span>
                {error}. Đảm bảo dịch vụ FastAPI đang khởi chạy tại{" "}
                <code className="font-mono bg-rose-950/20 px-1 py-0.5 rounded text-[11px]">
                  http://localhost:8000
                </code>
              </span>
            </div>
            <button
              onClick={checkBackendHealth}
              disabled={loading}
              className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-700 dark:text-rose-200 text-[11px] font-semibold transition-colors flex-shrink-0"
            >
              Thử lại
            </button>
          </div>
        )}

        {/* Quick Link to Benchmark Baselines Dashboard */}
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 sm:p-4 rounded-xl bg-gradient-to-r from-sky-500/10 via-emerald-500/5 to-transparent border border-sky-500/20 dark:border-sky-500/30 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center flex-shrink-0 text-sky-600 dark:text-sky-400">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                Dashboard Đối So Sánh 3 Baselines
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20 font-medium">
                  Hold-out Test (N=300)
                </span>
              </div>
              <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                Đối chiếu hiệu năng giữa XGBoost, FT-Transformer và Bio_ClinicalBERT kèm phân tích điểm mù lâm sàng &amp; ECE.
              </p>
            </div>
          </div>

          <Link
            href="/baselines"
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 text-white text-xs font-semibold shadow-sm flex items-center justify-center gap-2 transition-all flex-shrink-0 self-stretch sm:self-auto"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Xem Benchmark Baselines</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Doctor Clinical Intake & 3-Baselines Prediction Form */}
        <div>
          <PatientDataForm />
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
