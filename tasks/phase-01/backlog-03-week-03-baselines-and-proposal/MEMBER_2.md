# BACKLOG 03 (TUẦN 3) - NHIỆM VỤ THÀNH VIÊN 2 (BIOMEDICAL DATA & PRIVACY)
### Trọng Tâm: Chia Tập Cấp Độ Bệnh Nhân, Dataset Loader Đa Phương Thức & Phân Tích Sai Số Lâm Sàng

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 3 của Giai đoạn 1, Thành viên 2 hoàn thiện khâu xử lý dữ liệu cuối cùng bằng kỹ thuật phân chia theo cấp độ bệnh nhân (Patient-Level Group Splitting), đóng gói `Dataset` và `DataLoader` cho PyTorch, đồng thời thực hiện phân tích sâu về mặt y khoa đối với các ca bệnh dự đoán sai (Clinical Error Analysis) của 3 mô hình đối chứng.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Phân Chia Dữ Liệu Theo Cấp Độ Bệnh Nhân (`src/data_pipeline/dataset_loader.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Hiện thực hàm `create_patient_level_splits(df, patient_col='patient_id', target_col='diagnosis_label', test_size=0.15, val_size=0.15, seed=42)`:
     - Sử dụng `StratifiedGroupKFold` để bảo đảm hai điều kiện tiên quyết đồng thời:
       - **Group constraint:** Toàn bộ các lần khám (encounters) của cùng một `patient_id` chỉ được nằm trọn vẹn trong DUY NHẤT một tập (hoặc Train, hoặc Val, hoặc Test).
       - **Stratified constraint:** Phân phối 4 lớp bệnh lý giữa Train (70%), Val (15%), và Test (15%) giữ được sự cân bằng tương đương nhau.
  2. Áp dụng toàn bộ pipeline đã xây dựng ở Tuần 2 (`deidentifier`, `temporal_aligner`, `imputer`) lên các tập sau chia:
     - *Nguyên tắc Fit-Transform:* Chỉ `.fit()` bộ gán khuyết `imputer` trên tập Train, sau đó dùng chính tham số đó để `.transform()` lên tập Val và Test (ngăn ngừa rò rỉ phân phối dữ liệu).
  3. Xuất dữ liệu sạch ra 3 tệp Parquet chuẩn hóa:
     - `data/processed/train.parquet`
     - `data/processed/val.parquet`
     - `data/processed/test.parquet`
* **Đầu ra (Deliverables):**
  - Hàm `create_patient_level_splits` trong `src/data_pipeline/dataset_loader.py`.
  - 3 tệp dữ liệu sạch trong `data/processed/`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Đóng Gói Lớp `MultimodalEHRDataset` Sẵn Sàng Cho Giai Đoạn 2
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Xây dựng lớp `MultimodalEHRDataset(torch.utils.data.Dataset)` trong `src/data_pipeline/dataset_loader.py`:
     - Nhận vào dataframe và Tokenizer đã khởi tạo.
     - Phương thức `__getitem__(idx)` trả về một dictionary gồm 4 phần tử:
       - `tabular_tensor`: Tensor kiểu `float32` chứa 9 biến số liên tục đã chuẩn hóa và 4 biến phân loại.
       - `input_ids`: Tensor kiểu `int64` chứa token IDs của ghi chú bệnh án sau tokenizer (padded/truncated về độ dài 512).
       - `attention_mask`: Tensor kiểu `int64` chứa mặt nạ chú ý tương ứng.
       - `label`: Tensor kiểu `int64` chứa nhãn bệnh (0 đến 3).
  2. Viết hàm `get_data_loaders(batch_size=64)` trả về 3 DataLoader: `train_loader`, `val_loader`, `test_loader`.
* **Đầu ra (Deliverables):**
  - Lớp `MultimodalEHRDataset` và hàm `get_data_loaders`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Phân Tích Ma Trận Nhầm Lẫn & Các Ca Bệnh Sai Biệt Thực Tế
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Xuất hình ảnh ma trận nhầm lẫn (Confusion Matrix) cho cả 3 mô hình đối chứng lưu tại `data/confusion_matrices_baselines.png`.
  2. Thực hiện **Phân tích ca bệnh sai biệt (Discrepancy Analysis):** Lọc ra các ca bệnh cụ thể từ Hold-out Test Set để chỉ ra bản chất hạn chế của dữ liệu đơn phương thức:
     - *Trường hợp 1 (Bảng số sai, Văn bản đúng):* Bệnh nhân COPD giai đoạn đầu có các chỉ số sinh hiệu và xét nghiệm máu gần như bình thường (bảng số chẩn đoán nhầm thành Hen hoặc Không bệnh), nhưng trong ghi chú lâm sàng tự do bác sĩ ghi rõ *"tiền sử hút thuốc lào 30 bao-năm, khó thở xuất hiện liên tục khi đi bộ trên đường bằng"* $\rightarrow$ Chỉ mô hình NLP mới bắt được thông tin quyết định này.
     - *Trường hợp 2 (Văn bản sai, Bảng số đúng):* Bệnh nhân Suy tim sung huyết cấp có triệu chứng cơ năng *"khó thở, ho đờm"* rất dễ nhầm với Viêm phổi hoặc Hen trong văn bản ghi chú, nhưng bảng số học ghi nhận huyết áp tăng vọt $190/105$ mmHg, nhịp thở $32$ lần/phút, và SpO2 tụt $86\%$ không kèm sốt ($36.8^\circ C$) $\rightarrow$ Chỉ mô hình Bảng số mới nhận diện chính xác cơn phù phổi cấp do suy tim.
  3. Soạn thảo toàn bộ nội dung phân tích sai số lâm sàng này vào Mục 2 của `docs/PROPOSED_OPTIMAL_SOLUTION.md`.
* **Đầu ra (Deliverables):**
  - `data/confusion_matrices_baselines.png`.
  - Mục 2 trong `docs/PROPOSED_OPTIMAL_SOLUTION.md`.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 2 (ACCEPTANCE CRITERIA)
- [ ] 3 tệp Parquet trong `data/processed/` được tạo thành công; chạy script kiểm tra giao tập `set(train_patients) & set(test_patients) == set()` (100% không trùng lặp bệnh nhân).
- [ ] Lớp `MultimodalEHRDataset` khởi tạo DataLoader nạp mượt mà, trả về đúng 4 tensor với shape chuẩn.
- [ ] Tệp `data/confusion_matrices_baselines.png` hiển thị trực quan tỷ lệ nhầm lẫn giữa 4 nhóm bệnh.
- [ ] Cung cấp các case study cụ thể cho bản Báo cáo Đề xuất Phương án Tối ưu.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 2
1. **Kỹ Thuật Phân Chia Cấp Độ Bệnh Nhân (Patient-Level Partitioning):**
   * *Scikit-learn Documentation:* [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).
   * *Trọng tâm cần đọc:* Ngăn ngừa rò rỉ dữ liệu giữa các lần tái khám (encounters) của cùng một bệnh nhân. Tham khảo chi tiết tại Mục 4 của [`docs/03_DATA_PIPELINE_AND_PRIVACY.md`](../../docs/03_DATA_PIPELINE_AND_PRIVACY.md).
2. **PyTorch Dataset & DataLoader Đa Phương Thức:**
   * *PyTorch Official Tutorials:* [Datasets & DataLoaders](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html).
   * *Trọng tâm cần đọc:* Cách đóng gói từ điển chứa song song `tabular`, `input_ids`, `attention_mask`, và `label`.
3. **Phân Tích Ca Bệnh Sai Biệt Trong Y Khoa:**
   * *Hunik, L. et al. (2024).* "Prediction Models for Diagnosis in Primary Care Using Electronic Health Records." *JMIR Medical Informatics*, Preprint 62862.
   * *Trọng tâm cần đọc:* Thảo luận về việc mô hình bảng số bị mù mờ trước bệnh sử hút thuốc, thói quen sinh hoạt và mô tả cơn khó thở kịch phát về đêm của bệnh nhân.
4. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.6, Mục 3.1 và Mục 3.3).

