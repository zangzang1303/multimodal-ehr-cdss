# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Hybrid Retriever, EvidenceViewer Component, GuidelineDrawer & Kết Nối Full-Stack

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hiện Thực Hybrid Knowledge Retriever (`src/agent/retriever.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết lớp `HybridGuidelineRetriever` kết nối cơ sở dữ liệu Qdrant:
  - Tiếp nhận query triệu chứng hoặc câu hỏi phân biệt.
  - Kết hợp dense và BM25, xác định cách chuẩn hóa/hợp nhất điểm; đánh giá Recall@K trên tập truy vấn có nhãn. Trả `source_id`, phiên bản và vị trí mục/trang cho mỗi kết quả.
* **Đầu ra (Deliverable):** `src/agent/retriever.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng GuidelineDrawer & EvidenceViewer Component
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `frontend/src/components/GuidelineDrawer.tsx`: Drawer trượt mượt mà từ bên phải, hiển thị trọn vẹn văn bản phác đồ y tế chuẩn được trích dẫn (GINA/GOLD/ESC), tiêu đề phần và cấp độ chứng cứ (Evidence Level A/B).
  2. `frontend/src/components/EvidenceViewer.tsx`: Nhận đúng ghi chú đã khử định danh cùng mảng offsets; kiểm tra `text === note.slice(start, end)`, xử lý spans chồng lấn và hiển thị trạng thái claim chưa xác minh, không render HTML thô từ LLM.
* **Đầu ra (Deliverable):** `GuidelineDrawer.tsx`, `EvidenceViewer.tsx`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Viết Unit Tests Kiểm Tra Không Ảo Giác (`tests/test_agent_rag.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết bộ test kiểm tra:
  - Đảm bảo mọi span được trả đều khớp chính xác chỉ mục trong ghi chú đã khử định danh đang hiển thị.
  - Claim thiếu nguồn hoặc trích dẫn phác đồ không truy ngược được phải bị từ chối/gắn `unverified`; test thêm span sai, chồng lấn và thay đổi văn bản.
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
