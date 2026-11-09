# BACKLOG 07 (PACKAGING & PAPER) - NHIỆM VỤ THÀNH VIÊN 3 (FULL-STACK AI & FRONTEND)
### Trọng Tâm: Docker Compose Trọn Gói, Soạn Thảo Software Architecture Bài Báo & Video Kịch Bản Demo

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 3.1: Hoàn Thiện Docker Compose Trọn Gói Một Lệnh
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Viết `Dockerfile` đa tầng (Multi-stage build) cho Frontend Next.js để tối ưu dung lượng image (`frontend/Dockerfile`, `output: "standalone"`).
  2. `[x]` Viết file `docker-compose.yml` kết nối 3 dịch vụ:
     - `frontend`: cổng 3000 (hỗ trợ biến môi trường `FRONTEND_PORT`)
     - `api`: cổng 8000 (Backend FastAPI)
     - `qdrant`: cổng 6333 (Vector DB)
  3. `[x]` Kiểm thử khởi chạy trên môi trường sạch:
     ```bash
     docker compose up --build -d
     docker compose ps
     ```
  4. `[x]` Xác nhận cả 3 dịch vụ (`mcdss-qdrant`, `mcdss-api`, `mcdss-frontend`) đều đạt trạng thái `healthy` và giao tiếp với nhau trơn tru qua mạng nội bộ Docker (`mcdss-internal-net`), tự động lập chỉ mục 6 vector CPG vào collection `clinical_guidelines` trên Qdrant.
* **Đầu ra (Deliverable):** `docker-compose.yml`, `Dockerfile`, `requirements-deploy.txt`, `frontend/Dockerfile`, `.dockerignore`, `frontend/.dockerignore`, `.env.example`.
* **Trạng thái:** `[x] DONE` *(Đã xác minh build thành công cả 2 image `multimodal-ehr-cdss-api` và `multimodal-ehr-cdss-frontend`, khởi chạy stack và xác nhận cả 3 container `mcdss-qdrant`, `mcdss-api`, `mcdss-frontend` đều đạt trạng thái `(healthy)` cũng như giao tiếp đầu-cuối thành công).*

---

### 🔹 Nhiệm vụ 3.2: Soạn Thảo Phần Software Architecture & Sơ Đồ Vector
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Soạn thảo phần *Software Architecture & Multi-Agent Implementation* của bài báo khoa học: Mô tả chi tiết giao thức RESTful, luồng hội chẩn đa tác tử (`DiagnosticStateGraph`), cơ chế truy xuất lai (`HybridGuidelineRetriever` kết hợp Qdrant Cosine + Okapi BM25) và cơ chế highlight `EvidenceGrounder`.
  2. `[x]` Xuất các sơ đồ kiến trúc hệ thống dạng vector độ nét cao (TikZ / SVG) phục vụ in ấn xuất bản.
* **Đầu ra (Deliverable):** Bộ bản thảo LaTeX đa phân mục tại `docs/paper_latex/` kèm template học thuật `templates/mcdss_article.sty`, các sơ đồ TikZ (`figures/*.tex`) và sơ đồ vector SVG độc lập (`figures/svg/*.svg`).
* **Trạng thái:** `[x] DONE (Phần của Thành viên 3)` — *Các phân mục phối hợp với Thành viên 1 & Thành viên 2 đã được tạo sẵn khung template trống (`[TODO-TV1]`, `[TODO-TV2]`) để điền số liệu thật sau khi Thành viên 1 & 2 hoàn tất các backlog.*

