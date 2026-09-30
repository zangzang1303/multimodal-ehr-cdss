# BACKLOG 02 (TUẦN 2) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & SYSTEM)
### Trọng Tâm: Bộ Unit Tests Toàn Diện Data Pipeline, Giao Diện Form Bác Sĩ & Mock API Baseline

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 2 của Giai đoạn 1, Thành viên 3 đóng vai trò bảo chứng chất lượng hệ thống thông qua việc xây dựng bộ Unit Tests tự động nghiêm ngặt kiểm tra toàn bộ pipeline dữ liệu do Thành viên 2 viết. Đồng thời, xây dựng giao diện tương tác ban đầu `PatientDataForm.tsx` trên Next.js và mock API endpoint trên FastAPI để sẵn sàng kết nối dữ liệu.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Viết Bộ Unit Tests Cho Data Pipeline (`tests/test_data_pipeline.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Xây dựng tệp `tests/test_data_pipeline.py` sử dụng `pytest` với các test cases bắt buộc:
  1. **Test Khử định danh (`test_deidentifier`):**
     - Đưa vào văn bản chứa: Số CCCD 12 số, SĐT Việt Nam (+84912345678), email, tên người ("Bác sĩ Nguyễn Văn A khám cho bệnh nhân Trần Thị B tại Bệnh viện Bạch Mai ngày 12/03/2026").
     - Xác nhận (Assert): 100% các từ nhạy cảm trên biến mất và được thế bằng các token `[REDACTED_NAME]`, `[REDACTED_DATE]`, `[REDACTED_HOSPITAL]`, `[REDACTED_PHONE]`.
  2. **Test Khóa thời gian & Blacklist (`test_temporal_aligner`):**
     - Đưa vào bản ghi có sự kiện diễn ra lúc 10:00 và mốc chẩn đoán xác nhận là 09:30 $\rightarrow$ Assert sự kiện lúc 10:00 bị loại bỏ.
     - Đưa vào dataframe có chứa cột `fev1` hoặc `lvef` $\rightarrow$ Assert các cột này bị loại trừ hoặc bị phát hiện trong Blacklist.
  3. **Test Gán dữ liệu khuyết MICE (`test_imputer`):**
     - Đưa vào dataframe có 20% giá trị NaN ngẫu nhiên trên các cột sinh hiệu.
     - Sau khi qua `imputer.fit_transform()`: Assert `df.isna().sum().sum() == 0`, và các cột `_is_missing` tồn tại và chứa đúng giá trị nhị phân 0 và 1.
* **Lệnh thực thi & kiểm thử:**
  ```bash
  pytest tests/test_data_pipeline.py -v
  ```
* **Đầu ra (Deliverables):**
  - `tests/test_data_pipeline.py` (vượt qua 100% test cases).
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng Component Giao Diện Bác Sĩ (`PatientDataForm.tsx`)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  Xây dựng component `frontend/src/components/PatientDataForm.tsx` trên Next.js 14:
  1. **Bố cục 2 cột trực quan (Side-by-side Layout):**
     - **Cột Trái (Dữ liệu Bảng Số):**
       - 9 ô input nhập các chỉ số: Tuổi, Huyết áp tâm thu/tâm trương, Nhịp tim, Nhịp thở, $SpO_2$, Nhiệt độ, Bạch cầu (WBC), CRP.
       - Hiển thị badge dải sinh lý bình thường (ví dụ: `Normal: 90 - 130 mmHg`). Nếu người dùng nhập ngoài dải bình thường, tự động đổi màu viền sang cam/đỏ để cảnh báo sớm.
       - Các dropdown chọn: Giới tính, Tình trạng hút thuốc, Tiền sử tăng huyết áp, Đái tháo đường.
     - **Cột Phải (Ghi Chú Bệnh Án Tự Do):**
       - Textarea rộng rãi để bác sĩ dán hoặc gõ nội dung bệnh sử, tiền căn, kết quả khám thực thể.
       - Nút bấm tải dữ liệu mẫu (*"Load Sample Patient"*): Cho phép nạp nhanh dữ liệu giả lập của 1 ca bệnh mẫu để tiện demo và kiểm thử.
  2. **Nút Thao Tác Chính:**
     - Nút *"Chạy Dự Đoán 3 Baselines"* gửi request tới Backend.
* **Đầu ra (Deliverables):**
  - `frontend/src/components/PatientDataForm.tsx`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Mock API Endpoint Dự Đoán Baselines
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Tạo route tại `src/api/routes/inference.py`:
     - Endpoint: `POST /api/v1/predict/baseline`
     - Nhận body JSON theo schema `PatientInferenceRequest`.
     - Trả về cấu trúc JSON giả lập gồm xác suất của 3 baseline (để frontend có thể render thử nghiệm trước khi Thành viên 1 huấn luyện xong ở Tuần 3):
       ```json
       {
         "patient_id": "PT-001",
         "baseline_results": {
           "classical_tabular": {"predicted_class": "COPD", "confidence": 0.72},
           "tabular_deep": {"predicted_class": "COPD", "confidence": 0.68},
           "text_only": {"predicted_class": "ASTHMA", "confidence": 0.65}
         }
       }
       ```
  2. Kết nối component `PatientDataForm.tsx` với endpoint này qua hàm fetch trong `src/lib/api.ts`.
* **Đầu ra (Deliverables):**
  - `src/api/routes/inference.py`.
  - Cập nhật `src/api/main.py` để mount route.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 3 (ACCEPTANCE CRITERIA)
- [ ] Chạy lệnh `pytest tests/test_data_pipeline.py -v` đạt 100% Pass không có bất kỳ Warning/Error nào.
- [ ] Giao diện form trên Next.js hiển thị đẹp mắt, nhập liệu mượt mà, bấm *"Load Sample Patient"* tự động điền đầy đủ số và text.
- [ ] Bấm nút *"Chạy Dự Đoán 3 Baselines"* trên web gọi thành công API tới backend và nhận về phản hồi HTTP 200.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 3
1. **Kiểm Thử Phần Mềm Y Tế Với Pytest:**
   * *Pytest Official Documentation:* [docs.pytest.org](https://docs.pytest.org/en/stable/).
   * *Trọng tâm cần đọc:* Cách viết test assertions kiểm tra không có thông tin định danh (PII regex match) và kiểm tra cấm tuyệt đối rò rỉ dữ liệu tương lai.
2. **Thiết Kế Giao Diện Nhập Liệu Y Tế (Clinical Data Input UI):**
   * *TailwindCSS Forms & Controlled Components:* Thiết kế form 2 cột responsive, hỗ trợ đổi màu viền ô nhập tự động khi chỉ số vượt ra ngoài khoảng bình thường (`normal_range`).
   * *Lucide React Icons:* Sử dụng bộ icon y tế (`Activity`, `HeartPulse`, `Stethoscope`, `FileText`, `AlertTriangle`).
3. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 1, Mục 2.14, Mục 2.16 và Mục 4).

