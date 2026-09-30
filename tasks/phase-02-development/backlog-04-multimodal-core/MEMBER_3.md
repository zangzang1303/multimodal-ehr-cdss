# BACKLOG 02 - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Mock Endpoint, DiagnosticCard Component, Unit Tests Mạng Học Sâu & Dashboard Ablation

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Xây Dựng Mock Endpoint & DiagnosticCard Component
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Viết mock endpoint `POST /api/v1/predict/mock` trên FastAPI để Frontend phát triển giao diện hiển thị kết quả chẩn đoán sớm.
  2. Xây dựng `frontend/src/components/DiagnosticCard.tsx`:
     - Hiển thị danh sách Top-K bệnh lý có xác suất cao nhất.
     - Thanh đo rủi ro tương ứng (Progress bar) với 3 dải màu: Xanh lá ($<30\%$), Vàng cam ($30\% - 70\%$), Đỏ ($>70\%$).
     - Hiển thị nhãn *"Calibrated Confidence"* kèm tooltip giải thích xác suất đã hiệu chuẩn.
* **Đầu ra (Deliverable):** `DiagnosticCard.tsx`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Viết Bộ Unit Tests Cho Mạng Đa Phương Thức
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết `tests/test_multimodal_model.py`:
     - Kiểm tra `TabularTokenizer`: Nhận ma trận số và xuất đúng kích thước `[Batch, M+1, 128]`.
     - Kiểm tra `ClinicalTextEncoder`: Nhận input_ids và attention_mask, xuất đúng kích thước `[Batch, S+2, 128]`.
     - Kiểm tra `CrossAttentionFusion`: Forward pass, backward pass, gradients không bị lỗi NaN.
     - Kiểm tra `TemperatureScalingCalibrator`: Tỷ lệ xác suất sau hiệu chuẩn có tổng bằng 1.0.
  2. Chạy lệnh: `pytest tests/test_multimodal_model.py -v` (bảo đảm pass 100%).
* **Đầu ra (Deliverable):** `tests/test_multimodal_model.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Xây Dựng Trang Báo Cáo Ablation Study Trên Web
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** Tạo trang `frontend/src/app/evaluation/page.tsx` hiển thị bảng so sánh trực quan các chỉ số (AUROC, F1, ECE) giữa Tabular-only, Text-only, Concat và Cross-Attention.
* **Đầu ra (Deliverable):** `frontend/src/app/evaluation/page.tsx`.
* **Trạng thái:** `[ ] TODO`
