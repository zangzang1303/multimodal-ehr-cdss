# BACKLOG 07 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
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
  3. Cung cấp `.env.example`, nguồn checkpoint/snapshot được phép, bước restore nếu cần và kiểm thử khởi chạy trên môi trường sạch có Docker:
     ```bash
     docker compose up --build -d
     docker compose ps
     ```
  4. Xác nhận cả 3 dịch vụ healthy, gọi được API/UI và xử lý rõ trường hợp thiếu weights, Qdrant chưa sẵn sàng hoặc không có GPU.
* **Đầu ra (Deliverable):** `docker-compose.yml`, các `Dockerfile` hoàn chỉnh.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Soạn Thảo Phần Software Architecture & Sơ Đồ Vector
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Soạn thảo phần *Software Architecture & Multi-Agent Implementation* của bài báo khoa học: Mô tả chi tiết giao thức RESTful, luồng hội chẩn đa tác tử và cơ chế highlight Evidence Grounding.
  2. Xuất các sơ đồ kiến trúc hệ thống dạng vector độ nét cao (SVG / PDF) phục vụ in ấn xuất bản.
* **Đầu ra (Deliverable):** Bản thảo phần Software Architecture và các hình vẽ chất lượng cao.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Sản Xuất Video Kịch Bản Demo Lâm Sàng & Slide Báo Cáo
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Xây dựng kịch bản video demo lâm sàng (thời lượng 3 - 5 phút):
     - Mở đầu: Trình bày khoảng trống nghiên cứu có trích dẫn và phạm vi dữ liệu tổng hợp/kho công khai của dự án; kiểm tra lại mọi tỷ lệ nêu trong slide/video theo nguồn gốc.
     - Thao tác: Nhập ca bệnh lâm sàng khó vào `PatientDataForm.tsx`.
     - Kết quả: Hiển thị xác suất đã hiệu chuẩn và ECE thực đo trên strict test; không nói đạt $ECE < 0.05$ nếu kết quả chưa đạt.
     - Giải trình: Xem các câu chứng cứ được highlight trong bệnh án trên `EvidenceViewer.tsx` và tra cứu phác đồ trong `GuidelineDrawer.tsx`.
     - Phân tích: Trực quan hóa DCA với bệnh đích/hành động giả định, nêu rõ dữ liệu tổng hợp và giới hạn áp dụng.
  2. Biên tập video chất lượng Full HD kèm giọng thuyết minh và phụ đề.
  3. Chuẩn bị bộ slide thuyết trình nghiệm thu dự án.
* **Đầu ra (Deliverable):** Video Demo sản phẩm Full HD, Slide nghiệm thu dự án.
* **Trạng thái:** `[ ] TODO`
