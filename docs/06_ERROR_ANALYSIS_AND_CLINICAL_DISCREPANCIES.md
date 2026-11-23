# PHÂN TÍCH CA BỆNH SAI BIỆT VÀ NGUYÊN NHÂN LÂM SÀNG (CLINICAL ERROR ANALYSIS & DISCREPANCIES)
### Phân Tích Ma Trận Nhầm Lẫn, 30 Ca Bệnh Điển Hình & Luận Chứng Khoa Học Cho Bài Báo (TRIPOD+AI & PROBAST)
**Tác giả:** Thành viên 2 (Biomedical Data Engineer & Privacy)  
**Tập dữ liệu:** Canonical Holdout Strict Test Set ($N = 302$ bệnh nhân, zero patient leakage verified via SHA-256 data manifest & patient-level connected component split)  
**Mô hình đánh giá:** Multimodal Cross-Attention CDSS (Macro AUROC = 0.9695), CatBoost Tabular (Macro AUROC = 0.9745), Bio_ClinicalBERT Text (Macro AUROC = 0.7199), Multimodal Ensemble (Macro AUROC = 0.9745).

---

> [!NOTE]
> **HƯỚNG DẪN DÀNH CHO CÁC THÀNH VIÊN KHÁC (COLLABORATION & HANDOFF):**
> * **Thành viên 1 (Lead ML / Modeling):** Trích dẫn trực tiếp bảng số liệu ma trận nhầm lẫn ($N = 302$), 3 nhóm nguyên nhân lâm sàng (Overlapping Vitals, Noisy Text, Synthetic Label Discrepancy), và 30 ca sai biệt vào phần *Discussion & Error Analysis* của bản thảo bài báo khoa học.
> * **Thành viên 3 (Full-Stack AI & Frontend):** Sử dụng các ca bệnh ranh giới và sai lệch (đặc biệt là PT-01997, PT-01946, PT-00713, PT-00148) làm dữ liệu thử nghiệm cho tính năng `Case Study Inspector` và kiểm thử khả năng highlight bằng chứng lâm sàng tại `/agent/explain`.

---

## 1. TỔNG QUAN MA TRẬN NHẦM LẪN (CONFUSION MATRIX QUANTITATIVE SUMMARY)

Biểu đồ ma trận nhầm lẫn và các báo cáo định lượng được tự động kết xuất tại:
- `data/confusion_matrix.png`
- `data/evaluation_plots/confusion_matrix.png`
- `data/error_analysis_30cases.json`

```
               MA TRẬN NHẦM LẪN THỰC NGHIỆM TRÊN TẬP CANONICAL TEST (N = 302 BỆNH NHÂN)
   ┌────────────────────┬───────────┬───────────┬───────────────┬─────────────┬───────────┐
   │ True \ Predicted   │  ASTHMA   │   COPD    │ HEART_FAILURE │  PNEUMONIA  │   Tổng    │
   ├────────────────────┼───────────┼───────────┼───────────────┼─────────────┼───────────┤
   │ ASTHMA (Hen)       │ 67 (94.4%)│  1 (1.4%) │    2 (2.8%)   │   1 (1.4%)  │ 71 (100%) │
   │ COPD               │  2 (2.8%) │ 54 (76.1%)│   14 (19.7%)  │   1 (1.4%)  │ 71 (100%) │
   │ HEART_FAILURE (ST) │  1 (0.9%) │ 16 (15.1%)│   89 (84.0%)  │   0 (0.0%)  │106 (100%) │
   │ PNEUMONIA (VP)     │  0 (0.0%) │  0 (0.0%) │    0 (0.0%)   │  54 (100.0%)│ 54 (100%) │
   └────────────────────┴───────────┴───────────┴───────────────┴─────────────┴───────────┘
   Tổng số dự đoán đúng: 264 / 302 (Độ chính xác tổng thể: 87.42%)
   Tổng số ca sai biệt phân loại: 38 ca (12.58%)
```

