# KỊCH BẢN THUYẾT TRÌNH GIAI ĐOẠN 1 & 2 – M-CDSS
### Dung hợp dữ liệu bảng và ghi chú lâm sàng cho chẩn đoán phân biệt hô hấp – tim mạch

> **Bộ slide đi kèm (21 slide, đúng thứ tự dưới đây):** https://claude.ai/artifact/VzuvUSdf3Vv5ag5Rd7r8Fp – có ghi chú người nói trong từng slide; tải về dạng PPTX/PDF từ menu của trang. Thay thế `slide-nhóm-6 (1).pdf`.
> **Dùng cho:** buổi nghiệm thu / bảo vệ trước hội đồng. **Thời lượng mục tiêu:** 20–22 phút trình bày + 10 phút hỏi đáp.
> **Nguồn số liệu:** `results/registry.json` (bản dựng ngày 2026-11-27) và `data/rebuilt_strict_results_2026-10-28.json` (số liệu lịch sử Giai đoạn 1). Nếu chạy lại thí nghiệm, đối chiếu lại mọi con số trước khi trình bày.
> **Quy ước:** mỗi slide gồm *Mục tiêu* → *Hiển thị trên slide* → *Lời nói* → *Giải thích sâu* (kiến thức để tự tin trả lời, **không đọc**) → *Câu chuyển*.

---

## PHÂN CÔNG & THỜI LƯỢNG

| Phần | Slide | Người trình bày | Thời lượng |
| :--- | :---: | :--- | :---: |
| Mở đầu & vấn đề | 1–3 | TV1 (Lead ML) | 2,5 phút |
| **Giai đoạn 1** – dữ liệu, chống rò rỉ, 3 baseline | 4–9 | TV2 (dữ liệu) → TV1 (baseline) | 7 phút |
| **Giai đoạn 2** – mô hình dung hợp, giải trình, phần mềm, đánh giá | 10–19 | TV1 (mô hình, kết quả) → TV3 (RAG, hệ thống, demo) | 10 phút |
| Kết luận & hướng tiếp theo | 20–21 | TV1 | 1,5 phút |
| Hỏi đáp | – | Cả nhóm (theo bảng câu hỏi cuối tài liệu) | 10 phút |

**Thông điệp xuyên suốt (cả nhóm phải nói thống nhất):**
1. Chúng em xây dựng đầy đủ một hệ thống hỗ trợ chẩn đoán đa phương thức – từ dữ liệu, mô hình, giải trình đến phần mềm chạy được.
2. Chúng em đánh giá nó **trung thực**: kiểm soát rò rỉ, nhiều seed, khoảng tin cậy, báo cáo cả kết quả bất lợi.
3. Phát hiện quan trọng nhất: trên dữ liệu bán tổng hợp này, ghi chú lâm sàng **chép lại** số liệu của bảng, nên dung hợp chưa chứng minh được vượt trội; nhóm chỉ ra được *điều kiện* để dung hợp có ích.

---

# PHẦN MỞ ĐẦU

## Slide 1 — Trang bìa  *(TV1, 20 giây)*

**Hiển thị:** Tên đề tài · tên 3 thành viên và vai trò · giảng viên hướng dẫn · dòng cảnh báo nhỏ: *"Nguyên mẫu nghiên cứu trên dữ liệu bán tổng hợp – không dùng cho quyết định lâm sàng."*

**Lời nói:**
> Kính thưa hội đồng, nhóm em xin trình bày đề tài hệ thống hỗ trợ quyết định lâm sàng đa phương thức M-CDSS, kết hợp dữ liệu sinh hiệu – xét nghiệm với ghi chú bệnh án để hỗ trợ chẩn đoán phân biệt bốn bệnh gây khó thở. Em là … phụ trách mô hình học máy; bạn … phụ trách dữ liệu và bảo mật; bạn … phụ trách hệ thống và giao diện.

**Câu chuyển:** *"Trước hết, em xin nói vì sao bài toán này quan trọng."*

---

## Slide 2 — Bài toán lâm sàng  *(TV1, 1 phút)*

**Mục tiêu:** hội đồng hiểu vì sao phân biệt 4 bệnh này khó và có hậu quả.

**Hiển thị:**
- 4 bệnh: Hen phế quản · COPD · Suy tim · Viêm phổi cộng đồng – cùng biểu hiện **khó thở, ho, giảm SpO₂**.
- Hướng xử trí khác hẳn nhau: giãn phế quản/corticoid · lợi tiểu · kháng sinh.
- Hai nguồn thông tin trong bệnh án điện tử: **dữ liệu bảng** (sinh hiệu, xét nghiệm) và **ghi chú tự do** (bệnh sử, triệu chứng).

**Lời nói:**
> Bốn bệnh này thường đến với cùng một than phiền là khó thở, nhưng cách xử trí giờ đầu lại khác nhau: nhầm suy tim thành viêm phổi có thể dẫn đến truyền dịch quá mức. Bác sĩ ra quyết định dựa trên cả con số đo được lẫn câu chuyện bệnh sử. Câu hỏi của chúng em là: một mô hình AI dùng *cả hai* nguồn có hỗ trợ tốt hơn mô hình chỉ dùng một nguồn hay không.

**Giải thích sâu:**
- *Dữ liệu bảng (structured/tabular):* mỗi bệnh nhân là một hàng, mỗi biến là một cột (tuổi, huyết áp, SpO₂, CRP…).
- *Dữ liệu phi cấu trúc:* văn bản tự do, độ dài thay đổi, cần mô hình ngôn ngữ để biểu diễn.
- *Đa phương thức (multimodal):* kết hợp ≥ 2 loại dữ liệu khác bản chất trong cùng mô hình.

