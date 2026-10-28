# BÁO CÁO KẾT QUẢ GIAI ĐOẠN 1 — M-CDSS

**Phiên bản:** 28/10/2026  
**Trạng thái:** Đã tái chạy toàn bộ chuỗi dữ liệu và đánh giá bằng strict split.  
**Phạm vi:** phân loại bốn nhãn trên dữ liệu tổng hợp và ghi chú lâm sàng đã khử định danh.

## 1. Tóm tắt điều hành

Phiên bản này thay thế các số liệu benchmark trước đây. Kiểm tra lại phát hiện nguy cơ rò rỉ dữ liệu: ghi chú hoặc cụm nguồn có thể xuất hiện ở nhiều tập, văn bản chứa tín hiệu quá trực tiếp của nhãn, và cách sinh dữ liệu cũ có luật phụ thuộc nhãn. Vì vậy, các kết quả 94–98% accuracy trước đây **không còn là kết luận khoa học chính**.

Pipeline đã được xây dựng lại theo chuỗi: **khôi phục CSV → converter mới → strict split theo nhóm nguồn → audit → baseline**. Trên 302 mẫu kiểm thử độc lập theo nhóm, kết quả là:

| Baseline | AUROC macro | AUPRC macro | F1 macro | Accuracy | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|
| CatBoost (bảng) | 0,9223 | 0,7872 | 0,6083 | 0,6854 | 0,3844 | 0,0663 |
| FT-Transformer (bảng) | 0,8976 | 0,7023 | 0,5789 | 0,6589 | 0,4725 | 0,1152 |
| Bio_ClinicalBERT (văn bản) | **0,9735** | **0,9314** | **0,8421** | **0,8543** | **0,2329** | **0,0373** |

Kết luận: đánh giá nội bộ hiện đáng tin cậy hơn về mặt tách dữ liệu, nhưng chưa chứng minh hiệu quả trên dữ liệu bệnh viện thực. Bio_ClinicalBERT tốt nhất trên tập giữ lại; đây là tín hiệu cần ngoại kiểm, không phải bằng chứng sẵn sàng triển khai lâm sàng.

## 2. Mục tiêu và bài toán

M-CDSS phân loại bốn nhóm: `ASTHMA`, `COPD`, `HEART_FAILURE` và `PNEUMONIA`. Giai đoạn 1 đánh giá riêng hai hướng thông tin:

- Dữ liệu bảng: dấu hiệu sinh tồn, xét nghiệm, nhân khẩu học và biến lâm sàng có cấu trúc.
- Văn bản: ghi chú lâm sàng đã khử định danh.

Các baseline là mốc cho fusion đa phương thức ở giai đoạn sau, không phải mô hình chẩn đoán đã được phê duyệt.

## 3. Dữ liệu và xây dựng lại pipeline

Nguồn đầu vào đã khôi phục tại `data/sources/`, gồm cohort tổng hợp Synthea và MTSamples. Converter được sửa để:

- loại ghi chú MTSamples trùng giữa các nhãn;
- không quay vòng tái sử dụng ghi chú khi hết nguồn;
- loại transcription/assessment khỏi đầu vào, đồng thời che tên chẩn đoán đích;
- loại luật sinh đặc trưng phụ thuộc trực tiếp nhãn;
- lưu `source_patient_group` và `source_note_group` phục vụ truy vết.

Tập raw cuối cùng có **2.000** bản ghi, cân bằng 500 bản ghi mỗi nhãn. WBC khuyết 20,5%; CRP khuyết 22,4%.

## 4. Strict split và audit leakage

Chia tập bằng connected components trên `source_patient_group` và `source_note_group`: mọi bản ghi liên kết bởi cùng bệnh nhân nguồn hoặc ghi chú nguồn phải ở cùng một split.

| Tập | Số mẫu | ASTHMA | COPD | HEART_FAILURE | PNEUMONIA |
|---|---:|---:|---:|---:|---:|
| Huấn luyện | 1.425 | 358 | 358 | 340 | 369 |
| Xác thực | 273 | 71 | 71 | 54 | 77 |
| Kiểm thử | 302 | 71 | 71 | 106 | 54 |

