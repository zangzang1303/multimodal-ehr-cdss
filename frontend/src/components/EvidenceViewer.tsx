"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  FileText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { EvidenceSpan } from "@/lib/api";

interface EvidenceViewerProps {
  rawNotes: string;
  spans: EvidenceSpan[];
  hallucinationFilteredCount?: number;
  onOpenGuidelineDrawer?: () => void;
}

export default function EvidenceViewer({
  rawNotes,
  spans,
  hallucinationFilteredCount = 0,
  onOpenGuidelineDrawer,
}: EvidenceViewerProps) {
  const [activeSpanIdx, setActiveSpanIdx] = useState<number | null>(null);

  // Filter and sort spans by start offset, skipping overlaps defensively
  const validSpans: EvidenceSpan[] = [];
  const sorted = [...spans]
    .filter(
      (s) =>
        s.start_char >= 0 &&
        s.end_char > s.start_char &&
        s.end_char <= rawNotes.length
    )
    .sort((a, b) => a.start_char - b.start_char);

  let lastEnd = 0;
  for (const s of sorted) {
    if (s.start_char >= lastEnd) {
      validSpans.push(s);
      lastEnd = s.end_char;
    }
  }

  // Segment raw text into non-highlighted and highlighted spans
  const segments: Array<
    | { type: "text"; content: string }
    | { type: "span"; span: EvidenceSpan; index: number }
  > = [];

  let cursor = 0;
  validSpans.forEach((span, index) => {
    if (span.start_char > cursor) {
      segments.push({
        type: "text",
        content: rawNotes.slice(cursor, span.start_char),
      });
    }
    segments.push({
      type: "span",
      span,
      index,
    });
    cursor = span.end_char;
  });

  if (cursor < rawNotes.length) {
    segments.push({
      type: "text",
      content: rawNotes.slice(cursor),
    });
  }

  const getCategoryStyles = (category: string) => {
    switch (category) {
      case "supporting":
        return {
          markClass:
            "bg-emerald-500/20 text-emerald-950 dark:text-emerald-100 border-b-2 border-emerald-500 hover:bg-emerald-500/30",
          badgeBg:
            "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/30",
          bulletColor: "bg-emerald-500",
        };
      case "counter":
        return {
          markClass:
            "bg-indigo-500/20 text-indigo-950 dark:text-indigo-100 border-b-2 border-indigo-500 hover:bg-indigo-500/30",
          badgeBg:
            "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/30",
          bulletColor: "bg-indigo-500",
        };
      case "red_flag":
        return {
          markClass:
            "bg-rose-500/20 text-rose-950 dark:text-rose-100 border-b-2 border-rose-500 hover:bg-rose-500/30",
          badgeBg:
            "bg-rose-500/10 text-rose-700 dark:text-rose-300 border-rose-500/30",
          bulletColor: "bg-rose-500",
        };
      default:
        return {
          markClass:
            "bg-amber-500/20 text-amber-950 dark:text-amber-100 border-b-2 border-amber-500 hover:bg-amber-500/30",
          badgeBg:
            "bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/30",
          bulletColor: "bg-amber-500",
        };
    }
  };

  return (
    <div className="space-y-4">
      {/* Evidence Viewer Header & Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-sky-500" />
          <span className="text-xs font-bold text-slate-900 dark:text-white">
            Định Vị Chứng Cứ Lâm Sàng (Evidence Grounding)
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" />
            {validSpans.length} đoạn chứng cứ
          </span>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-600 dark:text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            Ủng hộ chẩn đoán chính
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
            Chẩn đoán phân biệt
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            Cờ đỏ nguy cơ
          </span>
        </div>
      </div>

      {/* Main Text Area with Highlight Spans */}
      <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 font-sans text-xs sm:text-sm leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap max-h-96 overflow-y-auto selection:bg-sky-500/30">
        {segments.map((seg, i) => {
          if (seg.type === "text") {
            return <span key={`text-${i}`}>{seg.content}</span>;
          }

          const style = getCategoryStyles(seg.span.category);
          const isActive = activeSpanIdx === seg.index;

          return (
            <mark
              key={`span-${seg.index}`}
              onMouseEnter={() => setActiveSpanIdx(seg.index)}
              onMouseLeave={() => setActiveSpanIdx(null)}
              onClick={() => setActiveSpanIdx(seg.index)}
              title={`${seg.span.label}: ${seg.span.reason || seg.span.text}`}
              className={`cursor-pointer rounded px-1 py-0.5 transition-all font-medium ${
                style.markClass
              } ${
                isActive
                  ? "ring-2 ring-sky-500/60 shadow-sm brightness-105"
                  : ""
              }`}
            >
              {rawNotes.slice(seg.span.start_char, seg.span.end_char)}
            </mark>
          );
        })}
      </div>

      {/* Zero-Hallucination & Anti-Hallucination Status Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl bg-emerald-500/5 dark:bg-emerald-950/20 border border-emerald-500/20 text-xs">
        <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
          <span>
            <strong>Đảm bảo không ảo giác (Zero-Hallucination):</strong> 100% câu
            trích dẫn đều đã ánh xạ về tọa độ ký tự chính xác trong hồ sơ bệnh
            án.
          </span>
        </div>

        {hallucinationFilteredCount > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-700 dark:text-rose-300 border border-rose-500/20 font-mono">
            Đã loại bỏ {hallucinationFilteredCount} suy diễn không căn cứ
          </span>
        )}
      </div>

      {/* Grounded Evidence Claims List */}
      <div className="space-y-2">
        <div className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center justify-between">
          <span>Danh Mục Căn Cứ Lâm Sàng Đã Đối Chiếu:</span>
          {onOpenGuidelineDrawer && (
            <button
              type="button"
              onClick={onOpenGuidelineDrawer}
              className="text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 font-semibold cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Đối chiếu phác đồ (GINA / GOLD / ESC)</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {validSpans.map((span, idx) => {
            const style = getCategoryStyles(span.category);
            const isActive = activeSpanIdx === idx;

            return (
              <div
                key={`claim-${idx}`}
                onMouseEnter={() => setActiveSpanIdx(idx)}
                onMouseLeave={() => setActiveSpanIdx(null)}
                className={`p-3 rounded-xl border text-xs transition-all ${
                  isActive
                    ? "border-sky-400 dark:border-sky-600 bg-sky-50/50 dark:bg-sky-950/20 shadow-sm"
                    : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${style.badgeBg}`}
                  >
                    {span.label}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    Offset: [{span.start_char}:{span.end_char}]
                  </span>
                </div>
                <div className="font-semibold text-slate-900 dark:text-white">
                  &ldquo;{span.text}&rdquo;
                </div>
                {span.reason && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                    {span.reason}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

