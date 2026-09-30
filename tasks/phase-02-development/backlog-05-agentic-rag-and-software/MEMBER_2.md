# BACKLOG 03 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Phân Mảnh Phác Đồ Y Khoa, Nạp Qdrant Vector DB, Evidence Grounder & Explain Endpoint

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Phân Mảnh Phác Đồ Lâm Sàng & Khởi Tạo Qdrant Vector Store
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Số hóa các hướng dẫn y khoa: GINA 2024, GOLD 2024, ESC 2023, Hướng dẫn Bộ Y tế tại `data/guidelines/`.
  2. Hiện thực `src/agent/knowledge_ingest.py`:
     - Phân mảnh theo cấu trúc lâm sàng (*Hierarchical Clinical Chunking*): Tiêu chuẩn chẩn đoán, Tiêu chuẩn loại trừ, Yếu tố nguy cơ, Triệu chứng cờ đỏ.
     - Sinh vector nhúng qua `sentence-transformers`.
     - Nạp vào collection `clinical_guidelines` trên Qdrant kèm metadata: `guideline_source`, `disease_entity`, `clinical_category`, `evidence_level`.
* **Đầu ra (Deliverable):** `src/agent/knowledge_ingest.py`, Qdrant Vector Store có sẵn dữ liệu.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Hiện Thực Thuật Toán Định Vị Bằng Chứng (Evidence Grounder)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Hiện thực `src/agent/evidence_grounder.py`:
  1. Nhận chuỗi văn bản bệnh án gốc $S_{raw}$ và danh sách các câu trích dẫn của LLM.
  2. Quét Exact match và Fuzzy sliding-window matcher (ngưỡng tương đồng $\ge 0.88$).
  3. Trả về mảng tọa độ `[{ "text": "...", "start": 142, "end": 215, "confidence": 1.0 }]`.
  4. Cơ chế chống ảo giác: Tự động gắn cờ và loại bỏ bất kỳ câu claim nào không khớp với chuỗi ký tự trong bệnh án gốc.
* **Đầu ra (Deliverable):** `src/agent/evidence_grounder.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Xây Dựng REST Endpoint `/api/v1/agent/explain`
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết route `POST /api/v1/agent/explain` trong `src/api/routes/agent_chat.py`:
  - Tiếp nhận `patient_id`, `target_diagnosis` và `clinical_notes`.
  - Gọi `DiagnosticAgent` suy luận và `EvidenceGrounder` lấy vị trí spans.
  - Trả về payload JSON hoàn chỉnh gồm lập luận biện luận, mảng spans và danh mục phác đồ tham chiếu.
* **Đầu ra (Deliverable):** `src/api/routes/agent_chat.py`.
* **Trạng thái:** `[ ] TODO`
