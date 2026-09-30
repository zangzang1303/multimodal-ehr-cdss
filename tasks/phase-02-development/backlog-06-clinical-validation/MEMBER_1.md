# BACKLOG 04 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Đo Đạc Đa Chiều Năng Lực Phân Biệt, Hiện Thực DCA Net Benefit & Ngoại Kiểm

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Đo Đạc Bộ Chỉ Số Khoa Học Định Lượng
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** 
  1. Viết module tính toán trong `src/evaluation/metrics.py`:
     - AUROC One-vs-Rest Macro (`roc_auc_score(multi_class='ovr', average='macro')`).
     - AUPRC Macro (`average_precision_score(average='macro')`).
     - Macro-F1 Score, Precision, Recall, Specificity.
     - Multiclass Brier Score.
  2. Đánh giá và lập bảng so sánh chi tiết giữa Baseline 1, Baseline 2, Baseline 3 và M-CDSS trên tập Hold-out Test Set.
* **Tiêu chuẩn nghiệm thu:** Multimodal Model đạt AUROC $\ge 0.88$ (cao hơn Baseline tối thiểu 0.04).
* **Đầu ra (Deliverable):** Báo cáo số liệu định lượng, cập nhật `src/evaluation/metrics.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Hiện Thực Phân Tích Đường Cong Quyết Định (DCA)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Hiện thực `src/evaluation/dca_analysis.py`:
     - Tính toán Net Benefit qua 50 ngưỡng xác suất $p_t \in [0.05, 0.80]$:
       $$\text{Net Benefit}(p_t) = \frac{\text{TP}}{N} - \frac{\text{FP}}{N} \cdot \left( \frac{p_t}{1 - p_t} \right)$$
     - Tính Net Benefit cho chiến lược "Treat All" và "Treat None".
  2. Xuất biểu đồ so sánh độ nét cao lưu tại `data/dca_curve.png`.
* **Đầu ra (Deliverable):** `src/evaluation/dca_analysis.py`, `data/dca_curve.png`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Thực Hiện Kiểm Định Ngoại Kiểm (External Validation)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Chạy mô hình trên một tập dữ liệu ngoại kiểm độc lập (phân vùng bệnh viện hoặc cơ sở y tế khác) để đánh giá độ suy giảm hiệu năng $\Delta \text{AUROC}$ theo đúng khuyến nghị của bài báo JMIR.
* **Đầu ra (Deliverable):** Báo cáo kết quả External Validation.
* **Trạng thái:** `[ ] TODO`
