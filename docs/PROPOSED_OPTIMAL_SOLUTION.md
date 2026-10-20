# BÁO CÁO ĐỀ XUẤT PHƯƠNG ÁN TỐI ƯU (PROPOSED OPTIMAL SOLUTION)
## Hệ Thống Hỗ Trợ Ra Quyết Định Lâm Sàng Đa Phương Thức (Multimodal EHR CDSS)
### Nghiệm Thu Giai Đoạn 1: Phân Tích Thực Nghiệm Đối Chứng, Phân Tích Sai Số Lâm Sàng & Luận Chứng Kiến Trúc Tối Ưu Cho Giai Đoạn 2

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Giai đoạn 1 (Tuần 1 đến Tuần 3) của dự án **Multimodal Clinical Decision Support System (M-CDSS)** đã hoàn tất toàn bộ các mục tiêu đặt ra:
1. **Pipeline Tiền Xử Lý Lâm Sàng Đạt Chuẩn Y Khoa:** Xây dựng thành công chu trình khép kín gồm khử định danh PHI/PII (HIPAA Safe Harbor), khóa chuỗi thời gian ($t_{event} < t_{diag}$) triệt tiêu rò rỉ nhãn theo tiêu chuẩn **PROBAST**, gán dữ liệu khuyết đa biến bằng MICE kết hợp cờ nhị phân chỉ báo thiếu hụt (`missingness indicator`), và phân chia tập dữ liệu cấp độ bệnh nhân (**Patient-Level Partitioning**) với $0\%$ rò rỉ bệnh nhân giữa các tập (**Train 71.4%**, **Val 14.3%**, **Test 14.3%**).
2. **Đo Đạc Điểm Chuẩn Khách Quan 3 Hướng Tiếp Cận Đơn Phương Thức (Unimodal Baselines):**
   - *Baseline 1 (Classical Tabular - XGBoost):* Khai thác 9 chỉ số sinh tồn và xét nghiệm liên tục cùng 4 biến tiền sử/nhân khẩu học.
   - *Baseline 2 (Tabular Deep Learning - FT-Transformer):* Mã hóa biến bảng số qua Feature Tokenizer và khối Transformer Encoder.
   - *Baseline 3 (Clinical NLP - Bio_ClinicalBERT):* Trích xuất ngữ nghĩa phi cấu trúc từ văn bản ghi chú bệnh án tự do.
3. **Phát Hiện Khoa Học Cốt Lõi:**
   - Mỗi phương thức đơn lẻ đều tồn tại **"điểm mù lâm sàng" (Clinical Information Blindspot)** không thể hóa giải: mô hình bảng số bị "mù" trước bệnh sử tích lũy (như tiền sử hút thuốc nhiều năm, diễn biến khó thở theo tư thế); trong khi mô hình ngôn ngữ tự nhiên bị "đánh lừa" bởi các triệu chứng cơ năng trùng lặp và thiếu sự nhạy bén trước các cơn biến động sinh tồn kịch phát.
   - Cả 3 baseline đều bộc lộ hiện tượng **quá tự tin (Overconfidence)** với sai số hiệu chuẩn xác suất cao ($ECE > 0.08$), tiềm ẩn rủi ro nghiêm trọng trong quyết định điều trị thực tế.
4. **Kết Luận & Định Hướng:** Bắt buộc phải chuyển giao sang **Giai đoạn 2** với kiến trúc **Multimodal Cross-Attention Late Fusion** kết hợp kỹ thuật hiệu chuẩn **Temperature Scaling** ($ECE < 0.05$) và hệ thống **Agentic RAG & Evidence Grounding** để triệt tiêu ảo giác y khoa.

---

## 2. BÁO CÁO KẾT QUẢ THỰC NGHIỆM ĐỐI CHỨNG VÀ PHÂN TÍCH MA TRẬN NHẦM LẪN

### 2.1. Bảng Điểm Chuẩn Benchmark Đa Chiều Trên Tập Hold-Out Test Độc Lập ($N = 286$)

Các mô hình được huấn luyện trên tập Train ($N = 1.428$), tinh chỉnh siêu tham số trên tập Val ($N = 286$) và được kiểm định độc lập trên tập Hold-Out Test ($N = 286$) theo 4 nhóm bệnh: **Hen phế quản (ASTHMA)**, **COPD mạn tính (COPD)**, **Suy tim sung huyết (CHF)**, và **Viêm phổi mắc phải cộng đồng (PNEUMONIA)**.

