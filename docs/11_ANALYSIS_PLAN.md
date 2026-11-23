# KẾ HOẠCH PHÂN TÍCH THỰC NGHIỆM ĐĂNG KÝ TRƯỚC (PRE-REGISTRATION ANALYSIS PLAN)
### Giai đoạn 3 – Nghiên cứu Chuyên sâu & Gia cố Bằng chứng (Backlog 09)
**Dự án:** M-CDSS (Multimodal Clinical Decision Support System)  
**Ngày đăng ký:** 2026-11-19 (Đăng ký trước khi chốt kết quả phân tích Backlog 09)  
**Đơn vị phụ trách:** Nhóm Nghiên cứu M-CDSS (Thành viên 2 - Biomedical Data Engineer & Privacy phụ trách DCA & Đánh giá Lâm sàng)

---

## 1. MỤC TIÊU & CÂU HỎI NGHIÊN CỨU
Kế hoạch phân tích này định nghĩa trước các tiêu chí, thang đo thống kê, bệnh lý đích và quy tắc đánh giá độ bền lâm sàng nhằm đảm bảo tính minh bạch khoa học, ngăn chặn p-hacking và cherry-picking kết quả:

- **RQ1 (So sánh công bằng):** Dưới cùng điều kiện huấn luyện và đánh giá trên tập kiểm tra độc lập (canonical strict holdout test $N=302$), mô hình dung hợp Cross-Attention so sánh như thế nào với các mô hình đơn phương thức (CatBoost, Bio_ClinicalBERT) và phương pháp dung hợp trung bình xác suất (Ensemble)?
- **RQ4b (Lợi ích ròng lâm sàng qua DCA):** Mô hình có mang lại Net Benefit vượt trội so với chiến lược "can thiệp tất cả" (Treat-all) và "không can thiệp" (Treat-none) trên dải ngưỡng lâm sàng thực tế?
- **Độ bền khi thiếu phương thức (Robustness under Missing Modalities):** Khi dữ liệu thực tế bị khuyết văn bản hoặc dữ liệu bảng, mô hình dung hợp bảo toàn hiệu năng ra sao?
- **Tổng quát hoá nội bộ (Internal Generalization):** Độ suy giảm hiệu năng khi phân tách theo dòng thời gian (Temporal Split) so với phân tách ngẫu nhiên có kiểm soát (Strict Split)?
- **Tính công bằng & Sai số lâm sàng (Fairness & Error Analysis):** Phân tích hiệu năng trên các nhóm dân số học (giới tính, nhóm tuổi, tiền sử hút thuốc) và phân tích nguyên nhân gốc rễ trên các ca nhầm lẫn.

---

## 2. CHỈ SỐ ĐÁNH GIÁ (PRIMARY & SECONDARY ENDPOINTS)

### 2.1. Chỉ số chính (Primary Metric)
- **Macro-average AUROC (Area Under the Receiver Operating Characteristic):** Trung bình số học One-vs-Rest AUROC qua 4 lớp bệnh (Asthma, COPD, Heart Failure, Pneumonia). Đây là chỉ số chính đo lường khả năng phân định bệnh học độc lập với ngưỡng phân loại.

### 2.2. Chỉ số phụ (Secondary Metrics)
- **Macro-average AUPRC (Area Under the Precision-Recall Curve):** Đánh giá độ chính xác và độ nhạy trên các lớp có kích thước mẫu khác nhau.
- **Macro-average F1-Score:** Đo lường tại ngưỡng quyết định tối ưu xác suất cực đại ($\arg\max$).
- **Multiclass Brier Score:** Đánh giá độ chính xác xác suất toàn diện (tổng bình phương sai số xác suất).
- **Expected Calibration Error (ECE):** 15 bins equal-mass hoặc 10 bins tiêu chuẩn sau hiệu chuẩn nhiệt độ (Temperature Scaling).
- **Net Benefit (NB) & Net Reduction in Interventions:** Theo công thức Vickers & Elkin (2006).

### 2.3. Quy ước thống kê suy luận (Statistical Inference)
- **Số vòng lặp Bootstrap:** $B = 2000$ vòng lặp bootstrap theo từng bệnh nhân (patient-level resampling).
- **Khoảng tin cậy:** 95% Confidence Interval (bách phân vị $[2.5\%, 97.5\%]$).
- **Hiệu chỉnh nhiều so sánh (Multiple Comparisons):** Áp dụng hiệu chỉnh Holm-Bonferroni khi kiểm định ý nghĩa thống kê giữa mô hình đề xuất và các baselines.

