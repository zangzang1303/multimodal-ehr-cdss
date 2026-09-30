# BACKLOG 01 (TUẦN 1) - NHIỆM VỤ THÀNH VIÊN 1 (LEAD ML / MODELING)
### Trọng Tâm: Chuẩn Hóa Môi Trường AI, Kiểm Tra CUDA, Cấu Hình Siêu Tham Số 3 Baselines & Khảo Sát Kiến Trúc

---

## 1. BỐI CẢNH & MỤC TIÊU
Trong Tuần 1 của Giai đoạn 1, Thành viên 1 chịu trách nhiệm thiết lập nền tảng tính toán Machine Learning / Deep Learning, đảm bảo hệ thống nhận diện đúng GPU CUDA, xây dựng tệp cấu hình siêu tham số tập trung `configs/model_config.yaml` cho 3 Baseline và nghiên cứu chuẩn bị mã nguồn tham chiếu cho FT-Transformer và Text Tokenizer.

---

## 2. DANH SÁCH NHIỆM VỤ CHI TIẾT (ACTIONABLE TASKS)

### 🔹 Nhiệm vụ 1.1: Thiết Lập Môi Trường Tính Toán & Kiểm Tra CUDA GPU
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  1. Kiểm tra và bổ sung các gói phụ thuộc cần thiết vào `requirements.txt`:
     - PyTorch ecosystem: `torch>=2.2.0`, `torchvision`, `torchaudio`.
     - Modeling & ML: `transformers>=4.38.0`, `scikit-learn>=1.4.0`, `xgboost>=2.0.0`, `catboost>=1.2.0`, `optuna>=3.5.0`.
     - Data processing: `pandas>=2.2.0`, `numpy>=1.26.0`, `pyarrow>=15.0.0`.
     - Utilities: `pyyaml>=6.0`, `tqdm>=4.66.0`.
  2. Viết script `scripts/verify_env.py` kiểm tra:
     - Phiên bản Python ($\ge 3.10$).
     - PyTorch có nhận diện CUDA hay không (`torch.cuda.is_available()`).
     - Tên GPU, dung lượng VRAM, phiên bản CUDA runtime.
     - Kiểm tra import thành công tất cả các thư viện trọng yếu.
* **Lệnh thực thi & kiểm thử:**
  ```bash
  pip install -r requirements.txt
  python scripts/verify_env.py
  ```
* **Đầu ra (Deliverables):**
  - Tệp `requirements.txt` cập nhật.
  - Script `scripts/verify_env.py`.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.2: Thiết Kế Tệp Cấu Hình Siêu Tham Số Tập Trung (`configs/model_config.yaml`)
* **Độ ưu tiên:** `[P0 - Blocker]`
* **Mô tả chi tiết:**
  Tạo tệp `configs/model_config.yaml` định nghĩa toàn bộ siêu tham số cho 3 Baselines trong Giai đoạn 1:
  1. **Baseline 1 (Classical Tabular ML - XGBoost & CatBoost):**
     - `random_forest`: `n_estimators: 200`, `max_depth: 12`, `random_state: 42`.
     - `xgboost`: `n_estimators: 300`, `max_depth: 6`, `learning_rate: 0.05`, `subsample: 0.8`, `colsample_bytree: 0.8`, `eval_metric: "mlogloss"`.
     - `catboost`: `iterations: 300`, `depth: 6`, `learning_rate: 0.05`, `random_seed: 42`.
  2. **Baseline 2 (Tabular Deep Learning - FT-Transformer):**
     - `d_token`: 128 (chiều vector nhúng của từng feature).
     - `n_blocks`: 4 (số tầng Transformer Encoder).
     - `attention_n_heads`: 4.
     - `attention_dropout`: 0.1.
     - `ffn_dropout`: 0.1.
     - `ffn_d_hidden`: 256.
     - `learning_rate`: 0.0001, `weight_decay`: 0.00001, `batch_size`: 64.
  3. **Baseline 3 (Clinical NLP - Bio_ClinicalBERT):**
     - `pretrained_model_name`: `"emilyalsentzer/Bio_ClinicalBERT"` (hoặc `"michiyasunaga/BioLinkBERT-base"`).
     - `max_seq_length`: 512.
     - `dropout_rate`: 0.2.
     - `learning_rate`: 0.00002, `batch_size`: 16, `epochs`: 5.
  4. **Training Common Config:**
     - `seed`: 42.
     - `early_stopping_patience`: 5.
     - `num_classes`: 4.
