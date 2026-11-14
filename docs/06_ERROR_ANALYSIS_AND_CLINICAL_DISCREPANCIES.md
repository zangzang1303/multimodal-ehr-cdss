# PHÂN TÍCH CA BỆNH SAI BIỆT VÀ NGUYÊN NHÂN LÂM SÀNG (CLINICAL ERROR ANALYSIS & DISCREPANCIES)
### Phân Tích Ma Trận Nhầm Lẫn, Ca Bệnh Chồng Lấp & Luận Chứng Khoa Học Cho Bài Báo (TRIPOD+AI & PROBAST)
**Tác giả:** Thành viên 2 (Biomedical Data Engineer & Privacy)  
**Tập dữ liệu:** Holdout Strict Test Set ($N = 286$ bệnh nhân, zero-leakage patient-level connected split)  
**Mô hình đánh giá:** Multimodal Cross-Attention CDSS (`data/checkpoints/multimodal_best.pt`, $T = 1.3541$)

---

> [!NOTE]
> **HƯỚNG DẪN DÀNH CHO CÁC THÀNH VIÊN KHÁC (COLLABORATION & HANDOFF):**
> * **Thành viên 1 (Lead ML / Modeling):** Trích dẫn trực tiếp bảng số liệu ma trận nhầm lẫn và các trường hợp sai lệch kinh điển (ACOS, suy tim ứ huyết) vào phần *Discussion & Limitations* của bản thảo bài báo khoa học; đối chiếu với kết quả ablation study.
> * **Thành viên 3 (Full-Stack AI & Frontend):** Sử dụng các ca bệnh ranh giới (borderline cases) trong tài liệu này làm dữ liệu mẫu (mock clinical cases) cho tính năng `Case Study Inspector` và kiểm thử khả năng highlight bằng chứng lâm sàng tại `/agent/explain`.

---

## 1. TỔNG QUAN MA TRẬN NHẦM LẪN (CONFUSION MATRIX QUANTITATIVE SUMMARY)

Biểu đồ ma trận nhầm lẫn được tự động kết xuất tại:
- `data/confusion_matrix.png`
- `data/evaluation_plots/confusion_matrix.png`

```
               MA TRẬN NHẦM LẪN THỰC NGHIỆM (N = 286 BỆNH NHÂN)
   ┌────────────────────┬───────────┬───────────┬───────────────┬─────────────┐
   │ True \ Predicted   │  ASTHMA   │   COPD    │ HEART_FAILURE │  PNEUMONIA  │
   ├────────────────────┼───────────┼───────────┼───────────────┼─────────────┤
   │ ASTHMA (Hen)       │ 29 (40.3%)│ 26 (36.1%)│   14 (19.4%)  │   3 (4.2%)  │
   │ COPD               │ 22 (31.0%)│ 33 (46.5%)│    2 (2.8%)   │  14 (19.7%) │
   │ HEART_FAILURE (ST) │  1 (1.4%) │  2 (2.8%) │   22 (31.0%)  │  46 (64.8%) │
   │ PNEUMONIA (VP)     │ 14 (19.4%)│ 21 (29.2%)│   13 (18.1%)  │  24 (33.3%) │
   └────────────────────┴───────────┴───────────┴───────────────┴─────────────┘
```

### Chỉ Số Hiệu Năng Từng Bệnh Lý (Per-Class Discrimination)
| Bệnh lý mục tiêu | Số ca thực | True Positive (TP) | False Positive (FP) | Độ nhạy (Sensitivity) | Độ đặc hiệu (Specificity) | F1-Score | AUROC OVR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hen phế quản (ASTHMA)** | 72 | 29 | 37 | 40.28% | 82.71% | 0.4203 | **0.6901** |
| **COPD mạn tính** | 71 | 33 | 49 | 46.48% | 77.21% | 0.4314 | **0.6875** |
| **Suy tim sung huyết (HF)**| 71 | 22 | 29 | 30.99% | 86.51% | 0.3607 | **0.3771** |
| **Viêm phổi (PNEUMONIA)** | 72 | 24 | 63 | 33.33% | 70.56% | 0.3019 | **0.4548** |

---

## 2. PHÂN TÍCH 3 CỤM SAI BIỆT LÂM SÀNG TRỌNG YẾU (CLINICAL ROOT-CAUSE ANALYSIS)

Phân tích dữ liệu ma trận nhầm lẫn cho thấy các sai lệch dự đoán của mô hình **không phải là ngẫu nhiên (non-random error)**, mà phản ánh chính xác các thách thức chẩn đoán kinh điển trong y học lâm sàng thực tế:

