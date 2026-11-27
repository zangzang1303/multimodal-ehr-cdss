"""Write MODEL_CARD.md for the deployment checkpoint from results/registry.json (no hand-typed numbers)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def f3(x):
    return "–" if x is None else f"{x:.3f}"


def main() -> None:
    reg = json.loads((ROOT / "results" / "registry.json").read_text(encoding="utf-8"))
    meta = reg["metadata"]
    rq1 = {m["model"]: m for m in reg["rq1_multiseed_comparison"]["models"]}
    dep = rq1["xattn_frozen"]
    cal = reg["rq4_calibration"]["methods"]
    rob = reg["rq4_missing_modality"]["by_model"]
    ckpt = ROOT / "data" / "checkpoints" / "multimodal_best.pt"
    sha = hashlib.sha256(ckpt.read_bytes()).hexdigest()
    comps = {c["comparator"]: c for c in reg["rq1_multiseed_comparison"]["comparisons_vs_deployment_model"]}
    fair = reg["fairness"]["subgroups"]
    lines = [
        "# MODEL CARD – M-CDSS cross-attention (BERT đóng băng)",
        "",
        "> **Nguyên mẫu nghiên cứu trên dữ liệu tổng hợp. Không dùng cho quyết định lâm sàng.**",
        f"> Sinh tự động bởi `scripts/export_model_card.py` từ `results/registry.json` ({meta['generated_at'][:19]}Z).",
        "",
        "## 1. Thông tin mô hình",
        f"- Checkpoint: `data/checkpoints/multimodal_best.pt` (SHA-256 `{sha}`)",
        f"- Kiến trúc: FT-Transformer (13 biến bảng) + Bio_ClinicalBERT đóng băng (`max_length` 512) + cross-attention có cổng, 4 lớp.",
        f"- Seed {meta['deployment_seed']} – chọn theo NLL validation thấp nhất trong {dep['n_seeds']} seed (quy tắc đăng ký trước, docs/11_ANALYSIS_PLAN.md A.1).",
        f"- Temperature scaling T = {reg['rq4_calibration']['temperature']} (khớp trên validation N = 273).",
        f"- Dữ liệu: `data/processed_rebuilt_strict/` (manifest SHA-256 `{meta['data_manifest_sha256'][:16]}…`).",
        "",
        "## 2. Mục đích sử dụng",
        "- **Dự kiến:** minh hoạ nghiên cứu về dung hợp dữ liệu bảng + ghi chú lâm sàng cho 4 chẩn đoán (hen, COPD, suy tim, viêm phổi), giảng dạy, demo phần mềm.",
        "- **Không dự kiến:** chẩn đoán, sàng lọc hay điều trị bệnh nhân thật; dữ liệu ngoài 4 nhóm bệnh; ghi chú tiếng Việt (mô hình huấn luyện trên ghi chú tiếng Anh).",
        "",
        f"## 3. Hiệu năng (test strict N = {reg['rq1_multiseed_comparison']['test_n']})",
        "| Mô hình | Macro AUROC (TB ± SD) | Macro-F1 | ECE | Δ AUROC so với mô hình này [CI 95%], p Holm |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]
    for key, row in rq1.items():
        c = comps.get(key)
        delta = "(mô hình này)" if key == "xattn_frozen" else \
            f"{-c['delta']:+.3f} [{-c['ci95'][1]:.3f}; {-c['ci95'][0]:.3f}], p={c['holm_adjusted_p']:.3f}"
        lines.append(f"| {row['label']} | {row['auroc_mean']:.3f} ± {row['auroc_sd']:.3f} | {row['f1_mean']:.3f} | "
                     f"{row['ece_mean']:.3f} | {delta} |")
    lines += [
        "",
        "Δ ở bảng trên là (mô hình so sánh − mô hình triển khai). **Mô hình triển khai không phải mô hình tốt nhất**: "
        "Bio_ClinicalBERT fine-tune và ensemble CatBoost + BERT có AUROC cao hơn có ý nghĩa thống kê. Mô hình này được "
        "chọn trước khi xem test vì tương thích với dịch vụ suy luận (BERT đầy đủ, đóng băng).",
        "",
        "## 4. Hiệu chuẩn",
        f"- ECE (10 bins): không hiệu chuẩn {f3(cal['uncalibrated']['ece_10_equal_width'])}, temperature "
        f"{f3(cal['temperature']['ece_10_equal_width'])} (CI {cal['temperature']['ece_ci95']}), vector scaling "
        f"{f3(cal['vector_scaling']['ece_10_equal_width'])}, isotonic {f3(cal['isotonic_ovr']['ece_10_equal_width'])}.",
        f"- Mục tiêu ECE < 0.05: {'đạt bởi ' + ', '.join(reg['rq4_calibration']['target_met_by']) if reg['rq4_calibration']['target_met_by'] else '**không đạt** với phương pháp nào'}.",
        "",
        "## 5. Độ bền khi thiếu dữ liệu (macro AUROC, trung bình qua seed)",
        "| Kịch bản | Mô hình này | CatBoost | BERT fine-tune |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for s in reg["rq4_missing_modality"]["scenarios"]:
        r = rob[s["scenario"]]
        lines.append(f"| {s['label']} | {f3(r.get('xattn_frozen', {}).get('mean'))} | {f3(r.get('catboost', {}).get('mean'))} | "
                     f"{f3(r.get('bert_ft', {}).get('mean'))} |")
    lines += ["", "## 6. Phân nhóm (dữ liệu tổng hợp – chỉ mô tả pipeline)",
              "| Nhóm | N | AUROC [CI 95%] | Ghi chú |", "| :--- | :---: | :---: | :--- |"]
    for k, v in fair.items():
        lines.append(f"| {k} | {v['sample_size']} | {f3(v['macro_auroc'])} {v['macro_auroc_ci95'] or ''} | {v.get('note', '')} |")
    lines += [
        "",
        "## 7. Giới hạn đã biết",
        "- Dữ liệu bán tổng hợp (Synthea + MTSamples); nhãn không do bác sĩ xác định; chưa ngoại kiểm, chưa khảo sát bác sĩ.",
        "- Ghi chú chứa lại sinh hiệu/xét nghiệm; tín hiệu văn bản phần lớn đến từ các con số này (xem RQ2 trong registry).",
        "- Tập test strict có phân bố nhân khẩu học khác tập huấn luyện (106/106 ca suy tim là nam, không có người đang hút thuốc).",
        "- Mô hình huấn luyện trên dữ liệu đầy đủ; mất toàn bộ dữ liệu bảng làm hiệu năng giảm mạnh.",
        "",
        "## 8. Giấy phép",
        "- Mã nguồn: xem `LICENSE`. Bio_ClinicalBERT: MIT. Synthea: Apache-2.0. MTSamples: điều khoản của mtsamples.com (chỉ nghiên cứu).",
        "- Không phân phối lại toàn văn phác đồ GINA/GOLD/ESC (có bản quyền); KB chỉ chứa diễn giải ngắn có trích dẫn.",
        "",
    ]
    (ROOT / "MODEL_CARD.md").write_text("\n".join(lines), encoding="utf-8")
    print("[OK] MODEL_CARD.md")


if __name__ == "__main__":
    main()
