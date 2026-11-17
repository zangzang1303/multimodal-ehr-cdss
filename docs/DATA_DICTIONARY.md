# TỪ ĐIỂN DỮ LIỆU ĐA PHƯƠNG THỨC (CLINICAL DATA DICTIONARY)
### M-CDSS Phase 2 / Backlog 07 - Nhiệm vụ 2.3 (Data Engineer & Biomedical Privacy)

---

## 1. TỔNG QUAN HỢP ĐỒNG DỮ LIỆU (DATA CONTRACT OVERVIEW)
Bộ dữ liệu nghiên cứu M-CDSS bao gồm $N = 2.000$ hồ sơ bệnh án đa phương thức được chuẩn hóa từ nguồn Synthea EHR và MTSamples. Mỗi bản ghi kết hợp dữ liệu bảng có cấu trúc ($\bm{x}_{\text{tab}} \in \mathbb{R}^{13}$), văn bản bệnh án tự do ($T$), và nhãn chẩn đoán xác định ($y \in \{0, 1, 2, 3\}$).

---

## 2. BIẾN SỐ BẢNG LIÊN TỤC (NUMERICAL CLINICAL PREDICTORS)

| Tên Biến (Variable) | Kiểu Dữ Liệu | Đơn Vị Đo | Dải Sinh Lý Hợp Lệ | Tỷ Lệ Khuyết Thiếu | Cơ Chế Xử Lý & Ý Nghĩa Lâm Sàng |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `age` | `float` | Năm (Years) | $[18.0, 100.0]$ | $0.0\%$ | Độ tuổi người bệnh lúc nhập viện. Bệnh nhân $>89$ tuổi được nhóm lại thành $90$ theo chuẩn HIPAA Safe Harbor. |
| `systolic_bp` | `float` | mmHg | $[80.0, 220.0]$ | $0.0\%$ | Huyết áp tâm thu đo lúc tiếp nhận ban đầu. Tăng cao trong cơn suy tim cấp thể tăng huyết áp. |
| `diastolic_bp` | `float` | mmHg | $[50.0, 130.0]$ | $0.0\%$ | Huyết áp tâm trương lúc tiếp nhận ban đầu. |
| `heart_rate` | `float` | nhịp/phút (bpm) | $[40.0, 180.0]$ | $0.0\%$ | Tần số tim đo đạc khi nghỉ. Nhịp nhanh phản ánh phản ứng bù trừ suy tim hoặc sốt nhiễm trùng. |
| `respiratory_rate` | `float` | lần/phút | $[10.0, 45.0]$ | $0.0\%$ | Tần số thở. Thở nhanh nông ($\ge 24$ lần/phút) là dấu hiệu kinh điển của suy hô hấp cấp và viêm phổi. |
| `spo2` | `float` | $\%$ | $[70.0, 100.0]$ | $0.0\%$ | Độ bão hòa oxy mao mạch ngoại vi qua SpO2. $\text{SpO}_2 < 92\%$ chỉ thị thiếu oxy mô nặng. |
| `temperature` | `float` | $^\circ\text{C}$ | $[35.0, 41.5]$ | $0.0\%$ | Thân nhiệt đo tại nách/miệng. Sốt $>38.0^\circ\text{C}$ hướng mạnh tới Viêm phổi mắc phải cộng đồng. |
| `wbc_count` | `float` | $\times 10^9/\text{L}$ | $[2.0, 35.0]$ | **$20.5\%$** | Số lượng bạch cầu máu ngoại vi. Tăng cao trong nhiễm trùng cấp tính; gán bằng thuật toán MICE. |
| `crp` | `float` | mg/L | $[0.1, 250.0]$ | **$22.4\%$** | Nồng độ Protein phản ứng C trong huyết thanh. Chỉ dấu viêm nhạy bén phân biệt viêm phổi và hen không nhiễm khuẩn; gán bằng MICE. |

---

## 3. BIẾN SỐ PHÂN LOẠI & YẾU TỐ NGUY CƠ (CATEGORICAL PREDICTORS)

| Tên Biến (Variable) | Kiểu Dữ Liệu | Mã Hóa (Encoding) | Tỷ Lệ Khuyết | Ý Nghĩa Lâm Sàng & Phân Bố |
| :--- | :---: | :---: | :---: | :--- |
| `gender` | `float` | `0.0: Nam (M)`<br>`1.0: Nữ (F)`<br>`2.0: Khác` | $0.0\%$ | Giới tính sinh học người bệnh ($51.2\%$ Nam, $48.8\%$ Nữ). |
| `smoking_status` | `float` | `0.0: Chưa từng hút (NEVER)`<br>`1.0: Đã bỏ (FORMER)`<br>`2.0: Đang hút (CURRENT)` | $0.0\%$ | Tiền sử tiếp xúc khói thuốc lá. Yếu tố nguy cơ hàng đầu gây tắc nghẽn luồng khí cố định trong COPD. |
| `history_hypertension` | `float` | `0.0: Không`<br>`1.0: Có tiền sử` | $0.0\%$ | Tiền sử bệnh tăng huyết áp mạn tính. Yếu tố nguy cơ gây suy tim phân suất tống máu bảo tồn (HFpEF). |
| `history_diabetes` | `float` | `0.0: Không`<br>`1.0: Có tiền sử` | $0.0\%$ | Tiền sử đái tháo đường Type 2. Làm tăng nguy cơ tổn thương vi mạch tim và biến chứng phổi. |

