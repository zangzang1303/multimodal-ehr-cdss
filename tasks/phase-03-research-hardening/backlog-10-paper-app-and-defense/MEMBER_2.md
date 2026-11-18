# BACKLOG 10 – THÀNH VIÊN 2 (Biomedical Data Engineer & Privacy)

## Nhiệm vụ 2.1 – Data & Cohort, Ethics
- `02_clinical_cohort.tex`: mô tả **trung thực** cách tạo dữ liệu: bảng từ Synthea, ghi chú từ MTSamples ghép với bệnh nhân tổng hợp, khối sinh hiệu được chèn vào ghi chú (nguồn gốc của phát hiện RQ2), PHI giả lập để kiểm thử de-ID.
- Flow diagram TRIPOD (nguồn → loại trừ → 2.000 hồ sơ → train/val/test 1425/273/302) dạng TikZ/SVG.
- Bảng 1 – đặc điểm đoàn hệ theo split và theo lớp (tuổi, giới, sinh hiệu trung vị [IQR], tỷ lệ thiếu).
- `08_discussion_ethics.tex`: kết quả audit PHI trước/sau, giấy phép dữ liệu/phác đồ/mô hình, tuyên bố không dùng lâm sàng.

## Nhiệm vụ 2.2 – TRIPOD+AI & PROBAST+AI
- Phụ lục `appendix_tripod_ai.tex`: 27 mục TRIPOD+AI, cột "Mục/trang" và "Ghi chú" (đánh dấu N/A có lý do, ví dụ ngoại kiểm chưa làm).
- Phụ lục PROBAST+AI: lấy bản đã chấm lại ở Backlog 08 + cập nhật miền Analysis theo kết quả Backlog 09.

## Nhiệm vụ 2.3 – Tài liệu tham khảo (12 → ≥ 35)
Nhóm bắt buộc có: TRIPOD+AI (Collins 2024), PROBAST+AI (Moons 2025), tổng quan JMIR đang trích, FT-Transformer, ClinicalBERT, BERT, Cross-attention / multimodal EHR fusion (ví dụ các khảo sát multimodal medical AI), Temperature scaling (Guo 2017), DCA (Vickers & Elkin 2006), Synthea, MTSamples, RAG (Lewis 2020), shortcut learning (Geirhos 2020), leakage trong ML (Kapoor & Narayanan 2023), MIMIC-IV, GINA/GOLD/ESC/BYT.
- **Mỗi mục phải kiểm tra tồn tại** (DOI/URL). Không trích tài liệu chưa đọc tóm tắt.
- Một người kiểm tra chéo toàn bộ `references.bib`.

## Nhiệm vụ 2.4 – Q&A phần dữ liệu & đạo đức
Câu trả lời ngắn cho: dữ liệu có thật không? vì sao không dùng dữ liệu bệnh viện VN? de-ID đánh giá thế nào? fairness có ý nghĩa gì trên dữ liệu tổng hợp? kế hoạch ngoại kiểm & xin phép đạo đức (IRB) ra sao?
