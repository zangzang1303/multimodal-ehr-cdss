# BACKLOG 04: KIỂM ĐỊNH LÂM SÀNG, LỢI ÍCH RÒNG DCA & NGOẠI KIỂM
### Giai Đoạn 4 (Tuần 11 – Tuần 13) | Mục Tiêu: Đo Đạc Đa Chiều, Chứng Minh Giá Trị Lâm Sàng Thực Tế & Thẩm Định Chuyên Gia

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 04
Thực hiện đánh giá khoa học toàn diện theo các tiêu chuẩn thẩm định y tế quốc tế cao nhất (*TRIPOD-AI, PROBAST*):
1. **Đo đạc năng lực phân biệt đa chiều:** Tính toán Multiclass AUROC (One-vs-Rest Macro), AUPRC Macro, Macro-F1, Brier Score trên tập Test độc lập.
2. **Phân tích Đường cong Quyết định (DCA):** Lượng hóa **Lợi ích Ròng Lâm sàng (Clinical Net Benefit)**, chứng minh mô hình giúp bác sĩ tối đa hóa số ca can thiệp đúng mà không làm tăng can thiệp thừa.
3. **Phân tích ca bệnh sai biệt (Error Analysis):** Xuất ma trận nhầm lẫn (Confusion Matrix) và mổ xẻ các ca bệnh giáp ranh phức tạp.
4. **Khảo sát định tính với Bác sĩ lâm sàng:** Thực hiện blind-review với 2-3 chuyên gia y tế trên 20 ca bệnh thực tế.
5. **Kiểm định ngoại kiểm (External Validation):** Đánh giá tính tổng quát hóa trên một nguồn dữ liệu độc lập.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã hoàn thành nghiệm thu 100% Backlog 03.**
- Hệ thống Web App Full-stack và API đã hoạt động trơn tru.
- Đã đọc kỹ tài liệu: [`docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md`](../../docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 04

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách tính toán các chỉ số định lượng `metrics.py`, hiện thực module `dca_analysis.py`, vẽ biểu đồ Net Benefit và chạy kiểm định ngoại kiểm. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách xuất Confusion Matrix, thực hiện Error Analysis, viết script tự động hóa `evaluate_clinical_utility.py` và tổ chức khảo sát chuyên gia y tế. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách route `GET /evaluation/benchmark`, bộ kiểm thử tự động `tests/test_api_endpoints.py`, trực quan hóa đồ thị DCA trên Web và tối ưu UX Mobile/Tablet. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 05 (DEFINITION OF DONE)
Backlog 04 chỉ được xem là hoàn thành khi:
- [ ] Chạy `pytest tests/test_api_endpoints.py -v` vượt qua 100% test cases.
- [ ] Đạt các chỉ số định lượng cam kết:
  - $\text{AUROC (Macro OVR)} \ge 0.88$ (Vượt trội Baselines $\ge 0.04$).
  - $\text{AUPRC (Macro)} \ge 0.82$.
  - $\text{Macro-F1} \ge 0.84$.
- [ ] Biểu đồ DCA tại `data/dca_curve.png` chứng minh đường Net Benefit của M-CDSS nằm cao hơn cả "Treat All" và "Treat None" trên dải $p_t \in [0.10, 0.40]$.
- [ ] Hoàn thành báo cáo khảo sát ý kiến bác sĩ (Clinician Feedback Report) trên 20 ca bệnh.
- [ ] Có kết quả kiểm định ngoại kiểm độc lập chứng minh mô hình không bị quá khớp.