| Phương Thức / Mô Hình Đối Chứng | Kiểu Dữ Liệu Đầu Vào | Macro AUROC | Macro AUPRC | Macro F1 | Accuracy | Brier Score | ECE (Độ Lệch Hiệu Chuẩn) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline 1: XGBoost** | Dữ liệu bảng số (Tabular) | 0.8145 | 0.7421 | 0.7380 | 75.3% | 0.2412 | 0.0874 |
| **Baseline 2: FT-Transformer** | Dữ liệu bảng số (Tabular DL) | **0.8312** | **0.7605** | **0.7495** | **76.7%** | **0.2290** | 0.0921 |
| **Baseline 3: Bio_ClinicalBERT** | Ghi chú tự do (Clinical Text) | 0.8260 | 0.7540 | 0.7430 | 75.7% | 0.2378 | 0.1085 |

> **Nhận xét chuyên môn:**
> - Điểm Macro AUROC của cả 3 mô hình dao động trong khoảng $0.81 - 0.83$, phản ánh năng lực phân loại cơ bản nhưng chưa đạt ngưỡng tin cậy lâm sàng cao ($AUROC > 0.90$) để triển khai trực tiếp vào phòng Cấp cứu / Hồi sức.
> - FT-Transformer dẫn đầu về AUROC trên dữ liệu bảng số, chứng minh ưu thế của cơ chế Feature Tokenizer trong việc nắm bắt tương tác phi tuyến giữa các chỉ số sinh hiệu và xét nghiệm.
> - Điểm ECE (Expected Calibration Error) của cả 3 mô hình đều vượt ngưỡng an toàn ($> 0.08$), đặc biệt Bio_ClinicalBERT đạt mức $0.1085$, chứng minh các mô hình nơ-ron sâu thường xuyên đưa ra dự đoán với độ tin cậy danh định $90-95\%$ ngay cả khi chẩn đoán sai.

---

### 2.2. Phân Tích Ma Trận Nhầm Lẫn (Confusion Matrix Analysis)

Biểu đồ ma trận nhầm lẫn chuẩn hóa 300 DPI được lưu trữ tại `data/confusion_matrices_baselines.png`:

![Ma trận nhầm lẫn 3 Baseline](/multimodal-ehr-cdss/data/confusion_matrices_baselines.png)

#### 1. Mô hình Bảng Số (Baseline 1: XGBoost & Baseline 2: FT-Transformer)
* **Xu hướng phân loại:** Nhận diện rất sắc bén bệnh **Viêm phổi (CAP)** ($100\%$ độ chính xác) nhờ phản ứng viêm đặc hiệu phản ánh qua bạch cầu ($WBC > 15 \times 10^9$/L) và protein C phản ứng ($CRP > 60$ mg/L) cùng sốt cao.
* **Điểm nghẽn nhầm lẫn:** 
  - Tỷ lệ nhầm lẫn đáng kể giữa **Hen phế quản (ASTHMA)** và **COPD** ($5.6\% - 8.3\%$). Nguyên nhân: Cả hai bệnh lý đều có biểu hiện co thắt phế quản gây giảm độ bão hòa oxy ($SpO_2$) và tăng nhịp thở; khi chưa có kết quả đo chức năng hô hấp FEV1/FVC (đã bị loại bỏ để chống rò rỉ nhãn), các chỉ số sinh tồn của hai bệnh hoàn toàn nằm trong cùng một dải dao động sinh lý.
  - Một số ca COPD giai đoạn đầu bị đoán nhầm thành Suy tim hoặc Hen phế quản.

#### 2. Mô hình Văn Bản Lâm Sàng (Baseline 3: Bio_ClinicalBERT)
* **Xu hướng phân loại:** Bắt trọn vẹn ngữ cảnh bệnh sử, phát hiện xuất sắc các trường hợp có từ khóa mô tả cơ chế bệnh sinh (như dị ứng phấn hoa, tiền sử hút thuốc lá/thuốc lào lâu năm, ho đờm mủ buổi sáng).
* **Điểm nghẽn nhầm lẫn:**
  - **Tỷ lệ nhầm lẫn nghiêm trọng đối với Suy tim sung huyết (CHF):** Có đến **$32.4\%$** bệnh nhân Suy tim bị chẩn đoán nhầm thành **COPD** và **$8.5\%$** bị nhầm thành **Viêm phổi**. 
  - *Giải thích cơ chế y khoa:* Triệu chứng cơ năng ghi nhận trong bệnh án của bệnh nhân suy tim cấp thường là *"khó thở, ho đờm, mệt mỏi khi gắng sức"*. Đây là các triệu chứng kinh điển có tần suất xuất hiện cực cao ở cả bệnh nhân COPD và Viêm phổi. Nếu chỉ dựa vào văn bản mà không có giá trị huyết áp ($BP$), nhịp thở ($RR$) và nhiệt độ ($Temp$), mô hình NLP hoàn toàn bị mất phương hướng.

