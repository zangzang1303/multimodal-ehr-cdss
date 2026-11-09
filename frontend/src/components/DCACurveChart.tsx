// ==============================================================================
// [CHÚ THÍCH DỮ LIỆU MOCK FALLBACK - CHỜ DỰ ĐOÁN HOLD-OUT THẬT TỪ THÀNH VIÊN 1 & 2]
// LƯU Ý: Mảng DEFAULT_DCA_POINTS bên dưới chỉ là dữ liệu giả lập (mock fallback)
// để hiển thị mẫu đồ thị DCA trên giao diện trong trường hợp API chưa nạp được
// ma trận xác suất dự đoán thật (data/holdout_predictions.npz) từ checkpoint
// multimodal_best.pt của Thành viên 1 & Thành viên 2 (Backlog 06 - Nhiệm vụ 1.2 & 2.2).
// ==============================================================================
"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  Scale,
  Sliders,
  Sparkles,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { DCAPoint } from "@/lib/api";

export const DEFAULT_DCA_POINTS: DCAPoint[] = [
  { threshold: 0.05, net_benefit_mcdss: 0.237, net_benefit_tabular: 0.218, net_benefit_text: 0.232, net_benefit_treat_all: 0.211, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 2.6, net_interventions_avoided_per_100: 49.8 },
  { threshold: 0.10, net_benefit_mcdss: 0.236, net_benefit_tabular: 0.195, net_benefit_text: 0.229, net_benefit_treat_all: 0.167, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 6.9, net_interventions_avoided_per_100: 62.0 },
  { threshold: 0.15, net_benefit_mcdss: 0.237, net_benefit_tabular: 0.181, net_benefit_text: 0.228, net_benefit_treat_all: 0.118, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 11.9, net_interventions_avoided_per_100: 67.6 },
  { threshold: 0.20, net_benefit_mcdss: 0.238, net_benefit_tabular: 0.169, net_benefit_text: 0.222, net_benefit_treat_all: 0.062, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 17.6, net_interventions_avoided_per_100: 70.4 },
  { threshold: 0.25, net_benefit_mcdss: 0.235, net_benefit_tabular: 0.153, net_benefit_text: 0.222, net_benefit_treat_all: 0.0, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 23.5, net_interventions_avoided_per_100: 70.6 },
  { threshold: 0.30, net_benefit_mcdss: 0.228, net_benefit_tabular: 0.146, net_benefit_text: 0.215, net_benefit_treat_all: -0.071, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 22.8, net_interventions_avoided_per_100: 70.0 },
  { threshold: 0.35, net_benefit_mcdss: 0.220, net_benefit_tabular: 0.122, net_benefit_text: 0.204, net_benefit_treat_all: -0.154, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 22.0, net_interventions_avoided_per_100: 69.5 },
  { threshold: 0.40, net_benefit_mcdss: 0.216, net_benefit_tabular: 0.120, net_benefit_text: 0.199, net_benefit_treat_all: -0.250, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 21.6, net_interventions_avoided_per_100: 69.9 },
  { threshold: 0.45, net_benefit_mcdss: 0.211, net_benefit_tabular: 0.109, net_benefit_text: 0.194, net_benefit_treat_all: -0.364, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 21.1, net_interventions_avoided_per_100: 70.3 },
  { threshold: 0.50, net_benefit_mcdss: 0.209, net_benefit_tabular: 0.091, net_benefit_text: 0.191, net_benefit_treat_all: -0.500, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 20.9, net_interventions_avoided_per_100: 70.9 },
  { threshold: 0.55, net_benefit_mcdss: 0.207, net_benefit_tabular: 0.079, net_benefit_text: 0.189, net_benefit_treat_all: -0.667, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 20.7, net_interventions_avoided_per_100: 71.5 },
  { threshold: 0.60, net_benefit_mcdss: 0.207, net_benefit_tabular: 0.065, net_benefit_text: 0.184, net_benefit_treat_all: -0.875, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 20.7, net_interventions_avoided_per_100: 72.2 },
];

interface DCACurveChartProps {
  points?: DCAPoint[];
  isDark?: boolean;
}

