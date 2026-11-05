# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Phân Mảnh Phác Đồ Y Khoa, Nạp Qdrant Vector DB, Evidence Grounder & Explain Endpoint

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Phân Mảnh Phác Đồ Lâm Sàng & Khởi Tạo Qdrant Vector Store
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Lập danh mục tài liệu GINA/GOLD/ESC/Bộ Y tế theo phiên bản phù hợp, nguồn chính thức, ngày truy cập và quyền lưu trữ; chỉ số hóa tài liệu được phép dùng tại `data/guidelines/`.
  2. Hiện thực `src/agent/knowledge_ingest.py`:
     - Phân mảnh theo cấu trúc lâm sàng (*Hierarchical Clinical Chunking*): Tiêu chuẩn chẩn đoán, Tiêu chuẩn loại trừ, Yếu tố nguy cơ, Triệu chứng cờ đỏ.
     - Sinh vector nhúng qua `sentence-transformers`.
     - Nạp vào collection `clinical_guidelines` trên Qdrant kèm `source_id`, phiên bản, mục/trang, nội dung gốc và các metadata lâm sàng có trong tài liệu; không tự gán `evidence_level` nếu nguồn không nêu.
* **Đầu ra (Deliverable):** `src/agent/knowledge_ingest.py`, Qdrant Vector Store có sẵn dữ liệu.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Hiện Thực Thuật Toán Định Vị Bằng Chứng (Evidence Grounder)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Hiện thực `src/agent/evidence_grounder.py`:
  1. Nhận đúng phiên bản ghi chú đã khử định danh $S$ đang hiển thị cho người dùng và danh sách trích dẫn/claim của LLM; không trả offset từ văn bản thô có PHI.
  2. Ưu tiên exact match và kiểm tra `S[start:end] == text`. Fuzzy match chỉ đề xuất ứng viên để kiểm tra tiếp, không tự động xác nhận claim ở ngưỡng 0.88.
  3. Trả về mảng tọa độ `[{ "text": "...", "start": 142, "end": 215, "confidence": 1.0 }]`.
  4. Gắn cờ/từ chối claim thiếu đoạn nguồn. Tách kiểm tra vị trí trích dẫn khỏi kiểm tra ý nghĩa lâm sàng; claim đúng vị trí vẫn có thể diễn giải sai.
* **Đầu ra (Deliverable):** `src/agent/evidence_grounder.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Xây Dựng REST Endpoint `/api/v1/agent/explain`
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết route `POST /api/v1/agent/explain` trong `src/api/routes/agent_chat.py`:
  - Tiếp nhận ca bệnh và ghi chú đã khử định danh; không tin `patient_id` hay `target_diagnosis` do client gửi như nhãn thật.
  - Gọi `DiagnosticAgent` suy luận và `EvidenceGrounder` lấy vị trí spans.
  - Trả về JSON gồm claims, trạng thái kiểm chứng, spans trên đúng văn bản hiển thị và trích dẫn phác đồ có ID/phiên bản/mục; trả trạng thái thiếu bằng chứng khi không truy hồi được nguồn.
* **Đầu ra (Deliverable):** `src/api/routes/agent_chat.py`.
* **Trạng thái:** `[ ] TODO`
