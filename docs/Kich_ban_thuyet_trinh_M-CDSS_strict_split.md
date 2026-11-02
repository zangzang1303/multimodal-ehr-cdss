# Báo cáo tiến độ đợt 1 đề tài M-CDSS
## Bộ nội dung slide tự đọc dành cho Giáo viên đánh giá

**Mục đích tài liệu:** Tài liệu này được biên soạn dưới dạng bộ slide tự đọc (Self-contained Slide Deck) gửi trực tiếp đến Giảng viên hướng dẫn và Hội đồng thẩm định đánh giá tiến độ Đợt 1 đề tài M-CDSS. Tài liệu tự cung cấp đầy đủ bối cảnh lâm sàng, khoảng trống nghiên cứu, nguồn gốc dữ liệu, thực nghiệm baseline, phân tích điểm yếu mô hình qua case study và kế hoạch triển khai Giai đoạn 2; hoàn toàn độc lập, không phụ thuộc vào thuyết trình miệng và không yêu cầu thao tác phần mềm hay truy cập kho mã nguồn.

**Cấu trúc tài liệu:** Gồm 16 slide nội dung chuyên sâu được cấu trúc chặt chẽ theo 6 phần trọng tâm, kèm 1 slide danh mục tài liệu tham khảo học thuật chính thức:
1. **Phần 1: Khoảng trống nghiên cứu** (Slide 2)
2. **Phần 2: Nêu đề tài & Kế hoạch thực hiện** (Slide 3)
3. **Phần 3: Nguồn gốc dữ liệu** (Slide 4)
4. **Phần 4: Các mô hình Baseline & Kết quả thực nghiệm** (Slide 5 – Slide 8)
5. **Phần 5: Case Study — Điểm yếu & Điểm mù của các mô hình** (Slide 9 – Slide 12)
6. **Phần 6: Hướng phát triển cho Giai đoạn 2** (Slide 13 – Slide 16)
7. **Tài liệu tham khảo chính** (Slide 17)

> **Quy chuẩn số liệu:** Toàn bộ kết quả thực nghiệm trong báo cáo này được đo lường chính thức theo quy trình kiểm soát rò rỉ dữ liệu nghiêm ngặt (Strict Group Split & Leakage Audit). Kết quả của các mô hình được ghi nhận khách quan trên tập kiểm thử độc lập gồm 302 hồ sơ bệnh án (Hold-out Test Set).

---

## Slide 1 — Trang bìa

**TÊN ĐỀ TÀI: HỆ THỐNG HỖ TRỢ CHẨN ĐOÁN LÂM SÀNG ĐA PHƯƠNG THỨC TỪ HỒ SƠ SỨC KHỎE ĐIỆN TỬ (M-CDSS)**

**Phân kỳ báo cáo:** Báo cáo tiến độ Đợt 1 — Khoảng trống nghiên cứu, Nền tảng dữ liệu chuẩn hóa, Đánh giá thực nghiệm các mô hình Baseline và Định hướng dung hợp Giai đoạn 2.  
**Lĩnh vực nghiên cứu:** Trí tuệ nhân tạo y sinh (Biomedical AI), Học sâu đa phương thức (Multimodal Deep Learning), Xử lý ngôn ngữ tự nhiên lâm sàng (Clinical NLP).  
**Từ khóa:** Electronic Health Records (EHR), Multimodal AI, Clinical Notes, Tabular Data, Cross-Attention Late Fusion, CDSS.

---

# PHẦN 1: KHOẢNG TRỐNG NGHIÊN CỨU

---

## Slide 2 — Tổng quan y văn & Khoảng trống nghiên cứu trong AI Y tế

**Công trình tổng quan nền tảng:**  
Nghiên cứu của Hunik et al., *Diagnostic prediction models for primary care, based on artificial intelligence and electronic health records: a systematic review* (JMIR, 2024).

