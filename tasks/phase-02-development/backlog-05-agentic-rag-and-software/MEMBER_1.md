# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng tâm: cấu hình RAG, giải trình có nguồn và đo độ trễ suy luận

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Đánh Giá & Cấu Hình Embedding Model Cho RAG
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Đánh giá `sentence-transformers/all-mpnet-base-v2` và phương án phù hợp ngôn ngữ tài liệu trên tập câu hỏi–đoạn phác đồ được gán nhãn; báo cáo Recall@K trước khi chọn model.
  2. Viết file cấu hình `configs/rag_config.yaml`:
     - `embedding_model`: "sentence-transformers/all-mpnet-base-v2"
     - `vector_dim`: 768
     - `distance_metric`: "Cosine"
     - `top_k`: 4
     - `similarity_threshold`: giá trị chọn trên tập validation truy hồi, không cố định 0.72 khi chưa đo.
* **Đầu ra (Deliverable):** `configs/rag_config.yaml`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Thiết Kế Đầu Ra Giải Trình Có Cấu Trúc
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Thiết kế đầu ra JSON có cấu trúc cho `DiagnosticAgent`:
  - Ép LLM nhận diện 2 bệnh có xác suất cao nhất ($H_1$ vs $H_2$).
  - Đối chiếu triệu chứng trong bệnh án với các tiêu chí chẩn đoán phân biệt của phác đồ.
  - Phân tách rõ ràng:
    + `pro_evidence_claims`: Câu văn trong bệnh án ủng hộ $H_1$.
    + `counter_evidence_claims`: Câu văn trong bệnh án ủng hộ $H_2$ hoặc làm giảm khả năng $H_1$.
    + `red_flags`: Cảnh báo dấu hiệu suy hô hấp, hội chứng vành cấp hoặc đe dọa tính mạng.
  - Mỗi claim có `source_type`, `source_id`, đoạn trích và trạng thái kiểm chứng; nếu thiếu nguồn, trả `unverified` hoặc từ chối. Không trình bày suy luận nội bộ của LLM như bằng chứng lâm sàng.
* **Đầu ra (Deliverable):** Module logic prompt trong `src/agent/diagnostic_agent.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Tối Ưu Hóa Inference Engine GPU Trên FastAPI
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết class nạp mô hình vào GPU lúc ứng dụng FastAPI khởi động (`lifespan event`) trong `src/api/routes/inference.py`.
  2. Viết endpoint `POST /api/v1/predict/multimodal`:
     - Nhận payload bảng và text ghi chú.
     - Tiền xử lý tensor $\rightarrow$ Forward pass qua Multimodal Fusion $\rightarrow$ Áp dụng Temperature Scaling.
     - Trả về danh sách xác suất đã hiệu chuẩn kèm thời gian thực thi `latency_ms`.
* **Tiêu chuẩn nghiệm thu:** Đo p50/p95 trên GPU và CPU (nếu hỗ trợ), ghi phần cứng, batch size, chiều ghi chú và phạm vi đo (model riêng hay toàn API). 150 ms là mục tiêu tối ưu có điều kiện, không áp cho RAG/LLM khi chưa benchmark.
* **Đầu ra (Deliverable):** `src/api/routes/inference.py`.
* **Trạng thái:** `[ ] TODO`
