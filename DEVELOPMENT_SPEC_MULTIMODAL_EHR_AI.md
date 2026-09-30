# SPECIFICATION VÀ HƯỚNG DẪN THỰC THI CHO AGENT CODE: HỆ THỐNG AI Y TẾ ĐA PHƯƠNG THỨC (MULTIMODAL CLINICAL DECISION SUPPORT SYSTEM)

> **Mục tiêu dự án:** Xây dựng hệ thống Trợ lý Chẩn đoán Lâm sàng Đa phương thức hoàn chỉnh (Full-stack AI System). Hệ thống giải quyết khoảng trống trong y văn hiện nay bằng cách kết hợp **Dữ liệu bảng có cấu trúc** (Sinh hiệu, Xét nghiệm, Mã ICD) và **Dữ liệu phi cấu trúc** (Ghi chú bệnh án lâm sàng tự do) thông qua mô hình **Multimodal Cross-Attention Fusion**, tích hợp **Agentic RAG** đối chiếu phác đồ điều trị và giải trình minh bạch theo chuẩn **TRIPOD-AI / PROBAST**.

---

## 1. TỔNG QUAN HỆ THỐNG & TECH STACK

```
[EHR Tabular Features] ──> [FT-Transformer Encoder] ──┐
                                                      ├──> [Cross-Attention Late Fusion] ──> [Calibrated Head] ──> [Risk Probabilities]
[Clinical Free Text]   ──> [Clinical LLM Embedding]  ──┘                                                                 │
                                                                                                                         ▼
[Clinical Guidelines]  ──> [Vector DB (Qdrant)]      ──> [Diagnostic Agent (RAG)] ────────> [Evidence Highlighting + Differential Diagnosis]
```

### 1.1. Core Tech Stack
* **Language & Runtime:** Python 3.10+, Node.js 18+ (Frontend)
* **AI / Deep Learning:** PyTorch, HuggingFace Transformers, `scikit-learn`, `xgboost`, `catboost`, `optuna`
* **NLP & De-identification:** `spaCy` (`en_core_web_sm` / `en_ner_bc5cdr_md`), `presidio-analyzer`
* **Knowledge Retrieval & Agent:** `langchain` / `langgraph` (hoặc custom lightweight agent flow), `qdrant-client` / `chromadb`, `sentence-transformers`
* **Backend API:** `FastAPI`, `pydantic v2`, `uvicorn`, `celery` + `redis` (cho batch inference lớn)
* **Frontend:** `Next.js 14` (App Router), `TypeScript`, `TailwindCSS`, `Lucide React`, `shadcn/ui`
* **DevOps & Testing:** `Docker`, `Docker Compose`, `pytest`, `httpx`

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT DIRECTORY TREE)