**Các số liệu quan trọng từ tổng quan hệ thống:**
- **10.657 công trình nghiên cứu** liên quan đến mô hình dự đoán chẩn đoán từ EHR được sàng lọc qua các cơ sở dữ liệu học thuật quốc tế.
- **Chỉ 15 nghiên cứu** đáp ứng đầy đủ các tiêu chuẩn phương pháp luận lâm sàng đưa vào phân tích tổng quan.
- **15/15 nghiên cứu (100%)** chỉ sử dụng dữ liệu có cấu trúc dạng bảng (ICD codes, chỉ số xét nghiệm); **chưa có nghiên cứu nào** trong tập này khai thác ghi chú văn bản tự do bằng các mô hình ngôn ngữ lâm sàng.
- **Đánh giá nguy cơ sai lệch theo công cụ PROBAST:** 9/15 nghiên cứu (60%) có nguy cơ sai lệch cao; 6/15 (40%) chưa rõ ràng; **0/15 nghiên cứu (0%)** đạt chuẩn nguy cơ sai lệch thấp.

**Kết luận từ y văn:**  
Tồn tại một **khoảng trống nghiên cứu rất lớn**: Hầu hết các giải pháp hiện tại bỏ quên nguồn tri thức phong phú trong ghi chú lâm sàng tự do (unstructured clinical text), đồng thời thiếu hụt quy trình kiểm soát rò rỉ dữ liệu chuẩn mực và minh bạch hiệu chuẩn xác suất trong các công bố AI y tế.

---

# PHẦN 2: NÊU ĐỀ TÀI & KẾ HOẠCH THỰC HIỆN

---

## Slide 3 — Mục tiêu đề tài & Kế hoạch thực hiện hai giai đoạn (M-CDSS)

**Mục tiêu tổng quát của đề tài:**  
Nghiên cứu, phát triển và đánh giá thực nghiệm nguyên mẫu hệ thống hỗ trợ quyết định lâm sàng đa phương thức (Multimodal CDSS) từ dữ liệu bảng số (sinh hiệu, xét nghiệm) và văn bản bệnh án tự do, đồng thời cung cấp khả năng giải thích minh bạch dựa trên y học chứng cứ.

**Phân kỳ thực hiện hai giai đoạn:**
- **Giai đoạn 1 (Đã hoàn thành):** Xây dựng kho dữ liệu 2.000 hồ sơ chuẩn hóa; thiết lập phân chia Strict Split và kiểm toán 0% rò rỉ; thực nghiệm đối chứng 3 mô hình Baseline đơn phương thức (CatBoost, FT-Transformer, Bio_ClinicalBERT); phân tích ca bệnh sai biệt chứng minh luận cứ khoa học cho dung hợp.
- **Giai đoạn 2 (Kế hoạch tiếp theo):** Xây dựng kiến trúc Multimodal Cross-Attention Late Fusion; tích hợp Agentic RAG truy xuất hướng dẫn điều trị (CPGs); đánh giá lâm sàng nâng cao (DCA, Bootstrap CI).

---

# PHẦN 3: NGUỒN GỐC DỮ LIỆU

---

## Slide 4 — Nguồn gốc dữ liệu & Cấu trúc bộ dữ liệu nghiên cứu

**Nguồn gốc dữ liệu:**  
Bộ dữ liệu được tổng hợp và chuẩn hóa từ hai nguồn bệnh án điện tử mở chuẩn mực: **Synthea EHR** (dữ liệu sinh hiệu, xét nghiệm dạng bảng chuẩn lâm sàng) và **MTSamples** (các báo cáo ghi chú lâm sàng thực tế của bác sĩ).

**Quy mô và thành phần bộ dữ liệu:**
- Tổng số **2.000 hồ sơ bệnh án đa phương thức**, phân bố hoàn toàn cân bằng **500 mẫu cho mỗi nhóm bệnh**:
  - Hen phế quản (ASTHMA): 500 hồ sơ (25%).
  - Bệnh phổi tắc nghẽn mạn tính (COPD): 500 hồ sơ (25%).
  - Suy tim (HEART_FAILURE): 500 hồ sơ (25%).
  - Viêm phổi (PNEUMONIA): 500 hồ sơ (25%).
- **Dữ liệu bảng có cấu trúc:** 12 trường đặc trưng gồm:
  - *Nhân khẩu học:* Tuổi, Giới tính.
  - *Sinh hiệu:* Huyết áp tâm thu/tâm trương, Nhịp tim, Nhịp thở, Thân nhiệt, SpO₂.
  - *Xét nghiệm & Bệnh nền:* Bạch cầu (WBC), Protein phản ứng C (CRP), Tiền sử hút thuốc lá, Tăng huyết áp, Đái tháo đường.
