# BACKLOG 04 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Text Encoder, Vòng Lặp Huấn Luyện Đa Phương Thức, Đo ECE & Kiểm Tra Công Bằng Thuật Toán

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Xây Dựng Tầng Mã Hóa Văn Bản Y Sinh (`src/models/text_encoder.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết lớp `ClinicalTextEncoder` nạp mô hình `emilyalsentzer/Bio_ClinicalBERT` hoặc `BioLinkBERT` từ HuggingFace Transformers.
  2. Xử lý ghi chú đã khử định danh với `max_length=512` để so sánh được với baseline strict; nếu giảm xuống 256 vì tài nguyên, ghi nhận thành một thí nghiệm riêng.
  3. Trích xuất ma trận biểu diễn ngữ cảnh $T_{text} \in \mathbb{R}^{(S+2) \times d_{text}}$ ($d_{text} = 768$).
  4. Áp dụng ma trận chiếu tuyến tính $W_{proj}$ chiếu về chiều $d = 128$: $H_{text} = T_{text} W_{proj} \in \mathbb{R}^{(S+2) \times 128}$.
* **Đầu ra (Deliverable):** `src/models/text_encoder.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Xây Dựng Vòng Lặp Huấn Luyện Đa Phương Thức (`scripts/train_multimodal.py`)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Viết script huấn luyện hoàn chỉnh hỗ trợ tối ưu AdamW, Cosine Annealing learning rate schedule, và Mixed Precision (`torch.cuda.amp.autocast`).
  2. Tích hợp cơ chế Early Stopping (dừng nếu sau 7 epochs validation loss không giảm).
  3. Bổ sung `--data-dir` (mặc định `data/processed_rebuilt_strict`), kiểm tra audit `passed: true`, và `--calibrate` chỉ khớp Temperature Scaling trên validation. Lưu seed, cấu hình, scaler/tokenizer, thứ tự nhãn và $T$ để inference tái lập được.
* **Lệnh chạy:**
  ```bash
  python scripts/train_multimodal.py --data-dir data/processed_rebuilt_strict --config configs/model_config.yaml --epochs 50 --batch_size 32 --calibrate
  ```
* **Đầu ra (Deliverable):** `scripts/train_multimodal.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Đo Đạc Chỉ Số Hiệu Chuẩn Xác Suất (ECE, MCE, Brier Score)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Tái sử dụng `expected_calibration_error` và `compute_multiclass_metrics` đã có trong `src/evaluation/metrics.py`; bổ sung MCE và kiểm thử định nghĩa metric nếu cần, tránh hai cách tính ECE/Brier khác nhau.
  2. Đo đạc xác suất trước và sau khi hiệu chuẩn trên tập Test.
  3. Vẽ biểu đồ Reliability Diagram chia 10 bins, lưu tại `data/calibration_curve.png`.
* **Tiêu chuẩn nghiệm thu:** Báo cáo ECE/Brier trước và sau hiệu chuẩn cùng reliability diagram trên strict test. $ECE < 0.05$ là mục tiêu, không điều chỉnh $T$ theo test để đạt ngưỡng.
* **Đầu ra (Deliverable):** `data/calibration_curve.png`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.4: Phân Tích Công Bằng Phân Nhóm Thuật Toán (Subgroup Fairness Audit)
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** Đánh giá AUROC/F1 theo tuổi và giới trên strict test, kèm cỡ mẫu và khoảng tin cậy; ghi rõ phân tích trên dữ liệu tổng hợp không chứng minh công bằng trên bệnh nhân thực. Xuất `data/fairness_report.json`.
* **Đầu ra (Deliverable):** `data/fairness_report.json`.
* **Trạng thái:** `[ ] TODO`
