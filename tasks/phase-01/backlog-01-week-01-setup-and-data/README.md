# BACKLOG 01 (TUẦN 1): THIẾT LẬP MÔI TRƯỜNG, DATA CONTRACT & DỮ LIỆU THÔ
### Giai Đoạn 1 | Mục Tiêu: Khởi Tạo Nền Móng Kỹ Thuật, Hợp Đồng Dữ Liệu & Thu Thập Dữ Liệu Thô

---

## 1. MỤC TIÊU CỐT LÕI CỦA TUẦN 1
Thiết lập toàn bộ hạ tầng cơ bản, các tệp cấu hình tham số, quy chuẩn mã nguồn và bộ dữ liệu thô ban đầu để cả 3 thành viên có thể làm việc song song mà không bị xung đột:
1. **Môi trường & Hạ tầng AI:** Chuẩn hóa môi trường Python 3.10+, PyTorch 2.2+ với hỗ trợ tăng tốc CUDA GPU, khóa phiên bản thư viện trong `requirements.txt`.
2. **Cấu hình Siêu tham số:** Khởi tạo `configs/model_config.yaml` quy định kiến trúc và siêu tham số cho 3 Baseline (XGBoost, FT-Transformer, Bio_ClinicalBERT).
3. **Hợp đồng Dữ liệu (Data Contract):** Thống nhất `configs/data_schema.yaml` gồm 9 biến số sinh hiệu/xét nghiệm liên tục, 4 biến phân loại nhân khẩu/tiền sử và 4 nhãn bệnh lý (Hen, COPD, Suy tim, Viêm phổi).
4. **Bộ dữ liệu thô (Raw Data):** Thu thập hoặc sinh tập dữ liệu bán tổng hợp (Semi-synthetic EHR) gồm ít nhất 2.000 ca bệnh có đủ cả thông tin bảng số và ghi chú lâm sàng tự do.
5. **Khung Ứng Dụng Nền Tảng:** Khởi tạo Backend FastAPI với endpoint `GET /health` và giao diện Next.js 14 khởi động thành công trên cổng 3000.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- Đã cài đặt Git, Python 3.10+ và Node.js 18+ trên máy phát triển.
- Máy tính có GPU NVIDIA hoặc đã cấu hình môi trường CUDA phù hợp.
- Đã đọc tài liệu: [`docs/01_RESEARCH_BACKGROUND_AND_GAP.md`](../../docs/01_RESEARCH_BACKGROUND_AND_GAP.md), [`DEVELOPMENT_SPEC_MULTIMODAL_EHR_AI.md`](../../DEVELOPMENT_SPEC_MULTIMODAL_EHR_AI.md) và đặc tả chi tiết code/kết quả tại [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG TUẦN 1

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách kiểm tra CUDA, hoàn thiện `requirements.txt`, soạn thảo `configs/model_config.yaml`, và nghiên cứu mã nguồn tham chiếu FT-Transformer / ClinicalBERT Tokenizer. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách hợp đồng dữ liệu `configs/data_schema.yaml`, xây dựng script sinh dữ liệu bán tổng hợp lâm sàng và lưu trữ an toàn tại `data/raw/`. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & System):** Phụ trách cấu hình quy chuẩn code format, khởi tạo khung FastAPI `GET /health`, khởi tạo Next.js 14 trên cổng 3000 và viết Pydantic schemas ban đầu. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG TUẦN 2 (DEFINITION OF DONE)
Backlog 01 (Tuần 1) chỉ được xem là hoàn thành khi:
- [ ] Chạy `python scripts/verify_env.py` trả về `CUDA Available: True`, hiển thị đúng tên GPU và phiên bản PyTorch.
- [ ] Tệp `configs/data_schema.yaml` và `configs/model_config.yaml` đã được tạo đầy đủ, đúng cú pháp YAML và được cả 3 thành viên thống nhất.
- [x] Tệp dữ liệu thô `data/raw/patients_raw.parquet` và `data/raw/clinical_notes_raw.jsonl` tồn tại cục bộ, có ít nhất 2.000 ca bệnh và không bị commit lên Git (đã thêm vào `.gitignore`).
- [ ] Backend FastAPI khởi động thành công (`uvicorn src.api.main:app --reload`), truy cập `http://localhost:8000/health` trả về mã 200 `{"status": "healthy"}`.
- [ ] Frontend Next.js khởi động thành công (`npm run dev`), truy cập `http://localhost:3000` hiển thị màn hình khởi động không có lỗi runtime.
