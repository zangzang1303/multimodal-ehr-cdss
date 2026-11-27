# BACKLOG 08 – THÀNH VIÊN 1 (Lead ML / Modeling & Evaluation)

> **Trạng thái 2026-11-23: HOÀN THÀNH** (kèm rà soát và sửa dữ liệu canonical của TV2 – xem CHANGELOG 2026-11-23)
>
> | Nhiệm vụ | Kết quả | Bằng chứng |
> | :--- | :--- | :--- |
> | 1.1 Chặn fallback | ✅ `src/models/backbone_loader.py`; áp dụng ở `text_encoder.py`, `train_multimodal.py`, `evaluate_clinical_utility.py`; chỉ còn `from_config` sau cờ `allow_random_backbone` | `tests/test_phase3_member1.py::test_missing_pretrained_weights_raise_instead_of_random_init` |
> | 1.2 Bảo vệ checkpoint + 5 seed | ✅ `src/models/checkpoint_io.py` (từ chối eval-only/0 epoch, smoke → `*.smoke.pt`, provenance); RQ1 chạy 5 seed (13, 42, 101, 2024, 7); checkpoint triển khai = cross-attention đóng băng seed 101 (NLL validation thấp nhất) | `data/checkpoints/multimodal_best.pt` (`training_metadata.epochs_total > 0`, `provenance`), `results/raw/rq1_training_summary.json` |
> | 1.3 Dự đoán từng bản ghi + baseline thật | ✅ `data/predictions/rq1/*.npz` (val + test + 5 kịch bản thiếu dữ liệu); baseline seed 42 xuất ra `data/checkpoints/baselines/` → `/predict/baseline` trả 200 từ mô hình thật | `scripts/export_baseline_artifacts.py`, `src/api/baseline_service.py` |
> | 1.4 Results registry | ✅ `scripts/build_results_registry.py` → `results/registry.json`; `scripts/export_latex_tables.py` → `docs/paper_latex/generated/`; API đọc registry/ablation sinh lại | Kiểm chứng chéo: `evaluate_clinical_utility.py` (đường code khác) cho AUROC 0.9583, ECE 0.0773 = registry |
>
> Ghi chú: AUROC cross-attention cũ (0.959, 1 seed) tái lập được trong khoảng 0.945–0.966 qua 5 seed (TB 0.956). Không có `make reproduce`; quy trình tái lập đầy đủ nằm ở README mục 6.2.

## Nhiệm vụ 1.1 – Chặn fallback "BERT ngẫu nhiên" (ngày 1)
**Vấn đề:** khi thiếu trọng số Bio_ClinicalBERT, code dùng `AutoModel.from_config(...)` → embedding nhiễu mà không báo lỗi.
**Vị trí:**
- `src/models/text_encoder.py` – khối `except OSError: ... AutoModel.from_config(config)`
- `scripts/train_multimodal.py` ~dòng 160–165
- `scripts/evaluate_clinical_utility.py` dòng 276–283

**Việc cần làm:**
1. Thay fallback bằng `raise RuntimeError("Thiếu trọng số <model>. Chạy: huggingface-cli download emilyalsentzer/Bio_ClinicalBERT")`.
2. Chỉ cho phép backbone ngẫu nhiên qua tham số tường minh `allow_random_backbone=True` (dùng trong unit test).
3. Ghi `backbone_revision` (commit hash snapshot HF) và `tokenizer_name` vào checkpoint.
4. Test mới: thiếu trọng số ⇒ raise.

**Nghiệm thu:** `grep -rn from_config src scripts` chỉ còn trong nhánh có cờ `allow_random_backbone`.

## Nhiệm vụ 1.2 – Bảo vệ checkpoint & huấn luyện lại đa seed (ngày 2–4, sau M2-2.2)
1. `train_multimodal.py`: **không bao giờ** ghi đè `multimodal_best.pt` khi `--eval-only`, `--smoke-test` hoặc `epochs_total == 0`. Ghi checkpoint mới vào `data/checkpoints/<run_id>/` rồi mới symlink/copy khi đạt điều kiện.
2. Chạy `scripts/run_multimodal_ablation.py` trên dữ liệu chuẩn (manifest M2) với **5 seed**: 13, 42, 101, 2024, 7. Bốn biến thể: tabular, text, concat, cross_attention.
3. Chọn checkpoint triển khai = cross_attention, seed có **validation NLL** tốt nhất (không xem test).
4. So sánh với kết quả 0,959 cũ; nếu lệch > 0,01 phải giải thích (ví dụ do sửa de-ID).

**Đầu ra:** `data/checkpoints/multimodal_best.pt` (metadata đầy đủ), `data/ablation_results_multiseed.json` (mean ± SD).

## Nhiệm vụ 1.3 – Lưu dự đoán từng mẫu cho mọi mô hình (ngày 3–4)
- Chạy lại `scripts/run_baselines.py` (CatBoost/XGBoost, FT-Transformer, Bio_ClinicalBERT) trên dữ liệu chuẩn, cùng 5 seed nếu khả thi (ít nhất 3).
- Lưu `data/predictions/{model}_{variant}_seed{s}.npz` gồm: `patient_id`, `y_true`, `logits`, `probs_raw`, `probs_calibrated`, cho cả **val** và **test**.
- Lưu mô hình baseline (CatBoost `.cbm`, FT `.pt`, BERT head) để M3 dùng cho `/predict/baseline` thật.

## Nhiệm vụ 1.4 – Results registry: một nguồn sự thật (ngày 4–5)
- Script `scripts/build_results_registry.py`: đọc toàn bộ `.npz` → tính metrics bằng `src/evaluation/metrics.py` → ghi `results/registry.json` (kèm git commit, data manifest SHA, seed, thời điểm).
- Script `scripts/export_latex_tables.py`: sinh `docs/paper_latex/generated/*.tex` (bảng benchmark, ablation, calibration) từ registry. Paper `\input{}` các file này – **không gõ tay số**.
- `GET /api/v1/evaluation/benchmark` và trang `/evaluation` đọc từ registry.

**Nghiệm thu Thành viên 1:** chạy lại từ đầu bằng 1 lệnh `make reproduce` (hoặc `scripts/reproduce_all.ps1`) ra cùng registry (sai khác ≤ 1e-6 với cùng seed/GPU).