- **Tỷ lệ dữ liệu khuyết thiếu thực tế:** Số lượng bạch cầu (WBC) khuyết 20,5%, Protein phản ứng C (CRP) khuyết 22,4% — mô phỏng trung thực thực tế lâm sàng tuyến đầu khi không phải bệnh nhân nào cũng được làm đầy đủ xét nghiệm máu.

---

# PHẦN 4: CÁC MÔ HÌNH BASELINE & KẾT QUẢ THỰC NGHIỆM

---

## Slide 5 — Thiết kế thực nghiệm và 3 mô hình Baseline

**Lựa chọn 3 mô hình đại diện đơn phương thức:**
1. **CatBoost (Đại diện Bảng số học - Cây quyết định tăng cường):**  
   - Thuật toán GBDT tối ưu cho dữ liệu bảng; vượt qua XGBoost trên tập validation (Macro-AUROC: 0,9084 vs 0,8895) nhờ cơ chế *Ordered Boosting* chống rò rỉ nhãn. Tối ưu trên 12 biến sinh hiệu và xét nghiệm.
2. **FT-Transformer (Đại diện Bảng số học - Học sâu chuyên biệt):**  
   - Feature Tokenizer Transformer chuyển từng chỉ số số học thành vector nhúng và tính toán tự chú ý (Self-Attention) giữa các đặc trưng; huấn luyện 19 epochs với cơ chế early stopping.
3. **Bio_ClinicalBERT (Đại diện Ngôn ngữ Y sinh):**  
   - Mô hình Transformer tiền huấn luyện chuyên biệt trên hàng triệu ghi chú hồi sức cấp cứu từ kho dữ liệu lâm sàng MIMIC-III; fine-tune trên ghi chú y khoa của đề tài qua 5 epochs (max length 512 tokens, learning rate 2e-5).

**Hệ thống 6 chỉ số đánh giá toàn diện chuẩn y sinh:**
- **Năng lực phân biệt & xếp hạng (Discrimination):** Macro AUROC và Macro AUPRC (chỉ số sống còn khi dữ liệu mất cân bằng).
- **Độ chính xác phân loại dứt khoát:** Macro-F1 và Accuracy.
- **Độ tin cậy xác suất & Hiệu chuẩn (Calibration):** Brier Score (khoảng cách bình phương xác suất) và ECE (Expected Calibration Error — sai số hiệu chuẩn kỳ vọng, tiêu chuẩn y tế khắt khe ECE < 0,05).

---

## Slide 6 — Kết quả thực nghiệm tổng hợp trên tập kiểm thử độc lập (N = 302)

| Mô hình Baseline | AUROC macro | AUPRC macro | F1 macro | Accuracy | Brier Score | ECE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **CatBoost** *(Nhánh Bảng số)* | 0,9223 | 0,7872 | 0,6083 | 0,6854 | 0,3844 | 0,0663 |
| **FT-Transformer** *(Nhánh Bảng sâu)* | 0,8976 | 0,7023 | 0,5789 | 0,6589 | 0,4725 | 0,1152 |
| **Bio_ClinicalBERT** *(Nhánh Văn bản)* | **0,9735** | **0,9314** | **0,8421** | **0,8543** | **0,2329** | **0,0373** |

![Bảng tổng hợp chỉ số Benchmark các mô hình sau huấn luyện](images/01_benchmark_metrics_post_train.png)

**Các phát hiện thực nghiệm then chốt:**
1. **Sức mạnh áp đảo của mô hình Ngôn ngữ y sinh:** Bio_ClinicalBERT dẫn đầu toàn diện trên cả 6 chỉ số. Đạt AUROC macro **0,9735** và Accuracy **85,43%**, vượt xa các mô hình bảng số khoảng 17–20% về độ chính xác phân loại.
2. **Hiệu năng của nhánh Bảng số:** CatBoost đạt năng lực phân biệt rất tốt (AUROC 0,9223), nhỉnh hơn FT-Transformer (0,8976). Tuy nhiên, độ chính xác phân loại bị giới hạn ở 68,54% do sinh hiệu đơn thuần thiếu thông tin bệnh sử.
3. **Độ tin cậy xác suất xuất sắc:** Bio_ClinicalBERT đạt chỉ số ECE **0,0373** — vượt qua tiêu chuẩn lâm sàng quốc tế khắt khe (ECE < 0,05), trong khi CatBoost đạt 0,0663.

