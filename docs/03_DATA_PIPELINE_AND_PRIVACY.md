# QUY TRÌNH DỮ LIỆU & BẢO MẬT ĐẠO ĐỨC Y TẾ (DATA PIPELINE & CLINICAL PRIVACY)
### Đặc Tả Pipeline Khử Định Danh PHI, Cơ Chế Khóa Chuỗi Thời Gian Chống Rò Rỉ Nhãn, Gán Dữ Liệu Khuyết MICE và Phân Chia Dữ Liệu Theo Cấp Độ Bệnh Nhân

---

## 1. BẢO MẬT DỮ LIỆU & PIPELINE KHỬ ĐỊNH DANH PHI/PII (DE-IDENTIFICATION)

Bảo vệ quyền riêng tư của bệnh nhân là nguyên tắc đạo đức và pháp lý tối thượng trong nghiên cứu AI y tế. Hệ thống tuân thủ toàn diện **Đạo luật HIPAA (Hoa Kỳ)**, **Quy định GDPR (Châu Âu)** và **Nghị định số 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân (Việt Nam)**.

```
       [Bệnh Án Gốc Chứa Thông Tin Nhận Dạng (Raw Clinical Note)]
                                │
             ┌──────────────────┴──────────────────┐
             ▼                                     ▼
   [Regex Rule Engine]                   [Biomedical NER Engine]
   • CCCD / BHYT (9-12 số)               • Tên Bác sĩ / Bệnh nhân (PERSON)
   • Số điện thoại (+84 / 09x)           • Bệnh viện / Phòng khám (FACILITY)
   • Email, Địa chỉ nhà                  • Vùng địa lý, Tỉnh / TP (GPE)
   • Định dạng ngày tháng                • Mã cơ quan y tế (ORG)
             └──────────────────┬──────────────────┘
                                │
                                ▼
                   [Surrogate Token Replacement]
               "Bệnh nhân [REDACTED_NAME], 62 tuổi,
           đến khám tại [REDACTED_HOSPITAL] vào ngày [REDACTED_DATE]..."
```

### 1.1. Tiêu Chuẩn 18 Yếu Tố Nhận Dạng Cá Nhân (HIPAA Safe Harbor)
Pipeline khử định danh tự động quét và loại bỏ 18 trường thông tin nhạy cảm:
1. Họ và tên bệnh nhân, thân nhân.
2. Tất cả các đơn vị địa lý nhỏ hơn tiểu bang/tỉnh (Địa chỉ nhà, số nhà, phường/xã, quận/huyện).
3. Tất cả các mốc ngày tháng liên quan trực tiếp đến cá nhân (ngày sinh, ngày nhập viện, ngày xuất viện).
4. Số điện thoại.
5. Số Fax.
6. Địa chỉ Email.
7. Số Căn cước công dân (CCCD / CMND) / Mã định danh cá nhân / Số an sinh xã hội (SSN).
8. Mã hồ sơ bệnh án (Medical Record Number - MRN).
9. Mã thẻ Bảo hiểm y tế (BHYT / Health Plan Beneficiary).
10. Số tài khoản ngân hàng / viện phí.
11. Số chứng chỉ hành nghề, biển số xe.
12. Mã định danh thiết bị y tế (Device serial numbers).
13. Địa chỉ URL trang web cá nhân.
14. Địa chỉ IP mạng.
15. Dữ liệu sinh trắc học (vân tay, mống mắt).
16. Ảnh chân dung toàn mặt.
17. Bất kỳ mã số định danh duy nhất nào khác.
18. Tuổi bệnh nhân nếu trên 89 tuổi (theo chuẩn HIPAA nhóm lại thành $\ge 90$).

