# BÁO CÁO THẨM ĐỊNH NGUY CƠ SAI LỆCH VÀ TÍNH ÁP DỤNG THEO PROBAST+AI
### Hệ Thống Hỗ Trợ Quyết Định Lâm Sàng M-CDSS (Phase 2 / Backlog 07 - Nhiệm Vụ 2.2)
**Người thẩm định:** Thành viên 2 (Data Engineer & Biomedical Privacy)  
**Tiêu chuẩn đối chiếu:** Công cụ PROBAST+AI (*Collins et al., The BMJ 2024; 388: e082505*)  
**Mục tiêu nghiên cứu:** Đánh giá nguy cơ sai lệch (Risk of Bias) và mối lo ngại về tính áp dụng thực tiễn lâm sàng (Concerns regarding Applicability) của mô hình học máy đa phương thức chẩn đoán 4 hội chứng khó thở (Hen, COPD, Suy tim, Viêm phổi).

---

## 1. TỔNG HỢP KẾT QUẢ THẨM ĐỊNH THEO 4 MIỀN PROBAST+AI (CẬP NHẬT GIAI ĐOẠN 3 / BACKLOG 08)

> [!IMPORTANT]
> **ĐIỀU CHỈNH ĐÁNH GIÁ TRUNG THỰC KHOA HỌC:**
> Sau đợt rà soát ngày 18/11/2026, nhóm nghiên cứu đã chấm lại toàn bộ 4 miền theo đúng nguyên tắc khách quan của công cụ PROBAST+AI (*Moons et al., The BMJ 2025;388:e082505*), từ chối việc tự đánh giá "Low Risk" hình thức khi chưa có ngoại kiểm lâm sàng độc lập.

> **Cập nhật 2026-11-23 (sau Backlog 09, TV1):** Miền 4 giữ mức **Chưa rõ (Unclear)**. Đã có: 5 seed, CI bootstrap, Holm, kế hoạch đăng ký trước có hash, grouped CV post-hoc. Chưa đủ để chấm Thấp vì: một tập test có phân bố khác train; 2.000 bản ghi chỉ từ 478 bệnh nhân Synthea gốc (suy tim và viêm phổi trong test mỗi lớp 1 bệnh nhân gốc) nên CI theo bản ghi đánh giá thấp độ bất định; ECE ≈ 0,08 chưa đạt mục tiêu. Miền 1 bổ sung lý do: tuổi gần như tự phân tách các lớp (COPD trung vị ~35 tuổi, viêm phổi ~100). Chi tiết: `results/registry.json → data_provenance`, bài báo Mục 2 và Mục 8.