---

## 3. PHÂN TÍCH ĐƯỜNG CONG QUYẾT ĐỊNH (DECISION CURVE ANALYSIS - DCA)

### 3.1. Bệnh lý đích (Target Disease)
- **Bệnh lý:** `HEART_FAILURE` (Suy tim sung huyết, ICD-10: I50).
- **Thiết lập:** One-vs-Rest (Suy tim vs. các bệnh lý hô hấp tương tự: Hen, COPD, Viêm phổi).

### 3.2. Hành động can thiệp lâm sàng giả định (Hypothetical Action)
- **Hành động:** Chỉ định khẩn cấp định lượng Peptide lợi niệu (NT-proBNP) kết hợp Siêu âm tim Doppler màu tại giường (Transthoracic Echocardiography - TTE) và hội chẩn chuyên khoa tim mạch sớm.
- **Ý nghĩa:** Giúp khẳng định hoặc loại trừ đợt cấp suy tim mất bù, tránh nhầm lẫn với đợt cấp COPD hoặc hen ác tính.

### 3.3. Dải ngưỡng xác suất can thiệp có lý do (Clinical Threshold Probability Range)
- **Dải ngưỡng quy định trước:** $p_t \in [0.05, 0.30]$ (từ 5% đến 30%).
- **Cơ sở lâm sàng:**
  - Chi phí xét nghiệm NT-proBNP và siêu âm tim tương đối thấp, không xâm lấn và ít biến chứng nguy hiểm đối với người bệnh.
  - Ngược lại, hậu quả của việc bỏ sót chẩn đoán suy tim cấp hoặc chậm trễ sử dụng thuốc lợi tiểu/thuốc dãn mạch có thể dẫn đến phù phổi cấp, suy hô hấp nặng và đe dọa tử vong.
  - Do đó, tỷ lệ đánh đổi (Harm:Benefit ratio) thường nằm trong khoảng $1:19$ ($p_t = 0.05$) đến $1:2.3$ ($p_t = 0.30$).
  - Bác sĩ cấp cứu sẵn sàng chỉ định can thiệp ngay cả khi xác suất nghi ngờ chỉ từ 5% – 10%.

### 3.4. Mô hình so sánh trong DCA
1. **Cross-Attention Multimodal CDSS (Đề xuất)**
2. **CatBoost (Baseline dữ liệu bảng)**
3. **Bio_ClinicalBERT (Baseline văn bản lâm sàng)**
4. **Probability-Averaged Ensemble (CatBoost + BERT)**
5. **Chiến lược can thiệp tất cả (Treat All)**
6. **Chiến lược không can thiệp (Treat None)**

### 3.5. Chỉ số báo cáo bắt buộc
- **Lợi ích ròng (Net Benefit - NB) tại các ngưỡng:** $p_t = 0.10$ và $p_t = 0.20$.
- **Chênh lệch Net Benefit ($\Delta\text{NB}$):** So với chiến lược tốt nhất kế tiếp.
- **Số can thiệp thừa tránh được trên 100 bệnh nhân (Net Reduction in Interventions per 100 patients):**
  $$\Delta \text{Interventions per 100} = \frac{\text{NB}_{\text{model}} - \text{NB}_{\text{comparator}}}{p_t} \times 100$$
- **Lưu ý dịch tễ học và cảnh báo ngoại suy:**
  > [!WARNING] Cảnh báo Ngoại suy Lâm sàng
  > Tỷ lệ bệnh nhân suy tim trong tập kiểm tra chuẩn là **35.1% (106/302)**, phản ánh đoàn hệ bệnh nhân nội trú/cấp cứu có chỉ định nhập viện chuyên sâu. Tỷ lệ này cao hơn đáng kể so với tỷ lệ hiện mắc suy tim tại y tế chăm sóc ban đầu (~1% – 4%). Do đó, giá trị Net Benefit tính toán được mang tính chất so sánh hiệu quả giữa các mô hình trong cùng đoàn hệ, không ngoại suy trực tiếp thành giá trị Net Benefit tuyệt đối tại các cơ sở khám chữa bệnh ban đầu chưa qua sàng lọc.

---

## 4. PHÂN TÍCH ĐỘ BỀN KHI THIẾU PHƯƠNG THỨC (ROBUSTNESS UNDER MISSING MODALITIES)

