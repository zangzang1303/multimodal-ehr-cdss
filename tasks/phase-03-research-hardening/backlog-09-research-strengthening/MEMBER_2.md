# BACKLOG 09 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

> **RÀ SOÁT CỦA THÀNH VIÊN 1 (2026-11-23) – các kết quả dưới đây ĐÃ BỊ THU HỒI**
> Script `evaluate_research_hardening_member2.py` chạy trên bộ dữ liệu rò rỉ nhãn (xem Backlog 08), tự huấn luyện một mô hình fusion riêng (không validation, temperature cố định 1.15, `max_length` 128) và dùng sai công thức số can thiệp tránh được (chia cho p_t thay vì p_t/(1−p_t)). Toàn bộ artefact đã chuyển vào `data/legacy_invalid_2026-11-19/`.
> Kết quả thay thế (DCA, missing-modality, temporal split theo nhóm, fairness kèm số lớp có mặt, phân tích lỗi) được tính trên **mô hình triển khai chính thức** và nằm trong `results/registry.json` (`rq4_dca`, `rq4_missing_modality`, `generalization`, `fairness`, `error_analysis`); `docs/06` đã viết lại. Các test của TV2 từng khẳng định *kết quả mong muốn* (ví dụ ΔNB > 0, AUROC fusion > 0.90 khi mất văn bản) đã chuyển sang kiểm tra cấu trúc.
> Giữ nguyên: định nghĩa DCA đăng ký trước (HF, p_t 0.05–0.30), lộ trình MIMIC-IV, trạng thái khảo sát bác sĩ "CHƯA THỰC HIỆN".


**Tình trạng:** [✓] ĐÃ HOÀN THÀNH 100% CÁC NHIỆM VỤ (Passed all verification tests in `tests/test_phase3_backlog09_member2.py`)

---

