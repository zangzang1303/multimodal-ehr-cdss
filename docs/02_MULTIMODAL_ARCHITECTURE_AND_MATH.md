# KIẾN TRÚC MẠNG ĐA PHƯƠNG THỨC & NỀN TẢNG TOÁN HỌC (MULTIMODAL ARCHITECTURE & MATHEMATICS)
### Đặc Tả Toán Học FT-Transformer, Clinical Text Encoder, Cross-Attention Late Fusion và Thuật Toán Hiệu Chuẩn Xác Suất Temperature Scaling

---

## 1. TỔNG QUAN KIẾN TRÚC TOÀN CẢNH (SYSTEM MATHEMATICAL TOPOLOGY)

Kiến trúc mạng của **M-CDSS** được xây dựng trên nguyên lý **Multimodal Late Fusion with Cross-Attention Interaction**. Hệ thống tiếp nhận đồng thời hai luồng dữ liệu dị thể:
1. Vector đặc trưng bảng số học $\mathbf{x}_{tab} = [\mathbf{x}^{(num)}, \mathbf{x}^{(cat)}]$.
2. Chuỗi văn bản ghi chú lâm sàng tự do $\mathbf{s}_{text} = (w_1, w_2, \dots, w_S)$.

```
   [Numerical & Categorical EHR]               [Clinical Free-Text Note]
                 │                                         │
        ┌────────▼────────┐                       ┌────────▼────────┐
        │Feature Tokenizer│                       │  Biomedical LLM │
        │   & Embeddings  │                       │    Tokenizer    │
        └────────┬────────┘                       └────────┬────────┘
                 │ E_0 ∈ R^(M+1) x d                       │
        ┌────────▼────────┐                       ┌────────▼────────┐
        │  FT-Transformer │                       │  BioLinkBERT /  │
        │ Encoder Layers  │                       │ ClinicalBERT Enc│
        └────────┬────────┘                       └────────┬────────┘
                 │ H_tab ∈ R^(M+1) x d                     │ H_text ∈ R^(S+1) x d
                 └──────────────┐           ┌──────────────┘
                                │           │
                                ▼           ▼
                        ┌───────────────────────────┐
                        │   CROSS-ATTENTION FUSION  │
                        │ Q = H_tab * W_Q           │
                        │ K = H_text * W_K          │
                        │ V = H_text * W_V          │
                        │ Residual Gated Mechanism  │
                        └─────────────┬─────────────┘
                                      │ h_fused ∈ R^d
                               ┌──────▼──────┐
                               │ Linear Head │
                               └──────┬──────┘
                                      │ Logits z ∈ R^K
                               ┌──────▼──────┐
                               │ Temperature │
                               │   Scaling   │ (Validation NLL Optimized)
                               └──────┬──────┘
                                      │
                                      ▼
                        Calibrated Probabilities p*
                             (ECE < 0.05)
```

---

## 2. NHÁNH MÃ HÓA DỮ LIỆU BẢNG: FT-TRANSFORMER (FEATURE TOKENIZER TRANSFORMER)

Kiến trúc **FT-Transformer** (*Gorishniy et al., NeurIPS 2021*) chuyển đổi dữ liệu dạng bảng từ không gian rời rạc/liên tục sang không gian embedding ngữ nghĩa liên tục tương tự như các token trong NLP, giúp mô hình hóa các mối quan hệ tương tác bậc cao (*high-order feature interactions*) giữa các chỉ số xét nghiệm và sinh hiệu.

### 2.1. Feature Tokenization Layer
Giả sử bệnh nhân có $M_{num}$ biến định lượng liên tục (tuổi, huyết áp, nhịp tim, $SpO_2$, nhiệt độ, bạch cầu, CRP...) và $M_{cat}$ biến định tính phân loại (giới tính, tiền sử hút thuốc, tăng huyết áp, đái tháo đường...).
Tổng số đặc trưng: $M = M_{num} + M_{cat}$.

#### Đối với biến liên tục (Numerical Features):
Mỗi biến liên tục $x_j^{(num)} \in \mathbb{R}$ ($j \in \{1, \dots, M_{num}\}$) được ánh xạ tuyến tính vào không gian embedding chiều $d$:
$$e_j^{(num)} = x_j^{(num)} \cdot \mathbf{w}_j^{(num)} + \mathbf{b}_j^{(num)} \in \mathbb{R}^d$$
Trong đó:
* $\mathbf{w}_j^{(num)} \in \mathbb{R}^d$ là vector trọng số có thể học riêng biệt cho biến thứ $j$.
* $\mathbf{b}_j^{(num)} \in \mathbb{R}^d$ là vector độ lệch (bias).