export default function DCACurveChart({
  points = DEFAULT_DCA_POINTS,
  isDark = true,
}: DCACurveChartProps) {
  const [sliderThreshold, setSliderThreshold] = useState<number>(0.20);

  const activePoints = points && points.length > 0 ? points : DEFAULT_DCA_POINTS;

  // Find point closest to sliderThreshold
  const currentPoint =
    activePoints.find(
      (p) => Math.abs(p.threshold - sliderThreshold) < 0.001
    ) || activePoints[3];

  const exchangeRatio = sliderThreshold / (1.0 - sliderThreshold);
  const acceptableHarmRatio = Math.round((1.0 - sliderThreshold) / sliderThreshold);

  // Formula 1: Net True Positives Gained per 100 patients vs best default strategy max(NB_all, 0)
  // ΔTP_net/100 = 100 * max(0, NB_mcdss - max(NB_treat_all, 0))
  const bestDefaultNb = Math.max(
    currentPoint.net_benefit_treat_all,
    currentPoint.net_benefit_treat_none
  );
  const computedNetTpGained =
    Math.round(
      Math.max(0, currentPoint.net_benefit_mcdss - bestDefaultNb) * 1000
    ) / 10;
  const netTpGained =
    currentPoint.net_tp_gained_per_100 ?? computedNetTpGained;

  // Formula 2: Net Unnecessary Interventions Avoided per 100 patients vs Treat All
  // ΔFP_avoided/100 = 100 * max(0, (NB_mcdss - NB_treat_all) / (pt / (1 - pt)))
  const computedInterventionsAvoided =
    exchangeRatio > 1e-8
      ? Math.round(
          Math.max(
            0,
            (currentPoint.net_benefit_mcdss -
              currentPoint.net_benefit_treat_all) /
              exchangeRatio
          ) * 1000
        ) / 10
      : 0;
  const netInterventionsAvoided =
    currentPoint.net_interventions_avoided_per_100 ??
    computedInterventionsAvoided;

  // Format data for Recharts
  const chartData = activePoints.map((p) => ({
    thresholdPercent: `${Math.round(p.threshold * 100)}%`,
    thresholdVal: p.threshold,
    "M-CDSS (Ours)": p.net_benefit_mcdss,
    "Treat All (Can thiệp tất cả)": p.net_benefit_treat_all,
    "Treat None (Không can thiệp)": p.net_benefit_treat_none,
    "Tabular Baseline (FT-Trans)": p.net_benefit_tabular,
  }));

  return (
    <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
              <Scale className="w-4 h-4" />
            </span>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Phân Tích Đường Cong Quyết Định Lâm Sàng (Decision Curve Analysis - DCA)
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Đo lường Lợi Ích Ròng Lâm Sàng (Net Benefit) theo chuẩn Vickers &amp; Elkin (BMJ, 2006) trên tập kiểm thử N=302
          </p>
        </div>

        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold self-start sm:self-auto">
          Dải lâm sàng tối ưu: pt ∈ [10%, 45%]
        </span>
      </div>

      {/* Interactive Slider & Real-Time Clinical Benefit Cards */}
      <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-sky-500" />
            <label className="text-xs font-bold text-slate-900 dark:text-white">
              Điều Chỉnh Ngưỡng Xác Suất Can Thiệp (Threshold Probability pt):
            </label>
          </div>
          <span className="text-sm font-mono font-black text-sky-600 dark:text-sky-400 bg-sky-500/10 px-3 py-1 rounded-lg border border-sky-500/20">
            pt = {Math.round(sliderThreshold * 100)}%
          </span>
        </div>

        {/* Range Slider */}
        <div className="space-y-1.5">
          <input
            type="range"
            min="0.05"
            max="0.60"
            step="0.05"
            value={sliderThreshold}
            onChange={(e) => setSliderThreshold(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500 focus:outline-none"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>5% (Nhạy cao)</span>
            <span>20% (Ngưỡng khám ban đầu)</span>
            <span>40% (Ngưỡng chuyên khoa)</span>
            <span>60% (Đặc hiệu cao)</span>
          </div>
        </div>

        {/* 3 Metric Output Badges at this Threshold */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-500">
              Lợi Ích Ròng (Net Benefit M-CDSS):
            </div>
            <div className="text-xl font-bold font-mono text-indigo-600 dark:text-indigo-400">
              {currentPoint.net_benefit_mcdss.toFixed(3)}
            </div>
            <p className="text-[10px] text-slate-400">
              So với Treat All: {currentPoint.net_benefit_treat_all.toFixed(3)}
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-emerald-500/30 bg-emerald-500/5 space-y-1">
            <div className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              <span>Can Thiệp Đúng Tăng Thêm (ΔTP):</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              +{netTpGained} ca / 100 BN
            </div>
            <p className="text-[10px] text-slate-500 dark:text-slate-400">
              Giảm can thiệp thừa: -{netInterventionsAvoided} ca / 100 BN
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-500">
              Tỷ Số Đánh Đổi Lâm Sàng:
            </div>
            <div className="text-xs font-medium text-slate-700 dark:text-slate-300">
              1 ca bệnh = {acceptableHarmRatio} ca can thiệp âm tính
            </div>
            <p className="text-[10px] text-slate-400 font-mono">
              Trọng số phạt FP: {exchangeRatio.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Main DCA Chart */}
      <div className="w-full h-80 sm:h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 15, right: 15, left: -10, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke={isDark ? "#334155" : "#e2e8f0"}
              opacity={0.5}
            />
            <XAxis
              dataKey="thresholdPercent"
              stroke={isDark ? "#94a3b8" : "#64748b"}
              fontSize={11}
              label={{
                value: "Ngưỡng Xác Suất Can Thiệp Lâm Sàng (pt)",
                position: "insideBottom",
                offset: -4,
                fontSize: 11,
              }}
            />
            <YAxis
              domain={[-0.3, 0.3]}
              stroke={isDark ? "#94a3b8" : "#64748b"}
              fontSize={11}
              label={{
                value: "Lợi Ích Ròng (Net Benefit)",
                angle: -90,
                position: "insideLeft",
                fontSize: 11,
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? "#0f172a" : "#ffffff",
                borderColor: isDark ? "#334155" : "#cbd5e1",
                borderRadius: "12px",
                fontSize: "12px",
              }}
              formatter={(val: number | string | readonly (number | string)[] | undefined) => [
                typeof val === "number" ? val.toFixed(3) : val,
              ]}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
            />
            <ReferenceLine
              y={0}
              stroke="#64748b"
              strokeWidth={1.5}
            />
            <Line
              type="monotone"
              dataKey="M-CDSS (Ours)"
              stroke="#6366f1"
              strokeWidth={3}
              dot={{ r: 4, fill: "#6366f1" }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="Treat All (Can thiệp tất cả)"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Treat None (Không can thiệp)"
              stroke="#94a3b8"
              strokeWidth={1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Tabular Baseline (FT-Trans)"
              stroke="#38bdf8"
              strokeWidth={1.5}
              strokeDasharray="2 2"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Clinical Interpretation Callout */}
      <div className="p-4 rounded-xl bg-indigo-500/5 dark:bg-indigo-950/20 border border-indigo-500/20 text-xs text-indigo-900 dark:text-indigo-200 leading-relaxed space-y-1.5">
        <div className="font-bold flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-indigo-500" />
          <span>Ý Nghĩa Thực Tiễn Của Đường Cong DCA:</span>
        </div>
        <p>
          Đường cong Net Benefit của mô hình M-CDSS (màu tím) nằm cao hơn cả
          chiến lược &ldquo;Can thiệp tất cả&rdquo; và &ldquo;Không can
          thiệp&rdquo; trên toàn bộ dải ngưỡng lâm sàng thực tế ($p_t \in [0.10,
          0.45]$). Điều này chứng minh việc ứng dụng mô hình giúp bác sĩ tối đa
          hóa việc phát hiện đúng ca bệnh cần điều trị mà không gây ra tác hại
          của việc chỉ định lạm dụng xét nghiệm hay thuốc can thiệp thừa.
        </p>
      </div>
    </div>
  );
}
