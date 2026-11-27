# BACKLOG 10 – THÀNH VIÊN 1 (Lead ML / Modeling & Evaluation)

> **Trạng thái 2026-11-27: HOÀN THÀNH phần TV1** (+ sửa phần của TV2/TV3 phát hiện khi rà soát)
>
> | Nhiệm vụ | Kết quả |
> | :--- | :--- |
> | 1.1 Abstract / Intro / Methods | ✅ viết lại `00`, `01`, `03`; tiêu đề và từ khoá bỏ khẳng định quá mức |
> | 1.2 Results | ✅ `07` dùng `\input{generated/*}` + macro; Discussion/Limitations trong `08`; `scripts/check_paper.py`: 0 macro thiếu, 0 bib thiếu, 0 ref hỏng, 0 TODO. **Chưa biên dịch PDF** (máy không có TeX). |
> | 1.3 Model card & release notes | ✅ `MODEL_CARD.md` (sinh từ registry), `RELEASE_NOTES.md` (chưa gắn tag – chờ nhóm duyệt) |
> | 1.4 Q&A | ✅ `docs/thuyết trình/QA_MO_HINH_VA_KET_QUA_MEMBER_1.md` (sinh từ registry) |
> | Bổ sung | Slide 13–17 sinh từ registry (`scripts/export_slide_results.py`); điền số vào kịch bản video & Q&A TV3; Bảng 1 sinh tự động; sửa 2 tài liệu tham khảo không tồn tại; sửa sơ đồ TRIPOD flow; README gỡ bảng số liệu bịa. |


## Nhiệm vụ 1.1 – Abstract, Introduction, Methods
- Viết lại `docs/paper_latex/sections/00_abstract.tex`: bỏ hoàn toàn `[TODO]`; nêu đúng kết quả RQ1–RQ5 (kể cả "fusion không vượt text-only/ensemble" nếu đúng như vậy, và phát hiện văn bản mã hoá lại sinh hiệu).
- Bỏ các khẳng định không có bằng chứng: "hiệu chuẩn đạt chuẩn lâm sàng", "chứng minh tính bổ trợ", "100% chống ảo giác" (thay bằng "100% span khớp chuỗi trên bộ test; độ đúng ngữ nghĩa kiểm thủ công x/20").
- `01_introduction.tex`: 3 câu hỏi khoảng trống → RQ1–RQ5 → 4 đóng góp (xem docs/10 mục 4).
- `03_methodology_fusion.tex`: thêm mục *Statistical analysis* (bootstrap theo bệnh nhân, Holm, số seed) và *Note-variant construction* (RQ2), *Simulation design* (RQ3 nếu có).

## Nhiệm vụ 1.2 – Results
- `07_empirical_results.tex`: mỗi RQ một tiểu mục, bảng `\input{generated/...}`; hình: bảng chính có CI, `fig_rq2_text_decomposition`, `fig_calibration`, (`fig_rq3_heatmap`).
- Xoá bảng DCA template cũ (giá trị treat-all gõ tay), thay bằng bảng sinh từ registry (phối hợp M2).

## Nhiệm vụ 1.3 – Phát hành & model card
- `MODEL_CARD.md`: mục đích sử dụng, **không dùng cho lâm sàng**, dữ liệu huấn luyện, metric + CI, hiệu chuẩn, giới hạn, fairness.
- `RELEASE_NOTES.md` cho `v1.0-research`; điều kiện phân phối checkpoint (Bio_ClinicalBERT: MIT; dữ liệu: Synthea Apache-2.0, MTSamples – kiểm tra điều khoản).
- Tag chỉ khi cả nhóm đồng ý phạm vi phát hành.

## Nhiệm vụ 1.4 – Chuẩn bị Q&A phần mô hình
Soạn câu trả lời ngắn (≤ 3 câu, có số liệu) cho:
1. Vì sao cross-attention không vượt BERT fine-tune / ensemble?
2. Làm sao biết không rò rỉ nhãn? (audit split, temporal lock, che `[REDACTED_DIAGNOSIS]`, RQ2)
3. ECE là gì, vì sao chưa < 0,05, temperature scaling khớp trên đâu?
4. Vì sao AUROC cao mà F1/accuracy thấp?
5. Nếu có MIMIC-IV, kỳ vọng thay đổi thế nào?