#### Đối với biến phân loại (Categorical Features):
Mỗi biến phân loại $x_k^{(cat)} \in \{1, 2, \dots, C_k\}$ ($k \in \{1, \dots, M_{cat}\}$) được ánh xạ thông qua ma trận Lookup Table:
$$e_k^{(cat)} = \mathbf{E}_k[x_k^{(cat)}] + \mathbf{b}_k^{(cat)} \in \mathbb{R}^d$$
Trong đó $\mathbf{E}_k \in \mathbb{R}^{C_k \times d}$ là từ điển nhúng riêng của biến phân loại thứ $k$.

#### Khởi tạo chuỗi Token và [CLS] Token:
Một vector học được đặc biệt $\mathbf{e}_{cls} \in \mathbb{R}^d$ được ghép vào đầu chuỗi đặc trưng:
$$\mathbf{E}_0 = \begin{bmatrix} \mathbf{e}_{cls} \\ e_1^{(num)} \\ \vdots \\ e_{M_{num}}^{(num)} \\ e_1^{(cat)} \\ \vdots \\ e_{M_{cat}}^{(cat)} \end{bmatrix} \in \mathbb{R}^{(M+1) \times d}$$

### 2.2. Transformer Encoder Layers
Ma trận embedding $\mathbf{E}_0$ được truyền qua $L$ tầng Transformer Encoder. Mỗi tầng thứ $l \in \{1, \dots, L\}$ bao gồm:
1. **Multi-Head Self-Attention (MHSA):**
   $$\mathbf{Q} = \mathbf{E}_{l-1} \mathbf{W}_Q^{(l)}, \quad \mathbf{K} = \mathbf{E}_{l-1} \mathbf{W}_K^{(l)}, \quad \mathbf{V} = \mathbf{E}_{l-1} \mathbf{W}_V^{(l)}$$
   $$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q} \mathbf{K}^T}{\sqrt{d_k}}\right) \mathbf{V}$$
   $$\tilde{\mathbf{E}}_{l-1} = \mathbf{E}_{l-1} + \text{Dropout}\left(\text{MHSA}(\text{LayerNorm}(\mathbf{E}_{l-1}))\right)$$

2. **Feed-Forward Network (FFN):**
   $$\text{FFN}(\mathbf{u}) = \text{Linear}_2\left(\text{GeLU}(\text{Linear}_1(\mathbf{u}))\right)$$
   $$\mathbf{E}_l = \tilde{\mathbf{E}}_{l-1} + \text{Dropout}\left(\text{FFN}(\text{LayerNorm}(\tilde{\mathbf{E}}_{l-1}))\right)$$

Sau $L$ tầng, ta thu được ma trận biểu diễn bảng $\mathbf{H}_{tab} = \mathbf{E}_L \in \mathbb{R}^{(M+1) \times d}$. Vector đại diện tổng hợp của dữ liệu bảng là token đầu tiên:
$$\mathbf{h}_{tab}^{cls} = \mathbf{H}_{tab}[0] \in \mathbb{R}^d$$

---

## 3. NHÁNH MÃ HÓA VĂN BẢN: CLINICAL TEXT ENCODER

Văn bản ghi chú lâm sàng $\mathbf{s}_{text}$ chứa đựng các mô tả bệnh sử, tiền căn, lý do vào viện và triệu chứng thực thể.

### 3.1. Tokenization & Biomedical Embedding
Văn bản được phân rã thành chuỗi $S$ subwords thông qua bộ tokenizer chuyên biệt cho y tế (WordPiece / Byte-Pair Encoding):
$$\mathbf{s}_{text} \xrightarrow{\text{Tokenizer}} (\text{[CLS]}, w_1, w_2, \dots, w_S, \text{[SEP]})$$

Chuỗi token được đưa qua mạng nơ-ron tiền huấn luyện trên hàng triệu bài báo PubMed và hồ sơ lâm sàng MIMIC: **BioLinkBERT** (*Yasunaga et al., 2022*) hoặc **Bio_ClinicalBERT** (*Alsentzer et al., 2019*).