**Câu chuyển:** *"Y văn hiện nay đã làm được gì và còn thiếu gì?"*

---

## Slide 3 — Khoảng trống nghiên cứu & câu hỏi nghiên cứu  *(TV1, 1 phút)*

**Hiển thị:**
- Tổng quan hệ thống Hunik et al., *JMIR Medical Informatics* 2025: 10.657 bản ghi → 15 nghiên cứu; **0/15 nguy cơ sai lệch thấp** (PROBAST); 13/15 chưa ngoại kiểm; chưa mô hình nào sẵn sàng triển khai.
- Hai rủi ro phương pháp: **rò rỉ dữ liệu** và **lối tắt (shortcut learning)**.
- 5 câu hỏi nghiên cứu: RQ1 so sánh công bằng · RQ2 tín hiệu văn bản từ đâu · RQ3 khi nào dung hợp có ích · RQ4 hiệu chuẩn, lợi ích ròng, độ bền · RQ5 giải trình kiểm chứng được.

**Lời nói:**
> Tổng quan gần đây trên JMIR cho thấy trong 15 nghiên cứu AI dùng hồ sơ điện tử ở tuyến cơ sở, không nghiên cứu nào đạt nguy cơ sai lệch thấp, chủ yếu vì mô tả phương pháp chưa đầy đủ. Vì vậy, ngoài việc xây mô hình, chúng em đặt mục tiêu đánh giá sao cho đáng tin. Đề tài trả lời năm câu hỏi này; Giai đoạn 1 chuẩn bị nền tảng dữ liệu và mốc so sánh, Giai đoạn 2 xây mô hình dung hợp, lớp giải trình, phần mềm và đánh giá.

**Giải thích sâu:**
- *PROBAST/PROBAST+AI* (Moons et al., BMJ 2025): công cụ chấm nguy cơ sai lệch của mô hình dự báo theo 4 miền: người tham gia, biến dự báo, kết cục, phân tích.
- *TRIPOD+AI* (Collins et al., BMJ 2024): danh mục 27 mục cần báo cáo khi công bố mô hình dự báo dùng AI.
- *Rò rỉ dữ liệu (data leakage):* thông tin của tập test hoặc của nhãn lọt vào đầu vào khi huấn luyện → hiệu năng ảo.
- Chú ý: **không** nói "100% nghiên cứu chỉ dùng dữ liệu bảng" – con số này chưa được xác minh.

**Câu chuyển:** *"Bạn … sẽ trình bày Giai đoạn 1 – xây nền dữ liệu."*

---

# GIAI ĐOẠN 1 — NỀN TẢNG DỮ LIỆU & BA MÔ HÌNH MỐC

## Slide 4 — Tổng quan Giai đoạn 1  *(TV2, 30 giây)*

**Hiển thị:** sơ đồ 3 tuần: *Tuần 1* hợp đồng dữ liệu & dữ liệu thô → *Tuần 2* khử định danh, khóa thời gian, gán khuyết → *Tuần 3* chia tập theo bệnh nhân, huấn luyện 3 baseline, phân tích lỗi, đề xuất kiến trúc.

**Lời nói:**
> Giai đoạn 1 có một nguyên tắc: chưa xây mô hình phức tạp khi dữ liệu chưa sạch và chưa có mốc so sánh. Kết quả của giai đoạn này là một bộ dữ liệu đã kiểm toán và ba mô hình đơn phương thức làm mốc.

**Câu chuyển:** *"Dữ liệu đến từ đâu?"*

---

## Slide 5 — Nguồn dữ liệu & thiết kế đoàn hệ  *(TV2, 1,5 phút)*

**Hiển thị:**
- **Synthea** (1.171 bệnh nhân tổng hợp): tuổi, giới, sinh hiệu, xét nghiệm, tiền sử, mã bệnh.
- **MTSamples** (4.999 ghi chú phiên mã thật, ẩn danh): phần bệnh sử – khám.
- Đoàn hệ: **2.000 bản ghi, 500/lớp**; 13 biến bảng (9 liên tục, 4 phân loại) + 1 ghi chú/bản ghi.
- Ghi chú gồm 305 ghi chú dựa trên MTSamples và 1.695 ghi chú theo mẫu.
- Sơ đồ flow TRIPOD (`docs/paper_latex/figures/svg/fig_tripod_flow.svg`).

**Lời nói:**
> Vì chưa được phép dùng dữ liệu bệnh viện thật, chúng em xây đoàn hệ bán tổng hợp: phần bảng lấy từ Synthea – bộ sinh bệnh nhân tổng hợp có mô phỏng diễn tiến bệnh – và phần văn bản lấy từ MTSamples. Mỗi bản ghi có 13 biến và một ghi chú. Chúng em nói rõ ngay từ đầu: đây là dữ liệu bán tổng hợp, nên mọi kết luận chỉ áp dụng trên đoàn hệ này.

**Giải thích sâu:**
- Biến liên tục: tuổi, HA tâm thu, HA tâm trương, nhịp tim, nhịp thở, SpO₂, nhiệt độ, bạch cầu (WBC), CRP. Biến phân loại: giới, hút thuốc, tăng huyết áp, đái tháo đường.
- Nhãn lấy từ mã điều kiện của lần khám trong Synthea, **không** do bác sĩ chẩn đoán → điểm yếu miền "Kết cục" của PROBAST.
- **Điểm yếu cần chủ động thừa nhận (phát hiện ở Giai đoạn 3):** 2.000 bản ghi chỉ sinh từ **478 bệnh nhân gốc**; lớp viêm phổi chỉ có 8 bệnh nhân gốc. Tuổi gần như tự phân tách các lớp (COPD trung vị ~35 tuổi, viêm phổi ~100 tuổi do chặn trên).

