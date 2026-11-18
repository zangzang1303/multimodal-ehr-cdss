# BACKLOG 09 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

## Nhiệm vụ 2.1 [CORE] – DCA làm đúng chuẩn (RQ4b)
- **Định nghĩa trước** (ghi vào `docs/11_ANALYSIS_PLAN.md`):
  - Bệnh đích: HEART_FAILURE (one-vs-rest).
  - Hành động giả định: chỉ định NT-proBNP / siêu âm tim sớm.
  - Dải ngưỡng có lý do: p_t ∈ [0,05; 0,30] (chi phí xét nghiệm thấp so với bỏ sót).
- Đường cong cho: cross-attention, CatBoost, BERT, ensemble, treat-all, treat-none; dải CI bootstrap.
- Báo cáo thêm ΔNB và "số can thiệp thừa tránh được / 100 bệnh nhân" tại 0,10 và 0,20.
- Lưu ý trong chú thích: tỷ lệ HF trong test = 35% (106/302), cao hơn thực tế chăm sóc ban đầu ⇒ net benefit không ngoại suy được.

## Nhiệm vụ 2.2 [CORE] – Độ bền khi thiếu phương thức & nhiễu
- **Missing modality khi suy luận:** (a) bỏ văn bản (chuỗi rỗng), (b) bỏ toàn bộ bảng (giá trị trung vị train), (c) thiếu ngẫu nhiên 10/30/50% biến bảng.
- So sánh fusion vs từng mô hình đơn phương thức; hình `fig_missing_modality.pdf`.
- Đây là luận điểm thực tế mạnh nhất cho fusion (bệnh án thực thường thiếu) – trình bày rõ trong slide.

## Nhiệm vụ 2.3 [CORE] – Kiểm tra tổng quát hoá nội bộ
- Leave-group-out: nhóm theo `source_note_group`/chuyên khoa MTSamples hoặc theo khoảng thời gian `encounter_timestamp` (temporal split: train cũ → test mới).
- Báo cáo ΔAUROC so với strict split. **Ghi rõ: kiểm tra độ bền nội bộ, không phải ngoại kiểm.**

## Nhiệm vụ 2.4 [CORE] – Fairness & error analysis trên mô hình đúng
- Phân nhóm: giới (M/F), tuổi (< 65 / ≥ 65), hút thuốc; mỗi nhóm có N, AUROC, F1 + CI bootstrap.
- Error analysis: 3 cặp nhầm lẫn nhiều nhất (dự kiến ASTHMA↔COPD, HF↔PNEUMONIA); đọc 10 ca mỗi cặp, phân loại nguyên nhân (giá trị sinh hiệu chồng lấn / văn bản nhiễu / nhãn tổng hợp mâu thuẫn).
- Cập nhật lại 2 case study PT-0044, PT-0254 bằng **dự đoán thật** của checkpoint mới (nếu ca đó còn trong test).

## Nhiệm vụ 2.5 [OPTIONAL] – Kênh dữ liệu thực / ngoại kiểm
- Bắt đầu ngay thủ tục PhysioNet (CITI "Data or Specimens Only Research") để xin MIMIC-IV / MIMIC-IV-Note. Nếu được cấp trước hạn: chạy pipeline trên một tập con nhỏ, cùng 4 nhãn (ICD-10 J45, J44, I50, J18) làm ngoại kiểm sơ bộ.
- Nếu không kịp: ghi trong paper là bước tiếp theo, kèm kế hoạch cụ thể.
- Khảo sát bác sĩ (`docs/07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md`): chỉ thực hiện nếu có ≥ 2 bác sĩ đồng ý; báo cáo số người, số ca, Likert, độ đồng thuận (Krippendorff α). Nếu không: ghi "chưa thực hiện".

**Nghiệm thu Thành viên 2:** registry có mục `dca`, `robustness`, `generalization`, `fairness`; hình DCA/missing-modality; error analysis cập nhật trong `docs/06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md`.
