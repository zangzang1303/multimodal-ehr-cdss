# BACKLOG 06 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Ma Trận Nhầm Lẫn, Error Analysis, Tự Động Hóa Evaluation & Khảo Sát Bác Sĩ

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Ma Trận Nhầm Lẫn & Phân Tích Ca Bệnh Sai Biệt (Error Analysis)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Vẽ biểu đồ ma trận nhầm lẫn (Confusion Matrix) đa lớp cho 4 bệnh lý (Hen, COPD, Suy tim, Viêm phổi) trên tập Test, lưu tại `data/confusion_matrix.png`.
  2. Lọc danh sách các ca bệnh dự đoán sai: Phân tích nguyên nhân lâm sàng (ví dụ: ca bệnh chồng lấp Hen-COPD có hút thuốc lá, hoặc ca suy tim giai đoạn đầu có ran rít giống hen phế quản) để cung cấp luận chứng cho bài báo khoa học.
* **Đầu ra (Deliverable):** 
  - `data/confusion_matrix.png` (Hình ảnh độ phân giải cao 300 DPI, hiển thị số ca và tỷ lệ %)
  - `docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md` (Tài liệu mổ xẻ 3 cụm ca sai biệt và 2 hồ sơ bệnh án điển hình `PT-0025`, `PT-0201`).
* **Đầu ra (Deliverable):** `data/confusion_matrix.png`, tài liệu phân tích ca bệnh sai biệt.
* **Trạng thái:** `[x] DONE`

> 💬 **GHI CHÚ PHỐI HỢP CHO THÀNH VIÊN KHÁC (HANDOFF & OVERRIDE):**
> * **Thành viên 1 (Lead ML / Modeling):** 
>   - Bổ sung / trích dẫn bảng số liệu ma trận nhầm lẫn 4x4 từ `docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md` vào mục *Results & Discussion* của bài báo khoa học.
>   - Đối chiếu sự phân tầng giữa 3 Baseline (CatBoost, FT-Transformer, Bio_ClinicalBERT) với M-CDSS để làm nổi bật luận điểm vì sao multimodal giải quyết được ca bệnh thiếu hụt cận lâm sàng hoặc văn bản ngắn.
> * **Thành viên 3 (Full-Stack AI & Frontend):** 
>   - Sử dụng các ca bệnh ranh giới trích xuất tại Mục 3 trong tài liệu `docs/06_...` làm dữ liệu mẫu (mock clinical cases) phục vụ kiểm thử tính năng giải thích ca bệnh (`/agent/explain`) và hiển thị thẻ cảnh báo rủi ro trên Web UI.

---

### 🔹 Nhiệm vụ 2.2: Tự Động Hóa Kịch Bản Đánh Giá Lâm Sàng
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Viết script `scripts/evaluate_clinical_utility.py`:
  - Nạp checkpoint, preprocessing và tập strict test từ `data/processed_rebuilt_strict/test.parquet`; kiểm tra audit/provenance trước đánh giá.
  - Tính toán toàn bộ các chỉ số phân biệt (AUROC, AUPRC, F1), chỉ số hiệu chuẩn (ECE, Brier) và lợi ích ròng (DCA).
  - Xuất toàn bộ biểu đồ ảnh (ROC curves, PR curves, DCA curve, Calibration curve) vào thư mục `data/evaluation_plots/`.
* **Lệnh chạy chuẩn hóa:**
* **Lệnh chạy:**
  ```bash
  python scripts/evaluate_clinical_utility.py --model_path data/checkpoints/multimodal_best.pt --test_data data/processed_rebuilt_strict/test.parquet --output_plots data/evaluation_plots/
  ```
* **Đầu ra (Deliverable):** 
  - `scripts/evaluate_clinical_utility.py`: Script tự động hóa toàn diện quy trình đánh giá lâm sàng.
  - `src/evaluation/dca_analysis.py`: Module tính toán đường cong DCA Net Benefit và Treat All / Treat None.
  - `data/evaluation_plots/`:
    - `confusion_matrix.png` & `data/confusion_matrix.png`
    - `roc_curves.png` (Multiclass One-vs-Rest ROC)
    - `pr_curves.png` (Multiclass Precision-Recall)
    - `dca_curve.png` & `data/dca_curve.png` (Net Benefit minh họa trên tập kiểm thử)
    - `calibration_curve.png` (Reliability Diagram 10 bins, Calibrated vs Uncalibrated)
    - `clinical_utility_metrics.json` (Số liệu đo lường đầy đủ đa chiều)
  - `data/benchmark_summary.json` (Bản tóm tắt chỉ số phục vụ API backend).
* **Đầu ra (Deliverable):** `scripts/evaluate_clinical_utility.py`.
* **Trạng thái:** `[x] DONE`

