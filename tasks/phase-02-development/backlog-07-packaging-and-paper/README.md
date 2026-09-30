# BACKLOG 05: ĐÓNG GÓI DOCKER, BÁO CÁO TRIPOD-AI & NGHIỆM THU
### Giai Đoạn 5 (Tuần 14 – Tuần 16) | Mục Tiêu: Sản Phẩm Hoàn Chỉnh Một Lệnh Chạy, Bài Báo Khoa Học & Video Demo

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 05
Đóng gói toàn diện hệ sinh thái thành sản phẩm sẵn sàng triển khai thực tế và hoàn tất hồ sơ công bố khoa học quốc tế:
1. **Đóng gói Docker Compose trọn gói:** Kết nối 3 dịch vụ (`frontend:3000`, `api:8000`, `qdrant:6333`) chạy chỉ bằng 1 lệnh duy nhất: `docker compose up --build`.
2. **Bản thảo Bài báo Khoa học chuẩn TRIPOD-AI:** Hoàn thành đầy đủ các phần: Tổng quan (Background), Phương pháp (Methods), Kết quả thực nghiệm (Results), Thảo luận (Discussion).
3. **Bảng Thẩm Định 20 Tiêu Chí PROBAST:** Báo cáo chi tiết chứng minh hệ thống đạt chuẩn Low Risk of Bias trên cả 4 miền (*Participants, Predictors, Outcome, Analysis*).
4. **Sản xuất Video Demo lâm sàng:** Thời lượng 3 - 5 phút trình bày bài toán y tế, khoảng trống JMIR, thao tác nhập liệu thực tế và tính năng giải trình không ảo giác.
5. **Công bố mã nguồn mở (Open-Source Release):** Gắn release tag `v1.0.0` trên GitHub, đính kèm trọng số mô hình và giấy phép bản quyền MIT License.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã hoàn thành nghiệm thu 100% Backlog 04.**
- Toàn bộ kết quả thực nghiệm AUROC, AUPRC, DCA Net Benefit và khảo sát bác sĩ đã có số liệu chính xác.
- Đã đọc kỹ tài liệu: [`docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md`](../../docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md) và [`README.md`](../../README.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 05

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách tối ưu hóa GPU runtime trong `Dockerfile`, viết phần *Methodology* & *Results* của Paper, gắn release tag `v1.0.0` và công bố weights. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách snapshot dữ liệu phác đồ Qdrant offline, viết phần *Clinical Cohort* của Paper, hoàn thiện Bảng kiểm toán 20 tiêu chí PROBAST và rà soát an ninh không lộ PHI. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách hoàn thiện `docker-compose.yml`, viết phần *Software Architecture* của Paper, vẽ sơ đồ vector độ nét cao, quay video demo lâm sàng và slide báo cáo nghiệm thu. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU CUỐI CÙNG CỦA DỰ ÁN (PROJECT FINAL ACCEPTANCE)
Dự án được nghiệm thu toàn diện khi:
- [ ] Chạy lệnh `docker compose up --build -d` trên máy tính mới khởi động thành công toàn bộ stack mà không cần thao tác thêm.
- [ ] Lệnh `pytest tests/` vượt qua 100% test cases trên toàn repository.
- [ ] Bản thảo bài báo khoa học chuẩn cấu trúc TRIPOD-AI hoàn tất, Bảng checklist 20 tiêu chí PROBAST đạt đánh giá Low Risk of Bias.
- [ ] Video Demo lâm sàng (3 - 5 phút) có âm thanh thuyết minh và hình ảnh sắc nét.
- [ ] Repository sạch sẽ, không có file rác, file `.env` mẫu đầy đủ, giấy phép MIT License hợp lệ.