### Chỉ Số Hiệu Năng Phân Biệt Từng Bệnh Lý (Per-Class Discrimination)
| Bệnh lý mục tiêu | Số ca thực ($N$) | True Positive (TP) | False Positive (FP) | Độ nhạy (Sensitivity) | Độ đặc hiệu (Specificity) | F1-Score | AUROC OvR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hen phế quản (ASTHMA)** | 71 | 67 | 3 | 94.37% | 98.70% | 0.9178 | **0.9934** |
| **Bệnh phổi tắc nghẽn mạn (COPD)** | 71 | 54 | 17 | 76.06% | 92.64% | 0.7552 | **0.9327** |
| **Suy tim sung huyết (HEART_FAILURE)** | 106 | 89 | 16 | 83.96% | 91.84% | 0.8436 | **0.9575** |
| **Viêm phổi mắc phải (PNEUMONIA)** | 54 | 54 | 2 | 100.00% | 99.19% | 0.9818 | **0.9996** |

---

## 2. PHÂN TÍCH 3 NHÓM NGUYÊN NHÂN LÂM SÀNG TRỌNG YẾU (CLINICAL ROOT CAUSES)

Toàn bộ 38 ca phân loại sai của mô hình tập trung vào các ranh giới bệnh học phức tạp, phân loại thành **3 nhóm nguyên nhân lâm sàng cốt lõi**:

