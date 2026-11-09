# BACKLOG 06 (VALIDATION) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Benchmark REST Route, Unit Tests Toàn Bộ Endpoints, UI Đồ Thị DCA & Tối Ưu UX

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Viết REST Endpoint Benchmark & Bộ API Tests
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết module `src/evaluation/dca_analysis.py` và route `GET /api/v1/evaluation/benchmark` trong `src/api/routes/evaluation_routes.py` tính toán động đường cong DCA (Vickers & Elkin, 2006) trên tập kiểm thử độc lập ($N=302$) và đọc bảng chỉ số tổng hợp từ các tệp kết quả thực nghiệm (`data/ablation_results.json`, `data/rebuilt_strict_results_2026-10-28.json`).
  2. Viết bộ kiểm thử tự động `tests/test_api_endpoints.py`:
     - Test route `/predict/mock`: Gửi payload bảng + text hợp lệ, kiểm tra mã 200, kiểm tra danh sách predictions có tổng xác suất = 1.0.
     - Test route `/agent/explain`: Gửi id ca bệnh hoặc payload, kiểm tra mã 200 và mảng evidence spans có vị trí `start` và `end`.
     - Test route `/evaluation/benchmark`: Kiểm tra mã 200, schema JSON và tính nhất quán toán học của các chỉ số DCA.
  3. Chạy lệnh: `pytest tests/test_api_endpoints.py -v` (bảo đảm pass 100%).
* **Đầu ra (Deliverable):** `src/evaluation/dca_analysis.py`, `src/api/routes/evaluation_routes.py`, `tests/test_api_endpoints.py`.
* **Trạng thái:** `[x] DONE` *(Lưu ý kỹ thuật: Module `dca_analysis.py` tính toán động Net Benefit, $\Delta\text{TP}_{\text{net}/100}$ và $\Delta\text{FP}_{\text{avoided}/100}$ trên phân bố nhãn tập kiểm thử $N=302$; khi tích hợp tệp dự đoán xác suất từng mẫu của Thành viên 1 từ checkpoint cuối, hàm `compute_dca_curve_from_predictions()` sẽ nhận trực tiếp ma trận xác suất đó).*

---

### 🔹 Nhiệm vụ 3.2: Tích Hợp Đồ Thị DCA Tương Tác Trên Giao Diện Bác Sĩ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Xây dựng component trực quan hóa đường cong DCA trên Frontend (`frontend/src/components/DCACurveChart.tsx`) và truyền dữ liệu trực tiếp từ API `getClinicalEvaluationBenchmark()` tại `frontend/src/app/evaluation/page.tsx`:
  - Vẽ đường cong Net Benefit của M-CDSS đối chiếu với "Treat All", "Treat None" và Baseline.
  - Cho phép người dùng kéo thanh trượt điều chỉnh ngưỡng can thiệp $p_t \in [0.05, 0.60]$ để quan sát số ca can thiệp đúng ròng tăng thêm ($\Delta\text{TP}_{\text{net}/100}$) và số ca can thiệp thừa tránh được ($\Delta\text{FP}_{\text{avoided}/100}$) khớp hoàn toàn với công thức trong bài báo.
* **Đầu ra (Deliverable):** Component `DCACurveChart.tsx` kết nối dữ liệu API trên `evaluation/page.tsx`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 3.3: Tối Ưu Hóa Giao Diện Cho Tablet / Mobile Lâm Sàng
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** Tinh chỉnh CSS Responsive: bảo đảm form nhập liệu và màn hình hội chẩn hiển thị mượt mà trên máy tính bảng (iPad / Galaxy Tab) của bác sĩ tại bàn khám bệnh; bổ sung micro-animations cho các thanh đo rủi ro.
* **Đầu ra (Deliverable):** Giao diện Web tối ưu hóa đa thiết bị.
* **Trạng thái:** `[x] DONE`
