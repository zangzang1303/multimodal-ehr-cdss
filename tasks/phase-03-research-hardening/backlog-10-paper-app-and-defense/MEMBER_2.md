# BACKLOG 10 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

**Trạng thái thực thi:** [✓] ĐÃ HOÀN THÀNH 100% CÁC NHIỆM VỤ  
**Ngày hoàn tất:** 2026-11-19  
**Người thực hiện:** Thành viên 2 (Biomedical Data Engineer & Privacy)  

---

## Nhiệm vụ 2.1 – Data & Cohort, Ethics [✓ HOÀN THÀNH]
- [x] **Cập nhật `docs/paper_latex/sections/02_clinical_cohort.tex`:**
  - Mô tả **trung thực** cách kiến tạo dữ liệu bán tổng hợp (semi-synthetic cohort): dữ liệu dạng bảng từ mô phỏng sinh lý học Synthea EHR, dữ liệu văn bản từ ghi chú lâm sàng MTSamples ghép nối có chọn lọc.
  - Phân tích rõ ràng việc **chèn khối sinh hiệu vào ghi chú theo template hành chính** – đây là cội nguồn phát hiện thực nghiệm then chốt RQ2 (hiện tượng dư thừa phương thức và mô hình text đọc lại sinh hiệu).
  - Trình bày việc **cài cắm thông tin định danh (PHI) giả lập** (mã thẻ BHYT, học hàm/học vị bác sĩ, bệnh viện viết HOA toàn bộ) để kiểm thử pipeline khử định danh.
- [x] **Flow diagram TRIPOD:**
  - Thiết kế sơ đồ dòng đối tượng hoàn chỉnh dạng TikZ vector: `docs/paper_latex/figures/fig_tripod_flow.tex` và nhúng trực tiếp vào Phân mục 2 qua `\input{figures/fig_tripod_flow}`.
  - Xuất phiên bản đồ họa vector SVG độc lập phục vụ trình chiếu slide/web: `docs/paper_latex/figures/svg/fig_tripod_flow.svg`.
  - Thể hiện đầy đủ luồng: Nguồn ($N_1 = 2.450, N_2 = 4.999$) $\rightarrow$ Tiêu chí loại trừ \& Anti-leakage $\rightarrow$ Đoàn hệ chuẩn hóa 2.000 hồ sơ $\rightarrow$ Stratified Group Splitting (Train 1.425 / Val 273 / Test 302, 0\% rò rỉ).
- [x] **Bảng 1 (Table 1) – Đặc điểm lâm sàng ban đầu của đoàn hệ:**
  - Số liệu thực nghiệm tính toán trực tiếp từ `data/processed_rebuilt_strict/*.parquet`.
  - Báo cáo phân tách song song theo cả hai chiều: (1) Theo các tập phân chia (Toàn bộ $N=2.000$, Train $N=1.425$, Val $N=273$, Test $N=302$) và (2) Theo 4 nhóm bệnh mục tiêu (Hen, COPD, Suy tim, Viêm phổi, $n=500$ mỗi nhóm).
  - Thể hiện đầy đủ: Tuổi, Giới tính, Tiền sử (hút thuốc, tăng huyết áp, đái tháo đường), 6 chỉ số sinh hiệu dạng Trung vị [IQR] và tỷ lệ khuyết thiếu thực tế (WBC khuyết 14,4\%, CRP khuyết 19,1\%).
- [x] **Cập nhật `docs/paper_latex/sections/08_discussion_ethics.tex`:**
  - Bảng thống kê chi tiết kết quả audit PHI trước/sau (mã BHYT giảm từ 84\% $\rightarrow$ 0\%, học hàm bác sĩ từ 72\% $\rightarrow$ 0\%, bệnh viện viết HOA từ 100\% $\rightarrow$ 0\%, bảo toàn sinh hiệu đạt 100\%).
  - Phân định ma trận giấy phép đa tầng: MIT cho mã nguồn M-CDSS; Apache 2.0 / PhysioNet Credentialed cho Bio\_ClinicalBERT; Apache 2.0 cho all-mpnet-base-v2 và Synthea; Academic Terms cho MTSamples; Fair-use citation cho phác đồ CPGs (GINA, GOLD, ESC, BYT).
  - Tuyên bố y đức minh bạch: M-CDSS là nguyên mẫu nghiên cứu hỗ trợ quyết định lâm sàng, không thay thế bác sĩ và chưa được phép sử dụng trực tiếp trên bệnh nhân thực tế khi chưa có thử nghiệm tiến cứu và phê duyệt IRB.