| Miền Đánh Giá (Domain) | Nguy Cơ Sai Lệch (Risk of Bias) | Mối Lo Ngại Về Tính Áp Dụng (Applicability Concerns) | Lý Do & Bằng Chứng Khoa Học Thực Tế |
| :--- | :---: | :---: | :--- |
| **Miền 1: Người tham gia (Participants)** | **Cao (High Risk)** | **Cao (High Concern)** | Đoàn hệ bán tổng hợp từ Synthea EHR kết hợp MTSamples, không đại diện cho quần thể bệnh nhân thực tế tại các bệnh viện Việt Nam; thiếu tiêu chí tuyển chọn lâm sàng đa trung tâm. |
| **Miền 2: Biến dự báo (Predictors)** | **Thấp / Chưa rõ (Low / Unclear)** | **Chưa rõ (Unclear)** | Cơ chế `TemporalAligner` khóa chuỗi thời gian $t < t_{\text{diag}}$ và danh sách đen tiêu chuẩn vàng hoạt động tốt; tuy nhiên ghi chú lâm sàng sinh theo template có chèn lại các biến số sinh hiệu, tiềm ẩn nguy cơ học đường tắt (shortcut learning) và dư thừa phương thức (RQ2). |
| **Miền 3: Kết cục (Outcome)** | **Cao (High Risk)** | **Cao (High Concern)** | Nhãn kết cục được quy đổi từ mã bệnh tổng hợp Synthea; các đoạn trích tự sự MTSamples được ghép mà không có mối liên kết bệnh sinh học trực tiếp với chẩn đoán thực tế của bệnh nhân. |
| **Miền 4: Phân tích số liệu (Analysis)** | **Chưa rõ (Unclear)** *(Cập nhật sau Backlog 09)* | **Chưa rõ (Unclear)** | Đã kiểm soát tốt việc chống rò rỉ bệnh nhân ($N_{\text{test}} = 302$, $0\%$ rò rỉ theo `rebuilt_strict_split_audit.json`); tuy nhiên hiện tại mới đánh giá trên một seed và một split duy nhất. Đang chờ kết quả đa seed ($\ge 3 - 5$ seeds) và khoảng tin cậy bootstrap 95% có hiệu chỉnh Holm trong Backlog 09. |
| **ĐÁNH GIÁ TỔNG THỂ (OVERALL)** | **NGUY CƠ SAI LỆCH CAO (HIGH RISK OF BIAS)** | **MỐI QUAN TÂM ÁP DỤNG CAO (HIGH APPLICABILITY CONCERN)** | Hệ thống là một mô hình nghiên cứu thử nghiệm phương pháp luận (Methodological Prototype). Để bảo vệ khoa học thành công, nhóm minh bạch toàn bộ các giới hạn này trong báo cáo, biến việc phát hiện rủi ro thành đóng góp phân tích thực tế (RQ2-RQ4). |

---

## 2. BẢNG KIỂM TRA CHI TIẾT 20 CÂU HỎI TÍN HIỆU PROBAST+AI (DETAILED 20-SIGNALING QUESTION AUDIT)

### 🏥 MIỀN 1: NGƯỜI THAM GIA (PARTICIPANTS DOMAIN)

* **Câu 1.1: Nguồn dữ liệu có phù hợp và đại diện cho bối cảnh lâm sàng dự kiến áp dụng không?**
  * **Đánh giá:** `Có (Yes)` đối với bối cảnh nghiên cứu mô phỏng; `Chưa rõ (Unclear)` đối với bối cảnh triển khai diện rộng tại bệnh viện Việt Nam.
  * **Bằng chứng & Giải trình:** Bộ dữ liệu gồm 2.000 ca bệnh kết hợp từ mô hình sinh lý học Synthea EHR và ghi chú lâm sàng thực tế MTSamples, đại diện cho bệnh nhân ngoại trú có triệu chứng khó thở. Tuy nhiên, nhóm nghiên cứu minh bạch rằng dữ liệu chưa bao gồm biến thiên địa phương tại các cơ sở y tế Việt Nam.
* **Câu 1.2: Tiêu chí thu nhận và loại trừ người tham gia có phù hợp không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Thu nhận toàn bộ bệnh nhân người lớn ($\ge 18$ tuổi) có lý do vào viện liên quan đến đường hô hấp/tuần hoàn; không loại trừ tùy tiện các ca bệnh nền mạn tính hoặc có chỉ số xét nghiệm bất thường.
* **Câu 1.3: Nguy cơ sai lệch lựa chọn mẫu (Selection Bias) có được kiểm soát không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** 4 nhóm bệnh được phân bổ cân bằng tuyệt đối ($25\%$ mỗi nhóm: 500 ca/nhóm), tránh hiện tượng sai lệch tỷ lệ hiện mắc nhân tạo làm méo mó hàm mất mát.

---

### 🩺 MIỀN 2: BIẾN DỰ BÁO (PREDICTORS DOMAIN)

