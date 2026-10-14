# BACKLOG 01 (TUẦN 1) - NHIỆM VỤ THÀNH VIÊN 2 (BIOMEDICAL DATA & PRIVACY)
### Trọng Tâm: Hợp Đồng Dữ Liệu Lâm Sàng, Sinh/Thu Thập Dữ Liệu Bệnh Án Thô & Quản Trị Bảo Mật

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 1 của Giai đoạn 1, Thành viên 2 giữ vai trò thiết kế Hợp đồng Dữ liệu cốt lõi (`configs/data_schema.yaml`) làm nền móng cho toàn bộ pipeline của cả nhóm. Đồng thời, chịu trách nhiệm thu thập hoặc xây dựng kịch bản sinh dữ liệu lâm sàng bán tổng hợp (Semi-synthetic EHR) chất lượng cao bao gồm cả chỉ số sinh hiệu/xét nghiệm số học và ghi chú lâm sàng tự do cho ít nhất 2.000 bệnh nhân.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Xây Dựng Hợp Đồng Dữ Liệu Chuẩn (`configs/data_schema.yaml`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Xây dựng tệp `configs/data_schema.yaml` định nghĩa chặt chẽ kiểu dữ liệu, miền giá trị sinh lý bình thường (Normal Range) và đơn vị đo theo đúng tiêu chuẩn y khoa:
  1. **9 Biến số liên tục (Numerical Features):**
     - `age`: `int`, min: 18, max: 110, đơn vị: tuổi.
     - `systolic_bp`: `float`, dải bình thường: [90.0, 130.0], min: 60.0, max: 240.0, đơn vị: mmHg.
     - `diastolic_bp`: `float`, dải bình thường: [60.0, 85.0], min: 40.0, max: 140.0, đơn vị: mmHg.
     - `heart_rate`: `float`, dải bình thường: [60.0, 100.0], min: 30.0, max: 220.0, đơn vị: bpm.
     - `respiratory_rate`: `float`, dải bình thường: [12.0, 20.0], min: 8.0, max: 50.0, đơn vị: breaths/min.
     - `spo2`: `float`, dải bình thường: [95.0, 100.0], min: 60.0, max: 100.0, đơn vị: %.
     - `temperature`: `float`, dải bình thường: [36.5, 37.5], min: 35.0, max: 42.0, đơn vị: độ C.
     - `wbc_count`: `float` (Bạch cầu), dải bình thường: [4.0, 10.0], min: 1.0, max: 50.0, đơn vị: $10^9$/L.
     - `crp`: `float` (Protein phản ứng C), dải bình thường: [0.0, 5.0], min: 0.0, max: 300.0, đơn vị: mg/L.
  2. **4 Biến phân loại (Categorical Features):**
     - `gender`: `["M", "F", "OTHER"]`.
     - `smoking_status`: `["NEVER", "FORMER", "CURRENT"]`.
     - `history_hypertension`: `[0, 1]`.
     - `history_diabetes`: `[0, 1]`.
  3. **4 Nhãn chẩn đoán mục tiêu (Multiclass Targets):**
     - `0`: `ASTHMA` (Hen phế quản).
     - `1`: `COPD` (Bệnh phổi tắc nghẽn mạn tính).
     - `2`: `CONGESTIVE_HEART_FAILURE` (Suy tim sung huyết).
     - `3`: `COMMUNITY_ACQUIRED_PNEUMONIA` (Viêm phổi mắc phải cộng đồng).
* **Đầu ra (Deliverables):**
  - Tệp `configs/data_schema.yaml` hoàn chỉnh.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 2.2: Thu Thập Hoặc Sinh Tập Dữ Liệu Lâm Sàng Thô (Synthetic EHR Generator)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Viết kịch bản `scripts/generate_synthetic_ehr.py` để sinh tập dữ liệu bán tổng hợp (hoặc trích xuất từ MIMIC-IV-Note subset) cho ít nhất $N = 2.000$ bệnh nhân độc lập với các đặc trưng lâm sàng sát thực tế:
     - Tạo mối tương quan thực tế giữa nhãn bệnh và các chỉ số sinh hiệu/xét nghiệm (ví dụ: Viêm phổi thường có WBC và CRP tăng cao kèm sốt; Hen/COPD có $SpO_2$ giảm và nhịp thở tăng; Suy tim có huyết áp cao và tiền sử tăng huyết áp).
     - Sinh ngẫu nhiên tỷ lệ missingness thực tế khoảng 15-25% cho các chỉ số xét nghiệm (CRP, WBC) để phục vụ thử nghiệm MICE ở Tuần 2.
  2. Cấu trúc mỗi bản ghi dữ liệu thô bao gồm:
     - Bảng số: `patient_id`, `encounter_id`, `encounter_timestamp`, `diagnostic_confirmed_timestamp`, 9 biến số, 4 biến phân loại, và nhãn `diagnosis_label`.
     - Ghi chú lâm sàng tự do (`clinical_notes`): Chứa văn bản mô tả bệnh sử thực tế, triệu chứng cơ năng, khám thực thể, và cố tình đưa vào các thực thể định danh giả định (tên người, số điện thoại, ngày khám, tên bệnh viện) để phục vụ kiểm thử pipeline De-ID ở Tuần 2.
  3. Lưu trữ dữ liệu:
     - Bảng số lưu tại `data/raw/patients_raw.parquet`.
     - Ghi chú lưu tại `data/raw/clinical_notes_raw.jsonl`.
* **Lệnh thực thi & kiểm thử:**
  ```bash
  python scripts/generate_synthetic_ehr.py --num_samples 2000 --output_dir data/raw/
  ```
* **Đầu ra (Deliverables):**
  - `scripts/generate_synthetic_ehr.py`.
  - `data/raw/patients_raw.parquet`.
  - `data/raw/clinical_notes_raw.jsonl`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 2.3: Thiết Lập Quản Trị Bảo Mật Dữ Liệu Cục Bộ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Đảm bảo cấu hình `.gitignore` chặn tuyệt đối không cho đẩy các thư mục chứa dữ liệu thô và dữ liệu đã xử lý lên Git remote:
     ```gitignore
     data/raw/
     data/processed/
     data/checkpoints/
     *.parquet
     *.jsonl
     ```
  2. Viết tài liệu hướng dẫn cấu trúc trường dữ liệu thô tại `data/README.md`.
* **Đầu ra (Deliverables):**
  - Tệp `.gitignore` được cập nhật chính xác.
  - Tệp `data/README.md`.
* **Trạng thái:** `[x] DONE`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 2 (ACCEPTANCE CRITERIA)
- [x] Tệp `configs/data_schema.yaml` chuẩn hóa đầy đủ 9 biến số, 4 biến phân loại, 4 nhãn bệnh, khớp hoàn toàn với đặc tả dự án.
- [x] Chạy thành công lệnh `python scripts/generate_synthetic_ehr.py` tạo ra tối thiểu 2.000 bản ghi.
- [x] Kiểm tra `patients_raw.parquet` đọc được bằng `pandas.read_parquet()` và `clinical_notes_raw.jsonl` có số lượng dòng khớp chính xác với số lượng `patient_id`.
- [x] Bàn giao schema và đường dẫn dữ liệu thô cho Thành viên 1 và Thành viên 3.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 2
1. **Nghiên cứu Tổng quan JMIR 2024 về biến số EHR tại tuyến cơ sở:**
   * *Hunik, L. et al. (2024).* "Prediction Models for Diagnosis in Primary Care Using Electronic Health Records: Systematic Review." *JMIR Medical Informatics*, Preprint 62862.
   * *Trọng tâm cần đọc:* Bảng 1 và Bảng 2 mô tả tần suất xuất hiện và phân bố của các chỉ số sinh hiệu (Huyết áp, $SpO_2$, Nhịp tim, Nhịp thở, Thân nhiệt) và xét nghiệm cơ bản (Bạch cầu WBC, CRP) trong các bệnh án hô hấp/tim mạch tuyến đầu. File tệp PDF có sẵn tại: [`docs/preprint-62862-accepted (1).pdf`](file:///d:/CODE/C%C3%81C%20V%E1%BA%A4N%20%C4%90%E1%BB%80%20HI%E1%BB%86N%20%C4%90%E1%BA%A0I/multimodal-ehr-cdss/docs/preprint-62862-accepted%20(1).pdf).
2. **Cơ sở dữ liệu lâm sàng mẫu MIMIC-IV & MIMIC-IV-Note:**
   * *Johnson, A. et al. (2023).* "MIMIC-IV-Note: De-identified free-text clinical notes." *PhysioNet*. [doi:10.13026/1n74-ne17](https://doi.org/10.13026/1n74-ne17).
   * *Trọng tâm cần đọc:* Cách cấu trúc ghi chú tiến trình điều trị (History of Present Illness, Physical Examination, Chief Complaint) để sinh dữ liệu văn bản sát thực tế lâm sàng.
3. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.1, Mục 2.2 và Mục 3.1).