### 3.2. Không Gian Biểu Diễn Ngữ Tự (Contextual Token Representations)
Đầu ra từ tầng ẩn cuối cùng của Text Encoder là ma trận ngữ cảnh:
$$\mathbf{T}_{text} \in \mathbb{R}^{(S+2) \times d_{text}}$$
Để đồng bộ chiều không gian với nhánh bảng, ta áp dụng ma trận chiếu tuyến tính $\mathbf{W}_{proj} \in \mathbb{R}^{d_{text} \times d}$:
$$\mathbf{H}_{text} = \mathbf{T}_{text} \mathbf{W}_{proj} \in \mathbb{R}^{(S+2) \times d}$$
Vector đại diện toàn diện của văn bản:
$$\mathbf{h}_{text}^{cls} = \mathbf{H}_{text}[0] \in \mathbb{R}^d$$

---

## 4. TẦNG DUNG HỢP LIÊN PHƯƠNG THỨC TRỄ (CROSS-ATTENTION LATE FUSION)

Thay vì chỉ nối ghép đơn giản hai vector ($\mathbf{h}_{tab} \oplus \mathbf{h}_{text}$ - Concat Fusion) vốn bỏ qua tương tác ngữ nghĩa giữa các số liệu xét nghiệm và triệu chứng cơ năng, M-CDSS áp dụng **Cross-Attention Mechanism**.

```
                Cross-Attention: Tabular Query -> Text Key/Value
                
  Tabular Tokens (H_tab) ──> [ Linear W_Q ] ──> Query (Q_tab)
                                                      │
                                                      ├──> [ MatMul & Scale 1/√d ] ──> [ Softmax ]
                                                      │                                     │
  Text Tokens (H_text)   ──> [ Linear W_K ] ──> Key (K_text)                                │
  Text Tokens (H_text)   ──> [ Linear W_V ] ──> Value (V_text) ───────────────────────────> MatMul
                                                                                            │
                                                                                            ▼
                                                                                   Context Vector A_tab2text
```

### 4.1. Công Thức Tính Cross-Attention
Ta sử dụng biểu diễn bảng $\mathbf{H}_{tab}$ đóng vai trò là **Query** ($Q$) để "truy vấn" các triệu chứng lâm sàng giải thích tương ứng trong văn bản $\mathbf{H}_{text}$ (**Key** $K$ và **Value** $V$):

1. **Phép chiếu ma trận (Linear Projections):**
   $$\mathbf{Q}_{tab} = \mathbf{H}_{tab} \mathbf{W}_Q^{(cross)} \in \mathbb{R}^{(M+1) \times d}$$
   $$\mathbf{K}_{text} = \mathbf{H}_{text} \mathbf{W}_K^{(cross)} \in \mathbb{R}^{(S+2) \times d}$$
   $$\mathbf{V}_{text} = \mathbf{H}_{text} \mathbf{W}_V^{(cross)} \in \mathbb{R}^{(S+2) \times d}$$

2. **Ma trận Trọng số Chú ý Liên phương thức (Cross-Attention Weights):**
   $$\mathbf{A} = \text{softmax}\left( \frac{\mathbf{Q}_{tab} \mathbf{K}_{text}^T}{\sqrt{d}} \right) \in \mathbb{R}^{(M+1) \times (S+2)}$$
   *Ý nghĩa lâm sàng:* Phần tử $A_{ij}$ biểu thị mức độ liên kết giữa chỉ số sinh hiệu/xét nghiệm thứ $i$ (ví dụ: $SpO_2$) với từ vựng thứ $j$ trong bệnh án (ví dụ: *"khó thở kịch phát về đêm"*).

3. **Tổng hợp Ngữ cảnh (Context Aggregation):**
   $$\mathbf{C}_{tab} = \mathbf{A} \mathbf{V}_{text} \in \mathbb{R}^{(M+1) \times d}$$

### 4.2. Cơ Chế Gated Residual Fusion (Cổng Dung Hợp Thích Ứng)
Để tránh việc văn bản tự do lấn át các chỉ số xét nghiệm định lượng khách quan (hoặc ngược lại khi xét nghiệm bị thiếu), hệ thống áp dụng cơ chế Cổng Gated Fusion:
$$\mathbf{h}_{cross} = \mathbf{C}_{tab}[0] \in \mathbb{R}^d \quad (\text{Context vector ứng với [CLS] token})$$
$$\mathbf{g} = \sigma\left( \mathbf{W}_g [\mathbf{h}_{tab}^{cls} \,\|\, \mathbf{h}_{cross}] + \mathbf{b}_g \right) \in \mathbb{R}^d$$
$$\mathbf{h}_{fused} = \mathbf{g} \odot \mathbf{h}_{tab}^{cls} + (\mathbf{1} - \mathbf{g}) \odot \mathbf{h}_{cross} \in \mathbb{R}^d$$
Trong đó:
* $\sigma(\cdot)$ là hàm sigmoid.
* $\odot$ là tích Hadamard (element-wise product).
* $\mathbf{g} \in (0, 1)^d$ đóng vai trò trọng số điều tiết động giữa dữ liệu số và dữ liệu văn bản.

