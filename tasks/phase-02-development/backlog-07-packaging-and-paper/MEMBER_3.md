# BACKLOG 07 (PACKAGING & PAPER) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Docker Compose Trọn Gói, Soạn Thảo Software Architecture Bài Báo & Video Kịch Bản Demo

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hoàn Thiện Docker Compose Trọn Gói Một Lệnh
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Viết `Dockerfile` đa tầng (Multi-stage build) cho Frontend Next.js để tối ưu dung lượng image (`frontend/Dockerfile`, `output: "standalone"`).
  2. `[x]` Viết file `docker-compose.yml` kết nối 3 dịch vụ: `frontend:3000`, `api:8000`, `qdrant:6333`.
  3. `[x]` Cung cấp `.env.example`, cấu hình xử lý thiếu weights/Qdrant và kiểm thử khởi chạy thực tế (`docker compose build` & `docker compose up -d`).
  4. `[x]` Xác nhận cả 3 dịch vụ (`mcdss-qdrant`, `mcdss-api`, `mcdss-frontend`) đạt trạng thái `(healthy)` và giao tiếp qua mạng nội bộ Docker (`mcdss-internal-net`).
* **Đầu ra (Deliverable):** `docker-compose.yml`, `Dockerfile`, `requirements-deploy.txt`, `frontend/Dockerfile`, `.dockerignore`, `frontend/.dockerignore`, `.env.example`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.2: Soạn Thảo Phần Software Architecture & Sơ Đồ Vector
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Soạn thảo phần *Software Architecture & Multi-Agent Implementation* (`docs/paper_latex/sections/04_software_architecture.tex`, `05_multi_agent_rag.tex`, `06_frontend_dca_ux.tex`) đồng bộ với mã nguồn thực thi (`HybridGuidelineRetriever`, `EvidenceGrounder`, RESTful API).
  2. `[x]` Xuất các sơ đồ kiến trúc hệ thống dạng vector độ nét cao (`figures/*.tex` TikZ và `figures/svg/*.svg`).
  3. `[ ]` Hoàn thiện các bảng số liệu thực nghiệm Giai đoạn 2 trong các phân mục phối hợp (`00_abstract.tex`, `02_clinical_cohort.tex`, `03_methodology_fusion.tex`, `07_empirical_results.tex`, `08_discussion_ethics.tex`) — *Chưa hoàn thành: còn các ô `[TODO-TV1]` / `[TODO-TV2]` chờ Thành viên 1 & Thành viên 2 chốt bộ kết quả đa seed và `results/registry.json` ở Phase 3.*
* **Đầu ra (Deliverable):** Bộ bản thảo LaTeX đa phân mục tại `docs/paper_latex/` kèm template `templates/mcdss_article.sty` và các sơ đồ vector.
* **Trạng thái:** `[ ] TODO` *(Đã hoàn thành 100% các phân mục kiến trúc phần mềm & sơ đồ vector thuộc phạm vi Thành viên 3; giữ `[ ] TODO` do bản thảo toàn bài vẫn còn các ô `[TODO-TV1]` / `[TODO-TV2]` phụ thuộc vào Thành viên 1 & 2 ở Phase 3).*

*(Xem danh sách chi tiết 7 nhóm `[TODO-TV1/TV2]` trong các file `docs/paper_latex/sections/*.tex` cần điền khi Thành viên 1 & 2 hoàn tất Phase 3).*

---

### 🔹 Nhiệm vụ 3.3: Sản Xuất Video Kịch Bản Demo Lâm Sàng & Slide Báo Cáo
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Xây dựng kịch bản video demo lâm sàng (3–5 phút) và kịch bản bộ slide 20 trang kèm cảnh báo dữ liệu tổng hợp & placeholder `[TODO-TV1/TV2]`:
     - `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md`
     - `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md`
  2. `[ ]` Quay và biên tập video chất lượng Full HD kèm giọng thuyết minh và phụ đề hoàn chỉnh *(Chưa hoàn thành: chờ hoàn tất giao diện & số liệu chốt cuối Phase 3 để quay bản cuối)*.
  3. `[ ]` Thiết kế và xuất bản file slide thuyết trình nghiệm thu dự án cuối cùng (PDF / PPTX) *(Chưa hoàn thành: chờ điền số liệu từ `results/registry.json` sau Phase 3)*.
* **Đầu ra (Deliverable):** Video Demo sản phẩm Full HD, Slide nghiệm thu dự án.
* **Trạng thái:** `[ ] TODO` *(Đã hoàn thành kịch bản chi tiết; chưa hoàn thành quay video Full HD và xuất file slide cuối cùng do chờ hoàn thiện Phase 3).*
