# HƯỚNG DẪN KỸ THUẬT CHI TIẾT GIAI ĐOẠN 1: CẤU TRÚC FILE CODE, QUY CÁCH LƯU KẾT QUẢ & TÀI LIỆU THAM KHẢO
### Multimodal Clinical Decision Support System (M-CDSS)
**Dành cho 3 Thành Viên Nhóm Phát Triển (Lead ML, Data Engineer, Full-Stack AI)**

---

## 1. TỔNG QUAN BẢN ĐỒ FILE CODE & FILE KẾT QUẢ GIAI ĐOẠN 1

Toàn bộ Giai đoạn 1 (Tuần 1 đến Tuần 3) vận hành theo chu trình khép kín:
```
[Dữ Liệu Thô (data/raw/)] 
   ──> [Data Pipeline (De-ID, Temporal Lock, MICE)] 
   ──> [Dữ Liệu Sạch (data/processed/)] 
   ──> [Huấn Luyện 3 Baselines (scripts/run_baselines.py)] 
   ──> [Kết Quả Benchmark (data/baseline_results.json + curves.png)] 
   ──> [Báo Cáo Đề Xuất Tối Ưu (docs/PROPOSED_OPTIMAL_SOLUTION.md)]
```

### Bảng Ánh Xạ File Code và File Kết Quả Đầu Ra

| STT | File Mã Nguồn (Code File) | Trách Nhiệm | Chức Năng Cốt Lõi | File Kết Quả Tạo Ra (Output File) | Định Dạng Lưu Trữ |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **01** | `configs/data_schema.yaml` | TV2 | Khai báo 9 biến số, 4 biến phân loại, 4 nhãn bệnh | `configs/data_schema.yaml` | YAML |
| **02** | `configs/model_config.yaml` | TV1 | Siêu tham số XGBoost, FT-Tabular, Bio_ClinicalBERT | `configs/model_config.yaml` | YAML |
| **03** | `scripts/verify_env.py` | TV1 | Kiểm tra CUDA GPU, PyTorch, packages | Console Logs / GPU Status | Text Log |
| **04** | `scripts/generate_synthetic_ehr.py` | TV2 | Sinh 2.000 ca bệnh thô (bảng + text ghi chú) | `data/raw/patients_raw.parquet`<br/>`data/raw/clinical_notes_raw.jsonl` | Apache Parquet<br/>JSON Lines |
| **05** | `src/data_pipeline/deidentifier.py` | TV2 | Khử định danh PHI/PII (Regex + spaCy NER) | Trả về text đã ẩn danh | In-memory String |
| **06** | `src/data_pipeline/temporal_aligner.py`| TV2 | Khóa thời gian $t < t_{diag}$, Blacklist FEV1/EF | Dataframe sạch rò rỉ nhãn | In-memory DataFrame |
| **07** | `src/data_pipeline/imputer.py` | TV2 | Gán khuyết MICE (Bayesian Ridge) + Binary Indicator | Dataframe không còn NaN | In-memory DataFrame |
| **08** | `src/data_pipeline/dataset_loader.py` | TV2 | Phân chia bệnh nhân 70/15/15 & PyTorch Dataset | `data/processed/train.parquet`<br/>`data/processed/val.parquet`<br/>`data/processed/test.parquet` | Apache Parquet (Snappy compressed) |
| **09** | `src/models/baselines.py` | TV1 | 3 Lớp Baselines: Classical, FT-Tabular, TextBERT | Checkpoints mô hình nạp trong RAM | PyTorch / Sklearn Models |
| **10** | `src/evaluation/metrics.py` | TV1 | Tính toán Macro AUROC, AUPRC, F1, Brier, ECE | Dictionary chỉ số đánh giá | In-memory Dict |
| **11** | `scripts/run_baselines.py` | TV1 | Huấn luyện tự động 3 Baselines, đo đạc & vẽ hình | `data/baseline_results.json`<br/>`data/baseline_curves.png`<br/>`data/confusion_matrices_baselines.png` | JSON file<br/>PNG (300 DPI)<br/>PNG (300 DPI) |
| **12** | `src/api/schemas.py` | TV3 | Pydantic Schemas cho API Request/Response | Hợp đồng API backend | Python Module |
| **13** | `src/api/main.py` & `routes/inference.py` | TV3 | FastAPI server: `/health`, `/api/v1/predict/baseline` | HTTP REST API Endpoints | JSON Response |
| **14** | `frontend/src/components/PatientDataForm.tsx` | TV3 | Giao diện nhập liệu 2 cột (số liệu + bệnh án) | Web UI Component | TypeScript / React |
| **15** | `frontend/src/app/baselines/page.tsx` | TV3 | Giao diện Dashboard so sánh đối đầu 3 Baselines | Web UI Page | Next.js Page |
| **16** | `tests/test_data_pipeline.py` | TV3 | Unit test khử PHI, khóa thời gian, MICE | Test Report | Pytest Output |
| **17** | `tests/test_baselines_benchmark.py` | TV3 | Unit test xác thực tính hợp lệ của `baseline_results.json` | Test Report | Pytest Output |
| **18** | `docs/PROPOSED_OPTIMAL_SOLUTION.md` | Cả 3 TV | Báo cáo đề xuất phương án tối ưu nghiệm thu GĐ 1 | `docs/PROPOSED_OPTIMAL_SOLUTION.md` | Markdown Report |

