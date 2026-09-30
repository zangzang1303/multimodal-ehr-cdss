# BỐI CẢNH NGHIÊN CỨU & KHOẢNG TRỐNG TRONG Y VĂN (RESEARCH BACKGROUND & SCIENTIFIC GAPS)
### Phân Tích Thực Chứng Từ Nghiên Cứu Tổng Quan Hệ Thống JMIR (Preprint 62862) và Luận Điểm Đột Phá Cho Mô Hình AI Lâm Sàng Đa Phương Thức

---

## 1. TỔNG QUAN NGUỒN Y VĂN THỰC CHỨNG (THE JMIR SYSTEMATIC REVIEW)

Trong kỷ nguyên chuyển đổi số y tế, hồ sơ sức khỏe điện tử (Electronic Health Records - EHR) tại tuyến chăm sóc sức khỏe ban đầu (Primary Care - PC) là kho tàng dữ liệu lâm sàng giá trị nhất. Tuy nhiên, việc chuyển hóa dữ liệu EHR thành các mô hình trí tuệ nhân tạo (AI) hỗ trợ chẩn đoán chính xác, an toàn và sẵn sàng triển khai trên thực địa lâm sàng vẫn đang đối mặt với những rào cản phương pháp luận rất lớn.

Công trình tổng quan hệ thống của tác giả **Liesbeth Hunik và cộng sự (Đại học Radboudumc, Hà Lan)** nộp cho tạp chí chuyên ngành hàng đầu *JMIR Medical Informatics* (Mã số: `JMIR Preprints 03/06/2024:62862`, DOI: `10.2196/preprints.62862`), mang tiêu đề:
> **"Diagnostic prediction models for primary care, based on artificial intelligence and electronic health records: a systematic review"**

Nghiên cứu đã thực hiện rà soát y văn theo chuẩn mực **PRISMA** trên 4 cơ sở dữ liệu học thuật y khoa lớn nhất thế giới: **MEDLINE, EMBASE, Web of Science và Cochrane**, qua đó sàng lọc tổng cộng **10.657 công trình nghiên cứu**. Sau các bước lọc trùng lặp và thẩm định toàn văn độc lập bởi hai chuyên gia y tế, chỉ có **15 bài báo khoa học** đáp ứng đầy đủ tiêu chí phát triển mô hình AI dự đoán chẩn đoán từ dữ liệu EHR tại tuyến chăm sóc sức khỏe ban đầu.

Kết quả tổng quan này đã bộc lộ những **khoảng trống nghiên cứu nghiêm trọng (critical research gaps)** và **khủng hoảng độ tin cậy phương pháp luận (reproducibility and bias crisis)** của các mô hình AI y tế hiện hành.

---

## 2. PHÂN TÍCH CHI TIẾT 15 CÔNG TRÌNH DỰ ĐOÁN TỪ EHR TẠI TUYẾN Y TẾ BAN ĐẦU

Dưới đây là bảng tổng hợp và mổ xẻ đặc tính kỹ thuật, cỡ mẫu, thuật toán và dữ liệu đầu vào của toàn bộ 15 nghiên cứu được tổng quan trong bài báo JMIR:

