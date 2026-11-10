# BACKLOG 04 - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
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
* **Trạng thái:** `[x] DONE` — `TabularTokenizer` và `FTTransformerEncoder` có kiểm thử shape/gradient trong `tests/test_phase2_member1.py`.

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
  4. Dùng `attention_mask` để bỏ qua padding của ghi chú; xác định rõ cách gộp đầu ra cross-attention thành $h_{cross}$ và hành vi khi thiếu một phương thức.
* **Đầu ra (Deliverable):** `src/models/multimodal_fusion.py`.
* **Trạng thái:** `[x] DONE` — `CrossAttentionFusion` xử lý padding và trường hợp thiếu text; bốn mode ablation có forward/backward test.

---

### 🔹 Nhiệm vụ 1.3: Module Hiệu Chuẩn Xác Suất (Temperature Scaling)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả:**
  1. Hiện thực `src/models/calibration.py`: Viết lớp `TemperatureScalingCalibrator`.
  2. Ràng buộc $T > 0$. Áp dụng thuật toán tối ưu L-BFGS trên Validation Set để cực tiểu hóa Cross-Entropy (NLL) Loss:
     $$\hat{p}_k = \frac{\exp(z_k / T)}{\sum_j \exp(z_j / T)}$$
  3. Khớp $T$ chỉ bằng validation logits; lưu $T$, thứ tự nhãn và cấu hình tiền xử lý cùng checkpoint. Không hiệu chỉnh bằng test.
* **Đầu ra (Deliverable):** `src/models/calibration.py`.
* **Trạng thái:** `[x] DONE` — L-BFGS khớp $T$ từ validation logits, checkpoint lưu $T$; test xác nhận NLL giảm và state round-trip.

---

### 🔹 Nhiệm vụ 1.4: Chạy Thực Nghiệm Ablation Study Toàn Diện
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả:** Chạy 4 biến thể trên cùng `data/processed_rebuilt_strict/` (khớp benchmark chính thức ngày 28/10/2026), cùng phân hoạch nguồn, seed và cách tính metric:
  1. Tabular-only (FT-Transformer).
  2. Text-only (Bio_ClinicalBERT).
  3. Concat Fusion ($h_{tab} \oplus h_{text}$).
  4. Cross-Attention Gated Fusion (Ours).
  Chọn checkpoint/siêu tham số bằng validation, giữ strict test cho lần báo cáo cuối. Nếu thêm cross-validation, tạo fold theo `source_patient_group`/`source_note_group` chỉ trong train, không đưa val/test vào fold huấn luyện. Lưu `data/checkpoints/multimodal_best.pt` và `data/ablation_results.json` với AUROC/AUPRC/F1/ECE/Brier, chênh lệch so với cả ba baseline strict và cấu hình tái lập.
* **Đầu ra (Deliverable):** `data/checkpoints/multimodal_best.pt`, `data/ablation_results.json`.
* **Trạng thái:** `[x] DONE` — `scripts/run_multimodal_ablation.py` đã chạy trên split rebuilt strict (1425/273/302), `max_length=512`, seed 42, tối đa 12 epoch với early stopping; xem `data/ablation_results.json`. Cross-attention AUROC 0.9594, ECE 0.0973 trên strict test. Backbone Bio_ClinicalBERT đóng băng ở cả bốn mode để vừa GPU; text-only ablation không tương đương baseline text đã fine-tune (AUROC 0.9735), và mô hình fusion chưa vượt baseline text này.

### Tái lập

```powershell
python scripts/run_multimodal_ablation.py --data-dir data/processed_rebuilt_strict --max-length 512 --epochs 12 --patience 4 --batch-size 16 --encoding-batch-size 4 --local-files-only
```

Checkpoint `data/checkpoints/multimodal_best.pt` chứa weights, $T$, schema, scaler, thứ tự nhãn và tên backbone; khi suy luận phải nạp riêng backbone Bio_ClinicalBERT cùng phiên bản. Đây là kết quả nghiên cứu trên dữ liệu tổng hợp/kho công khai, chưa đủ để triển khai lâm sàng.
