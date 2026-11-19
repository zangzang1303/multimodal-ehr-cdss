"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, Cpu, ShieldAlert } from "lucide-react";
import { getInferenceStatus, InferenceStatusResponse } from "@/lib/api";

export function ResearchDisclaimerBanner() {
  return (
    <div className="w-full bg-amber-500/15 dark:bg-amber-950/60 border-b border-amber-500/30 text-amber-950 dark:text-amber-200 text-xs py-2 px-4">
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-center font-medium">
        <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0" />
        <span>
          <strong>Nguyên mẫu nghiên cứu trên dữ liệu tổng hợp (Synthea / MTSamples)</strong>{" "}
          &ndash; Tuyệt đối không dùng cho quyết định lâm sàng hoặc ra y lệnh thực tế.
        </span>
      </div>
    </div>
  );
}

export function ModelCardFooter() {
  const [statusData, setStatusData] = useState<InferenceStatusResponse | null>(null);

  useEffect(() => {
    let active = true;
    getInferenceStatus()
      .then((res) => {
        if (active) setStatusData(res);
      })
      .catch(() => {
        // Silent fallback if backend offline
      });
    return () => {
      active = false;
    };
  }, []);

  const mc = statusData?.model_card;

  return (
    <footer className="mt-12 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-950/80 text-xs text-slate-600 dark:text-slate-400 py-5 px-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-1.5 font-semibold text-slate-800 dark:text-slate-200">
            <Cpu className="w-4 h-4 text-sky-500" />
            Model Card &amp; Provenance
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 font-mono text-[11px]">
            Checkpoint: {mc?.checkpoint_name ?? "multimodal_best.pt"}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 font-mono text-[11px]">
            SHA-256: {mc?.checkpoint_sha256_short ?? "unavailable"}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 font-mono text-[11px]">
            Trained: {mc?.trained_at ?? "—"}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 font-mono text-[11px]">
            Temp T: {mc?.temperature ?? "—"}
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 font-mono text-[11px] inline-flex items-center gap-1.5">
            <span>Manifest SHA: {mc?.data_manifest_sha ?? "—"}</span>
            {mc?.data_manifest_is_mock && (
              <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-800 dark:text-amber-300 border border-amber-500/30 text-[10px] font-bold">
                MOCK — chờ TV2
              </span>
            )}
          </span>
          <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20 font-mono text-[11px]">
            Explain Mode: {statusData?.reasoning_mode ?? "deterministic_template"}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-amber-700 dark:text-amber-400">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Phục vụ nghiên cứu khoa học (TRIPOD-AI / Phase 3)</span>
        </div>
      </div>
    </footer>
  );
}