```
clinical-multimodal-system/
├── data/
│   ├── raw/                        # Dữ liệu gốc (MIMIC-IV-Note subset hoặc synthetic data)
│   ├── processed/                  # Dữ liệu sau khử định danh & temporal alignment
│   ├── guidelines/                 # Tài liệu phác đồ y khoa (PDF/Markdown) cho RAG
│   └── vector_store/               # Database vector lưu embedding phác đồ
├── configs/
│   ├── model_config.yaml           # Siêu tham số cho FT-Transformer, LLM, Fusion layer
│   ├── rag_config.yaml             # Cấu hình embedding, chunking, threshold RAG
│   └── data_schema.yaml            # Danh sách biến xét nghiệm, sinh hiệu, nhãn bệnh
├── src/
│   ├── __init__.py
│   ├── data_pipeline/              # Tầng xử lý dữ liệu & Bảo mật PHI
│   │   ├── __init__.py
│   │   ├── deidentifier.py         # Module khử định danh HIPAA/PHI (NER + Regex)
│   │   ├── temporal_aligner.py     # Module khóa chuỗi thời gian (chống rò rỉ nhãn)
│   │   ├── imputer.py              # Xử lý missing data (MICE / KNN)
│   │   └── dataset_loader.py       # PyTorch Dataset cho dữ liệu đa phương thức
│   ├── models/                     # Tầng Mô hình hóa AI
│   │   ├── __init__.py
│   │   ├── baselines.py            # Baseline 1 & 2 (XGBoost, CatBoost, TabNet)
│   │   ├── text_encoder.py         # Nhánh Text Encoder (ClinicalBERT / Med-LLM)
│   │   ├── tabular_encoder.py      # Nhánh Tabular (FT-Transformer Feature Tokenizer)
│   │   ├── multimodal_fusion.py    # Mạng Cross-Attention Late Fusion
│   │   └── calibration.py          # Hiệu chuẩn xác suất (Platt Scaling, Isotonic)
│   ├── agent/                      # Tầng Agentic RAG & Giải trình
│   │   ├── __init__.py
│   │   ├── knowledge_ingest.py     # Chunking & Indexing phác đồ y khoa
│   │   ├── retriever.py            # Hybrid search (Vector + BM25)
│   │   ├── diagnostic_agent.py     # Agent phân tích chẩn đoán phân biệt & phản biện
│   │   └── evidence_grounder.py    # Highlight trích dẫn chính xác từ bệnh án gốc
│   ├── evaluation/                 # Đo đạc chỉ số khoa học
│   │   ├── __init__.py
│   │   ├── metrics.py              # AUROC, AUPRC, Macro-F1, ECE, Brier Score
│   │   ├── dca_analysis.py         # Decision Curve Analysis (Lợi ích lâm sàng)
│   │   └── probast_checklist.py    # Unit tests kiểm tra tuân thủ chuẩn PROBAST
│   └── api/                        # REST API Backend (FastAPI)
│       ├── __init__.py
│       ├── main.py                 # FastAPI Entrypoint
│       ├── schemas.py              # Pydantic schemas (Request/Response)
│       └── routes/
│           ├── inference.py        # Endpoints dự đoán (Baselines vs Multimodal)
│           ├── agent_chat.py       # Endpoint tương tác với Diagnostic Agent
│           └── evaluation_routes.py # API xuất báo cáo đánh giá & benchmark
├── frontend/                       # Web Dashboard cho Bác sĩ (Next.js)
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   ├── PatientDataForm.tsx # Form nhập sinh hiệu, xét nghiệm & ghi chú
│   │   │   ├── DiagnosticCard.tsx  # Hiển thị Top-K chẩn đoán + thanh đo rủi ro
│   │   │   ├── EvidenceViewer.tsx  # Hiển thị ghi chú kèm highlight câu chứng cứ
│   │   │   └── GuidelineDrawer.tsx # Drawer tra cứu phác đồ điều trị được trích dẫn
│   │   └── lib/api.ts
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_multimodal_model.py
│   ├── test_agent_rag.py
│   └── test_api_endpoints.py
├── scripts/
│   ├── run_baselines.py            # Huấn luyện baseline & xuất bảng so sánh
│   ├── train_multimodal.py         # Huấn luyện mô hình Multimodal Fusion
│   └── evaluate_clinical_utility.py# Vẽ biểu đồ Calibration và DCA Curve
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 3. DATA SCHEMA & SPECIFICATION DỮ LIỆU

### 3.1. Tabular Data Contract (`configs/data_schema.yaml`)
```yaml
features:
  numerical:
    - name: "age"
      type: "int"
      min: 18
      max: 110
    - name: "systolic_bp"
      type: "float"
      unit: "mmHg"
      normal_range: [90.0, 130.0]
    - name: "diastolic_bp"
      type: "float"
      unit: "mmHg"
      normal_range: [60.0, 85.0]
    - name: "heart_rate"
      type: "float"
      unit: "bpm"
      normal_range: [60.0, 100.0]
    - name: "respiratory_rate"
      type: "float"
      unit: "breaths/min"
      normal_range: [12.0, 20.0]
    - name: "spo2"
      type: "float"
      unit: "%"
      normal_range: [95.0, 100.0]
    - name: "temperature"
      type: "float"
      unit: "Celsius"
      normal_range: [36.5, 37.5]
    - name: "wbc_count"
      type: "float"
      unit: "10^9/L"
      normal_range: [4.0, 10.0]
    - name: "crp"
      type: "float"
      unit: "mg/L"
      normal_range: [0.0, 5.0]
  categorical:
    - name: "gender"
      categories: ["M", "F", "OTHER"]
    - name: "smoking_status"
      categories: ["NEVER", "FORMER", "CURRENT"]
    - name: "history_hypertension"
      categories: [0, 1]
    - name: "history_diabetes"
      categories: [0, 1]

targets:
  task_type: "multiclass"
  num_classes: 4
  labels:
    0: "ASTHMA"                     # Hen phế quản
    1: "COPD"                       # Bệnh phổi tắc nghẽn mạn tính
    2: "CONGESTIVE_HEART_FAILURE"   # Suy tim sung huyết
    3: "COMMUNITY_ACQUIRED_PNEUMONIA" # Viêm phổi mắc phải cộng đồng