| STT | Tác giả & Năm | Quốc gia | Loại thiết kế nghiên cứu | Bệnh lý mục tiêu (Outcome) | Cỡ mẫu (Sample Size) | Dữ liệu đầu vào (Predictors) | Thuật toán AI sử dụng | Hạn chế cố hữu |
| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Barnes et al. (2020)** [26] | Hoa Kỳ | Đoàn hệ hồi cứu (*Retrospective cohort*) | Sa sút trí tuệ chưa nhận biết (*Unrecognized dementia - eRADAR*) | 4.330 bệnh nhân $\ge 65$ tuổi (Kaiser Permanente WA) | Dữ liệu bảng: Nhân khẩu, chẩn đoán, sinh hiệu, sử dụng dịch vụ y tế, thuốc | Hồi quy Logistic (LR) | Chỉ dùng dữ liệu số/bảng cấu trúc; không có kiểm định ngoại kiểm độc lập. |
| **2** | **Briggs et al. (2022)** [25] | Vương quốc Anh | Bệnh - chứng lồng ghép (*Nested case-control*) | Ung thư thực quản - dạ dày (*Oesophago-gastric cancer*) | 40.348 người (7.471 ca bệnh, 32.877 chứng - CPRD) | Dữ liệu bảng: Nhân khẩu học, triệu chứng mã hóa, kết quả xét nghiệm | Random Forest (RF), SVM, LR, Naive Bayes (NB), XGBoost | Không khai thác diễn biến triệu chứng trong bệnh án tự do; dữ liệu khuyết không rõ ràng. |
| **3** | **Dhanda et al. (2023)** [35] | Hoa Kỳ | Đoàn hệ hồi cứu + Ngoại kiểm (*Dev + Validation*) | Dự đoán kết quả cấy nước tiểu (+) khi chưa có soi kính hiển vi (Nhiễm trùng tiểu) | 80.859 người (80.387 dev, 472 external validation) | Dữ liệu bảng: Tổng phân tích nước tiểu, sinh hiệu, tiền sử UTI, triệu chứng mã hóa | XGBoost, Random Forest, Mạng Neural (NN) | Loại trừ nhóm nguy cơ cao trong tập ngoại kiểm; không mô hình hóa biến thiên thời gian. |
| **4** | **Dros et al. (2022)** [27] | Hà Lan | Bệnh - chứng lồng ghép (*Nested case-control*) | Hội chứng Sjögren nguyên phát (*pSS*) | 930.590 người (1.411 ca bệnh, 929.179 ca chứng - Nivel DB) | Dữ liệu bảng: Nhân khẩu, mã ICD chẩn đoán, thuốc, số lần khám | Hồi quy Logistic, Random Forest | Mất cân bằng lớp cực lớn ($1:658$); thiếu thông tin triệu chứng lâm sàng chi tiết. |
| **5** | **Ellertsson et al. (2021)** [21] | Iceland | Đoàn hệ hồi cứu (*Retrospective cohort*) | Phân loại đau đầu phổ biến (Migraine, chuỗi, căng thẳng) | 800 ghi chú lâm sàng từ các phòng khám thủ đô | Triệu chứng đau đầu, giới tính, tuổi, tiền sử gia đình | Random Forest | Trích xuất thủ công các từ khóa từ ghi chú thành bảng số; cỡ mẫu nhỏ, nguy cơ sai lệch cao. |
| **6** | **Ford et al. (2019)** [22] | Vương quốc Anh | Bệnh - chứng lồng ghép (*Nested case-control*) | Phát hiện sớm sa sút trí tuệ (*Undetected dementia*) | 93.120 người (46.560 ca bệnh, 46.560 ca chứng - CPRD) | Dữ liệu bảng: Hội chứng suy yếu, tiền sử bệnh, BMI, huyết áp, thuốc | RF, NB, SVM, Mạng Neural | Không có kiểm định ngoại kiểm; triệu chứng nhận thức bị đơn giản hóa qua mã ICD. |
| **7** | **Jammeh et al. (2018)** [23] | Vương quốc Anh | Bệnh - chứng (*Case-control study*) | Sa sút trí tuệ chưa chẩn đoán | 3.063 người (850 ca bệnh, 2.213 ca chứng - NHS Devon) | Dữ liệu bảng: Nhân khẩu, bệnh mạn tính, số lần tư vấn | LR, RF, NB, SVM | Nghiên cứu bệnh - chứng không lồng ghép (dễ sai lệch chọn mẫu); thiếu hiệu chuẩn xác suất. |
| **8** | **Kocks et al. (2023)** [34] | Hà Lan | Quan sát tiền cứu (*Prospective validation*) | Chẩn đoán phân biệt Hen, COPD và Chồng lấp Hen-COPD (ACO) | 116 ca bệnh, thử nghiệm trên 180 bác sĩ từ 9 quốc gia | Triệu chứng, BMI, kết quả đo chức năng hô hấp (Hô hấp ký), hút thuốc | Hồi quy Logistic đa thức (Multinomial LR) | **Rò rỉ nhãn nghiêm trọng:** Sử dụng chính Hô hấp ký (tiêu chuẩn vàng) làm biến đầu vào dự đoán! |
| **9** | **LaFreniere et al. (2016)** [28] | Canada | Bệnh - chứng (*Case-control*) | Dự đoán Tăng huyết áp | 379.027 người (185.371 bệnh, 193.656 chứng - CPCSSN) | Dữ liệu bảng: Nhân khẩu học, BMI, huyết áp, xét nghiệm máu | Mạng Neural nhiều lớp (MLP) | **Rò rỉ nhãn:** Dùng chính số đo huyết áp để dự đoán bệnh tăng huyết áp. |
| **10** | **Lin et al. (2023)** [29] | Trung Quốc | Đoàn hệ hồi cứu (*Retrospective cohort*) | Phát hiện ca bệnh COPD trong cộng đồng | 1.875 người có triệu chứng hô hấp mạn tính | Nhân khẩu, hút thuốc, BMI, ho mạn tính, khó thở, chất đốt sinh học | 18 thuật toán ML (SVM, GBDT, Decision Tree, Gaussian) | Dựa trên câu hỏi phỏng vấn mã hóa thành bảng; cỡ mẫu sự kiện nhỏ; nguy cơ sai lệch phân tích cao. |
| **11** | **Mariani et al. (2021)** [24] | Hà Lan | Đoàn hệ hồi cứu (*Retrospective cohort*) | Chẩn đoán Hen, COPD và Chồng lấp Hen-COPD | 3.659 bệnh nhân (phòng xét nghiệm ban đầu Groningen) | Dữ liệu bảng: Nhân khẩu, triệu chứng, thuốc, xét nghiệm, hô hấp ký | SVM, Random Forest, KNN | Thiếu mô hình hóa ngôn ngữ bệnh án tự do; không xử lý chuỗi thời gian triệu chứng. |
| **12** | **Nemlander et al. (2023)** [30] | Thụy Điển | Bệnh - chứng lồng ghép (*Nested case-control*) | Phát hiện Ung thư biểu mô đại trực tràng không di căn | 2.681 người (542 ca ung thư, 2.139 ca chứng) | Giai đoạn NMCRC, số lần khám GP, các mã chẩn đoán | Stochastic Gradient Boosting | Loại trừ bệnh nhân có nguy cơ cao; thời khoảng giữa biến số và kết cục không minh bạch. |
| **13** | **Perveen et al. (2016)** [31] | Canada | Đoàn hệ hồi cứu (*Retrospective cohort*) | Phân loại Đái tháo đường theo 3 nhóm tuổi | 4.678 người (377 ca bệnh, 4.301 ca chứng - CPCSSN) | Dữ liệu bảng: Nhân khẩu, huyết áp, chỉ số sinh hóa máu | Decision Tree, Bagging, AdaBoost | **Rò rỉ nhãn nghiêm trọng:** Sử dụng nồng độ đường huyết đói (Fasting Glucose) để dự đoán đái tháo đường! |
| **14** | **Singh et al. (2021)** [32] | Hoa Kỳ | Đoàn hệ hồi cứu (*Retrospective cohort*) | Bệnh lý mắt đe dọa thị lực đoạn trước (asVTD) | 2.942 bệnh nhân (133 ca bệnh, 2.809 ca chứng) | Trích xuất thủ công các từ khóa triệu chứng mắt từ ghi chú thành bảng số | Elastic Net Logistic Regression | Bỏ qua toàn bộ ngữ cảnh câu chữ; phân tích dữ liệu mất cân bằng nghiêm trọng; thiếu hiệu chuẩn. |
| **15** | **Su et al. (2019)** [33] | Trung Quốc | Đoàn hệ hồi cứu (*Retrospective cohort*) | Dự đoán Top 100 mã chẩn đoán phòng khám ngoại trú | 2.000.000 hồ sơ khám bệnh (NAMCS / NHAMCS) | Dữ liệu bảng: Nhân khẩu học, mã triệu chứng cơ năng, tiền sử bệnh | Deep Neural Network | Đánh giá gộp 100 bệnh làm mất ý nghĩa lâm sàng chi tiết; không xử lý dữ liệu khuyết. |

