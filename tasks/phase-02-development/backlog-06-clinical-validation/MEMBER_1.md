# BACKLOG 06 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Đo Đạc Đa Chiều Năng Lực Phân Biệt, Hiện Thực DCA Net Benefit & Ngoại Kiểm

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Đo Đạc Bộ Chỉ Số Khoa Học Định Lượng
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** 
  1. Mở rộng `src/evaluation/metrics.py` (đã có AUROC/AUPRC/F1/Brier/ECE), bổ sung chỉ số còn thiếu và CI 95% bằng bootstrap theo nhóm nguồn/bệnh nhân:
     - AUROC One-vs-Rest Macro (`roc_auc_score(multi_class='ovr', average='macro')`).
     - AUPRC Macro (`average_precision_score(average='macro')`).
     - Macro-F1 Score, Precision, Recall, Specificity.
     - Multiclass Brier Score.
  2. Đánh giá và lập bảng so sánh chi tiết giữa Baseline 1, Baseline 2, Baseline 3 và M-CDSS trên tập Hold-out Test Set.
* **Tiêu chuẩn nghiệm thu:** So sánh trên cùng strict test với CatBoost, FT-Transformer và Bio_ClinicalBERT; báo cáo chênh lệch AUROC và CI 95%, kể cả khi không cải thiện. Baseline text strict hiện đạt AUROC 0.973453 nên không đặt điều kiện tăng tuyệt đối 0.04.
* **Đầu ra (Deliverable):** Báo cáo số liệu định lượng, cập nhật `src/evaluation/metrics.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Hiện Thực Phân Tích Đường Cong Quyết Định (DCA)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Hiện thực `src/evaluation/dca_analysis.py`:
     - Chọn trước một bệnh đích one-vs-rest, hành động giả định và quần thể. Chỉ dùng dải ngưỡng có lý do theo quyết định đó; tính Net Benefit:
       $$\text{Net Benefit}(p_t) = \frac{\text{TP}}{N} - \frac{\text{FP}}{N} \cdot \left( \frac{p_t}{1 - p_t} \right)$$
     - Tính Treat All/Treat None theo cùng bệnh đích; ghi tỷ lệ hiện mắc và số mẫu tại mỗi ngưỡng. Trên dữ liệu tổng hợp, gọi đây là DCA minh họa, không suy ra lợi ích lâm sàng thực tế.
  2. Xuất biểu đồ so sánh độ nét cao lưu tại `data/dca_curve.png`.
* **Đầu ra (Deliverable):** `src/evaluation/dca_analysis.py`, `data/dca_curve.png`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Thực Hiện Kiểm Định Ngoại Kiểm (External Validation)
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Xác minh nguồn ngoài, quyền sử dụng, nhãn và tính tương thích đầu vào trước khi gọi là ngoại kiểm. Nếu chưa có nguồn phù hợp, thực hiện leave-source-out/temporal split và ghi đúng là đánh giá độ bền nội bộ; không tuyên bố đã ngoại kiểm.
* **Đầu ra (Deliverable):** Báo cáo tính tổng quát hóa nêu loại kiểm tra, nguồn và giới hạn; danh sách đầu vào còn thiếu cho ngoại kiểm thực.
* **Trạng thái:** `[ ] TODO`
