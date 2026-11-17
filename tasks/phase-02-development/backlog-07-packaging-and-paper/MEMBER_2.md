# BACKLOG 07 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng tâm: snapshot Qdrant, cohort, PROBAST+AI, PHI và quyền sử dụng dữ liệu

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Tạo Snapshot Cơ Sở Dữ Liệu Qdrant Offline
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Tạo snapshot/manifest từ tài liệu phác đồ đã kiểm nguồn và quyền phân phối; ghi phiên bản Qdrant, embedding model, checksum và hướng dẫn restore. Không đưa phác đồ có bản quyền lên Git khi chưa được phép.
* **Đầu ra (Deliverable):**
  - Snapshot hợp lệ: `data/vector_store/qdrant_snapshot.tar.gz`
  - Manifest kỹ thuật: `data/vector_store/manifest.json` (SHA-256 checksums, Qdrant client 1.20.0, 768-dim Cosine, 14 clinical chunks, all-mpnet-base-v2)
  - Quản trị viên & kịch bản restore: `scripts/qdrant_snapshot_manager.py` (lệnh `create`, `restore`, `verify`)
  - Hướng dẫn restore chi tiết: `data/vector_store/README.md` và `docs/QDRANT_SNAPSHOT_AND_RESTORE_GUIDE.md`
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 2.2: Soạn Thảo Cohort & Đánh Giá PROBAST+AI
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết phần *Clinical Cohort & Data Pipeline* của bài báo khoa học: Mô tả quy trình De-ID, phương pháp khóa chuỗi thời gian, tỷ lệ missing data và kỹ thuật gán MICE, phân chia theo Patient ID.
  2. Dùng PROBAST+AI phù hợp loại nghiên cứu; ghi từng miền, câu hỏi áp dụng, bằng chứng và đánh giá nguy cơ sai lệch/tính áp dụng, kể cả mức cao hoặc chưa rõ. Không khẳng định Low Risk khi thiếu bằng chứng.
* **Đầu ra (Deliverable):**
  - Bản thảo LaTeX Cohort: `docs/paper_latex/sections/02_clinical_cohort.tex` ($N=2000$, Bảng đặc điểm lâm sàng ban đầu, quy trình De-ID 18 trường PHI, khóa thời gian $t < t_{\text{diag}}$, cấm tiêu chuẩn vàng, StratifiedGroupKFold 70:15:15, MICE với missing indicators).
  - Báo cáo thẩm định PROBAST+AI: `docs/08_PROBAST_AI_AUDIT_REPORT.md` (chi tiết 20 câu hỏi tín hiệu) và phân mục LaTeX `docs/paper_latex/sections/08_discussion_ethics.tex` (phân định rõ Low Risk cho sai lệch nội kiểm và mức Chưa rõ/Cao cho tính áp dụng ngoại kiểm trên dữ liệu thực tế tại Việt Nam).
* **Trạng thái:** `[x] DONE`

---

### 🔹 Nhiệm vụ 2.3: Rà Soát Bảo Mật PHI Lần Cuối & Giấy Phép Bản Quyền
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Rà mã nguồn, cấu hình, dữ liệu mẫu và lịch sử Git để tìm PHI/secret; lập báo cáo phạm vi, phát hiện và cách xử lý. Không gọi kết quả rà quét là bảo đảm tuyệt đối hoặc chứng chỉ độc lập.
  2. Hoàn thiện Data Dictionary; chỉ chọn MIT cho phần mã do nhóm có quyền cấp phép, ghi riêng giấy phép dữ liệu, phác đồ và pretrained models.
* **Đầu ra (Deliverable):**
  - Kịch bản rà quét tự động: `scripts/audit_phi_and_secrets.py`
  - Báo cáo kiểm toán bảo mật & giấy phép: `docs/09_PHI_AND_LICENSE_AUDIT_REPORT.md` (phạm vi, phát hiện 0 secret trong code/history, giải trình dữ liệu mẫu thô, tuyên bố miễn trừ bảo đảm tuyệt đối)
  - Từ điển dữ liệu đa phương thức: `docs/DATA_DICTIONARY.md` (đặc tả 13 biến bảng, 2 biến chỉ báo khuyết, văn bản bệnh án và 4 nhãn kết cục)
  - Giấy phép phân tầng: `LICENSE` (MIT cho mã nguồn nhóm phát triển) và `NOTICE` (ghi nhận bản quyền Bio_ClinicalBERT, MPNet, Synthea, MTSamples, GINA, GOLD, ESC, BYT).
* **Trạng thái:** `[x] DONE`