**Câu chuyển:** *"Dữ liệu có thông tin định danh và nguy cơ rò rỉ, chúng em xử lý thế nào?"*

---

## Slide 6 — Khử định danh PHI  *(TV2, 1 phút)*

**Hiển thị:**
- Ghi chú được cài **PHI giả lập** để kiểm thử: họ tên, CCCD, mã BHYT, số điện thoại, tên bác sĩ kèm học hàm, tên bệnh viện.
- `ClinicalDeidentifier`: luật regex có nhãn trường + ngữ cảnh tiếng Việt → thay bằng `[REDACTED_NAME]`, `[REDACTED_ID]`, `[REDACTED_HOSPITAL]`…
- Kết quả trên bộ dữ liệu hiện hành: mã BHYT còn sót **84% → 0%**, tên bác sĩ có học hàm **72% → 0%**; sinh hiệu được giữ nguyên 100%.

**Lời nói:**
> Dù dữ liệu là tổng hợp, chúng em vẫn xây pipeline khử định danh như với dữ liệu thật, và cố tình cài thông tin giả để kiểm tra. Lần rà soát đầu cho thấy còn sót mã BHYT và tên bác sĩ có học hàm; sau khi bổ sung luật, tỷ lệ sót về 0 mà không che nhầm các chỉ số như BP, HR, SpO₂.

**Giải thích sâu:**
- *PHI* (Protected Health Information) – theo HIPAA Safe Harbor có 18 loại định danh; ở Việt Nam liên quan Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.
- Kiểm thử âm tính (negative test): đảm bảo không che nhầm chữ viết tắt lâm sàng.
- Regex có giới hạn: không bắt được định danh viết tự do lạ → với dữ liệu thật cần thêm NER và kiểm tra thủ công.

**Câu chuyển:** *"Nguy cơ lớn hơn PHI là rò rỉ nhãn."*

---

## Slide 7 — Chống rò rỉ: khóa thời gian & chia theo bệnh nhân  *(TV2, 1,5 phút)*

**Hiển thị:**
- **Temporal lock:** chỉ giữ thông tin có thời điểm *trước* chẩn đoán; cấm biến "tiêu chuẩn vàng" (FEV₁/FVC, siêu âm tim EF, cấy đờm).
- Tên chẩn đoán trong ghi chú → `[REDACTED_DIAGNOSIS]`.
- **Chia theo nhóm:** bệnh nhân gốc **và** ghi chú nguồn không được xuất hiện ở hai tập → Train/Val/Test = **1.425 / 273 / 302**.
- Gán khuyết MICE **chỉ khớp trên train** (WBC thiếu ~20%, CRP ~22%), kèm biến chỉ báo thiếu.
- Audit tự động: 0 giao nhau giữa các tập; 0% ghi chú còn tên chẩn đoán.

**Lời nói:**
> Ba kiểu rò rỉ chúng em chặn: thứ nhất, dùng thông tin xuất hiện sau thời điểm chẩn đoán; thứ hai, đưa thẳng tên bệnh vào ghi chú; thứ ba, cùng một bệnh nhân hoặc cùng một ghi chú nguồn nằm ở cả tập huấn luyện và tập kiểm thử. Vì vậy chúng em không chia ngẫu nhiên theo dòng mà chia theo nhóm, và chỉ khớp bộ gán khuyết trên tập huấn luyện.

**Giải thích sâu:**
- Vì sao chia theo nhóm: nếu một bệnh nhân có 60 lần khám, chia ngẫu nhiên sẽ đưa 50 lần vào train, 10 lần vào test → mô hình "nhận ra bệnh nhân" chứ không học bệnh.
- *StratifiedGroupKFold*: vừa giữ tỷ lệ lớp, vừa không tách nhóm. Hệ quả phụ: tập test có phân bố lệch (suy tim 106 ca, viêm phổi 54 ca).
- *MICE* (Multiple Imputation by Chained Equations): ước lượng giá trị thiếu của mỗi biến từ các biến khác, lặp nhiều vòng. Khớp trên cả tập sẽ là rò rỉ.
- **Bài học Giai đoạn 3 (nên kể khi được hỏi):** một bản dữ liệu dựng lại giữa chừng đã vô tình đưa lại tên chẩn đoán và ghi chú trùng lặp; TF-IDF đạt AUROC 0,962 dù đã che số – chính audit nội dung phát hiện và nhóm đã thu hồi.

**Câu chuyển:** *"Trên nền dữ liệu này, bạn … trình bày ba mô hình mốc."*

---

## Slide 8 — Ba mô hình mốc (baseline)  *(TV1, 1,5 phút)*

**Hiển thị:**

| Baseline | Dữ liệu | Ý tưởng |
| :--- | :--- | :--- |
| CatBoost | Chỉ bảng | Cây tăng cường gradient – chuẩn mực cho dữ liệu bảng |
| FT-Transformer | Chỉ bảng | Mỗi biến thành một token, dùng self-attention |
| Bio_ClinicalBERT | Chỉ văn bản | Mô hình ngôn ngữ huấn luyện trước trên ghi chú lâm sàng MIMIC |

