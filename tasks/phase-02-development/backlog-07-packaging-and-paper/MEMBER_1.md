# BACKLOG 07 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Tối Ưu GPU Runtime, Soạn Thảo Methodology & Results Bài Báo, Gắn Release Tag v1.0.0

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Tối Ưu Hóa Trọng Số Mô Hình & GPU Container
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Chuẩn hóa checkpoint suy luận gồm weights, nhiệt độ $T$, thứ tự nhãn, cấu hình, scaler/tokenizer và phiên bản thư viện cần thiết; bỏ optimizer states nhưng giữ đủ thông tin tái lập dự đoán.
  2. Kiểm tra backend container trên CPU và, nếu có NVIDIA runtime, trên GPU; ghi tài nguyên và thời gian suy luận thực tế thay vì mặc định mọi máy có GPU.
* **Đầu ra (Deliverable):** Tệp trọng số mô hình tối ưu, `Dockerfile` cho API Backend.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Soạn Thảo Phần Methodology & Results Của Bài Báo Khoa Học
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** Viết nội dung 2 phần cốt lõi của bài báo khoa học chuẩn TRIPOD-AI:
  1. *Section Methodology:* Mô hình toán học FT-Transformer, Attention Layers, Cross-Attention Late Fusion và Temperature Scaling.
  2. *Section Empirical Results:* Bảng số liệu đối chứng 3 Baselines, kết quả Ablation Study, đồ thị ECE Reliability Diagram và DCA Net Benefit.
* **Đầu ra (Deliverable):** Bản thảo phần Methods & Results.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Chuẩn Bị Release Và Rà Quyền Công Bố Weights
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Rà code/model card, nguồn dữ liệu và điều kiện giấy phép của pretrained weights; soạn release notes và danh sách artifact được phép phân phối. Chỉ gắn tag hoặc công bố weights sau khi nhóm duyệt phạm vi phát hành.
* **Đầu ra (Deliverable):** Release notes dự thảo, model card, manifest/checksum và quyết định cấp phép; tag nếu đã được duyệt.
* **Trạng thái:** `[ ] TODO`