Khi ứng dụng thực tế trong bệnh viện, hồ sơ bệnh án điện tử thường xuyên thiếu hụt dữ liệu (bệnh nhân chưa kịp có ghi chú tự sự, hoặc thiếu xét nghiệm sinh hiệu). Thử nghiệm kiểm tra độ bền bao gồm 5 kịch bản suy luận:
1. **Đầy đủ 100% dữ liệu (Complete multimodal input)**
2. **Khuyết hoàn toàn phương thức văn bản (Missing text):** Thay thế ghi chú lâm sàng bằng chuỗi rỗng `""`.
3. **Khuyết hoàn toàn phương thức bảng (Missing tabular):** Thay thế toàn bộ 9 biến số bằng giá trị trung vị từ tập huấn luyện, 4 biến danh mục bằng giá trị phổ biến nhất.
4. **Khuyết ngẫu nhiên 10% biến số dạng bảng.**
5. **Khuyết ngẫu nhiên 30% biến số dạng bảng.**
6. **Khuyết ngẫu nhiên 50% biến số dạng bảng.**

So sánh trực tiếp sự suy giảm hiệu năng giữa Cross-Attention Multimodal, CatBoost và Bio_ClinicalBERT.

---

## 5. TỔNG QUÁT HOÁ NỘI BỘ (INTERNAL GENERALIZATION - TEMPORAL SPLIT)

Để đánh giá mức độ ổn định theo thời gian (temporal drift), thực hiện phân tích:
- **Tập dữ liệu:** Phân tách 2.000 bệnh nhân theo thuộc tính thời gian khám bệnh (`encounter_timestamp`):
  - **70% thời gian đầu (Train cũ):** Bệnh nhân từ 2026-06-01 đến 2026-08-03 ($N=1400$).
  - **30% thời gian sau (Test mới):** Bệnh nhân từ 2026-08-04 đến 2026-08-31 ($N=600$).
- **Mục tiêu:** Báo cáo $\Delta\text{AUROC} = \text{AUROC}_{\text{temporal}} - \text{AUROC}_{\text{strict}}$.
- **Khẳng định tính chất nghiên cứu:** Phân tích này là **kiểm tra độ bền nội bộ (Internal Generalization / Temporal Robustness)**, hoàn toàn không phải là ngoại kiểm trên bệnh viện độc lập bên ngoài (External Validation).

---

## 6. PHÂN TÍCH CÔNG BẰNG & SAI SỐ (FAIRNESS & ERROR ANALYSIS)

### 6.1. Phân nhóm dân số học (Subgroup Fairness)
Phân tích Macro AUROC và F1 kèm khoảng tin cậy 95% Bootstrap trên các phân nhóm:
1. **Giới tính:** Nam (`M`), Nữ (`F`).
2. **Độ tuổi:** Người trẻ/trung niên ($< 65$ tuổi), Người cao tuổi ($\ge 65$ tuổi).
3. **Tiền sử hút thuốc:** Không bao giờ hút (`NEVER`), Đã từng hút (`FORMER`), Đang hút thuốc (`CURRENT`).

### 6.2. Phân tích nguyên nhân sai số (Root Cause Error Analysis)
Xác định 3 cặp bệnh lý có tỷ lệ nhầm lẫn cao nhất trên ma trận nhầm lẫn (dự kiến Hen $\leftrightarrow$ COPD, Suy tim $\leftrightarrow$ Viêm phổi). Đọc chi tiết tối thiểu 10 ca bệnh cụ thể trên mỗi cặp (tổng $\ge 30$ ca) và phân loại nguyên nhân theo 3 miền lâm sàng:
1. **Giá trị sinh hiệu chồng lấn (Overlapping Vital Signs):** Chỉ số sinh hiệu nằm trong vùng giao thoa sinh lý bệnh.
2. **Văn bản lâm sàng gây nhiễu (Conflicting / Noisy Text):** Ghi chú chứa từ ngữ mô tả triệu chứng của nhiều bệnh đồng mắc.
3. **Nhãn dữ liệu tổng hợp mâu thuẫn (Synthetic Label Discrepancy):** Nhãn bệnh được gán nhưng các đặc trưng bệnh học mâu thuẫn.
Cập nhật lại 2 ca bệnh điển hình PT-0044 và PT-0254 dựa trên kết quả suy luận thực tế của mô hình mới.

---
*Kế hoạch phân tích này được đóng băng và lưu vào tài liệu kỹ thuật của dự án trước khi thực thi tính toán.*