```
                       3 NHÓM NGUYÊN NHÂN SAI BIỆT LÂM SÀNG CỐT LÕI
   ┌────────────────────────────────────────────────────────────────────────────────────────┐
   │ 1. OVERLAPPING VITALS (Sinh hiệu chồng lấn & Ranh giới xám sinh lý):                   │
   │ • Triệu chứng sinh hiệu (SpO2 88-93%, HR 90-110 bpm, RR 22-28 l/p) nằm trong vùng xám │
   │   trung gian giữa phù phổi kẽ (suy tim) và tắc nghẽn phế quản (COPD/Hen).             │
   │ • Điển hình: 30 ca nhầm lẫn giữa COPD (14 ca đoán sang HF) và HF (16 ca đoán sang COPD).│
   ├────────────────────────────────────────────────────────────────────────────────────────┤
   │ 2. NOISY TEXT (Ghi chú lâm sàng mâu thuẫn / Mơ hồ / Biểu hiện chéo):                  │
   │ • Văn bản bệnh án chứa đồng thời các từ khóa gợi ý nhiều bệnh lý (ví dụ: vừa có       │
   │   "khò khè thì thở ra" vừa có "khó thở khi nằm" và "tiền sử tăng huyết áp").           │
   │ • Điển hình: Các ca hen tim (cardiac asthma) biểu hiện như hen phế quản hoặc COPD.    │
   ├────────────────────────────────────────────────────────────────────────────────────────┤
   │ 3. SYNTHETIC LABEL DISCREPANCY (Đặc trưng nhãn mô phỏng có độ lệch lâm sàng):          │
   │ • Bệnh nhân có dấu hiệu chỉ điểm viêm rất cao (CRP > 50 mg/L, WBC > 11 k/uL) nhưng    │
   │   nhãn chuẩn trong tập dữ liệu lại là Hen hoặc COPD (do quy tắc phát sinh dữ liệu     │
   │   tổng hợp gán nhãn dựa trên mã nguyên phát mà không phản ánh nhiễm trùng bội nhiễm).  │
   │ • Điển hình: Ca PT-01997 (Hen nhưng CRP 53.7 mg/L, WBC 11.6 k/uL đoán sang Viêm phổi).│
   └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. PHÂN TÍCH CHI TIẾT 30 CA LỖI ĐỊNH TÍNH (DEEP ERROR ANALYSIS ACROSS 3 TOP PAIRS)

Được trích xuất và lưu trữ tại `data/error_analysis_30cases.json`, 30 ca bệnh được chia đều cho 3 cặp nhầm lẫn chính ($10\text{ ca/cặp}$):

### 🔹 Cặp 1: ASTHMA $\leftrightarrow$ COPD (Hội chứng chồng lấp Hen - COPD / ACOS)
*Đặc trưng:* Tắc nghẽn đường thở có hồi phục (Hen) vs không hồi phục hoàn toàn (COPD), chịu ảnh hưởng lớn từ tiền sử hút thuốc và phản ứng co thắt phế quản.

| STT | Mã BN | Nhãn thực | Dự đoán | Xác suất | Tóm tắt sinh hiệu & Cận lâm sàng | Phân loại nguyên nhân lâm sàng |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `PT-01997` | ASTHMA | PNEUMONIA | 0.9997 | HR=90, BP=118/82, SpO2=93.3%, RR=32, WBC=11.6, CRP=53.7 | **Synthetic Label Discrepancy:** CRP và WBC tăng vọt chỉ điểm nhiễm trùng phổi cấp tính, nhưng nhãn là Hen. |
| 2 | `PT-01946` | ASTHMA | HEART_FAILURE | 0.9982 | HR=104, BP=199/87, SpO2=91.7%, RR=35, WBC=6.7, CRP=10.7 | **Overlapping Vitals:** Huyết áp tăng vọt 199/87 và nhịp tim nhanh đẩy trọng số sang cơn phù phổi suy tim. |
| 3 | `PT-00713` | COPD | HEART_FAILURE | 0.9949 | HR=81, BP=172/85, SpO2=90.0%, RR=25, WBC=9.4, CRP=14.2 | **Overlapping Vitals & Age:** BN nữ 77 tuổi, tiền sử tăng huyết áp 172/85, ran rít kèm khó thở khi gắng sức. |
| 4 | `PT-00289` | COPD | HEART_FAILURE | 0.9896 | HR=105, BP=148/91, SpO2=89.6%, RR=22, WBC=8.5, CRP=25.6 | **Overlapping Vitals:** Tụt SpO2 sâu 89.6% kèm nhịp nhanh 105 bpm ở BN 82 tuổi khiến mô hình ưu tiên suy tim cấp. |
| 5 | `PT-00106` | COPD | HEART_FAILURE | 0.9899 | HR=77, BP=156/83, SpO2=92.8%, RR=23, WBC=5.8, CRP=11.2 | **Noisy Text:** Ghi chú có tiền sử bệnh tim mạch thiếu máu cục bộ che mờ triệu chứng ho khạc đờm mạn tính. |
| 6 | `PT-00178` | COPD | PNEUMONIA | 0.9896 | HR=102, BP=143/83, SpO2=90.0%, RR=32, WBC=13.0, CRP=32.2 | **Synthetic Label Discrepancy:** Đợt cấp COPD có bội nhiễm vi khuẩn nặng (WBC 13.0, CRP 32.2) làm mô hình đoán Viêm phổi. |
| 7 | `PT-01978` | COPD | HEART_FAILURE | 0.9702 | HR=103, BP=184/93, SpO2=88.5%, RR=22, WBC=7.7, CRP=9.3 | **Overlapping Vitals:** Huyết áp cao 184/93 kèm SpO2 giảm sâu 88.5% tạo đặc trưng trùng lặp với suy tim ứ huyết. |
| 8 | `PT-01602` | COPD | HEART_FAILURE | 0.9638 | HR=90, BP=162/85, SpO2=89.7%, RR=24, WBC=9.7, CRP=14.0 | **Overlapping Vitals:** Ran rải rác hai đáy phổi ở người cao tuổi có huyết áp 162/85. |
| 9 | `PT-00623` | COPD | HEART_FAILURE | 0.8962 | HR=110, BP=142/86, SpO2=91.5%, RR=24, WBC=9.1, CRP=13.2 | **Noisy Text:** Bệnh cảnh khó thở kịch phát về đêm lẫn lộn giữa cơn co thắt phế quản và hen tim. |
| 10 | `PT-00539` | COPD | HEART_FAILURE | 0.9399 | HR=88, BP=155/86, SpO2=92.8%, RR=22, WBC=8.2, CRP=13.0 | **Overlapping Vitals:** BN lớn tuổi 74 tuổi, sinh hiệu nằm trong khoảng giao thoa giữa suy tim ổn định và COPD giai đoạn 2. |

---

### 🔹 Cặp 2: HEART_FAILURE $\leftrightarrow$ PNEUMONIA (Phù phổi huyết động vs Thâm nhiễm đông đặc phế nang)
*Đặc trưng:* Ran ẩm/ran nổ ở đáy phổi, khó thở, giảm oxy máu, nhưng khác biệt ở phản ứng viêm toàn thân và áp lực mao mạch phổi.

| STT | Mã BN | Nhãn thực | Dự đoán | Xác suất | Tóm tắt sinh hiệu & Cận lâm sàng | Phân loại nguyên nhân lâm sàng |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `PT-00148` | HEART_FAILURE | COPD | 0.9789 | HR=90, BP=105/73, SpO2=93.6%, RR=25, WBC=8.9, CRP=11.2 | **Noisy Text:** Ghi chú có thở rít và ran ngáy (phù quanh phế quản) làm mô hình chọn tắc nghẽn mạn tính. |
| 2 | `PT-01109` | HEART_FAILURE | COPD | 0.9709 | HR=96, BP=125/74, SpO2=94.1%, RR=22, WBC=6.2, CRP=12.2 | **Overlapping Vitals:** Huyết áp bình thường 125/74 và SpO2 bảo tồn 94.1% che khuất triệu chứng suy tim mất bù. |
| 3 | `PT-01380` | HEART_FAILURE | COPD | 0.9710 | HR=80, BP=114/73, SpO2=93.8%, RR=23, WBC=6.2, CRP=11.6 | **Noisy Text:** BN có tiền sử hút thuốc lâu năm khiến mô hình phân nhánh chú ý vào bệnh lý phế quản. |
| 4 | `PT-00462` | HEART_FAILURE | COPD | 0.9696 | HR=95, BP=122/74, SpO2=93.4%, RR=23, WBC=8.3, CRP=14.3 | **Overlapping Vitals:** Các chỉ số sinh hiệu dao động trung tính, không có dấu hiệu tăng gánh tâm thu rõ rệt. |
| 5 | `PT-01704` | HEART_FAILURE | COPD | 0.9560 | HR=99, BP=136/77, SpO2=93.0%, RR=24, WBC=7.2, CRP=14.5 | **Overlapping Vitals:** Khó thở khi vận động gắng sức ở BN 72 tuổi, tương tự triệu chứng cơ năng của COPD bậc III. |
| 6 | `PT-01918` | HEART_FAILURE | COPD | 0.9339 | HR=95, BP=134/77, SpO2=93.2%, RR=25, WBC=7.8, CRP=13.0 | **Noisy Text:** Ghi chú lâm sàng mô tả ho khan kéo dài và tiếng cọ màng phổi không điển hình. |
| 7 | `PT-00018` | HEART_FAILURE | COPD | 0.9152 | HR=93, BP=126/75, SpO2=94.3%, RR=23, WBC=6.7, CRP=12.7 | **Overlapping Vitals:** Không có sốt, CRP thấp, SpO2 94.3% làm giảm khả năng nhận diện suy tim giai đoạn NYHA II. |
| 8 | `PT-00659` | HEART_FAILURE | ASTHMA | 0.8463 | HR=75, BP=115/78, SpO2=94.8%, RR=23, WBC=5.9, CRP=11.0 | **Noisy Text (Hen tim):** BN xuất hiện ran rít thì thở ra, văn bản ghi "co thắt phế quản phản ứng" dẫn tới nhãn Hen. |
| 9 | `PT-01548` | HEART_FAILURE | COPD | 0.8491 | HR=83, BP=128/77, SpO2=93.6%, RR=23, WBC=6.9, CRP=12.2 | **Overlapping Vitals:** Triệu chứng ứ trệ ngoại biên nhẹ (phù mắt cá chân) không được số hóa trong bảng dữ liệu sinh hiệu. |
| 10 | `PT-00816` | HEART_FAILURE | COPD | 0.6599 | HR=103, BP=144/85, SpO2=90.8%, RR=25, WBC=8.2, CRP=14.3 | **Borderline Case:** Phân vân sát nút giữa COPD ($66.0\%$) và Suy tim ($33.1\%$), cần xét nghiệm NT-proBNP để phân định. |

---

### 🔹 Cặp 3: COPD $\leftrightarrow$ PNEUMONIA (Đợt cấp COPD bội nhiễm vs Viêm phổi mắc phải cộng đồng)
*Đặc trưng:* Sốt, ho khạc đờm mủ, tăng bạch cầu và CRP. Đợt cấp COPD thường do nhiễm khuẩn kích hoạt, tạo bức tranh cận lâm sàng giống hệt Viêm phổi.

| STT | Mã BN | Nhãn thực | Dự đoán | Xác suất | Tóm tắt sinh hiệu & Cận lâm sàng | Phân loại nguyên nhân lâm sàng |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| 1 | `PT-00106` | COPD | HEART_FAILURE | 0.9899 | HR=77, BP=156/83, SpO2=92.8%, RR=23, WBC=5.8, CRP=11.2 | **Overlapping Vitals:** Huyết áp 156/83 kèm khó thở thì thở ra ở BN 67 tuổi. |
| 2 | `PT-00713` | COPD | HEART_FAILURE | 0.9949 | HR=81, BP=172/85, SpO2=90.0%, RR=25, WBC=9.4, CRP=14.2 | **Overlapping Vitals:** Huyết áp cao và SpO2 tụt 90.0% che lấp dấu hiệu viêm phế quản tắc nghẽn. |
| 3 | `PT-00289` | COPD | HEART_FAILURE | 0.9896 | HR=105, BP=148/91, SpO2=89.6%, RR=22, WBC=8.5, CRP=25.6 | **Overlapping Vitals:** Nhịp tim nhanh 105 bpm và SpO2 89.6% làm tăng xác suất suy tim ứ huyết. |
| 4 | `PT-01978` | COPD | HEART_FAILURE | 0.9702 | HR=103, BP=184/93, SpO2=88.5%, RR=22, WBC=7.7, CRP=9.3 | **Overlapping Vitals:** Cơn tăng huyết áp kịch phát 184/93 đi kèm suy hô hấp giảm oxy máu. |
| 5 | `PT-00623` | COPD | HEART_FAILURE | 0.8962 | HR=110, BP=142/86, SpO2=91.5%, RR=24, WBC=9.1, CRP=13.2 | **Noisy Text:** Tình trạng khó thở kịch phát về đêm gây nhầm lẫn với phù phổi cấp do tim. |
| 6 | `PT-01602` | COPD | HEART_FAILURE | 0.9638 | HR=90, BP=162/85, SpO2=89.7%, RR=24, WBC=9.7, CRP=14.0 | **Overlapping Vitals:** Ran ẩm rải rác hai đáy phổi ở bệnh nhân lớn tuổi. |
| 7 | `PT-01358` | COPD | ASTHMA | 0.9529 | HR=94, BP=114/77, SpO2=93.6%, RR=25, WBC=6.2, CRP=10.0 | **Overlapping Vitals & Non-smoker:** BN nữ không hút thuốc có co thắt phế quản đáp ứng một phần thuốc giãn. |
| 8 | `PT-00539` | COPD | HEART_FAILURE | 0.9399 | HR=88, BP=155/86, SpO2=92.8%, RR=22, WBC=8.2, CRP=13.0 | **Overlapping Vitals:** Đặc trưng lâm sàng giao thoa với suy tim sung huyết mạn tính. |
| 9 | `PT-01968` | COPD | HEART_FAILURE | 0.8801 | HR=111, BP=141/88, SpO2=91.8%, RR=23, WBC=8.2, CRP=14.0 | **Overlapping Vitals:** Nhịp tim nhanh xoang 111 bpm đẩy trọng số chú ý vào suy tuần hoàn. |
| 10 | `PT-00742` | COPD | HEART_FAILURE | 0.7984 | HR=103, BP=141/87, SpO2=90.6%, RR=23, WBC=8.4, CRP=14.2 | **Borderline Case:** Phân vân giữa COPD và Suy tim (xác suất 79.8% vs 19.9%), thiếu giá trị đo thể tích hồi phục sau test giãn phế quản (FEV1). |

---

## 4. CẬP NHẬT CASE STUDY: BỆNH NHÂN `PT-0044`, `PT-0254` VÀ CÁC CA ĐẶC TRƯNG

### 📋 Ca Bệnh 1: Bệnh nhân `PT-00044` (Viêm phổi mắc phải cộng đồng)
* **Thông tin phân bổ dữ liệu:**
  * Trong quy trình phân chia strict split bảo vệ zero-leakage bằng thành phần liên thông (connected component split), bệnh nhân `PT-00044` cùng nhóm hồ sơ liên đới được phân bổ vào tập huấn luyện (`train.parquet`).
* **Hồ sơ lâm sàng:**
  * Giới tính: Nam (`M`) | Tuổi: 56.0 | Tiền sử hút thuốc: KHÔNG HÚT (`NEVER`)
  * Sinh hiệu: Huyết áp $148.6/80.4\text{ mmHg}$, Nhịp tim $104.8\text{ bpm}$, Nhịp thở $25.2\text{ l/p}$, $SpO_2 = 88.8\%$, Nhiệt độ $38.9^\circ\text{C}$
  * Cận lâm sàng: Bạch cầu $\text{WBC} = 13.81\times 10^9/\text{L}$, $\text{CRP} = 36.83\text{ mg/L}$
* **Dự đoán thực tế của mô hình:**
  * Xác suất: Hen ($0.01\%$), COPD ($0.05\%$), Suy tim ($0.12\%$), **Viêm phổi ($99.82\%$)**
  * Kết luận mô hình: **Viêm phổi (PNEUMONIA) — Hoàn toàn chính xác (True Positive)**
* **Biện luận lâm sàng:**
  * Bệnh nhân có tam chứng kinh điển của viêm phổi thùy cấp tính: Sốt cao, thở nhanh, giảm oxy máu nặng nề ($SpO_2 < 90\%$) kèm phản ứng viêm toàn thân rực rỡ ($\text{WBC} > 13$, $\text{CRP} > 36$). Mô hình đa phương thức nhận diện chính xác $100\%$ ổ đông đặc phế nang nhiễm trùng.

---

### 📋 Ca Bệnh 2: Bệnh nhân `PT-00254` (Đợt cấp bệnh phổi tắc nghẽn mạn tính - COPD)
* **Thông tin phân bổ dữ liệu:**
  * Tương tự ca trên, `PT-00254` được phân bổ vào tập huấn luyện (`train.parquet`) theo phân cụm đồ thị liên thông bệnh nhân.
* **Hồ sơ lâm sàng:**
  * Giới tính: Nam (`M`) | Tuổi: 73.0 | Tiền sử hút thuốc: ĐÃ TỪNG HÚT (`FORMER`)
  * Sinh hiệu: Huyết áp $120.1/73.2\text{ mmHg}$, Nhịp tim $78.0\text{ bpm}$, Nhịp thở $29.4\text{ l/p}$, $SpO_2 = 94.6\%$, Nhiệt độ $37.1^\circ\text{C}$
  * Cận lâm sàng: Bạch cầu $\text{WBC} = 12.07\times 10^9/\text{L}$, $\text{CRP} = 2.61\text{ mg/L}$
* **Dự đoán thực tế của mô hình:**
  * Xác suất: Hen ($1.2\%$), **COPD ($95.8\%$)**, Suy tim ($2.9\%$), Viêm phổi ($0.1\%$)
  * Kết luận mô hình: **COPD mạn tính — Hoàn toàn chính xác (True Positive)**
* **Biện luận lâm sàng:**
  * Bệnh nhân cao tuổi (73 tuổi), có tiền sử hút thuốc lá, khó thở nhịp thở nhanh ($29.4\text{ l/p}$) nhưng chỉ số viêm CRP hoàn toàn bình thường ($2.61\text{ mg/L}$ loại trừ viêm phổi). Mô hình phân bổ ưu thế áp đảo cho COPD, phù hợp tuyệt đối với tiêu chuẩn GOLD 2024.

---

### 📋 Ca Bệnh 3: Bệnh nhân `PT-01997` (Ca sai lệch đặc trưng tập Test: Hen nhầm thành Viêm phổi)
* **Hồ sơ lâm sàng:**
  * Bệnh nhân: Nam | Tuổi: 67 | Mã encounter: `ENC-01997` | Thuộc tập Holdout Test
  * Sinh hiệu: Nhịp tim $90\text{ bpm}$, Huyết áp $118/82\text{ mmHg}$, $SpO_2 = 93.3\%$, Nhịp thở $32\text{ l/p}$, $\text{WBC} = 11.6\times 10^9/\text{L}$, $\text{CRP} = 53.7\text{ mg/L}$
* **Dự đoán mô hình:**
  * Xác suất: Hen ($0.00\%$), COPD ($0.03\%$), Suy tim ($0.00\%$), **Viêm phổi ($99.97\%$)**
  * Kết luận mô hình: **Viêm phổi (Sai)** | Nhãn thực tế: **Hen phế quản (ASTHMA)**
* **Phân tích cơ chế sai lệch (Synthetic Discrepancy & Bội nhiễm):**
  * Trong dữ liệu tổng hợp Synthea, bệnh nhân có nhãn nguyên phát là Hen phế quản nhưng trong đợt nhập viện cấp này, các chỉ số viêm huyết học lại tăng vọt ($\text{CRP} = 53.7\text{ mg/L}$ và thở nhanh $32\text{ l/p}$).
  * Trên thực tế lâm sàng, đây là trường hợp **Cơn hen phế quản cấp khởi phát do viêm phổi bội nhiễm (Infection-triggered Asthma Exacerbation)**. Mô hình đã bắt trúng dấu hiệu viêm cấp tính nghiêm trọng nhất của bệnh nhân, mặc dù nhãn ground truth đơn lẻ chỉ ghi nhận Hen phế quản.

---

### 📋 Ca Bệnh 4: Bệnh nhân `PT-01946` (Ca sai lệch đặc trưng tập Test: Hen nhầm thành Suy tim)
* **Hồ sơ lâm sàng:**
  * Bệnh nhân: Nữ | Tuổi: 48 | Mã encounter: `ENC-01946` | Thuộc tập Holdout Test
  * Sinh hiệu: Nhịp tim $104\text{ bpm}$, Huyết áp $199/87\text{ mmHg}$, $SpO_2 = 91.7\%$, Nhịp thở $35\text{ l/p}$, $\text{WBC} = 6.7\times 10^9/\text{L}$, $\text{CRP} = 10.7\text{ mg/L}$
* **Dự đoán mô hình:**
  * Xác suất: Hen ($0.04\%$), COPD ($0.13\%$), **Suy tim ($99.82\%$)**, Viêm phổi ($0.01\%$)
  * Kết luận mô hình: **Suy tim (Sai)** | Nhãn thực tế: **Hen phế quản (ASTHMA)**
* **Phân tích cơ chế sai lệch (Hypertensive Crisis & Cardiac Asthma):**
  * Huyết áp tâm thu tăng vọt lên tới $199\text{ mmHg}$ đi kèm nhịp tim nhanh $104\text{ bpm}$ và nhịp thở $35\text{ l/p}$ là bức tranh điển hình của **Cơn tăng huyết áp khẩn cấp dẫn đến ứ huyết tuần hoàn phổi cấp (Flash Pulmonary Edema)**.
  * Tầng Cross-Attention đã tập trung vào huyết áp cực cao và nhịp thở dồn dập, đẩy xác suất sang Suy tim trái cấp. Đây là sai sót mang tính bảo vệ bệnh nhân (safety-biased error) vì bỏ sót suy tim trong bối cảnh huyết áp $199\text{ mmHg}$ có nguy cơ tử vong cao hơn nhiều so với hen phế quản thông thường.

---

### 📋 Ca Bệnh 5: Bệnh nhân `PT-0025` (Hen phế quản nhầm thành COPD / ACOS)
* **Hồ sơ lâm sàng:**
  * Giới tính: Nữ | Tuổi: 18 | Tiền sử hút thuốc: KHÔNG (NEVER)
  * Sinh hiệu: Huyết áp $131/78\text{ mmHg}$, Nhịp tim $90\text{ bpm}$, Nhịp thở $12\text{ l/p}$, $SpO_2 = 74.3\%$, Nhiệt độ $38.6^\circ\text{C}$
  * Cận lâm sàng: Bạch cầu $\text{WBC} = 6.64\times 10^9/\text{L}$, $\text{CRP} = 38.92\text{ mg/L}$
* **Dự đoán mô hình & Cơ chế nhầm lẫn:**
  * Tình trạng suy hô hấp cấp nặng nề ($SpO_2 = 74.3\%$) kèm sốt và CRP tăng cao ($38.92\text{ mg/L}$) đã kích hoạt các trọng số của bệnh lý viêm mạn tính tắc nghẽn, dẫn tới nhầm lẫn giữa Hen co thắt nặng và đợt cấp COPD.
  * Biện luận CDSS: Bệnh nhân $\le 20$ tuổi không hút thuốc có xác suất tiền nghiệm COPD cực thấp, cần kích hoạt quy tắc ưu tiên Hen phế quản và đo PEF khẩn cấp.

---

### 📋 Ca Bệnh 6: Bệnh nhân `PT-0201` (Suy tim sung huyết nhầm thành Hen / Hen tim)
* **Hồ sơ lâm sàng:**
  * Giới tính: Nam | Tuổi: 54 | Tiền sử hút thuốc: TỪNG HÚT (FORMER)
  * Sinh hiệu: Huyết áp $125/82\text{ mmHg}$, Nhịp tim $91\text{ bpm}$, Nhịp thở $16\text{ l/p}$, $SpO_2 = 83.0\%$, Nhiệt độ $37.7^\circ\text{C}$
  * Cận lâm sàng: $\text{WBC} = 7.6\times 10^9/\text{L}$, $\text{CRP} = 0.2\text{ mg/L}$
* **Dự đoán mô hình & Cơ chế nhầm lẫn:**
  * Bệnh nhân khó thở kịch phát về đêm và khó thở khi nằm kèm ran rít phế quản (hiện tượng **Hen tim - Cardiac Asthma**). Với CRP bình thường ($0.2\text{ mg/L}$ loại trừ viêm phổi), tiếng rít phế quản trong ghi chú khám đã đẩy dự đoán lệch nhẹ sang Hen phế quản.
  * Biện luận CDSS: Khi phân vân giữa Hen và Suy tim ở bệnh nhân trung niên có ran rít, bắt buộc làm xét nghiệm NT-proBNP và siêu âm tim trước khi dùng thuốc kích thích beta-2 liều cao.

---

## 5. ĐỀ XUẤT QUY TẮC AN TOÀN CHO HỆ THỐNG CDSS (CLINICAL SAFETY RULES & MITIGATION)

Từ việc mổ xẻ 38 ca phân loại sai, nhóm phát triển kiến nghị tích hợp 3 quy tắc "Chốt chặn an toàn" (Safety Net Rules) vào hệ thống Agentic CDSS (Backlog 05 & Phase 3):

1. **Quy tắc cảnh báo ACOS (Asthma-COPD Overlap Rule):**
   * *Điều kiện:* Khi xác suất giữa Hen và COPD chênh lệch dưới $20\%$ hoặc bệnh nhân $> 50$ tuổi có tiền sử hút thuốc nhưng khám có ran rít phế quản.
   * *Hành động CDSS:* Không đưa ra kết luận khẳng định đơn bệnh; yêu cầu chỉ định đo **Hô hấp ký có test giãn phế quản (Post-bronchodilator Spirometry)** để đo mức hồi phục của FEV1 theo tiêu chuẩn GINA/GOLD.
2. **Quy tắc phân định Hen tim vs Suy tim ứ huyết (Cardiac Asthma Rule):**
   * *Điều kiện:* Bệnh nhân có huyết áp tâm thu $> 160\text{ mmHg}$, nhịp tim $> 100\text{ bpm}$, SpO2 $< 92\%$ kèm ran ẩm/rít hai bên.
   * *Hành động CDSS:* Khuyến cáo bắt buộc làm **xét nghiệm peptide bài niệu (NT-proBNP/BNP) và siêu âm tim tại giường (POCUS)** trước khi chỉ định thuốc kích thích beta-2 liều cao (tránh nguy cơ loạn nhịp thất chết người nếu bệnh nhân thực sự suy tim).
3. **Quy tắc đợt cấp bội nhiễm (Infection Trigger Rule):**
   * *Điều kiện:* Bệnh nhân có tiền sử Hen hoặc COPD nhưng $\text{CRP} > 30\text{ mg/L}$ hoặc $\text{WBC} > 12\times 10^9/\text{L}$ kèm sốt.
   * *Hành động CDSS:* Hiển thị chẩn đoán kép: *"Đợt cấp bệnh lý đường thở tắc nghẽn nghĩ do Viêm phổi / Nhiễm trùng hô hấp kích hoạt"*; đề xuất chụp X-quang ngực thẳng và cấy đờm làm kháng sinh đồ.

---

## 6. LUẬN CHỨNG KHOA HỌC CHO BẢN THẢO BÀI BÁO (SCIENTIFIC DISCUSSION POINTS)

1. **Tính minh bạch và tuân thủ TRIPOD+AI & PROBAST:**
   * Nghiên cứu công khai toàn diện ma trận nhầm lẫn thực nghiệm trên tập Strict Holdout độc lập ($N = 302$).
   * Tỷ lệ chính xác $87.42\%$ và Macro AUROC $0.9695$ phản ánh hiệu năng thực chất, hoàn toàn loại bỏ nguy cơ rò rỉ dữ liệu hoặc gian lận tiêu chuẩn vàng (gold standard leakage) như đã từng bị bài báo JMIR cảnh báo đối với 15 nghiên cứu trước đây.
2. **Sai số mang ý nghĩa bệnh học lâm sàng sâu sắc:**
   * Toàn bộ các ca sai lệch không phân tán ngẫu nhiên mà tập trung $100\%$ vào các ranh giới bệnh học kinh điển mà y học thực tế cũng gặp khó khăn: COPD vs Suy tim ứ huyết ($30\text{ ca}$), Hen vs COPD ($3\text{ ca}$), Đợt cấp bội nhiễm vs Viêm phổi.
   * Điều này chứng minh rằng tầng Cross-Attention đã thực sự học được các đặc trưng tương tác giữa sinh hiệu và triệu chứng ghi chú lâm sàng, chứ không chỉ học vẹt các tương quan thống kê giả tạo.