---

## Slide 7 — Phân tích đường cong ROC, Precision–Recall và Độ hiệu chuẩn

![Đường cong benchmark strict test: ROC micro-average, PR micro-average và Reliability Diagram](images/08_benchmark_curves.png)

**Phân tích chi tiết 3 đồ thị thực nghiệm:**
- **Đồ thị ROC Micro-average (Panel trái):** Đường cong của Bio_ClinicalBERT (màu xanh lá) tiệm cận góc trên bên trái với AUC micro đạt **0,969**, vượt trội CatBoost (0,923) và FT-Transformer (0,893) trên mọi ngưỡng độ nhạy.
- **Đồ thị Precision–Recall Micro-average (Panel giữa):** Bio_ClinicalBERT duy trì Precision rất cao ở mọi mức Recall, đạt Average Precision (AP micro) lên tới **0,922** (so với 0,813 của CatBoost và 0,722 của FT-Transformer).
- **Biểu đồ độ hiệu chuẩn Reliability Diagram (Panel phải):** Đường cong của Bio_ClinicalBERT bám sát đường chéo lý tưởng 45°, chứng minh xác suất dự đoán của mô hình phản ánh đúng xác suất xuất hiện bệnh thực tế, không bị hiện tượng tự tin thái quá.

*(Lưu ý: Đồ thị thể hiện chỉ số tính theo micro-average, trong khi bảng tại Slide 6 báo cáo macro-average, do đó có sự chênh lệch nhỏ giữa hai cách tính).*

---

## Slide 8 — Phân tích ma trận nhầm lẫn & Lỗi phân loại theo từng nhóm bệnh

![Ma trận nhầm lẫn của 3 mô hình Baseline trên tập kiểm thử độc lập](images/09_confusion_matrices.png)

**Phân tích cơ chế sai lệch qua ma trận phân loại (Tập test N = 302):**
- **Điểm yếu của mô hình Bảng số (CatBoost):**
  - *Nhầm lẫn nghiêm trọng giữa Hen và COPD:* **34/71 ca ASTHMA** bị phân loại nhầm thành COPD (chỉ đoán đúng 37 ca).
  - *Khó khăn nhận diện Viêm phổi:* **36/54 ca PNEUMONIA** bị đoán nhầm thành Hen (chỉ đoán đúng 11 ca).
  - *Cơ chế:* Sinh hiệu và chỉ số viêm (WBC, CRP) ở các đợt suy hô hấp cấp tính là tương đồng nhau; dữ liệu số đơn thuần không phân định được cơ chế co thắt hồi phục hay nhiễm trùng.
- **Sức mạnh và Hạn chế của mô hình Văn bản (Bio_ClinicalBERT):**
  - *Giải quyết xuất sắc sự nhầm lẫn Hen - COPD:* Đoán đúng **54/71 ca ASTHMA** và **60/71 ca COPD**.
  - *Nhận diện gần như tuyệt đối nhóm Suy tim:* Đoán đúng **105/106 ca HEART_FAILURE**.
  - *Điểm còn tồn tại:* 14/54 ca Viêm phổi vẫn bị nhầm sang Hen do triệu chứng khó thở và ran rít mô tả tương tự nhau trong bệnh án.

---

# PHẦN 5: CASE STUDY — ĐIỂM YẾU & ĐIỂM MÙ CỦA CÁC MÔ HÌNH

---

## Slide 9 — Tổng quan ca bệnh sai biệt điển hình giữa Bảng số và Văn bản

Trên tập kiểm thử độc lập 302 ca, nhóm nghiên cứu phát hiện các ca bệnh có dự đoán **hoàn toàn trái ngược** giữa mô hình Bảng số và mô hình Văn bản, bộc lộ rõ điểm yếu và điểm mù của từng phương thức:

