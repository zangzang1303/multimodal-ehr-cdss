"use client";

import React, { useEffect } from "react";
import {
  BookOpen,
  ShieldCheck,
  X,
} from "lucide-react";
import { GuidelineReference } from "@/lib/api";

interface GuidelineDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  guidelines: GuidelineReference[];
  activeDisease?: string;
}

export default function GuidelineDrawer({
  isOpen,
  onClose,
  guidelines,
  activeDisease,
}: GuidelineDrawerProps) {
  // Handle escape key to close drawer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-in fade-in duration-200">
      {/* Backdrop overlay */}
      <div
        className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-2xl bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col">
          {/* Drawer Header */}
          <div className="p-6 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 flex items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                  <BookOpen className="w-4 h-4" />
                </span>
                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span>Phác Đồ &amp; Hướng Dẫn Lâm Sàng Chuẩn (CPGs)</span>
                  {activeDisease && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-semibold border border-indigo-500/20 font-mono">
                      {activeDisease}
                    </span>
                  )}
                </h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Các phân mảnh đối chiếu phác đồ quốc tế (GINA, GOLD, ESC) và Bộ
                Y tế phục vụ Agentic RAG
              </p>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
              aria-label="Đóng bảng phác đồ"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Drawer Body - Scrollable Guidelines */}
          <div className="flex-1 p-6 space-y-5 overflow-y-auto">
            {guidelines.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400">
                Không tìm thấy phân mảnh phác đồ phù hợp.
              </div>
            ) : (
              guidelines.map((g) => (
                <div
                  key={g.chunk_id}
                  className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950/60 shadow-sm space-y-3"
                >
                  {/* Badges row */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800/80 pb-2.5">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20 font-mono">
                        {g.guideline_source}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                        {g.disease_entity}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold">
                        {g.evidence_level}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {g.chunk_id}
                      </span>
                    </div>
                  </div>

                  {/* Section Title */}
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
                    {g.section_title}
                  </h4>

                  {/* Content snippet */}
                  <p className="text-xs sm:text-[13px] text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap font-sans bg-slate-50 dark:bg-slate-900/40 p-3.5 rounded-xl border border-slate-100 dark:border-slate-800/60">
                    {g.text_content}
                  </p>
                </div>
              ))
            )}
          </div>

          {/* Drawer Footer */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 flex items-center justify-between text-xs text-slate-500">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Cơ sở tri thức Qdrant Vector Store • M-CDSS RAG</span>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:hover:bg-slate-200 dark:text-slate-900 text-xs font-semibold transition-colors"
            >
              Đóng
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

