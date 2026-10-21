# BACKLOG 03 (TUẦN 3) - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Huấn Luyện 3 Baselines, Đánh Giá Benchmark Đa Chiều & Luận Chứng Kiến Trúc Tối Ưu

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 3 của Giai đoạn 1, Thành viên 1 tiếp nhận 3 tập dữ liệu sạch từ Thành viên 2 để tiến hành huấn luyện, tinh chỉnh siêu tham số và đo đạc toàn diện hiệu năng của 3 Baselines đối chứng. Đồng thời, đóng góp nội dung kỹ thuật toán học sâu sắc vào Báo Cáo Đề Xuất Phương Án Tối Ưu để làm tiền đề cho Giai đoạn 2.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Hoàn Thiện Script & Huấn Luyện Tự Động 3 Baselines (`scripts/run_baselines.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Tiếp nhận 3 tệp Parquet sạch từ `data/processed/`: `train.parquet`, `val.parquet`, `test.parquet`.
  2. Hoàn thiện toàn bộ logic trong `scripts/run_baselines.py`:
     - **Huấn luyện Baseline 1 (Classical Tabular):** Huấn luyện XGBoost và CatBoost trên 9 biến số và 4 biến phân loại; chọn ra model tốt nhất dựa trên Validation Macro AUROC.
     - **Huấn luyện Baseline 2 (Tabular Deep Learning):** Huấn luyện FT-Transformer với AdamW, learning rate 1e-4, batch size 64 qua 20 epochs kèm Early Stopping (patience = 5).
     - **Huấn luyện Baseline 3 (Clinical NLP):** Fine-tune nhẹ lớp phân loại của `Bio_ClinicalBERT` trên văn bản ghi chú lâm sàng với learning rate 2e-5, max_length 512.
  3. Đánh giá độc lập cả 3 mô hình trên Hold-out Test Set và xuất ra tệp `data/baseline_results.json` với cấu trúc chuẩn:
     ```json
     {
       "baseline_1_classical_tabular": {
         "model_name": "XGBoost",
         "macro_auroc": 0.812,
         "macro_auprc": 0.745,
         "macro_f1": 0.738,
         "brier_score": 0.245,
         "ece": 0.089
       },
       "baseline_2_tabular_deep": {
         "model_name": "FT-Transformer",
         "macro_auroc": 0.835,
         "macro_auprc": 0.762,
         "macro_f1": 0.751,
         "brier_score": 0.228,
         "ece": 0.094
       },
       "baseline_3_text_only": {
         "model_name": "Bio_ClinicalBERT",
         "macro_auroc": 0.824,
         "macro_auprc": 0.758,
         "macro_f1": 0.742,
         "brier_score": 0.239,
         "ece": 0.112
       }
     }
     ```
* **Lệnh thực thi & kiểm thử:**
  ```bash
  python scripts/run_baselines.py --data_dir data/processed/ --output_file data/baseline_results.json
  ```
* **Đầu ra (Deliverables):**
  - `scripts/run_baselines.py`.
  - `data/baseline_results.json`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 1.2: Trực Quan Hóa Đồ Thị Đối Chiếu (`data/baseline_curves.png`)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  Viết script tạo đồ thị chất lượng cao so sánh 3 mô hình (lưu tại `data/baseline_curves.png`):
  1. **Subplot 1 (ROC Curves):** Đường cong ROC của 3 baselines và đường ngẫu nhiên (chance line).
  2. **Subplot 2 (Precision-Recall Curves):** Đường cong PR đối chiếu hiệu năng phân loại trên các lớp mất cân bằng.
  3. **Subplot 3 (Reliability Diagrams):** Đường cong độ tin cậy thể hiện rõ hiện tượng **Overconfidence** (sai lệch giữa độ tự tin dự đoán và độ chính xác thực tế - giải thích vì sao ECE của cả 3 baseline đều $> 0.08$).
* **Đầu ra (Deliverables):**
  - Tệp ảnh `data/baseline_curves.png`.
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 1.3: Soạn Thảo Cơ Sở Lý Thuyết & Luận Chứng Kiến Trúc Tối Ưu
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Soạn thảo phần Phân tích Kỹ thuật và Luận cứ Toán học để đóng góp vào tệp `docs/PROPOSED_OPTIMAL_SOLUTION.md`:
  1. **Luận giải vì sao cần Multimodal Late Fusion:** Chứng minh toán học rằng việc chỉ dùng bảng số (Baseline 1, 2) bỏ lỡ không gian ngữ nghĩa $H_{text}$, còn việc chỉ dùng văn bản (Baseline 3) mất đi độ nhạy lượng hóa của $SpO_2$ và xét nghiệm máu.
  2. **Đặc tả Cơ chế Cross-Attention:**
     - Thiết lập công thức: Dùng vector đặc trưng bảng số làm Query ($Q_{tab} = h_{tab} W_q$), chiếu lên biểu diễn ngữ cảnh của văn bản ($K_{text} = h_{text} W_k, V_{text} = h_{text} W_v$):
       $$\text{Attention}(Q_{tab}, K_{text}, V_{text}) = \text{softmax}\left(\frac{Q_{tab} K_{text}^T}{\sqrt{D}}\right) V_{text}$$
     - Cơ chế Cổng Gated Residual: $\mathbf{g} = \sigma(W_g [\mathbf{h}_{tab}^{cls} \,\|\, \mathbf{h}_{cross}] + b_g)$ để mô hình tự quyết định trọng số đóng góp của từng phương thức.
  3. **Luận giải giải pháp Hiệu chuẩn Xác suất (Calibration):** Đề xuất giải pháp **Temperature Scaling** đưa vào Giai đoạn 2 để hạ $ECE$ từ $> 0.08$ về $< 0.05$.
* **Đầu ra (Deliverables):**
  - Mục 3 & Mục 4 trong `docs/PROPOSED_OPTIMAL_SOLUTION.md`.
* **Trạng thái:** `[x] DONE`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 1 (ACCEPTANCE CRITERIA)
- [x] Chạy thành công `python scripts/run_baselines.py` không phát sinh lỗi bộ nhớ GPU (OOM) và ghi nhận đầy đủ số liệu 3 Baselines vào `data/baseline_results.json`.
- [x] Tệp `data/baseline_curves.png` được tạo với độ phân giải cao (300 DPI), đầy đủ chú thích trục và nhãn mô hình.
- [x] Hoàn thành nội dung lý thuyết và công thức toán học cho bản đề xuất phương án tối ưu.
- [x] Bàn giao kết quả thực nghiệm cho Thành viên 2 và Thành viên 3.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 1
1. **Lý Thuyết Cơ Chế Cross-Attention Late Fusion:**
   * *Vaswani, A. et al. (2017).* "Attention Is All You Need." *NeurIPS 2017*. [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).
   * *Trọng tâm cần đọc:* Công thức Scaled Dot-Product Attention áp dụng liên phương thức: Dùng vector bảng số làm Query ($Q_{tab}$) chiếu lên không gian từ ngữ của văn bản ($K_{text}, V_{text}$). Xem chi tiết tại [`docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md`](../../docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md).
2. **Hiệu Chuẩn Nhiệt Độ (Temperature Scaling):**
   * *Guo, C. et al. (2017).* "On Calibration of Modern Neural Networks." *ICML 2017*. [arXiv:1706.04599](https://arxiv.org/abs/1706.04599).
   * *Trọng tâm cần đọc:* Thuật toán tối ưu hóa tham số nhiệt độ $T$ trên Validation Set bằng phương pháp L-BFGS cực tiểu hóa Negative Log-Likelihood (NLL).
3. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.7, Mục 2.9, Mục 3.1 và Mục 3.2).