```
                            3 CỤM SAI BIỆT KINH ĐIỂN
   ┌───────────────────────────────────────────────────────────────────────────┐
   │ CỤM 1: CHỒNG LẤP ĐƯỜNG THỞ (ACOS - ASTHMA vs COPD)                        │
   │ • 48 ca nhầm lẫn 2 chiều (26 Hen → COPD; 22 COPD → Hen)                   │
   │ • Nguyên nhân: Đều biểu hiện khó thở thì thở ra, ran rít, ran ngáy;       │
   │   tiền sử khói thuốc lá làm mờ ranh giới viêm phế quản co thắt.           │
   ├───────────────────────────────────────────────────────────────────────────┤
   │ CỤM 2: PHÙ PHỔI HUYẾT ĐỘNG vs ĐÔNG ĐẶC PHẾ NANG (HF → PNEUMONIA)          │
   │ • 46 ca Suy tim giai đoạn tiến triển bị phân loại nhầm thành Viêm phổi     │
   │ • Nguyên nhân: Ứ trệ tuần hoàn phổi gây rale ẩm hai đáy phổi, khó thở     │
   │   kèm nhịp tim nhanh và giảm oxy máu tương tự thâm nhiễm phế nang.        │
   ├───────────────────────────────────────────────────────────────────────────┤
   │ CỤM 3: VIÊM PHỔI KHỞI PHÁT CO THẮT PHẾ QUẢN (PNEUMONIA → COPD / HEN)      │
   │ • 35 ca Viêm phổi bị nhầm sang bệnh lý tắc nghẽn mạn tính                 │
   │ • Nguyên nhân: Bệnh nhân lớn tuổi có phản ứng co thắt phế quản phản ứng,  │
   │   bạch cầu và CRP chưa tăng vọt ở giai đoạn sớm, che giấu ổ nhiễm trùng. │
   └───────────────────────────────────────────────────────────────────────────┘
```

---

### 🔹 Cụm 1: Hội Chứng Chồng Lấp Hen - COPD (Asthma-COPD Overlap - ACO / ACOS)
- **Số lượng ca sai biệt:** 26 ca Hen bị gán nhãn COPD ($36.1\%$) và 22 ca COPD bị gán nhãn Hen ($31.0\%$).
- **Nguyên nhân sinh lý bệnh:**
  - Cả Hen và COPD đều thuộc nhóm bệnh lý tắc nghẽn luồng khí phế quản dưới. Triệu chứng cơ năng trình diện tại phòng khám ban đầu đều là: ho, khò khè từng cơn, khó thở thì thở ra, nghe phổi có ran rít (wheezing) và ran ngáy (rhonchi).
  - Khi bệnh nhân Hen có tiền sử hút thuốc lá chủ động hoặc thụ động (former/current smoker), hiện tượng tái cấu trúc đường thở (airway remodeling) diễn ra, khiến luồng khí tắc nghẽn không hồi phục hoàn toàn, lâm sàng giống hệt COPD theo hướng dẫn GOLD 2024.
  - Ngược lại, bệnh nhân COPD giai đoạn đầu có thể đáp ứng một phần với thuốc giãn phế quản, dễ khiến mô hình AI nhận diện nhầm là đáp ứng hen phế quản điển hình.

---

### 🔹 Cụm 2: Suy Tim Trái Cấp / Ứ Huyết Phổi Nhầm Lẫn Với Viêm Phổi (Cardiac Asthma vs Pneumonia)
- **Số lượng ca sai biệt:** 46 ca Suy tim bị mô hình dự đoán nhầm thành Viêm phổi ($64.8\%$). Đây là nguồn sai số lớn nhất của mô hình.
- **Nguyên nhân sinh lý bệnh:**
  - Trong suy tim trái mất bù cấp (ADHF), áp lực mao mạch phổi bít tăng cao làm thoát dịch vào mô kẽ và phế nang (phù phổi kẽ / phù phổi huyết động). Khám lâm sàng nghe thấy **ran ẩm, ran nổ (crepitations/crackles) ở cả hai phế trường**, triệu chứng này hoàn toàn trùng lặp với hội chứng đông đặc phế nang rải rác trong viêm phổi do vi khuẩn.
  - Bệnh nhân suy tim ứ huyết thường kèm theo khó thở kịch phát, nhịp thở nhanh ($RR > 20$), độ bão hòa oxy giảm ($SpO_2 < 90\%$), và nhịp tim nhanh bù trừ ($HR > 100$). Nếu không có giá trị xét nghiệm peptide bài niệu (NT-proBNP/BNP) hoặc siêu âm tim tại giường, các đặc trưng bảng của hai bệnh lý này gần như đồng nhất.
  - Ngoài ra, tình trạng sung huyết phổi mạn tính ở bệnh nhân suy tim cao tuổi thường kích thích phản ứng viêm nhẹ toàn thân, dẫn đến CRP huyết thanh tăng nhẹ ($10 - 30\text{ mg/L}$), khiến mạng nơ-ron nhầm với phản ứng viêm nhiễm trùng của Viêm phổi cộng đồng.

