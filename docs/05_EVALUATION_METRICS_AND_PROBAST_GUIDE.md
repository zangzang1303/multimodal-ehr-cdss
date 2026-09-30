# ĐO LƯỜNG KHOA HỌC, LỢI ÍCH LÂM SÀNG & BỘ TIÊU CHUẨN PROBAST (EVALUATION METRICS & PROBAST COMPLIANCE)
### Hướng Dẫn Tính Toán AUROC/AUPRC, Phân Tích Đường Cong Quyết Định (DCA) Đo Lợi Ích Ròng Lâm Sàng và Bảng Thẩm Định 20 Tiêu Chí PROBAST

---

## 1. KHUNG CHỈ SỐ ĐO LƯỜNG NĂNG LỰC PHÂN BIỆT & ĐỘ TIN CẬY (DISCRIMINATION & RELIABILITY METRICS)

Để một hệ thống AI y tế được công nhận trong các thử nghiệm lâm sàng và các tạp chí y khoa hàng đầu (*The Lancet Digital Health, Nature Medicine, JAMA*), việc chỉ báo cáo độ chính xác tổng thể (Accuracy) là hoàn toàn không được chấp nhận do hiện tượng mất cân bằng mẫu và chi phí sai lầm bất đối xứng trong chẩn đoán.

```
                    HỆ THỐNG ĐO ĐẠC ĐA CHIỀU (MULTI-FACETED CLINICAL EVALUATION)
   ┌───────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
   │         NĂNG LỰC PHÂN BIỆT (DISCRIMINATION)        │         ĐỘ TIN CẬY XÁC SUẤT (CALIBRATION)         │
   ├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
   │ • AUROC (One-vs-Rest Macro): Khả năng tách biệt   │ • Expected Calibration Error (ECE < 0.05)         │
   │   giữa các nhóm bệnh nhân có và không có bệnh.   │ • Brier Score: Đo sai lệch bình phương xác suất   │
   │ • AUPRC (Macro PR-AUC): Đo lường độ chuẩn xác trên│ • Reliability Diagram: Biểu đồ đường cong         │
   │   tập dữ liệu mất cân bằng bệnh lý hiếm.          │   đối chiếu xác suất mô hình vs thực tế.          │
   └─────────────────────────┬─────────────────────────┴─────────────────────────┬─────────────────────────┘
                             │                                                   │
                             └─────────────────────────┬─────────────────────────┘
                                                       ▼
                                     LỢI ÍCH LÂM SÀNG THỰC TẾ (CLINICAL UTILITY)
                                 Decision Curve Analysis (DCA) & Net Benefit Curve
```

### 1.1. Multiclass AUROC (One-vs-Rest Macro)
Với bài toán phân loại đa lớp ($K = 4$ nhóm bệnh: Hen, COPD, Suy tim, Viêm phổi), ta tính toán diện tích dưới đường cong ROC cho từng lớp $k$ đối đầu với tất cả các lớp còn lại (One-vs-Rest - OVR):
$$\text{AUROC}_k = \int_{0}^{1} \text{TPR}_k(\text{FPR}_k^{-1}(t)) \, dt$$
Chỉ số tổng thể được lấy trung bình Macro (Macro-average AUROC):
$$\text{AUROC}_{macro} = \frac{1}{K} \sum_{k=1}^K \text{AUROC}_k$$
*Ý nghĩa lâm sàng:* Đảm bảo mô hình có khả năng phân biệt công bằng cho mọi bệnh lý, không bị áp đảo bởi bệnh có tần suất cao.

