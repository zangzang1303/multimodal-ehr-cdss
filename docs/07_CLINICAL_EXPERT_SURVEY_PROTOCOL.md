# GIAO THỨC KHẢO SÁT CHUYÊN GIA LÂM SÀNG & PHIẾU ĐÁNH GIÁ ĐỊNH TÍNH (CLINICAL EXPERT SURVEY PROTOCOL & RUBRIC)
### Đánh Giá Định Tính Hệ Thống Hỗ Trợ Ra Quyết Định Lâm Sàng Đa Phương Thức (M-CDSS)
**Quy chuẩn tuân thủ:** [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) & [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505)  
**Phụ trách:** Thành viên 2 (Biomedical Data Engineer & Privacy)  
**Tình trạng thực tế:** Đã hoàn thiện giao thức chuẩn hóa; **Khảo sát thực địa trên người đánh giá lâm sàng đang ở trạng thái CHƯA THỰC HIỆN (Pending Clinician Enrollment & IRB Ethics Clearance)** — không điền dữ liệu giả định theo quy tắc liêm chính khoa học.

---

> [!IMPORTANT]
> **TUYÊN BỐ LIÊM CHÍNH KHOA HỌC (SCIENTIFIC INTEGRITY DISCLAIMER):**
> Theo tiêu chuẩn nghiệm thu của Backlog 06: *"Nếu có bác sĩ/ca bệnh đủ điều kiện, báo cáo số người, số ca, cách chọn và kết quả; nếu không, ghi rõ chưa thực hiện, không thay bằng nhận xét giả định."*
> Toàn bộ dữ liệu ca bệnh nghiên cứu hiện tại được trích xuất từ tập dữ liệu tổng hợp / phi nhận danh (Synthea & MTSamples). Do đó, tài liệu này thiết lập toàn bộ quy trình, phương pháp chọn mẫu, phiếu khảo sát thang đo Likert và giao thức làm mù để sẵn sàng triển khai ngay khi hoàn tất thủ tục mời bác sĩ và được hội đồng đạo đức y sinh phê duyệt.

---

## 1. MỤC TIÊU VÀ ĐỐI TƯỢNG ĐÁNH GIÁ (SURVEY OBJECTIVES)

Khảo sát được thiết kế nhằm đánh giá 3 trụ cột lâm sàng của hệ thống M-CDSS thông qua góc nhìn của bác sĩ hành nghề thực tế:
1. **Mức độ chính xác và hợp lý lâm sàng (Diagnostic Accuracy & Clinical Plausibility):** Khả năng phân tầng nguy cơ và thứ tự ưu tiên của chẩn đoán sơ bộ do mô hình đề xuất.
2. **Tính thuyết phục của bằng chứng trích dẫn (Evidence Grounding & Explainability):** Mức độ chính xác của các câu chứng cứ y khoa được highlight trong văn bản bệnh án (evidence spans: triệu chứng cơ năng, thực thể, tiền sử).
3. **Tính hữu ích thực tiễn của hướng dẫn điều trị (Guideline Utility & Actionability):** Giá trị gia tăng của việc trích dẫn trực tiếp các phác đồ quốc tế (GINA 2024, GOLD 2024, ESC 2023) đối với quyết định chỉ định cận lâm sàng và phác đồ can thiệp ban đầu.

---

## 2. NGUỒN DỮ LIỆU, QUYỀN SỬ DỤNG VÀ THỦ TỤC ĐẠO ĐỨC (DATA GOVERNANCE & IRB)