| Mã bệnh nhân | Nhãn thực tế | Dự đoán Bảng (CatBoost) | Độ tin cậy Bảng | Dự đoán Văn bản (Bio_ClinicalBERT) | Độ tin cậy Văn bản | Bản chất sai biệt |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **PT-0044** | `ASTHMA` | `COPD` (Sai) | 78,82% | `ASTHMA` (Đúng) | 85,80% | **Điểm mù Bảng số** (Văn bản Đúng – Bảng Sai) |
| **PT-0089** | `ASTHMA` | `COPD` (Sai) | 83,13% | `ASTHMA` (Đúng) | 66,38% | **Điểm mù Bảng số** (Văn bản Đúng – Bảng Sai) |
| **PT-0174** | `COPD` | `COPD` (Đúng) | 80,38% | `ASTHMA` (Sai) | 58,66% | **Điểm mù Văn bản** (Bảng Đúng – Văn bản Sai) |
| **PT-0254** | `COPD` | `COPD` (Đúng) | 75,22% | `HEART_FAILURE` (Sai) | 58,99% | **Điểm mù Văn bản** (Bảng Đúng – Văn bản Sai) |

Hai ca bệnh **PT-0044** và **PT-0254** đại diện sâu sắc nhất cho cơ chế bù trừ điểm mù giữa hai nguồn dữ liệu.

---

## Slide 10 — Ca bệnh 1: Điểm yếu của Bảng số (Mã bệnh nhân PT-0044)

* **Nhãn thực tế (Ground Truth):** `ASTHMA` (Hen phế quản) — Bệnh nhân nữ 18 tuổi.
* **Kết quả đối chứng:**
  * Mô hình Bảng số (CatBoost): Dự đoán **SAI** thành `COPD` (Độ tin cậy: **78,82%**).
  * Mô hình Văn bản (Bio_ClinicalBERT): Dự đoán **ĐÚNG** thành `ASTHMA` (Độ tin cậy: **85,80%**).

![Dữ liệu Bảng số Ca 1](images/02_case1_pt0044_tabular_data.png)

![Ghi chú Lâm sàng Ca 1](images/03_case1_pt0044_clinical_text.png)

![Biểu đồ kết quả dự đoán Ca 1](images/06_case1_pt0044_model_predictions.png)

**Phân tích cơ chế bệnh học & Điểm mù mô hình:**
- **Vì sao Bảng số thất bại:** Bệnh nhân được đo sinh hiệu ngoài cơn khó thở cấp nên SpO₂ đạt 97,3%, nhịp thở và nhịp tim bình thường. Tuy nhiên, chỉ số viêm CRP tăng cao (24,28 mg/L) kết hợp tiền sử tăng huyết áp khiến CatBoost quy kết sang bệnh phổi tắc nghẽn mạn tính (`COPD`, 78,82%). Do thiếu chỉ số chức năng hô hấp FEV1, dữ liệu bảng đơn thuần không thể phân định được tính chất co thắt hồi phục của Hen.
- **Vì sao Văn bản thành công:** Bio_ClinicalBERT nắm bắt chính xác độ tuổi thanh thiếu niên (`18yo`), triệu chứng khởi phát cơn ho, khó thở tái diễn và đặc biệt là từ khóa tiền sử dùng thuốc dạng hít định liều (`Inhalers` — phác đồ đặc trưng của Hen), từ đó chẩn đoán chính xác ASTHMA với độ tự tin 85,80%.

---

## Slide 11 — Ca bệnh 2: Điểm yếu của Mô hình Văn bản (Mã bệnh nhân PT-0254)

* **Nhãn thực tế (Ground Truth):** `COPD` (Bệnh phổi tắc nghẽn mạn tính) — Bệnh nhân nữ 65 tuổi.
* **Kết quả đối chứng:**
  * Mô hình Văn bản (Bio_ClinicalBERT): Dự đoán **SAI** thành `HEART_FAILURE` (Độ tin cậy: **58,99%**).
  * Mô hình Bảng số (CatBoost): Dự đoán **ĐÚNG** thành `COPD` (Độ tin cậy: **75,22%**).

![Dữ liệu Bảng số Ca 2](images/04_case2_pt0254_tabular_data.png)

