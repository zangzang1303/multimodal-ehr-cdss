# Nhật Ký Thay Đổi Dự Án (Project Changelog)

Tất cả các thay đổi quan trọng trong dự án M-CDSS (Multimodal Clinical Decision Support System) sẽ được ghi nhận tại tệp này theo nguyên tắc trung thực khoa học và khả năng tái lập.

---

## [Phase 3 / Backlog 08] - 2026-11-18: Toàn Vẹn Khoa Học & Khả Năng Tái Lập (Integrity & Reproducibility)

### 1. Phân Tích Nguyên Nhân Gốc Của Sai Số $N = 287 / 286$ vs $N = 302$ (Root Cause Analysis)

Trong đợt rà soát ngày 2026-11-18 ([`docs/10_DANH_GIA_TONG_THE_VA_KE_HOACH_HOAN_THIEN.md`](docs/10_DANH_GIA_TONG_THE_VA_KE_HOACH_HOAN_THIEN.md)), nhóm phát hiện sự mâu thuẫn lớn giữa các báo cáo thực nghiệm Giai đoạn 2:
- Bảng Ablation Study (`data/ablation_results.json`) đo trên tập kiểm thử $N = 302$ (AUROC 0.959).
- Báo cáo phân tích công bằng (`data/fairness_report.json`) đo trên $N = 286$.
- Phân tích tiện ích lâm sàng và DCA (`data/benchmark_summary.json`, `data/evaluation_plots/clinical_utility_metrics.json`, `data/dca_curve.png`) đo trên $N = 287$ (AUROC 0.588).

**Nguyên nhân kỹ thuật đã xác minh:**
1. **Thiếu kiểm soát phiên bản đối với tệp Parquet:** Các tệp dữ liệu đã xử lý (`*.parquet`) được cấu hình trong `.gitignore` để tránh đưa dữ liệu lên Git. Tuy nhiên, nhóm chưa thiết lập cơ chế tệp kê khai kiểm soát toàn vẹn (Manifest File) kèm mã băm SHA-256. Do đó, giữa các máy của các thành viên tồn tại các phiên bản dữ liệu xử lý khác nhau.
2. **Khác biệt trong cơ chế sinh nhãn thô và phân chia nhóm (Splitting Discrepancy):**
   - Bộ dữ liệu chuẩn chính thức ban đầu được tạo với 2.000 bệnh nhân cân bằng tuyệt đối (500 ca mỗi nhóm bệnh). Khi phân chia bằng `StratifiedGroupKFold` trên cặp nhóm nguồn `(source_patient_group, source_note_group)`, việc các bệnh nhân cùng chia sẻ nhóm ghi chú làm cho kích thước tập test độc lập đạt $N = 302$ mẫu với phân bố lớp là `71 / 71 / 106 / 54`.
   - Một lần chạy lại kịch bản sinh dữ liệu `scripts/generate_synthetic_ehr.py` đã sử dụng phân bổ nhãn ngẫu nhiên đa thức (`random.choices`), dẫn đến phân bố nhãn bị lệch nhẹ (`483 / 504 / 512 / 501`). Khi đưa vào pipeline phân chia bệnh nhân thông thường, tập test bị co lại thành $N = 287$ (phân bố `69 / 72 / 74 / 72`) và tập val thành $N = 286$.
3. **Hiện tượng ghi đè Checkpoint và Fallback Silent Bert:**
   - Checkpoint `multimodal_best.pt` bị ghi đè bởi một lần chạy CPU có 0 epoch, đồng thời thiếu trọng số `Bio_ClinicalBERT` trên máy cục bộ dẫn đến fallback âm thầm sang mô hình ngẫu nhiên (`AutoModel.from_config`), khiến AUROC của mô hình trên tập $N = 287$ giảm mạnh xuống $\approx 0.58$.

---

### 2. Danh Sách Các Artefact Bị Ảnh Hưởng (Affected Artifacts)

Toàn bộ các artefact sau đây sinh ra từ tập test sai $N = 287$ hoặc checkpoint lỗi đã bị hủy hiệu lực:
- `data/benchmark_summary.json` (ghi nhận $N = 287$, AUROC 0.588 - Đã đánh dấu cần tái lập từ checkpoint mới).
- `data/evaluation_plots/clinical_utility_metrics.json` (ghi nhận $N = 287$ - Cần tái lập từ checkpoint mới).
- `data/evaluation_plots/dca_curve.png` & `data/dca_curve.png` (tính trên $N = 287$).
- `data/evaluation_plots/confusion_matrix.png` & `data/confusion_matrix.png` (tính trên $N = 287$).
- `data/evaluation_plots/calibration_curve.png` & `data/calibration_curve.png`.
- `data/fairness_report.json` (tính trên $N = 286$).

---

### 3. Biện Pháp Khắc Phục Triệt Để Của Thành Viên 2 (Remediation)

1. **Khôi phục bộ dữ liệu chuẩn duy nhất (Canonical Strict Dataset):**
   - Xây dựng lại `data/processed_rebuilt_strict/` với đúng $N = 2.000$ hồ sơ bệnh án (500 ca/nhóm bệnh), phân chia nghiệm ngặt:
     * **Train:** $N = 1.425$ (358 / 358 / 340 / 369)
     * **Val:** $N = 273$ (71 / 71 / 54 / 77)
     * **Test:** $N = 302$ (71 / 71 / 106 / 54)
   - Kiểm toán chống rò rỉ bệnh nhân và nhóm nguồn đạt $0\%$ (`scripts/audit_data_leakage.py`).
2. **Khóa dữ liệu bằng tệp kê khai `data/DATA_MANIFEST.json`:**
   - Lưu trữ mã băm SHA-256, số dòng, phân bố lớp và lệnh tái tạo cho cả 3 split.
   - Thêm module `src/data_pipeline/manifest.py::verify_manifest()`, bắt buộc mọi script thực nghiệm phải kiểm tra SHA-256 trước khi chạy.
3. **Nâng cấp công cụ khử định danh `ClinicalDeidentifier`:**
   - Khắc phục 100% tình trạng sót mã BHYT (`\b[A-Z]{2}\d{1,2}\d{10,13}\b`), học hàm/học vị bác sĩ Việt Nam (GS, PGS, TS, BS.CKII...), và tên bệnh viện viết HOA.
   - Đảm bảo giữ nguyên các thông số sinh hiệu (`BP`, `HR`, `SpO2`, `WBC`, `CRP`).
   - Tỷ lệ PHI còn sót trên cả 3 split đạt **$0.0\%$**.
4. **Chấm lại báo cáo nguy cơ sai lệch PROBAST+AI:**
   - Đánh giá trung thực nguy cơ sai lệch theo hướng dẫn của hội đồng khoa học (Participants: High, Predictors: Low/Unclear, Outcome: High, Analysis: Unclear).