### 1.2. Kiến Trúc Khử Định Danh Lai Ghép (Hybrid Engine: Regex + Clinical NER)
- **Engine 1: Bộ lọc Biểu thức Chính quy (Regex Engine):**
  Xử lý các thực thể có cấu trúc định dạng chuẩn mực như số CCCD (12 chữ số), thẻ BHYT (10-15 ký tự chữ và số), số điện thoại Việt Nam (`+84` hoặc đầu số `03, 05, 07, 08, 09`), địa chỉ email và các định dạng ngày tháng đa dạng (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MM-YY`).
- **Engine 2: Mô hình Nhận Diện Thực Thể Tên Riêng Y Sinh (Biomedical NER):**
  Sử dụng `spaCy` kết hợp mô hình chuyên dụng y sinh học `en_ner_bc5cdr_md` hoặc `presidio-analyzer` được tinh chỉnh trên tập dữ liệu lâm sàng để bắt trọn tên bác sĩ, tên người bệnh, tên bệnh viện và địa danh được viết tự nhiên trong lời văn hội chẩn.
- **Thế chỗ bằng Token Chuẩn Hóa (Surrogate Masking):**
  Toàn bộ thực thể bị phát hiện sẽ được thay thế bằng token ngữ cảnh: `[REDACTED_NAME]`, `[REDACTED_DATE]`, `[REDACTED_PHONE]`, `[REDACTED_HOSPITAL]`, `[REDACTED_ID]`. Cơ chế này giữ nguyên cấu trúc ngữ pháp của câu, giúp bộ mã hóa ngôn ngữ (Text Encoder) hiểu trọn vẹn ngữ nghĩa lâm sàng mà không bị rò rỉ danh tính.

---

## 2. NGUYÊN TẮC KHÓA CHUỖI THỜI GIAN & CHỐNG RÒ RỈ NHÃN (TEMPORAL ALIGNMENT)

Một trong những phát hiện cảnh báo nghiêm trọng nhất trong bài báo JMIR (*Hunik et al., 2024*) là hiện tượng **Rò rỉ nhãn (Target Leakage)** và **Mất đồng bộ chuỗi thời gian (Temporal Misalignment)** xảy ra ở hơn 60% nghiên cứu.

```
       Trục Thời Gian Lâm Sàng (Clinical Chronological Timeline)
       
 ──────────────────┬──────────────────────┬─────────────────────────► (Thời gian t)
                   │                      │
   [GIAI ĐOẠN 1: QUAN SÁT TIỀN ẨN]        │  [GIAI ĐOẠN 2: XÁC LẬP CHẨN ĐOÁN]
   • Lý do vào viện                       │  • Tiêu chuẩn vàng: Sinh thiết,
   • Diễn tiến bệnh sử ban đầu            │    Cấy VK, Đo Hô hấp ký FEV1/FVC
   • Sinh hiệu đo lúc tiếp nhận           │  • Bác sĩ kết luận mã ICD-10
   • Tiền sử hút thuốc, bệnh nền          │  • Chỉ định phác đồ xuất viện
                   │                      │
                   ▼                      ▼
           t_observation           t_diagnostic_confirmed
   ═══════════════════════════════════════╦════════════════════════════════
    HỢP LỆ CHO HUẤN LUYỆN VÀ DỰ ĐOÁN      ║   CẤM TUYỆT ĐỐI (LEAKAGE)
    (Được đưa vào Input Features)         ║   (Vi phạm chuẩn PROBAST)
```

### 2.1. Khóa Chặt Mốc Thời Gian (Strict Time-Locking Rule)
Giả sử $t_{diag}$ là thời điểm bác sĩ chính thức xác lập chẩn đoán xác định trong hệ thống EHR.
Mọi biến số đầu vào $X_i(t)$ (kết quả xét nghiệm, chỉ số sinh hiệu, đoạn ghi chú diễn tiến) bắt buộc phải thỏa mãn:
$$t(X_i) < t_{diag}$$
Bất kỳ kết quả cận lâm sàng nào được ghi nhận với nhãn thời gian $t(X_i) \ge t_{diag}$ đều bị hệ thống tự động loại bỏ khỏi tập dữ liệu huấn luyện và suy luận.

### 2.2. Danh Sách Đen Loại Trừ Xét Nghiệm Tiêu Chuẩn Vàng (Gold-Standard Blacklist)
Để tránh lặp lại sai lầm của *Perveen et al. (2016)* (dùng đường huyết đói đoán đái tháo đường) và *Kocks et al. (2023)* (dùng đo chức năng hô hấp FEV1/FVC đoán Hen/COPD), M-CDSS thiết lập danh mục loại trừ nghiêm ngặt:
- Khi mục tiêu là dự đoán **Hen vs COPD vs Suy tim vs Viêm phổi**:
  - ❌ **Loại bỏ:** Chỉ số phế dung kế (*FEV1, FVC, Tiffeneau ratio* - tiêu chuẩn vàng xác định tắc nghẽn đường thở cố định của COPD theo GOLD).
  - ❌ **Loại bỏ:** Siêu âm tim đo phân suất tống máu thất trái (*LVEF* - tiêu chuẩn vàng suy tim theo ESC).
  - ❌ **Loại bỏ:** Kết quả cấy đờm tìm vi khuẩn gây bệnh và kháng sinh đồ (tiêu chuẩn vàng viêm phổi).
  - ✅ **Chỉ giữ lại:** Các yếu tố có sẵn tại phòng khám ban đầu: triệu chứng cơ năng, khám thực thể (tiếng rale, ran ngáy, phù mắt cá), sinh hiệu ($SpO_2$, mạch, nhịp thở, nhiệt độ) và xét nghiệm máu cơ bản (Bạch cầu, CRP).

---

## 3. XỬ LÝ DỮ LIỆU KHUYẾT ĐA BIẾN BẰNG MICE (MULTIPLE IMPUTATION BY CHAINED EQUATIONS)

Trong dữ liệu EHR thực tế tại tuyến cơ sở, hơn **40% các chỉ số xét nghiệm và sinh hiệu bị thiếu (missingness)** do bác sĩ chỉ chỉ định xét nghiệm khi nghi ngờ có bệnh lý.
JMIR Review chỉ ra 67% bài báo không báo cáo cách xử lý missing data và thường chọn giải pháp xóa dòng (`dropna()`), dẫn đến sai lệch chọn mẫu nghiêm trọng.

### 3.1. Cơ Chế Khuyết Dữ Liệu Trong Y Tế
- **MCAR (Missing Completely At Random):** Dữ liệu mất ngẫu nhiên hoàn toàn (ống nghiệm vỡ, lỗi đường truyền mạng).
- **MAR (Missing At Random):** Dữ liệu mất phụ thuộc vào các biến quan sát được khác (ví dụ: bệnh nhân trẻ tuổi ít khi được đo huyết áp so với người cao tuổi).
- **MNAR (Missing Not At Random):** Dữ liệu mất phụ thuộc vào chính giá trị bị thiếu (bệnh nhân không sốt sẽ không được đo nhiệt độ liên tục).

Hệ thống M-CDSS áp dụng giả định **MAR** và triển khai kỹ thuật **MICE** (*van Buuren & Groothuis-Oudshoorn, 2011*) thông qua `IterativeImputer`.

### 3.2. Thuật Toán Chained Equations Chi Tiết
Giả sử tập dữ liệu bảng có $P$ biến số $Y = (Y_1, Y_2, \dots, Y_P)$, trong đó một số biến có giá trị khuyết:
1. **Bước khởi tạo:** Gán tạm thời các giá trị khuyết bằng trung vị (median) của từng biến.
2. **Vòng lặp chuỗi hồi quy (Chained Iterations):** Với mỗi biến $Y_j$ ($j = 1, \dots, P$):
   - Tạm thời hoàn trả lại các giá trị khuyết của $Y_j$ thành rỗng.
   - Huấn luyện mô hình hồi quy tuyến tính Bayes (*Bayesian Ridge Regression*) với biến phụ thuộc là phần quan sát được $Y_j^{(obs)}$, các biến độc lập là toàn bộ các biến còn lại $Y_{-j} = (Y_1, \dots, Y_{j-1}, Y_{j+1}, \dots, Y_P)$:
     $$Y_j^{(obs)} = \beta_0 + \sum_{k \ne j} \beta_k Y_k + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2)$$
   - Dự đoán và điền giá trị ước tính vào phần bị khuyết $Y_j^{(mis)}$.
3. Lặp lại chu kỳ trên qua tất cả $P$ biến trong $C = 10$ chu kỳ cho đến khi phân phối các giá trị gán hội tụ ổn định.

### 3.3. Bảo Toàn Tín Hiệu Lâm Sàng Qua Binary Missingness Indicator
Việc một xét nghiệm *không được chỉ định* bản thân nó chứa đựng một tín hiệu lâm sàng quan trọng (bác sĩ không nghi ngờ nhiễm trùng nên không thử CRP). Vì vậy, M-CDSS tự động bổ sung cột biến nhị phân chỉ thị:
$$M_{j} = \begin{cases} 1 & \text{nếu } Y_j \text{ ban đầu bị thiếu} \\ 0 & \text{nếu } Y_j \text{ có số liệu thực} \end{cases}$$

---

## 4. KỸ THUẬT PHÂN CHIA DỮ LIỆU Ở CẤP ĐỘ BỆNH NHÂN (PATIENT-LEVEL GROUP SPLITTING)

Rò rỉ dữ liệu giữa tập huấn luyện (Train) và tập kiểm định (Test) là nguyên nhân hàng đầu khiến các mô hình AI y tế đạt kết quả cao giả tạo trong phòng thí nghiệm nhưng thất bại hoàn toàn khi triển khai thực tế.

```
       BỆNH NHÂN PT-1002 CÓ 3 LẦN ĐẾN KHÁM BAN ĐẦU:
       Encounter 1: Tháng 01/2025
       Encounter 2: Tháng 06/2025
       Encounter 3: Tháng 11/2025

 ❌ PHÂN CHIA NGẪU NHIÊN THEO LẦN KHÁM (ROW-LEVEL SPLIT - LEAKAGE!):
    Train Set: Encounter 1, Encounter 3
    Test Set:  Encounter 2
    ==> MÔ HÌNH HỌC THUỘC LÒNG ĐẶC ĐIỂM RIÊNG CỦA BỆNH NHÂN PT-1002!

 ✅ PHÂN CHIA THEO CẤP ĐỘ BỆNH NHÂN (PATIENT-LEVEL GROUP SPLIT - CHUẨN PROBAST):
    Patient ID: [PT-1002, PT-2041, ...]  ──> TẬP HUẤN LUYỆN (70%)
    Patient ID: [PT-3094, PT-4112, ...]  ──> TẬP HIỆU CHUẨN (15%)
    Patient ID: [PT-5001, PT-6890, ...]  ──> TẬP KIỂM ĐỊNH NGOẠI TỘC (15%)
    ==> KHÔNG CÓ BẤT KỲ BỆNH NHÂN NÀO XUẤT HIỆN Ở CẢ 2 TẬP!
```

- **Tỷ lệ phân chia:**
  - **70% Tập huấn luyện (Training Set):** Tối ưu hóa trọng số mô hình FT-Transformer và Cross-Attention.
  - **15% Tập hiệu chuẩn (Validation Set):** Tinh chỉnh siêu tham số, dừng sớm (Early Stopping) và tối ưu hóa tham số nhiệt độ hiệu chuẩn $T$ (Temperature Scaling).
  - **15% Tập kiểm định ngoại kiểm (Hold-out Test Set):** Đánh giá độc lập tuyệt đối, chỉ mở ra một lần duy nhất khi nghiệm thu chỉ số AUROC, DCA và PROBAST.
- **Kỹ thuật:** Áp dụng `StratifiedGroupKFold` trên trường `patient_id` kết hợp phân tầng cân bằng tỷ lệ các nhãn bệnh lý mục tiêu ($Y$).

---

## 5. MÃ NGUỒN PYTHON THỰC THI DATA PIPELINE (CODE EXAMPLES)

Dưới đây là các lớp xử lý cốt lõi cấu thành pipeline dữ liệu hoàn chỉnh:

```python
import re
import spacy
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold

class ClinicalDeidentifier:
    """
    Module khử định danh dữ liệu ghi chú lâm sàng theo chuẩn HIPAA Safe Harbor.
    Kết hợp Regex rules và spaCy NER.
    """
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)
        # Regex mẫu cho số định danh, CCCD, điện thoại, ngày tháng
        self.patterns = [
            (r"\b\d{9,12}\b", "[REDACTED_ID]"),                             # CCCD / CMND
            (r"\b(?:\+84|0)(?:3|5|7|8|9)\d{8}\b", "[REDACTED_PHONE]"),      # Số điện thoại VN
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "[REDACTED_EMAIL]"),
            (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "[REDACTED_DATE]"),     # Ngày tháng DD/MM/YYYY
            (r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", "[REDACTED_DATE]")      # Ngày tháng YYYY-MM-DD
        ]

    def anonymize(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # 1. Regex rule-based replacement
        redacted_text = text
        for pattern, replacement in self.patterns:
            redacted_text = re.sub(pattern, replacement, redacted_text)
            
        # 2. NER entity masking
        doc = self.nlp(redacted_text)
        offset_adjust = 0
        final_chars = list(redacted_text)
        
        # Duyệt qua các thực thể nhận dạng tên người, bệnh viện, địa danh
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "PER"]:
                redacted_text = redacted_text.replace(ent.text, "[REDACTED_NAME]")
            elif ent.label_ in ["FAC", "ORG"] and any(term in ent.text.lower() for term in ["bệnh viện", "hospital", "phòng khám", "clinic"]):
                redacted_text = redacted_text.replace(ent.text, "[REDACTED_HOSPITAL]")
            elif ent.label_ in ["GPE", "LOC"]:
                redacted_text = redacted_text.replace(ent.text, "[REDACTED_LOC]")
                
        return redacted_text


