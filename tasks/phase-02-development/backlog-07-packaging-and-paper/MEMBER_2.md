# BACKLOG 07 - NHIỆM VỤ THÀNH VIÊN 2 (DATA ENGINEER & PRIVACY)
### Trọng tâm: snapshot Qdrant, cohort, PROBAST+AI, PHI và quyền sử dụng dữ liệu

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 2.1: Tạo Snapshot Cơ Sở Dữ Liệu Qdrant Offline
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Tạo snapshot/manifest từ tài liệu phác đồ đã kiểm nguồn và quyền phân phối; ghi phiên bản Qdrant, embedding model, checksum và hướng dẫn restore. Không đưa phác đồ có bản quyền lên Git khi chưa được phép.
* **Đầu ra (Deliverable):** Snapshot hợp lệ hoặc script ingest tái lập từ nguồn được phép, manifest và hướng dẫn restore.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.2: Soạn Thảo Cohort & Đánh Giá PROBAST+AI
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết phần *Clinical Cohort & Data Pipeline* của bài báo khoa học: Mô tả quy trình De-ID, phương pháp khóa chuỗi thời gian, tỷ lệ missing data và kỹ thuật gán MICE, phân chia theo Patient ID.
  2. Dùng PROBAST+AI phù hợp loại nghiên cứu; ghi từng miền, câu hỏi áp dụng, bằng chứng và đánh giá nguy cơ sai lệch/tính áp dụng, kể cả mức cao hoặc chưa rõ. Không khẳng định Low Risk khi thiếu bằng chứng.
* **Đầu ra (Deliverable):** Bản thảo Cohort và bảng PROBAST+AI có giải trình, nêu rõ dữ liệu tổng hợp và giới hạn ngoại kiểm.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 2.3: Rà Soát Bảo Mật PHI Lần Cuối & Giấy Phép Bản Quyền
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Rà mã nguồn, cấu hình, dữ liệu mẫu và lịch sử Git để tìm PHI/secret; lập báo cáo phạm vi, phát hiện và cách xử lý. Không gọi kết quả rà quét là bảo đảm tuyệt đối hoặc chứng chỉ độc lập.
  2. Hoàn thiện Data Dictionary; chỉ chọn MIT cho phần mã do nhóm có quyền cấp phép, ghi riêng giấy phép dữ liệu, phác đồ và pretrained models.
* **Đầu ra (Deliverable):** Báo cáo rà soát và khắc phục, Data Dictionary, LICENSE/NOTICE phù hợp.
* **Trạng thái:** `[ ] TODO`
