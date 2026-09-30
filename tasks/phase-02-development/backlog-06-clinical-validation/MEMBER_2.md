# BACKLOG 04 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Ma Trận Nhầm Lẫn, Error Analysis, Tự Động Hóa Evaluation & Khảo Sát Bác Sĩ

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Ma Trận Nhầm Lẫn & Phân Tích Ca Bệnh Sai Biệt (Error Analysis)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Vẽ biểu đồ ma trận nhầm lẫn (Confusion Matrix) đa lớp cho 4 bệnh lý (Hen, COPD, Suy tim, Viêm phổi) trên tập Test, lưu tại `data/confusion_matrix.png`.
  2. Lọc danh sách các ca bệnh dự đoán sai: Phân tích nguyên nhân lâm sàng (ví dụ: ca bệnh chồng lấp Hen-COPD có hút thuốc lá, hoặc ca suy tim giai đoạn đầu có ran rít giống hen phế quản) để cung cấp luận chứng cho bài báo khoa học.
* **Đầu ra (Deliverable):** `data/confusion_matrix.png`, tài liệu phân tích ca bệnh sai biệt.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Tự Động Hóa Kịch Bản Đánh Giá Lâm Sàng
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Viết script `scripts/evaluate_clinical_utility.py`:
  - Tự động nạp mô hình `multimodal_best.pt` và tập `test.parquet`.
  - Tính toán toàn bộ các chỉ số phân biệt (AUROC, AUPRC, F1), chỉ số hiệu chuẩn (ECE, Brier) và lợi ích ròng (DCA).
  - Xuất toàn bộ biểu đồ ảnh (ROC curves, PR curves, DCA curve, Calibration curve) vào thư mục `data/evaluation_plots/`.
* **Lệnh chạy:**
  ```bash
  python scripts/evaluate_clinical_utility.py --model_path data/checkpoints/multimodal_best.pt --test_data data/processed/test.parquet --output_plots data/evaluation_plots/
  ```
* **Đầu ra (Deliverable):** `scripts/evaluate_clinical_utility.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Tổ Chức Khảo Sát Đánh Giá Định Tính Với Bác Sĩ
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** 
  1. Xây dựng phiếu khảo sát lâm sàng (Likert Scale 1-5):
     - Mức độ chính xác của dự đoán sơ bộ.
     - Tính thuyết phục của các câu chứng cứ được highlight trong bệnh án.
     - Tính hữu ích của việc trích dẫn phác đồ GINA/GOLD/ESC.
  2. Mời 2-3 bác sĩ/chuyên gia y tế thực hiện blind-review trên 20 ca bệnh lâm sàng ngẫu nhiên.
  3. Tổng hợp thành báo cáo định tính (Clinician Feedback Report).
* **Đầu ra (Deliverable):** Báo cáo đánh giá của chuyên gia y tế.
* **Trạng thái:** `[ ] TODO`
