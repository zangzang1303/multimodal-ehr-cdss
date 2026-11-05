# BACKLOG 06: ĐÁNH GIÁ MÔ HÌNH, DCA & KIỂM TRA TÍNH TỔNG QUÁT
### Giai đoạn 2 (Tuần 11–13) | Mục tiêu: đo hiệu năng và giới hạn trên dữ liệu nghiên cứu

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 06
Đánh giá minh bạch theo [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) và xem xét nguy cơ sai lệch bằng [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505):
1. **Đo đạc năng lực phân biệt đa chiều:** Tính toán Multiclass AUROC (One-vs-Rest Macro), AUPRC Macro, Macro-F1, Brier Score trên tập Test độc lập.
2. **Phân tích Đường cong Quyết định (DCA):** Định nghĩa trước một bệnh đích theo one-vs-rest, hành động tương ứng, quần thể và dải ngưỡng có ý nghĩa; báo cáo net benefit so với treat-all/treat-none. Trên dữ liệu tổng hợp, đây là phân tích minh họa, không chứng minh lợi ích lâm sàng thực tế.
3. **Phân tích ca bệnh sai biệt (Error Analysis):** Xuất ma trận nhầm lẫn (Confusion Matrix) và mổ xẻ các ca bệnh giáp ranh phức tạp.
4. **Khảo sát định tính:** Soạn giao thức blind-review và phiếu khảo sát; chỉ báo cáo là khảo sát bác sĩ nếu đã tuyển được người tham gia và xác minh nguồn ca bệnh, quyền sử dụng dữ liệu.
5. **Kiểm tra tính tổng quát hóa:** Ưu tiên nguồn ngoại kiểm độc lập được phép sử dụng. Nếu chưa có, chạy leave-source-out hoặc temporal split và ghi rõ đó là kiểm tra độ bền nội bộ, không gọi là ngoại kiểm.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- Đã nghiệm thu Backlog 05 và khóa checkpoint, preprocessing, nhiệt độ hiệu chuẩn trước đánh giá tổng hợp; không tiếp tục chọn mô hình theo kết quả strict test đã xem ở Backlog 04.
- Hệ thống Web App Full-stack và API đã hoạt động trơn tru.
- Đọc [hướng dẫn đánh giá](../../../docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md); lập trước kế hoạch CI bootstrap theo nhóm nguồn/bệnh nhân và định nghĩa DCA. Xác định nguồn dữ liệu, quyền sử dụng và nhân sự cho các hoạt động khảo sát/ngoại kiểm trước khi đưa vào lịch bắt buộc.

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 06

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách tính toán các chỉ số định lượng `metrics.py`, hiện thực module `dca_analysis.py`, vẽ biểu đồ Net Benefit và chạy kiểm định ngoại kiểm. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách xuất Confusion Matrix, thực hiện Error Analysis, viết script tự động hóa `evaluate_clinical_utility.py` và tổ chức khảo sát chuyên gia y tế. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách route `GET /evaluation/benchmark`, bộ kiểm thử tự động `tests/test_api_endpoints.py`, trực quan hóa đồ thị DCA trên Web và tối ưu UX Mobile/Tablet. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 07 (DEFINITION OF DONE)
Backlog 06 hoàn thành khi:
- [ ] Test API mới cho `/predict/multimodal`, `/agent/explain`, `/evaluation/benchmark` chạy qua; test hiện có của Phase 1 không thay thế được các ca này.
- [ ] Báo cáo AUROC/AUPRC/F1/ECE/Brier của cả bốn mô hình trên cùng strict test, kèm CI 95% và chênh lệch so với từng baseline. Ghi nhận cả kết quả thấp hơn baseline; không tuyên bố mức tăng chưa quan sát được.
- [ ] `data/dca_curve.png` ghi rõ bệnh đích, hành động giả định, dải ngưỡng có lý do, số ca và so sánh treat-all/treat-none; diễn giải giới hạn của dữ liệu tổng hợp.
- [ ] Hoàn thành giao thức và phiếu khảo sát. Nếu có bác sĩ/ca bệnh đủ điều kiện, báo cáo số người, số ca, cách chọn và kết quả; nếu không, ghi rõ chưa thực hiện, không thay bằng nhận xét giả định.
- [ ] Báo cáo kiểm tra tính tổng quát hóa với nguồn độc lập nếu có; nếu chưa có, báo cáo leave-source-out/temporal split và ghi ngoại kiểm còn là việc chưa hoàn thành trước tuyên bố triển khai lâm sàng.
