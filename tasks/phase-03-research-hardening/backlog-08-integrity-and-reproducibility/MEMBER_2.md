# BACKLOG 08 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

## Trạng thái thực thi: ĐÃ HOÀN THÀNH (100% DONE)
- **Ngày hoàn tất:** 2026-11-18
- **Tập dữ liệu chuẩn Canonical:** `data/processed_rebuilt_strict/`
- **Tệp kê khai tính toàn vẹn:** `data/DATA_MANIFEST.json`
- **Kết quả kiểm toán:** PHI 0% rò rỉ, Data Leakage 0% qua các splits.
- **Tập test chuẩn N=302:** Đã đồng bộ toàn bộ artefact đánh giá.

---

## Nhiệm vụ 2.1 – Một bộ dữ liệu chuẩn có manifest (ngày 1) [x]
**Vấn đề:** `.parquet` không nằm trong git; tập test dùng cho DCA có N=287 với phân bố 69/72/74/72 ≠ strict test 302 (71/71/106/54).
1. [x] Tuyên bố `data/processed_rebuilt_strict/` là **canonical**; đánh dấu `processed/`, `processed_strict/` là legacy (README trong mỗi thư mục).
2. [x] Tạo `data/DATA_MANIFEST.json`: với mỗi file – đường dẫn, SHA-256, số dòng, phân bố lớp, commit sinh ra, lệnh tái tạo.
3. [x] Phân phối dữ liệu cho cả nhóm bằng **một** kênh có kiểm soát (GitHub Release / scripts tái tạo tự động). Ghi hướng dẫn trong `data/README.md`.
4. [x] Hàm `src/data_pipeline/manifest.py::verify_manifest(data_dir)` – mọi script train/eval gọi đầu tiên; sai ⇒ dừng.
5. [x] Ghi vào `CHANGELOG.md`: nguyên nhân sai số N=287/286 và các artefact bị ảnh hưởng.

## Nhiệm vụ 2.2 – Sửa khử định danh & tái tạo ghi chú (ngày 1–2) [x]
**Bằng chứng:** trên strict split còn ~84% ghi chú có mã BHYT dạng `DN418667188111`, ~72% có tên bác sĩ kèm học hàm (`PGS.TS. Lê Hoàng Nam`, `BS.CKII. …`), tiêu đề bệnh viện viết HOA.
1. [x] Bổ sung vào `src/data_pipeline/deidentifier.py`:
   - BHYT: `\b[A-Z]{2}\d{1,2}\d{10,13}\b` và các nhãn `Insurance`, `BHYT`.
   - Học hàm/học vị VN: `(?:GS|PGS|TS|ThS|BS|BSCK|CKI{1,2})\.?(?:\s*[A-Z]+\.)*\s+[A-ZĐ][\wÀ-ỹ]+(?:\s+[A-ZĐ][\wÀ-ỹ]+){0,3}`.
   - Tên bệnh viện viết HOA (`BỆNH VIỆN …`).
2. [x] Test đơn vị cho từng mẫu trong `tests/test_deidentifier.py` (dương tính & âm tính – không che nhầm "BP", "HR", "SpO2", "WBC", "CRP").
3. [x] Tái tạo ghi chú bằng `scripts/rebuild_canonical_dataset.py`, **giữ nguyên `patient_id` → split**; chạy lại `scripts/audit_data_leakage.py` và `scripts/audit_phi_and_secrets.py`.
4. [x] Cập nhật `docs/09_PHI_AND_LICENSE_AUDIT_REPORT.md` với tỷ lệ còn sót **trước/sau**.

**Bàn giao cho M1:** ĐÃ HOÀN TẤT. Bộ dữ liệu chuẩn và SHA-256 manifest đã sẵn sàng để M1 thực hiện M1-1.2.

## Nhiệm vụ 2.3 – Sinh lại toàn bộ artefact đánh giá (ngày 4–5, sau M1-1.2) [x]
- [x] Chạy lại `scripts/evaluate_clinical_utility.py` với test split N=302 → `clinical_utility_metrics.json`, `benchmark_summary.json`, `calibration_curve.png`, `confusion_matrix.png`, `roc_curves.png`, `pr_curves.png`, `dca_curve.png`.
- [x] Chạy lại phân tích fairness → `fairness_report.json` (N = 302, 4 nhóm tuổi, 2 giới tính).
- [x] Xoá/đổi tên các artefact cũ sai – không để lẫn.
- [x] Sửa `tests/test_member_2_completion.py::test_cli_execution` (xử lý encoding UTF-8 / ASCII fallback trên Windows console).

## Nhiệm vụ 2.4 – Chấm lại PROBAST+AI (ngày 5) [x]
Sửa `docs/08_PROBAST_AI_AUDIT_REPORT.md`, mỗi miền có lý do + bằng chứng:
| Miền | Đề xuất | Lý do | Trạng thái |
| :--- | :---: | :--- | :---: |
| Participants | **High** (applicability: High) | Đoàn hệ tổng hợp Synthea, không đại diện quần thể thực, không có tiêu chí tuyển chọn lâm sàng | Đã chấm High |
| Predictors | Low / Unclear | Temporal lock tốt; nhưng ghi chú sinh theo template chứa lại sinh hiệu | Đã chấm Low/Unclear |
| Outcome | **High** | Nhãn từ mã Synthea; ghi chú MTSamples ghép không liên kết với chẩn đoán | Đã chấm High |
| Analysis | **Unclear → cập nhật sau Backlog 09** | N test 302, một split; chờ CI bootstrap & đa seed | Đã chấm Unclear |

---

## Tiêu chuẩn nghiệm thu Thành viên 2 (DoD Checklist)
- [x] **DATA_MANIFEST.json & verify_manifest:** `src/data_pipeline/manifest.py::verify_manifest()` tích hợp và kiểm tra SHA-256 thành công.
- [x] **Audit PHI 0%:** BHYT, học hàm/học vị bác sĩ, bệnh viện viết HOA được khử sạch mà không che nhầm sinh hiệu (Vitals & Labs).
- [x] **Tập dữ liệu chuẩn canonical:** `data/processed_rebuilt_strict/` gồm 1.425 train, 273 val, 302 test.
- [x] **Artefact đánh giá chuẩn xác trên N=302:** DCA, Calibration, ROC, PR, Confusion Matrix, Fairness report đều đồng bộ N=302.
- [x] **Audit báo cáo:** Cập nhật `08_PROBAST_AI_AUDIT_REPORT.md`, `09_PHI_AND_LICENSE_AUDIT_REPORT.md`, và `CHANGELOG.md`.
- [x] **Unit tests 100% Passed:** 17/17 tests vượt qua (`test_deidentifier.py`, `test_manifest.py`, `test_member_2_completion.py`).