---

## 2. CHI TIẾT CẤU TRÚC FILE CODE & ĐẶC TẢ KỸ THUẬT

### 2.1. Cấu hình Dữ liệu (`configs/data_schema.yaml`) - Phụ trách: TV2
* **Mục đích:** Định nghĩa Hợp đồng Dữ liệu duy nhất cho cả hệ thống.
* **Cấu trúc nội dung:**
```yaml
features:
  numerical:
    - name: "age"
      type: "int"
      min: 18
      max: 110
      unit: "years"
    - name: "systolic_bp"
      type: "float"
      normal_range: [90.0, 130.0]
      min: 60.0
      max: 240.0
      unit: "mmHg"
    - name: "diastolic_bp"
      type: "float"
      normal_range: [60.0, 85.0]
      min: 40.0
      max: 140.0
      unit: "mmHg"
    - name: "heart_rate"
      type: "float"
      normal_range: [60.0, 100.0]
      min: 30.0
      max: 220.0
      unit: "bpm"
    - name: "respiratory_rate"
      type: "float"
      normal_range: [12.0, 20.0]
      min: 8.0
      max: 50.0
      unit: "breaths/min"
    - name: "spo2"
      type: "float"
      normal_range: [95.0, 100.0]
      min: 60.0
      max: 100.0
      unit: "%"
    - name: "temperature"
      type: "float"
      normal_range: [36.5, 37.5]
      min: 35.0
      max: 42.0
      unit: "Celsius"
    - name: "wbc_count"
      type: "float"
      normal_range: [4.0, 10.0]
      min: 1.0
      max: 50.0
      unit: "10^9/L"
    - name: "crp"
      type: "float"
      normal_range: [0.0, 5.0]
      min: 0.0
      max: 300.0
      unit: "mg/L"

  categorical:
    - name: "gender"
      categories: ["M", "F", "OTHER"]
    - name: "smoking_status"
      categories: ["NEVER", "FORMER", "CURRENT"]
    - name: "history_hypertension"
      categories: [0, 1]
    - name: "history_diabetes"
      categories: [0, 1]

targets:
  task_type: "multiclass"
  num_classes: 4
  labels:
    0: "ASTHMA"
    1: "COPD"
    2: "CONGESTIVE_HEART_FAILURE"
    3: "COMMUNITY_ACQUIRED_PNEUMONIA"
```

---

### 2.2. Script Sinh Dữ Liệu Lâm Sàng Thô (`scripts/generate_synthetic_ehr.py`) - Phụ trách: TV2
* **Mục đích:** Tạo tập dữ liệu bán tổng hợp gồm 2.000 bệnh nhân có đủ dữ liệu bảng số và ghi chú tự do sát thực tế lâm sàng.
* **Hàm cốt lõi:**
  ```python
  def generate_synthetic_data(num_patients: int = 2000, seed: int = 42) -> tuple[pd.DataFrame, list[dict]]:
      """
      Sinh cặp dữ liệu bảng số và ghi chú lâm sàng.
      Tạo mối tương quan bệnh lý:
      - ASTHMA: Trẻ hơn, SpO2 giảm nhẹ, rale rít, tiền sử dị ứng/hen.
      - COPD: Lớn tuổi, tiền sử hút thuốc nặng, SpO2 giảm, rale ngáy.
      - CHF: Huyết áp cao, nhịp thở nhanh, phù chân, khó thở khi nằm.
      - CAP: Sốt cao, WBC và CRP tăng vọt, ho đờm đục, rale ẩm.
      Chèn ngẫu nhiên tên bác sĩ, bệnh viện, SĐT, CCCD để test pipeline De-ID.
      """
  ```
