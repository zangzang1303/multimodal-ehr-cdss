# Artefact bị thu hồi (2026-11-19 → thu hồi 2026-11-23)

Các file trong thư mục này do `evaluate_research_hardening_member2.py` (Backlog 09, Thành viên 2) sinh ra.
**Không được trích dẫn trong bài báo, slide hay UI.** Giữ lại để truy vết.

Lý do thu hồi (rà soát của Thành viên 1, 2026-11-23):
1. Chạy trên bộ dữ liệu tái tạo ngày 2026-11-18 từ `data/raw/` (bản cũ): 86–90% ghi chú còn tên chẩn đoán,
   42% ghi chú test dùng lại thân ghi chú MTSamples gắn với một nhãn ở train. TF-IDF đã che hết số vẫn đạt
   macro AUROC 0,962 ⇒ rò rỉ nhãn qua văn bản.
2. Script tự huấn luyện một mô hình fusion riêng (không phải mô hình của dự án), không dùng validation,
   temperature cố định 1,15, `max_length = 128`.
3. Công thức số can thiệp tránh được chia cho p_t thay vì p_t/(1−p_t).

Kết quả thay thế: `results/registry.json` (sinh bởi `scripts/build_results_registry.py` từ
`data/predictions/rq1/` trên bộ canonical dựng lại bằng `scripts/rebuild_canonical_dataset.py`).