| Hạng mục | Quy định kiểm soát của hệ thống M-CDSS |
| :--- | :--- |
| **Nguồn gốc ca bệnh (Data Provenance)** | Tập kiểm thử độc lập `data/processed_rebuilt_strict/test.parquet` (xây dựng từ kho dữ liệu Synthea Primary Care và MTSamples Clinical Transcripts). |
| **Tuyên bố dữ liệu tổng hợp (Synthetic Disclosure)** | **Tất cả các ca bệnh đều được ghi rõ là ca bệnh tổng hợp/nghiên cứu**. Tuyệt đối không mạo nhận là bệnh án của bệnh nhân thực tế tại bệnh viện khi chưa có thỏa thuận dữ liệu y tế (DUA). |
| **Quyền riêng tư & Bảo vệ danh tính (De-identification)** | Toàn bộ các định danh cá nhân (Họ tên, CCCD/SSN, Địa chỉ, Số điện thoại, Cơ sở y tế) đều đã được mã hóa giả danh tính (Pseudonymized / Masked) theo chuẩn HIPAA Safe Harbor Method. |
| **Hội đồng đạo đức (IRB / Ethics Approval)** | Trước khi mời các bác sĩ chuyên khoa bên ngoài tham gia đánh giá, nhóm nghiên cứu phải nộp hồ sơ xin miễn trừ hoặc phê duyệt đạo đức nghiên cứu y sinh (IRB Exemption / Full Review) tại cơ quan chủ quản. |

---

## 3. PHƯƠNG PHÁP CHỌN MẪU VÀ QUY TRÌNH LÀM MÙ (SAMPLING & BLINDED REVIEW DESIGN)