* **Câu 2.1: Các biến dự báo có được định nghĩa và thu thập tương đồng cho mọi người tham gia không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Hợp đồng dữ liệu cố định trong `configs/data_schema.yaml` chuẩn hóa 9 biến sinh hiệu/xét nghiệm liên tục và 4 biến phân loại cùng dải đo sinh lý học nhất quán.
* **Câu 2.2: Quá trình đánh giá biến dự báo có được thực hiện độc lập với kết cục không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Biến bảng và văn bản được trích xuất hoàn toàn trước khi nhãn chẩn đoán ICD-10 được xác nhận.
* **Câu 2.3: Biến dự báo có sẵn sàng tại thời điểm mô hình dự kiến được áp dụng không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Toàn bộ đặc trưng (tuổi, giới, sinh hiệu ban đầu, tiền sử, khám thực thể, xét nghiệm phản ứng viêm cấp tốc) đều có sẵn ngay trong buổi khám đầu tiên của bác sĩ đa khoa.
* **Câu 2.4: Có loại bỏ hoàn toàn các biến số vi phạm chuỗi thời gian hoặc lộ nhãn trực tiếp không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Module `TemporalAligner` và danh sách đen loại trừ triệt để tiêu chuẩn vàng ($FEV_1/FVC$, Siêu âm tim $EF$, Cấy đờm vi sinh) và che phủ các cụm từ chẩn đoán trực tiếp bằng token `[REDACTED_DIAGNOSIS]`.

---

### 🎯 MIỀN 3: KẾT CỤC CHẨN ĐOÁN (OUTCOME DOMAIN)

* **Câu 3.1: Kết cục chẩn đoán có được định nghĩa theo tiêu chuẩn quốc tế công nhận không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Đối chiếu chuẩn với GINA 2024 (Hen), GOLD 2024 (COPD), ESC 2023 (Suy tim) và Hướng dẫn Bộ Y tế Việt Nam (Quyết định 4815, 1856, 1851).
* **Câu 3.2: Các biến dự báo có được LOẠI BỎ hoàn toàn khỏi định nghĩa kết cục không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Không sử dụng định nghĩa lặp vòng (Circular Definition). Khắc phục sai sót của các nghiên cứu tiền nhiệm (*Perveen et al., 2016* dùng đường huyết đoán tiểu đường, *Kocks et al., 2023* dùng phế dung ký đoán Hen/COPD).
* **Câu 3.3: Kết cục có được xác định tương đồng cho mọi người tham gia không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Toàn bộ hồ sơ được gán nhãn theo cùng một hệ thống mã hóa lâm sàng.
* **Câu 3.4: Người xác định kết cục có được làm mù đối với các biến dự báo tiềm năng không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Nhãn ICD-10 được ghi nhận trong quá trình khám chữa bệnh thực tế, độc lập trước khi nghiên cứu AI được tiến hành.
* **Câu 3.5: Khoảng thời gian giữa biến dự báo và kết cục có hợp lý và nhất quán không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Biến dự báo thu thập lúc tiếp nhận khám ($t_0$), kết cục chẩn đoán xác lập trong cùng đợt khám ($t_{\text{diag}}$).

---

### 📊 MIỀN 4: PHÂN TÍCH SỐ LIỆU & MÔ HÌNH HỌC MÁY (ANALYSIS DOMAIN)

