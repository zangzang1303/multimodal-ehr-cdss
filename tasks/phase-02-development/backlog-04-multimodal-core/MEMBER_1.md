# BACKLOG 02 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: FT-Transformer Encoder, Mạng Cross-Attention Late Fusion, Temperature Scaling & Ablation Study

---

## 1. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Hiện Thực FT-Transformer Encoder (`src/models/tabular_encoder.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:** 
  1. Viết lớp `TabularTokenizer`:
     - Ánh xạ $M_{num}$ biến liên tục: $e_j^{(num)} = x_j \cdot w_j + b_j \in \mathbb{R}^d$ ($d=128$).
     - Ánh xạ $M_{cat}$ biến phân loại qua `nn.Embedding`.
     - Ghép vector `[CLS]` token vào đầu chuỗi: $E_0 \in \mathbb{R}^{(M+1) \times d}$.
  2. Viết lớp `FTTransformerEncoder`: Truyền $E_0$ qua 4 tầng Transformer Encoder (Multi-Head Self-Attention + LayerNorm + FFN).
* **Tiêu chuẩn nghiệm thu:** Tensor đầu ra có shape `[Batch, M+1, 128]`.
* **Đầu ra (Deliverable):** `src/models/tabular_encoder.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Hiện Thực Mạng Cross-Attention Late Fusion (`src/models/multimodal_fusion.py`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Viết lớp `CrossAttentionFusion(nn.Module)`:
     - Query: $Q_{tab} = H_{tab} W_Q \in \mathbb{R}^{(M+1) \times d}$.
     - Key/Value: $K_{text} = H_{text} W_K$, $V_{text} = H_{text} W_V \in \mathbb{R}^{(S+2) \times d}$.
     - Scaled Dot-Product Attention: $A = \text{softmax}(Q K^T / \sqrt{d}) V$.
  2. Cổng Gated Residual Fusion:
     - $g = \sigma(W_g [h_{tab}^{cls} \,\|\, h_{cross}] + b_g) \in (0, 1)^d$.
     - $h_{fused} = g \odot h_{tab}^{cls} + (1 - g) \odot h_{cross}$.
  3. Classification Head: Linear projection $h_{fused} \rightarrow 4$ logits.
* **Đầu ra (Deliverable):** `src/models/multimodal_fusion.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Module Hiệu Chuẩn Xác Suất (Temperature Scaling)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Hiện thực `src/models/calibration.py`: Viết lớp `TemperatureScalingCalibrator`.
  2. Ràng buộc $T > 0$. Áp dụng thuật toán tối ưu L-BFGS trên Validation Set để cực tiểu hóa Cross-Entropy (NLL) Loss:
     $$\hat{p}_k = \frac{\exp(z_k / T)}{\sum_j \exp(z_j / T)}$$
  3. Lưu tham số $T$ trực tiếp vào checkpoint của mô hình.
* **Đầu ra (Deliverable):** `src/models/calibration.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.4: Chạy Thực Nghiệm Ablation Study Toàn Diện
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Chạy 4 biến thể mô hình qua 5-Fold Cross Validation:
  1. Tabular-only (FT-Transformer).
  2. Text-only (Bio_ClinicalBERT).
  3. Concat Fusion ($h_{tab} \oplus h_{text}$).
  4. Cross-Attention Gated Fusion (Ours).
  Lưu checkpoint tốt nhất vào `data/checkpoints/multimodal_best.pt` và bảng so sánh vào `data/ablation_results.json`.
* **Đầu ra (Deliverable):** `data/checkpoints/multimodal_best.pt`, `data/ablation_results.json`.
* **Trạng thái:** `[ ] TODO`