### 4.3. Classification Head & Logits
Vector dung hợp cuối cùng $\mathbf{h}_{fused}$ được đưa qua bộ phân loại đa lớp:
$$\mathbf{z} = \mathbf{W}_{out} \mathbf{h}_{fused} + \mathbf{b}_{out} \in \mathbb{R}^K$$
Với $K = 4$ tương ứng với 4 nhóm bệnh: **Hen phế quản, COPD, Suy tim sung huyết, Viêm phổi cộng đồng**.

---

## 5. TOÁN HỌC HIỆU CHUẨN XÁC SUẤT LÂM SÀNG (PROBABILITY CALIBRATION)

Trong y khoa, một mô hình dự đoán có độ phân biệt tốt (AUROC cao) nhưng xác suất không chuẩn hóa sẽ gây nguy hại lớn. Nếu mô hình đưa ra điểm số $p = 0.95$ nhưng trong 100 bệnh nhân nhận điểm $0.95$ chỉ có 50 người thực sự mắc bệnh, bác sĩ sẽ chỉ định quá mức các can thiệp xâm lấn hoặc kháng sinh mạnh.

### 5.1. Thuật Toán Temperature Scaling
**Temperature Scaling** (*Guo et al., ICML 2017*) là phương pháp hiệu chuẩn đơn tham số hậu nghiệm (*post-processing parametric calibration*) bảo toàn thứ tự xếp hạng của Logits (giữ nguyên AUROC) nhưng điều chỉnh độ dốc xác suất tiệm cận phân phối thực tế.

Với vector logits $\mathbf{z} \in \mathbb{R}^K$, phân phối xác suất đã hiệu chuẩn $\hat{\mathbf{p}}$ được tính bởi:
$$\hat{p}_k(T) = \frac{\exp(z_k / T)}{\sum_{j=1}^K \exp(z_j / T)}, \quad \forall k \in \{1, \dots, K\}$$
Trong đó $T > 0$ là **Nhiệt độ (Temperature parameter)**:
* Khi $T = 1$: Xác suất tương đương Softmax thông thường.
* Khi $T > 1$: Phân phối xác suất được "làm mềm" (softened), giảm bớt sự tự tin thái quá (overconfidence).
* Khi $T < 1$: Phân phối xác suất trở nên nhọn hơn.

#### Hàm Tối Ưu Nhiệt Độ $T$:
Tham số $T$ được tối ưu hóa độc lập trên tập Validation (không động chạm tới tập Train hay Test) bằng cách cực tiểu hóa hàm Mất mát Entropy chéo (Negative Log-Likelihood - NLL):
$$\min_{T > 0} \; \mathcal{L}_{NLL}(T) = - \frac{1}{N_{val}} \sum_{i=1}^{N_{val}} \sum_{k=1}^K y_{ik} \log \hat{p}_{ik}(T)$$

---

### 5.2. Công Thức Định Nghĩa Chỉ Số Hiệu Chuẩn: ECE, MCE và Brier Score

#### 1. Expected Calibration Error (ECE - Sai Số Hiệu Chuẩn Kỳ Vọng):
Chia dải xác suất dự đoán $[0, 1]$ thành $B$ khoảng (bins) đều nhau, ví dụ $B = 10$: $I_b = \left( \frac{b-1}{B}, \frac{b}{B} \right]$.
Gọi $B_b$ là tập hợp các mẫu có xác suất dự đoán cao nhất thuộc khoảng $I_b$:
* **Độ chính xác thực tế trong bin $b$ (Accuracy):**
  $$\text{acc}(B_b) = \frac{1}{|B_b|} \sum_{i \in B_b} \mathbf{1}(\hat{y}_i = y_i)$$
* **Độ tự tin trung bình trong bin $b$ (Confidence):**
  $$\text{conf}(B_b) = \frac{1}{|B_b|} \sum_{i \in B_b} \hat{p}_i$$