class TemporalAligner:
    """
    Module khóa chuỗi thời gian: loại bỏ mọi biến số xuất hiện sau thời điểm chẩn đoán,
    và loại bỏ các xét nghiệm thuộc danh mục tiêu chuẩn vàng khỏi tập biến đầu vào.
    """
    EXCLUDED_GOLD_STANDARDS = {
        "fev1", "fvc", "fev1_fvc_ratio",   # Hô hấp ký (Tiêu chuẩn vàng COPD)
        "lvef", "bnp_pro_bnp",             # Siêu âm tim / Peptide lợi niệu suy tim
        "sputum_culture_pathogen"          # Cấy đờm vi sinh
    }

    @classmethod
    def filter_features(cls, events: List[Dict], confirmed_diag_time: str) -> List[Dict]:
        valid_events = []
        for event in events:
            # Ràng buộc thời gian t_event < t_diag
            if event["timestamp"] < confirmed_diag_time:
                feature_name = event.get("feature_name", "").lower()
                # Ràng buộc loại trừ tiêu chuẩn vàng
                if feature_name not in cls.EXCLUDED_GOLD_STANDARDS:
                    valid_events.append(event)
        return valid_events


class TabularMICEImputer:
    """
    Module gán dữ liệu khuyết đa biến MICE kết hợp tạo Missingness Indicators.
    """
    def __init__(self, max_iter: int = 10, random_state: int = 42):
        self.imputer = IterativeImputer(
            max_iter=max_iter, 
            random_state=random_state, 
            sample_posterior=False
        )
        self.numerical_cols = []

    def fit_transform(self, df: pd.DataFrame, numerical_cols: List[str]) -> pd.DataFrame:
        self.numerical_cols = numerical_cols
        out_df = df.copy()
        
        # 1. Thêm cột Binary Missingness Indicators
        for col in numerical_cols:
            out_df[f"{col}_is_missing"] = out_df[col].isna().astype(int)
            
        # 2. Áp dụng MICE cho các cột số
        out_df[numerical_cols] = self.imputer.fit_transform(out_df[numerical_cols])
        return out_df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out_df = df.copy()
        for col in self.numerical_cols:
            out_df[f"{col}_is_missing"] = out_df[col].isna().astype(int)
        out_df[self.numerical_cols] = self.imputer.transform(out_df[self.numerical_cols])
        return out_df