* **Đầu ra (Deliverables):**
  - Tệp `configs/model_config.yaml` hoàn chỉnh.
* **Trạng thái:** `[ ] TODO`

---

### 🔹 Nhiệm vụ 1.3: Khảo Sát Kiến Trúc Tham Chiếu & Chuẩn Bị Tokenizer
* **Độ ưu tiên:** `[P1 - Critical]`
* **Mô tả chi tiết:**
  1. Nghiên cứu cơ chế mã hóa đặc trưng bảng số của FT-Transformer (*Gorishniy et al., NeurIPS 2021*):
     - Biến số liên tục qua phép chiếu affine: $e_j^{(num)} = x_j \cdot w_j + b_j \in \mathbb{R}^D$.
     - Biến phân loại qua bảng tra cứu Embedding: $e_j^{(cat)} = \mathbf{E}_j[c_j] \in \mathbb{R}^D$.
  2. Viết đoạn mã kiểm thử tải `AutoTokenizer` từ HuggingFace cho mô hình `emilyalsentzer/Bio_ClinicalBERT` để đảm bảo tải được cache model về máy mà không bị nghẽn mạng:
     ```python
     from transformers import AutoTokenizer
     tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
     print("Tokenizer loaded successfully! Vocab size:", tokenizer.vocab_size)
     ```
* **Đầu ra (Deliverables):**
  - Script test tokenizer hoặc ghi chú kiến trúc tại `docs/notes_tabular_encoder.md`.
* **Trạng thái:** `[ ] TODO`

---

## 3. TIÊU CHUẨN NGHIỆM THU CỦA THÀNH VIÊN 1 (ACCEPTANCE CRITERIA)
- [ ] Chạy `python scripts/verify_env.py` xuất ra trạng thái CUDA hợp lệ và không báo lỗi thiếu thư viện.
- [ ] Tệp `configs/model_config.yaml` được đọc thành công bằng `yaml.safe_load(open('configs/model_config.yaml'))` mà không có lỗi cú pháp.
- [ ] Tải được HuggingFace Tokenizer về cache cục bộ.
- [ ] Bàn giao `configs/model_config.yaml` cho Thành viên 2 và Thành viên 3.

---

## 4. TÀI LIỆU THAM KHẢO CHUYÊN MÔN DÀNH CHO THÀNH VIÊN 1
1. **Kiến trúc mạng dạng bảng FT-Transformer:**
   - *Gorishniy, Y., Rubachev, A., Khrulkov, V., & Babenko, A. (2021).* "Revisiting Deep Learning Models for Tabular Data." *NeurIPS 2021*. [arXiv:2106.11959](https://arxiv.org/abs/2106.11959).
   - *Trọng tâm cần đọc:* Mục 3.2 (Feature Tokenizer) và Bảng siêu tham số chuẩn ($d_{token}=128, n_{blocks}=4, heads=4, dropout=0.1$).
2. **Mô hình Ngôn ngữ Y sinh Bio_ClinicalBERT:**
   - *Alsentzer, E. et al. (2019).* "Publicly Available Clinical BERT Embeddings." *NAACL Workshop on Clinical NLP*. [arXiv:1904.03323](https://arxiv.org/abs/1904.03323).
   - *Trọng tâm cần đọc:* Cách tokenization các từ viết tắt lâm sàng và độ dài ngữ cảnh `max_seq_length=512`.
   - *Mô hình HuggingFace:* [`emilyalsentzer/Bio_ClinicalBERT`](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT).
3. **Cẩm nang kỹ thuật của dự án:**
   - Đọc chi tiết tại: [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md) (Mục 2.1 và Mục 2.7).

