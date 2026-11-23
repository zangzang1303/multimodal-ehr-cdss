# BACKLOG 09 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **Cập nhật trạng thái thực hiện (Phase 3 — Bản chuẩn hóa sau rà soát):** Đã tách `eval_rag.py` sang chế độ **chỉ đọc** trên Qdrant từ xa (xác minh khớp chiều `768`, `64/64` `chunk_id`, `SHA-256` của `text_content` và 8 trường metadata, *chưa xác nhận chất lượng ngữ nghĩa của vector băm*), đánh dấu rõ audit 50 ca là **sơ bộ** (`preliminary_non_strict_holdout` từ `data/processed/test.parquet` $N=287$, chưa phải `strict N=302`, 0 template fallback), đổi tên trường đo probe sang `out_of_note_probe_rejection_rate`, và giữ giới hạn diễn giải trung thực cạnh các chỉ số Recall.

## Nhiệm vụ 3.1 [CORE] – Đánh giá truy xuất & neo bằng chứng (RQ5)

- [x] Mở rộng `data/retrieval_queries_member3.json` lên **60 truy vấn** (15/bệnh lý) chuẩn hóa toàn bộ ID tham chiếu về đúng 64 chunk JSON (`data/guidelines/*.json`) có gán nhãn kép độc lập ($\kappa_{\text{Cohen}} = 0,9449$).
- [x] Cập nhật và chạy **chỉ đọc** `scripts/eval_rag.py` trên Qdrant Docker sống (`http://127.0.0.1:6333`, xác minh chiều `768`, `64/64` `chunk_id`, `64/64` `SHA-256` nội dung và `64/64` trên 8 trường metadata; `qdrant_vector_semantics_verified=false`, `strict_qdrant=True`), ghi vào `results/rag_evaluation_report.json` và `results/registry.json["rag"]` (**đều đo với vector băm 768-D ngoại tuyến `dense_encoder_is_semantic_model=false`, chưa phải `all-mpnet-base-v2`**): `dense_only` (`R@1=0,7833`, `R@3=0,9167`, `R@5=0,9833`, `MRR=0,8688`, `nDCG@5=0,8729`), `bm25_only` & `hybrid_rrf` (`R@1=0,9000`, `R@3=0,9500`, `R@5=1,0000`, `MRR=0,9319`, `nDCG@5=0,9354`).
- [x] Thực hiện **kiểm tra sơ bộ** (`audit_status = "preliminary_non_strict_holdout"`) bất biến tọa độ và từ chối chuỗi ngoài văn bản trên **50 ca từ `data/processed/test.parquet`** ($N=287$, chưa phải tập `strict N=302` chính thức, 0 ca template fallback): `200/200` claim ứng viên của `explain_clinical_case()` thỏa mãn khớp vị trí ký tự `display_note[start:end] == text`, `50/50` đầu dò chuỗi ngoài bệnh án bị loại (`out_of_note_probe_rejection_rate = 1,00`), đồng thời xuất 20 đoạn thực tế sang `results/grounding_manual_audit_20_samples.json`. _(Phạm vi: kết quả sơ bộ chỉ chứng minh khớp chuỗi & lọc probe ngoài văn bản trên split cũ, không đo hallucination ngữ nghĩa và không thay thế kiểm định trên `strict N=302`)._
- [ ] **Chấm ngữ nghĩa thủ công 20 mẫu span (`manual_semantic_precision_20_spans`):** **Chưa hoàn thành (`null` / `pending_human_review`)** — _Lý do:_ Đã gỡ bỏ phép kiểm tra độ dài giả lập; đang chờ người đánh giá đọc đối chiếu 20 mẫu trong `results/grounding_manual_audit_20_samples.json` và điền `human_verified`.
- [ ] **Đánh giá lại trên tập ghi chú strict hold-out `N = 302` (`data/processed_rebuilt_strict/test.parquet`) và với encoder ngữ nghĩa `all-mpnet-base-v2` + `bge-reranker-v2-m3`:** **Chưa hoàn thành** — _Lý do:_ Hiện chưa có `data/processed_rebuilt_strict/test.parquet` của TV2 và môi trường ngoại tuyến thiếu cache HuggingFace của hai mô hình này.

## Nhiệm vụ 3.2 [CORE] – Cơ sở tri thức phác đồ đúng chuẩn trích dẫn