Kết quả Giai đoạn 1 (test strict N = 302, 1 seed, 2026-10-28): CatBoost **0,922** · FT-Transformer **0,898** · Bio_ClinicalBERT **0,973** (macro AUROC).

**Lời nói:**
> Chúng em chọn ba baseline đại diện cho hai phương thức: hai mô hình bảng – một cổ điển, một học sâu – và một mô hình văn bản. Kết quả bất ngờ đầu tiên: mô hình chỉ đọc văn bản cao nhất, AUROC 0,973. Chúng em sẽ quay lại câu hỏi vì sao ở phần RQ2.

**Giải thích sâu:**
- *Macro AUROC one-vs-rest:* với mỗi bệnh, coi bệnh đó là dương tính, các bệnh khác là âm tính, tính diện tích dưới đường ROC; lấy trung bình 4 bệnh. 0,5 = đoán ngẫu nhiên, 1 = phân tách hoàn hảo. Không phụ thuộc ngưỡng.
- CatBoost xử lý tốt biến phân loại, ít cần chỉnh tham số.
- FT-Transformer (Gorishniy et al., 2021): token hoá từng biến → Transformer → token [CLS] làm biểu diễn.
- Bio_ClinicalBERT (Alsentzer et al., 2019): BERT huấn luyện tiếp trên ghi chú MIMIC-III; Giai đoạn 1 fine-tune khối encoder cuối.
- Ở Giai đoạn 3, các số này được chạy lại với 5 seed: CatBoost 0,925 ± 0,003; FT-Transformer 0,929 ± 0,019; BERT fine-tune 0,975 ± 0,004 – khớp với Giai đoạn 1.

**Câu chuyển:** *"Nhưng một con số AUROC chưa đủ – chúng em xem mô hình sai ở đâu."*

---

## Slide 9 — Phân tích lỗi & đề xuất kiến trúc  *(TV1, 1 phút)*

**Hiển thị:**
- Hai ca minh hoạ: **PT-0044** (hen) – mô hình bảng đoán COPD (78,8%), mô hình văn bản đoán đúng (85,8%); **PT-0254** (COPD) – mô hình văn bản đoán suy tim (59,0%), mô hình bảng đoán đúng (75,2%).
- Giả thuyết: hai phương thức sai ở những chỗ khác nhau → **dung hợp** có thể bổ sung cho nhau.
- Đề xuất: FT-Transformer + Bio_ClinicalBERT + **cross-attention** + **hiệu chuẩn nhiệt độ** + lớp **giải trình có trích dẫn**.

**Lời nói:**
> Khi đối chiếu từng ca, chúng em thấy có ca mô hình bảng sai mà mô hình văn bản đúng, và ngược lại. Từ đó hình thành giả thuyết của Giai đoạn 2: kết hợp hai phương thức sẽ khắc phục điểm mù của từng bên. Đây là *giả thuyết*, và phần sau sẽ cho thấy kết quả kiểm chứng nó ra sao.

**Câu chuyển:** *"Em xin chuyển sang Giai đoạn 2: hiện thực hoá đề xuất."*

---

# GIAI ĐOẠN 2 — MÔ HÌNH DUNG HỢP, GIẢI TRÌNH, PHẦN MỀM & ĐÁNH GIÁ

## Slide 10 — Kiến trúc tổng thể  *(TV1, 1 phút)*

**Hiển thị:** sơ đồ `docs/paper_latex/figures/fig01_system_architecture.tex`:
Dữ liệu bảng → FT-Transformer ─┐
Ghi chú → Bio_ClinicalBERT ────┴→ Cross-attention → Temperature scaling → Xác suất 4 bệnh
Xác suất + ghi chú → Truy xuất phác đồ (Qdrant) → Neo bằng chứng → Giao diện bác sĩ

**Lời nói:**
> Hệ thống có ba tầng: tầng mô hình cho ra xác suất đã hiệu chuẩn; tầng giải trình truy xuất phác đồ và chỉ ra câu chứng cứ trong chính bệnh án; tầng phần mềm gồm API và giao diện, đóng gói bằng Docker.

**Câu chuyển:** *"Trọng tâm của tầng mô hình là cơ chế chú ý chéo."*

---

## Slide 11 — Cross-attention & hiệu chuẩn nhiệt độ  *(TV1, 1,5 phút)*

**Hiển thị:**
- Q = token [CLS] của bảng; K, V = các token văn bản: `softmax(QKᵀ/√d)·V`.
- Cổng (gate) trộn biểu diễn bảng và phần lấy từ văn bản: `h = g⊙bảng + (1−g)⊙văn_bản`.
- Temperature scaling: `p = softmax(z/T)`, T khớp trên validation; mô hình triển khai T = 1,21.
- Ba biến thể đối chứng: chỉ bảng · chỉ văn bản · ghép nối (concat).

**Lời nói:**
> Thay vì ghép phẳng hai vector, phần bảng "đặt câu hỏi" lên văn bản: dựa vào sinh hiệu, mô hình tìm những đoạn văn bản liên quan nhất. Một cổng học được quyết định tin bên nào nhiều hơn cho từng bệnh nhân. Cuối cùng chúng em chia logit cho một hệ số nhiệt độ học trên tập validation, để xác suất 80% thật sự nghĩa là khoảng 80% đúng.