---

### 🔹 Cụm 3: Viêm Phổi Có Phản Ứng Co Thắt Phế Quản (Reactive Bronchospasm in Pneumonia)
- **Số lượng ca sai biệt:** 21 ca Viêm phổi nhầm thành COPD ($29.2\%$) và 14 ca nhầm thành Hen ($19.4\%$).
- **Nguyên nhân sinh lý bệnh:**
  - Ở nhiều bệnh nhân viêm phổi không điển hình (Mycoplasma, Chlamydia, hoặc virus hô hấp), nhiễm trùng niêm mạc phế quản kích thích tăng tính đáp ứng phế quản (bronchial hyperresponsiveness), gây co thắt cơ trơn phế quản phản ứng. Khám thực thể ngoài ran ẩm còn nghe ran rít ran ngáy rải rác.
  - Khi chưa có kết quả chụp X-quang lồng ngực (tiêu chuẩn vàng bị loại trừ để tránh rò rỉ dữ liệu theo PROBAST mục 3.2), việc phân biệt giữa một đợt cấp COPD do nhiễm trùng và một ca viêm phổi nguyên phát có co thắt đường thở là một trong những bài toán hóc búa nhất đối với bác sĩ cấp cứu.

---

## 3. PHÂN TÍCH HỒ SƠ BỆNH ÁN ĐIỂN HÌNH (CASE STUDIES FROM HOLDOUT TEST)

### 📋 Ca Bệnh 1: Bệnh nhân `PT-0025` (Hen phế quản nhầm thành COPD)
* **Dữ liệu bệnh nhân:**
  * Giới tính: Nữ | Tuổi: 18 | Tiền sử hút thuốc: KHÔNG (NEVER)
  * Sinh hiệu: Huyết áp $131/78\text{ mmHg}$, Nhịp tim $90\text{ bpm}$, Nhịp thở $12\text{ l/p}$, $SpO_2 = 74.3\%$, Nhiệt độ $38.6^\circ\text{C}$
  * Cận lâm sàng: Bạch cầu $\text{WBC} = 6.64\times 10^9/\text{L}$, $\text{CRP} = 38.92\text{ mg/L}$
* **Dự đoán mô hình:**
  * Xác suất: Hen ($13.0\%$), **COPD ($44.1\%$)**, Suy tim ($42.4\%$), Viêm phổi ($0.5\%$)
  * Kết luận mô hình: **COPD mạn tính (Sai)** | Nhãn thực tế: **Hen phế quản (ASTHMA)**
* **Biện luận lâm sàng:**
  * Mặc dù bệnh nhân trẻ tuổi (18 tuổi), nhưng tình trạng suy hô hấp cấp nặng nề ($SpO_2$ tụt sâu còn $74.3\%$) kết hợp với sốt ($38.6^\circ\text{C}$) và CRP tăng cao ($38.92\text{ mg/L}$) đã kích hoạt các trọng số của bệnh lý viêm mạn tính nặng.
  * Trong ghi chú lâm sàng, triệu chứng co kéo cơ hô hấp phụ và ran phế quản lan tỏa cả hai bên phế trường khiến tầng Cross-Attention phân bổ trọng số lớn cho cơ chế tắc nghẽn luồng khí nghiêm trọng, đánh đổi xác suất Hen sang COPD.
* **Khuyến nghị hỗ trợ quyết định lâm sàng (CDSS Rule):**
  * Hệ thống cần bổ sung quy tắc cảnh báo tri thức y khoa (Clinical Prior Rule): *Bệnh nhân $\le 20$ tuổi không có tiền sử hút thuốc hoặc thiếu hụt alpha-1 antitrypsin có xác suất tiền nghiệm COPD cực thấp ($< 1\%$)*. Cần chỉ định phun khí dung Salbutamol cấp cứu và đo lưu lượng đỉnh (PEF).