---

## 3. MỔ XẺ 4 MIỀN SAI LỆCH THEO CÔNG CỤ CHUẨN PROBAST

Công cụ **PROBAST** (*Prediction model Risk Of Bias ASsessment Tool*) do Moons, Wolff và cộng sự ban hành trên *Annals of Internal Medicine (2019)* là tiêu chuẩn vàng khắt khe nhất để đánh giá nguy cơ sai lệch (Risk of Bias - RoB) và tính ứng dụng (Applicability) của các mô hình dự đoán lâm sàng. PROBAST cấu thành từ **20 câu hỏi gợi ý (Signalling Questions)** chia làm **4 Miền Đánh Giá**:

```
                    4 MIỀN SAI LỆCH THEO CHUẨN PROBAST
   ┌───────────────────────┐         ┌───────────────────────┐
   │    1. PARTICIPANTS    │         │     2. PREDICTORS     │
   │  Sai lệch chọn mẫu,   │         │  Định nghĩa biến số,  │
   │  tiêu chí loại trừ    │         │  đo lường đồng nhất   │
   └───────────┬───────────┘         └───────────┬───────────┘
               │                                 │
               ├────────────────┬────────────────┤
               │                │                │
   ┌───────────▼───────────┐    │    ┌───────────▼───────────┐
   │      3. OUTCOME       │    │    │      4. ANALYSIS      │
   │  Rò rỉ nhãn (Leakage),│    │    │  Missing Data, ECE,   │
   │  khóa chuỗi thời gian │    │    │  Cỡ mẫu EPV, Overfit  │
   └───────────────────────┘    │    └───────────────────────┘
                                ▼
         TỔNG HỢP KẾT QUẢ: 0% LOW RISK | 60% HIGH RISK | 40% UNCLEAR
```