**Giải thích sâu:**
- *Attention:* trọng số = mức tương đồng giữa truy vấn và khoá; đầu ra = tổng có trọng số của giá trị. Mặt nạ padding ngăn chú ý vào token đệm.
- *Hiệu chuẩn:* mạng nơ-ron thường quá tự tin. Temperature scaling chỉ có 1 tham số, **không đổi thứ hạng** nên không đổi AUROC/accuracy, chỉ đổi độ tin cậy.
- *ECE* (Expected Calibration Error): chia dự đoán thành các bin theo độ tin cậy, lấy trung bình |độ chính xác − độ tin cậy| có trọng số.
- Thiết kế công bằng ở Giai đoạn 3: BERT 11 khối đầu đóng băng, khối cuối hoặc đóng băng hoặc fine-tune **cho cả** mô hình văn bản và mô hình dung hợp.

**Câu chuyển:** *"Bạn … trình bày lớp giải trình."*

---

## Slide 12 — Giải trình: truy xuất phác đồ & neo bằng chứng  *(TV3, 1,5 phút)*

**Hiển thị:**
- Cơ sở tri thức: **64 đoạn** diễn giải ngắn từ GINA 2024, GOLD 2024, ESC 2023, hướng dẫn Bộ Y tế (QĐ 1851/2020, 2767/2023, 1857/2022, 4815/2020) – có mã nguồn, phiên bản, mục.
- Truy xuất lai: vector + BM25, hợp nhất RRF; 60 truy vấn gán nhãn kép (κ = 0,94): Recall@5 = 1,00, MRR = 0,93.
- `EvidenceGrounder`: mỗi câu chứng cứ phải khớp **đúng vị trí ký tự** trong ghi chú đã khử định danh; câu không có trong bệnh án bị loại.
- Trên 50 ca test strict: 199/200 claim được neo; 50/50 chuỗi giả bị từ chối.
- Chế độ suy luận: **mẫu tất định** (chưa dùng LLM).

**Lời nói:**
> Bác sĩ không tin một con số trơ trọi. Hệ thống trả kèm đoạn phác đồ liên quan và tô sáng câu chứng cứ ngay trong bệnh án. Điểm mấu chốt: mọi câu tô sáng phải tồn tại nguyên văn tại đúng vị trí trong ghi chú – nếu không khớp thì bị loại. Chúng em cũng nói rõ giới hạn: khớp chuỗi không có nghĩa là diễn giải lâm sàng đúng, và phần chấm ngữ nghĩa thủ công 20 đoạn chưa thực hiện.

**Giải thích sâu:**
- *RAG* (Lewis et al., 2020): truy xuất tài liệu rồi dùng làm căn cứ cho câu trả lời.
- *BM25:* xếp hạng theo từ khoá; *vector dense:* theo ngữ nghĩa. *RRF:* cộng nghịch đảo thứ hạng của hai danh sách.
- Hiện vector dùng hàm băm 768 chiều ngoại tuyến (chưa có encoder all-mpnet trong cache) → nói rõ nếu bị hỏi.
- *Cohen's κ:* độ đồng thuận giữa 2 người gán nhãn đã trừ ngẫu nhiên; 0,94 là rất cao.
- Không phân phối toàn văn GINA/GOLD/ESC vì có bản quyền.

**Câu chuyển:** *"Tất cả được đóng gói thành một ứng dụng chạy được."*

---

## Slide 13 — Ứng dụng & demo  *(TV3, 2 phút – demo trực tiếp hoặc video dự phòng)*

**Hiển thị / thao tác:**
1. Trang chủ: nhập ca `PT-0254` (preset) → bấm phân tích.
2. **DiagnosticCard:** xác suất đã hiệu chuẩn (COPD ~92%), nhãn "Calibrated", cảnh báo khi Top-1 < 55%.
3. **EvidenceViewer:** câu chứng cứ tô màu trong ghi chú. **GuidelineDrawer:** mở đoạn phác đồ GOLD.
4. Công tắc **thiếu phương thức:** ẩn ghi chú → xác suất thay đổi.
5. Trang `/evaluation`: bảng RQ1, biểu đồ RQ2, DCA – đọc trực tiếp từ `results/registry.json`.
6. Banner "nguyên mẫu nghiên cứu", footer model card (checkpoint SHA, seed 101, T = 1,21).

**Lời nói:**
> Đây là giao diện cho bác sĩ. Em nhập một ca, hệ thống trả xác suất đã hiệu chuẩn, tô sáng chứng cứ, mở phác đồ tương ứng. Em thử tắt ghi chú để thấy mô hình phản ứng khi thiếu dữ liệu. Mọi số liệu trên trang đánh giá đọc từ một tệp kết quả duy nhất, không có số gõ tay.

**Giải thích sâu:**
- Kiến trúc: Next.js 14 (giao diện) – FastAPI (API) – Qdrant (vector DB); `docker compose up`. Bản đầy đủ: `MCDSS_INSTALL_ML=1`.
- Độ trễ đo nội tiến trình trên CPU: `/predict/multimodal` p50 ≈ 782 ms, `/predict/baseline` ≈ 203 ms, `/agent/explain` ≈ 19 ms.
- Nếu demo lỗi: chuyển ngay sang video/ảnh chụp, không gỡ lỗi trước hội đồng.

**Câu chuyển:** *"Bây giờ là câu hỏi quan trọng nhất: mô hình dung hợp có thật sự tốt hơn không?"*

---

## Slide 14 — Thiết kế đánh giá  *(TV1, 45 giây)*

**Hiển thị:**
- Kế hoạch phân tích **đăng ký trước** (hash đóng băng trước khi chạy).
- 10 mô hình × **5 seed**; hiệu chuẩn trên validation; báo cáo trên test strict N = 302.
- CI 95% bootstrap (B = 2000), hiệu chỉnh Holm; phân tích độ nhạy: temporal split, 5-fold grouped CV (post-hoc).

