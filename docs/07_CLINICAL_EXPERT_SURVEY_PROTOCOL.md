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
   │ 4. Tuyển dụng bác sĩ & Thu thập đánh giá thực │ [⏳] CHƯA THỰC HIỆN (PENDING)     │
   │    (Lý do: Đang chuẩn bị hồ sơ IRB và thỏa    │      Không thay thế bằng số liệu │
   │     thuận bảo mật với cơ sở khám bệnh)        │      đánh giá giả lập).          │
   └───────────────────────────────────────────────┴──────────────────────────────────┘
```

### Kế Hoạch Triển Khai Trong Giai Đoạn Tiếp Theo (Next Steps for Phase 3):
1. **Phối hợp Thành viên 1:** Tích hợp bộ quy tắc loại trừ dựa trên ý kiến sơ bộ của chuyên gia (ví dụ: tuổi $\le 20$ kèm không hút thuốc thì phạt nặng xác suất COPD).
2. **Phối hợp Thành viên 3:** Xây dựng cửa sổ Modal khảo sát (In-App Doctor Survey Widget) ngay trên giao diện Web bác sĩ (`frontend`) để khi thử nghiệm lâm sàng, bác sĩ có thể bấm 1-click chấm điểm trực tiếp cho ca bệnh mà không cần dùng phiếu giấy.