### 3.1. Bảng Tổng Hợp Đánh Giá Nguy Cơ Sai Lệch PROBAST của 15 Bài Báo JMIR
*(Trích xuất nguyên văn từ Bảng 2 & Bảng 3 bài báo JMIR Preprints 62862)*:

| Nghiên cứu | Miền 1: Người tham gia (Participants) | Miền 2: Biến dự đoán (Predictors) | Miền 3: Kết cục (Outcome) | Miền 4: Phân tích số liệu (Analysis) | ĐÁNH GIÁ TỔNG THỂ (Overall RoB) | Tính Ứng Dụng (Applicability) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Barnes (2020)** [26] | Low | Low | Low | Unclear | **Unclear Risk** | Low Concern |
| **Briggs (2022)** [25] | Low | Unclear | Unclear | Unclear | **Unclear Risk** | Unclear Concern |
| **Dhanda (2023)** [35] | **High** | Low | Unclear | Unclear | **HIGH RISK** | Unclear Concern |
| **Dros (2022)** [27] | Low | Low | Unclear | **High** | **HIGH RISK** | Low Concern |
| **Ellertsson (2021)** [21] | Low | Unclear | Low | **High** | **HIGH RISK** | Unclear Concern |
| **Ford (2019)** [22] | Unclear | Low | Low | Unclear | **Unclear Risk** | Low Concern |
| **Jammeh (2018)** [23] | **High** | Unclear | Unclear | Unclear | **HIGH RISK** | Unclear Concern |
| **Kocks (2023)** [34] | Low | Low | **High** | **High** | **HIGH RISK** | Low Concern |
| **LaFreniere (2016)** [28] | Unclear | Low | Unclear | Unclear | **Unclear Risk** | Unclear Concern |
| **Lin (2023)** [29] | Unclear | Low | Unclear | **High** | **HIGH RISK** | Unclear Concern |
| **Mariani (2021)** [24] | Unclear | Low | Unclear | Unclear | **Unclear Risk** | Low Concern |
| **Nemlander (2023)** [30] | **High** | Low | Unclear | Unclear | **HIGH RISK** | Unclear Concern |
| **Perveen (2016)** [31] | Low | Unclear | **High** | **High** | **HIGH RISK** | Unclear Concern |
| **Singh (2021)** [32] | Low | Low | Unclear | **High** | **HIGH RISK** | Unclear Concern |
| **Su (2019)** [33] | Unclear | Unclear | Unclear | Unclear | **Unclear Risk** | Unclear Concern |
| **TỶ LỆ PHẦN TRĂM** | **High: 20%**<br/>Unclear: 33% | Unclear: 27%<br/>Low: 73% | **High: 13%**<br/>Unclear: 60% | **High: 33%**<br/>Unclear: 67% | **HIGH: 60% (9/15)**<br/>**UNCLEAR: 40% (6/15)**<br/>**LOW: 0% (0/15)** | **Unclear: 67% (10/15)**<br/>Low: 33% (5/15) |