```
                       QUY TRÌNH ĐÁNH GIÁ LÀM MÙ ĐÔI (DOUBLE-BLIND PROTOCOL)
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 1. CHỌN MẪU PHÂN TẦNG CÂN BẰNG (STRATIFIED COHORT SAMPLING)                            │
  │ • Lấy ngẫu nhiên N = 20 ca bệnh từ tập Holdout Test (mỗi bệnh lý 5 ca).               │
  │ • Tỷ lệ phân bổ: 60% ca mô hình dự đoán đúng (TP) và 40% ca mô hình dự đoán sai (FP). │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │ 2. XÓA BỎ THÔNG TIN NGUỒN & NHÃN HỆ THỐNG (BLINDING & MASKING)                         │
  │ • Bác sĩ đánh giá KHÔNG được xem nhãn gốc của dữ liệu.                                 │
  │ • Bác sĩ đánh giá KHÔNG biết trước ca nào mô hình đoán đúng, ca nào đoán sai.          │
  │ • Thứ tự các ca bệnh được xáo trộn ngẫu nhiên (Randomized sequence).                  │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │ 3. HỘI ĐỒNG BÁC SĨ ĐÁNH GIÁ ĐỘC LẬP (EXPERT PANEL CRITERIA)                           │
  │ • Tối thiểu 03 Bác sĩ: Bác sĩ Nội khoa tổng quát, Bác sĩ Hô hấp, Bác sĩ Tim mạch.     │
  │ • Tiêu chí: Có chứng chỉ hành nghề (CCHN) và $\ge 2$ năm kinh nghiệm lâm sàng.         │
  │ • Đánh giá độc lập từng ca bệnh trên phiếu khảo sát chuẩn hóa (không trao đổi trước).  │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. PHIẾU KHẢO SÁT CHUYÊN GIA LÂM SÀNG (CLINICAL EVALUATION RUBRIC)

> **Hướng dẫn dành cho Bác sĩ:**  
> Bác sĩ vui lòng đọc tóm tắt bệnh án (bao gồm sinh hiệu, xét nghiệm máu ban đầu và ghi chú lâm sàng), đối chiếu với phân tích do hệ thống CDSS đưa ra và chấm điểm theo thang đo Likert 5 mức độ:  
> * **1 điểm:** Hoàn toàn không đồng ý / Rất kém / Tiềm ẩn nguy cơ lâm sàng  
> * **2 điểm:** Không đồng ý / Kém / Chưa đủ tin cậy  
> * **3 điểm:** Trung tính / Chấp nhận được ở mức sơ bộ  
> * **4 điểm:** Đồng ý / Tốt / Có giá trị tham khảo lâm sàng rõ rệt  
> * **5 điểm:** Hoàn toàn đồng ý / Rất tốt / Rất chuẩn xác theo thực hành lâm sàng  

---

### PHẦN I: THÔNG TIN NGƯỜI ĐÁNH GIÁ (EVALUATOR PROFILE)
1. **Mã số bác sĩ (Ẩn danh):** `[ EVAL_MD_01 / EVAL_MD_02 / ... ]`
2. **Chuyên khoa công tác:** 
   - [ ] Nội Tổng Quát / Y Học Gia Đình
   - [ ] Hô Hấp
   - [ ] Tim Mạch
   - [ ] Hồi Sức Cấp Cứu (ICU/Emergency)
3. **Số năm kinh nghiệm lâm sàng sau tốt nghiệp:** `[ ... ]` năm
4. **Học hàm / Học vị:** Bác sĩ / Thạc sĩ / BS CKI / BS CKII / Tiến sĩ

---

### PHẦN II: NỘI DUNG ĐÁNH GIÁ TỪNG CA BỆNH (CASE-BY-CASE EVALUATION FORM)
*Mỗi bác sĩ hoàn thành phiếu này cho 20 ca bệnh trong bộ hồ sơ thẩm định.*

**Mã ca bệnh:** `[ CASE_ID_XX ]` | **Thời gian hoàn thành:** `[ ... ]` phút

#### Trụ Cột 1: Mức Độ Chính Xác Của Dự Đoán Sơ Bộ (Diagnostic Precision)
| STT | Tiêu chí đánh giá | 1 (Rất kém) | 2 (Kém) | 3 (T.Tính) | 4 (Tốt) | 5 (Rất tốt) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Q1.1** | Thứ tự phân tầng xác suất chẩn đoán sơ bộ (Top-1 và Top-2) phù hợp với bức tranh lâm sàng tổng thể của bệnh nhân. | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q1.2** | Mức độ tin cậy xác suất (%) được hiệu chuẩn (Calibrated Probability) phản ánh đúng độ phức tạp và bất định của ca bệnh, không gây chủ quan hoặc tự tin giả tạo. | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q1.3** | Trong các ca bệnh chồng lấp (Hen - COPD hoặc Suy tim có ran rít), mô hình không loại trừ hoàn toàn các chẩn đoán phân biệt quan trọng. | [ ] | [ ] | [ ] | [ ] | [ ] |

#### Trụ Cột 2: Tính Thuyết Phục Của Bằng Chứng Highlight (Evidence Grounding)
| STT | Tiêu chí đánh giá | 1 (Rất kém) | 2 (Kém) | 3 (T.Tính) | 4 (Tốt) | 5 (Rất tốt) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Q2.1** | Các đoạn văn bản được highlight trong phần bệnh án (`evidence spans`) thực sự là các triệu chứng hoặc dấu hiệu thực thể có giá trị định hướng chẩn đoán. | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q2.2** | Hệ thống không highlight các thông tin nhiễu, thông tin hành chính hoặc các câu không liên quan đến bệnh lý hô hấp - tim mạch. | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q2.3** | Mức độ dễ hiểu và tính trực quan của giao diện hiển thị câu chứng cứ giúp bác sĩ tiết kiệm thời gian đọc lướt hồ sơ bệnh án. | [ ] | [ ] | [ ] | [ ] | [ ] |

#### Trụ Cột 3: Tính Hữu Ích Của Phác Đồ GINA / GOLD / ESC (Guideline Utility)
| STT | Tiêu chí đánh giá | 1 (Rất kém) | 2 (Kém) | 3 (T.Tính) | 4 (Tốt) | 5 (Rất tốt) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Q3.1** | Việc trích dẫn các tiêu chuẩn chẩn đoán quốc tế (GINA 2024 / GOLD 2024 / ESC 2023) giúp bác sĩ dễ dàng ra quyết định chỉ định cận lâm sàng tiếp theo (X-quang, Hô hấp ký, Siêu âm tim). | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q3.2** | Lời khuyên phác đồ điều trị ban đầu do hệ thống đề xuất là an toàn, không có tương tác thuốc nguy hiểm hoặc chống chỉ định rõ ràng. | [ ] | [ ] | [ ] | [ ] | [ ] |
| **Q3.3** | Hệ thống cảnh báo rõ ràng giới hạn của AI và nhắc nhở bác sĩ phải thăm khám trực tiếp trước khi đưa ra y lệnh chính thức. | [ ] | [ ] | [ ] | [ ] | [ ] |

---

### PHẦN III: CÂU HỎI MỞ VÀ Ý KIẾN ĐÓNG GÓP (QUALITATIVE FEEDBACK)
1. *Bác sĩ cảm thấy điểm hạn chế lớn nhất của hệ thống hỗ trợ ra quyết định này trong bối cảnh phòng khám ngoại trú là gì?*  
   `....................................................................................................`
2. *Bác sĩ có sẵn sàng sử dụng công cụ này như một trợ lý hội chẩn bước hai (Second-opinion Assistant) tại bàn khám không? Vì sao?*  
   `....................................................................................................`

---

## 5. BÁO CÁO THỰC TRẠNG VÀ KẾ HOẠCH HÀNH ĐỘNG (STATUS REPORT & ROLLOUT ROADMAP)

```
                            BÁO CÁO HIỆN TRẠNG TRIỂN KHAI
   ┌───────────────────────────────────────────────┬──────────────────────────────────┐
   │ HẠNG MỤC                                      │ TÌNH TRẠNG HIỆN TẠI (STATUS)     │
   ├───────────────────────────────────────────────┼──────────────────────────────────┤
   │ 1. Bộ câu hỏi khảo sát Likert Scale 1-5       │ [✓] ĐÃ HOÀN THÀNH & BAN HÀNH     │
   │ 2. Giao thức làm mù đôi & chọn mẫu phân tầng  │ [✓] ĐÃ THIẾT KẾ & ĐÓNG GÓI       │
   │ 3. Khung bảo vệ quyền riêng tư HIPAA          │ [✓] ĐÃ PHÊ DUYỆT (Tập Test ẩn)   │
   │ 4. Tuyển dụng bác sĩ & Thu thập đánh giá thực │ [⚠️] CHƯA THỰC HIỆN              │
   │    (Số lượng bác sĩ đồng ý chính thức < 2;     │      Ghi nhận minh bạch theo     │
   │     không thay thế bằng điểm số giả định)      │      quy chuẩn TRIPOD+AI)        │
   │ 5. Lộ trình ngoại kiểm PhysioNet / MIMIC-IV   │ [✓] ĐÃ HOÀN TẤT THIẾT KẾ LỘ TRÌNH│
   └───────────────────────────────────────────────┴──────────────────────────────────┘
