# BACKLOG 03 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Hybrid Retriever, EvidenceViewer Component, GuidelineDrawer & Kết Nối Full-Stack

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hiện Thực Hybrid Knowledge Retriever (`src/agent/retriever.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết lớp `HybridGuidelineRetriever` kết nối cơ sở dữ liệu Qdrant:
  - Tiếp nhận query triệu chứng hoặc câu hỏi phân biệt.
  - Kết hợp điểm Cosine Dense Embedding và lọc từ khóa BM25 để trả về các phân mảnh phác đồ phù hợp nhất kèm metadata.
* **Đầu ra (Deliverable):** `src/agent/retriever.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng GuidelineDrawer & EvidenceViewer Component
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `frontend/src/components/GuidelineDrawer.tsx`: Drawer trượt mượt mà từ bên phải, hiển thị trọn vẹn văn bản phác đồ y tế chuẩn được trích dẫn (GINA/GOLD/ESC), tiêu đề phần và cấp độ chứng cứ (Evidence Level A/B).
  2. `frontend/src/components/EvidenceViewer.tsx`: Nhận chuỗi bệnh án gốc và mảng offsets `[{start, end, text}]`. Tự động chèn thẻ `<mark>` highlight màu vàng làm sáng các câu chứng cứ trong bệnh án.
* **Đầu ra (Deliverable):** `GuidelineDrawer.tsx`, `EvidenceViewer.tsx`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Viết Unit Tests Kiểm Tra Không Ảo Giác (`tests/test_agent_rag.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết bộ test kiểm tra:
  - Đảm bảo 100% câu claim được `EvidenceGrounder` trả về đều tồn tại chính xác tại chỉ mục ký tự trong bệnh án gốc.
  - Đảm bảo nếu LLM bịa đặt một câu không có trong bệnh án, hệ thống sẽ loại bỏ hoàn toàn câu đó.
  - Chạy lệnh: `pytest tests/test_agent_rag.py -v` (pass 100%).
* **Đầu ra (Deliverable):** `tests/test_agent_rag.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.4: Tích Hợp API Client & Đồng Bộ Toàn Bộ Giao Diện
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết `frontend/src/lib/api.ts` kết nối các endpoint Backend.
  2. Nối thông suốt luồng người dùng trên Web: Bác sĩ nhập ca bệnh $\rightarrow$ Bấm nút $\rightarrow$ Gọi API `/predict/multimodal` $\rightarrow$ Gọi API `/agent/explain` $\rightarrow$ Hiển thị Card xác suất + Highlight bệnh án + Drawer phác đồ.
* **Đầu ra (Deliverable):** Giao diện Web tương tác trọn vẹn tại `http://localhost:3000`.
* **Trạng thái:** `[ ] TODO`