![Ghi chú Lâm sàng Ca 2](images/05_case2_pt0254_clinical_text.png)

![Biểu đồ kết quả dự đoán Ca 2](images/07_case2_pt0254_model_predictions.png)

**Phân tích cơ chế bệnh học & Điểm mù mô hình:**
- **Vì sao Văn bản thất bại (Nhiễu từ vựng & Che nhãn chống rò rỉ):** Nhằm tuân thủ kiểm soát rò rỉ, tên chẩn đoán đã được che bằng `[REDACTED_DIAGNOSIS]`. Bio_ClinicalBERT đối mặt với ngữ cảnh nặng nề: bệnh nhân cao tuổi suy hô hấp nằm viện dưỡng lão, mở khí quản, nghe phổi có ran ẩm/ran rít (`crackles/wheezes`), dùng aspirin và thuốc an thần. Bối cảnh từ vựng này trùng lặp với suy tim sung huyết có biến chứng hô hấp, khiến mô hình ngôn ngữ đoán nhầm sang `HEART_FAILURE` (58,99%).
- **Vì sao Bảng số thành công (Mỏ neo huyết động học):** Trái ngược với sự nhiễu loạn từ vựng, dữ liệu bảng cung cấp cấu hình huyết động học cực kỳ đặc thù: Huyết áp (115,9/80,1 mmHg) và nhịp tim (64,3 bpm) hoàn toàn ổn định—loại trừ hoàn toàn cơn tăng áp hay nhịp nhanh phản xạ của đợt suy tim cấp. CatBoost chẩn đoán chính xác `COPD` với độ tin cậy 75,22%.

---

## Slide 12 — Luận cứ khoa học từ Case Study: Tính tất yếu của Dung hợp Đa phương thức

**Kết luận khoa học then chốt rút ra từ hai Case Study:**
1. **Không có phương thức đơn lẻ nào chiếm ưu thế tuyệt đối trong mọi tình huống:**
   - Dữ liệu văn bản vượt trội trong việc khai thác bệnh sử, phác đồ dùng thuốc và diễn tiến triệu chứng nhưng **dễ bị nhiễu ngữ nghĩa** khi bệnh cảnh phức tạp hoặc khi tên bệnh đã bị che.
   - Dữ liệu bảng số đóng vai trò *"mỏ neo huyết động học"* (hemodynamic anchor) giữ cho chẩn đoán không bị chệch hướng bởi các từ vựng gây nhiễu, nhưng **bị điểm mù** khi sinh hiệu đo ngoài cơn cấp.
2. **Cơ sở khoa học vững chắc cho Giai đoạn 2:**
   - Sự thất bại xen kẽ giữa hai phương thức khẳng định: Ghép nối đơn giản là chưa đủ.
   - Hệ thống cần một cơ chế **Cross-Attention Late Fusion**: Cho phép vector đặc trưng bảng số làm truy vấn (Query) chiếu vào vector văn bản (Key, Value), từ đó tự động điều chỉnh trọng số chú ý vào đúng các từ khóa lâm sàng phù hợp với tình trạng huyết động thực tế của người bệnh.

---

# PHẦN 6: HƯỚNG PHÁT TRIỂN CHO GIAI ĐOẠN 2

---

## Slide 13 — Kiến trúc Dung hợp Đa phương thức Cross-Attention Late Fusion

```text
                                   KIẾN TRÚC ĐA PHƯƠNG THỨC M-CDSS
                                   
  DỮ LIỆU ĐẦU VÀO                   BỘ MÃ HÓA CHUYÊN BIỆT                 DUNG HỢP & RA QUYẾT ĐỊNH
┌──────────────────┐               ┌───────────────────────┐
│ Dữ liệu Bảng     │──────────────>│ FT-Transformer        │────────┐
│ (Sinh hiệu/XN)   │               │ (Biểu diễn bảng số)   │        │     ┌───────────────────────┐
└──────────────────┘               └───────────────────────┘        ├────>│ Cross-Attention       │
                                                                    │     │ Late Fusion Layer     │
┌──────────────────┐               ┌───────────────────────┐        │     └──────────┬────────────┘
│ Ghi chú Lâm sàng │──────────────>│ Bio_ClinicalBERT      │────────┘                │
│ (Bệnh án tự do)  │               │ (Biểu diễn ngữ nghĩa) │                         v
└──────────────────┘               └───────────────────────┘              ┌───────────────────────┐
                                                                          │ Classification Head   │
                                                                          │ (Dự đoán 4 nhóm bệnh) │
                                                                          └──────────┬────────────┘
                                                                                     │
                                                                                     v
                                                                          ┌───────────────────────┐
                                                                          │ Temperature Scaling   │
                                                                          │ (Hiệu chuẩn ECE<0,05) │
                                                                          └───────────────────────┘
```