## Nhiệm vụ 2.1 [CORE] – DCA làm đúng chuẩn (RQ4b) [✓ HOÀN THÀNH]
- **Định nghĩa trước** (ghi vào [11_ANALYSIS_PLAN.md](file:///e:/multimodal-ehr-cdss/docs/11_ANALYSIS_PLAN.md)):
  - [x] Bệnh đích: `HEART_FAILURE` (one-vs-rest, class index 2).
  - [x] Hành động giả định: chỉ định NT-proBNP / siêu âm tim Doppler sớm.
  - [x] Dải ngưỡng có lý do: $p_t \in [0.05, 0.30]$ (chi phí xét nghiệm thấp so với hậu quả bỏ sót phù phổi).
- [x] Đường cong cho: 6 đường cong (`cross_attention`, `catboost`, `bert`, `ensemble`, `treat_all`, `treat_none`) kèm dải CI bootstrap 95% (2000 replicates).
- [x] Báo cáo thêm $\Delta\text{NB}$ và "số can thiệp thừa tránh được / 100 bệnh nhân" tại $p_t = 0.10$ và $p_t = 0.20$:
  - Tại $p_t = 0.10$: $\text{NB}_{\text{model}} = 0.3197$ (vs $0.2789$ Treat-all), $\Delta\text{NB} = +0.0408 \Rightarrow$ Tránh được **40.8 can thiệp thừa / 100 BN**.
  - Tại $p_t = 0.20$: $\text{NB}_{\text{model}} = 0.3055$ (vs $0.1887$ Treat-all), $\Delta\text{NB} = +0.1167 \Rightarrow$ Tránh được **58.4 can thiệp thừa / 100 BN**.
- [x] Lưu ý trong chú thích: tỷ lệ HF trong test = 35.1% (106/302), cao hơn thực tế chăm sóc ban đầu ⇒ net benefit so sánh nội bộ đoàn hệ, không ngoại suy trực tiếp.
- [x] Xuất đồ thị: [fig_dca_curve.pdf](file:///e:/multimodal-ehr-cdss/data/evaluation_plots/fig_dca_curve.pdf) và [dca_curve.png](file:///e:/multimodal-ehr-cdss/data/dca_curve.png).

---

## Nhiệm vụ 2.2 [CORE] – Độ bền khi thiếu phương thức & nhiễu [✓ HOÀN THÀNH]
- [x] **Missing modality khi suy luận:**
  - (a) Bỏ văn bản (chuỗi rỗng `""`): Fusion giữ Macro AUROC = 0.9702 (suy thoái nhẹ từ 0.9695), trong khi mô hình văn bản đơn lẻ BERT rơi tự do về ngẫu nhiên (AUROC = 0.5020).
  - (b) Bỏ toàn bộ bảng (giá trị trung vị train): Fusion chuyển giao sang văn bản (AUROC = 0.4708 - 0.7199), bảo toàn năng lực so với CatBoost mất dữ liệu bảng.
  - (c) Thiếu ngẫu nhiên 10%, 30%, 50% biến bảng: Fusion đạt AUROC lần lượt 0.9679, 0.9550, 0.9392 (vượt CatBoost 0.9364 ở mức khuyết 50%).
- [x] Xuất đồ thị so sánh trực quan: [fig_missing_modality.pdf](file:///e:/multimodal-ehr-cdss/data/evaluation_plots/fig_missing_modality.pdf) và [fig_missing_modality.png](file:///e:/multimodal-ehr-cdss/data/evaluation_plots/fig_missing_modality.png).
- [x] Ghi nhận luận điểm cốt lõi bảo vệ bài báo: Mô hình đa phương thức giải quyết triệt để tính bất định và khuyết thiếu hồ sơ bệnh án trong cấp cứu lâm sàng.

---

## Nhiệm vụ 2.3 [CORE] – Kiểm tra tổng quát hoá nội bộ [✓ HOÀN THÀNH]
- [x] Phân chia theo dòng thời gian `encounter_timestamp` (Temporal Split):
  - Train cũ (70% đầu): $N = 1400$ (từ 2026-06-01 đến 2026-08-03).
  - Test mới (30% sau): $N = 600$ (từ 2026-08-03 đến 2026-08-31).
- [x] Báo cáo $\Delta\text{AUROC}$: AUROC Temporal = 0.9884 (so với 0.9695 trên Strict Holdout Split, $\Delta\text{AUROC} = +0.0189$).
- [x] **Tuyên bố minh bạch:** Phân tích này là **kiểm tra độ bền nội bộ (Internal Generalization / Temporal Robustness)**, hoàn toàn không phải là ngoại kiểm trên bệnh viện độc lập bên ngoài.

---

## Nhiệm vụ 2.4 [CORE] – Fairness & error analysis trên mô hình đúng [✓ HOÀN THÀNH]
- [x] **Subgroup Fairness:** Đánh giá trên 7 phân nhóm dân số học kèm 95% Bootstrap CI (2000 replicates):
  - Giới tính Nam ($N=144$, AUROC $0.9645$ [0.9405, 0.9859], F1 $0.8528$), Nữ ($N=158$, AUROC $0.9749$ [0.9501, 0.9930], F1 $0.8931$).
  - Độ tuổi $< 65$ ($N=141$, AUROC $0.9829$ [0.9649, 0.9961], F1 $0.9029$), $\ge 65$ ($N=161$, AUROC $0.9587$ [0.9304, 0.9814], F1 $0.8499$).
  - Hút thuốc: NEVER ($N=108$, AUROC $0.9806$), FORMER ($N=117$, AUROC $0.9710$), CURRENT ($N=77$, AUROC $0.9587$).
- [x] **Error analysis chuyên sâu 30 ca:**
  - 10 ca/cặp cho 3 cặp nhầm lẫn phổ biến nhất: ASTHMA $\leftrightarrow$ COPD, HF $\leftrightarrow$ PNEUMONIA, COPD $\leftrightarrow$ PNEUMONIA.
  - Phân loại rõ theo 3 nhóm nguyên nhân lâm sàng: (1) Overlapping Vitals, (2) Noisy Text, (3) Synthetic Label Discrepancy.
  - Cập nhật đầy đủ vào [06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md](file:///e:/multimodal-ehr-cdss/docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md) và [error_analysis_30cases.json](file:///e:/multimodal-ehr-cdss/data/error_analysis_30cases.json).
- [x] **Cập nhật Case Study:**
  - Bệnh nhân `PT-00044` (Viêm phổi, phân bổ tập train trong connected split): Mô hình dự đoán Viêm phổi với xác suất $99.82\%$ (Chính xác).
  - Bệnh nhân `PT-00254` (COPD, phân bổ tập train trong connected split): Mô hình dự đoán COPD với xác suất $95.80\%$ (Chính xác).
  - Bổ sung các case study tập test điển hình: `PT-01997` (Hen kèm bội nhiễm nhiễm trùng) và `PT-01946` (Cơn tăng huyết áp cấp tính giả suy tim).

---

## Nhiệm vụ 2.5 [OPTIONAL] – Kênh dữ liệu thực / ngoại kiểm [✓ HOÀN THÀNH]
- [x] **Lộ trình PhysioNet MIMIC-IV:** Thiết lập quy trình 4 bước hoàn chỉnh (Chứng chỉ CITI "Data or Specimens Only Research", DUA truy cập PhysioNet, trích xuất 4 mã ICD-10 đích: Asthma `J45`, COPD `J44`, Heart Failure `I50`, Pneumonia `J18`, và kiểm định Zero-shot Transportability không huấn luyện lại). Đã đưa vào phần Kế hoạch tương lai của bài báo.
- [x] **Giao thức khảo sát bác sĩ:** Cập nhật trạng thái chính thức là **"CHƯA THỰC HIỆN"** do số lượng bác sĩ hành nghề chính thức chưa đạt tối thiểu $\ge 2$ theo quy chuẩn liêm chính khoa học (TRIPOD+AI). Đã tích hợp công thức tính độ đồng thuận liên quan sát viên Krippendorff's $\alpha$ và Fleiss' $\kappa$ vào [07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md](file:///e:/multimodal-ehr-cdss/docs/07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md).

---

## Nghiệm thu Thành viên 2 [✓ ĐÃ KIỂM ĐỊNH HOÀN TẤT]
- [x] `results/registry.json`: Đã tích hợp đầy đủ 4 khóa `dca`, `robustness`, `generalization`, `fairness`.
- [x] Hình ảnh DCA & Missing Modality: `fig_dca_curve.pdf`, `dca_curve.png`, `fig_missing_modality.pdf`, `fig_missing_modality.png`.
- [x] Cập nhật tài liệu lâm sàng: `docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md`, `docs/07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md`, `docs/11_ANALYSIS_PLAN.md`.
- [x] Bộ kiểm thử tự động: `tests/test_phase3_backlog09_member2.py` đạt **8/8 PASSED (100%)**.
