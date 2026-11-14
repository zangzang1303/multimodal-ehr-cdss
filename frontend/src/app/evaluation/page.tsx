"use client";

import DCACurveChart from "@/components/DCACurveChart";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  Cpu,
  Info,
  Moon,
  RefreshCw,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sun,
  Table2,
  TrendingUp,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import {
  AblationStudyResponse,
  DCAPoint,
  FALLBACK_ABLATION_RESULTS,
  getAblationBenchmarks,
  getClinicalEvaluationBenchmark,
} from "@/lib/api";

export default function AblationEvaluationPage() {
  const [data, setData] = useState<AblationStudyResponse>(
    FALLBACK_ABLATION_RESULTS
  );
  const [dcaPoints, setDcaPoints] = useState<DCAPoint[]>([]);
  const [dcaStatus, setDcaStatus] = useState<string>("illustrative_simulation_pending_patient_level_predictions");
  const [loading, setLoading] = useState<boolean>(true);
  const [isDark, setIsDark] = useState<boolean>(true);
  const [mounted, setMounted] = useState<boolean>(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);
  const [activeTab, setActiveTab] = useState<"ablation" | "dca">("ablation");

  useEffect(() => {
    setMounted(true);
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

  const loadAblationData = async () => {
    setLoading(true);
    try {
      const [ablationRes, evalRes] = await Promise.all([
        getAblationBenchmarks(),
        getClinicalEvaluationBenchmark().catch(() => null),
      ]);
      setData(ablationRes);
      if (evalRes?.decision_curve_analysis?.threshold_points?.length) {
        setDcaPoints(evalRes.decision_curve_analysis.threshold_points);
        setDcaStatus(evalRes.evaluation_metadata.dca_status ?? "illustrative_simulation_pending_patient_level_predictions");
      }
    } catch {
      setData(FALLBACK_ABLATION_RESULTS);
      setDcaPoints([]);
      setDcaStatus("illustrative_simulation_pending_patient_level_predictions");
    } finally {
      setLastRefreshed(new Date());
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAblationData();
  }, []);

  // Format data for Recharts BarChart comparing AUROC, F1, Accuracy
  const performanceChartData = [
    {
      name: "Tabular-only",
      fullName: "FT-Transformer (Tabular)",
      AUROC: Number((data.models.tabular_only.macro_auroc * 100).toFixed(2)),
      AUPRC: Number((data.models.tabular_only.macro_auprc * 100).toFixed(2)),
      F1: Number((data.models.tabular_only.macro_f1 * 100).toFixed(2)),
      Accuracy: Number((data.models.tabular_only.accuracy * 100).toFixed(2)),
    },
    {
      name: "Text-only",
      fullName: "Bio_ClinicalBERT (Text)",
      AUROC: Number((data.models.text_only.macro_auroc * 100).toFixed(2)),
      AUPRC: Number((data.models.text_only.macro_auprc * 100).toFixed(2)),
      F1: Number((data.models.text_only.macro_f1 * 100).toFixed(2)),
      Accuracy: Number((data.models.text_only.accuracy * 100).toFixed(2)),
    },
    {
      name: "Concat Fusion",
      fullName: "Concat (h_tab || h_text)",
      AUROC: Number((data.models.concat_fusion.macro_auroc * 100).toFixed(2)),
      AUPRC: Number((data.models.concat_fusion.macro_auprc * 100).toFixed(2)),
      F1: Number((data.models.concat_fusion.macro_f1 * 100).toFixed(2)),
      Accuracy: Number((data.models.concat_fusion.accuracy * 100).toFixed(2)),
    },
    {
      name: "Cross-Attention",
      fullName: "Cross-Attention Gated (Ours)",
      AUROC: Number((data.models.cross_attention_fusion.macro_auroc * 100).toFixed(2)),
      AUPRC: Number((data.models.cross_attention_fusion.macro_auprc * 100).toFixed(2)),
      F1: Number((data.models.cross_attention_fusion.macro_f1 * 100).toFixed(2)),
      Accuracy: Number((data.models.cross_attention_fusion.accuracy * 100).toFixed(2)),
    },
  ];

  // Format data for ECE calibration comparison chart
  const calibrationChartData = [
    {
      name: "Tabular-only",
      fullName: "FT-Transformer",
      ECE: Number((data.models.tabular_only.ece * 100).toFixed(2)),
      Brier: Number((data.models.tabular_only.brier_score * 100).toFixed(2)),
      fill: "#38bdf8",
    },
    {
      name: "Text-only",
      fullName: "Bio_ClinicalBERT",
      ECE: Number((data.models.text_only.ece * 100).toFixed(2)),
      Brier: Number((data.models.text_only.brier_score * 100).toFixed(2)),
      fill: "#34d399",
    },
    {
      name: "Concat Fusion",
      fullName: "Concat Fusion",
      ECE: Number((data.models.concat_fusion.ece * 100).toFixed(2)),
      Brier: Number((data.models.concat_fusion.brier_score * 100).toFixed(2)),
      fill: "#f59e0b",
    },
    {
      name: "Cross-Attention",
      fullName: "Cross-Attention (Ours)",
      ECE: Number((data.models.cross_attention_fusion.ece * 100).toFixed(2)),
      Brier: Number((data.models.cross_attention_fusion.brier_score * 100).toFixed(2)),
      fill: "#6366f1",
    },
  ];

  const modelsList = [
    data.models.tabular_only,
    data.models.text_only,
    data.models.concat_fusion,
    data.models.cross_attention_fusion,
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Sticky Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800/80 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs flex items-center gap-1.5"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Trang Chủ</span>
            </Link>

            <div className="h-5 w-[1px] bg-slate-200 dark:bg-slate-800" />

            <div className="flex items-center gap-2">
              <span className="font-heading text-base sm:text-lg font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
                Ablation Study
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30">
                  Backlog 04
                </span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-3">
            <Link
              href="/baselines"
              className="px-3 py-1.5 rounded-xl border border-sky-200 dark:border-sky-800/60 bg-sky-50 dark:bg-sky-950/30 text-sky-700 dark:text-sky-300 text-xs font-semibold hover:bg-sky-100 dark:hover:bg-sky-900/40 transition-all flex items-center gap-1.5"
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Xem 3 Baselines</span>
            </Link>

            <button
              onClick={loadAblationData}
              disabled={loading}
              title={lastRefreshed ? `Làm mới (Lần cuối: ${lastRefreshed.toLocaleTimeString()})` : "Làm mới dữ liệu"}
              className="p-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors disabled:opacity-50"
              aria-label="Tải lại dữ liệu ablation"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>

            <button
              onClick={toggleTheme}
              aria-label="Chuyển chế độ sáng/tối"
              className="p-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-all"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-sky-500" />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {/* Hero Banner */}
        <div className="relative p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-900/10 via-sky-900/5 to-emerald-900/10 border border-indigo-500/20 dark:border-indigo-500/30 overflow-hidden shadow-sm">
          <div className="max-w-3xl space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              Nghiên Cứu Đánh Giá Thành Phần Đa Phương Thức (Ablation Benchmark)
            </div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 dark:text-white tracking-tight">
              Ablation Study: Tabular vs Text vs Concat vs Cross-Attention
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Khảo sát thực nghiệm đối chứng vai trò của cơ chế chú ý liên phương thức (Cross-Attention)
              và hiệu chuẩn Temperature Scaling trên tập kiểm thử độc lập ({data.experiment_metadata.test_samples} mẫu, phân tách nhóm bệnh nhân theo dữ liệu hiện hành).
            </p>
          </div>
        </div>

        {/* Methodological Context & Scope Callout */}
        <div className="p-4 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-xs text-sky-800 dark:text-sky-300 leading-relaxed flex items-start gap-3">
          <Info className="w-4 h-4 text-sky-600 dark:text-sky-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Phạm vi nghiên cứu &amp; Tuyên bố y đức:</span>{" "}
            Các chỉ số đánh giá được ghi nhận trên tập dữ liệu kiểm thử chuẩn hóa nội bộ (N=302 mẫu, nguồn Synthea &amp; MTSamples). Hệ thống đóng vai trò nguyên mẫu hỗ trợ quyết định (CDSS) phục vụ mục đích nghiên cứu học thuật, không thay thế chẩn đoán chuyên môn của bác sĩ và cần tiếp tục kiểm định độc lập trên dữ liệu lâm sàng thực tế tại bệnh viện.
          </div>
        </div>

        {/* Evaluation View Mode Tabs: Ablation Benchmarks vs Clinical DCA & PROBAST */}
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
          <button
            type="button"
            onClick={() => setActiveTab("ablation")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === "ablation"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800"
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>1. Thử Nghiệm Ablation &amp; Hiệu Chuẩn ECE</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("dca")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === "dca"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800"
            }`}
          >
            <Scale className="w-4 h-4" />
            <span>2. Minh họa DCA &amp; khung PROBAST (Backlog 06)</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-normal">
              Minh họa
            </span>
          </button>
        </div>

        {activeTab === "dca" ? (
          <div className="space-y-8 animate-in fade-in duration-200">
            {/* Interactive DCA Curve Component */}
            <DCACurveChart points={dcaPoints} isDark={isDark} dcaStatus={dcaStatus} />

            {/* PROBAST 4 Domains Compliance Matrix */}
            <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-500" />
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Bảng Thẩm Định 20 Tiêu Chí PROBAST (Prediction Model Risk of Bias Assessment)
                  </h3>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold border border-emerald-500/20">
                  Chưa có đánh giá PROBAST độc lập
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2">
                  <div className="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>Miền 1: Người Tham Gia (Participants)</span>
                    <span className="text-slate-500 font-bold">Chưa đánh giá</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                    Cần mô tả nguồn dữ liệu, tiêu chí chọn mẫu và khả năng áp dụng cho quần thể bệnh nhân thực tế.
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2">
                  <div className="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>Miền 2: Biến Dự Đoán (Predictors)</span>
                    <span className="text-slate-500 font-bold">Chưa đánh giá</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                    Cần kiểm tra mốc thời gian của từng biến và chứng minh không có rò rỉ thông tin sau chẩn đoán.
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2">
                  <div className="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>Miền 3: Kết Cục Chẩn Đoán (Outcome)</span>
                    <span className="text-slate-500 font-bold">Chưa đánh giá</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                    Cần kiểm tra quy trình gán nhãn và mức độ độc lập giữa người gán nhãn với dự đoán mô hình.
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2">
                  <div className="font-bold text-slate-900 dark:text-white flex items-center justify-between">
                    <span>Miền 4: Phân Tích Số Liệu (Analysis)</span>
                    <span className="text-slate-500 font-bold">Chưa đánh giá</span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                    Cần đánh giá sai lệch, hiệu chuẩn, thiếu dữ liệu và kiểm định ngoài trước khi chấm mức nguy cơ.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8 animate-in fade-in duration-200">
            {/* 4 Summary Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl border border-indigo-200 dark:border-indigo-900/50 bg-white dark:bg-slate-900 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>Độ Tăng Trưởng AUROC</span>
              <TrendingUp className="w-4 h-4 text-indigo-500" />
            </div>
            <div className="text-2xl sm:text-3xl font-black font-mono text-indigo-600 dark:text-indigo-400">
              +{(data.key_findings.auroc_gain_over_tabular * 100).toFixed(2)}%
            </div>
            <p className="text-[11px] text-slate-500">
              Kết quả lấy từ artifact huấn luyện strict split hiện hành.
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-emerald-200 dark:border-emerald-900/50 bg-white dark:bg-slate-900 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>Macro AUROC Tốt Nhất</span>
              <Sparkles className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl sm:text-3xl font-black font-mono text-emerald-600 dark:text-emerald-400">
              {(data.models.cross_attention_fusion.macro_auroc * 100).toFixed(2)}%
            </div>
            <p className="text-[11px] text-slate-500">
              Cấu hình Cross-Attention Gated Fusion (Ours).
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-sky-200 dark:border-sky-900/50 bg-white dark:bg-slate-900 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>Macro F1-Score Đạt Được</span>
              <Activity className="w-4 h-4 text-sky-500" />
            </div>
            <div className="text-2xl sm:text-3xl font-black font-mono text-sky-600 dark:text-sky-400">
              {(data.models.cross_attention_fusion.macro_f1 * 100).toFixed(2)}%
            </div>
            <p className="text-[11px] text-slate-500">
              So sánh với các cấu hình khác trên cùng tập kiểm thử.
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-teal-200 dark:border-teal-900/50 bg-white dark:bg-slate-900 shadow-sm space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
              <span>Độ Hiệu Chuẩn ECE</span>
              <ShieldCheck className="w-4 h-4 text-teal-500" />
            </div>
            <div className="text-2xl sm:text-3xl font-black font-mono text-teal-600 dark:text-teal-400">
              {(data.models.cross_attention_fusion.ece * 100).toFixed(2)}%
            </div>
            <p className="text-[11px] text-slate-500">
              ECE của cấu hình này theo tập kiểm thử hiện hành.
            </p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Performance Bar Chart */}
          <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-sky-500" />
                  So Sánh Năng Lực Phân Biệt &amp; Độ Chính Xác (%)
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Đối chứng giữa 4 cấu hình mô hình trên tập kiểm thử độc lập (N=302).
                </p>
              </div>
            </div>

            {mounted && (
              <div className="w-full h-72 sm:h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceChartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis domain={[50, 100]} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? "#0f172a" : "#ffffff",
                        borderColor: isDark ? "#334155" : "#e2e8f0",
                        borderRadius: "12px",
                        fontSize: "12px",
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                    <Bar dataKey="AUROC" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Macro AUROC" />
                    <Bar dataKey="F1" fill="#34d399" radius={[4, 4, 0, 0]} name="Macro F1" />
                    <Bar dataKey="Accuracy" fill="#818cf8" radius={[4, 4, 0, 0]} name="Accuracy" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Chart 2: ECE Calibration Chart */}
          <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-emerald-500" />
                  Sai Lệch Hiệu Chuẩn ECE (Thấp Hơn Là Tốt Hơn)
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Đường nét đứt màu đỏ biểu thị ngưỡng khuyến nghị tham khảo (ECE = 5.0%).
                </p>
              </div>
            </div>

            {mounted && (
              <div className="w-full h-72 sm:h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={calibrationChartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 14]} tick={{ fontSize: 11 }} label={{ value: "ECE (%)", angle: -90, position: "insideLeft", fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? "#0f172a" : "#ffffff",
                        borderColor: isDark ? "#334155" : "#e2e8f0",
                        borderRadius: "12px",
                        fontSize: "12px",
                      }}
                    />
                    <ReferenceLine y={5.0} stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Ngưỡng ECE < 5%", fill: "#ef4444", fontSize: 10, position: "top" }} />
                    <Bar dataKey="ECE" radius={[4, 4, 0, 0]} name="ECE (%)">
                      {calibrationChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {/* Detailed Metrics Comparison Table */}
        <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Table2 className="w-4 h-4 text-indigo-500" />
              Bảng Tổng Hợp Chỉ Số Thực Nghiệm Ablation (Ablation Matrix)
            </h3>
            <span className="text-xs text-slate-500">Hold-out Test Set (N=302)</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 font-semibold">
                  <th className="py-3 px-3">Cấu Hình Mô Hình</th>
                  <th className="py-3 px-3">Phương Thức Dữ Liệu</th>
                  <th className="py-3 px-3 text-right">Macro AUROC</th>
                  <th className="py-3 px-3 text-right">Macro AUPRC</th>
                  <th className="py-3 px-3 text-right">Macro F1</th>
                  <th className="py-3 px-3 text-right">Accuracy</th>
                  <th className="py-3 px-3 text-right">Brier Score</th>
                  <th className="py-3 px-3 text-right">ECE</th>
                  <th className="py-3 px-3 text-right">Δ AUROC vs Tabular</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
                {modelsList.map((m) => {
                  const isBest = m.id === "cross_attention_fusion";
                  return (
                    <tr
                      key={m.id}
                      className={`transition-colors ${
                        isBest
                          ? "bg-indigo-500/5 dark:bg-indigo-950/20 font-semibold text-indigo-900 dark:text-indigo-200"
                          : "hover:bg-slate-50 dark:hover:bg-slate-800/40 text-slate-700 dark:text-slate-300"
                      }`}
                    >
                      <td className="py-3.5 px-3 font-sans font-medium flex items-center gap-2">
                        {isBest && <Sparkles className="w-3.5 h-3.5 text-indigo-500 flex-shrink-0" />}
                        <span>{m.name}</span>
                      </td>
                      <td className="py-3.5 px-3 font-sans text-slate-500 text-[11px]">{m.modality}</td>
                      <td className="py-3.5 px-3 text-right font-bold">
                        {m.macro_auroc.toFixed(4)}
                      </td>
                      <td className="py-3.5 px-3 text-right">{m.macro_auprc.toFixed(4)}</td>
                      <td className="py-3.5 px-3 text-right">{m.macro_f1.toFixed(4)}</td>
                      <td className="py-3.5 px-3 text-right">{m.accuracy.toFixed(4)}</td>
                      <td className="py-3.5 px-3 text-right">{m.brier_score.toFixed(4)}</td>
                      <td className="py-3.5 px-3 text-right">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] ${
                            m.ece < 0.05
                              ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold"
                              : "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                          }`}
                        >
                          {m.ece.toFixed(4)}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        {m.net_gain_auroc && m.net_gain_auroc > 0 ? (
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                            +{(m.net_gain_auroc * 100).toFixed(2)}%
                          </span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Technical Insights & Hypotheses Validated */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <Scale className="w-4 h-4 text-sky-500" />
              <span>Tại sao Concat kém hơn Cross-Attention?</span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Mô hình Concat ghép phẳng hai vector [h_tab || h_text] nhưng chưa khai thác được tương tác ma trận chú ý chéo giữa chỉ số số học và từ vựng lâm sàng, ghi nhận AUROC thấp hơn (-0.0263) so với Cross-Attention trên tập kiểm thử này.
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <Cpu className="w-4 h-4 text-emerald-500" />
              <span>Vai trò &ldquo;Mỏ neo huyết động học&rdquo;</span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Dữ liệu bảng cung cấp các trị số sinh tồn định lượng khách quan, hỗ trợ ổn định dự đoán và giảm thiểu nguy cơ chệch hướng khi văn bản lâm sàng có nhiều từ vựng bệnh cảnh nặng (như trường hợp ca PT-0254).
            </p>
          </div>

          <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
              <ShieldCheck className="w-4 h-4 text-indigo-500" />
              <span>Hiệu chuẩn Temperature Scaling</span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              10.13% xuống 9.73% theo artifact hiện hành.
            </p>
          </div>
        </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>M-CDSS Backlog 04 &amp; 06 — Multimodal Core, Ablation Study &amp; Clinical DCA</span>
          </div>
          <div>M-CDSS Research Consortium © 2026. Next.js 14 &amp; FastAPI.</div>
        </div>
      </footer>
    </div>
  );
}
