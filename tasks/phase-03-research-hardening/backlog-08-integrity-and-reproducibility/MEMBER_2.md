# BACKLOG 08 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

## Nhiệm vụ 2.1 – Một bộ dữ liệu chuẩn có manifest (ngày 1)
**Vấn đề:** `.parquet` không nằm trong git; tập test dùng cho DCA có N=287 với phân bố 69/72/74/72 ≠ strict test 302 (71/71/106/54).
1. Tuyên bố `data/processed_rebuilt_strict/` là **canonical**; đánh dấu `processed/`, `processed_strict/` là legacy (README trong mỗi thư mục).
2. Tạo `data/DATA_MANIFEST.json`: với mỗi file – đường dẫn, SHA-256, số dòng, phân bố lớp, commit sinh ra, lệnh tái tạo.
3. Phân phối dữ liệu cho cả nhóm bằng **một** kênh có kiểm soát (Git LFS, DVC, hoặc GitHub Release asset riêng tư). Ghi hướng dẫn trong `data/README.md`.
4. Hàm `src/data_pipeline/manifest.py::verify_manifest(data_dir)` – mọi script train/eval gọi đầu tiên; sai ⇒ dừng.
5. Ghi vào CHANGELOG: nguyên nhân sai số N=287/286 và các artefact bị ảnh hưởng.

## Nhiệm vụ 2.2 – Sửa khử định danh & tái tạo ghi chú (ngày 1–2)
**Bằng chứng:** trên strict split còn ~84% ghi chú có mã BHYT dạng `DN418667188111`, ~72% có tên bác sĩ kèm học hàm (`PGS.TS. Lê Hoàng Nam`, `BS.CKII. …`), tiêu đề bệnh viện viết HOA.
1. Bổ sung vào `src/data_pipeline/deidentifier.py`:
   - BHYT: `\b[A-Z]{2}\d{1,2}\d{10,13}\b` và các nhãn `Insurance`, `BHYT`.
   - Học hàm/học vị VN: `(?:GS|PGS|TS|ThS|BS|BSCK|CKI{1,2})\.?(?:\s*[A-Z]+\.)*\s+[A-ZĐ][\wÀ-ỹ]+(?:\s+[A-ZĐ][\wÀ-ỹ]+){0,3}`.
   - Tên bệnh viện viết HOA (`BỆNH VIỆN …`).
2. Test đơn vị cho từng mẫu (dương tính & âm tính – không che nhầm "BP", "HR").
3. Tái tạo ghi chú, **giữ nguyên `patient_id` → split**; chạy lại `scripts/audit_data_leakage.py` và `scripts/audit_phi_and_secrets.py`.
4. Cập nhật `docs/09_PHI_AND_LICENSE_AUDIT_REPORT.md` với tỷ lệ còn sót **trước/sau**.

**Bàn giao cho M1** ngay khi xong (M1-1.2 phụ thuộc).

## Nhiệm vụ 2.3 – Sinh lại toàn bộ artefact đánh giá (ngày 4–5, sau M1-1.2)
- Chạy lại `scripts/evaluate_clinical_utility.py` với checkpoint mới → `clinical_utility_metrics.json`, `benchmark_summary.json`, `calibration_curve.png`, `confusion_matrix.png`, `roc/pr_curves.png`, `dca_curve.png`.
- Chạy lại phân tích fairness → `fairness_report.json` (N phải = 302).
- Xoá/đổi tên các artefact cũ sai (`*_INVALID_2026-11-17.json`) – không để lẫn.
- Sửa `tests/test_member_2_completion.py::test_cli_execution` (lỗi mã hoá ký tự `✓` trên Windows – đặt `PYTHONIOENCODING=utf-8` hoặc so khớp ASCII).

## Nhiệm vụ 2.4 – Chấm lại PROBAST+AI (ngày 5)
Sửa `docs/08_PROBAST_AI_AUDIT_REPORT.md`, mỗi miền có lý do + bằng chứng:
| Miền | Đề xuất | Lý do |
| :--- | :---: | :--- |
| Participants | **High** (applicability: High) | Đoàn hệ tổng hợp Synthea, không đại diện quần thể thực, không có tiêu chí tuyển chọn lâm sàng |
| Predictors | Low / Unclear | Temporal lock tốt; nhưng ghi chú sinh theo template chứa lại sinh hiệu |
| Outcome | **High** | Nhãn từ mã Synthea; ghi chú MTSamples ghép không liên kết với chẩn đoán |
| Analysis | **Unclear → cập nhật sau Backlog 09** | N test 302, một split; chờ CI bootstrap & đa seed |

**Nghiệm thu Thành viên 2:** manifest + verify chạy trong mọi script; audit PHI 0%; artefact đánh giá N=302; PROBAST có lý do từng miền.
