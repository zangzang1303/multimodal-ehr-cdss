# BACKLOG 08: TOÀN VẸN KHOA HỌC & KHẢ NĂNG TÁI LẬP
### Giai đoạn 3 – Tuần 1 | Mục tiêu: mọi con số có thể truy ngược về đúng dữ liệu, đúng checkpoint, đúng code

---

## 1. VÌ SAO CẦN BACKLOG NÀY
Rà soát 2026-11-18 (xem [docs/10](../../../docs/10_DANH_GIA_TONG_THE_VA_KE_HOACH_HOAN_THIEN.md)) cho thấy:
- `multimodal_best.pt` bị ghi đè bởi lần chạy 0 epoch; DCA/benchmark/fairness tính trên mô hình AUROC 0,58 và tập test N=287 thay vì strict test N=302.
- Ba nơi âm thầm dùng **BERT khởi tạo ngẫu nhiên** khi thiếu trọng số.
- Dữ liệu `.parquet` không được quản lý phiên bản → mỗi máy một dữ liệu.
- `/agent/explain` lỗi; `/predict/baseline` gán cứng kết quả case study.
- ~84% ghi chú còn mã BHYT, ~72% còn tên bác sĩ.
- `pytest`: 13 failed, 2 errors.

## 2. THỨ TỰ PHỤ THUỘC (QUAN TRỌNG)
```
M2-2.1 Chốt dữ liệu chuẩn + manifest ─┐
M2-2.2 Sửa de-ID & tái tạo ghi chú ───┼─► M1-1.2 Huấn luyện lại (5 seed) ─► M2-2.3 Sinh lại DCA/fairness/confusion
M1-1.1 Chặn fallback BERT ngẫu nhiên ─┘          └─► M1-1.3 Baseline lưu dự đoán ─► M1-1.4 Results registry
M3-3.1..3.4 làm song song ngay từ ngày 1
```
Sửa de-ID (2.2) làm thay đổi văn bản ⇒ **phải xong trước** khi huấn luyện lại. Giữ nguyên phân công bệnh nhân vào train/val/test (cùng `patient_id` → cùng split).

## 3. PHÂN CÔNG
* 🧬 **Thành viên 1:** chặn fallback, bảo vệ checkpoint, huấn luyện lại đa seed, lưu dự đoán từng mẫu, results registry. 👉 [MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2:** dữ liệu chuẩn có manifest, sửa khử định danh, sinh lại toàn bộ artefact đánh giá, sửa PROBAST. 👉 [MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3:** sửa `/agent/explain` và test, gỡ mock gán cứng, dọn header "MOCK", CI GitHub Actions, pin phiên bản Docker. 👉 [MEMBER_3.md](MEMBER_3.md)

## 4. DEFINITION OF DONE
- [ ] `pytest tests/` **100% pass** trên máy sạch (và trên CI).
- [ ] `data/DATA_MANIFEST.json` tồn tại; mọi script train/eval từ chối chạy khi SHA-256/số dòng không khớp. Strict test = **302** mẫu (71/71/106/54).
- [ ] Không còn đường code nào khởi tạo text backbone ngẫu nhiên ngoài test unit có cờ rõ ràng.
- [ ] `multimodal_best.pt` có `epochs_total > 0`, `backbone_revision`, `data_manifest_sha`; tái tạo AUROC cross-attention trong ±0,01 so với giá trị đã báo cáo (hoặc giải thích chênh lệch).
- [ ] `data/predictions/*.npz` cho mọi mô hình × seed (val + test).
- [ ] `results/registry.json` là nguồn duy nhất; `benchmark_summary.json`, `clinical_utility_metrics.json`, `fairness_report.json`, `dca_curve.png` được sinh lại từ checkpoint mới.
- [ ] Audit PHI: 0% mã BHYT/tên bác sĩ còn sót trên cả 3 split.
- [ ] Không còn kết quả gán cứng trong bất kỳ endpoint nào frontend gọi.
- [ ] `docs/08_PROBAST_AI_AUDIT_REPORT.md` được chấm lại có lý do cho từng miền.
