# BACKLOG 02 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Text Encoder, Vòng Lặp Huấn Luyện Đa Phương Thức, Đo ECE & Kiểm Tra Công Bằng Thuật Toán

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Xây Dựng Tầng Mã Hóa Văn Bản Y Sinh (`src/models/text_encoder.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết lớp `ClinicalTextEncoder` nạp mô hình `emilyalsentzer/Bio_ClinicalBERT` hoặc `BioLinkBERT` từ HuggingFace Transformers.
  2. Xử lý chuỗi văn bản đã khử định danh (max_length = 256).
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
  3. Bổ sung cờ lệnh `--calibrate` tự động gọi module Temperature Scaling của TV1 khi huấn luyện xong.
* **Lệnh chạy:**
  ```bash
  python scripts/train_multimodal.py --config configs/model_config.yaml --epochs 50 --batch_size 32 --calibrate
  ```
* **Đầu ra (Deliverable):** `scripts/train_multimodal.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Đo Đạc Chỉ Số Hiệu Chuẩn Xác Suất (ECE, MCE, Brier Score)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết các hàm `compute_ece`, `compute_mce`, `compute_brier_score` trong `src/evaluation/metrics.py`.
  2. Đo đạc xác suất trước và sau khi hiệu chuẩn trên tập Test.
  3. Vẽ biểu đồ Reliability Diagram chia 10 bins, lưu tại `data/calibration_curve.png`.
* **Tiêu chuẩn nghiệm thu:** Chứng minh chỉ số sau hiệu chuẩn đạt **$ECE < 0.05$** (sai lệch dưới 5%).
* **Đầu ra (Deliverable):** `data/calibration_curve.png`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.4: Phân Tích Công Bằng Phân Nhóm Thuật Toán (Subgroup Fairness Audit)
* **Độ ưu tiên:** `[P2 - Normal]`
* **Mô tả:** Đánh giá hiệu năng AUROC và F1 phân tầng theo độ tuổi ($<65$ vs $\ge 65$) và giới tính (Nam vs Nữ). Xuất kết quả vào `data/fairness_report.json` phục vụ báo cáo khoa học.
* **Đầu ra (Deliverable):** `data/fairness_report.json`.
* **Trạng thái:** `[ ] TODO`