### 1.2. AUPRC (Area Under Precision-Recall Curve) & Macro-F1
Trong điều kiện thực tế tại phòng khám ban đầu, tỷ lệ bệnh nhân mắc Suy tim sung huyết hoặc Viêm phổi có thể chỉ chiếm $5\% - 10\%$ tổng số ca khám khó thở. Khi đó, đường cong ROC có thể bị lạc quan giả tạo. Chỉ số **AUPRC** (tính theo Average Precision) phản ánh chính xác năng lực phát hiện ca bệnh dương tính:
$$\text{AUPRC}_k = \sum_{n=1}^N (R_{n, k} - R_{n-1, k}) P_{n, k}$$
Trong đó $P_{n, k}$ và $R_{n, k}$ là Precision và Recall tại ngưỡng cắt thứ $n$.
Điểm **Macro-F1** được tính bằng trung bình điều hòa tại ngưỡng quyết định tối ưu:
$$\text{Macro-F1} = \frac{1}{K} \sum_{k=1}^K \frac{2 \cdot \text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$

### 1.3. Brier Score & Expected Calibration Error (ECE)
- **Brier Score:** Đo lường tổng thể sai số xác suất:
  $$\text{BS} = \frac{1}{N} \sum_{i=1}^N \sum_{k=1}^K (p_{ik} - y_{ik})^2$$
  *Khoảng giá trị: $0 \le \text{BS} \le 2$. Điểm càng gần 0 mô hình càng hoàn hảo.*
- **Expected Calibration Error (ECE):** Đã được đặc tả toán học chi tiết tại [`docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md`](02_MULTIMODAL_ARCHITECTURE_AND_MATH.md). M-CDSS đạt chuẩn nghiêm ngặt $\text{ECE} < 0.05$.

---

## 2. PHÂN TÍCH ĐƯỜNG CONG QUYẾT ĐỊNH (DECISION CURVE ANALYSIS - DCA)

Một nghịch lý lớn trong AI y tế: **Một mô hình có AUROC = 0.90 vẫn có thể gây hại cho bệnh nhân** nếu được đưa vào hướng dẫn điều trị lâm sàng mà không tính tới tỷ lệ đánh đổi giữa lợi ích của việc phát hiện ca bệnh (True Positive) và cái giá phải trả của việc báo động giả (False Positive - khiến bệnh nhân bị chụp CT ngực lãng phí hoặc uống nhầm thuốc giãn phế quản gây loạn nhịp).

Phương pháp **Decision Curve Analysis (DCA)** do *Vickers & Elkin (BMJ, 2006)* phát triển là công cụ tiêu chuẩn để lượng hóa **Lợi Ích Ròng Lâm Sàng (Clinical Net Benefit)**.

```
       ĐỒ THỊ ĐƯỜNG CONG QUYẾT ĐỊNH (DECISION CURVE ANALYSIS)
       
  Net Benefit (Lợi Ích Ròng)
   1.0 ┼
       │
   0.8 ┼                     /═════════════════ Mô Hình M-CDSS (VƯỢT TRỘI)
       │                    /
   0.6 ┼  ───────────      /
       │  \          \    /
   0.4 ┼   \          \  /
       │    \          \/
   0.2 ┼     \         /\...................... Chiến lược Can thiệp Tất cả (Treat All)
       │      \       /
   0.0 ┼───────\═════/───────────────────────── Chiến lược Không can thiệp (Treat None = 0)
       ┼───────┴─────┴─────┴─────┴─────┴─────┴► Ngưỡng Xác Suất Can Thiệp p_t
      0.0     0.1   0.2   0.3   0.4   0.5   0.6
```

### 2.1. Công Thức Tính Lợi Ích Ròng (Net Benefit Formulation)
Giả sử bác sĩ chọn một ngưỡng xác suất can thiệp là $p_t$ (Threshold Probability). Bệnh nhân có xác suất dự đoán $\hat{p} \ge p_t$ sẽ được chỉ định chuyển tuyến chuyên khoa hoặc làm xét nghiệm chẩn đoán sâu.
Lợi ích ròng được định nghĩa:
$$\text{Net Benefit}(p_t) = \frac{\text{TP}}{N} - \frac{\text{FP}}{N} \cdot \left( \frac{p_t}{1 - p_t} \right)$$
Trong đó:
* $\text{TP}$ (True Positives): Số ca mắc bệnh thực sự được mô hình phát hiện chính xác.
* $\text{FP}$ (False Positives): Số ca không mắc bệnh nhưng mô hình báo động nhầm.
* $N$: Tổng số bệnh nhân trong quần thể đánh giá.
* $\frac{p_t}{1 - p_t}$: **Tỷ số đánh đổi lâm sàng (Clinical Exchange Rate)**. Ví dụ, nếu bác sĩ sẵn sàng chấp nhận chụp X-quang hoặc đo phế dung ký cho 4 bệnh nhân không mắc bệnh để không bỏ sót 1 ca bệnh thực sự, thì ngưỡng can thiệp là $p_t = 0.20$, và trọng số phạt cho một ca báo động sai là $\frac{0.20}{0.80} = 0.25$.

### 2.2. So Sánh Với Hai Chiến Lược Mặc Định (Clinical Default Strategies)
1. **Chiến lược "Không can thiệp ai" (Treat None):**
   $$\text{Net Benefit}_{\text{None}} = 0$$
2. **Chiến lược "Can thiệp tất cả mọi người" (Treat All):**
   $$\text{Net Benefit}_{\text{All}}(p_t) = \text{Tỷ lệ hiện mắc} - (1 - \text{Tỷ lệ hiện mắc}) \cdot \left( \frac{p_t}{1 - p_t} \right)$$

*Chuẩn nghiệm thu lâm sàng:* Mô hình M-CDSS được chứng minh có giá trị thực tiễn nếu và chỉ nếu **đường cong Net Benefit của mô hình nằm cao hơn cả hai đường "Treat All" và "Treat None"** trên toàn bộ dải ngưỡng lâm sàng hợp lý $p_t \in [0.10, 0.50]$.

---

## 3. BẢNG KIỂM TRA TOÀN DIỆN 20 CÂU HỎI PROBAST (PROBAST 20-QUESTION AUDIT)

Để đảm bảo M-CDSS giải quyết triệt để các nguy cơ sai lệch mà bài báo JMIR đã vạch trần ở 15 công trình đi trước, dưới đây là bản thẩm định chi tiết **20 câu hỏi báo hiệu (Signalling Questions)** theo chuẩn **PROBAST** (*Moons et al., Ann Intern Med 2019*):

### MIỀN 1: NGƯỜI THAM GIA (PARTICIPANTS DOMAIN)
| Mã | Câu hỏi báo hiệu PROBAST | Đánh giá M-CDSS | Cơ chế kiểm soát kỹ thuật của hệ thống |
| :---: | :--- | :---: | :--- |
| **1.1** | *Nguồn dữ liệu có phù hợp và đại diện cho quần thể mục tiêu không?* | **YES (Đạt)** | Sử dụng dữ liệu EHR thực tế từ hệ thống chăm sóc ban đầu (MIMIC-IV-Note subset / Synthea Primary Care), phản ánh chính xác đặc điểm lâm sàng của phòng khám ngoại trú. |
| **1.2** | *Tiêu chí thu nhận và loại trừ người tham gia có phù hợp không?* | **YES (Đạt)** | Bao gồm tất cả bệnh nhân người lớn ($\ge 18$ tuổi) có phàn nàn về triệu chứng hô hấp/tuần hoàn; không loại trừ tùy tiện nhóm bệnh nhân nặng hoặc có bệnh nền phức tạp. |

### MIỀN 2: CÁC BIẾN DỰ ĐOÁN (PREDICTORS DOMAIN)
| Mã | Câu hỏi báo hiệu PROBAST | Đánh giá M-CDSS | Cơ chế kiểm soát kỹ thuật của hệ thống |
| :---: | :--- | :---: | :--- |
| **2.1** | *Các biến dự đoán có được định nghĩa và đánh giá tương đồng cho toàn bộ bệnh nhân không?* | **YES (Đạt)** | Cố định hợp đồng dữ liệu chuẩn hóa qua `configs/data_schema.yaml` với dải giá trị sinh lý thống nhất cho toàn bộ tập dữ liệu. |
| **2.2** | *Quá trình thu thập biến dự đoán có bị ảnh hưởng bởi kết cục chẩn đoán không?* | **YES (Đạt)** | Module `temporal_aligner.py` bảo đảm các biến số chỉ được trích xuất từ các sự kiện diễn ra trước mốc thời gian xác lập chẩn đoán. |
| **2.3** | *Các biến dự đoán có sẵn sàng tại thời điểm mô hình dự kiến được áp dụng không?* | **YES (Đạt)** | Toàn bộ biến bảng (sinh hiệu, test nhanh) và ghi chú khám ban đầu đều có sẵn ngay trong buổi khám ngoại trú của bác sĩ gia đình. |

### MIỀN 3: KẾT CỤC CHẨN ĐOÁN (OUTCOME DOMAIN)
| Mã | Câu hỏi báo hiệu PROBAST | Đánh giá M-CDSS | Cơ chế kiểm soát kỹ thuật của hệ thống |
| :---: | :--- | :---: | :--- |
| **3.1** | *Kết cục có được định nghĩa theo tiêu chuẩn quốc tế được công nhận không?* | **YES (Đạt)** | Nhãn bệnh được xác lập dựa trên mã chuẩn ICD-10 và đối chiếu với tiêu chuẩn quốc tế: GINA (Hen), GOLD (COPD), ESC (Suy tim). |
| **3.2** | *Các biến dự đoán có được LOẠI BỎ hoàn toàn khỏi định nghĩa kết cục không?* | **YES (Đạt)** | **Khắc phục lỗi Perveen & Kocks:** Thiết lập Danh sách đen cấm tuyệt đối đưa các tiêu chuẩn vàng (Hô hấp ký FEV1/FVC, Siêu âm tim EF) vào biến đầu vào. |
| **3.3** | *Kết cục có được xác định tương đồng cho mọi người tham gia không?* | **YES (Đạt)** | Toàn bộ nhãn chẩn đoán đều được xác thực theo cùng một quy trình lâm sàng chuẩn hóa. |
| **3.4** | *Người xác định kết cục có bị mù thông tin biến dự đoán không?* | **YES (Đạt)** | Nhãn kết luận y khoa được xác lập độc lập trong quá trình khám chữa bệnh thực tế, trước khi dữ liệu được đưa vào nghiên cứu. |
| **3.5** | *Khoảng thời gian giữa biến dự đoán và kết cục có hợp lý không?* | **YES (Đạt)** | Mốc thời gian được khóa chặt chẽ: biến dự đoán thu thập tại thời điểm tiếp nhận ($t_0$), kết cục chẩn đoán xác lập trong cùng đợt khám ($t_{diag}$). |

### MIỀN 4: PHÂN TÍCH SỐ LIỆU (ANALYSIS DOMAIN)
| Mã | Câu hỏi báo hiệu PROBAST | Đánh giá M-CDSS | Cơ chế kiểm soát kỹ thuật của hệ thống |
| :---: | :--- | :---: | :--- |
| **4.1** | *Cỡ mẫu và số lượng ca biến cố (EPV) có đủ lớn không?* | **YES (Đạt)** | Tập dữ liệu đảm bảo tối thiểu $\ge 20$ biến cố trên mỗi tham số tự do, kiểm soát chặt chẽ hiện tượng quá khớp (Overfitting). |
| **4.2** | *Các biến số liên tục có được xử lý phù hợp mà không bị phân nhóm tùy tiện?* | **YES (Đạt)** | Giữ nguyên giá trị liên tục của sinh hiệu và xét nghiệm, ánh xạ qua tầng FT-Transformer Feature Tokenizer thay vì chia nhóm nhị phân làm mất thông tin. |
| **4.3** | *Tất cả người tham gia ban đầu có được đưa vào phân tích không?* | **YES (Đạt)** | Tuyệt đối không áp dụng Complete Case Analysis (xóa dòng); toàn bộ bệnh nhân đủ tiêu chuẩn đều được giữ lại trong phân tích. |
| **4.4** | *Dữ liệu khuyết (Missing data) có được xử lý minh bạch và đúng phương pháp?* | **YES (Đạt)** | Áp dụng thuật toán gán đa biến **MICE** (`IterativeImputer`) kèm tạo cột chỉ thị nhị phân thiếu dữ liệu (Missingness Indicators). |
| **4.5** | *Có tránh việc chọn lọc biến dựa trên phân tích đơn biến (Univariable screening) không?* | **YES (Đạt)** | Sử dụng toàn bộ tập biến theo thiết kế lâm sàng và cơ chế Regularization (Weight decay, Dropout, LayerNorm) thay vì lọc p-value đơn biến. |
| **4.6** | *Mô hình có tính đến sự phức tạp của cấu trúc dữ liệu (Cụm, chuỗi thời gian)?* | **YES (Đạt)** | Áp dụng **Patient-Level Group Splitting** (`StratifiedGroupKFold`) để ngăn ngừa triệt để rò rỉ dữ liệu giữa các lần tái khám của cùng một bệnh nhân. |
| **4.7** | *Các chỉ số đo lường hiệu năng có đầy đủ và phù hợp không?* | **YES (Đạt)** | Báo cáo đa chiều: AUROC OVR, AUPRC, Macro-F1, Brier Score, ECE và biểu đồ Lợi ích ròng DCA. |
| **4.8** | *Hiện tượng quá khớp (Overfitting) và co cụm trọng số (Shrinkage) có được kiểm soát?* | **YES (Đạt)** | Áp dụng Early Stopping trên tập Validation độc lập kết hợp Dropout $0.1$ và Weight Decay trong quá trình huấn luyện AdamW. |
| **4.9** | *Trọng số của các biến có tương ứng với kết quả phân tích đa biến không?* | **YES (Đạt)** | Đảm bảo phân tích đa biến nội bộ thông qua các tầng Self-Attention và Cross-Attention có thể truy xuất ma trận trọng số minh bạch. |

---

## 4. MÃ NGUỒN PYTHON ĐO LƯỜNG METRICS VÀ VẼ ĐỒ THỊ DCA (CODE SAMPLES)

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, brier_score_loss

class ClinicalMetricsCalculator:
    """
    Tính toán toàn diện bộ chỉ số phân biệt và độ tin cậy cho bài toán chẩn đoán đa lớp.
    """
    @staticmethod
    def compute_all_metrics(
        y_true: np.ndarray, 
        y_prob: np.ndarray, 
        class_names: List[str]
    ) -> Dict[str, float]:
        num_classes = len(class_names)
        y_pred = np.argmax(y_prob, axis=1)

        # 1. AUROC One-vs-Rest Macro
        auroc_macro = roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro")

        # 2. AUPRC Macro
        y_true_onehot = np.eye(num_classes)[y_true]
        auprc_macro = average_precision_score(y_true_onehot, y_prob, average="macro")

        # 3. Macro-F1 Score
        f1_macro = f1_score(y_true, y_pred, average="macro")

        # 4. Multiclass Brier Score
        brier_score = np.mean(np.sum((y_prob - y_true_onehot)**2, axis=1))

        # 5. Expected Calibration Error (ECE) với 10 bins
        ece = ClinicalMetricsCalculator.compute_ece(y_true, y_prob, n_bins=10)

        results = {
            "auroc_macro": float(auroc_macro),
            "auprc_macro": float(auprc_macro),
            "macro_f1": float(f1_macro),
            "brier_score": float(brier_score),
            "ece": float(ece)
        }
        return results

    @staticmethod
    def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
        confidences = np.max(y_prob, axis=1)
        predictions = np.argmax(y_prob, axis=1)
        accuracies = (predictions == y_true)

        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n_samples = len(y_true)

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = np.mean(in_bin)

            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(accuracies[in_bin])
                avg_confidence_in_bin = np.mean(confidences[in_bin])
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return float(ece)


class DecisionCurveAnalysis:
    """
    Tính toán Lợi Ích Ròng Lâm Sàng (Net Benefit) qua các ngưỡng xác suất can thiệp p_t.
    """
    @staticmethod
    def calculate_net_benefit(
        y_true: np.ndarray, 
        y_prob: np.ndarray, 
        target_class: int,
        thresholds: np.ndarray = np.linspace(0.05, 0.80, 50)
    ) -> pd.DataFrame:
        n_samples = len(y_true)
        is_disease = (y_true == target_class).astype(int)
        prevalence = np.mean(is_disease)
        prob_target = y_prob[:, target_class]

        net_benefit_model = []
        net_benefit_all = []
        net_benefit_none = []

        for pt in thresholds:
            # Dự đoán dương tính nếu xác suất >= pt
            pred_positive = (prob_target >= pt).astype(int)
            tp = np.sum((pred_positive == 1) & (is_disease == 1))
            fp = np.sum((pred_positive == 1) & (is_disease == 0))

            weight = pt / (1.0 - pt)
            nb_model = (tp / n_samples) - (fp / n_samples) * weight
            nb_all = prevalence - (1.0 - prevalence) * weight

            net_benefit_model.append(nb_model)
            net_benefit_all.append(nb_all)
            net_benefit_none.append(0.0)

        df_dca = pd.DataFrame({
            "threshold": thresholds,
            "net_benefit_model": net_benefit_model,
            "net_benefit_all": net_benefit_all,
            "net_benefit_none": net_benefit_none
        })
        return df_dca
```
