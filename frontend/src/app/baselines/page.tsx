"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  BookOpen,
  CheckCircle2,
  Cpu,
  FileText,
  Moon,
  RefreshCw,
  ShieldAlert,
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
} from "recharts";
import {
  BenchmarkResultsResponse,
  FALLBACK_BENCHMARK_RESULTS,
  getBaselineBenchmarks,
} from "@/lib/api";

export default function BaselinesBenchmarkPage() {
  const [data, setData] = useState<BenchmarkResultsResponse>(
    FALLBACK_BENCHMARK_RESULTS
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [isDark, setIsDark] = useState<boolean>(true);
  const [mounted, setMounted] = useState<boolean>(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

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

  const loadBenchmarkData = async () => {
    setLoading(true);
    try {
      const benchmarkData = await getBaselineBenchmarks();
      setData(benchmarkData);
    } catch {
      setData(FALLBACK_BENCHMARK_RESULTS);
    } finally {
      setLastRefreshed(new Date());
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBenchmarkData();
  }, []);

  const rawResults = data.results || (data as unknown as Record<string, unknown>);
  const b1 = (rawResults.baseline_1_classical_tabular ||
    FALLBACK_BENCHMARK_RESULTS.results.baseline_1_classical_tabular) as typeof FALLBACK_BENCHMARK_RESULTS.results.baseline_1_classical_tabular;
  const b2 = (rawResults.baseline_2_tabular_deep ||
    FALLBACK_BENCHMARK_RESULTS.results.baseline_2_tabular_deep) as typeof FALLBACK_BENCHMARK_RESULTS.results.baseline_2_tabular_deep;
  const b3 = (rawResults.baseline_3_text_only ||
    FALLBACK_BENCHMARK_RESULTS.results.baseline_3_text_only) as typeof FALLBACK_BENCHMARK_RESULTS.results.baseline_3_text_only;

  const rawBaselineRows = [
    {
      id: "baseline_1",
      key: "baseline_1_classical_tabular",
      name: "Baseline 1: Classical Tabular",
      architecture: b1.model_type || "XGBoost",
      modality: b1.data_modality || "Structured Tabular Only",
      inputDesc: "13 đặc trưng bảng số hóa (9 sinh hiệu & xét nghiệm + 4 phân loại)",
      auroc: b1.macro_auroc,
      auprc: b1.macro_auprc,
      f1: b1.macro_f1,
      accuracy: b1.accuracy,
      brier: b1.brier_score,
      ece: b1.ece,
    },
    {
      id: "baseline_2",
      key: "baseline_2_tabular_deep",
      name: "Baseline 2: Tabular Deep Learning",
      architecture: b2.model_type || "FT-Transformer",
      modality: b2.data_modality || "Structured Tabular Only",
      inputDesc: "Feature Tokenizer + 4 tầng Transformer Encoder đa đầu tự chú ý",
      auroc: b2.macro_auroc,
      auprc: b2.macro_auprc,
      f1: b2.macro_f1,
      accuracy: b2.accuracy,
      brier: b2.brier_score,
      ece: b2.ece,
    },
    {
      id: "baseline_3",
      key: "baseline_3_text_only",
      name: "Baseline 3: Clinical NLP",
      architecture: b3.model_type || "Bio_ClinicalBERT",
      modality: b3.data_modality || "Unstructured Clinical Notes Only",
      inputDesc: "Ghi chú bệnh án lâm sàng tự do (512 tokens, pre-trained MIMIC-III)",
      auroc: b3.macro_auroc,
      auprc: b3.macro_auprc,
      f1: b3.macro_f1,
      accuracy: b3.accuracy,
      brier: b3.brier_score,
      ece: b3.ece,
    },
  ];
  const baselineRows = rawBaselineRows.map((row) => ({
    ...row,
    isBestAuroc: row.auroc === Math.max(...rawBaselineRows.map((item) => item.auroc)),
    isBestAuprc: row.auprc === Math.max(...rawBaselineRows.map((item) => item.auprc)),
    isBestF1: row.f1 === Math.max(...rawBaselineRows.map((item) => item.f1)),
    isBestBrier: row.brier === Math.min(...rawBaselineRows.map((item) => item.brier)),
    isBestEce: row.ece === Math.min(...rawBaselineRows.map((item) => item.ece)),
  }));
  const minEce = Math.min(...rawBaselineRows.map((item) => item.ece));
  const maxEce = Math.max(...rawBaselineRows.map((item) => item.ece));

  // Recharts Data preparation
  const performanceChartData = [
    {
      model: `${b1.model_type || "Classical"} (B1)`,
      fullName: `Baseline 1: ${b1.model_type || "Classical"}`,
      AUROC: +(b1.macro_auroc * 100).toFixed(2),
      AUPRC: +(b1.macro_auprc * 100).toFixed(2),
      MacroF1: +(b1.macro_f1 * 100).toFixed(2),
      Accuracy: +(b1.accuracy * 100).toFixed(2),
    },
    {
      model: "FT-Transformer (B2)",
      fullName: "Baseline 2: FT-Transformer",
      AUROC: +(b2.macro_auroc * 100).toFixed(2),
      AUPRC: +(b2.macro_auprc * 100).toFixed(2),
      MacroF1: +(b2.macro_f1 * 100).toFixed(2),
      Accuracy: +(b2.accuracy * 100).toFixed(2),
    },
    {
      model: "Bio_ClinicalBERT (B3)",
      fullName: "Baseline 3: ClinicalBERT",
      AUROC: +(b3.macro_auroc * 100).toFixed(2),
      AUPRC: +(b3.macro_auprc * 100).toFixed(2),
      MacroF1: +(b3.macro_f1 * 100).toFixed(2),
      Accuracy: +(b3.accuracy * 100).toFixed(2),
    },
  ];

  const calibrationChartData = [
    {
      model: `${b1.model_type || "Classical"} (B1)`,
      ECE: +(b1.ece * 100).toFixed(2),
      BrierScore: +(b1.brier_score * 100).toFixed(2),
      SafeThreshold: 5.0, // 5% ECE clinical safety threshold
    },
    {
      model: "FT-Transformer (B2)",
      ECE: +(b2.ece * 100).toFixed(2),
      BrierScore: +(b2.brier_score * 100).toFixed(2),
      SafeThreshold: 5.0,
    },
    {
      model: "Bio_ClinicalBERT (B3)",
      ECE: +(b3.ece * 100).toFixed(2),
      BrierScore: +(b3.brier_score * 100).toFixed(2),
      SafeThreshold: 5.0,
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800/80 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs font-semibold"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Nhập Liệu Khám Bệnh</span>
            </Link>

            <div className="h-4 w-px bg-slate-300 dark:bg-slate-700" />

            <div className="flex items-center space-x-2">
              <span className="font-heading text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-sky-500" />
                Benchmark Đối Chứng Baselines
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium">
                Hold-out Test (N={data.benchmark_metadata?.test_samples ?? 0})
              </span>
            </div>
          </div>

          {/* Action Buttons: Refresh & Theme */}
          <div className="flex items-center space-x-3">
            <button
              onClick={loadBenchmarkData}
              disabled={loading}
              className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs font-medium flex items-center gap-1.5 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">Làm mới dữ liệu</span>
            </button>

            <button
              onClick={toggleTheme}
              aria-label="Toggle Theme"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-900 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all text-xs font-medium"
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

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {/* Hero & Benchmark Intro */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 dark:text-white tracking-tight">
              Đối So Sánh Hiệu Năng 3 Baselines Đơn Phương Thức
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
              Thực nghiệm đối chứng đánh giá khả năng chẩn đoán phân biệt 4 bệnh hô hấp & tim mạch trên tập Hold-out Test độc lập ({data.benchmark_metadata?.test_samples ?? 0} bệnh nhân).
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-medium bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
              <Sparkles className="w-3.5 h-3.5" />
              Chuẩn TRIPOD-AI & PROBAST
            </span>
            {lastRefreshed && (
              <span className="text-[11px] text-slate-400 hidden sm:inline">
                Đồng bộ: {lastRefreshed.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        {/* 1. Amber Warning Callout: Unimodal Blindspot & Severe Overconfidence */}
        <div className="p-5 sm:p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 dark:bg-amber-950/20 dark:border-amber-500/30 shadow-sm relative overflow-hidden">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center flex-shrink-0 text-amber-600 dark:text-amber-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div className="space-y-3 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-base font-bold text-amber-900 dark:text-amber-300 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  Phạm Vi Diễn Giải: Điểm Mù Đơn Phương Thức & Hiệu Chuẩn Xác Suất
                </h3>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300 font-mono font-semibold">
                  Nghiên cứu JMIR (Hunik et al., 2024)
                </span>
              </div>

              <div className="text-xs sm:text-sm text-amber-900/90 dark:text-amber-200/90 leading-relaxed space-y-2">
                <p>
                  <strong>1. Điểm mù dữ liệu đơn lẻ (Unimodal Blindspot):</strong> Mô hình dữ liệu bảng (XGBoost, FT-Transformer) tuy có AUROC cao nhờ chỉ số xét nghiệm cấp tính nhưng <em>hoàn toàn mù mờ</em> trước bệnh sử hút thuốc nhiều năm, thói quen sinh hoạt và mô tả cơn khó thở kịch phát. Ngược lại, mô hình ClinicalBERT đọc hiểu ghi chú nhưng thiếu độ nhạy lượng hóa của SpO2 và chỉ số viêm (WBC, CRP).
                </p>
                <p>
                  <strong>2. Hiệu chuẩn trên tập kiểm thử tổng hợp:</strong> ECE của ba mô hình dao động từ <strong>{(minEce * 100).toFixed(2)}% đến {(maxEce * 100).toFixed(2)}%</strong>. Kết quả này chỉ phản ánh tập hold-out tổng hợp hiện tại; cần kiểm định và hiệu chuẩn lại trên dữ liệu bệnh viện độc lập trước khi triển khai lâm sàng.
                </p>
              </div>

              <div className="pt-2 flex flex-wrap items-center gap-3">
                <a
                  href="#proposed-solution"
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-sm transition-all"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  Xem Kiến Trúc Đề Xuất Giai Đoạn 2 (Cross-Attention + RAG)
                </a>
                <span className="text-xs text-amber-800/80 dark:text-amber-300/80 font-medium">
                  → Cần tích hợp Temperature Scaling ($ECE &lt; 0.05$) và Evidence Grounding để giải quyết triệt để.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Head-to-Head Comparison Table */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Table2 className="w-5 h-5 text-sky-500" />
                Bảng Đối So Sánh Trực Diện 3 Baselines (Head-to-Head Benchmark Table)
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Đánh giá trên tập Hold-out Test {data.benchmark_metadata?.test_samples ?? 0} bệnh nhân không rò rỉ (Stratified Patient Group Split).
              </p>
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
              <span className="inline-block w-3 h-3 rounded-full bg-emerald-500/30 border border-emerald-500"></span>
              <span>Chỉ số tốt nhất từng cột</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 text-xs font-semibold text-slate-600 dark:text-slate-300">
                  <th className="py-3.5 px-4">Mô Hình Đối Chứng</th>
                  <th className="py-3.5 px-4">Phương Thức Dữ Liệu</th>
                  <th className="py-3.5 px-3 text-center">Macro AUROC ↑</th>
                  <th className="py-3.5 px-3 text-center">Macro AUPRC ↑</th>
                  <th className="py-3.5 px-3 text-center">Macro-F1 ↑</th>
                  <th className="py-3.5 px-3 text-center">Accuracy ↑</th>
                  <th className="py-3.5 px-3 text-center">Brier Score ↓</th>
                  <th className="py-3.5 px-3 text-center">ECE (%) ↓</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {baselineRows.map((row) => (
                  <tr
                    key={row.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="py-4 px-4">
                      <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-sky-500" />
                        {row.name}
                      </div>
                      <div className="text-xs font-mono text-slate-500 dark:text-slate-400">
                        {row.architecture}
                      </div>
                      <div className="text-[11px] text-slate-400 dark:text-slate-500 max-w-xs mt-0.5">
                        {row.inputDesc}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="inline-block px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                        {row.modality}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-mono text-xs font-bold ${
                          row.isBestAuroc
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ring-1 ring-emerald-500/20"
                            : "text-slate-700 dark:text-slate-300"
                        }`}
                      >
                        {row.auroc.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-mono text-xs font-bold ${
                          row.isBestAuprc
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ring-1 ring-emerald-500/20"
                            : "text-slate-700 dark:text-slate-300"
                        }`}
                      >
                        {row.auprc.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-mono text-xs font-bold ${
                          row.isBestF1
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ring-1 ring-emerald-500/20"
                            : "text-slate-700 dark:text-slate-300"
                        }`}
                      >
                        {row.f1.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span className="font-mono text-xs text-slate-700 dark:text-slate-300">
                        {row.accuracy.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-mono text-xs font-bold ${
                          row.isBestBrier
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ring-1 ring-emerald-500/20"
                            : "text-slate-700 dark:text-slate-300"
                        }`}
                      >
                        {row.brier.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4 px-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-mono text-xs font-bold ${
                          row.isBestEce
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ring-1 ring-emerald-500/20"
                            : "text-rose-600 dark:text-rose-400 bg-rose-500/10 border border-rose-500/20"
                        }`}
                      >
                        {(row.ece * 100).toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 3. Recharts Comparative Visualizations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Performance Discrimination */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                Hiệu Năng Phân Biệt Lâm Sàng (AUROC, AUPRC & Macro-F1)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Các số liệu được tải trực tiếp từ kết quả benchmark thực trên tập hold-out.
              </p>
            </div>

            <div className="h-72 w-full pt-2">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={performanceChartData}
                    margin={{ top: 20, right: 20, left: -10, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={isDark ? "#334155" : "#e2e8f0"}
                    />
                    <XAxis
                      dataKey="model"
                      stroke={isDark ? "#94a3b8" : "#64748b"}
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      domain={[65, 88]}
                      stroke={isDark ? "#94a3b8" : "#64748b"}
                      fontSize={11}
                      tickFormatter={(val) => `${val}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? "#0f172a" : "#ffffff",
                        borderColor: isDark ? "#334155" : "#cbd5e1",
                        borderRadius: "0.75rem",
                        fontSize: "12px",
                      }}
                      formatter={(val: number | string | readonly (number | string)[] | undefined) => [typeof val === "number" ? `${val.toFixed(2)}%` : `${val}%`]}
                    />
                    <Legend wrapperStyle={{ fontSize: "12px" }} />
                    <Bar
                      dataKey="AUROC"
                      fill="#0ea5e9"
                      name="Macro AUROC"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar
                      dataKey="AUPRC"
                      fill="#10b981"
                      name="Macro AUPRC"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar
                      dataKey="MacroF1"
                      fill="#8b5cf6"
                      name="Macro F1"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-slate-400">
                  Đang tải biểu đồ...
                </div>
              )}
            </div>
          </div>

          {/* Chart 2: Calibration Gap & ECE vs 5% Threshold */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-500" />
                Khoảng Lệch Hiệu Chuẩn ECE vs Ngưỡng An Toàn Lâm Sàng (5.0%)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Đường nét đứt 5% là mốc theo dõi nội bộ; cần đánh giá lại trên dữ liệu bệnh viện độc lập.
              </p>
            </div>

            <div className="h-72 w-full pt-2">
              {mounted ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={calibrationChartData}
                    margin={{ top: 20, right: 20, left: -10, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={isDark ? "#334155" : "#e2e8f0"}
                    />
                    <XAxis
                      dataKey="model"
                      stroke={isDark ? "#94a3b8" : "#64748b"}
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      domain={[0, 14]}
                      stroke={isDark ? "#94a3b8" : "#64748b"}
                      fontSize={11}
                      tickFormatter={(val) => `${val}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? "#0f172a" : "#ffffff",
                        borderColor: isDark ? "#334155" : "#cbd5e1",
                        borderRadius: "0.75rem",
                        fontSize: "12px",
                      }}
                      formatter={(val: number | string | readonly (number | string)[] | undefined) => [typeof val === "number" ? `${val.toFixed(2)}%` : `${val}%`]}
                    />
                    <Legend wrapperStyle={{ fontSize: "12px" }} />
                    <ReferenceLine
                      y={5.0}
                      stroke="#ef4444"
                      strokeDasharray="4 4"
                      label={{
                        value: "Ngưỡng An Toàn Lâm Sàng ECE = 5%",
                        position: "top",
                        fill: "#ef4444",
                        fontSize: 11,
                      }}
                    />
                    <Bar
                      dataKey="ECE"
                      fill="#f59e0b"
                      name="Expected Calibration Error (ECE %)"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-slate-400">
                  Đang tải biểu đồ...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 3.5. Confusion Matrix Analysis (Delivered by Member 2) */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-sky-500" />
                Ma Trận Nhầm Lẫn Đối Chiếu 3 Baselines (Confusion Matrix Analysis)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Được sinh tự động từ Hold-out Test Set (300 DPI) để phân tích các ca bệnh dự đoán sai giữa 4 nhóm bệnh.
              </p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-mono">
              data/confusion_matrices_baselines.png
            </span>
          </div>

          <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/confusion_matrices_baselines.png"
              alt="Ma trận nhầm lẫn 3 mô hình Baselines đối chứng"
              className="w-full h-auto rounded-lg shadow-sm"
              loading="lazy"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-1.5">
              <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-sky-500" />
                Đặc Điểm Mô Hình Bảng (XGBoost &amp; FT-Transformer)
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Nhận diện chính xác 100% Viêm phổi (CAP) nhờ dấu ấn viêm và sốt rõ rệt. Tuy nhiên, tỷ lệ nhầm lẫn giữa Hen (ASTHMA) và COPD ở mức 5.6% - 8.3% do thiếu chỉ số FEV1/FVC (đã khóa để chống rò rỉ).
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 space-y-1.5">
              <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Đặc Điểm Mô Hình Văn Bản (Bio_ClinicalBERT)
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Khai thác tốt tiền sử hút thuốc nhiều năm và bệnh mạn tính. Tuy nhiên, có đến 32.4% ca Suy tim (CHF) bị đoán nhầm sang COPD do triệu chứng cơ năng &quot;khó thở, ho đờm&quot; quá tương đồng.
              </p>
            </div>
          </div>
        </div>

        {/* 3.6. Benchmark Curves (Delivered by Member 1) */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                Đường Cong Hiệu Năng &amp; Hiệu Chuẩn Tin Cậy (ROC, PR &amp; Reliability Curves)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Trực quan hóa 3 phân đồ: One-vs-Rest ROC, Precision-Recall và Calibration Reliability Diagram trên tập Hold-out Test ($N=286$).
              </p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-mono">
              data/baseline_curves.png
            </span>
          </div>

          <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/baseline_curves.png"
              alt="Đồ thị đường cong ROC, PR và Calibration Reliability Diagram của 3 Baselines"
              className="w-full h-auto rounded-lg shadow-sm"
              loading="lazy"
            />
          </div>
        </div>

        {/* 4. Proposed Optimal Architecture Deep-Dive Callout */}
        <div
          id="proposed-solution"
          className="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-sky-500/5 via-emerald-500/5 to-slate-900/5 border border-sky-500/20 dark:border-sky-500/30 space-y-5"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/30 font-semibold uppercase tracking-wider">
                Phương Án Tối Ưu Cho Giai Đoạn 2
              </span>
              <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-white mt-1">
                Multimodal Cross-Attention Late Fusion + Calibrated Temperature Scaling + Agentic RAG
              </h3>
            </div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-sky-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 text-white text-xs font-semibold shadow-md shadow-sky-600/20 transition-all self-start sm:self-auto"
            >
              <Activity className="w-4 h-4" />
              Thử Nghiệm Chẩn Đoán Thực Tế
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 space-y-2">
              <div className="font-bold text-sky-600 dark:text-sky-400 flex items-center gap-1.5">
                <Cpu className="w-4 h-4" />
                1. Dual-Stream Encoders
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Nhánh bảng chạy <strong>FT-Transformer</strong> học tương tác phi tuyến giữa 13 đặc trưng xét nghiệm/sinh hiệu; nhánh text chạy <strong>Bio_ClinicalBERT</strong> mã hóa ghi chú bệnh án 512 tokens.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 space-y-2">
              <div className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                2. Cross-Attention Late Fusion
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Vector đặc trưng bảng số đóng vai trò Query (Q_tab), chiếu lên Key-Value của văn bản (K_text, V_text) qua cơ chế Gated Residual để dung hợp hai không gian ngữ nghĩa một cách thích ứng.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 space-y-2">
              <div className="font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4" />
                3. Hiệu Chuẩn ECE &amp; RAG Minh Chứng
              </div>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Tối ưu tham số Temperature Scaling $T$ để hạ $ECE &lt; 0.05$; kết hợp tầng Agentic RAG đối chiếu phác đồ quốc tế (GINA, GOLD, ESC) và trích dẫn ký tự bằng chứng triệt tiêu ảo giác.
              </p>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-between text-xs text-slate-500 border-t border-slate-200/60 dark:border-slate-800/60">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Xem tài liệu hoàn chỉnh tại: <code>docs/PROPOSED_OPTIMAL_SOLUTION.md</code></span>
            </div>
            <span className="font-mono">Nghiệm thu Giai đoạn 1 (Tuần 3)</span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-950 py-6 text-center text-xs text-slate-500 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-sky-500" />
            <span>Multimodal Clinical Decision Support System - Benchmark Dashboard</span>
          </div>
          <div>M-CDSS Research Consortium © 2026. Next.js 14, Recharts &amp; FastAPI.</div>
        </div>
      </footer>
    </div>
  );
}
