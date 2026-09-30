# BACKLOG 05 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Tối Ưu GPU Runtime, Soạn Thảo Methodology & Results Bài Báo, Gắn Release Tag v1.0.0

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Tối Ưu Hóa Trọng Số Mô Hình & GPU Container
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:**
  1. Dọn dẹp và chuẩn hóa tệp checkpoint cuối cùng `data/checkpoints/multimodal_best.pt` (chỉ giữ lại model weights và nhiệt độ $T$, loại bỏ optimizer states để giảm dung lượng file xuống tối thiểu).
  2. Cấu hình PyTorch GPU runtime trong `Dockerfile` cho Backend API, bảo đảm container nhận diện được card đồ họa NVIDIA.
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

### 🔹 Nhiệm vụ 1.3: Gắn Release Tag & Công Bố Weights
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Rà soát lại toàn bộ code tầng model, dọn dẹp các script thử nghiệm tạm thời, gắn release tag `v1.0.0` trên git và soạn thảo release notes.
* **Đầu ra (Deliverable):** Git Tag `v1.0.0`, Release Notes chính thức.
* **Trạng thái:** `[ ] TODO`
