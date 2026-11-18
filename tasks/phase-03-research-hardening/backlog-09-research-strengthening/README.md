# BACKLOG 09: NÂNG TẦM NGHIÊN CỨU – SO SÁNH CÔNG BẰNG, PHÂN RÃ TÍN HIỆU & ĐỘ BỀN
### Giai đoạn 3 – Tuần 2 | Mục tiêu: trả lời RQ1–RQ5 bằng bằng chứng có khoảng tin cậy

---

## 1. CÂU HỎI NGHIÊN CỨU
| RQ | Câu hỏi | Thí nghiệm | Phụ trách |
| :---: | :--- | :--- | :---: |
| RQ1 | Dưới so sánh công bằng, cross-attention có vượt mô hình đơn phương thức tốt nhất & cách dung hợp đơn giản? | Ma trận so sánh đa seed + paired bootstrap CI | M1 |
| RQ2 | Tín hiệu nhánh văn bản đến từ đâu? | Phân rã: gốc / che số / bỏ khối sinh hiệu / chỉ tự sự | M1 |
| RQ3 | Khi nào fusion có ích? | Mô phỏng bổ trợ có kiểm soát (ρ, σ) | M1 *(optional)* |
| RQ4 | Hiệu chuẩn, lợi ích ròng, độ bền khi thiếu phương thức? | Calibration, DCA, missing-modality, leave-group-out | M1 + M2 |
| RQ5 | Giải trình có neo bằng chứng & truy xuất đúng phác đồ? | Retrieval Recall@k/MRR, grounding precision, (LLM mode) | M3 |

**Bằng chứng sơ bộ cho RQ2 (rà soát 2026-11-18):** TF-IDF+LR đạt AUROC 0,922 trên văn bản gốc nhưng chỉ **0,553** khi che toàn bộ con số; LR chỉ trên 9 biến bảng đạt 0,920. ⇒ nhánh text chủ yếu đọc lại sinh hiệu nhúng trong ghi chú.

## 2. ĐIỀU KIỆN TIÊN QUYẾT
- Backlog 08 nghiệm thu: dữ liệu có manifest, checkpoint đúng, `data/predictions/*.npz` đầy đủ, registry hoạt động.
- **Đăng ký trước (pre-registration nội bộ):** trước khi chạy, ghi vào `docs/11_ANALYSIS_PLAN.md`: metric chính (macro AUROC), metric phụ, mô hình so sánh, số seed, số vòng bootstrap, bệnh đích & dải ngưỡng DCA. Không đổi sau khi thấy kết quả test.

## 3. PHÂN CÔNG
* 🧬 **Thành viên 1:** RQ1, RQ2, RQ3, hiệu chuẩn (RQ4a). 👉 [MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2:** DCA, missing-modality, leave-group-out, fairness, error analysis, kênh ngoại kiểm. 👉 [MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3:** đánh giá RAG/grounding, KB phác đồ, LLM mode (optional), latency. 👉 [MEMBER_3.md](MEMBER_3.md)

Nhãn **[CORE]** = bắt buộc để bảo vệ; **[OPTIONAL]** = làm nếu còn thời gian, nếu không chuyển vào "Hướng phát triển".

## 4. DEFINITION OF DONE
- [ ] `docs/11_ANALYSIS_PLAN.md` được commit **trước** commit kết quả đầu tiên của tuần.
- [ ] Bảng chính: ≥ 8 mô hình × ≥ 3 seed, mean ± SD, CI 95% paired bootstrap (theo bệnh nhân) cho ΔAUROC so với từng baseline, có hiệu chỉnh Holm.
- [ ] Bảng/biểu đồ phân rã tín hiệu văn bản (RQ2) cho TF-IDF, BERT và cross-attention.
- [ ] Hiệu chuẩn: temperature vs vector scaling vs isotonic (fit trên val), ECE + CI, classwise ECE.
- [ ] DCA một bệnh đích định nghĩa trước, có CI và các mô hình so sánh.
- [ ] Missing-modality & leave-group-out có kết quả, ghi rõ "kiểm tra độ bền nội bộ".
- [ ] RAG: Recall@k, MRR trên ≥ 60 truy vấn có nhãn; tỷ lệ claim được neo / bị từ chối; latency p50/p95.
- [ ] Toàn bộ kết quả vào `results/registry.json`; **đóng băng registry** cuối tuần (tag `results-freeze`).
