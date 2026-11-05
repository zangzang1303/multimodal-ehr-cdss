# BACKLOG 07: ĐÓNG GÓI DOCKER, BÁO CÁO TRIPOD+AI & NGHIỆM THU
### Giai đoạn 2 (Tuần 14–16) | Mục tiêu: bản chạy tái lập được, bản thảo nghiên cứu và demo

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 07
Đóng gói bản nghiên cứu có thể tái lập và báo cáo trung thực phạm vi đánh giá:
1. **Đóng gói Docker Compose trọn gói:** Kết nối 3 dịch vụ (`frontend:3000`, `api:8000`, `qdrant:6333`) chạy chỉ bằng 1 lệnh duy nhất: `docker compose up --build`.
2. **Bản thảo theo [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378):** Hoàn thành Background, Methods, Results, Discussion, giới hạn, khả năng tái lập và checklist báo cáo; đây là hướng dẫn báo cáo, không phải chứng nhận hiệu quả.
3. **Đánh giá nguy cơ sai lệch bằng [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505):** Ghi nhận từng miền và lý do đánh giá, kể cả nguy cơ cao hoặc chưa rõ; không đặt “Low Risk of Bias” làm kết quả phải đạt.
4. **Video demo nghiên cứu:** Thời lượng 3–5 phút trình bày bài toán, thao tác trên ca tổng hợp, xác suất đã hiệu chuẩn và cách kiểm tra trích dẫn; nêu rõ giới hạn của bằng chứng và dữ liệu.
5. **Chuẩn bị phát hành:** Rà quyền sử dụng mã nguồn, phác đồ, dữ liệu, weights và phụ thuộc; chuẩn bị release notes và tag sau khi nghiệm thu. Chỉ công bố lên GitHub khi nhóm đã chấp thuận phạm vi phát hành.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- Đã nghiệm thu Backlog 06 ở phạm vi đánh giá nghiên cứu; kết quả chưa thực hiện (ví dụ ngoại kiểm hoặc khảo sát chuyên gia) được ghi rõ và không điền số liệu thay thế.
- Các artifact đánh giá có phiên bản, split, seed và đường dẫn truy xuất; đã xác định nguồn cung cấp checkpoint, Qdrant snapshot, tài liệu phác đồ và biến môi trường cho bản chạy sạch.
- Đọc [hướng dẫn đánh giá](../../../docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md) và [README dự án](../../../README.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 07

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách checkpoint/runtime, viết Methods & Results, chuẩn bị release notes và kiểm tra điều kiện công bố weights. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách snapshot phác đồ có quyền sử dụng, viết Cohort, đánh giá PROBAST+AI và rà soát PHI/giấy phép. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách hoàn thiện `docker-compose.yml`, viết phần *Software Architecture* của Paper, vẽ sơ đồ vector độ nét cao, quay video demo lâm sàng và slide báo cáo nghiệm thu. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU CUỐI CÙNG CỦA DỰ ÁN (PROJECT FINAL ACCEPTANCE)
Dự án được nghiệm thu toàn diện khi:
- [ ] Trên môi trường sạch có Docker và các artifact được cung cấp theo hướng dẫn, `docker compose up --build -d` chạy ba dịch vụ healthy; có `.env.example`, hướng dẫn lấy checkpoint/snapshot hợp lệ và smoke test API/UI.
- [ ] Lệnh `pytest tests/` vượt qua 100% test cases trên toàn repository.
- [ ] Bản thảo và checklist TRIPOD+AI hoàn tất; bảng PROBAST+AI nêu rõ nguy cơ sai lệch, tính áp dụng và bằng chứng cho từng nhận định. Kết luận chỉ giới hạn ở dữ liệu và đánh giá đã thực hiện.
- [ ] Video Demo lâm sàng (3 - 5 phút) có âm thanh thuyết minh và hình ảnh sắc nét.
- [ ] Repository không chứa dữ liệu nhạy cảm/secret; `.env.example`, tài liệu cấp phép và nguồn gốc artifact đầy đủ. Tag/release công khai là bước riêng sau rà soát quyền và chấp thuận của nhóm.