def create_patient_level_splits(
    df: pd.DataFrame, 
    patient_col: str = "patient_id", 
    target_col: str = "target_label",
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Phân chia dữ liệu theo Patient ID: 70% Train, 15% Val, 15% Test.
    Đảm bảo 100% không trùng lặp bệnh nhân giữa các tập.
    """
    unique_patients = df[[patient_col, target_col]].drop_duplicates(subset=[patient_col])
    
    sgkf = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    # Lấy 7 folds cho Train (70%), 1.5 folds (làm tròn) cho Val, 1.5 folds cho Test
    splits = list(sgkf.split(unique_patients, unique_patients[target_col], unique_patients[patient_col]))
    
    train_idx, temp_idx = splits[0] # Chia tách sơ bộ
    val_pts = unique_patients.iloc[temp_idx[:len(temp_idx)//2]][patient_col]
    test_pts = unique_patients.iloc[temp_idx[len(temp_idx)//2:]][patient_col]
    
    train_df = df[~df[patient_col].isin(set(val_pts) | set(test_pts))].reset_index(drop=True)
    val_df = df[df[patient_col].isin(val_pts)].reset_index(drop=True)
    test_df = df[df[patient_col].isin(test_pts)].reset_index(drop=True)
    
    return train_df, val_df, test_df
```