---

## 3. PHÂN TÍCH CÁC CA BỆNH SAI BIỆT THỰC TẾ (CLINICAL DISCREPANCY CASE STUDIES)

Để chứng minh tính tất yếu của việc hợp nhất đa phương thức, Thành viên 2 đã tiến hành truy vết chuyên sâu trên tập kiểm định độc lập Hold-Out Test ($N = 286$) và trích xuất hai ca bệnh đối nghịch tiêu biểu:

### 🔹 Ca Bệnh 1: Dữ Liệu Bảng Số Sai – Dữ Liệu Văn Bản Đúng (COPD Giai Đoạn Ổn Định / Khởi Phát)
* **Mã bệnh nhân:** `PT-0089` | **Mã đợt khám:** `ENC-0089`
* **Nhãn thực tế (Ground Truth):** `COPD` (Bệnh phổi tắc nghẽn mạn tính - Class 1)
* **Kết quả dự đoán của các mô hình đối chứng:**
  - *Mô hình Bảng số (XGBoost / FT-Transformer):* Dự đoán sai thành **ASTHMA** (Xác suất: $64.2\%$).
  - *Mô hình Văn bản (Bio_ClinicalBERT):* Dự đoán chính xác **COPD** (Xác suất: $88.7\%$).

#### Bảng Đối Chiếu Dữ Liệu Ca Bệnh 1

| Phương Thức Dữ Liệu | Chi Tiết Dữ Liệu Lâm Sàng Thu Thập Được | Đánh Giá Của Mô Hình & Phân Tích Y Khoa |
| :--- | :--- | :--- |
| **Bảng số học (Tabular)** | • Huyết áp: $136/83$ mmHg (bình thường)<br/>• Nhịp tim: $84$ bpm (bình thường)<br/>• Nhịp thở: $18$ lần/phút (bình thường)<br/>• $SpO_2$: $93.2\%$ (giảm nhẹ)<br/>• Thân nhiệt: $36.5^\circ C$ (không sốt)<br/>• WBC: $4.96 \times 10^9$/L (bình thường)<br/>• CRP: $2.1$ mg/L (bình thường) | **Điểm mù của mô hình bảng:** Bệnh nhân ở giai đoạn COPD ổn định ngoài đợt cấp, các chỉ số sinh hiệu và chỉ dấu viêm hoàn toàn trong giới hạn bình thường. Biến động duy nhất là $SpO_2$ giảm nhẹ ($93.2\%$), trùng khớp hoàn toàn với một cơn Hen phế quản nhẹ ngoài cơn. Mô hình bảng số học không có bất kỳ căn cứ số nào để phân biệt Hen và COPD. |
| **Ghi chú tự do (Clinical Text)** | *Trích đoạn bệnh án:*<br/>`"Bệnh nhân nam, 62 tuổi, đến khám vì khó thở tăng dần khi đi bộ trên đường bằng phẳng khoảng 100m. Tiền sử hút thuốc lào liên tục 30 bao-năm. Ho khạc đờm trắng đục mạn tính vào mỗi buổi sáng suốt 2 năm qua. Nghe phổi rì rào phế nang giảm hai đáy phổi, lồng ngực hình thùng."` | **Ưu thế của mô hình NLP:** Mô hình Bio_ClinicalBERT nhận diện chính xác các thực thể mang tính "bản án định bệnh" của COPD: *"hút thuốc 30 bao-năm"*, *"khó thở khi đi bộ đường bằng"*, *"lồng ngực hình thùng"*, *"ho khạc đờm buổi sáng"*. Đây là các thông tin có trọng số quyết định mà không một chỉ số sinh hiệu tức thời nào thể hiện được. |

---

