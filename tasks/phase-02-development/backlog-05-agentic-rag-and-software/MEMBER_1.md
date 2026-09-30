# BACKLOG 03 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Cấu Hình RAG, Thiết Kế Prompt Hội Chẩn Đối Kháng & Tối Ưu Tốc Độ Suy Luận GPU

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Đánh Giá & Cấu Hình Embedding Model Cho RAG
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Thử nghiệm độ tương đồng ngữ nghĩa của `sentence-transformers/all-mpnet-base-v2` đối với các câu hỏi triệu chứng y khoa so với các đoạn văn phác đồ.
  2. Viết file cấu hình `configs/rag_config.yaml`:
     - `embedding_model`: "sentence-transformers/all-mpnet-base-v2"
     - `vector_dim`: 768
     - `distance_metric`: "Cosine"
     - `top_k`: 4
     - `similarity_threshold`: 0.72
* **Đầu ra (Deliverable):** `configs/rag_config.yaml`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Thiết Kế Prompt Chain-of-Thought (CoT) Đối Kháng
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Thiết kế cấu trúc Prompt chuyên sâu cho `DiagnosticAgent`:
  - Ép LLM nhận diện 2 bệnh có xác suất cao nhất ($H_1$ vs $H_2$).
  - Đối chiếu triệu chứng trong bệnh án với các tiêu chí chẩn đoán phân biệt của phác đồ.
  - Phân tách rõ ràng:
    + `pro_evidence_claims`: Câu văn trong bệnh án ủng hộ $H_1$.
    + `counter_evidence_claims`: Câu văn trong bệnh án ủng hộ $H_2$ hoặc làm giảm khả năng $H_1$.
    + `red_flags`: Cảnh báo dấu hiệu suy hô hấp, hội chứng vành cấp hoặc đe dọa tính mạng.
  - Ràng buộc cấu trúc đầu ra nghiêm ngặt bằng chuẩn JSON.
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
* **Tiêu chuẩn nghiệm thu:** Độ trễ suy luận $\le 150\text{ms}$/request trên GPU.
* **Đầu ra (Deliverable):** `src/api/routes/inference.py`.
* **Trạng thái:** `[ ] TODO`