---

## Nhiệm vụ 2.2 – TRIPOD+AI & PROBAST+AI [✓ HOÀN THÀNH]
- [x] **Biên soạn Phụ lục TRIPOD+AI (`docs/paper_latex/sections/appendix_tripod_ai.tex`):**
  - Bao phủ đầy đủ 27 tiêu chuẩn theo hướng dẫn quốc tế TRIPOD+AI (Collins et al., The BMJ / Nat Med 2024; Moons et al., The BMJ 2024).
  - Bảng đối chiếu gồm 5 cột: Mục, Chủ đề, Tiêu chuẩn báo cáo, Vị trí trong bài báo, và Ghi chú thực thi lâm sàng \& kỹ thuật.
  - Đánh dấu rõ ràng các mục N/A kèm lý do khoa học minh bạch (ví dụ: Mục 18 Ngoại kiểm độc lập trên bệnh nhân thực tế tại Việt Nam hiện chưa thực hiện và được ghi nhận là giới hạn cốt lõi).
- [x] **Biên soạn Phụ lục PROBAST+AI (`docs/paper_latex/sections/appendix_probast_ai.tex`):**
  - Chuyển giao toàn bộ đánh giá 20 câu hỏi tín hiệu từ Backlog 08 và cập nhật kết quả phân tích thống kê chuyên sâu từ Backlog 09.
  - Miền 4 (Analysis) được nâng cấp thành công lên **Low Risk of Bias / Low Applicability Concern** nhờ bổ sung: 95\% Bootstrap CI (2.000 replicates), hiệu chỉnh Holm-Bonferroni, kiểm tra tổng quát hóa chuỗi thời gian ($N=600$, AUROC 0,9884), kiểm tra thiếu hụt phương thức (Missing modality stress test), phân tích lợi ích ròng DCA trên suy tim và phân tích 30 ca sai biệt.
  - Duy trì kết luận tổng thể liêm chính: **High Risk of Bias / High Applicability Concern** xuất phát từ bản chất dữ liệu bán tổng hợp (Miền 1 & Miền 3).
- [x] **Tích hợp vào `docs/paper_latex/main.tex`:**
  - Đã nạp môi trường `\appendix` cùng hai tệp phụ lục `\input{sections/appendix_tripod_ai}` và `\input{sections/appendix_probast_ai}`.

---

## Nhiệm vụ 2.3 – Tài liệu tham khảo (12 → ≥ 35) [✓ HOÀN THÀNH]
- [x] **Mở rộng `docs/paper_latex/references.bib`:**
  - Nâng cấp từ 12 lên **38 tài liệu tham khảo học thuật chính thức** (vượt chỉ tiêu $\ge 35$).
  - Bao phủ đầy đủ các nhóm bắt buộc:
    - **Hướng dẫn & Đánh giá sai lệch:** TRIPOD+AI Statement (`collins2024tripod`), TRIPOD+AI E&E (`moons2024tripod`), PROBAST+AI (`probastai2024bmj`, `moons2025probast`), TRIPOD/PROBAST Protocol (`collins2021protocol`).
    - **Tổng quan nền tảng & Sai sót:** Tổng quan JMIR (`hunik2024diagnostic`), Shortcut learning (`geirhos2020shortcut`), Data Leakage trong ML (`kapoor2023leakage`).
    - **Kiến trúc mô hình & Dung hợp:** FT-Transformer (`gorishniy2021revisiting`), Bio\_ClinicalBERT (`alsentzer2019publicly`), BERT (`devlin2019bert`), BioBERT (`lee2020biobert`), CatBoost (`prokhorenkova2018catboost`), Attention (`vaswani2017attention`), Tổng quan Multimodal AI y tế (`huang2020multimodal`, `kline2022multimodal`, `shickel2018deepehr`), Sentence-BERT (`reimers2019sentence`), DPR (`karpukhin2020dense`), RAG (`lewis2020rag`).
    - **Hiệu chuẩn & Tiện ích lâm sàng:** Temperature Scaling (`guo2017calibration`), Đánh giá hiệu chuẩn y học (`vancalster2019calibration`), Decision Curve Analysis (`vickers2006decision`, `vickers2016netbenefit`), Đạo đức & Fairness trong AI y tế (`rajkomar2018fairness`).
    - **Dữ liệu & Khử định danh:** Synthea EHR (`walonoski2018synthea`), MTSamples (`mtsamples2012`), MIMIC-IV (`johnson2023mimiciv`), MICE (`vanbuuren2011mice`), Khử định danh y tế tự động (`neamatullah2008deidentification`), Hướng dẫn HIPAA Safe Harbor (`hhs2012hipaa`).
    - **Phác đồ Hướng dẫn Điều trị Lâm sàng (CPGs):** GINA 2024 Hen (`gina2024asthma`), GOLD 2024 COPD (`gold2024copd`), ESC 2023 Suy tim (`mcdonagh2023esc`), Bộ Y tế Việt Nam (Hen `moh2020asthma`, COPD `moh2023copd`, Suy tim `moh2022heartfailure`, Viêm phổi `moh2020pneumonia`).
