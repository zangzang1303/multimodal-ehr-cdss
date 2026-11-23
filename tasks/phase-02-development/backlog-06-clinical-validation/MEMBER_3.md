# BACKLOG 06 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Benchmark REST Route, Unit Tests Toàn Bộ Endpoints, UI Đồ Thị DCA & Tối Ưu UX

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Viết REST Endpoint Benchmark & Bộ API Tests
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Viết route `GET /api/v1/evaluation/benchmark` trong `src/api/routes/evaluation_routes.py` trả về bảng chỉ số tổng hợp JSON (AUROC, AUPRC, F1, ECE, DCA Net Benefit) đọc từ các tệp thực nghiệm (`data/ablation_results.json`) và `evaluate_holdout_dca()`.
  2. `[x]` Mở rộng `tests/test_api_endpoints.py`:
     - Test route `/predict/multimodal`: Gửi payload bảng + text hợp lệ (kèm kiểm tra checkpoint contract & 503 khi thiếu weights), tổng xác suất = 1.0.
     - Test route `/agent/explain`: Gửi ca bệnh và ghi chú không hợp lệ (trả 400/422 thay vì 200), kiểm tra spans có `start`/`end` khớp `display_note`.
     - Test route `/evaluation/benchmark`: Kiểm tra mã 200, schema JSON, trạng thái `dca_status` và xử lý mượt khi thiếu artifact `.npz` từng mẫu.
  3. `[x]` Chạy lệnh `pytest tests/test_api_endpoints.py -v`: **19/19 tests passed 100%**.
* **Đầu ra (Deliverable):** `src/api/routes/evaluation_routes.py`, `tests/test_api_endpoints.py`.
* **Trạng thái:** `[x] DONE` *(Lưu ý: Chế độ DCA trong `evaluation_routes.py` tự động dùng mô phỏng minh họa `illustrative_simulation_pending_patient_level_predictions` cho tới khi Thành viên 1 & 2 xuất tệp dự đoán từng mẫu `.npz` ở Phase 3).*

---

### 🔹 Nhiệm vụ 3.2: Tích Hợp Đồ Thị DCA Tương Tác Trên Giao Diện Bác Sĩ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Xây dựng component trực quan hóa đường cong DCA trên Frontend (`frontend/src/components/DCACurveChart.tsx`):
  - `[x]` Vẽ đường cong Net Benefit của M-CDSS đối chiếu với "Treat All", "Treat None" và Baseline bằng Recharts nhận dữ liệu trực tiếp từ API `/api/v1/evaluation/benchmark`.
  - `[x]` Hiển thị rõ bệnh đích One-vs-Rest (`HEART_FAILURE / Macro 4 lớp`), hành động giả định (`Siêu âm tim Doppler & NT-proBNP`), tỷ lệ hiện mắc (`35.1% HF / Macro 25.0%`), dải ngưỡng hợp lệ `pt ∈ [10%, 45%]`, cảnh báo nghiên cứu minh họa và giới hạn thanh trượt chỉ kéo trong dải định trước `[0.10, 0.45]`.
* **Đầu ra (Deliverable):** `frontend/src/components/DCACurveChart.tsx`, `frontend/src/app/evaluation/page.tsx`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.3: Tối Ưu Hóa Giao Diện Cho Tablet / Mobile Lâm Sàng
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** `[x]` Tinh chỉnh CSS Responsive cho bàn khám (`PatientDataForm.tsx`, `DiagnosticCard.tsx`, `evaluation/page.tsx`) và micro-animations (`next lint` & `next build` pass 0 lỗi).
* **Đầu ra (Deliverable):** Giao diện Web tối ưu hóa đa thiết bị.
* **Trạng thái:** `[x] DONE`