- [x] Sửa `data/guidelines/CATALOG.yaml`: gỡ bỏ câu `"permitted under FAIR guidelines"`, ghi rõ GINA/GOLD/ESC là tài liệu có bản quyền chỉ trích dẫn ngắn & diễn giải phục vụ nghiên cứu, giữ nguyên thông tin văn bản pháp quy Bộ Y tế VN.
- [x] Tạo `data/guidelines/extended_clinical_guidelines_v2.json` (50 chunk mới) kết hợp 14 chunk cũ tạo thành **64 chunk JSON chuẩn hóa** (16 chunk/bệnh) đầy đủ `source_id`, `version`, `page_or_section`, `is_paraphrase`, bảo toàn `evidence_level: null` cho `BYT_VN_CAP_2020`.
- [x] Đã ingest riêng bằng `knowledge_ingest.py` và xác minh đọc-chỉ khớp chiều `768`, `64/64` `chunk_id`, `64/64` `SHA-256` nội dung và `64/64` trên 8 trường metadata truy nguyên giữa `data/guidelines/*.json`, RAM BM25 và Qdrant Docker `v1.20.0` (*chưa xác nhận chất lượng ngữ nghĩa của vector băm ngoại tuyến*).
- [ ] **Cập nhật snapshot Qdrant gắn SHA-256 cùng `manifest.json` chính thức của TV2/TV1:** **Chưa hoàn thành** — _Lý do:_ Hiện mới gắn tham chiếu với file **mock** `data/DATA_MANIFEST.json`, chờ TV2 chốt bản dữ liệu đóng băng chính thức.

## Nhiệm vụ 3.3 [OPTIONAL] – Chế độ suy luận LLM có ràng buộc

- [ ] **Tùy chọn tích hợp `reasoning_mode = "llm"` có ràng buộc JSON + `EvidenceGrounder`:** **Chủ động không triển khai (chọn nhánh fallback của đặc tả)** — _Lý do:_ Giữ chế độ mặc định tất định **`deterministic_template`** và gọi đúng tên trong mọi tài liệu.

## Nhiệm vụ 3.4 [CORE] – Đo độ trễ

- [x] Mở rộng và chạy `scripts/benchmark_latency.py --base-url http://127.0.0.1:8000` đo trực tiếp qua HTTP/TCP Docker (`measurement_mode = "http_docker_end_to_end"`, 200 lượt gọi ấm sau 1 cold request, note 340 ký tự, _Windows 11 AMD64, CPU 16 logical cores_) ghi vào `results/latency_report.json` & `results/registry.json["latency"]`: `/api/v1/agent/explain` (**HTTP 200**: `cold=169,03 ms`, `mean=63,49 ms`, `p50=62,92 ms`, `p95=84,23 ms`, `p99=92,25 ms`).
- [ ] **Đo latency `HTTP 200` của `/api/v1/predict/multimodal`, `/api/v1/predict/baseline` và trên GPU:** **Chưa hoàn thành** — _Lý do:_ Trên stack Docker triển khai nhẹ hiện tại, cả `/predict/baseline` (`p95=51,24 ms`) và `/predict/multimodal` (`p95=50,55 ms`) đều đo phản hồi bảo vệ **`HTTP 503`** (thiếu baseline thật của TV1, thiếu `torch` trong `requirements-deploy.txt`, thiếu cache `Bio_ClinicalBERT` và không có GPU).

## Nhiệm vụ 3.5 [CORE] – UI cho các phát hiện mới

- [x] Tạo `GET /api/v1/evaluation/registry` và cập nhật trang `/evaluation` (Tab 3 hiển thị phạm vi Qdrant đọc-chỉ `768-D/ID/SHA-256/8 metadata` kèm cảnh báo chưa xác nhận chất lượng vector băm ngoại tuyến, nhãn **sơ bộ** cho audit 50 ca từ `data/processed/test.parquet` `N=287`, trường `out_of_note_probe_rejection_rate`, và ô `Chờ chấm tay (20 mẫu)`).
- [x] Sửa nhãn biểu đồ `DCACurveChart.tsx` về đúng mô tả **Macro One-vs-Rest trung bình 4 lớp** (loại bỏ nhãn gán riêng `HEART_FAILURE` / `35.1%` / Doppler echo không khớp công thức).
- [x] Sửa banner `EvidenceViewer.tsx` tránh khẳng định quá mức (`khớp vị trí ký tự... không đồng nghĩa xác nhận ngữ nghĩa hay chẩn đoán lâm sàng`).
- [x] Bổ sung công tắc **RQ4 Missing-Modality Toggle** trong `PatientDataForm.tsx` và cảnh báo bất định Top-1 $< 55\%$ trong `DiagnosticCard.tsx`.
- [ ] **Hiển thị số liệu thực nghiệm chính thức cho RQ1 (CI 95%), RQ2 (phân rã văn bản), DCA hold-out và RQ4 trên `/evaluation`:** **Chưa hoàn thành với dữ liệu thật** — _Lý do:_ TV1 & TV2 chưa bàn giao kết quả đa seed và file dự đoán hold-out từng mẫu; UI hiện hiển thị từ dữ liệu mô phỏng/mock có gắn nhãn cảnh báo rõ ràng.

**Trạng thái nghiệm thu Backlog 09 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Còn chờ chấm tay 20 mẫu grounding, dữ liệu strict `N=302`, cache `all-mpnet-base-v2`/`Bio_ClinicalBERT`, GPU và kết quả RQ1–RQ4 thật từ TV1/TV2.
