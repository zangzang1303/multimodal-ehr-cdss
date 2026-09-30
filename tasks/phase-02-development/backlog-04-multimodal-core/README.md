# BACKLOG 02: MULTIMODAL CORE, CROSS-ATTENTION & HIỆU CHUẨN XÁC SUẤT
### Giai Đoạn 2 (Tuần 4 – Tuần 7) | Mục Tiêu: Xây Dựng Mạng Học Sâu Đa Phương Thức & Đưa ECE < 0.05

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 02
Hợp nhất hai luồng dữ liệu (bảng số và văn bản ghi chú) qua cơ chế chú ý liên phương thức và kiểm soát độ tin cậy xác suất:
1. **Nhánh Bảng:** Xây dựng `TabularTokenizer` & `FTTransformerEncoder` ánh xạ các chỉ số liên tục và phân loại vào không gian chiều $D = 128$.
2. **Nhánh Văn Bản:** Xây dựng `ClinicalTextEncoder` (BioLinkBERT / ClinicalBERT) kết hợp ma trận chiếu tuyến tính $W_{proj}$.
3. **Mạng Cross-Attention Late Fusion:** Sử dụng $H_{tab}$ làm Query truy vấn $H_{text}$ (Key, Value) kết hợp Cổng Gated Residual Fusion thích ứng.
4. **Hiệu chuẩn xác suất lâm sàng:** Triển khai **Temperature Scaling** tối ưu NLL trên Validation Set, đưa chỉ số **$ECE < 0.05$**.
5. **Nghiên cứu triệt tiêu (Ablation Study):** Chạy thực nghiệm đối chứng 4 cấu hình (Tabular vs Text vs Concat vs Cross-Attention), lưu checkpoint tốt nhất vào `data/checkpoints/multimodal_best.pt`.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã hoàn thành nghiệm thu 100% Backlog 01.**
- Các tệp dữ liệu sạch `data/processed/train.parquet`, `val.parquet`, `test.parquet` đã sẵn sàng.
- Đã đọc kỹ tài liệu toán học: [`docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md`](../../docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 02

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách hiện thực FT-Transformer (`tabular_encoder.py`), Cross-Attention (`multimodal_fusion.py`), Temperature Scaling (`calibration.py`), và chạy Ablation Study. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách Clinical Text Encoder (`text_encoder.py`), vòng lặp huấn luyện `scripts/train_multimodal.py`, đo ECE và vẽ `data/calibration_curve.png`, kiểm tra công bằng phân nhóm (Fairness check). 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách Mock API `/predict`, UI Component `DiagnosticCard.tsx`, bộ Unit Tests `tests/test_multimodal_model.py` và trang `/evaluation` trên Next.js. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 03 (DEFINITION OF DONE)
Backlog 02 chỉ được xem là hoàn thành khi:
- [ ] Chạy `pytest tests/test_multimodal_model.py -v` vượt qua 100% test cases (tensor shapes, gradients, loss).
- [ ] Huấn luyện thành công mô hình bằng lệnh `python scripts/train_multimodal.py --calibrate` và lưu checkpoint tại `data/checkpoints/multimodal_best.pt`.
- [ ] Đạt chỉ số độ tin cậy xác suất kỳ vọng: **$ECE < 0.05$** trên tập test, xuất ra biểu đồ `data/calibration_curve.png`.
- [ ] Hoàn tất bảng so sánh Ablation Study trong `data/ablation_results.json` chứng minh mô hình Multimodal vượt trội hơn ít nhất $0.04$ AUROC so với Tabular Baseline.
- [ ] Component `DiagnosticCard.tsx` hiển thị đúng thanh đo rủi ro và nhãn *"Calibrated Confidence"*.