* **Quy cách lưu file kết quả:**
  1. `data/raw/patients_raw.parquet`: Lưu bảng số bằng `df.to_parquet("data/raw/patients_raw.parquet", index=False)`.
  2. `data/raw/clinical_notes_raw.jsonl`: Lưu mỗi ca bệnh trên 1 dòng JSON:
     ```json
     {"patient_id": "PT-0001", "encounter_id": "ENC-0001", "encounter_timestamp": "2026-09-10T08:30:00", "diagnostic_confirmed_timestamp": "2026-09-10T11:00:00", "raw_text": "Bệnh nhân Nguyễn Văn An, 64 tuổi, SĐT 0912345678 đến khám tại Bệnh viện Bạch Mai do khó thở..."}
     ```

---

### 2.3. Pipeline Khử Định Danh (`src/data_pipeline/deidentifier.py`) - Phụ trách: TV2
* **Class cốt lõi:** `ClinicalDeidentifier`
* **Phương thức:**
  ```python
  class ClinicalDeidentifier:
      def __init__(self, spacy_model: str = "en_core_web_sm"):
          # Khởi tạo Regex patterns và load model spaCy
          ...

      def deidentify_text(self, text: str) -> str:
          """
          Đầu vào: Chuỗi văn bản bệnh án thô chứa tên, ngày, SĐT, CCCD.
          Đầu ra: Chuỗi văn bản đã thế chỗ bằng [REDACTED_NAME], [REDACTED_DATE],...
          """
  ```
* **Quy chuẩn token thay thế:**
  - `[REDACTED_NAME]`: Tên bệnh nhân, bác sĩ.
  - `[REDACTED_PHONE]`: Số điện thoại.
  - `[REDACTED_ID]`: Số CCCD, số thẻ BHYT, MRN.
  - `[REDACTED_HOSPITAL]`: Bệnh viện, cơ sở khám chữa bệnh.
  - `[REDACTED_DATE]`: Mốc ngày tháng cá nhân.

---

### 2.4. Khóa Chuỗi Thời Gian & Lọc Blacklist (`src/data_pipeline/temporal_aligner.py`) - Phụ trách: TV2
* **Class cốt lõi:** `TemporalAligner`
* **Phương thức:**
  ```python
  class TemporalAligner:
      GOLD_STANDARD_BLACKLIST = [
          "fev1", "fvc", "fev1_fvc_ratio", "tiffeneau_ratio",  # Tiêu chuẩn vàng COPD (GOLD)
          "lvef", "ef", "ejection_fraction",                   # Tiêu chuẩn vàng Suy tim (ESC)
          "sputum_culture_bacteria", "antibiotic_sensitivity"  # Tiêu chuẩn vàng Viêm phổi
      ]

      def filter_events_by_time(self, events_df: pd.DataFrame, 
                                event_time_col: str, 
                                diag_time_col: str) -> pd.DataFrame:
          """Loại bỏ triệt để bản ghi có event_time >= diag_time."""

      def remove_gold_standard_leakage(self, df: pd.DataFrame) -> pd.DataFrame:
          """Loại bỏ bất kỳ cột nào thuộc GOLD_STANDARD_BLACKLIST."""
  ```

---

### 2.5. Gán Dữ Liệu Khuyết MICE (`src/data_pipeline/imputer.py`) - Phụ trách: TV2
* **Class cốt lõi:** `ClinicalMICEImputer`
* **Phương thức:**
  ```python
  class ClinicalMICEImputer:
      def __init__(self, max_iter: int = 10, random_state: int = 42):
          # Sử dụng IterativeImputer(estimator=BayesianRidge())
          ...

      def fit(self, X: pd.DataFrame):
          """Chỉ học trên tập Train (tránh rò rỉ phân phối)."""

      def transform(self, X: pd.DataFrame) -> pd.DataFrame:
          """
          1. Gán khuyết cho 9 biến số qua MICE.
          2. Gán khuyết biến phân loại bằng Mode.
          3. Tự động thêm cột nhị phân '{feature}_is_missing' (0 hoặc 1).
          """
  ```

---

