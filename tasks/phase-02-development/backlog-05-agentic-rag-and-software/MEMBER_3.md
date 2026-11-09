# BACKLOG 05 (AGENTIC RAG & UI) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Hybrid Retriever, EvidenceViewer Component, GuidelineDrawer & Kết Nối Full-Stack

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hiện Thực Hybrid Knowledge Retriever (`src/agent/retriever.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết lớp `HybridGuidelineRetriever` kết nối cơ sở dữ liệu Qdrant / In-memory:
  - Tiếp nhận query triệu chứng hoặc câu hỏi phân biệt.
  - Kết hợp điểm Cosine Dense Embedding (nạp và truy vấn `PointStruct` trên `QdrantClient` với `Distance.COSINE`) và điểm từ khóa Okapi BM25 ($k_1=1.5, b=0.75$) theo tổ hợp lồi $S_{\text{hybrid}} = \alpha S_{\text{bm25}} + (1 - \alpha) S_{\text{cosine}}$ để trả về các phân mảnh phác đồ phù hợp nhất kèm metadata (`GOLD_2024`, `GINA_2024`, `ESC_2023`, `BYT_2020`).
* **Đầu ra (Deliverable):** `src/agent/retriever.py`, `src/agent/diagnostic_graph.py`, `src/agent/__init__.py`.
* **Trạng thái:** `[x] DONE` *(Đã hiện thực đầy đủ Qdrant Vector indexing/querying + Okapi BM25 + Cosine Hybrid scoring và kiểm thử tự động trong `tests/test_agent_rag.py`).*

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng GuidelineDrawer & EvidenceViewer Component
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `frontend/src/components/GuidelineDrawer.tsx`: Drawer trượt mượt mà từ bên phải, hiển thị trọn vẹn văn bản phác đồ y tế chuẩn được trích dẫn (GINA/GOLD/ESC/Bộ Y tế), tiêu đề phần và cấp độ chứng cứ (Evidence Level A/B).
  2. `frontend/src/components/EvidenceViewer.tsx`: Nhận chuỗi bệnh án gốc và mảng offsets `[{start, end, text, category, label, reason}]`. Tự động chèn thẻ `<mark>` highlight màu sắc trực quan (xanh lá cho ủng hộ, xanh tím cho phân biệt, đỏ cho cờ đỏ).
* **Đầu ra (Deliverable):** `GuidelineDrawer.tsx`, `EvidenceViewer.tsx`.
* **Trạng thái:** `[x] DONE` *(Đã hoàn thiện cả 2 components và tích hợp vào `DiagnosticCard.tsx`).*

---

### 🔹 Nhiệm vụ 3.3: Viết Unit Tests Kiểm Tra Không Ảo Giác (`tests/test_agent_rag.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết bộ test kiểm tra:
  - Đảm bảo 100% câu claim được `EvidenceGrounder` trả về đều tồn tại chính xác tại chỉ mục ký tự trong bệnh án gốc.
  - Đảm bảo nếu LLM bịa đặt một câu không có trong bệnh án, hệ thống sẽ loại bỏ hoàn toàn câu đó.
  - Kiểm tra Qdrant indexing, hybrid score (`bm25_score` + `cosine_score`) và luồng 4 nút `DiagnosticStateGraph`.
  - Chạy lệnh: `pytest tests/test_agent_rag.py -v` (pass 100%).
* **Đầu ra (Deliverable):** `tests/test_agent_rag.py`.
* **Trạng thái:** `[x] DONE` *(11/11 tests trong `test_agent_rag.py` passed 100%).*

---

### 🔹 Nhiệm vụ 3.4: Tích Hợp API Client & Đồng Bộ Toàn Bộ Giao Diện
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết `frontend/src/lib/api.ts` kết nối các endpoint Backend (`explainClinicalCase`).
  2. Nối thông suốt luồng người dùng trên Web: Bác sĩ nhập ca bệnh $\rightarrow$ Bấm nút $\rightarrow$ Gọi API `/predict/mock` $\rightarrow$ Gọi API `/agent/explain` $\rightarrow$ Hiển thị Card xác suất + Highlight bệnh án + Drawer phác đồ.
* **Đầu ra (Deliverable):** Giao diện Web tương tác trọn vẹn tại `http://localhost:3000`.
* **Trạng thái:** `[x] DONE` *(Route `POST /api/v1/agent/explain` thực thi `DiagnosticStateGraph` và kết nối thông suốt với Frontend).*