**Lời nói:**
> Để tránh chọn kết quả đẹp, chúng em ghi trước kế hoạch phân tích và khoá lại bằng mã băm trước khi chạy. Mỗi mô hình chạy năm seed, có khoảng tin cậy, và so sánh nhiều cặp được hiệu chỉnh Holm.

**Giải thích sâu:**
- *Seed:* hạt giống ngẫu nhiên; chạy nhiều seed để thấy độ dao động do khởi tạo.
- *Bootstrap ghép cặp:* lấy mẫu lại cùng một tập bệnh nhân cho hai mô hình, tính hiệu AUROC 2000 lần → khoảng tin cậy của hiệu.
- *Holm:* hiệu chỉnh p khi kiểm định nhiều so sánh, giảm dương tính giả.
- Chú ý: bootstrap theo bản ghi, mà bản ghi chung bệnh nhân gốc → CI hẹp hơn thực tế.

---

## Slide 15 — RQ1: So sánh công bằng  *(TV1, 2 phút)*

**Hiển thị:**

| Mô hình | AUROC test strict (TB ± SD) | So với cross-attention | Grouped CV |
| :--- | :---: | :--- | :---: |
| Logistic Regression (bảng) | 0,945 | không khác (p = 0,46) | 0,909 ± 0,021 |
| CatBoost (bảng) | 0,925 ± 0,003 | thấp hơn (p = 0,01) | 0,892 ± 0,036 |
| BERT fine-tune (văn bản) | **0,975 ± 0,004** | **cao hơn** (Δ +0,020, p = 0,012) | 0,894 ± 0,148 |
| Ensemble CatBoost + BERT | **0,978 ± 0,003** | **cao hơn** (Δ +0,024, p = 0,009) | 0,931 ± 0,066 |
| **Cross-attention (triển khai)** | 0,956 ± 0,008 | tham chiếu | **0,949 ± 0,016** |

**Lời nói:**
> Đây là kết quả trung thực. Trên tập test strict, mô hình chỉ đọc văn bản fine-tune và một ensemble rất đơn giản đều cao hơn mô hình dung hợp của chúng em một cách có ý nghĩa thống kê; mô hình dung hợp chỉ ngang Logistic Regression dùng bảng. Tuy nhiên khi kiểm tra lại bằng grouped cross-validation, mô hình dung hợp lại ổn định nhất, trong khi BERT dao động mạnh – có fold chỉ còn 0,63. Kết luận của chúng em: chưa có bằng chứng dung hợp vượt trội, và thứ hạng mô hình không bền trên dữ liệu này.

**Giải thích sâu:**
- Vì sao kết quả trái chiều: tập test chỉ gồm 62 bệnh nhân gốc; suy tim và viêm phổi mỗi lớp **1 bệnh nhân**. Đổi bệnh nhân rơi vào test là đổi thứ hạng.
- *Ensemble* là phương án dung hợp đơn giản nhất (trung bình xác suất) – phản biện luôn hỏi; chúng em đã đưa vào.
- Mô hình triển khai được chọn **trước** khi xem test theo quy tắc NLL validation thấp nhất (seed 101) – không cherry-pick.
- Macro-F1 cross-attention chỉ ~0,69 dù AUROC cao: 42/62 lỗi thuộc **một** bệnh nhân viêm phổi ~82 tuổi bị đoán là hen (mô hình học "viêm phổi ≈ 100 tuổi").

**Câu chuyển:** *"Vậy vì sao mô hình chỉ đọc văn bản lại mạnh đến thế?"*

---

## Slide 16 — RQ2: Tín hiệu văn bản đến từ đâu?  *(TV1, 1,5 phút)*

**Hiển thị:**

| Biến thể ghi chú | TF-IDF | BERT fine-tune | Cross-attention |
| :--- | :---: | :---: | :---: |
| Gốc | 0,917 | 0,974 | 0,954 |
| Che **mọi con số** | **0,541** | **0,679** | 0,920 |
| Bỏ sinh hiệu (còn tuổi) | 0,885 | 0,905 | 0,965 |
| Chỉ phần tự sự | 0,826 | 0,776 | 0,917 |

Hình: `fig_rq2_text_decomposition`.

**Lời nói:**
> Chúng em làm một thí nghiệm đơn giản: lần lượt xoá các phần của ghi chú. Khi che hết các con số, mô hình văn bản rơi gần về mức đoán ngẫu nhiên. Khi chỉ bỏ sinh hiệu mà còn giữ tuổi, văn bản vẫn rất mạnh – vì trong dữ liệu này tuổi gần như quyết định bệnh. Nghĩa là ghi chú đang chép lại chính số liệu của bảng; "hai phương thức" thực chất là một. Đây là một dạng lối tắt mà nếu không kiểm tra, ta dễ kết luận sai rằng AI đã hiểu văn bản lâm sàng.

**Giải thích sâu:**
- *Shortcut learning* (Geirhos et al., 2020): mô hình dùng tín hiệu dễ nhưng không có ý nghĩa nhân quả.
- Cross-attention giữ ~0,92 khi che số vì lùi về nhánh bảng → chứng tỏ nó *dựa vào bảng*, không phải văn bản.
- Đây là đóng góp phương pháp: một kiểm tra rẻ (che số) nên làm với mọi bộ dữ liệu EHR đa phương thức.

**Câu chuyển:** *"Nếu văn bản thật sự có thông tin riêng thì sao?"*

---

