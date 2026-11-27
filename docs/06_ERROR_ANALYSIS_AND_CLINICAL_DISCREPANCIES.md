# PHÂN TÍCH LỖI & SAI BIỆT LÂM SÀNG (ERROR ANALYSIS)
### Mô hình triển khai: cross-attention (BERT đóng băng), seed 101 – tập test strict N = 302

> Cập nhật 2026-11-23 (Thành viên 1, Phase 3). Bản trước (2026-11-19) phân tích một mô hình fusion khác, huấn luyện trên bộ dữ liệu bị rò rỉ nhãn – đã thu hồi, xem `data/legacy_invalid_2026-11-19/README.md`.
> Số liệu đầy đủ, máy đọc được: `results/registry.json → error_analysis` (30 ca nhầm lẫn có độ tin cậy cao nhất, ma trận nhầm lẫn, case study). Hình: `data/evaluation_plots/fig_confusion_matrix.png`.

---

## 1. Ma trận nhầm lẫn (xác suất đã hiệu chuẩn, argmax)

| Thực tế \ Dự đoán | ASTHMA | COPD | HEART_FAILURE | PNEUMONIA | Sai / tổng |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **ASTHMA** | 61 | 9 | 0 | 1 | 10 / 71 |
| **COPD** | 9 | 61 | 1 | 0 | 10 / 71 |
| **HEART_FAILURE** | 0 | 0 | 106 | 0 | 0 / 106 |
| **PNEUMONIA** | 35 | 1 | 6 | 12 | 42 / 54 |

Tổng 62 lỗi / 302 bản ghi (accuracy 0,795).

## 2. Phát hiện chính: lỗi tập trung ở **một bệnh nhân gốc**

| Phát hiện | Bằng chứng | Hệ quả |
| :--- | :--- | :--- |
| 42/62 lỗi thuộc **một** bệnh nhân Synthea gốc (toàn bộ 54 bản ghi viêm phổi trong test là các lần khám của người này) | `source_patient_group` của các ca sai | Độ chính xác của lớp viêm phổi trên test thực chất là kết quả trên **1 bệnh nhân** |
| Lớp suy tim đúng 106/106 – cũng chỉ **một** bệnh nhân gốc | `data_provenance` trong registry | Hiệu năng hoàn hảo của lớp này không có ý nghĩa thống kê |
| Bệnh nhân viêm phổi trong test ~82 tuổi, trong khi viêm phổi ở tập train tập trung quanh 100 tuổi (tuổi bị chặn trên [18; 100] khi chuyển đổi từ Synthea) | Bảng 1 của bài báo (`generated/tab_cohort.tex`) | Mô hình học **lối tắt tuổi** (“viêm phổi ≈ 100 tuổi”) ⇒ nhầm bệnh nhân viêm phổi 82 tuổi thành hen |
| Hen ↔ COPD (18 lỗi) phân tán trên nhiều bệnh nhân gốc | 8 bệnh nhân hen, 56 bệnh nhân COPD trong test | Nhóm lỗi duy nhất phản ánh vùng chồng lấp sinh hiệu giữa nhiều bệnh nhân – tương ứng vùng chồng lấp hen–COPD (ACOS) trên lâm sàng, nơi phân biệt cần hô hấp ký và test hồi phục phế quản (không có trong dữ liệu đầu vào) |
| Ghi chú dạng MTSamples có tỷ lệ lỗi thấp hơn ghi chú template (11,8% so với 22,3%) | phân tích theo loại ghi chú | Ghi chú template ngắn, giống nhau, ít thông tin ngoài các con số |

## 3. Phân loại nguyên nhân (áp dụng cho 30 ca có độ tin cậy cao nhất trong registry)

1. **Lối tắt nhân khẩu học / bệnh nhân gốc (Shortcut – demographic / source-patient):** dự đoán dựa vào tuổi hoặc “dấu vân tay” của một bệnh nhân Synthea lặp lại nhiều lần. Chiếm phần lớn lỗi (cặp PNEUMONIA → ASTHMA).
2. **Chồng lấn sinh hiệu (Overlapping vitals):** hen và COPD có SpO₂, nhịp thở, CRP trong cùng vùng giá trị.
3. **Nhãn tổng hợp mâu thuẫn (Synthetic label discrepancy):** nhãn lấy từ mã điều kiện Synthea của lần khám, phần tự sự MTSamples (khi có) không liên quan bệnh học tới bệnh nhân đó.

## 4. Case study từ Giai đoạn 1 (cùng `patient_id`, nay nằm trong tập test strict)

| Ca | Nhãn | Xác suất mô hình triển khai (đã hiệu chuẩn) | Ghi chú |
| :--- | :--- | :--- | :--- |
| `PT-0044` | ASTHMA | ASTHMA 0,580 · COPD 0,407 · HF 0,007 · PNEUMONIA 0,006 | Đúng nhưng sát ranh giới hen/COPD – Phase 1: mô hình bảng đoán COPD, mô hình văn bản đoán đúng |
| `PT-0254` | COPD | COPD 0,927 · ASTHMA 0,050 · HF 0,021 · PNEUMONIA 0,001 | Đúng, độ tin cậy cao |

*(Nguồn: `results/registry.json → error_analysis.case_studies`.)*

## 5. Khuyến nghị
- Không diễn giải hiệu năng theo lớp cho suy tim và viêm phổi; báo cáo kèm số bệnh nhân gốc.
- Ưu tiên kết quả grouped CV (`sensitivity_grouped_cv_posthoc`) khi bàn về độ ổn định.
- Với dữ liệu thật: tách split theo bệnh nhân gốc **và** đảm bảo đủ bệnh nhân/lớp; kiểm tra tương quan nhãn – tuổi trước khi huấn luyện.