### 2.6. Chia Tập Bệnh Nhân & Dataset Loader (`src/data_pipeline/dataset_loader.py`) - Phụ trách: TV2
* **Hàm phân chia:**
  ```python
  def create_patient_level_splits(
      df: pd.DataFrame, 
      patient_col: str = "patient_id", 
      target_col: str = "diagnosis_label", 
      train_size: float = 0.70, 
      val_size: float = 0.15, 
      test_size: float = 0.15, 
      seed: int = 42
  ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
      """
      Áp dụng StratifiedGroupKFold theo patient_id.
      Đảm bảo 100% không có patient_id nào xuất hiện ở 2 tập khác nhau.
      """
  ```
* **Quy cách lưu file kết quả:**
  Lưu trực tiếp vào `data/processed/`:
  - `data/processed/train.parquet` (70% ~ 1.400 bệnh nhân).
  - `data/processed/val.parquet` (15% ~ 300 bệnh nhân).
  - `data/processed/test.parquet` (15% ~ 300 bệnh nhân).
* **Lớp PyTorch Dataset:**
  ```python
  class MultimodalEHRDataset(torch.utils.data.Dataset):
      def __init__(self, df: pd.DataFrame, notes_dict: dict, tokenizer, max_length: int = 512):
          ...
      def __getitem__(self, idx: int) -> dict:
          return {
              "tabular": torch.tensor(..., dtype=torch.float32),      # [13] biến (9 số + 4 cat)
              "input_ids": torch.tensor(..., dtype=torch.long),       # [512] tokens
              "attention_mask": torch.tensor(..., dtype=torch.long),  # [512] mask
              "label": torch.tensor(..., dtype=torch.long)            # scalar (0-3)
          }
  ```

---

### 2.7. Khung 3 Baselines (`src/models/baselines.py`) - Phụ trách: TV1
* **3 Lớp mô hình đối chứng:**
  1. `ClassicalTabularBaseline`:
     - Sklearn Pipeline: `ColumnTransformer` (StandardScaler + OneHotEncoder) + `XGBClassifier(objective='multi:softprob', n_estimators=300, max_depth=6)`.
     - Cung cấp: `.fit(X, y)`, `.predict(X)`, `.predict_proba(X)`.
  2. `TabularDeepBaseline(nn.Module)`:
     - Mạng FT-Transformer rút gọn: `FeatureTokenizer` chiếu từng biến lên $D=128$, qua 4 lớp `TransformerEncoderLayer`, pooling `[CLS]` token và đi qua linear classification head.
  3. `TextOnlyBaseline(nn.Module)`:
     - Tải `emilyalsentzer/Bio_ClinicalBERT` từ HuggingFace.
     - Trích xuất token `[CLS]` (768 chiều), qua Dropout (0.2) và Linear Layer (768 -> 4).

---

### 2.8. Hệ Thống Đo Đạc Độ Đo Đa Lớp (`src/evaluation/metrics.py`) - Phụ trách: TV1
* **Hàm đánh giá chuẩn:**
  ```python
  def compute_multiclass_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
      """
      Đầu vào:
        y_true: vector nhãn thực tế [N] (giá trị 0, 1, 2, 3)
        y_prob: ma trận xác suất dự đoán [N, 4] (tổng mỗi hàng = 1.0)
      Đầu ra dict:
        {
          "macro_auroc": float,
          "macro_auprc": float,
          "macro_f1": float,
          "accuracy": float,
          "brier_score": float,
          "ece": float
        }
      """
  ```

---

### 2.9. Script Huấn Luyện Tự Động 3 Baselines (`scripts/run_baselines.py`) - Phụ trách: TV1
* **Mục đích:** Đọc dữ liệu từ `data/processed/`, lần lượt huấn luyện Baseline 1, 2, 3 trên tập Train; chọn model tốt nhất trên tập Val; và đo đạc lần cuối trên tập Test.
* **Lệnh chạy:**
  ```bash
  python scripts/run_baselines.py --data_dir data/processed/ --output_json data/baseline_results.json --output_plot data/baseline_curves.png
  ```

---

## 3. ĐẶC TẢ CHI TIẾT CÁC FILE KẾT QUẢ ĐẦU RA (OUTPUT DATA SCHEMAS)

