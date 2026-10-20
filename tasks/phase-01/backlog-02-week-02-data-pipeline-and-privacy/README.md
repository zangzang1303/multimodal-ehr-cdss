# BACKLOG 02 (TUẦN 2): DATA PIPELINE, BẢO MẬT DE-ID & KHUNG 3 BASELINES
### Giai Đoạn 1 | Mục Tiêu: Xây Dựng Pipeline Tiền Xử Lý Lâm Sàng Chuẩn PROBAST & Dựng Khung 3 Baselines

---

## 1. MỤC TIÊU CỐT LÕI CỦA TUẦN 2
Tuần 2 giải quyết trực diện các sai sót phương pháp luận nghiêm trọng mà nghiên cứu tổng quan JMIR (*Hunik et al., 2024*) đã cảnh báo (rò rỉ nhãn, mất đồng bộ thời gian, xóa bỏ dữ liệu khuyết vô tội vạ) và chuẩn bị sẵn sàng khung 3 mô hình đối chứng:
1. **Khử định danh PHI tự động (`deidentifier.py`):** Áp dụng cơ chế lai giữa Regex Rule Engine và Biomedical NER (`en_core_web_sm` / `en_ner_bc5cdr_md`) che dấu danh tính bệnh nhân và bác sĩ bằng các surrogate tokens (`[REDACTED_*]`).
2. **Khóa chuỗi thời gian & Chống rò rỉ nhãn (`temporal_aligner.py`):**
   - Loại bỏ 100% các sự kiện có $t_{event} \ge t_{diag}$.
   - Thiết lập **Gold-Standard Blacklist** loại bỏ các xét nghiệm tiêu chuẩn vàng (Hô hấp ký FEV1/FVC của Hen/COPD, Siêu âm tim EF của Suy tim, cấy vi khuẩn của Viêm phổi) khỏi biến đầu vào.
3. **Xử lý dữ liệu khuyết đa biến MICE (`imputer.py`):** Áp dụng hồi quy chuỗi Chained Equations (Bayesian Ridge) gán khuyết theo cơ chế MAR và tạo các cột nhị phân `_is_missing` để bảo toàn tín hiệu lâm sàng.
4. **Khung 3 Baselines (`src/models/baselines.py`):** Xây dựng lớp mã nguồn hoàn chỉnh cho Baseline 1 (Classical Tabular: XGBoost/CatBoost), Baseline 2 (Tabular Deep Learning: FT-Transformer), và Baseline 3 (Clinical NLP: Bio_ClinicalBERT).
5. **Kiểm thử tự động & Giao diện:** Bộ Unit Tests `tests/test_data_pipeline.py` kiểm tra toàn bộ pipeline và giao diện form nhập liệu `PatientDataForm.tsx` trên Next.js 14.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã nghiệm thu hoàn tất Backlog 01 (Tuần 1).**
- Tệp `configs/data_schema.yaml` và `configs/model_config.yaml` đã được phê duyệt.
- Dữ liệu thô `data/raw/patients_raw.parquet` và `clinical_notes_raw.jsonl` đã sẵn sàng.
- Đã đọc kỹ tài liệu: [`docs/03_DATA_PIPELINE_AND_PRIVACY.md`](../../docs/03_DATA_PIPELINE_AND_PRIVACY.md) và đặc tả chi tiết code/kết quả tại [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG TUẦN 2

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách hiện thực khung 3 Baselines trong `src/models/baselines.py`, viết khung pipeline huấn luyện `scripts/run_baselines.py` và module tính các độ đo đánh giá đa lớp. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách toàn bộ module trong `src/data_pipeline/`: `deidentifier.py`, `temporal_aligner.py`, và `imputer.py`, đảm bảo tuân thủ tiêu chuẩn HIPAA và PROBAST. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & System):** Phụ trách viết bộ Unit Test `tests/test_data_pipeline.py` kiểm tra rò rỉ dữ liệu, xây dựng component `PatientDataForm.tsx` trên Next.js và mock API endpoint `/api/v1/predict/baseline`. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG TUẦN 3 (DEFINITION OF DONE)
Backlog 02 (Tuần 2) chỉ được xem là hoàn thành khi:
- [x] Chạy `pytest tests/test_data_pipeline.py -v` vượt qua 100% test cases (chứng minh không rò rỉ nhãn, không còn dữ liệu định danh, và dữ liệu khuyết được gán đầy đủ).
- [x] Module `src/models/baselines.py` khởi tạo được cả 3 lớp mô hình và chạy thử nghiệm forward pass thành công với dữ liệu mẫu (dummy batch).
- [x] Khung script `scripts/run_baselines.py` nhận tham số CLI, kiểm tra đủ `train/val/test.parquet`, và sẵn sàng nạp dữ liệu sạch.
- [x] Giao diện `PatientDataForm.tsx` trên Next.js nhập đủ 9 chỉ số, 4 biến phân loại và ghi chú; production build và API prediction contract đều vượt kiểm thử.

---

## 5. TỔNG KẾT NGHIỆM THU BACKLOG 02

Backlog 02 đã hoàn thành và sẵn sàng chuyển sang bước chia dữ liệu theo bệnh nhân ở Tuần 3:

- **Data & Privacy:** De-ID che các mẫu PHI tiếng Việt/Anh; temporal lock loại mọi sự kiện tại hoặc sau chẩn đoán và các biến tiêu chuẩn vàng; MICE chỉ xử lý 9 biến số và 4 biến phân loại, giữ nguyên ID/nhãn để ngăn rò rỉ outcome.
- **Modeling:** Có pipeline Random Forest/XGBoost/CatBoost, FT-Transformer số học và wrapper Bio_ClinicalBERT. Smoke test offline của ba nhánh đều trả tensor/xác suất kích thước `[batch, 4]`.
- **Evaluation:** Có Macro AUROC, Macro AUPRC, Macro F1, accuracy, multiclass Brier score và ECE, kèm xác thực shape/miền xác suất.
- **Application:** Form Next.js gọi `POST /api/v1/predict/baseline`; backend khử định danh ghi chú trước mock inference và trả đủ ba kết quả.
- **Automation:** `python scripts/run_baselines.py --help` mô tả CLI; `--smoke-test` cho phép kiểm tra kiến trúc trước khi `data/processed/train.parquet`, `val.parquet`, `test.parquet` được tạo ở Tuần 3.

### Lệnh nghiệm thu

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/run_baselines.py --smoke-test
cd frontend
npm.cmd run build
```

### Ranh giới bàn giao sang Tuần 3

Backlog này dựng khung và kiểm tra forward pass; chưa công bố chất lượng mô hình. Huấn luyện/benchmark chính thức chỉ thực hiện sau patient-level split để tránh một bệnh nhân xuất hiện ở nhiều tập. Text baseline Bio_ClinicalBERT dùng backbone huấn luyện chủ yếu trên ghi chú tiếng Anh, nên kết quả trên ghi chú tiếng Việt phải được báo cáo như một giới hạn thực nghiệm.
