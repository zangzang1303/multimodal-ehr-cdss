# BACKLOG 03 (TUẦN 3) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & SYSTEM)
### Trọng Tâm: Dashboard Đối So sánh Baselines, Unit Tests Benchmark & Soạn Thảo Đề Xuất Tối Ưu

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 3 của Giai đoạn 1, Thành viên 3 phụ trách trực quan hóa toàn bộ kết quả thực nghiệm đối chứng lên giao diện web Next.js, viết bộ test kiểm tra tính toàn vẹn của kết quả benchmark và giữ vai trò chủ trì tổng hợp, biên tập và xuất bản tài liệu trọng thể: **Báo Cáo Đề Xuất Phương Án Tối Ưu (`docs/PROPOSED_OPTIMAL_SOLUTION.md`)** nhằm nghiệm thu chính thức Giai đoạn 1 và mở khóa Giai đoạn 2.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Viết Unit Tests Kiểm Tra Tính Toàn Vẹn Benchmark (`tests/test_baselines_benchmark.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Xây dựng script kiểm thử tự động `tests/test_baselines_benchmark.py` để bảo đảm tính khách quan và khoa học:
  1. Kiểm tra sự tồn tại của tệp `data/baseline_results.json`.
  2. Xác thực (Assert) tệp JSON có đầy đủ cả 3 khóa: `baseline_1_classical_tabular`, `baseline_2_tabular_deep`, `baseline_3_text_only`.
  3. Xác thực các giá trị chỉ số toán học:
     - `0.5 < macro_auroc <= 1.0`
     - `0.0 <= macro_f1 <= 1.0`
     - `0.0 <= brier_score <= 1.0`
     - `0.0 <= ece <= 1.0`
     - Không có giá trị `NaN`, `Inf` hoặc `null` trong bất kỳ trường nào.
* **Lệnh thực thi & kiểm thử:**
  ```bash
  pytest tests/test_baselines_benchmark.py -v
  ```
* **Đầu ra (Deliverables):**
  - `tests/test_baselines_benchmark.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.2: Xây Dựng Màn Hình Dashboard So Sánh Baselines Trên Web
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  Xây dựng trang giao diện tại `frontend/src/app/baselines/page.tsx`:
  1. **Bảng Đối So Sánh (Head-to-Head Comparison Table):**
     - Hiển thị 3 hàng tương ứng 3 Baselines, các cột hiển thị: Tên mô hình, Dữ liệu đầu vào, AUROC, AUPRC, Macro-F1, Brier Score, ECE.
     - Highlight màu nổi bật chỉ số cao nhất của từng cột.
  2. **Biểu Đồ So Sánh Trực Quan:**
     - Sử dụng Chart.js hoặc Recharts hiển thị Bar Chart so sánh hiệu năng và độ lệch ECE giữa 3 mô hình.
  3. **Callout Phân Tích Điểm Nghẽn:**
     - Hộp thông báo màu hổ phách cảnh báo hiện tượng "Unimodal Information Blindspot" và "Overconfidence (ECE > 0.08)" của các mô hình hiện tại, dẫn link tới tài liệu Đề xuất Phương án Tối ưu.
* **Lệnh thực thi & kiểm thử:**
  Mở trình duyệt tại `http://localhost:3000/baselines`.
* **Đầu ra (Deliverables):**
  - `frontend/src/app/baselines/page.tsx`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 3.3: Chủ Trì Soạn Thảo Báo Cáo Đề Xuất Phương Án Tối Ưu (`docs/PROPOSED_OPTIMAL_SOLUTION.md`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Tổng hợp kết quả từ Thành viên 1 và Thành viên 2 để hoàn thiện tài liệu quyết định `docs/PROPOSED_OPTIMAL_SOLUTION.md` bao gồm 6 mục tiêu chuẩn:
  1. **Tóm tắt điều hành (Executive Summary):** Mục tiêu của Giai đoạn 1 và kết luận chính từ 3 Baselines.
  2. **Báo cáo kết quả thực nghiệm đối chứng:** Trích dẫn bảng số liệu từ `data/baseline_results.json` và phân tích khoảng cách hiệu năng giữa dữ liệu bảng và dữ liệu văn bản.
  3. **Phân tích ca bệnh sai biệt (Clinical Discrepancy Case Studies):** Tích hợp 2 ca bệnh thực tế do TV2 phân tích, chứng minh vì sao cần kết hợp cả 2 nguồn thông tin.
  4. **Kiến trúc phương án tối ưu đề xuất cho Giai đoạn 2:**
     - Tích hợp mạng *FT-Transformer* (nhánh bảng) và *Bio_ClinicalBERT* (nhánh text).
     - Cơ chế *Cross-Attention Late Fusion* (toán học do TV1 đóng góp).
     - Cơ chế *Temperature Scaling* đưa $ECE < 0.05$.
     - Tầng *Agentic RAG* đối chiếu phác đồ GINA/GOLD/ESC và trích dẫn bằng chứng ký tự (*Evidence Grounding*) chống ảo giác.
  5. **Kế hoạch hành động & Phân công nhiệm vụ Giai đoạn 2:** Sơ đồ lộ trình triển khai chi tiết cho nhóm 3 người từ Tuần 4 trở đi.
  6. **Biên bản nghiệm thu Giai đoạn 1:** Chữ ký xác nhận hoàn thành mục tiêu của cả 3 thành viên.
* **Đầu ra (Deliverables):**
  - `docs/PROPOSED_OPTIMAL_SOLUTION.md` hoàn chỉnh.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 3 (ACCEPTANCE CRITERIA)
- [ ] Chạy lệnh `pytest tests/test_baselines_benchmark.py -v` đạt 100% Pass.
- [ ] Trang `http://localhost:3000/baselines` hiển thị bảng so sánh và biểu đồ sắc nét, tải dữ liệu động từ backend hoặc file JSON.
- [ ] Tệp `docs/PROPOSED_OPTIMAL_SOLUTION.md` được viết hoàn chỉnh, khoa học, đầy đủ công thức toán và case study, được cả nhóm thông qua để sẵn sàng chuyển sang Giai đoạn 2.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 3
1. **Tiêu Chuẩn Báo Cáo Lâm Sàng TRIPOD-AI:**
   * *Collins, G. S. et al. (2024).* "TRIPOD+AI Statement: Updated Guidance for Reporting Clinical Prediction Models That Use Artificial Intelligence." *The BMJ*, 385:e078378. [doi:10.1136/bmj-2023-078378](https://www.bmj.com/content/385/bmj-2023-078378).
   * *Trọng tâm cần đọc:* Hướng dẫn báo cáo đầy đủ thông tin về bài toán, dữ liệu bảng đối chiếu baselines và các chỉ số đo lường hiệu năng/hiệu chuẩn khi soạn thảo `docs/PROPOSED_OPTIMAL_SOLUTION.md`.
2. **Dashboard Đối So Sánh Hiệu Năng Trên Next.js 14:**
   * *Recharts / Chart.js Integration:* [recharts.org](https://recharts.org/).
   * *Trọng tâm cần đọc:* Cách biểu diễn Bar Chart so sánh AUROC/F1 giữa 3 mô hình và Callout cảnh báo hiện tượng "Unimodal Blindspot" cho bác sĩ.
3. **Cẩm nang kỹ thuật của dự án:**
   * Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 1, Mục 2.15, Mục 3.1 và Mục 5).