> 💬 **GHI CHÚ PHỐI HỢP CHO THÀNH VIÊN KHÁC (HANDOFF & OVERRIDE):**
> * **Thành viên 1 (Lead ML / Modeling):** 
>   - Thành viên 2 đã dựng sẵn khung nền tảng `src/evaluation/dca_analysis.py` để không làm nghẽn tiến độ. Thành viên 1 **cần ghi đè (override) hoặc bổ sung** thêm:
>     1. Tính khoảng tin cậy 95% Bootstrap (95% CI) cho Net Benefit theo nhóm nguồn bệnh nhân.
>     2. So sánh đường cong DCA của M-CDSS với 3 mô hình Baseline (CatBoost, FT-Transformer, Bio_ClinicalBERT) trên cùng một biểu đồ nếu cần thiết cho bài báo.
>     3. Bổ sung báo cáo kiểm định ngoại kiểm (External Validation / Temporal Split) theo nhiệm vụ 1.3.
> * **Thành viên 3 (Full-Stack AI & Frontend):** 
>   - Tích hợp dữ liệu từ `data/benchmark_summary.json` và `data/evaluation_plots/clinical_utility_metrics.json` vào route `GET /api/v1/evaluation/benchmark` trong `src/api/routes/evaluation_routes.py`.
>   - Sử dụng mảng dữ liệu `dca_curve_sample_points` (hoặc `dca_table`) để vẽ biểu đồ tương tác Recharts / Chart.js trên giao diện bác sĩ (Nhiệm vụ 3.2).
>   - Cần bổ sung xử lý biệt lệ (Graceful degradation / Error handling) khi các file json/png chưa được sinh ra.

---

### 🔹 Nhiệm vụ 2.3: Tổ Chức Khảo Sát Đánh Giá Định Tính Với Bác Sĩ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** 
  1. Xây dựng phiếu khảo sát lâm sàng (Likert Scale 1-5):
     - Mức độ chính xác của dự đoán sơ bộ.
     - Tính thuyết phục của các câu chứng cứ được highlight trong bệnh án.
     - Tính hữu ích của việc trích dẫn phác đồ GINA/GOLD/ESC.
  2. Xác định nguồn ca, quyền sử dụng, cách chọn mẫu, người đánh giá, cách làm mù và thủ tục cần thiết trước khi mời tham gia. Ca tổng hợp phải được ghi là ca tổng hợp.
  3. Nếu tuyển được người tham gia, báo cáo số bác sĩ/ca và kết quả thực; nếu chưa, nộp giao thức và ghi khảo sát chưa thực hiện.
* **Đầu ra (Deliverable):** 
  - `docs/07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md`: Giao thức nghiên cứu chuẩn mực, phương pháp chọn mẫu phân tầng 20 ca bệnh, thiết kế làm mù đôi (Double-blind) và phiếu khảo sát thang đo Likert 1-5 gồm 9 câu hỏi định lượng kèm câu hỏi mở.
  - Báo cáo thực trạng: Đã ghi nhận minh bạch khảo sát với bác sĩ thực tế **CHƯA THỰC HIỆN (Pending Clinician Enrollment & IRB Approval)**, tuân thủ nghiêm ngặt chuẩn TRIPOD+AI / PROBAST (tuyệt đối không bịa đặt số liệu khảo sát).
* **Đầu ra (Deliverable):** Giao thức/phiếu khảo sát và báo cáo kết quả nếu có dữ liệu thật từ người đánh giá.
* **Trạng thái:** `[x] DONE`

> 💬 **GHI CHÚ PHỐI HỢP CHO THÀNH VIÊN KHÁC (HANDOFF & OVERRIDE):**
> * **Thành viên 1 (Lead ML / Modeling):** 
>   - Tham khảo các câu hỏi định tính trong phiếu khảo sát (đặc biệt là tiêu chí Q1.3 về khả năng xử lý ca bệnh chồng lấp) để chuẩn bị kịch bản phản biện (rebuttal) cho các reviewer y khoa.
> * **Thành viên 3 (Full-Stack AI & Frontend):** 
>   - Có thể dựa trên mẫu phiếu khảo sát Likert 1-5 tại Mục 4 của `docs/07_...` để xây dựng component `DoctorFeedbackModal` trên Frontend, cho phép bác sĩ lâm sàng khi trải nghiệm bản demo có thể gửi đánh giá phản hồi trực tiếp về cơ sở dữ liệu.

---

## 2. TỔNG HỢP TIẾN ĐỘ THÀNH VIÊN 2 (MEMBER 2 SUMMARY)
- [x] **2.1: Ma trận nhầm lẫn & Error Analysis:** Đã xuất `data/confusion_matrix.png` và hoàn thành tài liệu `docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md`.
- [x] **2.2: Tự động hóa kịch bản đánh giá:** Đã viết `scripts/evaluate_clinical_utility.py`, chạy thực nghiệm thành công, sinh toàn bộ đồ thị `data/evaluation_plots/` và các file chỉ số JSON.
- [x] **2.3: Giao thức & Phiếu khảo sát bác sĩ:** Đã ban hành `docs/07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md` kèm báo cáo thực trạng minh bạch theo chuẩn TRIPOD+AI.
