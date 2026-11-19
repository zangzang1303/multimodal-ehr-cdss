# BACKLOG 09 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **Cập nhật trạng thái thực hiện (Phase 3 — Chưa commit):** Thành viên 3 đã hoàn tất bộ kiểm định RAG 60 truy vấn, mở rộng KB lên 64 đoạn JSON (70 vector), đo độ trễ CPU 200 lượt và xây dựng UI mới. Tuy nhiên backlog **chưa hoàn thành 100%** do thiếu kết quả thật RQ1–RQ4 từ TV1/TV2 và thiếu cache trọng số `all-mpnet-base-v2`/`bge-reranker-v2-m3`/`Bio_ClinicalBERT` + GPU trên máy cục bộ.

## Nhiệm vụ 3.1 [CORE] – Đánh giá truy xuất & neo bằng chứng (RQ5)
- [x] Mở rộng `data/retrieval_queries_member3.json` lên **60 truy vấn** (15/bệnh lý) có gán nhãn kép độc lập và tính hệ số đồng thuận $\kappa_{\text{Cohen}} = 0,9725$.
- [x] Tạo và thực thi `scripts/eval_rag.py` ghi kết quả đo thực tế (`is_mock: false`) vào `results/rag_evaluation_report.json` và `results/registry.json["rag"]` cho `dense_only`, `bm25_only`, `hybrid_rrf` (`Recall@1/3/5`, `MRR`, `nDCG@5`).
- [x] Hoàn tất kiểm định Grounding trên **50 ca lâm sàng**: `100/100` nhận định thật neo đúng (`1,00`), `50/50` nhận định tiêm nhiễu ảo giác bị bác bỏ (`1,00`), tỷ lệ khớp chuỗi con `1,00` và kiểm tra ngữ nghĩa thủ công `20/20` đoạn trích (`1,00`).
- [ ] **Đánh giá thêm cấu hình dense `all-mpnet-base-v2` gốc và reranker `bge-reranker-v2-m3`:** **Chưa hoàn thành** — *Lý do:* Môi trường kiểm thử ngoại tuyến không có sẵn bộ nhớ đệm HuggingFace của `all-mpnet-base-v2` và `bge-reranker-v2-m3`, do đó nhánh dense phải chạy qua fallback vector băm 768 chiều (`768d_hashed_deterministic_cpu_fallback`) để không treo quá trình đánh giá.

## Nhiệm vụ 3.2 [CORE] – Cơ sở tri thức phác đồ đúng chuẩn trích dẫn
- [x] Sửa `data/guidelines/CATALOG.yaml`: gỡ bỏ câu `"permitted under FAIR guidelines"`, ghi rõ GINA/GOLD/ESC là tài liệu có bản quyền chỉ trích dẫn ngắn & diễn giải phục vụ nghiên cứu, giữ nguyên thông tin văn bản pháp quy và số quyết định Bộ Y tế VN.
- [x] Tạo `data/guidelines/extended_clinical_guidelines_v2.json` mở rộng từ 14 lên **64 chunk JSON** (16 chunk/bệnh) đầy đủ `source_id`, `version`, `section_locator`, `clinical_category`, `is_paraphrase`, bảo toàn `evidence_level: null` cho nguồn `BYT_VN_CAP_2020`.
- [x] Đã ingest lại toàn bộ (64 JSON + 6 seed = **70 vector** trong Qdrant `clinical_guidelines`) và kiểm định qua `tests/test_knowledge_ingest.py`.
- [ ] **Cập nhật snapshot Qdrant gắn SHA-256 cùng `manifest.json` chính thức của TV1:** **Chưa hoàn thành** — *Lý do:* Hiện mới gắn tham chiếu với file **mock** `data/DATA_MANIFEST.json`, chờ TV1 chốt bản dữ liệu đóng băng chính thức.

## Nhiệm vụ 3.3 [OPTIONAL] – Chế độ suy luận LLM có ràng buộc
- [ ] **Tùy chọn tích hợp `reasoning_mode = "llm"` có ràng buộc JSON + `EvidenceGrounder`:** **Chủ động không triển khai trong đợt này (chọn nhánh fallback của đặc tả Nhiệm vụ 3.3)** — *Lý do:* Nhằm tránh phụ thuộc LLM ngoài hoặc yêu cầu VRAM lớn, hệ thống thống nhất giữ chế độ mặc định tất định **`deterministic_template`** và đã rà soát toàn bộ paper LaTeX + slide gọi đúng tên là *pipeline giải trình truy xuất + neo bằng chứng (deterministic)*.

## Nhiệm vụ 3.4 [CORE] – Đo độ trễ
- [x] Viết và thực thi `scripts/benchmark_latency.py` đo 200 lượt gọi ấm sau 1 cold request (độ dài ghi chú 340 ký tự, cấu hình *Windows 11 AMD64, 16 logical cores*) ghi `p50/p95/p99` thực tế vào `results/latency_report.json` và `results/registry.json["latency"]` (`/api/v1/agent/explain` HTTP 200: `p50 = 9,15 ms`, `p95 = 11,46 ms`; `/api/v1/predict/baseline`: `p95 = 4,74 ms`).
- [ ] **Đo latency trên GPU và luồng `HTTP 200` của `/api/v1/predict/multimodal`:** **Chưa hoàn thành** — *Lý do:* Máy hiện tại chạy CPU-only và thiếu cache cục bộ của `emilyalsentzer/Bio_ClinicalBERT`, nên `/api/v1/predict/multimodal` trả về `HTTP 503` an toàn (`p95 = 102,52 ms`) đúng thiết kế bảo vệ; cần chạy lại trên máy có cache HF đầy đủ và GPU.

## Nhiệm vụ 3.5 [CORE] – UI cho các phát hiện mới
- [x] Tạo điểm cuối `GET /api/v1/evaluation/registry` và cập nhật trang `/evaluation` (Tab 3 hiển thị dữ liệu thống nhất từ `results/registry.json`, bao gồm bảng RQ5 RAG và Latency thật của TV3).
- [x] Bổ sung công tắc **RQ4 Missing-Modality Toggle** trong `PatientDataForm.tsx` cho phép ẩn văn bản hoặc chỉ số bảng để quan sát biến thiên xác suất trực tiếp khi demo.
- [x] Bổ sung hộp cảnh báo bất định lâm sàng trong `DiagnosticCard.tsx` khi xác suất Top-1 $< 55\%$.
- [ ] **Hiển thị số liệu thực nghiệm chính thức cho RQ1 (CI 95%), RQ2 (phân rã văn bản) và RQ4 trên `/evaluation`:** **Chưa hoàn thành với dữ liệu thật** — *Lý do:* Thành viên 1 & 2 chưa xuất kết quả đa seed thật vào `results/registry.json`; UI hiện hiển thị từ dữ liệu **mock** (`is_mock: true`) có nhãn phân biệt rõ ràng trên `/evaluation`.

**Trạng thái nghiệm thu Backlog 09 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Phần `rag`, `latency` và `KB >= 60 chunk` của TV3 đã có số đo thật; các phần RQ1–RQ4 trên UI và benchmark `HTTP 200` của `/predict/multimodal` + `all-mpnet-base-v2`/`GPU` còn chờ kết quả từ TV1/TV2 và môi trường có đầy đủ cache HF/GPU.
