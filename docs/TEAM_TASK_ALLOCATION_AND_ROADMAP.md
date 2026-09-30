# KẾ HOẠCH PHÂN CHIA NHIỆM VỤ CHI TIẾT THEO TUẦN CHO NHÓM 3 THÀNH VIÊN
### Hệ Thống Hỗ Trợ Ra Quyết Định Chẩn Đoán Đa Phương Thức (Multimodal EHR-CDSS)
**Lộ trình phát triển 16 tuần (5 giai đoạn) chuẩn TRIPOD-AI & PROBAST**

---

## 1. PHÂN CHIA VAI TRÒ & TRÁCH NHIỆM CỐT LÕI (ROLE ASSIGNMENTS)

Để dự án vận hành trơn tru như một nhóm nghiên cứu công nghệ y tế (Medical AI Lab) chuyên nghiệp, 3 thành viên sẽ đảm nhận 3 vị trí chuyên trách với sự phối hợp chặt chẽ:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CƠ CẤU NHÂN SỰ DỰ ÁN (3 THÀNH VIÊN)                          │
├────────────────────────────────┬────────────────────────────────┬──────────────────────────────┤
│  THÀNH VIÊN 1: LEAD ML/DL     │  THÀNH VIÊN 2: DATA & PRIVACY  │  THÀNH VIÊN 3: FULL-STACK AI │
│  (Deep Learning & Modeling)    │  (Biomedical Data Engineer)    │  (Backend, Agent & Frontend) │
├────────────────────────────────┼────────────────────────────────┼──────────────────────────────┤
│ • Kiến trúc FT-Transformer     │ • Pipeline Khử định danh PHI   │ • Thiết kế luồng Multi-Agent │
│ • Fine-tune Clinical Text LLM  │ • Khóa thời gian Temporal Sync │ • Thuật toán Evidence Ground │
│ • Mạng Cross-Attention Fusion  │ • Gán khuyết đa biến MICE      │ • FastAPI REST API Backend   │
│ • Hiệu chuẩn Temperature Scale │ • Patient-level Group Split    │ • Next.js 14 Clinician UI    │
│ • Benchmark Baselines          │ • Vector DB & Guideline Ingest │ • Docker Compose & DevOps    │
└────────────────────────────────┴────────────────────────────────┴──────────────────────────────┘
```

---

## 2. LỘ TRÌNH 16 TUẦN CHI TIẾT TỪNG THÀNH VIÊN (WEEK-BY-WEEK BREAKDOWN)

### GIAI ĐOẠN 1: DỮ LIỆU, KHỬ ĐỊNH DANH & BENCHMARK BASELINES (TUẦN 1 – TUẦN 3)

#### 🎯 TUẦN 1: Thiết Lập Môi Trường, Data Schema & Thu Thập Dữ Liệu
* **Mục tiêu chung:** Chuẩn hóa toàn bộ môi trường lập trình, cấu trúc repository và nạp dữ liệu thô.
* **Thành viên 1 (Lead ML):**
  - Thiết lập Git repository, cấu hình `requirements.txt`, thiết lập quy chuẩn code formatting (`black`, `flake8`).
  - Viết `configs/model_config.yaml` quy định siêu tham số cho Tabular Model, Text Model và Fusion Layer.
  - Nghiên cứu mã nguồn tham chiếu FT-Transformer (*Gorishniy et al.*).
  - *Đầu ra:* `requirements.txt`, `configs/model_config.yaml`, script kiểm tra CUDA GPU sẵn sàng.
* **Thành viên 2 (Data Engineer):**
  - Xây dựng hợp đồng dữ liệu `configs/data_schema.yaml` (9 biến số liên tục, 4 biến phân loại, dải sinh lý bình thường, 4 nhãn bệnh).
  - Thu thập hoặc sinh tập dữ liệu bán tổng hợp lâm sàng (MIMIC-IV-Note subset hoặc Synthea Multimodal EHR) gồm bảng số và file văn bản ghi chú tương ứng.
  - Lưu trữ dữ liệu thô an toàn tại `data/raw/` (cấu hình `.gitignore` không đẩy dữ liệu thô lên git).
  - *Đầu ra:* `configs/data_schema.yaml`, `data/raw/patients_raw.parquet`, `data/raw/clinical_notes_raw.jsonl`.
* **Thành viên 3 (Full-stack AI):**
  - Khởi tạo khung dự án Next.js 14 tại thư mục `frontend/` (cài đặt TailwindCSS, Lucide-react, Shadcn UI).
  - Thiết lập khung FastAPI tại `src/api/` với cấu trúc routes và kiểm tra endpoint `GET /health`.
  - Viết `Dockerfile` nền tảng cho backend và frontend.
  - *Đầu ra:* Khung frontend chạy được `npm run dev`, khung backend chạy được `uvicorn src.api.main:app`.

---

#### 🎯 TUẦN 2: Bảo Mật De-ID, Khóa Chuỗi Thời Gian (Temporal Sync) & Xử Lý Dữ Liệu Khuyết MICE
* **Mục tiêu chung:** Xây dựng Data Pipeline hoàn chỉnh, loại bỏ 100% rủi ro rò rỉ nhãn theo chuẩn PROBAST.
* **Thành viên 1 (Lead ML):**
  - Viết module khung cho 3 mô hình đối chứng tại `src/models/baselines.py`: `ClassicalTabularBaseline` (Random Forest, XGBoost, CatBoost).
  - Viết khung pipeline huấn luyện và grid search siêu tham số bằng Optuna.
  - *Đầu ra:* Lớp `ClassicalTabularBaseline` trong `src/models/baselines.py`.
* **Thành viên 2 (Data Engineer):**
  - Xây dựng `src/data_pipeline/deidentifier.py`: Tích hợp Regex phát hiện CCCD, SĐT, Email kết hợp spaCy NER (`en_core_web_sm`) thay thế bằng `[REDACTED_*]`.
  - Xây dựng `src/data_pipeline/temporal_aligner.py`: Khóa chuỗi thời gian $t_{event} < t_{diag}$, thiết lập Danh sách đen loại trừ Hô hấp ký FEV1/FVC, Siêu âm tim EF khỏi input.
  - Xây dựng `src/data_pipeline/imputer.py`: Áp dụng MICE (`IterativeImputer`) cho biến số và tạo cột binary missingness indicators.
  - *Đầu ra:* `src/data_pipeline/deidentifier.py`, `temporal_aligner.py`, `imputer.py`.
* **Thành viên 3 (Full-stack AI):**
  - Viết bộ Unit Test `tests/test_data_pipeline.py`: Kiểm tra tính năng che dấu thông tin cá nhân của deidentifier, kiểm tra không có sự kiện nào sau mốc $t_{diag}$ lọt qua `temporal_aligner`.
  - Xây dựng Pydantic Schemas sơ bộ tại `src/api/schemas.py` cho yêu cầu dự đoán lâm sàng.
  - *Đầu ra:* `tests/test_data_pipeline.py` (chạy lệnh `pytest tests/test_data_pipeline.py` pass 100%).

---

#### 🎯 TUẦN 3: Patient-Level Splitting & Benchmark Hệ Thống 3 Baselines
* **Mục tiêu chung:** Hoàn tất tập dữ liệu chuẩn hóa và huấn luyện xong 3 mô hình nền tảng đối chứng.
* **Thành viên 1 (Lead ML):**
  - Hoàn thiện script `scripts/run_baselines.py`:
    + Huấn luyện Baseline 1: XGBoost / Random Forest trên dữ liệu bảng.
    + Huấn luyện Baseline 2: TabNet hoặc FT-Transformer chỉ dùng dữ liệu bảng.
    + Huấn luyện Baseline 3: Classifier dùng Text Embeddings từ BioLinkBERT/ClinicalBERT.
  - Ghi nhận kết quả benchmark ban đầu và lưu vào `data/baseline_results.json`.
  - *Đầu ra:* `scripts/run_baselines.py`, `data/baseline_results.json`.
* **Thành viên 2 (Data Engineer):**
  - Viết hàm `create_patient_level_splits` trong `src/data_pipeline/dataset_loader.py` áp dụng `StratifiedGroupKFold` theo `patient_id` (tỷ lệ 70% Train, 15% Val, 15% Test).
  - Xuất các file dữ liệu sạch: `data/processed/train.parquet`, `data/processed/val.parquet`, `data/processed/test.parquet`.
  - Viết `PyTorch Dataset` và `DataLoader` trả về đồng thời `(tabular_tensor, input_ids, attention_mask, labels)`.
  - *Đầu ra:* 3 tập dữ liệu trong `data/processed/`, lớp `MultimodalEHRDataset` sẵn sàng cho PyTorch.
* **Thành viên 3 (Full-stack AI):**
  - Thiết kế màn hình giao diện nhập liệu lâm sàng ban đầu trên Next.js: Component `PatientDataForm.tsx` (form 2 cột: bên trái nhập sinh hiệu/xét nghiệm số, bên phải textarea paste bệnh án).
  - Tích hợp gọi API thử nghiệm tới backend.
  - *Đầu ra:* Giao diện `PatientDataForm.tsx` trên Next.js hiển thị tương tác mượt mà.

---

### GIAI ĐOẠN 2: PHÁT TRIỂN MẠNG MULTIMODAL AI CORE & HIỆU CHUẨN XÁC SUẤT (TUẦN 4 – TUẦN 7)

#### 🎯 TUẦN 4: Xây Dựng FT-Transformer & Clinical Text Encoder
* **Mục tiêu chung:** Hoàn thành độc lập hai nhánh mã hóa (Tabular Stream & Text Stream).
* **Thành viên 1 (Lead ML):**
  - Hiện thực `src/models/tabular_encoder.py`: Xây dựng `TabularTokenizer` biến đổi biến liên tục ($e_j^{(num)} = x_j \cdot w_j + b_j$) và biến phân loại qua Embedding Lookup, tích hợp các tầng Transformer Encoder với LayerNorm và MHSA.
  - Kiểm tra tensor shape đầu ra: `[Batch_Size, M+1, D]`.
  - *Đầu ra:* `src/models/tabular_encoder.py`.
* **Thành viên 2 (Data Engineer):**
  - Hiện thực `src/models/text_encoder.py`: Tích hợp HuggingFace `AutoModel` tải `emilyalsentzer/Bio_ClinicalBERT` hoặc `michiyasunaga/BioLinkBERT-base`.
  - Viết hàm chiếu tuyến tính đồng bộ chiều không gian $D_{text} \rightarrow D$ (`W_proj`).
  - Chuẩn bị pipeline fine-tuning nhẹ bằng LoRA / PEFT nếu cần thiết.
  - *Đầu ra:* `src/models/text_encoder.py`.
* **Thành viên 3 (Full-stack AI):**
  - Thiết kế Mock API endpoint `/api/v1/predict/multimodal` trên FastAPI để Frontend có thể phát triển giao diện hiển thị kết quả chẩn đoán sớm.
  - Xây dựng component `DiagnosticCard.tsx` trên Next.js (thanh đo phần trăm xác suất kèm màu cảnh báo theo mức độ rủi ro).
  - *Đầu ra:* Mock endpoint FastAPI, UI Component `DiagnosticCard.tsx`.

---

#### 🎯 TUẦN 5: Tích Hợp Mạng Cross-Attention Late Fusion
* **Mục tiêu chung:** Hợp nhất hai luồng biểu diễn qua cơ chế tương tác đa phương thức Cross-Attention.
* **Thành viên 1 (Lead ML):**
  - Hiện thực `CrossAttentionFusion` trong `src/models/multimodal_fusion.py`:
    + Tabular làm Query ($Q_{tab} \in \mathbb{R}^{(M+1) \times D}$).
    + Text làm Key & Value ($K_{text}, V_{text} \in \mathbb{R}^{(S+2) \times D}$).
    + Tính toán ma trận Attention Weights: $\text{softmax}(Q K^T / \sqrt{D}) V$.
    + Tích hợp Cổng Gated Residual Fusion: $\mathbf{g} = \sigma(W_g [\mathbf{h}_{tab}^{cls} \,\|\, \mathbf{h}_{cross}] + b_g)$.
  - Xây dựng Classification Head xuất ra 4 Logits tương ứng 4 bệnh.
  - *Đầu ra:* `src/models/multimodal_fusion.py`.
* **Thành viên 2 (Data Engineer):**
  - Xây dựng vòng lặp huấn luyện trong `scripts/train_multimodal.py`: Hỗ trợ tối ưu hóa AdamW, điều chỉnh Learning Rate Schedule (Cosine Annealing), tính toán loss qua CrossEntropy và lưu Best Checkpoint dựa trên Validation Loss.
  - Hỗ trợ Mixed Precision (`torch.cuda.amp.autocast`) để tối ưu tốc độ trên GPU.
  - *Đầu ra:* `scripts/train_multimodal.py`.
* **Thành viên 3 (Full-stack AI):**
  - Viết bộ Unit Test `tests/test_multimodal_model.py`: Kiểm thử forward pass với dữ liệu giả lập, kiểm tra kích thước tensor output và bảo đảm gradient lan truyền ngược (backward pass) bình thường không bị NaN/Inf.
  - *Đầu ra:* `tests/test_multimodal_model.py` (pass 100%).

---

#### 🎯 TUẦN 6: Module Hiệu Chuẩn Xác Suất (Probability Calibration)
* **Mục tiêu chung:** Đưa Expected Calibration Error (ECE) của mô hình về dưới ngưỡng $0.05$.
* **Thành viên 1 (Lead ML):**
  - Hiện thực `src/models/calibration.py`: Xây dựng thuật toán **Temperature Scaling** tối ưu tham số nhiệt độ $T$ trên Validation Set bằng phương pháp L-BFGS cực tiểu hóa NLL.
  - Bổ sung tùy chọn Isotonic Regression / Platt Scaling cho từng lớp bệnh.
  - Tích hợp tham số $T$ trực tiếp vào checkpoint của mô hình.
  - *Đầu ra:* `src/models/calibration.py`, hàm `calibrate_model(model, val_loader)`.
* **Thành viên 2 (Data Engineer):**
  - Viết module tính toán ECE, MCE và Brier Score trong `src/evaluation/metrics.py`.
  - Đo đạc chỉ số ECE trước và sau khi hiệu chuẩn trên tập Test Set, xuất biểu đồ Reliability Diagram (đường cong độ tin cậy) lưu vào `data/calibration_curve.png`.
  - *Đầu ra:* `data/calibration_curve.png`, chứng minh $ECE_{post} < 0.05$.
* **Thành viên 3 (Full-stack AI):**
  - Cập nhật Pydantic Schema `PredictionResult` với trường `calibrated: bool` và `calibration_temperature: float`.
  - Nâng cấp giao diện `DiagnosticCard.tsx` hiển thị nhãn xác thực *"Calibrated Clinical Probability"* với tooltip giải thích ý nghĩa cho bác sĩ.
  - *Đầu ra:* Cập nhật API schema và giao diện UI hiển thị xác suất đã hiệu chuẩn.

---

#### 🎯 TUẦN 7: Thực Hiện Nghiên Cứu Triệt Tiêu Toàn Diện (Comprehensive Ablation Study)
* **Mục tiêu chung:** Thu thập bằng chứng thực nghiệm khoa học chứng minh tính vượt trội của Cross-Attention Fusion.
* **Thành viên 1 (Lead ML):**
  - Thực hiện chạy thực nghiệm 4 cấu hình Ablation:
    1. *Tabular-only (FT-Transformer)*
    2. *Text-only (BioLinkBERT)*
    3. *Simple Concat Fusion ($h_{tab} \oplus h_{text}$)*
    4. *Cross-Attention Gated Fusion (Ours)*
  - Lập bảng so sánh AUROC, Macro-F1, AUPRC qua 5 lần chạy (5-fold cross validation).
  - *Đầu ra:* Báo cáo kết quả Ablation Study, lưu trọng số mô hình tốt nhất vào `data/checkpoints/multimodal_best.pt`.
* **Thành viên 2 (Data Engineer):**
  - Kiểm tra tính ổn định của mô hình trên các phân nhóm nhân khẩu học (Subgroup Analysis: nhóm tuổi $<65$ vs $\ge 65$, Nam vs Nữ) để đảm bảo không có thiên lệch thuật toán (Fairness Check).
  - Bắt đầu thu thập các tài liệu Hướng dẫn Chẩn đoán điều trị chuẩn (GINA 2024, GOLD 2024, ESC 2023, Bộ Y tế) đưa vào `data/guidelines/`.
  - *Đầu ra:* `data/guidelines/*.md` hoặc `*.pdf`, báo cáo phân tích công bằng thuật toán.
* **Thành viên 3 (Full-stack AI):**
  - Xây dựng trang `Benchmark & Ablation Dashboard` trên giao diện Next.js, hiển thị biểu đồ radar và bảng so sánh động giữa các biến thể mô hình.
  - *Đầu ra:* Trang `/evaluation` trên Frontend.

---

### GIAI ĐOẠN 3: AGENTIC RAG, EXPLAINABILITY & PHẦN MỀM HOÀN CHỈNH (TUẦN 8 – TUẦN 10)

#### 🎯 TUẦN 8: Cơ Sở Dữ Liệu Vector & Hybrid Retriever Phác Đồ Y Khoa
* **Mục tiêu chung:** Xây dựng kho tri thức y khoa chuẩn hóa và công cụ tìm kiếm ngữ nghĩa cho Agent.
* **Thành viên 1 (Lead ML):**
  - Lựa chọn và đánh giá mô hình nhúng văn bản y sinh (*Embedding Model*): `sentence-transformers/all-mpnet-base-v2` hoặc `pritamdeka/BioBERT-mnli`.
  - Kiểm thử độ chính xác truy xuất (Recall@k, MRR) trên bộ câu hỏi triệu chứng đối chiếu phác đồ.
  - *Đầu ra:* Cấu hình `configs/rag_config.yaml`.
* **Thành viên 2 (Data Engineer):**
  - Hiện thực `src/agent/knowledge_ingest.py`: Đọc các phác đồ trong `data/guidelines/`, thực hiện phân mảnh theo cấu trúc y khoa (*Hierarchical Clinical Chunking*: Phân biệt rõ Tiêu chuẩn chẩn đoán, Yếu tố loại trừ, Dấu hiệu cờ đỏ, Điều trị ban đầu).
  - Cài đặt và khởi tạo Qdrant Vector Database (chạy qua Docker local), lưu vector cùng metadata chi tiết vào collection `clinical_guidelines`.
  - *Đầu ra:* `src/agent/knowledge_ingest.py`, Qdrant Vector Store sẵn sàng hoạt động.
* **Thành viên 3 (Full-stack AI):**
  - Hiện thực `src/agent/retriever.py`: Xây dựng cơ chế tìm kiếm lai (Hybrid Search kết hợp Cosine Similarity từ Vector Qdrant và lọc từ khóa BM25).
  - Viết component `GuidelineDrawer.tsx` trên Frontend (cho phép bác sĩ trượt mở drawer xem chi tiết đoạn phác đồ gốc được trích dẫn).
  - *Đầu ra:* `src/agent/retriever.py`, Component `GuidelineDrawer.tsx`.

---

#### 🎯 TUẦN 9: Multi-Agent Chẩn Đoán Phân Biệt & Evidence Grounder (Triệt Tiêu Ảo Giác)
* **Mục tiêu chung:** Xây dựng bộ não lập luận lâm sàng có trích dẫn ký tự chính xác từ bệnh án gốc.
* **Thành viên 1 (Lead ML):**
  - Thiết kế Prompt System và Chain-of-Thought (CoT) chuyên sâu cho `DiagnosticAgent`: Buộc LLM đóng vai trò Chuyên gia Hội chẩn phân tích đối kháng 2 chiều (bằng chứng ủng hộ Top-1, bằng chứng hướng về Top-2, tiêu chuẩn loại trừ, cảnh báo cấp cứu).
  - Tối ưu hóa cấu trúc JSON đầu ra nghiêm ngặt (*Constrained JSON Decoding*).
  - *Đầu ra:* Module logic cốt lõi trong `src/agent/diagnostic_agent.py`.
* **Thành viên 2 (Data Engineer):**
  - Hiện thực `src/agent/evidence_grounder.py`: Thuật toán tìm kiếm chuỗi ký tự (Exact match & Fuzzy sliding window) đối chiếu các câu trích dẫn của LLM với văn bản bệnh án gốc.
  - Trả về danh sách chính xác vị trí `[start_char, end_char]` trong chuỗi gốc; tự động loại bỏ các câu lập luận bịa đặt không có căn cứ (Anti-hallucination filter).
  - *Đầu ra:* `src/agent/evidence_grounder.py`.
* **Thành viên 3 (Full-stack AI):**
  - Hiện thực Component `EvidenceViewer.tsx` trên Next.js: Nhận văn bản bệnh án gốc kèm mảng offsets, tự động làm sáng (highlight) các câu văn chứng cứ bằng dải màu phân biệt (vàng cho triệu chứng ủng hộ, đỏ cho dấu hiệu nguy hiểm).
  - Viết `tests/test_agent_rag.py` kiểm tra: 100% các câu quote được hiển thị đều map đúng chuỗi ký tự trong văn bản.
  - *Đầu ra:* `EvidenceViewer.tsx`, `tests/test_agent_rag.py` (pass 100%).

---

#### 🎯 TUẦN 10: Tích Hợp Toàn Bộ REST API Backend & Hoàn Thiện Web Dashboard
* **Mục tiêu chung:** Kết nối thông suốt Backend FastAPI với Frontend Next.js.
* **Thành viên 1 (Lead ML):**
  - Tối ưu hóa Inference Pipeline: Nạp mô hình `multimodal_best.pt` vào bộ nhớ GPU một lần duy nhất lúc khởi động FastAPI (Lifespan event), đảm bảo thời gian suy luận dưới 150ms/ca bệnh.
  - Viết endpoint `POST /api/v1/predict/multimodal`.
  - *Đầu ra:* `src/api/routes/inference.py`.
* **Thành viên 2 (Data Engineer):**
  - Viết endpoint `POST /api/v1/agent/explain`: Tiếp nhận ID bệnh nhân, kích hoạt luồng Agentic RAG và trả về cấu trúc phân tích kèm Evidence Spans và Guideline sources.
  - Xây dựng database lưu trữ lịch sử chẩn đoán (SQLite/PostgreSQL nhẹ).
  - *Đầu ra:* `src/api/routes/agent_chat.py`.
* **Thành viên 3 (Full-stack AI):**
  - Hoàn thiện `src/api/main.py` với CORS, Middleware logging thời gian đáp ứng (latency), xử lý ngoại lệ chuẩn RESTful.
  - Nối toàn bộ UI trên Next.js với Backend qua `src/lib/api.ts`: Bác sĩ nhập liệu $\rightarrow$ Bấm "Phân Tích Chẩn Đoán" $\rightarrow$ Hiển thị tức thì Card xác suất + Highlight bệnh án + Drawer phác đồ.
  - *Đầu ra:* `src/api/main.py`, Giao diện Web App hoạt động hoàn chỉnh từ đầu đến cuối.

---

### GIAI ĐOẠN 4: ĐO LƯỜNG KHOA HỌC, LỢI ÍCH LÂM SÀNG & NGOẠI KIỂM (TUẦN 11 – TUẦN 13)

#### 🎯 TUẦN 11: Đo Đạc Đa Chiều Các Chỉ Số Khoa Học (AUROC, AUPRC, F1, Brier)
* **Mục tiêu chung:** Thực hiện đo lường định lượng toàn diện trên tập Hold-out Test độc lập.
* **Thành viên 1 (Lead ML):**
  - Hoàn thiện module `src/evaluation/metrics.py`: Tính toán Multiclass AUROC (One-vs-Rest Macro), AUPRC Macro, Macro-F1, Sensitivity, Specificity, Brier Score.
  - So sánh chi tiết hiệu năng giữa mô hình Multimodal Fusion và 3 Baselines.
  - *Đầu ra:* Báo cáo số liệu thực nghiệm hoàn chỉnh, bảng kết quả định lượng.
* **Thành viên 2 (Data Engineer):**
  - Xuất báo cáo ma trận nhầm lẫn (Confusion Matrix) cho từng bệnh lý.
  - Phân tích các ca dự đoán sai (Error Analysis): Xác định các ca bệnh giáp ranh phức tạp (ví dụ: Chồng lấp Hen-COPD có kèm suy tim nhẹ) để cung cấp ngữ cảnh phân tích cho báo cáo khoa học.
  - *Đầu ra:* `data/confusion_matrix.png`, tài liệu phân tích ca bệnh sai biệt.
* **Thành viên 3 (Full-stack AI):**
  - Xây dựng endpoint `GET /api/v1/evaluation/benchmark` xuất kết quả đo lường dưới dạng JSON cho hệ thống.
  - Viết `tests/test_api_endpoints.py` kiểm tra toàn bộ mã HTTP status, cấu trúc payload và latency của mọi route API.
  - *Đầu ra:* `src/api/routes/evaluation_routes.py`, `tests/test_api_endpoints.py`.

---

#### 🎯 TUẦN 12: Phân Tích Đường Cong Quyết Định (DCA - Decision Curve Analysis)
* **Mục tiêu chung:** Chứng minh giá trị lợi ích thực tiễn lâm sàng (Clinical Net Benefit) vượt trội.
* **Thành viên 1 (Lead ML):**
  - Hiện thực module `src/evaluation/dca_analysis.py`: Tính toán chỉ số Net Benefit theo công thức Vickers & Elkin trên dải ngưỡng xác suất $p_t \in [0.05, 0.80]$.
  - Vẽ biểu đồ so sánh đường cong Net Benefit của M-CDSS với chiến lược "Treat All" và "Treat None".
  - *Đầu ra:* `src/evaluation/dca_analysis.py`, `data/dca_curve.png`.
* **Thành viên 2 (Data Engineer):**
  - Viết kịch bản `scripts/evaluate_clinical_utility.py` tự động hóa toàn bộ việc tải checkpoint, chạy trên tập Test, vẽ và lưu các đồ thị DCA, Calibration, ROC, PR-Curve thành file ảnh độ phân giải cao phục vụ bài báo khoa học.
  - *Đầu ra:* `scripts/evaluate_clinical_utility.py`.
* **Thành viên 3 (Full-stack AI):**
  - Hiển thị trực quan đồ thị DCA trực tiếp trên giao diện Admin/Doctor Settings để người dùng có thể tùy chỉnh ngưỡng can thiệp $p_t$ mong muốn theo điều kiện cơ sở vật chất của phòng khám.
  - *Đầu ra:* Component trực quan hóa DCA trên Frontend.

---

#### 🎯 TUẦN 13: Thẩm Định Với Chuyên Gia Y Tế & Kiểm Định Ngoại Kiểm (External Validation)
* **Mục tiêu chung:** Xác thực độ tin cậy định tính với bác sĩ lâm sàng và kiểm định trên nguồn dữ liệu ngoại kiểm độc lập.
* **Thành viên 1 (Lead ML):**
  - Chạy mô hình trên một tập dữ liệu ngoại kiểm độc lập hoàn toàn (ví dụ: một phân vùng bệnh viện khác chưa từng xuất hiện trong quá trình huấn luyện) để đánh giá khả năng tổng quát hóa (Generalizability) theo đúng khuyến nghị của JMIR.
  - Đánh giá mức độ suy giảm hiệu năng ngoại kiểm ($\Delta \text{AUROC}$).
  - *Đầu ra:* Báo cáo kết quả External Validation.
* **Thành viên 2 (Data Engineer):**
  - Thiết kế bảng câu hỏi khảo sát lâm sàng (Likert Scale 1-5): Tính chính xác của chẩn đoán phân biệt, mức độ hữu ích của trích dẫn phác đồ, và độ tin cậy của việc highlight bằng chứng bệnh án.
  - Mời 2-3 bác sĩ/chuyên gia y tế thực hiện blind-review trên 20 ca bệnh lâm sàng ngẫu nhiên.
  - *Đầu ra:* Báo cáo định tính đánh giá của chuyên gia y tế (Clinician Feedback Report).
* **Thành viên 3 (Full-stack AI):**
  - Thu thập phản hồi từ người dùng thực tế về trải nghiệm giao diện (UI/UX), tối ưu hóa tốc độ tải trang, tinh chỉnh giao diện mobile-responsive cho máy tính bảng của bác sĩ.
  - *Đầu ra:* Phiên bản Frontend hoàn thiện, tối ưu hóa giao diện.

---

### GIAI ĐOẠN 5: ĐÓNG GÓI DOCKER, BÁO CÁO TRIPOD-AI & NGHIỆM THU (TUẦN 14 – TUẦN 16)

#### 🎯 TUẦN 14: Đóng Gói Toàn Bộ Hệ Thống Bằng Docker & Docker-Compose
* **Mục tiêu chung:** Biến toàn bộ dự án thành sản phẩm có thể triển khai chỉ bằng 1 lệnh duy nhất.
* **Thành viên 1 (Lead ML):**
  - Tối ưu hóa file trọng số mô hình (Model Quantization / TorchScript / ONNX nếu cần) để giảm dung lượng tải xuống và tiết kiệm VRAM khi chạy trên máy chủ bệnh viện.
  - Đóng gói container API Backend trong `Dockerfile` với PyTorch và GPU runtime.
  - *Đầu ra:* `Dockerfile` backend tối ưu.
* **Thành viên 2 (Data Engineer):**
  - Đóng gói cấu hình nạp sẵn cơ sở dữ liệu tri thức Qdrant Vector Store vào container để khi khởi động là có sẵn phác đồ điều trị mà không cần crawl/ingest lại từ đầu.
  - Viết tài liệu hướng dẫn sao lưu và phục hồi dữ liệu y tế an toàn.
  - *Đầu ra:* Container cấu hình Qdrant Vector DB có sẵn dữ liệu.
* **Thành viên 3 (Full-stack AI):**
  - Viết `Dockerfile` đa tầng (Multi-stage build) cho Frontend Next.js để giảm dung lượng image xuống dưới 150MB.
  - Hoàn thiện file `docker-compose.yml` kết nối 3 dịch vụ: `frontend` (port 3000), `api` (port 8000), `vector-db` (port 6333).
  - Kiểm thử khởi chạy từ đầu trên máy tính mới: `docker compose up --build`.
  - *Đầu ra:* `docker-compose.yml`, kiểm thử chạy thông suốt 100%.

---

#### 🎯 TUẦN 15: Soạn Thảo Báo Cáo Khoa Học Chuẩn TRIPOD-AI & Kiểm Toán PROBAST
* **Mục tiêu chung:** Hoàn thiện bản thảo bài báo khoa học đầy đủ và đạt chuẩn thẩm định y tế.
* **Thành viên 1 (Lead ML):**
  - Chịu trách nhiệm viết phần **Phương Pháp Luận (Methodology)** và **Kết Quả (Results)** của bài báo khoa học: Công thức toán FT-Transformer, Attention Weights, kết quả Ablation Study, đồ thị Calibration và DCA Curve.
  - *Đầu ra:* Bản thảo phần Methods & Results (tiếng Anh hoặc tiếng Việt chuẩn học thuật).
* **Thành viên 2 (Data Engineer):**
  - Chịu trách nhiệm viết phần **Dữ Liệu Lâm Sàng (Data Cohort)**, **Xử Lý Dữ Liệu Khuyết & De-ID** và **Bảng Kiểm Toán 20 Tiêu Chí PROBAST**: Chứng minh hệ thống đạt chuẩn Low Risk of Bias trên cả 4 miền.
  - *Đầu ra:* Bản thảo phần Cohort & Bảng checklist PROBAST chi tiết.
* **Thành viên 3 (Full-stack AI):**
  - Chịu trách nhiệm viết phần **Kiến Trúc Hệ Thống (System Architecture)**, **Agentic RAG Flow** và **Giao Diện Lâm Sàng (Clinician Interface)**.
  - Thiết kế các hình minh họa kiến trúc chất lượng cao (Vector figures) phục vụ xuất bản.
  - *Đầu ra:* Sơ đồ kiến trúc độ nét cao và bản thảo phần Software Architecture.

---

#### 🎯 TUẦN 16: Hoàn Thiện Video Demo, Open-Source Release & Báo Cáo Nghiệm Thu
* **Mục tiêu chung:** Bàn giao toàn bộ dự án, nghiệm thu sản phẩm mã nguồn mở hoàn chỉnh.
* **Thành viên 1 (Lead ML):**
  - Review toàn bộ mã nguồn mô hình, dọn dẹp sạch sẽ các checkpoint tạm thời, gắn tag phiên bản phát hành `v1.0.0-release`.
  - Soạn thảo tài liệu hướng dẫn tinh chỉnh mô hình cho cộng đồng nghiên cứu.
  - *Đầu ra:* Release tag trên Git, tệp weights chính thức.
* **Thành viên 2 (Data Engineer):**
  - Kiểm tra rà soát an ninh lần cuối: Bảo đảm tuyệt đối không có bất kỳ thông tin bệnh nhân thực nào bị rò rỉ trong git history hoặc các file ví dụ mẫu.
  - Hoàn thiện tài liệu Data Dictionary và Giấy phép bản quyền mã nguồn mở (MIT License).
  - *Đầu ra:* Báo cáo kiểm định an toàn dữ liệu, file License.
* **Thành viên 3 (Full-stack AI):**
  - Quay video demo kịch bản hoàn chỉnh (3 - 5 phút):
    1. Giới thiệu khoảng trống y văn từ JMIR.
    2. Thao tác nhập ca bệnh khó trên Web Dashboard.
    3. Xem kết quả dự báo đã hiệu chuẩn.
    4. Khám phá tính năng Agentic RAG giải trình và highlight trực tiếp câu văn trong bệnh án gốc.
  - Kiểm tra toàn bộ link tài liệu trong `README.md` và thư mục `docs/`.
  - *Đầu ra:* Video Demo sản phẩm chất lượng cao, bài thuyết trình Slide nghiệm thu hoàn chỉnh.

---

## 3. MA TRẬN PHỤ THUỘC & ĐIỂM BÀN GIAO (DEPENDENCY & HAND-OFF MATRIX)

Để không thành viên nào bị nghẽn công việc (blocking), các điểm bàn giao cốt tử giữa 3 thành viên được quy định như sau:

```
[Tuần 1: Thành viên 2 (Data Schema)]
              │ Bàn giao Schema biến số
              ▼
[Tuần 2: Thành viên 1 (Khung Baseline)] ───► [Tuần 3: Thành viên 2 (Bộ dữ liệu sạch train/val/test)]
                                                               │
                                                               ▼
                                              [Tuần 4-5: Thành viên 1 (Mô hình Multimodal hoàn tất)]
                                                               │
                                                               ▼
                                              [Tuần 6: Thành viên 1 bàn giao Checkpoint cho TV3]
                                                               │
                                                               ▼
[Tuần 8: TV2 bàn giao Qdrant Guideline DB] ──► [Tuần 9-10: Thành viên 3 kết nối Agentic RAG + API + UI]
                                                               │
                                                               ▼
                                              [Tuần 11-13: Cả 3 cùng chạy Benchmark & Viết Paper]
```

---

## 4. QUY ƯỚC QUẢN LÝ MÃ NGUỒN (GIT WORKFLOW) CHO NHÓM 3 NGƯỜI

1. **Nhánh chính (`main`):**
   - Luôn luôn ở trạng thái ổn định (Production-ready).
   - Chỉ merge vào `main` khi có ít nhất 1 thành viên khác review và toàn bộ test cases `pytest tests/` pass 100%.
2. **Quy tắc đặt tên nhánh tính năng (Feature Branches):**
   - Thành viên 1: `feat/model-ft-transformer`, `feat/model-cross-attention`, `feat/model-calibration`
   - Thành viên 2: `feat/data-deid-pipeline`, `feat/data-mice-imputer`, `feat/rag-guidelines-ingest`
   - Thành viên 3: `feat/agent-differential-reasoner`, `feat/api-fastapi-routes`, `feat/ui-clinician-dashboard`
3. **Quy tắc Commit Message:**
   - Sử dụng chuẩn Conventional Commits:
     + `feat(model): implement cross-attention layer between tabular and text`
     + `fix(data): enforce strict temporal lock before diagnostic timestamp`
     + `docs(probast): add 20-question audit compliance justification`
     + `test(api): add async tests for multimodal predict endpoint`