```

> [!IMPORTANT]
> **MINH BẠCH VỀ TÌNH TRẠNG KHẢO SÁT CHUYÊN GIA LÂM SÀNG:**  
> Theo quy chuẩn nghiệm thu Task 2.5 (Backlog 09) và nguyên tắc liêm chính khoa học: *"Chỉ báo cáo kết quả khảo sát khi có $\ge 2$ bác sĩ hành nghề chính thức tham gia đánh giá độc lập; nếu chưa đủ, bắt buộc ghi rõ 'CHƯA THỰC HIỆN', tuyệt đối không được tự bịa số liệu Likert hay nhận xét giả định"*.  
> Hiện tại, do nhóm nghiên cứu chưa hoàn tất ký kết DUA lâm sàng và chưa tuyển đủ tối thiểu 02 bác sĩ chuyên khoa có chứng chỉ hành nghề (CCHN) hoàn thành trọn vẹn 20 ca đánh giá mù đôi, khảo sát được bảo lưu ở trạng thái **CHƯA THỰC HIỆN**.  
> Khi đạt đủ điều kiện tuyển mộ ($\ge 2$ bác sĩ), nhóm sẽ tiến hành thu thập và tính toán độ đồng thuận liên quan sát viên (Inter-rater Agreement) bằng hệ số **Krippendorff's Alpha ($\alpha$)** và **Fleiss' Kappa ($\kappa$)** cho thang đo thứ bậc nhiều người đánh giá.

---

## 6. LỘ TRÌNH DỮ LIỆU THỰC & NGOẠI KIỂM BỆNH VIỆN QUA PHYSIONET MIMIC-IV (REAL-WORLD EXTERNAL VALIDATION ROADMAP)

Để giải quyết triệt để ranh giới giữa dữ liệu tổng hợp (Synthea/MTSamples) và thực hành lâm sàng thực địa, nhóm nghiên cứu đã thiết lập lộ trình ngoại kiểm độc lập (External Hospital Validation) sử dụng cơ sở dữ liệu hồi cứu quy mô lớn **MIMIC-IV** và **MIMIC-IV-Note** (Beth Israel Deaconess Medical Center, Boston, MA):

```
                     LỘ TRÌNH 4 BƯỚC NGOẠI KIỂM PHYSIONET MIMIC-IV
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ BƯỚC 1: ĐÀO TẠO ĐẠO ĐỨC & CHỨNG CHỈ CITI (CITI TRAINING PROGRAM)                       │
  │ • Hoàn thành khóa học: "Data or Specimens Only Research" trên CITI Program.            │
  │ • Nộp chứng chỉ cho PhysioNet để đạt tư cách "Credentialed User".                      │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │ BƯỚC 2: KÝ THỎA THUẬN SỬ DỤNG DỮ LIỆU (DUA - DATA USE AGREEMENT)                       │
  │ • Ký cam kết bảo mật: không tái nhận danh bệnh nhân, không chia sẻ dữ liệu ra ngoài.   │
  │ • Được cấp quyền truy cập BigQuery / Cloud Storage cho MIMIC-IV v2.2 & MIMIC-IV-Note.  │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │ BƯỚC 3: TRÍCH XUẤT TẬP CON NGOẠI KIỂM THEO 4 MÃ ICD-10 ĐÍCH                           │
  │ Trích xuất bệnh nhân nhập viện ban đầu có chẩn đoán xuất viện (diagnoses_icd) tương ứng:│
  │ • Hen phế quản (Asthma):           ICD-10 J45 (J45.0 - J45.9)                          │
  │ • Bệnh phổi tắc nghẽn mạn (COPD):   ICD-10 J44 (J44.0, J44.1, J44.9)                   │
  │ • Suy tim sung huyết (HF):         ICD-10 I50 (I50.1, I50.2x, I50.3x, I50.9)           │
  │ • Viêm phổi mắc phải (Pneumonia):  ICD-10 J18 (J18.0, J18.1, J18.9)                    │
  │ Khai thác: Sinh hiệu cấp cứu đầu tiên (ED vitals) + Ghi chú tiếp nhận (Discharge/ED).   │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │ BƯỚC 4: THỰC THI KIỂM ĐỊNH NGOẠI KIỂM KHÔNG HUẤN LUYỆN LẠI (ZERO-SHOT TRANSPORTABILITY)│
  │ • Nạp checkpoint mô hình M-CDSS huấn luyện trên Synthetic EHR.                         │
  │ • Suy luận trực tiếp trên tập trích xuất MIMIC-IV (N = 1000 ca, 250 ca/bệnh lý).        │
  │ • Đo lường độ suy giảm hiệu năng ngoại kiểm: ΔAUROC, ΔAUPRC, Calibration Drift (ECE).  │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

### Kế hoạch công bố khoa học (Scientific Paper Transition):
Trong bản thảo bài báo khoa học (Mục *Limitations & Future Directions*), nhóm sẽ tuyên bố rõ ràng:
1. Nghiên cứu hiện tại đã hoàn thiện toàn diện về mặt kiến trúc đa phương thức, kiểm định nội bộ đa chiều (DCA, Missing Modality, Subgroup Fairness, Temporal Generalization).
2. Quy trình trích xuất và giao thức ngoại kiểm MIMIC-IV 4 nhóm ICD-10 đã được đóng gói hoàn chỉnh thành mã nguồn và sẽ được kích hoạt ngay khi hoàn tất phê duyệt tài khoản PhysioNet Credentialed.

