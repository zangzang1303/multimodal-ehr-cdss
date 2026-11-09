# BACKLOG 07 (PACKAGING & PAPER) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Docker Compose Trọn Gói, Soạn Thảo Software Architecture Bài Báo & Video Kịch Bản Demo

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hoàn Thiện Docker Compose Trọn Gói Một Lệnh
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết `Dockerfile` đa tầng (Multi-stage build) cho Frontend Next.js để tối ưu dung lượng image.
  2. Viết file `docker-compose.yml` kết nối 3 dịch vụ:
     - `frontend`: cổng 3000
     - `api`: cổng 8000 (Backend FastAPI)
     - `qdrant`: cổng 6333 (Vector DB)
  3. Kiểm thử khởi chạy trên môi trường sạch:
     ```bash
     docker compose up --build -d
     docker compose ps
     ```
  4. Xác nhận cả 3 dịch vụ đều healthy và giao tiếp với nhau trơn tru qua mạng nội bộ Docker.
* **Đầu ra (Deliverable):** `docker-compose.yml`, `frontend/Dockerfile`, `.dockerignore`, `frontend/.dockerignore`, `.env.example`.
* **Trạng thái:** `[x] DONE` (Đã hoàn thiện Multi-stage `frontend/Dockerfile` với `output: "standalone"`, `docker-compose.yml` kết nối 3 dịch vụ `qdrant:6333`, `api:8000`, `frontend:3000` qua mạng `mcdss-internal-net` kèm healthchecks và xác thực cấu hình `docker compose config` hợp lệ 100%).

---

### 🔹 Nhiệm vụ 3.2: Soạn Thảo Phần Software Architecture & Sơ Đồ Vector
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Soạn thảo phần *Software Architecture & Multi-Agent Implementation* của bài báo khoa học: Mô tả chi tiết giao thức RESTful, luồng hội chẩn đa tác tử và cơ chế highlight Evidence Grounding.
  2. Xuất các sơ đồ kiến trúc hệ thống dạng vector độ nét cao (SVG / PDF / TikZ) phục vụ in ấn xuất bản.
* **Đầu ra (Deliverable):** Bộ bản thảo LaTeX đa phân mục tại `docs/paper_latex/` kèm template học thuật `templates/mcdss_article.sty`, các sơ đồ TikZ (`figures/*.tex`) và sơ đồ vector SVG độc lập (`figures/svg/*.svg`).
* **Trạng thái:** `[x] DONE` (Đã xây dựng hoàn chỉnh cấu trúc LaTeX đa file tại `docs/paper_latex/` gồm `main.tex`, `templates/mcdss_article.sty`, 9 phân mục `sections/00..08.tex`, 3 sơ đồ vector TikZ và bản xuất SVG độ nét cao).

---

### 🔹 Nhiệm vụ 3.3: Sản Xuất Video Kịch Bản Demo Lâm Sàng & Slide Báo Cáo
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Xây dựng kịch bản video demo lâm sàng (thời lượng 3 - 5 phút):
     - Mở đầu: Trình bày khoảng trống y văn từ JMIR Systematic Review (100% dữ liệu bảng, nguy cơ sai lệch cao).
     - Thao tác: Nhập ca bệnh lâm sàng khó vào `PatientDataForm.tsx`.
     - Kết quả: Hiển thị thanh đo xác suất đã hiệu chuẩn ($ECE < 0.05$) trên `DiagnosticCard.tsx`.
     - Giải trình: Xem các câu chứng cứ được highlight trong bệnh án trên `EvidenceViewer.tsx` và tra cứu phác đồ trong `GuidelineDrawer.tsx`.
     - Phân tích: Trực quan hóa đồ thị Lợi ích ròng DCA trên trang `/evaluation`.
  2. Biên tập kịch bản thuyết minh, phụ đề và bộ slide báo cáo nghiệm thu dự án (kèm các slide cơ sở lý thuyết nền tảng ở đầu như Giai đoạn 1).
* **Đầu ra (Deliverable):**
  - `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md`
  - `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md`
* **Trạng thái:** `[x] DONE` (Đã hoàn thành kịch bản Video Demo 5 phân cảnh 4 phút 30 giây và bộ nội dung 20 Slide tự đọc kèm kịch bản lời thuyết trình nghiệm thu Giai đoạn 2).