Chỉ số **ECE** được định nghĩa bằng tổng chênh lệch tuyệt đối có trọng số:
$$\text{ECE} = \sum_{b=1}^B \frac{|B_b|}{N} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$
*Tiêu chuẩn nghiệm thu của M-CDSS: $\text{ECE} < 0.05$ (tức sai lệch xác suất dưới 5%).*

#### 2. Maximum Calibration Error (MCE - Sai Số Hiệu Chuẩn Tối Đa):
Đo lường sai lệch tệ nhất trong các bin rủi ro cao:
$$\text{MCE} = \max_{b \in \{1, \dots, B\}} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

#### 3. Brier Score:
Đo lường sai số bình phương trung bình giữa xác suất dự đoán và nhãn thực tế:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N \sum_{k=1}^K (p_{ik} - y_{ik})^2$$
*Giá trị Brier Score càng nhỏ (tiệm cận 0), chất lượng dự đoán xác suất càng hoàn hảo.*

---

## 6. MÃ NGUỒN THAM CHIẾU PYTORCH (REFERENCE IMPLEMENTATION)

Dưới đây là khối mã nguồn mẫu thực thi tầng **CrossAttentionFusion** và **TemperatureScalingCalibrator**:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple

class CrossAttentionFusion(nn.Module):
    """
    Tầng Cross-Attention Late Fusion giữa Tabular Stream và Text Stream.
    Query: Tabular representation (M+1 tokens x D)
    Key/Value: Text representation (S+2 tokens x D)
    """
    def __init__(self, embed_dim: int = 128, num_heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        
        # Multi-Head Cross Attention
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=embed_dim, 
            num_heads=num_heads, 
            dropout=dropout, 
            batch_first=True
        )
        self.layer_norm_q = nn.LayerNorm(embed_dim)
        self.layer_norm_kv = nn.LayerNorm(embed_dim)
        
        # Gated fusion projection: g = sigmoid(W * [h_tab; h_cross] + b)
        self.gate_proj = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.Sigmoid()
        )
        self.dropout = nn.Dropout(dropout)
        self.post_norm = nn.LayerNorm(embed_dim)

    def forward(
        self, 
        h_tab: torch.Tensor, 
        h_text: torch.Tensor,
        text_padding_mask: torch.Tensor = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        h_tab: [Batch, M+1, D]
        h_text: [Batch, S+2, D]
        text_padding_mask: [Batch, S+2] (True nếu là padding)
        Returns:
            h_fused: [Batch, D]
            attn_weights: [Batch, M+1, S+2]
        """
        q = self.layer_norm_q(h_tab)
        kv = self.layer_norm_kv(h_text)
        
        # Attention output: [Batch, M+1, D]
        attn_out, attn_weights = self.cross_attn(
            query=q, 
            key=kv, 
            value=kv, 
            key_padding_mask=text_padding_mask
        )
        
        # Trích xuất biểu diễn tại vị trí [CLS] (token index 0)
        h_tab_cls = h_tab[:, 0, :]        # [Batch, D]
        h_cross_cls = attn_out[:, 0, :]   # [Batch, D]
        
        # Tính toán Gating dynamic weight
        gate = self.gate_proj(torch.cat([h_tab_cls, h_cross_cls], dim=-1)) # [Batch, D]
        h_fused = gate * h_tab_cls + (1.0 - gate) * h_cross_cls
        h_fused = self.post_norm(self.dropout(h_fused))
        
        return h_fused, attn_weights


class TemperatureScalingCalibrator(nn.Module):
    """
    Module hiệu chuẩn xác suất bằng Temperature Scaling tối ưu NLL trên Validation Set.
    """
    def __init__(self):
        super().__init__()
        # Tham số T khởi tạo bằng 1.0, ràng buộc T > 0
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Chia logits cho nhiệt độ T và áp dụng Softmax
        """
        temperature = torch.clamp(self.temperature, min=0.01)
        return F.softmax(logits / temperature, dim=-1)

    def fit(self, val_logits: torch.Tensor, val_labels: torch.Tensor, lr: float = 0.01, max_iter: int = 100):
        """
        Tối ưu hóa T bằng thuật toán L-BFGS để cực tiểu hóa NLL
        """
        nll_criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)

        def eval_step():
            optimizer.zero_grad()
            temp = torch.clamp(self.temperature, min=0.01)
            scaled_logits = val_logits / temp
            loss = nll_criterion(scaled_logits, val_labels)
            loss.backward()
            return loss

        optimizer.step(eval_step)
        print(f"Optimal Temperature calibrated: T = {self.temperature.item():.4f}")
```