- [x] **Kiểm tra chéo tồn tại:** 100\% các mục đều có mã định danh số DOI, ISBN hoặc URL chính thức, đã kiểm tra chéo không có mục nào là tài liệu giả lập.

---

## Nhiệm vụ 2.4 – Q&A phần dữ liệu & đạo đức [✓ HOÀN THÀNH]
- [x] **Biên soạn tài liệu phòng vệ đề tài (`docs/thuyết trình/QA_DEFENSE_MEMBER_2_DATA_ETHICS.md`):**
  - Trả lời sắc bén, súc tích (2–3 câu), có số liệu dẫn chứng cụ thể cho 5 câu hỏi trọng tâm của Hội đồng:
    1. *Dữ liệu có thật không?* $\rightarrow$ Minh bạch bán tổng hợp (Synthea + MTSamples), tự chấm High Risk theo PROBAST.
    2. *Vì sao không dùng dữ liệu bệnh viện Việt Nam?* $\rightarrow$ Tuân thủ Nghị định 13/2023/NĐ-CP, Luật Khám chữa bệnh 15/2023/QH15 và yêu cầu phê duyệt của Hội đồng Đạo đức (IRB).
    3. *Khử định danh (de-ID) được đánh giá thế nào?* $\rightarrow$ Đưa tỷ lệ sót từ 72\%--100\% về đúng 0,0\%, kiểm thử âm tính bảo toàn 100\% sinh hiệu.
    4. *Tính công bằng (Fairness) có ý nghĩa gì trên dữ liệu tổng hợp?* $\rightarrow$ Phép kiểm toán thuật toán (algorithmic fairness audit) kiểm chứng hàm mất mát không thiên lệch, chứng minh tính sẵn sàng của pipeline trước khi nạp dữ liệu thực.
    5. *Kế hoạch ngoại kiểm lâm sàng \& xin phép đạo đức (IRB) ra sao?* $\rightarrow$ Lộ trình 2 giai đoạn: Ngoại kiểm Zero-shot trên MIMIC-IV (Mỹ) và Đề cương nghiên cứu hồi cứu đa trung tâm nộp IRB tại Việt Nam kèm giao thức khảo sát chuyên gia.

---

## Danh mục Deliverables đã bàn giao
1. `docs/paper_latex/sections/02_clinical_cohort.tex`
2. `docs/paper_latex/figures/fig_tripod_flow.tex`
3. `docs/paper_latex/figures/svg/fig_tripod_flow.svg`
4. `docs/paper_latex/sections/08_discussion_ethics.tex`
5. `docs/paper_latex/sections/appendix_tripod_ai.tex`
6. `docs/paper_latex/sections/appendix_probast_ai.tex`
7. `docs/paper_latex/main.tex`
8. `docs/paper_latex/references.bib`
9. `docs/thuyết trình/QA_DEFENSE_MEMBER_2_DATA_ETHICS.md`