#### 📌 DANH SÁCH CHI TIẾT CÁC VỊ TRÍ TEMPLATE TRỐNG CẦN BỔ SUNG SAU KHI CÓ KẾT QUẢ TỪ THÀNH VIÊN 1 & 2:
1. **`docs/paper_latex/sections/00_abstract.tex` (Mục *Kết quả - Results*):**
   - `[TODO-TV1/TV2 (Backlog 04 Task 1.4, 2.3 & Backlog 06 Task 1.1)]`: Điền các chỉ số thực nghiệm `AUROC macro`, `AUPRC macro`, `Macro-F1`, `Brier Score`, `ECE` sau hiệu chuẩn Temperature Scaling từ checkpoint `data/checkpoints/multimodal_best.pt`.
   - `[TODO-TV1/TV2 (Backlog 06 Task 1.2 & 2.2)]`: Điền giá trị `Net Benefit` thực nghiệm, dải ngưỡng hiệu quả lâm sàng $p_t$, số ca can thiệp đúng ròng $\Delta\text{TP}_{\text{net}/100}$ và số ca can thiệp thừa tránh được $\Delta\text{FP}_{\text{avoided}/100}$ sau khi xuất ma trận dự đoán hold-out `data/holdout_predictions.npz`.
2. **`docs/paper_latex/sections/02_clinical_cohort.tex` (Mục 2.3 — Bảng `tab:subgroup_fairness_template`):**
   - `[TODO-TV2 (Backlog 04 Task 2.4)]`: Điền cỡ mẫu $n$, `Macro AUROC`, `Macro-F1`, `ECE` và độ chênh lệch cực đại $\Delta_{\max}$ cho 4 phân nhóm nhân khẩu học (Tuổi $<65$, Tuổi $\ge 65$, Nam, Nữ) từ tệp `data/fairness_report.json`.
3. **`docs/paper_latex/sections/03_methodology_fusion.tex` (Mục 3.3 — *Cấu hình Huấn luyện và Tối ưu Thời gian Suy luận GPU*):**
   - `[TODO-TV2 (Backlog 04 Task 2.2)]`: Điền số epoch dừng sớm (Early Stopping) và Validation NLL Loss sau khi chạy `scripts/train_multimodal.py`.
   - `[TODO-TV1 (Backlog 04 Task 1.3)]`: Điền giá trị tham số nhiệt độ tối ưu $T^*$ học được từ Validation Set lưu trong `data/checkpoints/multimodal_best.pt`.
   - `[TODO-TV1 (Backlog 05 Task 1.3 & Backlog 07 Task 1.1)]`: Điền độ trễ suy luận trung bình trên GPU (`ms/request`, mục tiêu $\le 150\text{ms}$) và dung lượng file `multimodal_best.pt` sau khi cắt bỏ optimizer states.
4. **`docs/paper_latex/sections/05_multi_agent_rag.tex` (Mục 5.1 — Nút 2 & Nút 3):**
   - `[TODO-TV1 (Backlog 05 Task 1.1)]`: Điền kết quả thử nghiệm độ tương đồng ngữ nghĩa của mô hình nhúng `sentence-transformers/all-mpnet-base-v2` (`vector_dim=768`, `similarity_threshold=0.72`) từ `configs/rag_config.yaml`.
   - `[TODO-TV2 (Backlog 05 Task 2.1 & Backlog 07 Task 2.1)]`: Điền tổng số chunks phác đồ thực tế ($\ge 100$ chunks) và thống kê phân bố theo từng nguồn (GINA 2024, GOLD 2024, ESC 2023, Bộ Y tế) sau khi chạy `src/agent/knowledge_ingest.py`.
   - `[TODO-TV1 (Backlog 05 Task 1.2)]`: Điền thông số mô hình LLM và kết quả thực nghiệm của module Prompt Chain-of-Thought đối kháng trong `src/agent/diagnostic_agent.py`.
5. **`docs/paper_latex/sections/06_frontend_dca_ux.tex` (Mục 6.1 — `DiagnosticCard.tsx`):**
   - `[TODO-TV1/TV2]`: Điền giá trị `ECE` thực nghiệm chính thức sau hiệu chuẩn trên tập Test.
