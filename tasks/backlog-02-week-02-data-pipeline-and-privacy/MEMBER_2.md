# BACKLOG 02 (TUẦN 2) - NHIỆM VỤ THÀNH VIÊN 2 (BIOMEDICAL DATA & PRIVACY)
### Trọng Tâm: Triển Khai Bộ Ba Pipeline Bảo Mật PHI, Khóa Thời Gian & Gán Khuyết MICE

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 2 của Giai đoạn 1, Thành viên 2 gánh vác trọng trách cốt tử nhất về phương pháp luận: hiện thực bộ ba module dữ liệu y sinh tại `src/data_pipeline/` nhằm giải quyết dứt điểm các vấn đề mà bài báo JMIR (*Hunik et al., 2024*) đã chỉ ra: rò rỉ thông tin cá nhân (vi phạm HIPAA), rò rỉ nhãn do mất đồng bộ thời gian (Target Leakage), và thiên lệch mẫu do xóa dữ liệu khuyết.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Xây Dựng Pipeline Khử Định Danh PHI (`src/data_pipeline/deidentifier.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Hiện thực lớp `ClinicalDeidentifier` kết hợp cơ chế lai (Hybrid De-ID Engine) tuân thủ 18 tiêu chuẩn HIPAA Safe Harbor:
  1. **Regex Engine:** Xây dựng các mẫu biểu thức chính quy tối ưu để phát hiện:
     - Số Căn cước công dân / Định danh (9 - 12 chữ số).
     - Số điện thoại Việt Nam (`+84` hoặc đầu số `03, 05, 07, 08, 09`).
     - Mã thẻ Bảo hiểm y tế (BHYT) và Mã hồ sơ bệnh án (MRN).
     - Địa chỉ Email.
     - Các định dạng ngày tháng: `DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YY`, v.v.
  2. **Biomedical NER Engine:** Tích hợp `spaCy` nạp mô hình `en_core_web_sm` (hoặc `en_ner_bc5cdr_md` / `presidio-analyzer`) để nhận diện thực thể tên riêng:
     - `PERSON`: Tên bệnh nhân, người nhà, tên bác sĩ khám.
     - `ORG` / `FACILITY`: Tên bệnh viện, trạm y tế, phòng khám.
     - `GPE` / `LOC`: Địa chỉ nhà, tên tỉnh/thành phố, quận/huyện.
  3. **Surrogate Token Replacement:** Thay thế toàn bộ thực thể nhạy cảm bằng các token ngữ cảnh: `[REDACTED_NAME]`, `[REDACTED_DATE]`, `[REDACTED_HOSPITAL]`, `[REDACTED_PHONE]`, `[REDACTED_ID]` nhằm giữ trọn vẹn ngữ nghĩa ngữ pháp cho Text Encoder.
* **Đầu ra (Deliverables):**
  - `src/data_pipeline/deidentifier.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Khóa Chuỗi Thời Gian & Chống Rò Rỉ Nhãn (`src/data_pipeline/temporal_aligner.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Hiện thực lớp `TemporalAligner` nhằm kiểm soát nghiêm ngặt nguy cơ sai lệch theo chuẩn PROBAST:
  1. **Khóa mốc thời gian chẩn đoán (Time-Locking):**
     - Tiếp nhận mốc thời gian xác lập chẩn đoán của bác sĩ: $t_{diag} =$ `diagnostic_confirmed_timestamp`.
     - Lọc bỏ triệt để mọi sự kiện lâm sàng, ghi chú diễn tiến hoặc kết quả cận lâm sàng có mốc thời gian phát sinh:
       $$t_{event} \ge t_{diag}$$
  2. **Danh sách đen tiêu chuẩn vàng (Gold-Standard Blacklist):**
     - Tự động kiểm tra và loại bỏ khỏi tập biến đầu vào các xét nghiệm đóng vai trò tiêu chuẩn vàng xác định bệnh:
       - ❌ Loại bỏ Hô hấp ký / Phế dung kế: `fev1`, `fvc`, `fev1_fvc_ratio` (tiêu chuẩn vàng COPD/Hen).
       - ❌ Loại bỏ Siêu âm tim: `lvef`, `ef` (tiêu chuẩn vàng suy tim theo ESC).
       - ❌ Loại bỏ Kết quả cấy đờm vi khuẩn (tiêu chuẩn vàng viêm phổi).
     - Nếu phát hiện bất kỳ biến nào trong blacklist lọt vào dữ liệu đầu vào, hàm phải phát tín hiệu cảnh báo hoặc loại bỏ tự động kèm log cảnh báo.
* **Đầu ra (Deliverables):**
  - `src/data_pipeline/temporal_aligner.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Xử Lý Dữ Liệu Khuyết Bằng MICE (`src/data_pipeline/imputer.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Hiện thực lớp `ClinicalImputer` áp dụng kỹ thuật gán khuyết đa biến MICE (*Multiple Imputation by Chained Equations*):
  1. Sử dụng `sklearn.impute.IterativeImputer` với `estimator=BayesianRidge()` cho 9 biến số liên tục, lặp qua 10 chu kỳ chuỗi hồi quy (`max_iter=10, random_state=42`).
  2. Sử dụng `SimpleImputer(strategy='most_frequent')` cho các biến phân loại bị thiếu.
  3. **Tạo cột Binary Missingness Indicator:** Với mỗi biến số $Y_j$, tự động tạo cột nhị phân đi kèm $Y_j\text{\_is\_missing} \in \{0, 1\}$ để giữ lại tín hiệu lâm sàng quan trọng (ví dụ: việc bác sĩ không chỉ định thử CRP phản ánh bác sĩ không nghi ngờ nhiễm trùng).
  4. Xuất báo cáo tỷ lệ missingness của từng feature trước và sau khi gán.
* **Đầu ra (Deliverables):**
  - `src/data_pipeline/imputer.py`.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 2 (ACCEPTANCE CRITERIA)
- [ ] Chạy thử nghiệm `deidentifier.py` trên 100 câu bệnh án thô: 100% tên người, số điện thoại, ngày khám, CCCD được che bằng token chuẩn.
- [ ] Thử nghiệm `temporal_aligner.py` với ca bệnh giả định có kết quả sau $t_{diag}$: xác nhận kết quả bị loại bỏ thành công.
- [ ] Thử nghiệm `imputer.py` trên bảng có 25% NaN: bảng sau gán không còn bất kỳ giá trị NaN nào, các cột `_is_missing` được tạo đầy đủ.
- [ ] Bàn giao 3 module cho Thành viên 3 để tích hợp vào bộ Unit Tests tự động.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 2
1. **Quy định Khử Định Danh Y Tế Chuẩn HIPAA:**
   * *U.S. Department of Health and Human Services (HHS):* "Guidance Regarding Methods for De-identification of Protected Health Information in Accordance with the Health Insurance Portability and Accountability Act (HIPAA) Privacy Rule." [hhs.gov/hipaa](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html).
   * *Trọng tâm cần đọc:* 18 tiêu chuẩn nhận dạng cá nhân cần che giấu (Mục 1.1 trong [`docs/03_DATA_PIPELINE_AND_PRIVACY.md`](../../docs/03_DATA_PIPELINE_AND_PRIVACY.md)).
2. **Kiểm Soát Rò Rỉ Nhãn Theo Chuẩn PROBAST:**
   * *Wolff, R. F. et al. (2019).* "PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies." *Annals of Internal Medicine*, 170(1), 51-58. [doi:10.7326/M18-1376](https://www.acpjournals.org/doi/10.7326/M18-1376).
   * *Trọng tâm cần đọc:* Domain 2 (Predictors - câu hỏi 2.1 & 2.2 về việc cấm đưa xét nghiệm tiêu chuẩn vàng FEV1, EF vào biến đầu vào) và Domain 3 (Outcome - thời điểm xác lập chẩn đoán).
3. **Lý Thuyết Thuật Toán Gán Khuyết Đa Biến (MICE):**
   * *van Buuren, S., & Groothuis-Oudshoorn, K. (2011).* "mice: Multivariate Imputation by Chained Equations in R." *Journal of Statistical Software*, 45(3), 1-67. [doi:10.18637/jss.v045.i03](https://doi.org/10.18637/jss.v045.i03).
   * *Trọng tâm cần đọc:* Cơ chế lặp chuỗi hồi quy Bayesian Ridge qua 10 chu kỳ và bảo toàn tín hiệu lâm sàng bằng Binary Missingness Indicator.
4. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.3, Mục 2.4 và Mục 2.5).