### 3.1. File Kết Quả Điểm Chuẩn (`data/baseline_results.json`)
Tệp này do `scripts/run_baselines.py` xuất ra. Đây là cơ sở thực nghiệm bắt buộc để nghiệm thu Giai đoạn 1:
```json
{
  "benchmark_metadata": {
    "evaluation_date": "2026-10-07T14:30:00",
    "test_samples": 300,
    "num_classes": 4,
    "classes": ["ASTHMA", "COPD", "CONGESTIVE_HEART_FAILURE", "COMMUNITY_ACQUIRED_PNEUMONIA"]
  },
  "results": {
    "baseline_1_classical_tabular": {
      "model_type": "XGBoost",
      "data_modality": "Structured Tabular Only",
      "macro_auroc": 0.8145,
      "macro_auprc": 0.7421,
      "macro_f1": 0.7380,
      "accuracy": 0.7533,
      "brier_score": 0.2412,
      "ece": 0.0874
    },
    "baseline_2_tabular_deep": {
      "model_type": "FT-Transformer (Tabular DL)",
      "data_modality": "Structured Tabular Only",
      "macro_auroc": 0.8312,
      "macro_auprc": 0.7605,
      "macro_f1": 0.7495,
      "accuracy": 0.7667,
      "brier_score": 0.2290,
      "ece": 0.0921
    },
    "baseline_3_text_only": {
      "model_type": "Bio_ClinicalBERT",
      "data_modality": "Unstructured Clinical Notes Only",
      "macro_auroc": 0.8260,
      "macro_auprc": 0.7540,
      "macro_f1": 0.7430,
      "accuracy": 0.7567,
      "brier_score": 0.2378,
      "ece": 0.1085
    }
  },
  "summary_findings": {
    "highest_auroc_model": "FT-Transformer (0.8312)",
    "calibration_warning": "Tất cả 3 baseline đều có ECE > 0.08 (chưa được hiệu chuẩn, có hiện tượng overconfidence).",
    "clinical_blindspot": "Mô hình bảng số thiếu ngữ cảnh bệnh sử; mô hình text thiếu độ nhạy chỉ số sinh tồn. Cần phương án Multimodal Late Fusion ở Giai đoạn 2."
  }
}
```

---

### 3.2. File Đồ Thị So Sánh Hiệu Năng (`data/baseline_curves.png`)
* **Định dạng:** PNG, kích thước $1800 \times 600$ px (300 DPI).
* **Nội dung 3 đồ thị con (3 Subplots):**
  - **Subplot 1 (One-vs-Rest ROC Curves):** So sánh 3 đường cong ROC của 3 baseline kèm diện tích dưới đường cong (AUC).
  - **Subplot 2 (Precision-Recall Curves):** So sánh PR-Curve giữa 3 mô hình.
  - **Subplot 3 (Calibration Reliability Diagram):** Trục hoành là Mean Predicted Confidence, trục tung là Fraction of Positives (thể hiện rõ đường cong lệch xa đường chéo lý tưởng $y=x$, chứng minh ECE cao).

---

### 3.3. File Ma Trận Nhầm Lẫn (`data/confusion_matrices_baselines.png`)
* **Định dạng:** PNG, gồm 3 ma trận nhiệt (Heatmap) đặt cạnh nhau đại diện cho 3 mô hình.
* **Mục tiêu:** Phục vụ trực tiếp việc trích dẫn ca bệnh sai biệt cho Báo Cáo Đề Xuất Tối Ưu (`docs/PROPOSED_OPTIMAL_SOLUTION.md`).

---

## 4. QUY TRÌNH CHẠY THỰC THI TUẦN TỰ (END-TO-END WORKFLOW)

Khi làm việc, 3 thành viên thực hiện phối hợp theo đúng thứ tự 6 lệnh terminal sau:

```bash
# BƯỚC 1: Kiểm tra môi trường GPU & packages (TV1 thực hiện)
python scripts/verify_env.py

# BƯỚC 2: Sinh dữ liệu lâm sàng thô 2.000 ca (TV2 thực hiện)
python scripts/generate_synthetic_ehr.py --num_samples 2000 --output_dir data/raw/

# BƯỚC 3: Chạy Unit Tests kiểm tra Pipeline dữ liệu, De-ID, Temporal Lock, MICE (TV3 thực hiện)
pytest tests/test_data_pipeline.py -v

# BƯỚC 4: Huấn luyện tự động 3 Baselines & xuất kết quả benchmark (TV1 thực hiện)
python scripts/run_baselines.py --data_dir data/processed/ --output_json data/baseline_results.json --output_plot data/baseline_curves.png

# BƯỚC 5: Kiểm tra tính hợp lệ của tệp kết quả benchmark JSON (TV3 thực hiện)
pytest tests/test_baselines_benchmark.py -v

# BƯỚC 6: Khởi chạy Web Dashboard hiển thị kết quả so sánh 3 Baselines (TV3 thực hiện)
cd frontend && npm run dev   # Mở trình duyệt xem tại http://localhost:3000/baselines
```

