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

const DEFAULT_DCA_POINTS: DCAPoint[] = [
  { threshold: 0.05, net_benefit_mcdss: 0.245, net_benefit_tabular: 0.231, net_benefit_text: 0.241, net_benefit_treat_all: 0.211, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 3.4 },
  { threshold: 0.10, net_benefit_mcdss: 0.238, net_benefit_tabular: 0.214, net_benefit_text: 0.230, net_benefit_treat_all: 0.167, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 7.1 },
  { threshold: 0.15, net_benefit_mcdss: 0.229, net_benefit_tabular: 0.198, net_benefit_text: 0.219, net_benefit_treat_all: 0.118, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 11.1 },
  { threshold: 0.20, net_benefit_mcdss: 0.221, net_benefit_tabular: 0.180, net_benefit_text: 0.208, net_benefit_treat_all: 0.063, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 15.8 },
  { threshold: 0.25, net_benefit_mcdss: 0.212, net_benefit_tabular: 0.162, net_benefit_text: 0.196, net_benefit_treat_all: 0.0, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 21.2 },
  { threshold: 0.30, net_benefit_mcdss: 0.201, net_benefit_tabular: 0.141, net_benefit_text: 0.183, net_benefit_treat_all: -0.071, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 20.1 },
  { threshold: 0.35, net_benefit_mcdss: 0.189, net_benefit_tabular: 0.119, net_benefit_text: 0.169, net_benefit_treat_all: -0.154, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 18.9 },
  { threshold: 0.40, net_benefit_mcdss: 0.174, net_benefit_tabular: 0.098, net_benefit_text: 0.151, net_benefit_treat_all: -0.250, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 17.4 },
  { threshold: 0.45, net_benefit_mcdss: 0.158, net_benefit_tabular: 0.074, net_benefit_text: 0.134, net_benefit_treat_all: -0.364, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 15.8 },
  { threshold: 0.50, net_benefit_mcdss: 0.139, net_benefit_tabular: 0.049, net_benefit_text: 0.112, net_benefit_treat_all: -0.500, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 13.9 },
  { threshold: 0.55, net_benefit_mcdss: 0.116, net_benefit_tabular: 0.024, net_benefit_text: 0.089, net_benefit_treat_all: -0.667, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 11.6 },
  { threshold: 0.60, net_benefit_mcdss: 0.091, net_benefit_tabular: 0.002, net_benefit_text: 0.063, net_benefit_treat_all: -0.875, net_benefit_treat_none: 0.0, net_tp_gained_per_100: 9.1 },
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

  // Find point closest to sliderThreshold
  const currentPoint =
    points.find(
      (p) => Math.abs(p.threshold - sliderThreshold) < 0.001
    ) || points[3];

  const deltaOverAll = Math.max(
    0,
    currentPoint.net_benefit_mcdss - currentPoint.net_benefit_treat_all
  );
  const netTpGained =
    currentPoint.net_tp_gained_per_100 ||
    Math.round(deltaOverAll * 1000) / 10;

  const exchangeRatio = sliderThreshold / (1.0 - sliderThreshold);
  const acceptableHarmRatio = Math.round((1.0 - sliderThreshold) / sliderThreshold);

  // Format data for Recharts
  const chartData = points.map((p) => ({
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
            Đường cong minh họa bằng điểm dựng sẵn; chưa đo trên dự đoán từng bệnh nhân.
          </p>
        </div>

        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold self-start sm:self-auto">
          Dải ngưỡng minh họa: pt ∈ [10%, 45%]
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
              So với Treat All: {(currentPoint.net_benefit_treat_all).toFixed(3)}
            </p>
          </div>

          <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-emerald-500/30 bg-emerald-500/5 space-y-1">
            <div className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              <span>Can Thiệp Đúng Tăng Thêm:</span>
            </div>
            <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              +{netTpGained} ca
            </div>
            <p className="text-[10px] text-slate-500 dark:text-slate-400">
              Số ca đúng ròng trên mỗi 100 bệnh nhân
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
          <span>Cách đọc đường cong DCA minh họa:</span>
        </div>
        <p>
          Các điểm dựng sẵn chỉ minh họa cách so sánh lợi ích ròng giữa mô hình,
          can thiệp tất cả và không can thiệp. Cần tính lại từ dự đoán và nhãn
          kiểm thử trước khi đưa ra kết luận lâm sàng.
        </p>
      </div>
    </div>
  );
}
