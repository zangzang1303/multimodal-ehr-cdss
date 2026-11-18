# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Hybrid Retriever, EvidenceViewer Component, GuidelineDrawer & Kết Nối Full-Stack

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hiện Thực Hybrid Knowledge Retriever (`src/agent/retriever.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết lớp `HybridGuidelineRetriever` kết nối cơ sở dữ liệu Qdrant:
  - `[x]` Tiếp nhận query triệu chứng hoặc câu hỏi phân biệt (`disease_filter` hỗ trợ lọc theo bệnh lý hoặc giữ `ALL_RESPIRATORY_CARDIAC`).
  - `[x]` Kết hợp Dense Vector trên Qdrant (`query_points`) và Sparse BM25 qua hợp nhất thứ hạng nghịch đảo Reciprocal Rank Fusion (RRF: $\sum \frac{1}{60 + \text{rank} + 1}$); tự động nạp thêm các phân mảnh chuẩn trong `data/guidelines/*.json`; đạt `Recall@3 = 1.000` trên tập kiểm thử `scripts/eval_member3_retrieval.py`; trả đầy đủ metadata truy nguyên (`source_id`, `version`, `section_locator`, `source_verified`).
* **Đầu ra (Deliverable):** `src/agent/retriever.py`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng GuidelineDrawer & EvidenceViewer Component
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` `frontend/src/components/GuidelineDrawer.tsx`: Drawer trượt mượt mà từ bên phải, hiển thị văn bản phác đồ (GINA/GOLD/ESC/Bộ Y tế), tiêu đề phần, cấp độ chứng cứ và thông tin nguồn (`source_id`, `version`, `section_locator`, cảnh báo khi nguồn chưa xác minh).
  2. `[x]` `frontend/src/components/EvidenceViewer.tsx`: Nhận đúng ghi chú đã khử định danh (`display_note`) cùng mảng offsets; kiểm tra chặt bất biến `text === note.slice(start, end)`, loại bỏ spans chồng lấn, hiển thị số lượng trích dẫn chưa xác minh/bị lọc và tuyệt đối không render HTML thô từ LLM.
* **Đầu ra (Deliverable):** `frontend/src/components/GuidelineDrawer.tsx`, `frontend/src/components/EvidenceViewer.tsx`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.3: Viết Unit Tests Kiểm Tra Không Ảo Giác (`tests/test_agent_rag.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết bộ test kiểm tra:
  - `[x]` Đảm bảo mọi span được trả đều khớp chính xác chỉ mục trong ghi chú đã khử định danh (`display_note[start_char:end_char] == span["text"]`).
  - `[x]` Claim thiếu nguồn hoặc trích dẫn phác đồ không có `source_id`/`version`/`section_locator` bị từ chối; kiểm thử thêm span cắt xén/chồng lấn (`test_grounder_rejects_partial_and_overlapping_claims`).
  - `[x]` Chạy lệnh `pytest tests/test_agent_rag.py tests/test_agent_explain_api.py tests/test_evidence_grounder.py -v`: **20/20 tests passed 100%**.
* **Đầu ra (Deliverable):** `tests/test_agent_rag.py`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.4: Tích Hợp API Client & Đồng Bộ Toàn Bộ Giao Diện
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Viết `frontend/src/lib/api.ts` kết nối các endpoint Backend (`/api/v1/predict/multimodal`, `/api/v1/predict/mock`, `/api/v1/agent/explain`).
  2. `[x]` Nối thông suốt luồng người dùng trên Web: Bác sĩ nhập ca bệnh $\rightarrow$ Bấm nút $\rightarrow$ Gọi API `/predict/multimodal` $\rightarrow$ Gọi API `/agent/explain` $\rightarrow$ Hiển thị Card xác suất + Highlight bệnh án + Drawer phác đồ (`next lint` & `next build` pass 0 lỗi).
* **Đầu ra (Deliverable):** Giao diện Web tương tác trọn vẹn tại `http://localhost:3000`.
* **Trạng thái:** `[x] DONE`
