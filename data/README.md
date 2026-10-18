# Multimodal Clinical Decision Support System (M-CDSS) - Data Directory

## 1. Tổng Quan Cấu Trúc Thư Mục Dữ Liệu
Thư mục `data/` được tổ chức theo kiến trúc phân tầng phục vụ pipeline xử lý và mô hình học máy:

```
data/
├── raw/                      # Dữ liệu bán tổng hợp thô ban đầu (chưa khử định danh, chưa gán khuyết)
│   ├── patients_raw.parquet  # Dữ liệu bảng số lâm sàng (2.000+ bệnh nhân)
│   └── clinical_notes_raw.jsonl # Ghi chú bệnh án lâm sàng tự do (chứa PHI/PII giả định)
├── processed/                # Dữ liệu đã qua pipeline tiền xử lý (De-ID, Temporal Lock, MICE)
│   ├── train.parquet         # Tập huấn luyện (70%)
│   ├── val.parquet           # Tập kiểm định (15%)
│   └── test.parquet          # Tập kiểm thử độc lập (15%)
├── checkpoints/              # Checkpoints trọng số mô hình trong quá trình huấn luyện
├── guidelines/               # Hướng dẫn lâm sàng tham chiếu phục vụ RAG (Gold Guidelines)
└── vector_store/             # Cơ sở dữ liệu vector (Qdrant / FAISS indices)
```

## 2. Đặc Tả Dữ Liệu Thô (`data/raw/`)

### 2.1. Bảng số lâm sàng (`patients_raw.parquet`)
Tệp lưu trữ dưới định dạng Apache Parquet gồm các trường:
* **Khóa định danh & Thời gian:**
  - `patient_id` (`str`): Mã định danh bệnh nhân (VD: `PT-0001`).
  - `encounter_id` (`str`): Mã đợt khám/nhập viện (VD: `ENC-0001`).
  - `encounter_timestamp` (`str` / ISO 8601): Mốc thời gian bắt đầu tiếp nhận ca bệnh (VD: `2026-09-10T08:30:00`).
  - `diagnostic_confirmed_timestamp` (`str` / ISO 8601): Mốc thời gian bác sĩ ra chẩn đoán chính thức (dùng để khóa chuỗi thời gian, chống rò rỉ nhãn theo PROBAST).

* **9 Biến số liên tục (Continuous Numerical Features):**
  - `age` (`int`): Tuổi (18 - 110 tuổi).
  - `systolic_bp` (`float`): Huyết áp tâm thu (mmHg, bình thường: 90.0 - 130.0).
  - `diastolic_bp` (`float`): Huyết áp tâm trương (mmHg, bình thường: 60.0 - 85.0).
  - `heart_rate` (`float`): Nhịp tim (bpm, bình thường: 60.0 - 100.0).
  - `respiratory_rate` (`float`): Nhịp thở (breaths/min, bình thường: 12.0 - 20.0).
  - `spo2` (`float`): Độ bão hòa oxy trong máu (% , bình thường: 95.0 - 100.0).
  - `temperature` (`float`): Thân nhiệt (độ C, bình thường: 36.5 - 37.5).
  - `wbc_count` (`float`): Số lượng bạch cầu ($10^9$/L, bình thường: 4.0 - 10.0, có 15-25% tỷ lệ thiếu ngẫu nhiên).
  - `crp` (`float`): Protein phản ứng C (mg/L, bình thường: 0.0 - 5.0, có 15-25% tỷ lệ thiếu ngẫu nhiên).

* **4 Biến phân loại (Categorical Features):**
  - `gender` (`str`): Giới tính (`"M"`, `"F"`, `"OTHER"`).
  - `smoking_status` (`str`): Tình trạng hút thuốc lá (`"NEVER"`, `"FORMER"`, `"CURRENT"`).
  - `history_hypertension` (`int`): Tiền sử tăng huyết áp (`0` hoặc `1`).
  - `history_diabetes` (`int`): Tiền sử đái tháo đường (`0` hoặc `1`).

* **Nhãn bệnh mục tiêu (Target Label):**
  - `diagnosis_label` (`int`): Mã nhãn phân loại 4 nhóm bệnh:
    * `0`: `ASTHMA` (Hen phế quản)
    * `1`: `COPD` (Bệnh phổi tắc nghẽn mạn tính)
    * `2`: `CONGESTIVE_HEART_FAILURE` (Suy tim sung huyết)
    * `3`: `COMMUNITY_ACQUIRED_PNEUMONIA` (Viêm phổi mắc phải cộng đồng)

### 2.2. Ghi chú lâm sàng tự do (`clinical_notes_raw.jsonl`)
Mỗi bản ghi được lưu trên một dòng JSON Lines độc lập:
```json
{
  "patient_id": "PT-0001",
  "encounter_id": "ENC-0001",
  "encounter_timestamp": "2026-09-10T08:30:00",
  "diagnostic_confirmed_timestamp": "2026-09-10T11:00:00",
  "raw_text": "Bệnh nhân Nguyễn Văn An, 64 tuổi, SĐT 0912345678 đến khám tại Bệnh viện Bạch Mai...",
  "chief_complaint": "Khó thở khi gắng sức kèm ho khan...",
  "history_of_present_illness": "Bệnh khởi phát 3 ngày trước...",
  "physical_examination_notes": "Nghe phổi có rale rít rải rác...",
  "prior_medications": "Salbutamol xịt..."
}
```
*Lưu ý bảo mật*: Trong `raw_text` cố tình chèn các thực thể PHI/PII giả định (tên bệnh nhân, số điện thoại, ngày khám, số CMND/CCCD, tên bệnh viện, thẻ BHYT) để phục vụ việc kiểm thử pipeline De-Identification ở Tuần 2.

## 3. Chính Sách Quản Trị Bảo Mật (HIPAA / Safe Harbor)
- Toàn bộ dữ liệu trong `data/raw/`, `data/processed/`, và các file `*.parquet`, `*.jsonl`, `*.csv` đều được cấu hình trong `.gitignore` để ngăn chặn việc commit thông tin dữ liệu bệnh án lên Git repository.
- Chỉ lưu trữ các tệp `.gitkeep` để duy trì cấu trúc thư mục rỗng trên remote.