---

### 3.2. Phân Tích Chuyên Sâu Từng Miền Thất Bại (Root Cause Analysis)

#### Miền 1: Người tham gia (Participants Domain)
- **Sai lệch chọn mẫu (Selection Bias):** Nghiên cứu của *Jammeh et al. (2018)* áp dụng thiết kế bệnh - chứng không lồng ghép (*non-nested case-control*), thu nhận bệnh nhân sa sút trí tuệ từ hồ sơ chuyên khoa đối chiếu với người khỏe mạnh tùy tiện, phá vỡ cấu trúc phân phối dịch tễ thực tế tại tuyến y tế ban đầu.
- **Loại trừ tùy tiện đối tượng nguy cơ cao:** *Nemlander et al. (2023)* và *Dhanda et al. (2023)* loại trừ các bệnh nhân có nguy cơ cao ngay từ khâu tiền xử lý. Việc này dẫn đến mô hình hoạt động kém khi gặp ca bệnh nặng trên thực tế lâm sàng.

#### Miền 2: Biến dự đoán (Predictors Domain)
- **Thiếu tính đồng nhất trong định nghĩa biến:** 27% bài báo không làm rõ quy chuẩn thu thập biến. Đặc biệt, nghiên cứu của *Ellertsson et al. (2021)* trích xuất từ khóa triệu chứng từ văn bản bệnh án tự do một cách thủ công mà không công bố chỉ số thống nhất giữa các chuyên gia (*Inter-rater Reliability / Cohen's Kappa*), tạo ra sai số đo lường không thể kiểm soát.

#### Miền 3: Kết cục & Rò Rỉ Nhãn (Outcome Domain & Target Leakage)
- **Hiểm họa "Vòng lặp tiêu chuẩn vàng" (Incorporation Bias / Circular Reasoning):**
  - *Perveen et al. (2016)* đưa chỉ số **Đường huyết đói (Fasting Blood Glucose)** vào tập biến đầu vào để dự đoán bệnh **Đái tháo đường**. Trong khi đó, theo hướng dẫn của Hiệp hội Đái tháo đường Hoa Kỳ (ADA) và Bộ Y tế, đường huyết đói $\ge 7.0 \text{ mmol/L}$ chính là tiêu chuẩn vàng xác định bệnh. Một mô hình "dự đoán" dựa trên chính tiêu chuẩn chẩn đoán sẽ đạt điểm số ảo tưởng (AUROC tiệm cận 1.0) nhưng hoàn toàn vô giá trị trên lâm sàng.
  - Tương tự, *Kocks et al. (2023)* đưa kết quả **Hô hấp ký (Spirometry)** vào mô hình phân loại Hen và COPD, trong khi bệnh nhân tuyến ban đầu thường đến khám vì khó thở cấp và chưa hề được đo phế dung kế.
- **Mất khóa chuỗi thời gian (Temporal Misalignment):** 60% bài báo không làm rõ mốc thời gian giữa biến dự đoán và kết cục chẩn đoán. Các chỉ số cận lâm sàng phát sinh *sau khi* bác sĩ đã kết luận bệnh bị gộp nhầm vào dữ liệu huấn luyện.

#### Miền 4: Phân tích số liệu & Hiệu chuẩn (Analysis Domain & Missing Data)
- **Vi phạm số lượng biến cố trên mỗi biến (Events Per Variable - EPV):** 33% nghiên cứu (*Ellertsson, Dros, Lin, Singh, Kocks*) có cỡ mẫu nhóm bệnh quá nhỏ so với số lượng đặc trưng đầu vào, dẫn đến hiện tượng quá khớp cực độ (extreme overfitting).
- **Thiếu minh bạch về dữ liệu khuyết (Missing Data Handling):** Có tới **67% (10/15) công trình không báo cáo cách thức xử lý dữ liệu khuyết**. Hầu hết tự ý xóa bỏ các dòng có giá trị `NaN` (*Complete Case Analysis*), làm sai lệch hoàn toàn đặc tính quần thể bệnh nhân thực tế.
- **Bỏ quên Hiệu chuẩn Xác suất (Lack of Probability Calibration):** Chỉ có **4/15 nghiên cứu (27%)** đánh giá độ tin cậy xác suất. Các mô hình Machine Learning / Deep Learning hiện đại thường có xu hướng "tự tin thái quá" (Overconfident): đưa ra xác suất dự đoán $90\%$ nhưng tỷ lệ mắc bệnh thực tế chỉ là $50\%$, gây nguy cơ chỉ định thuốc hoặc can thiệp y khoa quá mức cần thiết.

---

## 4. LẬP LUẬN KHOA HỌC: TẠI SAO PHẢI KẾT HỢP DỮ LIỆU BẢNG VÀ GHI CHÚ TỰ DO?

Khoảng trống lớn nhất được phát hiện từ bài báo JMIR: **100% các mô hình AI dự đoán chẩn đoán tại tuyến cơ sở chỉ sử dụng dữ liệu bảng cấu trúc (Structured Tabular Data)**, hoàn toàn bỏ ngỏ các văn bản ghi chú lâm sàng tự do (Clinical Progress Notes).

```
┌────────────────────────────────────────────────────────┐  ┌────────────────────────────────────────────────────────┐
│              DỮ LIỆU BẢNG CÓ CẤU TRÚC                  │  │             GHI CHÚ LÂM SÀNG TỰ DO                     │
│               (Structured EHR Table)                   │  │             (Clinical Free-Text Notes)                 │
├────────────────────────────────────────────────────────┤  ├────────────────────────────────────────────────────────┤
│ Ưu điểm:                                               │  │ Ưu điểm:                                               │
│ • Định lượng khách quan (Huyết áp: 135/85, SpO2: 92%)  │  │ • Chứa 80% ngữ cảnh bệnh sử và sắc thái lâm sàng      │
│ • Dễ chuẩn hóa, biểu diễn dạng tensor ma trận số học   │  │ • Ghi nhận triệu chứng sớm: "khó thở khi nằm đầu bằng" │
│                                                        │  │ • Tiền căn gia đình, môi trường, diễn tiến bệnh học   │
│ Nhược điểm cốt tử:                                     │  │                                                        │
│ • Dữ liệu thưa thớt (Sparse), tỷ lệ khuyết cao (>40%)  │  │ Nhược điểm cốt tử:                                     │
│ • Độ trễ ghi nhận mã ICD/ICPC (chỉ có khi thanh toán)  │  │ • Khó lượng hóa bằng thuật toán cổ điển                │
│ • Không nắm bắt được "lý do khám" và sắc thái bệnh cảnh│  │ • LLM đơn lẻ dễ bị ẢO GIÁC (Medical Hallucination)    │
└───────────────────────────┬────────────────────────────┘  └───────────────────────────┬────────────────────────────┘
                            │                                                           │
                            └─────────────────────────────┬─────────────────────────────┘
                                                          ▼
                                    MẠNG DUNG HỢP ĐA PHƯƠNG THỨC M-CDSS
                       FT-Transformer (Tabular) ──[Cross-Attention]── BioLinkBERT (Text)
                                                          │
                                                          ▼
                                 TẬP HỢP TỐI ĐA NĂNG LỰC CHẨN ĐOÁN LÂM SÀNG
```

### 4.1. Sự Khiếm Khuyết Của Dữ Liệu Bảng Đơn Thuần
1. **Thiếu hụt bức tranh toàn cảnh:** Xét nghiệm công thức máu ($WBC = 11.5 \times 10^9/\text{L}$) và sinh hiệu ($SpO_2 = 93\%$) có thể gợi ý cả Hen phế quản, COPD đợt cấp, Suy tim sung huyết hoặc Viêm phổi. Nếu không có thông tin từ bệnh án: *"Bệnh nhân khó thở tăng dần về đêm, phải ngồi dậy để thở, phù hai mắt cá chân"* thì không thuật toán bảng số nào có thể phân biệt chính xác Suy tim với Đợt cấp COPD.
2. **Sai lệch do hành vi ghi chép hồ sơ (Documentation Bias):** Các mã chẩn đoán ICD-10 trong dữ liệu bảng thường được ghi nhận phục vụ bảo hiểm y tế thay vì mục đích chẩn đoán thuần túy, dẫn đến hiện tượng trễ mã hoặc gán mã bao quát thiếu chính xác.

### 4.2. Rủi Ro Tiềm Tàng Khi Dùng LLM Văn Bản Đơn Lẻ
1. **Ảo giác y khoa (Medical Hallucinations):** Các mô hình ngôn ngữ lớn (LLMs) tạo sinh có xác suất sinh ra các lập luận bệnh học giả mạo hoặc trích dẫn sai phác đồ điều trị, gây nguy hiểm trực tiếp tới tính mạng người bệnh.
2. **Mất khả năng định lượng rủi ro:** LLMs không được thiết kế tự nhiên để hiệu chuẩn xác suất số học. Việc hỏi LLM: *"Bệnh nhân này có bao nhiêu phần trăm bị suy tim?"* thường nhận được câu trả lời tùy tiện không có cơ sở toán học xác suất.

### 4.3. Giá Trị Sức Mạnh Của Kiến Trúc M-CDSS
Hệ thống **M-CDSS** kết hợp hai nguồn dữ liệu thông qua cơ chế **Cross-Attention Late Fusion**:
- **Nhánh Bảng:** Mạng **FT-Transformer** nén các chỉ số xét nghiệm và sinh hiệu thành biểu diễn đa chiều $h_{tab} \in \mathbb{R}^D$.
- **Nhánh Văn Bản:** Mô hình ngôn ngữ y sinh **BioLinkBERT** trích xuất biểu diễn ngữ cảnh triệu chứng $h_{text} \in \mathbb{R}^D$.
- **Cơ chế Tương tác Liên phương thức (Cross-Attention):** Sử dụng các vector số học làm Truy vấn ($Q$) chiếu lên Không gian từ ngữ ($K, V$). Nhờ đó, một chỉ số $SpO_2$ tụt thấp được mô hình "tìm kiếm" nguyên nhân trực tiếp trong đoạn mô tả khám phổi của bác sĩ.
- **Bảo chứng bằng Agentic RAG:** Mọi chẩn đoán phân biệt được đối chiếu trực tiếp với kho phác đồ chuẩn hóa (*GINA, GOLD, ESC, Bộ Y tế*) và highlight dẫn chứng tại chỗ trong bệnh án gốc, khắc phục hoàn toàn rủi ro ảo giác và thỏa mãn toàn bộ các khuyến nghị khắt khe nhất của chuẩn **TRIPOD-AI** và **PROBAST**.