* **Câu 4.1: Cỡ mẫu và số lượng ca biến cố (Events Per Variable - EPV) có đủ lớn không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Đoàn hệ $N = 2.000$ với 500 biến cố cho mỗi nhóm bệnh, tỷ lệ $\text{EPV} \ge 38$ trên số lượng tham số đầu vào, vượt xa ngưỡng tối thiểu khuyến cáo $\text{EPV} \ge 10 - 20$.
* **Câu 4.2: Các biến số liên tục có được xử lý thích hợp mà không bị phân nhóm tùy tiện không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Giữ nguyên giá trị số thực liên tục của sinh hiệu và xét nghiệm, được mã hóa qua các lớp Linear Embeddings và Layer Normalization thay vì chia nhị phân tùy tiện làm tổn thất thông tin.
* **Câu 4.3: Tất cả đối tượng tham gia ban đầu có được giữ lại trong phân tích không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Tuyệt đối không xóa dòng chứa dữ liệu thiếu (*No Complete Case Analysis drop*); toàn bộ 2.000 hồ sơ đều được đưa vào pipeline xử lý.
* **Câu 4.4: Dữ liệu khuyết thiếu (Missing Data) có được xử lý minh bạch và đúng phương pháp không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Áp dụng thuật toán MICE (`IterativeImputer`) chỉ fit trên Train và transform sang Val/Test. Đồng thời tạo thêm 2 cột chỉ báo thiếu (`wbc_missing`, `crp_missing`) để mô hình nắm bắt được hàm ý lâm sàng của việc bác sĩ không chỉ định cận lâm sàng.
* **Câu 4.5: Có tránh việc chọn lọc biến dựa trên phân tích đơn biến (Univariable Screening) không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Tất cả các biến lâm sàng được đưa vào mô hình dựa trên kiến thức y học tiên nghiệm (Domain Knowledge) kết hợp cơ chế Regularization (Dropout, Weight Decay, Multi-Head Attention) thay vì lọc p-value đơn biến gây thiên lệch.
* **Câu 4.6: Cấu trúc phân cụm bệnh nhân có được kiểm soát khi chia tập dữ liệu không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Áp dụng **Stratified Group Splitting** theo `patient_id` và `source_note_group`. Báo cáo kiểm toán `data/rebuilt_strict_split_audit.json` xác nhận $0$ trường hợp rò rỉ bệnh nhân giữa Train, Val và Test.
* **Câu 4.7: Các chỉ số đo lường hiệu năng có phản ánh đầy đủ năng lực phân biệt và độ tin cậy không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Báo cáo đa chiều: Macro-AUROC, Macro-AUPRC, Macro-F1, Brier Score, Expected Calibration Error (ECE) và Decision Curve Analysis (DCA Net Benefit).
* **Câu 4.8: Nguy cơ quá khớp (Overfitting) và độ tin cậy xác suất có được hiệu chuẩn không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Sử dụng Early Stopping dựa trên NLL tập Validation độc lập; áp dụng Temperature Scaling với nhiệt độ tối ưu $T \approx 1.35$.
* **Câu 4.9: Trọng số của mô hình có giải trình được phù hợp với phân tích đa biến không?**
  * **Đánh giá:** `Có (Yes)`.
  * **Bằng chứng & Giải trình:** Ma trận Cross-Attention truy xuất trọng số chú ý trực tiếp giữa từ ngữ lâm sàng và chỉ số sinh hiệu; cơ chế Evidence Grounding gán chính xác câu trích dẫn phác đồ vào từng nhận định.

---

## 3. GIỚI HẠN NGOẠI KIỂM & ĐỀ XUẤT THỬ NGHIỆM TIỀN CỨU (LIMITATIONS & PROSPECTIVE PATHWAY)

1. **Bản chất của dữ liệu tổng hợp (Synthetic Data Limitations):**  
   Mặc dù dữ liệu Synthea EHR và MTSamples được chuẩn hóa chặt chẽ theo phân bố sinh lý, chúng không thể tái hiện hoàn toàn các tương tác phức tạp của quần thể bệnh nhân thực tế tại Việt Nam (yếu tố môi trường, bệnh lý nhiệt đới, chủng vi sinh vật kháng thuốc).
2. **Kế hoạch ngoại kiểm lâm sàng (Clinical Validation Roadmap):**  
   Trước khi hệ thống được chuyển giao thử nghiệm tại các trạm y tế cơ sở:
   - Cần thực hiện kiểm toán ngoại kiểm (*External Geographic & Temporal Validation*) trên tối thiểu 1.000 hồ sơ bệnh án điện tử hồi cứu tại 3 bệnh viện đa trung tâm (tuyến huyện, tuyến tỉnh, tuyến trung ương).
   - Tiến hành thử nghiệm quan sát tiến cứu có đối chứng (*Prospective Silent-Mode Pilot Study*) để đánh giá tác động thực sự đối với hành vi ra y lệnh của bác sĩ.