```

### 3.2. Unstructured Clinical Note Schema
```json
{
  "patient_id": "PT-98213",
  "encounter_timestamp": "2026-09-14T09:30:00",
  "chief_complaint": "Bệnh nhân khó thở tăng dần về đêm kèm ho khạc đờm trắng đục 3 ngày nay.",
  "history_of_present_illness": "Bệnh nhân có tiền sử hút thuốc lá 20 bao-năm. Khó thở xuất hiện khi gắng sức nhẹ, phải ngồi để thở về đêm. Không sốt cao, không đau ngực kiểu màng phổi.",
  "physical_examination_notes": "Rì rào phế nang giảm hai đáy phổi, rale rít và rale ngáy rải rác thì thở ra. Phù nhẹ hai mắt cá chân, tĩnh mạch cổ nổi tư thế 45 độ.",
  "prior_medications": "Salbutamol xịt ngắt quãng, Amlodipine 5mg"
}
```

---

## 4. CHI TIẾT CÁC MODULE KỸ THUẬT CỐT LÕI

### Module 1: Data Pipeline & Bảo Mật Khử Định Danh (`src/data_pipeline/`)
* **`deidentifier.py`:**
  - Nhận text ghi chú lâm sàng $ightarrow$ Áp dụng pipeline NER (nhận diện `PATIENT`, `DOCTOR`, `HOSPITAL`, `DATE`, `PHONE`, `SSN`) $ightarrow$ Thay thế bằng tokens `[REDACTED_NAME]`, `[REDACTED_DATE]`.
* **`temporal_aligner.py`:**
  - Nhận danh sách sự kiện khám bệnh kèm timestamp.
  - Loại bỏ toàn bộ ghi chú/kết quả xét nghiệm có `timestamp >= diagnostic_confirmed_timestamp`.
  - Kiểm tra loại trừ: Không cho phép đưa các feature là "tiêu chuẩn vàng chẩn đoán" (Gold Standard Target) vào dữ liệu đầu vào.
* **`imputer.py`:**
  - Triển khai `IterativeImputer` (MICE) cho biến số liên tục và `SimpleImputer(strategy='most_frequent')` cho biến phân loại.
  - Lưu và xuất log tỷ lệ missingness của từng feature trước và sau khi gán.

### Module 2: Mô Hình Đa Phương Thức (`src/models/`)
* **`tabular_encoder.py` (FT-Transformer Layer):**
  - Chuyển đổi $d$ biến số và phân loại thành các Feature Embeddings kích thước $d 	imes E$.
  - Đi qua $L$ lớp Transformer Encoder $ightarrow$ Trích xuất vector đại diện $h_{tab} \in \mathbb{R}^{D_{tab}}$.
* **`text_encoder.py` (Clinical Text Encoder):**
  - Nhận text bệnh án đã tiền xử lý $ightarrow$ Tokenizer $ightarrow$ Truyền qua Transformer Language Model (ví dụ: `emilyalsentzer/Bio_ClinicalBERT` hoặc `medical-llm-embeddings`) $ightarrow$ Pooled vector $h_{text} \in \mathbb{R}^{D_{text}}$.
* **`multimodal_fusion.py` (Cross-Attention Network):**
  - Ánh xạ $h_{tab}$ và $h_{text}$ về cùng chiều không gian $D$.
  - Tính toán Cross-Attention: $Q_{tab} = h_{tab} W_q$, $K_{text} = h_{text} W_k$, $V_{text} = h_{text} W_v$.
  - $	ext{Attention}(Q_{tab}, K_{text}, V_{text}) = 	ext{softmax}\left(rac{Q_{tab} K_{text}^T}{\sqrt{D}}ight) V_{text}$.
  - Ghép nối Residual + Linear Fusion $ightarrow$ Feature Vector $h_{fused}$.
* **`calibration.py` (Platt & Temperature Scaling):**
  - Tối ưu tham số nhiệt độ $T$ trên Validation Set: $\hat{p}_i = 	ext{softmax}(z_i / T)$.
  - Đảm bảo điểm Expected Calibration Error (ECE) $< 0.05$.

### Module 3: Agentic RAG & Giải Trình Lâm Sàng (`src/agent/`)
* **`knowledge_ingest.py`:**
  - Đọc tài liệu Hướng dẫn Chẩn đoán (NICE, GINA cho Hen/COPD, ESC cho Suy tim, Bộ Y tế).
  - Chunking theo cấu trúc y khoa (Tiêu chuẩn chẩn đoán, Yếu tố nguy cơ, Chẩn đoán phân biệt, Triệu chứng báo động).
  - Lưu vào Vector DB cùng Metadata chuẩn.
* **`diagnostic_agent.py`:**
  - **Bước 1 (Hypothesis Generation):** Nhận kết quả Top-K xác suất từ Multimodal Model.
  - **Bước 2 (Evidence Retrieval):** Truy vấn Vector DB lấy các tiêu chuẩn chẩn đoán phân biệt của 2 bệnh có xác suất cao nhất.
  - **Bước 3 (Self-Reflection & Differential Synthesis):** Prompt LLM đóng vai trò Chuyên gia Hội chẩn lâm sàng:
    * Chỉ ra các bằng chứng ủng hộ chẩn đoán A từ ghi chú bệnh án.
    * Chỉ ra các bằng chứng không ủng hộ hoặc hướng về chẩn đoán B.
    * Đưa ra cảnh báo dấu hiệu nguy hiểm (Red Flags) nếu có.
* **`evidence_grounder.py`:**
  - Trích xuất vị trí chỉ mục (character offset start, end) của các câu trong bệnh án gốc được LLM sử dụng làm dẫn chứng, truyền về frontend để highlight màu vàng/xanh.

### Module 4: REST API Backend (`src/api/`)
* **Endpoint 1:** `POST /api/v1/predict/multimodal`
  - *Input:* `{ tabular_data: {...}, clinical_notes: "..." }`
  - *Output:* `{ predictions: [{ label: "COPD", probability: 0.74, calibrated: true }, ...], latency_ms: 120 }`
* **Endpoint 2:** `POST /api/v1/agent/explain`
  - *Input:* `{ patient_id: "...", prediction_id: "...", target_diagnosis: "COPD" }`
  - *Output:* `{ reasoning: "...", evidence_spans: [{ text: "...", start: 102, end: 180 }], guideline_sources: [{ title: "GINA 2024", section: "..." }] }`
* **Endpoint 3:** `GET /api/v1/evaluation/benchmark`
  - *Output:* Bảng so sánh chỉ số AUROC, F1, ECE giữa Baseline 1, Baseline 2, Baseline 3 và Multimodal Fusion Model.

---

## 5. KẾ HOẠCH BƯỚC THỰC HIỆN TỪNG BƯỚC CHO AGENT CODE (PHASED TASKS)

Khi thực thi code, Agent Code hãy làm lần lượt theo 8 Task sau, viết Unit Test cho từng Task trước khi chuyển sang Task tiếp theo:

### Task 1: Khởi tạo Project Skeleton, Configs & Môi Trường
1. Tạo cấu trúc thư mục như Mục 2.
2. Tạo file `requirements.txt` bao gồm:
   `torch`, `transformers`, `accelerate`, `scikit-learn`, `xgboost`, `catboost`, `optuna`, `spacy`, `fastapi`, `uvicorn`, `pydantic`, `qdrant-client`, `sentence-transformers`, `matplotlib`, `seaborn`, `pytest`.
3. Viết `configs/data_schema.yaml` và `configs/model_config.yaml`.

### Task 2: Xây dựng Pipeline Xử Lý Dữ Liệu & Khử Định Danh (`src/data_pipeline/`)
1. Implement `src/data_pipeline/deidentifier.py`: Regex + spaCy để khử PII/PHI.
2. Implement `src/data_pipeline/temporal_aligner.py`: Lọc biến theo timestamp sự kiện.
3. Implement `src/data_pipeline/imputer.py`: Missing value handling (MICE).
4. Implement `src/data_pipeline/dataset_loader.py`: Custom PyTorch Dataset trả về `(tabular_tensor, input_ids, attention_mask, label)`.
5. Viết tests trong `tests/test_data_pipeline.py`.

### Task 3: Xây dựng Các Mô Hình Đối Chứng (Baselines) (`src/models/baselines.py`)
1. Triển khai Class `ClassicalTabularBaseline`: Chứa pipeline huấn luyện `RandomForestClassifier`, `XGBClassifier`, `CatBoostClassifier`.
2. Triển khai Class `TabularDeepBaseline`: Huấn luyện MLP / FT-Transformer chỉ trên dữ liệu bảng.
3. Triển khai Class `TextOnlyBaseline`: Huấn luyện Classifier chỉ dùng Text Embeddings.
4. Viết script `scripts/run_baselines.py` để benchmark và lưu kết quả vào `data/baseline_results.json`.

### Task 4: Xây dựng Mạng Multimodal Fusion (`src/models/multimodal_fusion.py`)
1. Xây dựng `TabularTokenizer` & `FTTransformerEncoder`.
2. Xây dựng `ClinicalTextEncoder` (dựa trên HuggingFace AutoModel).
3. Xây dựng lớp `CrossAttentionFusion(nn.Module)`.
4. Viết hàm forward kết hợp cả hai luồng và đưa qua Classification Head.
5. Implement `src/models/calibration.py` (Temperature Scaling).
6. Viết script `scripts/train_multimodal.py` hỗ trợ huấn luyện có Early Stopping và tính Validation Loss.
7. Viết tests trong `tests/test_multimodal_model.py`.

### Task 5: Xây dựng Tầng Agentic RAG & Trích Xuất Dẫn Chứng (`src/agent/`)
1. Implement `src/agent/knowledge_ingest.py`: Đọc các file guideline trong `data/guidelines/` $ightarrow$ sinh embedding $ightarrow$ nạp vào Qdrant (hoặc local ChromaDB/FAISS).
2. Implement `src/agent/retriever.py`: Hàm tìm kiếm đoạn hướng dẫn y tế theo query triệu chứng.
3. Implement `src/agent/diagnostic_agent.py`: Prompt template chặt chẽ cho LLM để đưa ra phân tích lâm sàng có cấu trúc JSON.
4. Implement `src/agent/evidence_grounder.py`: Hàm so khớp câu trích dẫn của LLM với văn bản gốc để lấy offset `start` và `end`.
5. Viết tests trong `tests/test_agent_rag.py`.

### Task 6: Xây dựng Tầng Đo Đạc Khoa Học & Báo Cáo PROBAST (`src/evaluation/`)
1. Implement `src/evaluation/metrics.py`: Tính toán `roc_auc_score` (One-vs-Rest), `average_precision_score` (PR-AUC), `f1_score`, `expected_calibration_error`, `brier_score_loss`.
2. Implement `src/evaluation/dca_analysis.py`: Tính toán Net Benefit qua các ngưỡng xác suất can thiệp ($p_t \in [0.01, 0.99]$) và vẽ đồ thị DCA.
3. Viết script `scripts/evaluate_clinical_utility.py` xuất báo cáo so sánh đa tiêu chí và lưu các biểu đồ PNG.

### Task 7: Xây dựng Backend REST API (`src/api/`)
1. Implement `src/api/schemas.py`: Định nghĩa Pydantic Models cho mọi request/response.
2. Implement `src/api/routes/inference.py`: API chạy dự đoán cho cả Baselines và Multimodal Model.
3. Implement `src/api/routes/agent_chat.py`: API streaming kết quả giải trình chẩn đoán từ Agentic RAG.
4. Implement `src/api/main.py`: Khởi tạo FastAPI app, cấu hình CORS, mount routes.
5. Viết tests trong `tests/test_api_endpoints.py`.

### Task 8: Xây dựng Giao Diện Bác Sĩ (Frontend Next.js) & Đóng Gói Docker
1. Khởi tạo Frontend trong thư mục `frontend/` với Next.js và TailwindCSS.
2. Xây dựng component `PatientDataForm.tsx` cho phép nhập song song chỉ số bảng và paste ghi chú lâm sàng.
3. Xây dựng component `DiagnosticCard.tsx` hiển thị thanh xác suất rủi ro đã hiệu chuẩn (Calibrated Confidence Bar).
4. Xây dựng component `EvidenceViewer.tsx` tự động highlight các câu trong bệnh án được Agent trích dẫn.
5. Viết `Dockerfile` cho Backend & Frontend, cấu hình `docker-compose.yml` để chạy toàn bộ hệ thống bằng 1 lệnh: `docker compose up --build`.

---

## 6. UNIT TEST & TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

Một task được coi là hoàn thành khi và chỉ khi:
1. **Toàn bộ Test Cases pass:** Chạy `pytest tests/` không có lỗi.
2. **Không có Target Leakage:** Unit test của `temporal_aligner` xác nhận không có bất kỳ feature nào xuất hiện sau mốc thời gian chẩn đoán.
3. **Hiệu năng Multimodal vượt trội Baselines:** 
   - Multimodal AUROC $\ge$ Tabular Baseline AUROC $+ 0.04$
   - Expected Calibration Error (ECE) $< 0.06$
4. **Agentic RAG không bị ảo giác:** 100% các đoạn trích dẫn (Evidence Spans) phải map chính xác với chuỗi ký tự có thực trong ghi chú bệnh án gốc.
5. **Docker Build thành công:** Toàn bộ stack API + Vector DB + Frontend khởi chạy thông suốt qua `docker-compose up`.