## Slide 17 — RQ3: Khi nào dung hợp có ích? (mô phỏng)  *(TV1, 1 phút)*

**Hiển thị:** heatmap `fig_rq3_heatmap`: ρ = tỷ lệ ca được chèn câu triệu chứng đặc hiệu vào ghi chú đã che số; σ = nhiễu trên dữ liệu bảng.
- ρ = 0: dung hợp ≈ bảng (Δ ≈ −0,005).
- ρ = 1, σ = 0: cross-attention 0,976 vs tốt nhất đơn lẻ 0,939 (Δ **+0,037**); ρ = 1, σ = 0,5: Δ **+0,054**.
- Concat không đạt được mức này.

**Lời nói:**
> Chúng em mô phỏng: chèn vào một phần ghi chú câu triệu chứng đặc trưng lấy từ phác đồ, và làm nhiễu dữ liệu bảng. Khi văn bản mang thông tin mà bảng không có, cross-attention vượt cả hai mô hình đơn lẻ và vượt cả cách ghép đơn giản. Đây là mô phỏng, không phải hiệu năng lâm sàng – nhưng nó cho thấy kiến trúc hoạt động đúng khi dữ liệu thoả điều kiện.

**Giải thích sâu:** tín hiệu do nhóm thiết kế (có 10% câu gây nhiễu từ lớp sai) → chỉ chứng minh cơ chế. Với dữ liệu thật (ví dụ MIMIC-IV), ghi chú mô tả triệu chứng, đáp ứng điều trị mà bảng không có – đúng điều kiện ρ cao.

---

## Slide 18 — RQ4: Hiệu chuẩn & độ bền khi thiếu dữ liệu  *(TV1, 1 phút)*

**Hiển thị:**
- ECE: 0,079 (chưa hiệu chuẩn) → **0,077** (temperature); vector scaling, isotonic không tốt hơn → **chưa đạt mục tiêu < 0,05**.
- Thiếu dữ liệu lúc suy luận (AUROC):

| Kịch bản | Cross-attention | CatBoost |
| :--- | :---: | :---: |
| Đầy đủ | 0,956 | 0,925 |
| Thiếu 50% biến số | **0,888** | 0,823 |
| Mất toàn bộ bảng | 0,678 | 0,500 |
| Mất văn bản | 0,902 | 0,925 |

**Lời nói:**
> Hiệu chuẩn có cải thiện nhưng chưa đạt mục tiêu đặt ra – chúng em báo cáo đúng như vậy. Khi thiếu một phần biến số, mô hình dung hợp chịu đựng tốt hơn CatBoost vì vẫn đọc được giá trị trong ghi chú; nhưng mất toàn bộ bảng thì giảm mạnh. Hướng cải thiện là huấn luyện có bỏ ngẫu nhiên phương thức.

**Giải thích sâu:** validation chỉ 273 ca và test lệch phân bố → khó đạt ECE thấp. *Modality dropout:* khi huấn luyện, ngẫu nhiên ẩn một phương thức để mô hình học cách tự lập.

---

## Slide 19 — DCA & tự thẩm định PROBAST+AI  *(TV1, 1 phút)*

**Hiển thị:**
- DCA suy tim (one-vs-rest), ngưỡng định trước 5–30%, hành động giả định: NT-proBNP + siêu âm tim.
- p_t = 0,10: NB mô hình 0,345 vs can thiệp tất cả 0,279 (giảm ~60 can thiệp/100 BN); p_t = 0,20: 0,344 vs 0,189.
- **Cảnh báo:** 106 ca suy tim trong test đến từ 1 bệnh nhân gốc → chỉ minh hoạ phương pháp.
- PROBAST+AI: Người tham gia **Cao** · Biến dự báo **Thấp/Chưa rõ** · Kết cục **Cao** · Phân tích **Chưa rõ** → tổng thể **nguy cơ sai lệch cao**.

**Lời nói:**
> Phân tích đường cong quyết định cho thấy dùng mô hình có lợi ích ròng cao hơn chiến lược xét nghiệm tất cả, nhưng toàn bộ ca suy tim trong tập test là của một bệnh nhân gốc, nên chúng em chỉ coi đây là minh hoạ phương pháp. Tự thẩm định theo PROBAST+AI, chúng em chấm nguy cơ sai lệch cao do bản chất dữ liệu bán tổng hợp – chúng em chọn nói thẳng điều này.

**Giải thích sâu:**
- *Net benefit* = TP/N − FP/N × p_t/(1−p_t). Ngưỡng p_t thể hiện tỷ lệ đánh đổi hại/lợi bác sĩ chấp nhận.
- Số can thiệp giảm ròng/100 = (NB − NB_all) × (1−p_t)/p_t × 100 (Vickers 2016). Bản trước dùng sai công thức – đã sửa.

---

# KẾT LUẬN

## Slide 20 — Kết luận & đóng góp  *(TV1, 1 phút)*

**Hiển thị:**
1. **Quy trình dữ liệu có kiểm toán rò rỉ** đến mức nội dung ghi chú – đã bắt được một lỗi rò rỉ thật trong quá trình làm.
2. **Đánh giá công bằng, đăng ký trước:** dung hợp chưa vượt phương án đơn giản trên test strict; ổn định nhất trong grouped CV.
3. **Phân tích cơ chế:** tín hiệu văn bản = số liệu chép lại; mô phỏng chỉ ra điều kiện để dung hợp có ích.
4. **Nguyên mẫu phần mềm tái lập được:** xác suất hiệu chuẩn, giải trình neo vị trí ký tự, mọi số liệu từ một registry.

