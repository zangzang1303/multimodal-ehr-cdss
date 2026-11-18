# BACKLOG 09 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

## Nhiệm vụ 3.1 [CORE] – Đánh giá truy xuất & neo bằng chứng (RQ5)
- Mở rộng `data/retrieval_queries_member3.json` lên **≥ 60 truy vấn** (15/bệnh: triệu chứng, tiêu chuẩn chẩn đoán, chẩn đoán phân biệt, cờ đỏ). Hai thành viên gán nhãn chunk liên quan độc lập → báo cáo Cohen's κ.
- So sánh dense (all-mpnet-base-v2), BM25, hybrid (và reranker `bge-reranker-v2-m3` nếu có sẵn trong cache): Recall@1/3/5, MRR, nDCG@5.
- Grounding: trên 50 ca test, đo (a) % claim có span khớp ghi chú, (b) % claim bị từ chối, (c) kiểm tra thủ công 20 span: span có thực sự ủng hộ claim không (precision ngữ nghĩa) – vì trùng chuỗi không chứng minh diễn giải đúng.
- Script `scripts/eval_rag.py` → registry mục `rag`.

## Nhiệm vụ 3.2 [CORE] – Cơ sở tri thức phác đồ đúng chuẩn trích dẫn
- KB hiện có **14 chunk** diễn giải. Mở rộng lên ~60–100 chunk: mỗi chunk có `source_id`, phiên bản, chương/mục/trang, loại (tiêu chuẩn chẩn đoán / phân biệt / cờ đỏ), `is_paraphrase`.
- Sửa `data/guidelines/CATALOG.yaml`: GINA/GOLD/ESC là tài liệu **có bản quyền** – bỏ câu "permitted under FAIR guidelines"; ghi "trích dẫn ngắn & diễn giải cho mục đích nghiên cứu, không phân phối lại toàn văn". Hướng dẫn BYT là văn bản pháp quy – ghi số quyết định.
- Ingest lại, cập nhật snapshot + `manifest.json`.

## Nhiệm vụ 3.3 [OPTIONAL] – Chế độ suy luận LLM có ràng buộc
- Thêm `reasoning_mode = "llm"` sau cờ cấu hình (nhà cung cấp cấu hình qua `.env`, mặc định tắt). Đầu ra JSON schema cố định; **mọi claim phải qua EvidenceGrounder**, claim không neo được bị loại.
- So sánh với chế độ deterministic trên 30 ca: % claim được neo, số claim hữu ích, latency, chi phí.
- Không gửi dữ liệu chưa khử định danh ra dịch vụ ngoài; chỉ dùng ghi chú tổng hợp đã de-ID.
- Nếu không làm: trong paper/slide gọi đúng tên là **"pipeline giải trình truy xuất + neo bằng chứng (deterministic)"**, không gọi "LLM agent".

## Nhiệm vụ 3.4 [CORE] – Đo độ trễ
- `scripts/benchmark_latency.py`: 200 request/endpoint (`/predict/multimodal`, `/agent/explain`), warm & cold, CPU và GPU (nếu có). Báo cáo p50/p95/p99 kèm cấu hình máy, độ dài ghi chú.

## Nhiệm vụ 3.5 [CORE] – UI cho các phát hiện mới
- Trang `/evaluation`: bảng chính có CI, biểu đồ phân rã văn bản (RQ2), DCA có dải CI, missing-modality.
- Trang phân tích ca: cho phép bỏ một phương thức để xem xác suất thay đổi (demo trực tiếp RQ4 trước hội đồng).
- Hiển thị khoảng không chắc chắn và cảnh báo khi max prob < ngưỡng (ví dụ "Mô hình không chắc chắn – cần đánh giá lâm sàng").

**Nghiệm thu Thành viên 3:** registry có `rag`, `latency`; KB ≥ 60 chunk có metadata đầy đủ; UI hiển thị kết quả từ registry.