---

## 5. DANH MỤC TÀI LIỆU THAM KHẢO CHUYÊN MÔN CỐT LÕI (REFERENCES)

Để viết báo cáo đề xuất tối ưu và code đúng chuẩn y khoa quốc tế, các thành viên cần nghiên cứu các tài liệu tham khảo chính sau:

1. **Khoảng trống y văn & Nguy cơ sai lệch trong AI Y tế:**
   * **Hunik, L. et al. (2024).** *"Prediction Models for Diagnosis in Primary Care Using Electronic Health Records: Systematic Review."* **JMIR Medical Informatics**, Preprint 62862.
     - *Ý nghĩa:* Nguồn gốc bài toán dự án. Chỉ ra 100% mô hình thiếu dữ liệu text, 60% có Target Leakage và Temporal Misalignment, 67% xử lý sai dữ liệu khuyết. Tệp PDF có sẵn tại: [`docs/preprint-62862-accepted (1).pdf`](file:///d:/CODE/C%C3%81C%20V%E1%BA%A4N%20%C4%90%E1%BB%80%20HI%E1%BB%86N%20%C4%90%E1%BA%A0I/multimodal-ehr-cdss/docs/preprint-62862-accepted%20(1).pdf).
2. **Kiến trúc Mạng Nơ-ron Dạng Bảng (FT-Transformer):**
   * **Gorishniy, Y., Rubachev, A., Khrulkov, V., & Babenko, A. (2021).** *"Revisiting Deep Learning Models for Tabular Data."* **NeurIPS 2021**.
     - *Ý nghĩa:* Cơ sở lý thuyết của `TabularTokenizer` và `FTTransformerEncoder`. Chứng minh Feature Tokenizer Transformer vượt trội MLP và cạnh tranh sòng phẳng với Gradient Boosted Trees trên dữ liệu bảng số.
3. **Mô hình Ngôn ngữ Chuyên sâu Y sinh:**
   * **Alsentzer, E. et al. (2019).** *"Publicly Available Clinical BERT Embeddings."* **NAACL Clinical NLP Workshop 2019**.
     - *Ý nghĩa:* Mô hình nền tảng của Baseline 3 (`emilyalsentzer/Bio_ClinicalBERT`) được tiền huấn luyện trên MIMIC-III Clinical Notes.
   * **Yasunaga, M. et al. (2022).** *"LinkBERT: Pre-training Language Models with Document Links."* **ACL 2022**.
     - *Ý nghĩa:* Mô hình `BioLinkBERT` dùng làm Text Encoder mở rộng cho Giai đoạn 2.
4. **Xử lý Dữ liệu Khuyết Đa biến (MICE):**
   * **van Buuren, S., & Groothuis-Oudshoorn, K. (2011).** *"mice: Multivariate Imputation by Chained Equations in R."* **Journal of Statistical Software**, 45(3), 1-67.
     - *Ý nghĩa:* Thuật toán hồi quy chuỗi Chained Equations (Bayesian Ridge) được triển khai qua `sklearn.impute.IterativeImputer`.
5. **Tiêu chuẩn Thẩm định & Giảm Sai Lệch Lâm Sàng (PROBAST & TRIPOD-AI):**
   * **Wolff, R. F. et al. (2019).** *"PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies."* **Annals of Internal Medicine**, 170(1), 51-58.
     - *Ý nghĩa:* 20 tiêu chuẩn vàng để kiểm toán mô hình không có bias (đặc biệt Domain 2: Predictors và Domain 3: Outcome).
   * **Collins, G. S. et al. (2024).** *"TRIPOD+AI Statement: Updated Guidance for Reporting Clinical Prediction Models That Use Artificial Intelligence."* **The BMJ**, 385:e078378.
     - *Ý nghĩa:* Khung hướng dẫn báo cáo khoa học bắt buộc phải tuân theo khi soạn thảo Báo Cáo Đề Xuất và Bài Báo cuối kỳ.
6. **Hiệu Chuẩn Xác Suất (Probability Calibration):**
   * **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).** *"On Calibration of Modern Neural Networks."* **ICML 2017**.
     - *Ý nghĩa:* Nguồn gốc công thức **Temperature Scaling** để tối ưu hóa ECE mà nhóm sẽ đề xuất áp dụng ở Giai đoạn 2.