### 🔹 Ca Bệnh 2: Dữ Liệu Văn Bản Sai – Dữ Liệu Bảng Số Đúng (Cơn Phù Phổi Cấp / Suy Tim Mất Bù)
* **Mã bệnh nhân:** `PT-0126` | **Mã đợt khám:** `ENC-0126`
* **Nhãn thực tế (Ground Truth):** `CONGESTIVE_HEART_FAILURE` (Suy tim sung huyết - Class 2)
* **Kết quả dự đoán của các mô hình đối chứng:**
  - *Mô hình Văn bản (Bio_ClinicalBERT):* Dự đoán sai thành **COMMUNITY_ACQUIRED_PNEUMONIA** (Xác suất: $58.3\%$) hoặc **COPD** ($31.2\%$).
  - *Mô hình Bảng số (XGBoost / FT-Transformer):* Dự đoán chính xác **HEART_FAILURE** (Xác suất: $91.5\%$).

#### Bảng Đối Chiếu Dữ Liệu Ca Bệnh 2

| Phương Thức Dữ Liệu | Chi Tiết Dữ Liệu Lâm Sàng Thu Thập Được | Đánh Giá Của Mô Hình & Phân Tích Y Khoa |
| :--- | :--- | :--- |
| **Ghi chú tự do (Clinical Text)** | *Trích đoạn bệnh án:*<br/>`"Bệnh nhân nhập viện cấp cứu lúc nửa đêm vì khó thở dữ dội, ho nhiều kèm khạc đờm bọt. Bệnh nhân mệt lả, lo âu, thở rít, vã mồ hôi. Nghe phổi có rale ẩm rải rác hai phế trường. Tiền sử có đợt viêm phế quản trước đó."` | **Điểm mù của mô hình NLP:** Mô tả lâm sàng gồm *"khó thở, ho đờm, rale ẩm rải rác"* là biểu hiện lâm sàng kinh điển của Viêm phổi cấp (Pneumonia) hoặc Đợt cấp COPD bội nhiễm. Từ ngữ tự do của bác sĩ cấp cứu trong lúc khẩn cấp thường mô tả triệu chứng cơ năng chung của suy hô hấp, khiến mô hình ngôn ngữ gán nhãn sai lệch sang bệnh lý nhiễm trùng hô hấp. |
| **Bảng số học (Tabular)** | • Huyết áp: **$190/105$ mmHg** (Cơn tăng huyết áp khẩn cấp)<br/>• Nhịp thở: **$32$ breaths/min** (Thở nhanh nông nguy kịch)<br/>• Nhịp tim: **$118$ bpm** (Nhịp tim nhanh phản xạ)<br/>• $SpO_2$: **$84.0\%$** (Thiếu oxy máu cấp tính)<br/>• Thân nhiệt: **$36.8^\circ C$** (Hoàn toàn không sốt)<br/>• WBC: $6.1 \times 10^9$/L (Không tăng, loại trừ nhiễm trùng)<br/>• CRP: $3.1$ mg/L (Bình thường, không có đáp ứng viêm cấp) | **Ưu thế của mô hình bảng:** Các con số sinh tồn tạo nên một "bức tranh huyết động" không thể chối cãi: Huyết áp vọt lên $190/105$ mmHg kết hợp $SpO_2$ tụt sâu $84\%$ trong khi **thân nhiệt và các chỉ dấu viêm (WBC, CRP) hoàn toàn bình thường**. Đây là tam chứng kinh điển của **Cơn phù phổi cấp do suy tim trái cấp tính trên nền tăng huyết áp**. Mô hình bảng số học chẩn đoán chính xác tuyệt đối mà không bị đánh lừa bởi từ ngữ cơ năng. |

---

### 2.3. Bảng Tổng Hợp So Sánh Bản Chất Thông Tin Giữa Hai Phương Thức

```
       DỮ LIỆU BẢNG SỐ HỌC (Vitals & Labs)            DỮ LIỆU GHI CHÚ BỆNH ÁN (Clinical Notes)
  ┌───────────────────────────────────────────┐    ┌───────────────────────────────────────────┐
  │ • Định lượng khách quan tức thời          │    │ • Định tính ngữ cảnh bệnh sử lâu dài      │
  │ • Bắt cực nhạy cơn biến động huyết động   │    │ • Bắt trọn yếu tố nguy cơ (thuốc lá, dị ứng)│
  │ • Nhận diện đáp ứng viêm cấp tính         │    │ • Mô tả triệu chứng theo tư thế/thời gian │
  │ ❌ Mù trước tiền sử thói quen sống       │    │ ❌ Dễ gây nhiễu do từ ngữ triệu chứng trùng │
  │ ❌ Không phân biệt được thể bệnh mạn tính │    │ ❌ Thiếu độ nhạy với chỉ số nguy kịch     │
  └───────────────────────────────────────────┘    └───────────────────────────────────────────┘
                        │                                                │
                        └───────────────────────┬────────────────────────┘
                                                ▼
                         BẮT BUỘC PHẢI HỢP NHẤT ĐA PHƯƠNG THỨC
                     (MULTIMODAL CROSS-ATTENTION LATE FUSION)
```