**Nguyên lý vận hành các khối kỹ thuật:**
- **Nhánh Bảng số:** FT-Transformer mã hóa các mối tương tác phi tuyến giữa sinh hiệu và xét nghiệm thành vector biểu diễn đặc trưng bảng.
- **Nhánh Ngôn ngữ y sinh:** Bio_ClinicalBERT mã hóa toàn bộ ngữ cảnh bệnh sử, triệu chứng cơ năng và tiền sử dùng thuốc thành vector biểu diễn văn bản.
- **Tầng Cross-Attention Late Fusion:** Vector bảng số đóng vai trò Truy vấn ($Q$) chiếu lên Khóa ($K$) và Giá trị ($V$) của văn bản, cho phép tín hiệu sinh hiệu định hướng sự chú ý vào đúng các từ khóa lâm sàng then chốt.
- **Hiệu chuẩn xác suất (Temperature Scaling):** Tối ưu hóa độ tin cậy xác suất sau dung hợp, đảm bảo ECE < 0,05 trên tập kiểm thử độc lập.

---

## Slide 14 — Hệ thống Giải thích Lâm sàng dựa trên Y học chứng cứ (Agentic RAG)

```text
  HỆ THỐNG GIẢI THÍCH LÂM SÀNG DỰA TRÊN Y HỌC CHỨNG CỨ (AGENTIC RAG)
┌──────────────────────────────┐        ┌───────────────────────┐         ┌───────────────────────┐
│ Hướng dẫn điều trị Y khoa    │───────>│ Vector Store &        │────────>│ Diagnostic Agent      │
│ (CPGs: GINA, GOLD, Bộ Y tế)  │        │ Semantic Retriever    │         │ (Giải thích & Bằng cớ)│
└──────────────────────────────┘        └───────────────────────┘         └───────────────────────┘
                                                                                      │
                                                                                      v
                                                                          ┌───────────────────────┐
                                                                          │ Evidence Grounding    │
                                                                          │ (Trích dẫn cụ thể)    │
                                                                          └───────────────────────┘
```

**Mục tiêu giải thích minh bạch cho bác sĩ:**
- **Kho tri thức chuẩn y khoa:** Tích hợp trực tiếp Hướng dẫn chẩn đoán và điều trị của Bộ Y tế, phác đồ toàn cầu GINA (cho Hen) và GOLD (cho COPD).
- **Cơ chế neo bằng chứng (Evidence Grounding):** Loại bỏ hoàn toàn nguy cơ "ảo giác" (hallucination) của LLM. Mọi khuyến nghị chẩn đoán phân biệt của hệ thống bắt buộc phải kèm theo 2 căn cứ:
  1. *Căn cứ hồ sơ bệnh nhân:* Trích dẫn trực tiếp đoạn văn bản ghi chú hoặc chỉ số sinh hiệu bất thường cụ thể.
  2. *Căn cứ y văn:* Trích dẫn số trang, mục điều khoản tương ứng trong hướng dẫn điều trị chính thức.

---

## Slide 15 — Phương pháp luận Đánh giá Lâm sàng Mở rộng & Lộ trình thực hiện

