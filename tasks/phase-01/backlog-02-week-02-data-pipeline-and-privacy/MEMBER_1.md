# BACKLOG 02 (TUẦN 2) - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Hiện Thực Khung Mã Nguồn 3 Baselines & Xây Dựng Hệ Thống Độ Đo Đánh Giá Đa Lớp

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 2 của Giai đoạn 1, Thành viên 1 tập trung xây dựng toàn bộ kiến trúc mã nguồn cho 3 Mô hình Đối chứng (Baselines) tại `src/models/baselines.py`, viết khung kịch bản huấn luyện tự động `scripts/run_baselines.py` và triển khai module tính toán độ đo đánh giá khoa học đa lớp `src/evaluation/metrics.py`.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Hiện Thực Khung 3 Baselines (`src/models/baselines.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Xây dựng tệp `src/models/baselines.py` chứa 3 lớp mô hình độc lập:
  1. **Lớp `ClassicalTabularBaseline`:**
     - Tích hợp `scikit-learn` Pipeline: Bộ tiền xử lý `ColumnTransformer` (dùng `StandardScaler` cho 9 biến số và `OneHotEncoder(handle_unknown='ignore')` cho 4 biến phân loại).
     - Hỗ trợ lựa chọn estimator: `RandomForestClassifier`, `XGBClassifier` (đa lớp qua `objective='multi:softprob'`), hoặc `CatBoostClassifier(loss_function='MultiClass')`.
     - Cung cấp các phương thức chuẩn: `.fit(X_train, y_train)`, `.predict(X)`, `.predict_proba(X)`.
  2. **Lớp `TabularDeepBaseline(nn.Module)`:**
     - Xây dựng mạng nơ-ron học sâu dạng bảng (FT-Transformer đơn luồng hoặc Deep MLP kèm Residual Connections).
     - Đầu vào: Tensor bảng số sau chuẩn hóa.
     - Đầu ra: Tensor logits kích thước `[batch_size, 4]`.
  3. **Lớp `TextOnlyBaseline(nn.Module)`:**
     - Tải backbone Transformer y sinh từ HuggingFace (`emilyalsentzer/Bio_ClinicalBERT`).
     - Trích xuất representation từ token `[CLS]` (hoặc Mean Pooling): $h_{cls} \in \mathbb{R}^{768}$.
     - Đi qua Dropout ($p = 0.2$) và Linear Head: $W_{cls} \in \mathbb{R}^{768 \times 4}$ để xuất ra 4 logits tương ứng 4 bệnh lý.
* **Đầu ra (Deliverables):**
  - `src/models/baselines.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Xây Dựng Module Tính Độ Đo Đánh Giá Đa Lớp (`src/evaluation/metrics.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Viết tệp `src/evaluation/metrics.py` triển khai hàm tính toán toàn diện các chỉ số phân loại đa lớp:
  1. **Macro AUROC:** `roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')`.
  2. **Macro AUPRC:** `average_precision_score(y_true_onehot, y_prob, average='macro')`.
  3. **Macro F1-Score & Accuracy:** `f1_score(y_true, y_pred, average='macro')`.
  4. **Multi-class Brier Score:** Đo khoảng cách giữa phân phối xác suất dự đoán và nhãn one-hot:
     $$\text{Brier} = \frac{1}{N} \sum_{i=1}^N \sum_{k=1}^K (p_{ik} - y_{ik})^2$$
  5. **Expected Calibration Error (ECE):** Phân chia thành $M = 10$ bins theo độ tin cậy để đo mức độ hiệu chuẩn xác suất:
     $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$$
* **Đầu ra (Deliverables):**
  - `src/evaluation/metrics.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Xây Dựng Khung Script Huấn Luyện (`scripts/run_baselines.py`)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Xây dựng cấu trúc CLI cho `scripts/run_baselines.py` sử dụng `argparse`:
     - `--data_dir`: Đường dẫn thư mục chứa dữ liệu processed.
     - `--config`: Đường dẫn tới `configs/model_config.yaml`.
     - `--output_file`: Tệp lưu kết quả JSON (mặc định `data/baseline_results.json`).
     - `--baseline`: Tùy chọn huấn luyện (`all`, `tabular_classic`, `tabular_deep`, `text_only`).
  2. Viết khung nạp dữ liệu và khung vòng lặp huấn luyện, sẵn sàng tiếp nhận dữ liệu sạch phân chia theo cấp độ bệnh nhân từ Thành viên 2 ở Tuần 3.
* **Đầu ra (Deliverables):**
  - `scripts/run_baselines.py` (khung mã nguồn).
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 1 (ACCEPTANCE CRITERIA)
- [ ] Lớp `ClassicalTabularBaseline` huấn luyện thử và dự đoán xác suất thành công trên dữ liệu bảng giả lập.
- [ ] Lớp `TextOnlyBaseline` thực hiện forward pass thành công với một batch dummy token `(input_ids, attention_mask)` và trả về tensor kích thước `[batch_size, 4]`.
- [ ] Chạy unit test kiểm thử hàm `compute_multiclass_metrics` trong `src/evaluation/metrics.py` xuất ra đúng dict chứa 5 chỉ số (AUROC, AUPRC, F1, Brier, ECE).
- [ ] Script `scripts/run_baselines.py --help` hiển thị đầy đủ hướng dẫn CLI.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 1
1. **Xử lý Pipeline bảng số đa lớp với Scikit-learn & XGBoost:**
   * *Scikit-learn Documentation:* [Pipeline & ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html#column-transformer).
   * *XGBoost Documentation:* [Multiclass Objective (`multi:softprob`)](https://xgboost.readthedocs.io/en/stable/parameter.html).
2. **Công thức toán học các độ đo khoa học (ECE, Brier Score, AUROC):**
   * *Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).* "On Calibration of Modern Neural Networks." *ICML 2017*. [arXiv:1706.04599](https://arxiv.org/abs/1706.04599).
   * *Trọng tâm cần đọc:* Mục 2 (Definitions of Calibration, ECE, MCE, and Reliability Diagrams). Xem công thức triển khai trực tiếp tại Mục 2.8 của [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md).
3. **Mã nguồn và kiến trúc Baseline:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.7, Mục 2.8 và Mục 3.1).