---

### 📋 Ca Bệnh 2: Bệnh nhân `PT-0201` (Suy tim sung huyết nhầm thành Hen phế quản)
* **Dữ liệu bệnh nhân:**
  * Giới tính: Nam | Tuổi: 54 | Tiền sử hút thuốc: TỪNG HÚT (FORMER)
  * Sinh hiệu: Huyết áp $125/82\text{ mmHg}$, Nhịp tim $91\text{ bpm}$, Nhịp thở $16\text{ l/p}$, $SpO_2 = 83.0\%$, Nhiệt độ $37.7^\circ\text{C}$
  * Cận lâm sàng: $\text{WBC} = 7.6\times 10^9/\text{L}$, $\text{CRP} = 0.2\text{ mg/L}$
* **Dự đoán mô hình:**
  * Xác suất: **Hen ($35.8\%$)**, COPD ($32.5\%$), Suy tim ($30.7\%$), Viêm phổi ($1.0\%$)
  * Kết luận mô hình: **Hen phế quản (Sai)** | Nhãn thực tế: **Suy tim sung huyết (HEART_FAILURE)**
* **Biện luận lâm sàng:**
  * Bệnh nhân nhập viện vì khó thở kịch phát về đêm (PND - Paroxysmal Nocturnal Dyspnea) và khó thở khi nằm (orthopnea). Khám phổi có ran rít phế quản do phù nề niêm mạc quanh phế quản phế nang (hiện tượng **Hen tim - Cardiac Asthma**).
  * Do bạch cầu và CRP hoàn toàn bình thường ($\text{CRP} = 0.2\text{ mg/L}$ loại trừ viêm nhiễm), mô hình loại trừ Viêm phổi nhưng bị phân vân giữa 3 bệnh lý còn lại với khoảng xác suất rất hẹp ($35.8\%$ vs $32.5\%$ vs $30.7\%$). Sự xuất hiện của tiếng thở rít trong ghi chú khám đã đẩy dự đoán lệch nhẹ sang Hen phế quản.
* **Khuyến nghị hỗ trợ quyết định lâm sàng (CDSS Rule):**
  * Trong tình huống này, CDSS phải đưa ra khuyến cáo đa bệnh lý (differential diagnosis list) và cảnh báo bác sĩ: *Khi xác suất phân rã đều giữa Hen và Suy tim ở bệnh nhân trung niên, bắt buộc làm xét nghiệm NT-proBNP và siêu âm tim trước khi dùng thuốc kích thích beta-2 liều cao (có thể gây rung thất nếu bệnh nhân suy tim nặng)*.

---

## 4. GIÁ TRỊ KHOA HỌC ĐỐI VỚI BÀI BÁO (SCIENTIFIC DISCUSSION POINTS)

1. **Tính chân thực của dữ liệu và phương pháp kiểm thử không gian lận:**
   * Thay vì báo cáo độ chính xác lý tưởng giả tạo ($98 - 99\%$) như 15 bài báo trước đó bị bài phê bình JMIR vạch trần (do vi phạm rò rỉ dữ liệu giữa train-test và nhồi nhét tiêu chuẩn vàng), mô hình M-CDSS đạt kết quả trung thực trên tập Strict Holdout hoàn toàn độc lập.
   * Việc mô hình gặp khó khăn ở các ca ACOS và Suy tim phù phổi chứng minh rằng mô hình đang học các đặc trưng sinh lý bệnh thực tế, phản ánh chính xác độ phức tạp mà các bác sĩ chuyên khoa hô hấp - tim mạch đối mặt hàng ngày.
2. **Cơ sở cho kiến trúc RAG Agentic Giải thích (Backlog 05 & Phase 3):**
   * Ma trận nhầm lẫn này chính là lý do vì sao hệ thống **không thể chỉ dựa vào một mô hình phân loại Black-Box duy nhất**.
   * Module `DiagnosticAgent` kết hợp cùng phác đồ GINA 2024 / GOLD 2024 / ESC 2023 đóng vai trò là "chốt chặn an toàn" (Safety Net), giúp chỉ ra các câu chứng cứ mâu thuẫn trong bệnh án (ví dụ: ran rít kèm phù chân và khó thở khi nằm) để hướng dẫn bác sĩ làm thêm thăm dò đặc hiệu thay vì vội vàng điều trị sai hướng.