```text
LỘ TRÌNH TRIỂN KHAI GIAI ĐOẠN 2 THEO THỨ TỰ PHỤ THUỘC KHOA HỌC
[Tháng 11/2026]              [Tháng 12/2026]              [Tháng 01/2027]              [Tháng 02/2027]
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│ 1. Multimodal Core  │─────>│ 2. Agentic RAG      │─────>│ 3. Đánh giá Mở rộng │─────>│ 4. Nghiệm thu       │
│ • Cross-Attention   │      │ • Hướng dẫn y khoa  │      │ • Phân tích DCA     │      │ • Hoàn thiện báo cáo│
│ • Huấn luyện fusion │      │ • Semantic Search   │      │ • Bootstrap CI      │      │ • Chuẩn TRIPOD-AI   │
│ • So sánh Ablation  │      │ • Evidence Grounding│      │ • Kiểm định Fairness│      │ • Nghiệm thu đề tài │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

**Các phương pháp đánh giá lâm sàng nâng cao:**
- **Phân tích đường cong quyết định (Decision Curve Analysis - DCA):** Đo lường lợi ích ròng lâm sàng (Net Benefit) trên thực tế ở các ngưỡng can thiệp y tế khác nhau, vượt ra ngoài các chỉ số học máy thuần túy.
- **Khoảng tin cậy Bootstrap (95% CI):** Lấy mẫu lại 1.000 lần để xác thực tính ổn định thống kê của các chỉ số AUROC, AUPRC, Macro-F1.
- **Kiểm định độ công bằng (Fairness Audit):** Kiểm tra tính nhất quán về độ nhạy và độ đặc hiệu giữa các nhóm tuổi và giới tính.
- **Tuân thủ chuẩn báo cáo quốc tế TRIPOD-AI:** Chuẩn hóa quy trình tài liệu phục vụ nghiệm thu và công bố học thuật.

---

## Slide 16 — Giới hạn nghiên cứu & Điều kiện ứng dụng lâm sàng

**Các giới hạn hiện tại của nghiên cứu:**
- **Đặc điểm dữ liệu:** Dữ liệu nghiên cứu được tổng hợp và chuẩn hóa từ các nguồn mở y sinh uy tín (Synthea, MTSamples); cần mở rộng thêm các tập kiểm thử đa cơ sở y tế trong tương lai.
- **Quy mô tập kiểm thử:** Đánh giá trên 302 mẫu độc lập chuẩn hóa; tuy đã phân bổ đều 4 nhóm bệnh nhưng vẫn cần xác thực trên các phân bố bệnh nhân đa dạng hơn.

**Ranh giới và Tuyên bố y đức:**  
Hệ thống là một **nghiên cứu học thuật nhằm phát triển nguyên mẫu hỗ trợ quyết định (Clinical Decision Support)**, tuyệt đối không đóng vai trò thay thế bác sĩ hay đưa ra quyết định điều trị tự động trên bệnh nhân thực tế. Mọi bước ứng dụng lâm sàng trong tương lai đều phải tuân thủ nghiêm ngặt các phê duyệt của Hội đồng Đạo đức trong nghiên cứu y sinh học.

---

## Slide 17 — Danh mục tài liệu tham khảo khoa học chính

1. **Hunik, M., et al. (2024).** *Diagnostic prediction models for primary care, based on artificial intelligence and electronic health records: a systematic review.* JMIR Preprints, 62862.
2. **Alsentzer, E., Murphy, J., Boag, W., et al. (2019).** *Publicly Available Clinical BERT Embeddings.* Proceedings of the 2nd Clinical Natural Language Processing Workshop, NAACL, pp. 72–78.
3. **Gorishniy, Y., Rubachev, I., Khrulkov, V., & Babenko, A. (2021).** *Revisiting Deep Learning Models for Tabular Data (FT-Transformer).* Advances in Neural Information Processing Systems (NeurIPS 2021), 34, pp. 18932–18943.
4. **Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018).** *CatBoost: unbiased boosting with categorical features.* Advances in Neural Information Processing Systems (NeurIPS 2018), 31, pp. 6638–6648.
5. **Collins, G. S., Dhiman, P., Andaur Navarro, C. L., et al. (2021).** *Protocol for development of a reporting guideline (TRIPOD-AI) and risk of bias tool (PROBAST-AI) for diagnostic and prognostic prediction model studies based on artificial intelligence.* BMJ Open, 11(7), e048008.
6. **Global Initiative for Chronic Obstructive Lung Disease (GOLD). (2024).** *Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease.*
7. **Global Initiative for Asthma (GINA). (2024).** *Global Strategy for Asthma Management and Prevention.*