**Lời nói:**
> Tóm lại, chúng em đã xây dựng trọn vẹn một hệ thống hỗ trợ chẩn đoán đa phương thức và đánh giá nó một cách nghiêm ngặt. Kết quả không phải "mô hình của chúng em tốt nhất", mà là hiểu được *khi nào* dung hợp có giá trị và *vì sao* những con số cao có thể đánh lừa. Chúng em tin đây là kết quả có ích hơn cho những ai sẽ làm tiếp với dữ liệu thật.

---

## Slide 21 — Giới hạn & hướng tiếp theo  *(TV1, 30 giây)*

**Hiển thị:**
- Giới hạn: dữ liệu bán tổng hợp, 478 bệnh nhân gốc, nhãn không do bác sĩ; một tập test; ECE chưa đạt; chưa LLM; chưa chấm ngữ nghĩa thủ công; chưa khảo sát bác sĩ, chưa ngoại kiểm.
- Tiếp theo: (1) MIMIC-IV (đang làm thủ tục CITI/PhysioNet); (2) modality dropout; (3) chế độ LLM có ràng buộc neo bằng chứng; (4) khảo sát ≥ 2 bác sĩ theo giao thức đã soạn; (5) đề cương IRB với dữ liệu bệnh viện Việt Nam.

**Lời nói:**
> Chúng em xin cảm ơn hội đồng đã lắng nghe và rất mong nhận được góp ý.

---

# PHỤ LỤC A — BỘ CÂU HỎI DỰ KIẾN & GỢI Ý TRẢ LỜI

| # | Câu hỏi | Ai trả lời | Ý chính (≤ 3 câu) |
| :---: | :--- | :---: | :--- |
| 1 | Dữ liệu có thật không? | TV2 | Bán tổng hợp: bảng từ Synthea, văn bản từ MTSamples. Chưa có phê duyệt đạo đức để dùng dữ liệu bệnh viện. Kết luận chỉ áp dụng trên đoàn hệ này. |
| 2 | Mô hình của nhóm không thắng, vậy đóng góp là gì? | TV1 | Đóng góp là quy trình đánh giá đáng tin, phát hiện lối tắt văn bản, điều kiện để dung hợp có ích (RQ3) và phần mềm tái lập được. Báo cáo kết quả âm tính trung thực là đúng chuẩn TRIPOD+AI. |
| 3 | Sao biết không rò rỉ? | TV2 | Chia theo bệnh nhân gốc và ghi chú nguồn; che tên chẩn đoán; audit tự động; thử che số thì văn bản về ~0,54. |
| 4 | Vì sao AUROC cao mà F1 thấp? | TV1 | AUROC đo xếp hạng ở mọi ngưỡng, F1 ở một ngưỡng. Lỗi dồn vào một bệnh nhân viêm phổi gốc. |
| 5 | ECE là gì, sao chưa đạt? | TV1 | Sai lệch giữa độ tin cậy và tỷ lệ đúng. Validation nhỏ, test lệch phân bố; báo cáo đúng 0,077. |
| 6 | Grounding có chống ảo giác không? | TV3 | Đảm bảo câu tô sáng có thật trong bệnh án (199/200, 50/50 chuỗi giả bị loại). Không đảm bảo diễn giải đúng ngữ nghĩa – chưa chấm thủ công. |
| 7 | Vì sao chưa dùng LLM? | TV3 | Ưu tiên tái lập và kiểm chứng; chế độ tất định không bịa. LLM có ràng buộc là hướng tiếp theo. |
| 8 | Chạy CPU được không, nhanh không? | TV3 | Được: ~0,8 giây/ca cho mô hình dung hợp trên CPU; giải trình ~20 ms. |
| 9 | DCA có ý nghĩa gì ở đây? | TV1 | Minh hoạ phương pháp; tỷ lệ suy tim 35% và từ 1 bệnh nhân gốc nên không ngoại suy. |
| 10 | Fairness trên dữ liệu tổng hợp có nghĩa không? | TV2 | Chỉ kiểm tra pipeline phân nhóm; nhiều nhóm thiếu lớp nên không kết luận công bằng. |
| 11 | Triển khai thật cần gì? | TV3 | Dữ liệu thật + ngoại kiểm, phê duyệt IRB, chuẩn HL7 FHIR, phân quyền, nhật ký kiểm toán, giám sát trôi dữ liệu. |
| 12 | Nếu có MIMIC-IV thì sao? | TV1 | Ghi chú thật chứa thông tin ngoài bảng – đúng điều kiện RQ3. Kỳ vọng AUROC tuyệt đối thấp hơn nhưng đo được đóng góp thật của văn bản. |

**Nguyên tắc khi trả lời:** trả lời ngắn, có số, thừa nhận giới hạn trước khi bị chỉ ra; không hứa điều chưa đo; câu nào chưa biết thì nói "nhóm sẽ kiểm tra và bổ sung".

# PHỤ LỤC B — CHECKLIST TRƯỚC BUỔI BẢO VỆ
- [ ] Đối chiếu mọi số trên slide với `results/registry.json` / `MODEL_CARD.md`.
- [ ] Chạy thử demo trên máy trình chiếu; chuẩn bị video và ảnh chụp dự phòng.
- [ ] Mỗi người tập phần mình ≥ 2 lần, bấm giờ; tổng ≤ 22 phút.
- [ ] Mỗi người thuộc 4 câu hỏi Phụ lục A trong phần của mình.
- [ ] Mang theo bản in PROBAST+AI và bảng RQ1 để chỉ khi hội đồng hỏi.