6. **`docs/paper_latex/sections/07_empirical_results.tex` (Mục 7.1, 7.2, 7.3, 7.4):**
   - **Bảng `tab:benchmark_comparison` (Nhóm 2 — Ablation & M-CDSS Giai đoạn 2):** Điền các ô `[TODO-TV1]` và `[TODO-TV2]` (`AUROC`, `AUPRC`, `Macro-F1`, `Accuracy`, `Brier`, `ECE`) cho 3 hàng `Concat Late Fusion`, `M-CDSS Uncalibrated` và `M-CDSS Calibrated`, cùng nhận xét mức tăng $\Delta\text{AUROC}, \Delta\text{Macro-F1}$ và tham chiếu đồ thị `data/calibration_curve.png`.
   - **Mục 7.2 (Ca bệnh `PT-0044`, `PT-0254` & Confusion Matrix):** Điền xác suất dự đoán thực tế sau hiệu chuẩn và trọng số Cross-Attention của M-CDSS trên 2 ca bệnh, kèm chèn biểu đồ `data/confusion_matrix.png` (Nhiệm vụ 2.1 Backlog 06 của Thành viên 2).
   - **Bảng `tab:dca_empirical_template` (Mục 7.3 — DCA Net Benefit):** Điền các cột $\text{NB}_{\text{Tabular}}$, $\text{NB}_{\text{Text}}$, $\text{NB}_{\text{M-CDSS}}$, $\Delta\text{TP}_{\text{net}/100}$ và $\Delta\text{FP}_{\text{avoided}/100}$ tại các ngưỡng $p_t \in \{0.10, 0.20, 0.25, 0.35, 0.45\}$ sau khi chạy `scripts/evaluate_clinical_utility.py` (Nhiệm vụ 1.2 & 2.2 Backlog 06 của Thành viên 1 & 2).
   - **Mục 7.4 (External Validation & Clinician Survey):** Điền độ suy giảm hiệu năng $\Delta\text{AUROC}$ ngoại kiểm (`[TODO-TV1: Backlog 06 Task 1.3]`) và điểm khảo sát Likert 1–5 của 2–3 bác sĩ trên 20 ca bệnh ngẫu nhiên (`[TODO-TV2: Backlog 06 Task 2.3]`).
7. **`docs/paper_latex/sections/08_discussion_ethics.tex` (Mục 8.1 — PROBAST & Bảo mật PHI):**
   - `[TODO-TV2]`: Điền chỉ số `ECE` thực nghiệm vào hàng 4 Bảng `tab:probast_summary`.
   - `[TODO-TV2 (Backlog 07 Task 2.2)]`: Đính kèm Phụ lục Bảng thẩm định chi tiết 20 câu hỏi tín hiệu PROBAST (Supplementary Material).
   - `[TODO-TV2 (Backlog 07 Task 2.3)]`: Điền kết quả rà quét bảo mật PHI lần cuối trên toàn bộ repository và lịch sử git commit.

---

### 🔹 Nhiệm vụ 3.3: Sản Xuất Video Kịch Bản Demo Lâm Sàng & Slide Báo Cáo
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. `[x]` Xây dựng kịch bản video demo lâm sàng (thời lượng 3 - 5 phút) và kịch bản bộ slide báo cáo nghiệm thu dự án (đã chừa sẵn các ô `[TODO-TV1/TV2]` tại Phân cảnh 3, Phân cảnh 5 của kịch bản Video và tại các Slide 13, 14, 15, 17, 18 của kịch bản Slide để điền số liệu thật của Thành viên 1 & 2):
     - `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md`
     - `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md`
  2. `[ ]` Quay và biên tập video chất lượng Full HD kèm giọng thuyết minh và phụ đề hoàn chỉnh.
  3. `[ ]` Thiết kế và xuất bản file slide thuyết trình nghiệm thu dự án cuối cùng (PDF / PPTX).
* **Đầu ra (Deliverable):** Video Demo sản phẩm Full HD, Slide nghiệm thu dự án.
* **Trạng thái:** `[ ] TODO` *(Đã hoàn thành kịch bản chi tiết cho Video Demo và Slide báo cáo; chờ điền số liệu thực nghiệm cuối của Thành viên 1 & 2 và xuất 2 sản phẩm media cuối cùng).*
