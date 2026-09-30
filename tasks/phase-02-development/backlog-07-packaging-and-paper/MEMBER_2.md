# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng Tâm: Snapshot Qdrant Offline, Soạn Thảo Cohort & Bảng Thẩm Định 20 Tiêu Chí PROBAST, Rà Soát PHI

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Tạo Snapshot Cơ Sở Dữ Liệu Qdrant Offline
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Đóng gói thư mục lưu trữ volume của Qdrant (`data/vector_store/`) để khi khởi chạy `docker-compose.yml`, Qdrant đã chứa sẵn 100% dữ liệu phác đồ y khoa đã được lập chỉ mục, không cần crawl hay nạp lại từ đầu.
* **Đầu ra (Deliverable):** Thư mục snapshot dữ liệu Qdrant sẵn sàng gắn volume.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Soạn Thảo Phần Cohort & Bảng Thẩm Định 20 Tiêu Chí PROBAST
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết phần *Clinical Cohort & Data Pipeline* của bài báo khoa học: Mô tả quy trình De-ID, phương pháp khóa chuỗi thời gian, tỷ lệ missing data và kỹ thuật gán MICE, phân chia theo Patient ID.
  2. Hoàn thiện văn bản Bảng Thẩm Định 20 Tiêu Chí PROBAST chi tiết: Chứng minh hệ thống M-CDSS đạt chuẩn Low Risk of Bias trên cả 4 miền (*Participants, Predictors, Outcome, Analysis*) để kẹp vào phụ lục bài báo (Supplementary Material).
* **Đầu ra (Deliverable):** Bản thảo phần Cohort và Bảng thẩm định PROBAST hoàn chỉnh.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Rà Soát Bảo Mật PHI Lần Cuối & Giấy Phép Bản Quyền
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Chạy công cụ rà quét bảo mật trên toàn bộ repository (mã nguồn, file configs, test data, git commit history) để đảm bảo tuyệt đối không có bất kỳ thông tin bệnh nhân thực nào bị rò rỉ.
  2. Hoàn thiện file `LICENSE` (MIT License) và Data Dictionary chính thức.
* **Đầu ra (Deliverable):** Chứng chỉ kiểm toán an toàn dữ liệu, file `LICENSE`.
* **Trạng thái:** `[ ] TODO`