---

## 4. BIẾN CHỈ BÁO KHUYẾT THIẾU (MISSINGNESS INDICATORS)

| Tên Biến (Variable) | Kiểu Dữ Liệu | Giá Trị Mã Hóa | Ý Nghĩa Kỹ Thuật & Lâm Sàng |
| :--- | :---: | :---: | :--- |
| `wbc_missing` | `float` | `1.0` nếu khuyết, `0.0` nếu có | Đánh dấu bản ghi ban đầu bị khuyết xét nghiệm bạch cầu WBC. Giúp mô hình nhận biết bác sĩ lâm sàng không nghi ngờ nhiễm khuẩn cấp. |
| `crp_missing` | `float` | `1.0` nếu khuyết, `0.0` nếu có | Đánh dấu bản ghi ban đầu bị khuyết xét nghiệm protein phản ứng C. |

---

## 5. PHƯƠNG THỨC VĂN BẢN TỰ DO (FREE-TEXT CLINICAL NOTE)

| Trường Văn Bản | Cấu Trúc Nội Dung | Quy Trình Tiền Xử Lý \& Khử Định Danh |
| :--- | :--- | :--- |
| `clinical_note` / `text` | Ghi chú hội chẩn lâm sàng mô tả:<br>1. *Lý do vào viện (Chief Complaint)*<br>2. *Bệnh sử diễn tiến (History of Present Illness)*<br>3. *Tiền sử dị ứng \& dùng thuốc (Medications)*<br>4. *Dấu hiệu khám thực thể (Physical Exam: ran ẩm, ran nổ, ran ngáy, phù mắt cá)* | - Loại bỏ 18 định danh cá nhân theo HIPAA Safe Harbor.<br>- Thay thế bằng surrogate tokens: `[REDACTED_NAME]`, `[REDACTED_DATE]`, `[REDACTED_PHONE]`, `[REDACTED_HOSPITAL]`.<br>- Khóa chuỗi thời gian: loại bỏ hoàn toàn các ghi chú diễn tiến sau mốc $t_{\text{diag}}$.<br>- Che phủ từ khóa lộ nhãn bằng `[REDACTED_DIAGNOSIS]`. |

---

## 6. NHÃN KẾT CỤC CHẨN ĐOÁN MỤC TIÊU (DIAGNOSTIC OUTCOME TARGET)

| Mã Nhãn (`diagnosis_label`) | Tên Bệnh Lý Quốc Tế | Tiêu Chuẩn Vàng Đối Chiếu | Tiêu Chuẩn Lâm Sàng Ban Đầu |
| :---: | :--- | :--- | :--- |
| `0` | **Hen Phế Quản (ASTHMA)** | Hướng dẫn **GINA 2024** | Cơn khó thở khò khè biến thiên ngày đêm, nặng về đêm/sáng sớm, tiền sử cơ địa dị ứng, đáp ứng tốt với thuốc giãn phế quản tác dụng nhanh SABA. |
| `1` | **Bệnh Phổi Tắc Nghẽn Mạn Tính (COPD)** | Hướng dẫn **GOLD 2024** | Khó thở tiến triển liên tục khi gắng sức, ho khạc đờm mạn tính, tiền sử hút thuốc lá nặng (>10 bao-năm), lồng ngực hình thùng, rì rào phế nang giảm. |
| `2` | **Suy Tim Sung Huyết (HEART_FAILURE)** | Hướng dẫn **ESC 2023** | Khó thở kịch phát về đêm, khó thở khi nằm phẳng, phù mềm ấn lõm hai chi dưới, tĩnh mạch cổ nổi, tiếng T3 gallop hoặc ran ẩm đáy phổi hai bên. |
| `3` | **Viêm Phổi Mắc Phải Cộng Đồng (PNEUMONIA)** | Hướng dẫn **Bộ Y tế (QĐ 4815)** \& ATS | Khởi phát cấp tính với sốt cao rét run, đau ngực kiểu màng phổi, ho có đờm mủ đục hoặc đờm rỉ sắt, hội chứng đông đặc phổi (ran nổ khu trú, rung thanh tăng). |

---

## 7. QUẢN LÝ PHÂN CHIA VÀ TOÀN VẸN ĐOÀN HỆ (SPLIT & GOVERNANCE)

* **Tập Huấn Luyện (Train Split):** $N = 1.425$ ($71.3\%$), lưu tại `data/processed/train.parquet`.
* **Tập Kiểm Định (Validation Split):** $N = 273$ ($13.7\%$), lưu tại `data/processed/val.parquet`.
* **Tập Kiểm Thử Độc Lập (Holdout Test Split):** $N = 302$ ($15.1\%$), lưu tại `data/processed/test.parquet`.
* **Kiểm toán Chống Rò Rỉ:** Phân chia theo `StratifiedGroupKFold` trên cặp nhóm `(source_patient_group, source_note_group)`. File kiểm toán `data/rebuilt_strict_split_audit.json` xác nhận giao số $\mathcal{P}_{\text{train}} \cap \mathcal{P}_{\text{val}} \cap \mathcal{P}_{\text{test}} = \emptyset$.