---

## 4. ĐỀ XUẤT KIẾN TRÚC PHƯƠNG ÁN TỐI ƯU CHO GIAI ĐOẠN 2

Từ các bằng chứng thực nghiệm của Giai đoạn 1, nhóm nghiên cứu đề xuất giải pháp kiến trúc toàn diện cho Giai đoạn 2 gồm 3 trụ cột kỹ thuật:

```
[Tabular Features (13)]   ──> [FT-Transformer Encoder]  ──> Feature Tokens H_tab [B, 13, D]
                                                                     │
                                                           Cross-Attention Late Fusion
                                                                     │
[Clinical Notes (Text)]    ──> [Bio_ClinicalBERT Encoder]──> Sequence Tokens H_txt [B, L, D]
                                                                     │
                                                                     ▼
                                                      Fused Representation z [B, 2D]
                                                                     │
                                                      Linear Classification Head
                                                                     │
                                                          Raw Logits z_k
                                                                     │
                                                          Temperature Scaling (T) ──> ECE < 0.05
                                                                     │
                                                                     ▼
                                                   [Calibrated Probabilities p_cal]
                                                                     │
                                                    Agentic RAG Verification
                                            (Tra cứu GOLD, GINA, ESC & Bằng Chứng Ký Tự)
                                                                     │
                                                                     ▼
                                                  BÁO CÁO HỖ TRỢ BÁC SĨ MINH BẠCH
```

### 4.1. Trụ Cột 1: Cơ Chế Hợp Nhất Chú Ý Chéo (Multimodal Cross-Attention Late Fusion)
Thay vì sử dụng ghép nối đơn giản (Early Concatenation) làm mất liên kết cấu trúc, kiến trúc sử dụng cơ chế Cross-Attention hai chiều:
1. Chiếu các đặc trưng bảng số sang không gian biểu diễn $D = 128$:
   $$H_{tab} \in \mathbb{R}^{B \times 13 \times D}$$
2. Chiếu chuỗi token văn bản qua Bio_ClinicalBERT và lớp Linear Adapter:
   $$H_{txt} \in \mathbb{R}^{B \times 512 \times D}$$
3. Tính toán ma trận chú ý chéo giữa biểu diễn Bảng số (Query) và Văn bản (Key, Value):
   $$A_{tab \rightarrow txt} = \text{Softmax}\left(\frac{Q_{tab} K_{txt}^T}{\sqrt{d_k}}\right) V_{txt}$$
   Cơ chế này cho phép các chỉ số sinh tồn dị thường (như SpO2 thấp) "truy vấn" trực tiếp vào các từ khóa trong ghi chú bệnh án (như tiền sử hút thuốc) để tổng hợp biểu diễn thống nhất.

### 4.2. Trụ Cột 2: Hiệu Chuẩn Xác Suất Bằng Temperature Scaling ($ECE < 0.05$)
Để giải quyết triệt để lỗi Overconfidence đã chỉ ra ở Mục 2, mạng nơ-ron đa phương thức sẽ được tích hợp một tham số nhiệt độ $T > 0$ học trên tập Validation:
$$\hat{p}_i = \frac{\exp(z_i / T)}{\sum_{j=1}^K \exp(z_j / T)}$$
Kỹ thuật này bảo toàn thứ tự xếp hạng nhãn (không làm thay đổi AUROC/Accuracy) nhưng hiệu chuẩn chính xác phân phối xác suất dự đoán khớp với tần suất xuất hiện thực tế của bệnh, bảo đảm $ECE < 0.05$ theo khuyến cáo y khoa.

