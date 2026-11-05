# BACKLOG 04: MULTIMODAL CORE, CROSS-ATTENTION & HIỆU CHUẨN XÁC SUẤT
### Giai đoạn 2 (Tuần 4–7) | Mục tiêu: huấn luyện và đánh giá mô hình đa phương thức trên strict split

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 04
Hợp nhất hai luồng dữ liệu (bảng số và văn bản ghi chú) qua cơ chế chú ý liên phương thức và kiểm soát độ tin cậy xác suất:
1. **Nhánh Bảng:** Xây dựng `TabularTokenizer` & `FTTransformerEncoder` ánh xạ các chỉ số liên tục và phân loại vào không gian chiều $D = 128$.
2. **Nhánh Văn Bản:** Xây dựng `ClinicalTextEncoder` (BioLinkBERT / ClinicalBERT) kết hợp ma trận chiếu tuyến tính $W_{proj}$.
3. **Mạng Cross-Attention Late Fusion:** Sử dụng $H_{tab}$ làm Query truy vấn $H_{text}$ (Key, Value) kết hợp Cổng Gated Residual Fusion thích ứng.
4. **Hiệu chuẩn xác suất:** Khớp Temperature Scaling trên validation; đánh giá ECE, Brier và reliability diagram một lần trên strict test. $ECE < 0.05$ là mục tiêu nghiên cứu, không phải điều kiện để sửa ngưỡng theo test.
5. **Ablation Study:** So sánh Tabular, Text, Concat và Cross-Attention trên cùng `data/processed_strict/`, cùng nhãn và quy trình đánh giá; lưu checkpoint được chọn theo validation vào `data/checkpoints/multimodal_best.pt`.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- Đã nghiệm thu Backlog 03 của Phase 1 và thống nhất [báo cáo benchmark strict](<../../../docs/Báo cáo CVĐ - số liệu thực.md>) là mốc khoa học hiện hành; `data/baseline_results.json` và `data/processed/` thuộc pipeline cũ.
- Có `data/processed_rebuilt_strict/{train,val,test}.parquet` (1425/273/302 mẫu); chạy lại `python scripts/audit_data_leakage.py --data-dir data/processed_rebuilt_strict --output data/rebuilt_strict_split_audit.json` và xác nhận `passed: true` trước huấn luyện.
- Đọc [kiến trúc và toán học](../../../docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md). Chốt nhãn, tokenizer, chiều chuỗi, feature schema và preprocessing theo train; không fit hoặc chọn mô hình trên test.

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 04

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách hiện thực FT-Transformer (`tabular_encoder.py`), Cross-Attention (`multimodal_fusion.py`), Temperature Scaling (`calibration.py`), và chạy Ablation Study. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách Clinical Text Encoder (`text_encoder.py`), vòng lặp huấn luyện `scripts/train_multimodal.py`, đo ECE và vẽ `data/calibration_curve.png`, kiểm tra công bằng phân nhóm (Fairness check). 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách Mock API `/predict`, UI Component `DiagnosticCard.tsx`, bộ Unit Tests `tests/test_multimodal_model.py` và trang `/evaluation` trên Next.js. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 05 (DEFINITION OF DONE)
Backlog 04 hoàn thành khi:
- [ ] Chạy `pytest tests/test_multimodal_model.py -v` vượt qua 100% test cases (tensor shapes, gradients, loss).
- [ ] `python scripts/train_multimodal.py --data-dir data/processed_rebuilt_strict --config configs/model_config.yaml --calibrate` lưu checkpoint, cấu hình, seed, scaler/tokenizer và nhiệt độ $T$ đã khớp trên validation.
- [ ] `data/calibration_curve.png` và báo cáo ECE/Brier trước–sau hiệu chuẩn trên strict test; ghi kết quả thực tế dù không đạt mục tiêu $ECE < 0.05$.
- [ ] `data/ablation_results.json` ghi đủ bốn cấu hình, cùng split, AUROC/AUPRC/F1/ECE/Brier và chênh lệch so với từng baseline strict. Báo cáo cả kết quả không cải thiện; không đặt mức tăng AUROC cố định làm điều kiện nghiệm thu.
- [ ] Component `DiagnosticCard.tsx` hiển thị đúng thanh đo rủi ro và nhãn *"Calibrated Confidence"*.
