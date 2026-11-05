"use client";

import React, { useState } from "react";
import {
    Activity,
    ChevronDown,
    ChevronUp,
    Cpu,
    FileText,
    HelpCircle,
    Info,
    Layers,
    RotateCcw,
    Scale,
    ShieldCheck,
    Sparkles,
} from "lucide-react";
import { MultimodalMockResponse } from "@/lib/api";

interface DiagnosticCardProps {
    result: MultimodalMockResponse;
    onReset?: () => void;
}

export default function DiagnosticCard({
    result,
    onReset,
}: DiagnosticCardProps) {
    const [showTooltip, setShowTooltip] = useState<boolean>(false);
    const [showStreamDetails, setShowStreamDetails] = useState<boolean>(true);

    // Helper function to return styling according to the 3 risk bands
    const getRiskBandConfig = (percentage: number) => {
        if (percentage >= 70) {
            return {
                label: "Nguy cơ cao",
                tier: "high",
                textColor: "text-rose-600 dark:text-rose-400",
                bgColor: "bg-rose-500",
                badgeBg:
                    "bg-rose-500/10 text-rose-700 dark:text-rose-300 border-rose-500/20",
                barColor: "bg-gradient-to-r from-rose-500 to-rose-600",
            };
        }
        if (percentage >= 30) {
            return {
                label: "Nguy cơ trung bình",
                tier: "moderate",
                textColor: "text-amber-600 dark:text-amber-400",
                bgColor: "bg-amber-500",
                badgeBg:
                    "bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/20",
                barColor: "bg-gradient-to-r from-amber-500 to-amber-600",
            };
        }
        return {
            label: "Nguy cơ thấp",
            tier: "low",
            textColor: "text-emerald-600 dark:text-emerald-400",
            bgColor: "bg-emerald-500",
            badgeBg:
                "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/20",
            barColor: "bg-gradient-to-r from-emerald-500 to-emerald-600",
        };
    };

    const topPrediction = result.top_k_predictions[0] || {
        disease: result.predicted_disease,
        disease_name: result.predicted_disease_name,
        probability: result.confidence,
        percentage: Math.round(result.confidence * 1000) / 10,
        risk_level: "high",
    };

    const topBand = getRiskBandConfig(topPrediction.percentage);

    return (
        <div
            id="diagnostic-card-root"
            className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl overflow-hidden transition-all duration-300 animate-in fade-in slide-in-from-bottom-2"
        >
            {/* Card Header & Primary Diagnostic Summary */}
            <div className="p-6 bg-gradient-to-br from-slate-50 via-white to-sky-50/30 dark:from-slate-900 dark:via-slate-900 dark:to-sky-950/20 border-b border-slate-100 dark:border-slate-800">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                    <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/10 text-sky-700 dark:text-sky-300 border border-sky-500/20">
                            <Sparkles className="w-3.5 h-3.5 text-sky-500" />
                            M-CDSS Multimodal Core (Phase 2)
                        </span>
                        <span className="text-xs text-slate-500 dark:text-slate-400">
                            ID:{" "}
                            <strong className="font-mono text-slate-700 dark:text-slate-300">
                                {result.patient_id}
                            </strong>
                        </span>
                    </div>

                    {/* Calibrated Confidence Badge with Interactive Tooltip */}
                    <div className="flex items-center gap-2">
                        {onReset && (
                            <button
                                type="button"
                                onClick={onReset}
                                title="Làm mới phiếu kết quả"
                                className="p-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 text-xs transition-colors"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                            </button>
                        )}
                        <div className="relative inline-block">
                            <button
                                type="button"
                                id="badge-calibrated-confidence"
                                onMouseEnter={() => setShowTooltip(true)}
                                onMouseLeave={() => setShowTooltip(false)}
                                onClick={() => setShowTooltip(!showTooltip)}
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 shadow-sm transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                                aria-label="Xem giải thích hiệu chuẩn xác suất"
                            >
                                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                                <span>Calibrated Confidence</span>
                                <HelpCircle className="w-3 h-3 text-emerald-600/70" />
                            </button>

                            {/* Tooltip popover */}
                            {showTooltip && (
                                <div
                                    role="tooltip"
                                    className="absolute right-0 top-full mt-2 w-80 sm:w-96 p-4 rounded-xl bg-slate-900 text-white dark:bg-slate-800 text-xs shadow-2xl border border-slate-700 z-50 animate-in fade-in duration-200"
                                >
                                    <div className="flex items-start gap-2.5 mb-2">
                                        <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                                        <div>
                                            <h4 className="font-bold text-white text-xs">
                                                Xác Suất Đã Qua Hiệu Chuẩn
                                                (Calibrated Probability)
                                            </h4>
                                            <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                                                Xác suất này đã qua hiệu chuẩn
                                                hậu nghiệm bằng thuật toán{" "}
                                                <strong className="text-emerald-400">
                                                    Temperature Scaling (T ={" "}
                                                    {result.temperature})
                                                </strong>{" "}
                                                trên tập Validation nội bộ, tiệm
                                                cận{" "}
                                                <strong className="text-emerald-400">
                                                    ECE = {result.ece_score}{" "}
                                                    &lt; 0.05
                                                </strong>
                                                .
                                            </p>
                                        </div>
                                    </div>
                                    <div className="pt-2 border-t border-slate-700/60 text-[11px] text-slate-400">
                                        <span className="font-semibold text-slate-300">
                                            Ý nghĩa y khoa:
                                        </span>{" "}
                                        Điểm số phản ánh tần suất rủi ro
                                        ước tính trên tập kiểm thử nội bộ, hỗ trợ
                                        giảm thiểu hiện tượng tự tin thái quá
                                        (overconfidence) thường gặp ở các mô
                                        hình học sâu.
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Top-1 Diagnosis Showcase */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pt-2">
                    <div>
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                            Gợi ý chẩn đoán có xác suất cao nhất (Mô hình tham khảo)
                        </span>
                        <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight mt-1 flex items-center gap-3">
                            <span>{topPrediction.disease_name}</span>
                        </h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5 flex items-center gap-2">
                            <span
                                className={`inline-block w-2 h-2 rounded-full ${topBand.bgColor}`}
                            />
                            Phân tầng rủi ro:{" "}
                            <strong className={topBand.textColor}>
                                {topBand.label}
                            </strong>
                            <span className="text-slate-400">•</span>
                            <span>
                                ECE: {(result.ece_score * 100).toFixed(1)}%
                            </span>
                        </p>
                    </div>

                    <div className="flex items-baseline gap-2 self-start md:self-end">
                        <span className="text-4xl sm:text-5xl font-black font-mono tracking-tight text-slate-900 dark:text-white">
                            {topPrediction.percentage}%
                        </span>
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                            độ tin cậy
                        </span>
                    </div>
                </div>
            </div>

            {/* Main Body: Top-K Ranked Diseases with 3-Band Progress Bars */}
            <div className="p-6 space-y-6">
                <div>
                    <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <Activity className="w-4 h-4 text-sky-500" />
                            Bảng Phân Bố Xác Suất Tham Khảo Top-K Bệnh Lý (Ranked
                            Pathologies)
                        </h4>
                        <div className="hidden sm:flex items-center gap-3 text-[11px] text-slate-500">
                            <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-emerald-500" />{" "}
                                &lt;30%: Thấp
                            </span>
                            <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-amber-500" />{" "}
                                30-70%: Trung bình
                            </span>
                            <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-rose-500" />{" "}
                                &gt;70%: Cao
                            </span>
                        </div>
                    </div>

                    {/* List of 4 pathologies */}
                    <div className="space-y-4">
                        {result.top_k_predictions.map((item, idx) => {
                            const band = getRiskBandConfig(item.percentage);
                            const isTop = idx === 0;

                            return (
                                <div
                                    key={item.disease}
                                    className={`p-3.5 rounded-xl border transition-all ${
                                        isTop
                                            ? "bg-slate-50/80 dark:bg-slate-800/40 border-slate-300/80 dark:border-slate-700 shadow-sm"
                                            : "bg-white dark:bg-slate-900/60 border-slate-100 dark:border-slate-800/70"
                                    }`}
                                >
                                    <div className="flex items-center justify-between gap-3 mb-2">
                                        <div className="flex items-center gap-2.5 min-w-0">
                                            <span
                                                className={`w-5 h-5 rounded-md flex items-center justify-center text-xs font-bold ${
                                                    isTop
                                                        ? "bg-sky-500 text-white"
                                                        : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                                                }`}
                                            >
                                                {idx + 1}
                                            </span>
                                            <span className="font-semibold text-xs sm:text-sm text-slate-900 dark:text-white truncate">
                                                {item.disease_name}
                                            </span>
                                            <span
                                                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${band.badgeBg}`}
                                            >
                                                {band.label}
                                            </span>
                                        </div>

                                        <div className="text-right flex-shrink-0">
                                            <span className="font-mono font-bold text-xs sm:text-sm text-slate-900 dark:text-white">
                                                {item.percentage}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* 3-Band Progress Bar with Reference Threshold Markers */}
                                    <div className="relative w-full h-3 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                                        {/* Threshold guides at 30% and 70% */}
                                        <div
                                            className="absolute top-0 bottom-0 left-[30%] w-[1px] bg-slate-300 dark:bg-slate-700 z-10"
                                            title="Ngưỡng 30%"
                                        />
                                        <div
                                            className="absolute top-0 bottom-0 left-[70%] w-[1px] bg-slate-300 dark:bg-slate-700 z-10"
                                            title="Ngưỡng 70%"
                                        />

                                        {/* Progress Fill */}
                                        <div
                                            className={`h-full rounded-full transition-all duration-700 ease-out ${band.barColor}`}
                                            style={{
                                                width: `${Math.min(100, Math.max(1, item.percentage))}%`,
                                            }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Multi-Stream Modality Comparison Accordion */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <button
                        type="button"
                        onClick={() => setShowStreamDetails(!showStreamDetails)}
                        className="w-full flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-sky-600 dark:hover:text-sky-400 py-2 transition-colors"
                    >
                        <span className="flex items-center gap-2">
                            <Layers className="w-4 h-4 text-indigo-500" />
                            Chi Tiết Đóng Góp Các Phương Thức (Modality Stream
                            Breakdown)
                        </span>
                        {showStreamDetails ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                        ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                        )}
                    </button>

                    {showStreamDetails && (
                        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 animate-in fade-in duration-200">
                            {/* Tabular Stream */}
                            <div className="p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
                                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                                    <Cpu className="w-3.5 h-3.5 text-sky-500" />
                                    <span>Dữ Liệu Bảng (Tabular)</span>
                                </div>
                                <div className="text-xs font-bold text-slate-900 dark:text-white">
                                    {result.modality_streams.tabular_stream
                                        ?.predicted_disease || "N/A"}
                                </div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 flex justify-between">
                                    <span>Độ tin cậy:</span>
                                    <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">
                                        {result.modality_streams.tabular_stream
                                            ? `${(result.modality_streams.tabular_stream.confidence * 100).toFixed(1)}%`
                                            : "N/A"}
                                    </span>
                                </div>
                            </div>

                            {/* Text Stream */}
                            <div className="p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
                                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                                    <FileText className="w-3.5 h-3.5 text-emerald-500" />
                                    <span>Ghi Chú Lâm Sàng (Text)</span>
                                </div>
                                <div className="text-xs font-bold text-slate-900 dark:text-white">
                                    {result.modality_streams.text_stream
                                        ?.predicted_disease || "N/A"}
                                </div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 flex justify-between">
                                    <span>Độ tin cậy:</span>
                                    <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">
                                        {result.modality_streams.text_stream
                                            ? `${(result.modality_streams.text_stream.confidence * 100).toFixed(1)}%`
                                            : "N/A"}
                                    </span>
                                </div>
                            </div>

                            {/* Multimodal Cross-Attention Fusion */}
                            <div className="p-3.5 rounded-xl border border-indigo-200 dark:border-indigo-900/50 bg-indigo-50/30 dark:bg-indigo-950/20">
                                <div className="flex items-center gap-2 text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-2">
                                    <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                                    <span>Cross-Attention Fusion</span>
                                </div>
                                <div className="text-xs font-bold text-indigo-950 dark:text-indigo-200">
                                    {result.modality_streams.multimodal_fusion
                                        ?.predicted_disease ||
                                        topPrediction.disease}
                                </div>
                                <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-1 flex justify-between">
                                    <span>Calibrated:</span>
                                    <span className="font-mono font-bold text-indigo-900 dark:text-indigo-100">
                                        {topPrediction.percentage}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Dynamic Attention Gate Weight Indicator */}
                {result.fusion_gate_weights && (
                    <div className="p-3 rounded-xl bg-slate-100/70 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 text-xs">
                        <div className="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-400 mb-1.5">
                            <span className="flex items-center gap-1 font-medium">
                                <Scale className="w-3 h-3 text-sky-500" />
                                Trọng số cổng thích ứng (Adaptive Gating
                                Weights):
                            </span>
                            <span className="font-mono">
                                Bảng:{" "}
                                {(
                                    result.fusion_gate_weights.g_tabular * 100
                                ).toFixed(0)}
                                % | Văn bản:{" "}
                                {(
                                    result.fusion_gate_weights.g_text * 100
                                ).toFixed(0)}
                                %
                            </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex">
                            <div
                                className="bg-sky-500 h-full transition-all duration-500"
                                style={{
                                    width: `${result.fusion_gate_weights.g_tabular * 100}%`,
                                }}
                                title={`Trọng số Bảng: ${(result.fusion_gate_weights.g_tabular * 100).toFixed(0)}%`}
                            />
                            <div
                                className="bg-emerald-500 h-full transition-all duration-500"
                                style={{
                                    width: `${result.fusion_gate_weights.g_text * 100}%`,
                                }}
                                title={`Trọng số Văn bản: ${(result.fusion_gate_weights.g_text * 100).toFixed(0)}%`}
                            />
                        </div>
                    </div>
                )}

                {/* Clinical Research Disclaimer */}
                <div className="pt-3 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 flex items-start gap-2">
                    <Info className="w-3.5 h-3.5 text-sky-500 flex-shrink-0 mt-0.5" />
                    <span>
                        <strong>Lưu ý chuyên môn:</strong> Kết quả trên là sản phẩm nghiên cứu thử nghiệm hỗ trợ quyết định (CDSS), không thay thế kết luận chẩn đoán và chỉ định điều trị của bác sĩ chuyên khoa.
                    </span>
                </div>
            </div>
        </div>
    );
}
