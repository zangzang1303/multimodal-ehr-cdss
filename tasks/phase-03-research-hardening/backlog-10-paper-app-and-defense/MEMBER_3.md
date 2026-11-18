# BACKLOG 10 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

## Nhiệm vụ 3.1 – Docker clean-run & smoke test
- Trên **máy thứ hai** (hoặc VM sạch): làm theo README từ đầu → `docker compose up --build -d` → 3 dịch vụ healthy.
- `scripts/smoke_test.ps1` / `.sh`: `/health`, `/api/v1/predict/status`, 1 ca `/predict/multimodal`, 1 ca `/agent/explain`, trang `/` và `/evaluation` trả 200.
- README: mục "Quick start 5 phút", cách lấy checkpoint + data + Qdrant snapshot (kèm SHA-256), yêu cầu phần cứng, xử lý sự cố thường gặp.

## Nhiệm vụ 3.2 – Section System & hình vẽ
- `04_software_architecture.tex`, `05_multi_agent_rag.tex`, `06_frontend_dca_ux.tex`: xoá `[TODO]`; mô tả đúng chế độ suy luận (deterministic / LLM nếu đã làm); thêm bảng latency p50/p95 và bảng RAG (Recall@k, MRR, grounding).
- Xuất sơ đồ kiến trúc vector (SVG/PDF) đồng bộ giữa paper và slide; ảnh chụp UI thật (không mock).

## Nhiệm vụ 3.3 – Video demo 3–5 phút
Kịch bản (cập nhật `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md`, xoá 10 placeholder):
1. (0:00–0:30) Bài toán & cảnh báo phạm vi nghiên cứu.
2. (0:30–2:00) Nhập ca tổng hợp → xác suất hiệu chuẩn → highlight chứng cứ → mở drawer phác đồ.
3. (2:00–3:00) Bỏ phương thức văn bản → xác suất thay đổi (minh hoạ RQ4); ca mô hình không chắc chắn.
4. (3:00–4:00) Trang đánh giá: bảng có CI, phân rã văn bản (RQ2), DCA.
5. (4:00–4:30) Giới hạn & hướng phát triển.

## Nhiệm vụ 3.4 – Slide thuyết trình (15–20 trang) & demo trực tiếp
Cập nhật `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md` (xoá 21 placeholder). Mạch đề xuất:
1. Vấn đề & khoảng trống (1–2) → 2. Câu hỏi nghiên cứu (1) → 3. Dữ liệu & chống rò rỉ (2) → 4. Phương pháp (2) → 5. Kết quả RQ1–RQ2 – **phát hiện chính** (3) → 6. Hiệu chuẩn, DCA, độ bền (2) → 7. Hệ thống & demo (3) → 8. Giới hạn trung thực (1) → 9. Hướng phát triển: MIMIC-IV, khảo sát bác sĩ, LLM có ràng buộc (1) → 10. Kết luận (1).
- Chuẩn bị **phương án dự phòng**: video demo cục bộ + ảnh chụp, nếu demo trực tiếp lỗi mạng/GPU.
- Bấm giờ: tổng ≤ thời lượng quy định, mỗi người nói phần mình phụ trách.

## Nhiệm vụ 3.5 – Q&A phần hệ thống
Câu trả lời ngắn cho: Vì sao Qdrant? grounding chống ảo giác đến mức nào? latency bao nhiêu, chạy CPU được không? triển khai thực tế cần gì (HL7 FHIR, phân quyền, audit log, giám sát drift)?