Audit đạt: giao nhau train/validation/test bằng **0** theo `patient_id`, `source_patient_group` và `source_note_group`; mọi split có đủ bốn lớp. Đây là thay đổi then chốt xử lý nguyên nhân làm điểm số cũ quá cao.

## 5. Thiết lập benchmark

Seed là 42, huấn luyện bằng CUDA. CatBoost được chọn từ các ứng viên bảng theo AUROC macro validation (CatBoost 0,9084; XGBoost 0,8895). FT-Transformer chạy 19 epochs. Bio_ClinicalBERT fine-tune block encoder cuối và classification head, sequence length 512, learning rate 2e-5, chạy 5 epochs.

Chỉ số gồm AUROC macro, AUPRC macro, F1 macro, accuracy, Brier và ECE. AUROC/AUPRC macro được ưu tiên để so sánh cân bằng giữa các nhãn và chất lượng xếp hạng xác suất.

## 6. Diễn giải kết quả

Bio_ClinicalBERT đạt kết quả cao nhất. Trong nhánh bảng, CatBoost tốt hơn FT-Transformer (accuracy 0,6854 so với 0,6589). Khoảng chênh validation–test ở FT-Transformer và BERT cho thấy mô hình còn nhạy với phân bố nhóm nguồn; không nên chọn mô hình chỉ dựa vào validation.

Về calibration, BERT có ECE 0,0373; CatBoost 0,0663; FT-Transformer 0,1152. Do đó câu tóm tắt tự động trong file kết quả rằng “tất cả ECE dưới 0,05” là sai; báo cáo này dùng các giá trị chi tiết ở bảng trên.

Sanity check với cây quyết định nông (độ sâu 4) chỉ đạt accuracy **0,7285** trên strict test, thấp hơn nhiều so với kết quả cũ xấp xỉ 0,955. Đây là bằng chứng hỗ trợ nhận định pipeline cũ được hưởng lợi từ leakage/lặp nguồn hơn là mô hình mới kém đi.

## 7. Giới hạn và rủi ro

- Dữ liệu tổng hợp và kho công khai không thay thế cohort bệnh viện thực, cũng không đại diện toàn diện cho Việt Nam.
- Strict split giảm mạnh leakage theo nguồn nhưng không loại bỏ hoàn toàn domain/style bias trong văn bản.
- Test set lệch lớp vừa phải; cần thêm bootstrap confidence interval, phân tích lỗi theo lớp và calibration theo lớp.
- Chưa có tối ưu ngưỡng theo chi phí lâm sàng, đánh giá công bằng, hay prospective evaluation.

Không dùng mô hình để ra quyết định điều trị. Mọi ứng dụng lâm sàng cần ngoại kiểm đa cơ sở, phê duyệt đạo đức, bảo mật dữ liệu và giám sát sau triển khai.

## 8. Kết luận và khuyến nghị

Giai đoạn 1 đã có benchmark tái lập được và audit chống leakage theo nhóm nguồn. Đây là mốc kết quả chính thức; các số liệu accuracy rất cao ở pipeline cũ chỉ còn giá trị lịch sử kỹ thuật. Bước tiếp theo là fusion bảng–văn bản theo đúng strict split, bootstrap CI, leave-source-out/temporal split và ngoại kiểm dữ liệu thực đã được phê duyệt.

## 9. Artefact tái lập

- Kết quả số: `data/rebuilt_strict_results_2026-10-28.json`
- Audit: `data/rebuilt_strict_split_audit.json`
- ROC/PR: `data/rebuilt_strict_curves_2026-10-28.png`
- Ma trận nhầm lẫn: `data/rebuilt_strict_confusion_2026-10-28.png`
- Converter: `scripts/convert_sources_to_raw.py`
- Tách/tải dữ liệu: `src/data_pipeline/dataset_loader.py`
- Audit script: `scripts/audit_data_leakage.py`
- Baseline: `scripts/run_baselines.py`

Các lệnh tái lập được cập nhật trong `README.md`: converter mới, strict processing, audit rồi `scripts/run_baselines.py` trên thư mục processed strict.
