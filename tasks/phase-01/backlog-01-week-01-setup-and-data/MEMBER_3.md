# BACKLOG 01 (TUẦN 1) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & SYSTEM)
### Trọng Tâm: Khung Ứng Dụng FastAPI, Khung Next.js 14, Pydantic Contract & Quy Chuẩn Code

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 1 của Giai đoạn 1, Thành viên 3 đóng vai trò kiến trúc sư phần mềm, thiết lập toàn bộ khung mã nguồn ứng dụng bao gồm Backend FastAPI hiệu năng cao, Frontend Next.js 14 hiện đại, xây dựng các lớp Pydantic Schemas làm hợp đồng truyền tải API và thiết lập quy chuẩn kiểm thử/chất lượng mã nguồn cho toàn nhóm.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Khởi Tạo Khung Dự Án Backend FastAPI
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Xây dựng điểm vào của ứng dụng backend tại `src/api/main.py`:
     - Cấu hình CORS middleware cho phép kết nối an toàn từ `http://localhost:3000` (Next.js frontend).
     - Định nghĩa endpoint kiểm tra sức khỏe hệ thống `GET /health`:
       ```python
       @app.get("/health", tags=["System"])
       async def health_check():
           return {
               "status": "healthy",
               "version": "1.0.0-phase1",
               "timestamp": datetime.utcnow().isoformat()
           }
       ```
     - Cấu hình cấu trúc routes module hóa: `src/api/routes/`.
  2. Viết file `Dockerfile` cho backend nhằm hỗ trợ chạy môi trường container hóa chuẩn.
* **Lệnh thực thi & kiểm thử:**
  ```bash
  uvicorn src.api.main:app --reload --port 8000
  curl http://localhost:8000/health
  ```
* **Đầu ra (Deliverables):**
  - `src/api/main.py`.
  - `Dockerfile` (Backend).
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Khởi Tạo Khung Giao Diện Next.js 14
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Khởi tạo ứng dụng web hiện đại trong thư mục `frontend/` sử dụng Next.js 14 (App Router), TypeScript, TailwindCSS và Lucide React:
     - Tạo layout chính `frontend/src/app/layout.tsx` với typography chuẩn Inter/Outfit, hỗ trợ giao diện y tế chuyên nghiệp (Dark/Light mode, dải màu y tế xanh ngọc `emerald`/xanh dương `sky`).
     - Tạo trang chủ ban đầu `frontend/src/app/page.tsx` hiển thị tiêu đề hệ thống *"Multimodal Clinical Decision Support System - Phase 1: Baselines & Research Benchmark"*.
  2. Cấu hình file `frontend/src/lib/api.ts` chứa client gọi HTTP tới FastAPI backend (`http://localhost:8000`).
* **Lệnh thực thi & kiểm thử:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
  Truy cập trình duyệt tại `http://localhost:3000`.
* **Đầu ra (Deliverables):**
  - Khung mã nguồn thư mục `frontend/` hoàn chỉnh.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Xây Dựng Pydantic Schemas Cốt Lõi (`src/api/schemas.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Dựa trên `configs/data_schema.yaml` do Thành viên 2 thiết kế, triển khai các lớp Pydantic v2 trong `src/api/schemas.py`:
  1. `TabularFeatures`: Xác thực 9 chỉ số liên tục và 4 biến phân loại với ràng buộc giá trị min, max hợp lý.
  2. `ClinicalNoteInput`: Xác thực văn bản bệnh án lâm sàng (`patient_id`, `encounter_timestamp`, `raw_text`).
  3. `BaselinePredictionResult`: Cấu trúc trả về dự đoán gồm tên bệnh, xác suất (0.0 đến 1.0) và tên baseline thực hiện dự đoán.
* **Đầu ra (Deliverables):**
  - `src/api/schemas.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.4: Thiết Lập Quy Chuẩn Định Dạng Code & Kiểm Thử
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Cấu hình linter và formatter: `.flake8`, `pyproject.toml` (cấu hình `black` độ dài dòng 100 ký tự).
  2. Thiết lập thư mục `tests/` với `pytest.ini` và viết test kiểm tra endpoint health trong `tests/test_api_endpoints.py`:
     ```python
     def test_health_check(client):
         response = client.get("/health")
         assert response.status_code == 200
         assert response.json()["status"] == "healthy"
     ```
* **Lệnh thực thi & kiểm thử:**
  ```bash
  pytest tests/test_api_endpoints.py -v
  ```
* **Đầu ra (Deliverables):**
  - `.flake8`, `pyproject.toml`, `pytest.ini`.
  - `tests/test_api_endpoints.py`.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 3 (ACCEPTANCE CRITERIA)
- [ ] Backend FastAPI khởi động mượt mà tại cổng 8000, endpoint `/health` trả về HTTP 200.
- [ ] Frontend Next.js khởi động mượt mà tại cổng 3000, không có cảnh báo hay lỗi biên dịch TypeScript.
- [ ] Lệnh `pytest tests/test_api_endpoints.py` vượt qua 100% test cases.
- [ ] Pydantic Schemas trong `src/api/schemas.py` xác thực đúng các trường dữ liệu theo `configs/data_schema.yaml`.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 3
1. **FastAPI & Pydantic v2 Architecture:**
   * *FastAPI Official Documentation:* [fastapi.tiangolo.com](https://fastapi.tiangolo.com/).
   * *Trọng tâm cần đọc:* Hướng dẫn CORS Middleware, Pydantic v2 `BaseModel`, `Field` validation constraints và Lifespan context manager (`@asynccontextmanager`).
2. **Next.js 14 App Router & Medical UI Design:**
   * *Next.js 14 Official Documentation:* [nextjs.org/docs/app](https://nextjs.org/docs/app).
   * *TailwindCSS Clinical UI Styling:* Áp dụng bảng màu y tế chuẩn (`emerald-600` cho dải bình thường, `amber-500` cho ranh giới cảnh báo, `rose-600` cho bất thường nghiêm trọng).
3. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 1, Mục 2.12 và Mục 2.13).

