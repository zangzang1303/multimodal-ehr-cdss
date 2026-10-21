# BACKLOG 03 (TUẦN 3): PATIENT SPLIT, BENCHMARK 3 BASELINES & ĐỀ XUẤT PHƯƠNG ÁN TỐI ƯU
### Giai Đoạn 1 | Mục Tiêu: Nghiệm Thu Benchmark Đối Chứng, Phân Tích Sai Số & Soạn Thảo Đề Xuất Tối Ưu

---

## 1. MỤC TIÊU CỐT LÕI CỦA TUẦN 3 (MỐC CHUYỂN GIAO GIAI ĐOẠN 1)
Tuần 3 là tuần về đích của Giai đoạn 1. Mục tiêu tối hậu là đưa ra bằng chứng thực nghiệm khách quan về hiệu năng và giới hạn của 3 hướng tiếp cận đơn phương thức (Unimodal), từ đó hoàn thiện Báo Cáo Đề Xuất Phương Án Tối Ưu để mở khóa Giai đoạn 2:
1. **Phân chia dữ liệu cấp độ bệnh nhân (Patient-Level Group Split):** Sử dụng `StratifiedGroupKFold` chia tập dữ liệu 70% Train, 15% Val, 15% Test theo `patient_id`. Xuất ra 3 tệp dữ liệu sạch tại `data/processed/`.
2. **Huấn luyện hoàn tất 3 Baselines:**
   - *Baseline 1 (Classical Tabular):* Huấn luyện XGBoost / CatBoost trên dữ liệu bảng.
   - *Baseline 2 (Tabular Deep Learning):* Huấn luyện FT-Transformer / MLP trên dữ liệu bảng.
   - *Baseline 3 (Clinical NLP):* Huấn luyện Bio_ClinicalBERT trên văn bản ghi chú lâm sàng.
3. **Đánh giá Benchmark Đa Chiều:** Đo đạc trên tập Hold-out Test độc lập và lưu kết quả vào `data/baseline_results.json` gồm đầy đủ các chỉ số: Macro AUROC, Macro AUPRC, Macro F1, Brier Score, và ECE.
4. **Phân Tích Sai Số Lâm Sàng (Error Analysis):** Lập ma trận nhầm lẫn (Confusion Matrix) và phân tích các ca bệnh dự đoán sai:
   - Các ca bệnh mà mô hình Bảng số đoán sai nhưng mô hình Văn bản đoán đúng.
   - Các ca bệnh mà mô hình Văn bản đoán sai nhưng mô hình Bảng số đoán đúng.
5. **Soạn Thảo Báo Cáo Đề Xuất Phương Án Tối Ưu (Proposed Optimal Solution):**
   - Đúc kết khoảng trống thực nghiệm của 3 baselines.
   - Luận chứng chi tiết kiến trúc đề xuất cho Giai đoạn 2: **Multimodal Cross-Attention Late Fusion** kết hợp **Temperature Scaling** ($ECE < 0.05$) và **Agentic RAG & Evidence Grounding** triệt tiêu ảo giác.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã nghiệm thu hoàn tất Backlog 02 (Tuần 2).**
- Toàn bộ pipeline khử định danh, khóa chuỗi thời gian và MICE imputer đã vượt qua 100% test cases.
- Khung mã nguồn 3 Baselines trong `src/models/baselines.py` đã sẵn sàng nhận dữ liệu.
- Đã đọc tài liệu: [`docs/01_RESEARCH_BACKGROUND_AND_GAP.md`](../../docs/01_RESEARCH_BACKGROUND_AND_GAP.md), [`docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md`](../../docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md) và đặc tả chi tiết code/kết quả tại [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG TUẦN 3

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách chạy huấn luyện tự động 3 Baselines qua `scripts/run_baselines.py`, tối ưu siêu tham số, xuất file điểm chuẩn `data/baseline_results.json`, vẽ biểu đồ `data/baseline_curves.png` và soạn thảo phần luận cứ toán học cho Đề xuất Tối ưu. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách thực hiện chia tập theo `patient_id` lưu vào `data/processed/`, hoàn thiện lớp `MultimodalEHRDataset`, xuất ma trận nhầm lẫn và chủ trì phân tích các ca bệnh sai biệt lâm sàng (Clinical Discrepancy Analysis). 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & System):** Phụ trách trang Dashboard so sánh Baselines trên Next.js (`frontend/src/app/baselines/page.tsx`), viết test benchmark tự động và chủ trì tổng hợp tệp báo cáo hoàn chỉnh **`docs/PROPOSED_OPTIMAL_SOLUTION.md`** nghiệm thu Giai đoạn 1. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ KẾT THÚC GIAI ĐOẠN 1 (DEFINITION OF DONE)
Backlog 03 (Tuần 3) và GIAI ĐOẠN 1 chỉ được xem là hoàn thành khi:
- [x] Tồn tại 3 tệp dữ liệu sạch: `data/processed/train.parquet`, `data/processed/val.parquet`, `data/processed/test.parquet` với 100% không có rò rỉ bệnh nhân giữa các tập.
- [x] Chạy thành công lệnh `python scripts/run_baselines.py` xuất ra tệp `data/baseline_results.json` ghi nhận đầy đủ AUROC, AUPRC, Macro-F1, Brier Score của cả 3 Baselines.
- [x] Tệp `data/baseline_curves.png` hiển thị đồ thị so sánh ROC, PR-Curve và Calibration Reliability Diagram của 3 mô hình.
- [x] Tệp tài liệu `docs/PROPOSED_OPTIMAL_SOLUTION.md` được hoàn thiện đầy đủ, phân tích rõ điểm mù của 3 baselines và đề xuất kiến trúc Multimodal Fusion + RAG rõ ràng từng công thức toán và module.
- [x] Trang `/baselines` trên giao diện web hiển thị bảng so sánh đối chứng trực quan cho bác sĩ.