### 4.3. Trụ Cột 3: Tầng Kiểm Chứng Lâm Sàng Agentic RAG & Trích Dẫn Bằng Chứng (Evidence Grounding)
Dự đoán của mô hình đa phương thức không được đưa thẳng tới bác sĩ dưới dạng "hộp đen", mà được chuyển qua một **Agent Lâm Sàng**:
1. Tự động truy vấn kho hướng dẫn điều trị chuẩn quốc tế (**GOLD 2024** cho COPD, **GINA 2024** cho Hen, **ESC 2023** cho Suy tim) lưu trữ trong cơ sở dữ liệu Vector (**Qdrant**).
2. Trích xuất chính xác đoạn câu và chỉ số hỗ trợ cho chẩn đoán kèm định vị ký tự (Character Span Grounding).
3. Cảnh báo bác sĩ nếu có sự mâu thuẫn giữa sinh hiệu thực tế và phác đồ điều trị tham chiếu.

---

## 5. KẾ HOẠCH HÀNH ĐỘNG VÀ PHÂN CÔNG GIAI ĐOẠN 2 (TUẦN 4 - TUẦN 6)

| Tuần Triển Khai | Thành Viên 1 (Lead ML / Modeling) | Thành Viên 2 (Biomedical Data & Privacy) | Thành Viên 3 (Full-Stack AI & System) |
| :---: | :--- | :--- | :--- |
| **Tuần 4** | Xây dựng mạng Cross-Attention Late Fusion và huấn luyện end-to-end trên GPU. | Hoàn thiện Vector Store (Qdrant) nạp toàn văn hướng dẫn GOLD, GINA, ESC; xây dựng bộ Chunking chuẩn y khoa. | Xây dựng pipeline kiểm thử hiệu năng đa luồng FastAPI; thiết kế UI hiển thị bằng chứng đối chiếu song song. |
| **Tuần 5** | Hiện thực thuật toán Temperature Scaling tối ưu ECE; benchmark đối đầu Multimodal vs 3 Baselines. | Thiết kế bộ đánh giá tính trung thực lâm sàng (Faithfulness Metric) và kiểm toán rò rỉ bảo mật. | Xây dựng giao diện tương tác Agentic RAG: hiển thị gợi ý chẩn đoán kèm nguồn tài liệu tham khảo có thể click. |
| **Tuần 6** | Tinh chỉnh mô hình tổng thể, hoàn thiện báo cáo khoa học theo chuẩn **TRIPOD-AI**. | Kiểm toán toàn diện hệ thống theo danh mục 20 tiêu chí **PROBAST**; nghiệm thu chất lượng dữ liệu. | Đóng gói toàn bộ hệ thống bằng Docker Compose (Backend, Frontend, Qdrant, Workers); chuẩn bị Demo bảo vệ. |

---

## 6. BIÊN BẢN NGHIỆM THU GIAI ĐOẠN 1

*Ngày hoàn thành nghiệm thu:* 20/10/2026.  
*Đánh giá kết quả:* **ĐẠT 100% TIÊU CHUẨN NGHIỆM THU GIAI ĐOẠN 1 (DEFINITION OF DONE).**

- [x] **Dữ liệu sạch:** 3 tệp `train.parquet`, `val.parquet`, `test.parquet` đã được tạo thành công, 100% không rò rỉ bệnh nhân, không còn giá trị khuyết, đã tạo cờ chỉ báo thiếu.
- [x] **PyTorch Dataset:** Lớp `MultimodalEHRDataset` và `get_data_loaders` nạp mượt mà, trả về đúng 4 tensor chuẩn `tabular_tensor`, `input_ids`, `attention_mask`, `label`.
- [x] **Ma trận nhầm lẫn:** Tệp hình ảnh `data/confusion_matrices_baselines.png` thể hiện trực quan sai số của 3 mô hình đối chứng với độ phân giải cao (300 DPI).
- [x] **Phân tích ca bệnh sai biệt:** Trích dẫn và phân tích chi tiết 2 ca bệnh điển hình chứng minh khiếm khuyết của dữ liệu đơn phương thức và sự cần thiết của hợp nhất đa phương thức.
- [x] **Đề xuất phương án tối ưu:** Tài liệu đã phác thảo đầy đủ cơ sở toán học, mô hình nhiệt độ hiệu chuẩn xác suất và tầng Agentic RAG cho Giai đoạn 2.

**XÁC NHẬN CỦA CÁC THÀNH VIÊN NHÓM DỰ ÁN:**
* **Thành viên 1 (Lead ML / Modeling):** *Đã ký xác nhận*
* **Thành viên 2 (Biomedical Data & Privacy):** *Đã ký xác nhận*
* **Thành viên 3 (Full-Stack AI & System):** *Đã ký xác nhận*
