# BACKLOG 04 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Benchmark REST Route, Unit Tests Toàn Bộ Endpoints, UI Đồ Thị DCA & Tối Ưu UX

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Viết REST Endpoint Benchmark & Bộ API Tests
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết route `GET /api/v1/evaluation/benchmark` trong `src/api/routes/evaluation_routes.py` trả về bảng chỉ số tổng hợp JSON (AUROC, AUPRC, F1, ECE, DCA Net Benefit giữa 3 Baselines và Ours).
  2. Viết bộ kiểm thử tự động `tests/test_api_endpoints.py`:
     - Test route `/predict/multimodal`: Gửi payload bảng + text hợp lệ, kiểm tra mã 200, kiểm tra danh sách predictions có tổng xác suất = 1.0.
     - Test route `/agent/explain`: Gửi id ca bệnh, kiểm tra mã 200 và mảng evidence spans có vị trí `start` và `end`.
     - Test route `/evaluation/benchmark`: Kiểm tra mã 200 và schema JSON.
  3. Chạy lệnh: `pytest tests/test_api_endpoints.py -v` (bảo đảm pass 100%).
* **Đầu ra (Deliverable):** `src/api/routes/evaluation_routes.py`, `tests/test_api_endpoints.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Tích Hợp Đồ Thị DCA Tương Tác Trên Giao Diện Bác Sĩ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Xây dựng component trực quan hóa đường cong DCA trên Frontend (`recharts` hoặc `chart.js`):
  - Vẽ đường cong Net Benefit của M-CDSS đối chiếu với "Treat All" và "Treat None".
  - Cho phép người dùng kéo thanh trượt điều chỉnh ngưỡng can thiệp $p_t$ để quan sát số ca can thiệp đúng ròng tăng thêm tương ứng.
* **Đầu ra (Deliverable):** Component biểu đồ DCA tương tác trên Frontend.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Tối Ưu Hóa Giao Diện Cho Tablet / Mobile Lâm Sàng
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** Tinh chỉnh CSS Responsive: bảo đảm form nhập liệu và màn hình hội chẩn hiển thị mượt mà trên máy tính bảng (iPad / Galaxy Tab) của bác sĩ tại bàn khám bệnh; bổ sung micro-animations cho các thanh đo rủi ro.
* **Đầu ra (Deliverable):** Giao diện Web tối ưu hóa đa thiết bị.
* **Trạng thái:** `[ ] TODO`
