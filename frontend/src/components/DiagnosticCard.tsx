"use client";

import React, { useState } from "react";
import {
    Activity,
    AlertOctagon,
    AlertTriangle,
    BookOpen,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    Cpu,
    FileSearch,
    FileText,
    HelpCircle,
    Info,
    Layers,
    RotateCcw,
    Scale,
    ShieldAlert,
    ShieldCheck,
    Sparkles,
} from "lucide-react";
import {
    AgentExplainResponse,
    explainClinicalCase,
    MultimodalMockResponse,
} from "@/lib/api";
import EvidenceViewer from "@/components/EvidenceViewer";
import GuidelineDrawer from "@/components/GuidelineDrawer";

interface DiagnosticCardProps {
    result: MultimodalMockResponse;
    onReset?: () => void;
    clinicalNotes?: string;
}

export default function DiagnosticCard({
    result,
    onReset,
    clinicalNotes,
}: DiagnosticCardProps) {
    const [showTooltip, setShowTooltip] = useState<boolean>(false);
    const [showStreamDetails, setShowStreamDetails] = useState<boolean>(true);

    // Agentic RAG state
    const [explainLoading, setExplainLoading] = useState<boolean>(false);
    const [explainData, setExplainData] = useState<AgentExplainResponse | null>(
        null,
    );
    const [explainError, setExplainError] = useState<string | null>(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
    const [showExplanation, setShowExplanation] = useState<boolean>(false);

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

    const handleAuditEvidence = async () => {
        if (explainData) {
            setShowExplanation(!showExplanation);
            return;
        }

        const noteToAudit =
            clinicalNotes && clinicalNotes.trim().length >= 5
                ? clinicalNotes
                : `Bệnh nhân ${result.patient_id} vào viện vì khó thở tăng dần kèm ho kéo dài. Khám phổi nghe ran rít ran ngáy thì thở ra. Tiền sử dùng thuốc theo chỉ định.`;

        setExplainLoading(true);
        setExplainError(null);

        try {
            const data = await explainClinicalCase({
                patient_id: result.patient_id,
                clinical_notes: noteToAudit,
                target_diagnosis: result.predicted_disease,
                differential_diagnosis:
                    result.top_k_predictions[1]?.disease || undefined,
            });
            setExplainData(data);
            setShowExplanation(true);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setExplainError(err.message);
            } else {
                setExplainError("Không thể kết nối dịch vụ Agentic RAG");
            }
        } finally {
            setExplainLoading(false);
        }
    };

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
                                                cận ngưỡng khuyến nghị{" "}
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
                                        Điểm số phản ánh tần suất rủi ro ước
                                        tính trên tập kiểm thử nội bộ, hỗ trợ
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
                            Gợi ý chẩn đoán có xác suất cao nhất (Mô hình tham
                            khảo)
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
                            Bảng Phân Bố Xác Suất Tham Khảo Top-K Bệnh Lý
                            (Ranked Pathologies)
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
                                        <div
                                            className="absolute top-0 bottom-0 left-[30%] w-[1px] bg-slate-300 dark:bg-slate-700 z-10"
                                            title="Ngưỡng 30%"
                                        />
                                        <div
                                            className="absolute top-0 bottom-0 left-[70%] w-[1px] bg-slate-300 dark:bg-slate-700 z-10"
                                            title="Ngưỡng 70%"
                                        />

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
                        className="w-full flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-sky-600 dark:hover:text-sky-400 py-2 transition-colors cursor-pointer"
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

                {/* --- BACKLOG 05: AGENTIC RAG & CLINICAL EVIDENCE AUDITING --- */}
                <div className="pt-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                                <BookOpen className="w-4 h-4" />
                            </span>
                            <div>
                                <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                                    Hội Chẩn Đa Tác Tử &amp; Kiểm Toán Chứng Cứ
                                    (Agentic RAG)
                                </h4>
                                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                                    Đối chiếu tiêu chuẩn chẩn đoán phân biệt
                                    quốc tế &amp; định vị bằng chứng nguyên văn
                                </p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={handleAuditEvidence}
                            disabled={explainLoading}
                            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50 cursor-pointer"
                        >
                            {explainLoading ? (
                                <>
                                    <Activity className="w-4 h-4 animate-spin" />
                                    <span>Đang hội chẩn Agentic RAG...</span>
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4" />
                                    <span>
                                        {showExplanation
                                            ? "Ẩn Bảng Chứng Cứ"
                                            : "Xem Bằng Chứng & Phác Đồ"}
                                    </span>
                                </>
                            )}
                        </button>
                    </div>

                    {explainError && (
                        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                            <span>{explainError}</span>
                        </div>
                    )}

                    {/* Agentic RAG Result Box */}
                    {showExplanation && explainData && (
                        <div className="space-y-4 pt-2 animate-in fade-in slide-in-from-top-2 duration-300">
                            {/* Differential Reasoning Card */}
                            <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-500/5 via-sky-500/5 to-slate-500/5 border border-indigo-500/20 dark:border-indigo-500/30 space-y-3">
                                <div className="flex flex-wrap items-center justify-between gap-2">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-bold text-indigo-900 dark:text-indigo-300">
                                            Biện Luận Chẩn Đoán Phân Biệt:
                                        </span>
                                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-semibold border border-emerald-500/30">
                                            {explainData.primary_diagnosis_name}{" "}
                                            (Ưu tiên)
                                        </span>
                                        <span className="text-xs text-slate-400">
                                            vs
                                        </span>
                                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-500/30">
                                            {explainData.differential_diagnosis_name ||
                                                explainData.differential_diagnosis}{" "}
                                            (Đối trọng)
                                        </span>
                                    </div>

                                    <button
                                        type="button"
                                        onClick={() => setIsDrawerOpen(true)}
                                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-indigo-600 text-xs font-medium shadow-sm transition-all cursor-pointer"
                                    >
                                        <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
                                        <span>
                                            Xem Phác Đồ (
                                            {
                                                explainData.guideline_references
                                                    .length
                                            }
                                            )
                                        </span>
                                    </button>
                                </div>

                                <p className="text-xs sm:text-[13px] text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                                    {explainData.differential_reasoning}
                                </p>

                                {/* Red Flags if any */}
                                {explainData.red_flags &&
                                    explainData.red_flags.length > 0 && (
                                        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs space-y-1">
                                            <div className="font-bold text-rose-700 dark:text-rose-300 flex items-center gap-1.5">
                                                <AlertOctagon className="w-4 h-4 text-rose-500" />
                                                <span>
                                                    Cảnh Báo Cờ Đỏ Cấp Cứu
                                                    (Clinical Red Flags):
                                                </span>
                                            </div>
                                            <ul className="list-disc list-inside text-rose-600 dark:text-rose-400 space-y-0.5 pl-2">
                                                {explainData.red_flags.map(
                                                    (rf, i) => (
                                                        <li key={`rf-${i}`}>
                                                            {rf}
                                                        </li>
                                                    ),
                                                )}
                                            </ul>
                                        </div>
                                    )}

                                {/* Recommended Next Investigations */}
                                {explainData.recommended_investigations &&
                                    explainData.recommended_investigations
                                        .length > 0 && (
                                        <div className="p-3 rounded-xl bg-sky-500/5 dark:bg-sky-950/20 border border-sky-500/10 text-xs space-y-1.5">
                                            <div className="font-semibold text-sky-900 dark:text-sky-200 flex items-center gap-1.5">
                                                <CheckCircle2 className="w-3.5 h-3.5 text-sky-500" />
                                                <span>
                                                    Đề Xuất Xét Nghiệm Xác Chẩn
                                                    Theo Phác Đồ:
                                                </span>
                                            </div>
                                            <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-0.5 pl-2 text-[11px]">
                                                {explainData.recommended_investigations.map(
                                                    (inv, i) => (
                                                        <li key={`inv-${i}`}>
                                                            {inv}
                                                        </li>
                                                    ),
                                                )}
                                            </ul>
                                        </div>
                                    )}
                            </div>

                            {/* Evidence Viewer with Highlighted Spans */}
                            <EvidenceViewer
                                rawNotes={
                                    clinicalNotes &&
                                    clinicalNotes.trim().length >= 5
                                        ? clinicalNotes
                                        : `Bệnh nhân ${result.patient_id} vào viện vì khó thở tăng dần kèm ho kéo dài. Khám phổi nghe ran rít ran ngáy thì thở ra. Tiền sử dùng thuốc theo chỉ định.`
                                }
                                spans={explainData.grounded_spans}
                                hallucinationFilteredCount={
                                    explainData.hallucination_filtered_count
                                }
                                onOpenGuidelineDrawer={() =>
                                    setIsDrawerOpen(true)
                                }
                            />

                            {/* Guideline Drawer */}
                            <GuidelineDrawer
                                isOpen={isDrawerOpen}
                                onClose={() => setIsDrawerOpen(false)}
                                guidelines={explainData.guideline_references}
                                activeDisease={result.predicted_disease}
                            />
                        </div>
                    )}
                </div>

                {/* Clinical Research Disclaimer */}
                <div className="pt-3 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 flex items-start gap-2">
                    <Info className="w-3.5 h-3.5 text-sky-500 flex-shrink-0 mt-0.5" />
                    <span>
                        <strong>Lưu ý chuyên môn:</strong> Kết quả trên là sản
                        phẩm nghiên cứu thử nghiệm hỗ trợ quyết định (CDSS),
                        không thay thế kết luận chẩn đoán và chỉ định điều trị
                        của bác sĩ chuyên khoa.
                    </span>
                </div>
            </div>
        </div>
    );
}
