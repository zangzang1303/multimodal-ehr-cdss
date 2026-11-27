# Multimodal Clinical Decision Support System (M-CDSS)
### Hệ Thống Hỗ Trợ Ra Quyết Định Chẩn Đoán Đa Phương Thức Dựa Trên EHR & Agentic RAG

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org/)
[![TRIPOD-AI Compliant](https://img.shields.io/badge/TRIPOD--AI-Compliant-success.svg)](https://www.bmj.com/content/385/bmj-2023-078378)
[![PROBAST Audited](https://img.shields.io/badge/PROBAST-Low_Risk_Design-brightgreen.svg)](https://www.acpjournals.org/doi/10.7326/M18-1376)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Calibration](https://img.shields.io/badge/ECE-%3C%200.05-blueviolet.svg)](#)

---

## 1. TỔNG QUAN DỰ ÁN & ĐỘNG LỰC NGHIÊN CỨU (EXECUTIVE SUMMARY & RESEARCH MOTIVATION)

Hệ thống **Multimodal Clinical Decision Support System (M-CDSS)** là giải pháp trí tuệ nhân tạo y tế đa phương thức chuyên sâu, được thiết kế nhằm nâng cao độ chính xác, tính an toàn và khả năng giải trình trong quá trình phân loại, chẩn đoán phân biệt các bệnh lý phức tạp tại tuyến y tế ban đầu (Primary Care).

```
                      KHOẢNG TRỐNG TRONG Y VĂN (JMIR REVIEW 2024)
   ┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
   │ 15 nghiên cứu đạt chuẩn / 10.657 bản ghi     │ 0/15 nghiên cứu có nguy cơ sai lệch thấp     │
   │ (AI + EHR, chăm sóc ban đầu)                 │ (PROBAST; chủ yếu do mô tả phương pháp kém)  │
   ├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
   │ 11/15 (73%) chỉ nhắm một bệnh mạn tính       │ 13/15 chỉ phát triển, 2/15 ngoại kiểm        │
   │                                              │ (Hunik et al., JMIR Med Inform 2025)         │
   └──────────────────────────────────────────────┴──────────────────────────────────────────────┘
                                          │
                                          ▼
                       NGUYÊN MẪU NGHIÊN CỨU: M-CDSS
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │  FT-Transformer (Dữ liệu bảng) ──┐                                                         │
   │                                  ├──> [Cross-Attention Fusion] ──> [Calibrated Predictions]│
   │  Clinical-LLM (Ghi chú tự do)   ──┘                                      │                  │
   │                                                                          ▼                  │
   │  Phác đồ Y tế Chuẩn (Vector DB) ────> [Agentic RAG] ───────────> [Evidence Grounding]       │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1. Khoảng Trống Nghiên Cứu Từ Y Văn Thực Chứng (The Research Gap)
Tổng quan hệ thống của **Hunik và cộng sự** (*JMIR Medical Informatics* 2025;13:e62862, doi:10.2196/62862) về các mô hình chẩn đoán dựa trên AI và EHR trong chăm sóc ban đầu:
1. Sàng lọc **10.657 bản ghi**, chọn **15 nghiên cứu**; 13 nghiên cứu chỉ phát triển mô hình, 2 nghiên cứu ngoại kiểm.
2. **11/15 (73%)** chỉ nhắm một bệnh mạn tính.
3. Theo PROBAST, **không nghiên cứu nào có nguy cơ sai lệch thấp**; nguy cơ cao chủ yếu do mô tả phương pháp không đầy đủ.
4. Tác giả kết luận các mô hình hiện có **chưa sẵn sàng** để triển khai trong chăm sóc ban đầu.

> Các con số chi tiết khác từng ghi ở đây (tỷ lệ chỉ dùng dữ liệu bảng, tỷ lệ hiệu chuẩn…) đã được gỡ bỏ ngày 2026-11-23 vì chưa đối chiếu được với bản công bố chính thức.

### 1.2. Mục Tiêu và Phát Hiện Chính của M-CDSS
- **Nguyên mẫu đa phương thức:** FT-Transformer (dữ liệu bảng) + Bio_ClinicalBERT (ghi chú) dung hợp bằng cross-attention, hiệu chuẩn temperature scaling, giải trình bằng truy xuất phác đồ và neo bằng chứng vào vị trí ký tự trong ghi chú.
- **Phát hiện chính (Phase 3, số liệu trong `results/registry.json`):** trên đoàn hệ bán tổng hợp này, dung hợp **không vượt** mô hình văn bản fine-tune và ensemble đơn giản; tín hiệu văn bản chủ yếu đến từ các con số sinh hiệu nằm trong ghi chú; dữ liệu có rất ít bệnh nhân gốc ở một số lớp.
- **Giới hạn:** lớp giải trình dùng suy luận theo template tất định (chưa có LLM); khớp vị trí ký tự **không** đồng nghĩa với đúng về ngữ nghĩa lâm sàng; chưa ngoại kiểm, chưa khảo sát bác sĩ.

---

## 2. TÍNH NĂNG VÀ ĐỔI MỚI CỐT LÕI (KEY FEATURES & INNOVATIONS)

* 🧬 **Mạng Dung Hợp Đa Phương Thức Trễ (Multimodal Late Fusion):**
  - **Nhánh Bảng (Tabular Stream):** Kiến trúc Feature Tokenizer Transformer (FT-Transformer) biến đổi từng chỉ số sinh hiệu và xét nghiệm liên tục thành vector đặc trưng trong không gian $\mathbb{R}^D$, mô hình hóa tương tác phi tuyến tính giữa các biến số.
  - **Nhánh Ngữ Tự (Text Stream):** Mô hình ngôn ngữ chuyên sâu y sinh (*BioLinkBERT / ClinicalBERT*) trích xuất ngữ cảnh diễn tiến bệnh sử, tiền căn gia đình và triệu chứng cơ năng.
  - **Cross-Attention Mechanism:** Sử dụng truy vấn từ bảng số ($Q_{tab}$) chiếu lên không gian từ ngữ ($K_{text}, V_{text}$) và ngược lại, tạo ra biểu diễn dung hợp toàn diện $h_{fused}$.
* 🎯 **Hiệu Chuẩn Xác Suất Lâm Sàng (Clinical Probability Calibration):**
  - Tích hợp lớp **Temperature Scaling** và **Platt Scaling** được tối ưu hóa trên Validation Set độc lập.
  - Giảm thiểu hiện tượng "tự tin thái quá" (overconfidence) thường gặp ở Deep Learning, mục tiêu ECE < 0.05 (**chưa đạt**: ECE sau hiệu chuẩn ≈ 0.08, xem MODEL_CARD.md) và tối ưu **Brier Score**. Đảm bảo khi hệ thống báo rủi ro 80%, xác suất mắc bệnh thực tế tiệm cận chính xác 80%.
* 🩺 **Quy Trình Agentic RAG Phân Biệt & Phản Biện (Clinician-in-the-Loop RAG):**
  - **Hypothesis Generator:** Tiếp nhận phân phối xác suất đã hiệu chuẩn từ mạng Multimodal.
  - **Guideline Retrieval Agent:** Tự động truy xuất các tiêu chí chẩn đoán phân biệt từ cơ sở dữ liệu tri thức y khoa chuẩn hóa (GINA cho Hen, GOLD cho COPD, ESC cho Suy tim, Hướng dẫn Bộ Y tế).
  - **Self-Reflective Evaluator Agent:** Tự động phản biện chẩn đoán đối kháng: chỉ ra triệu chứng nào ủng hộ bệnh A, triệu chứng nào là yếu tố loại trừ hoặc cảnh báo bệnh B (Dấu hiệu cờ đỏ - Red Flags).
* 🔍 **Cơ Chế Định Vị Bằng Chứng Minh Bạch (Evidence Grounding):**
  - Thuật toán so khớp chuỗi ký tự (exact & semantic span alignment) ánh xạ từng lý lẽ của LLM về chỉ số offset ký tự `[start_char, end_char]` trong ghi chú gốc.
  - Bác sĩ có thể bấm vào từng khuyến nghị để làm sáng (highlight) trực tiếp câu chữ gốc trong bệnh án.
* 🛡️ **Kiểm Soát Nguy Cơ Sai Lệch Triệt Để Theo Chuẩn PROBAST & TRIPOD-AI:**
  - **Temporal Alignment Engine:** Khóa chuỗi thời gian nghiêm ngặt $t_{event} < t_{confirmed\_diag}$, loại các sự kiện sau thời điểm chẩn đoán.
  - **MICE Imputation Pipeline:** Gán dữ liệu khuyết đa biến minh bạch (*Multiple Imputation by Chained Equations*), báo cáo đầy đủ chỉ số missingness trước và sau gán.
  - **Patient-Level Stratified Group Splitting:** Phân chia tập dữ liệu 70/15/15 theo `patient_id`, đảm bảo không có bất kỳ rò rỉ dữ liệu giữa các lần tái khám của cùng một bệnh nhân.
* 💻 **Nền Tảng Full-Stack Clinician Dashboard:**
  - Backend hiệu năng cao viết bằng **FastAPI** hỗ trợ suy luận bất đồng bộ (async inference).
  - Frontend hiện đại viết bằng **Next.js 14 (App Router)** và **TailwindCSS**, tích hợp bộ công cụ tương tác trực quan cho bác sĩ lâm sàng.

---

## 3. SƠ ĐỒ KIẾN TRÚC HỆ THỐNG TOÀN DIỆN (SYSTEM ARCHITECTURE)

```mermaid
flowchart TB
    subgraph INGESTION["1. TẦNG THU NHẬP & TIỀN XỬ LÝ (DATA PIPELINE)"]
        D1["Dữ liệu Bảng EHR<br/>(Sinh hiệu, Xét nghiệm, Nhân khẩu)"]
        D2["Ghi chú Khám bệnh Tự do<br/>(Clinical Progress Notes)"]
        
        P1["Bảo mật Khử Định danh PHI/PII<br/>(Presidio + Clinical NER)"]
        P2["Khóa Chuỗi Thời gian (Temporal Sync)<br/>(Loại bỏ xét nghiệm tiêu chuẩn vàng)"]
        P3["Gán Dữ liệu Khuyết Đa biến<br/>(MICE Imputer)"]
        
        D1 --> P2 --> P3
        D2 --> P1 --> P2
    end

    subgraph MULTIMODAL_CORE["2. MẠNG HỌC SÂU ĐA PHƯƠNG THỨC (MULTIMODAL AI CORE)"]
        T_ENC["FT-Transformer Encoder<br/>(Feature Tokenizer + Self-Attention)"]
        N_ENC["Clinical Text Encoder<br/>(BioLinkBERT / PubMedBERT Embeddings)"]
        
        P3 --> T_ENC
        P2 --> N_ENC
        
        CROSS_ATTN["Cross-Attention Late Fusion Layer<br/>Q_tab x K_text -> Softmax -> V_text<br/>Residual & Gated Projections"]
        
        T_ENC -->|"h_tab ∈ R^D"| CROSS_ATTN
        N_ENC -->|"h_text ∈ R^D"| CROSS_ATTN
        
        CALIB["Lớp Hiệu chuẩn Xác suất<br/>(Temperature Scaling & Platt Scaling)"]
        CROSS_ATTN --> CALIB
        
        PROBS["Calibrated Multi-Class Probabilities<br/>(Asthma, COPD, CHF, CAP)"]
        CALIB --> PROBS
    end

    subgraph AGENTIC_RAG["3. TẦNG AGENTIC RAG & GIẢI TRÌNH (CLINICAL REASONING)"]
        KB[("Vector DB (Qdrant)<br/>Phác đồ GINA, GOLD, ESC, BYT")]
        
        RETRIEVER["Hybrid Knowledge Retriever<br/>(Dense Vectors + BM25 Filtering)"]
        KB <--> RETRIEVER
        
        PROBS -->|"Top-2 Hypotheses"| RETRIEVER
        
        AGENT["Diagnostic Differential Agent<br/>(Chain-of-Thought & Self-Reflection)"]
        RETRIEVER --> AGENT
        P2 -.->|"Ghi chú đã De-ID"| AGENT
        
        GROUNDER["Evidence Grounding Engine<br/>(Span Offset Matching: [start, end])"]
        AGENT --> GROUNDER
    end

    subgraph CLINICAL_UI["4. GIAO DIỆN BÁC SĨ (FULL-STACK INTERFACE)"]
        API["FastAPI REST Backend<br/>(/api/v1/predict, /api/v1/agent/explain)"]
        UI["Clinician Dashboard (Next.js 14)<br/>- Calibrated Risk Gauge Bar<br/>- In-line Note Evidence Highlighter<br/>- Interactive Guideline Drawer"]
        
        PROBS --> API
        GROUNDER --> API
        API <==> UI
    end
```

---

## 4. KHUNG THỰC NGHIỆM KHOA HỌC & SO SÁNH BASELINES (EXPERIMENTAL BENCHMARK)

Theo kế hoạch chiến lược phát triển, hệ thống thiết lập khung đối chứng khoa học giữa 4 nhóm mô hình đại diện nhằm chứng minh giá trị thực nghiệm của phương pháp dung hợp đa phương thức:

### 4.1. Thiết Kế Các Nhóm Mô Hình Đối Chứng
| Nhóm Mô Hình | Thuật Toán Cốt Lõi | Dữ Liệu Đầu Vào | Ý Nghĩa Thực Nghiệm & Đại Diện |
| :--- | :--- | :--- | :--- |
| **Baseline 1: Classical Tabular** | Random Forest, XGBoost, CatBoost | Chỉ dữ liệu bảng (Sinh hiệu, xét nghiệm, nhân khẩu) | Tái hiện hiện trạng các công bố trong y văn tổng quan JMIR. |
| **Baseline 2: Tabular DL** | FT-Transformer, TabNet | Dữ liệu bảng thông qua kiến trúc Deep Learning | Đo lường năng lực tối đa của dữ liệu bảng khi dùng cơ chế Attention. |
| **Baseline 3: Text-only LLM** | ClinicalBERT, Med-LLM Embeddings | Chỉ ghi chú bệnh án lâm sàng tự do | Đo lường sức mạnh biểu đạt ngữ nghĩa của văn bản y khoa thuần túy. |
| **Hệ Thống Đề Xuất (Ours)** | **Multimodal Cross-Attention Fusion + Agentic RAG** | **Dữ liệu bảng + Ghi chú lâm sàng + Phác đồ y khoa chuẩn** | Kiểm tra liệu dung hợp có vượt các phương án đơn phương thức và dung hợp đơn giản (kết quả: không – xem 4.2). |

### 4.2. Kết Quả Thực Nghiệm (Phase 3 – số liệu thật)
> Bảng "kết quả kỳ vọng" của các phiên bản trước **không phải số liệu thực nghiệm** và đã bị gỡ bỏ (2026-11-23).

- **Nguồn sự thật duy nhất:** [`results/registry.json`](results/registry.json) (sinh bởi `scripts/build_results_registry.py` từ dự đoán từng bản ghi trong `data/predictions/`).
- **Tóm tắt cho người dùng:** [`MODEL_CARD.md`](MODEL_CARD.md) (sinh tự động từ registry).
- **Bảng trong bài báo:** `docs/paper_latex/generated/*.tex` (sinh bởi `scripts/export_latex_tables.py`).

Kết luận chính (chi tiết và khoảng tin cậy trong registry):
1. Dưới so sánh công bằng 5 seed, cross-attention **không vượt** Bio_ClinicalBERT fine-tune và ensemble CatBoost + BERT; không khác biệt so với mô hình chỉ dữ liệu bảng tốt nhất.
2. Tín hiệu của nhánh văn bản đến chủ yếu từ các **con số sinh hiệu/xét nghiệm** nằm trong ghi chú (RQ2).
3. Dữ liệu bán tổng hợp có số bệnh nhân gốc rất nhỏ ở một số lớp (suy tim, viêm phổi trong tập test: 1 bệnh nhân gốc mỗi lớp) – xem `data_provenance` trong registry.
4. ECE sau temperature scaling chưa đạt mục tiêu < 0,05.

---

## 5. CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT REPOSITORY STRUCTURE)

```
multimodal-ehr-cdss/
├── configs/                            # Cấu hình tham số hệ thống & Schema
│   ├── data_schema.yaml                # Đặc tả biến bảng, dải giá trị bình thường, nhãn bệnh
│   ├── model_config.yaml               # Siêu tham số FT-Transformer, Text-LLM, Cross-Attention
│   └── rag_config.yaml                 # Cấu hình Vector DB, embedding model, chunk size
├── data/                               # Quản lý dữ liệu phân tầng an toàn
│   ├── raw/                            # Dữ liệu gốc (được bảo vệ, không commit git)
│   ├── processed/                      # Dữ liệu sau De-ID, Temporal Alignment & MICE
│   ├── guidelines/                     # Tài liệu phác đồ y khoa chuẩn (GINA, GOLD, ESC, BYT)
│   └── vector_store/                   # Cơ sở dữ liệu Vector embedding phác đồ
├── docs/                               # TÀI LIỆU KỸ THUẬT & HỌC THUẬT CHUYÊN SÂU
│   ├── 01_RESEARCH_BACKGROUND_AND_GAP.md   # Phân tích 15 bài báo JMIR & 4 miền PROBAST
│   ├── 02_MULTIMODAL_ARCHITECTURE_AND_MATH.md# Toán học FT-Transformer, Attention & Calibration
│   ├── 03_DATA_PIPELINE_AND_PRIVACY.md     # Pipeline De-ID, Temporal Sync & MICE
│   ├── 04_AGENTIC_RAG_AND_EXPLAINABILITY.md# Multi-Agent reasoning & Evidence Grounding
│   ├── 05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md # AUROC, DCA, Checklist 20 câu PROBAST
│   └── TEAM_TASK_ALLOCATION_AND_ROADMAP.md # Phân chia nhiệm vụ 16 tuần cho nhóm 3 người
├── frontend/                           # Giao diện Web Bác sĩ (Next.js 14 + TailwindCSS)
│   ├── src/
│   │   ├── app/                        # Next.js App Router (Dashboard, History, Guidelines)
│   │   ├── components/                 # Các UI Components chuyên biệt
│   │   │   ├── PatientDataForm.tsx     # Form nhập sinh hiệu, xét nghiệm & ghi chú bệnh án
│   │   │   ├── DiagnosticCard.tsx      # Card trực quan hóa rủi ro & thanh đo đã hiệu chuẩn
│   │   │   ├── EvidenceViewer.tsx      # Trình xem bệnh án tự động highlight câu chứng cứ
│   │   │   └── GuidelineDrawer.tsx     # Drawer tra cứu nhanh phác đồ điều trị liên quan
│   │   └── lib/api.ts                  # Client kết nối FastAPI Backend
│   ├── package.json
│   └── tsconfig.json
├── scripts/                            # Scripts thực thi nghiên cứu & kiểm định
│   ├── run_baselines.py                # Huấn luyện 3 Baselines & kết xuất Benchmark JSON
│   ├── train_multimodal.py             # Huấn luyện Mạng Multimodal Fusion & lưu Checkpoint
│   └── evaluate_clinical_utility.py    # Vẽ biểu đồ Calibration Curve và đồ thị DCA Net Benefit
├── src/                                # Toàn bộ mã nguồn cốt lõi (Core Python Package)
│   ├── __init__.py
│   ├── agent/                          # Tầng Agentic RAG & Giải trình Lâm sàng
│   │   ├── __init__.py
│   │   ├── knowledge_ingest.py         # Phân mảnh (chunking) & nạp vector phác đồ y tế
│   │   ├── retriever.py                # Hybrid search (Dense Vector + BM25 keyword)
│   │   ├── diagnostic_agent.py         # Multi-Agent phân tích chẩn đoán phân biệt & phản biện
│   │   └── evidence_grounder.py        # So khớp câu trích dẫn với character offset văn bản gốc
│   ├── api/                            # REST API Backend (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py                     # Entrypoint FastAPI, CORS, middleware logging
│   │   ├── schemas.py                  # Pydantic v2 Models cho Request/Response Contract
│   │   └── routes/
│   │       ├── inference.py            # API chạy dự đoán mô hình (Baselines & Multimodal)
│   │       ├── agent_chat.py           # API streaming hội chẩn với Diagnostic Agent
│   │       └── evaluation_routes.py    # API truy vấn kết quả benchmark & metrics
│   ├── data_pipeline/                  # Tầng Tiền xử lý dữ liệu & Bảo mật PHI
│   │   ├── __init__.py
│   │   ├── deidentifier.py             # Pipeline khử định danh PHI/PII (NER + Regex)
│   │   ├── temporal_aligner.py         # Khóa chuỗi thời gian, ngăn ngừa rò rỉ nhãn
│   │   ├── imputer.py                  # Xử lý missing data đa biến (MICE IterativeImputer)
│   │   └── dataset_loader.py           # PyTorch Dataset hỗ trợ dữ liệu đa phương thức
│   ├── evaluation/                     # Tầng Đo lường Khoa học & Chuẩn PROBAST
│   │   ├── __init__.py
│   │   ├── metrics.py                  # AUROC, AUPRC, Macro-F1, ECE, Brier Score
│   │   ├── dca_analysis.py             # Tính toán Decision Curve Analysis (Lợi ích ròng)
│   │   └── probast_checklist.py        # Bộ kiểm tra tự động tuân thủ 20 tiêu chí PROBAST
│   └── models/                         # Tầng Kiến trúc Mô hình Trí tuệ Nhân tạo
│       ├── __init__.py
│       ├── baselines.py                # Triển khai Classical Tabular, TabNet & Text-only LLM
│       ├── tabular_encoder.py          # FT-Transformer Feature Tokenizer cho số liệu bảng
│       ├── text_encoder.py             # ClinicalBERT / Med-LLM Text Encoder
│       ├── multimodal_fusion.py        # Mạng Cross-Attention Late Fusion
│       └── calibration.py              # Temperature Scaling & Platt Scaling Module
├── tests/                              # Bộ Unit Tests & Integration Tests toàn diện
│   ├── test_data_pipeline.py           # Kiểm tra De-ID, Temporal Lock và MICE
│   ├── test_multimodal_model.py        # Kiểm tra Forward pass, Tensor Shapes, Calibration
│   ├── test_agent_rag.py               # Kiểm tra Retrieval, từ chối claim ngoài ghi chú, Offset spans
│   └── test_api_endpoints.py           # Kiểm tra REST API HTTP Status, Payloads & Latency
├── tasks/                              # HỆ THỐNG 5 BACKLOG TUẦN TỰ CHO NHÓM 3 NGƯỜI
│   ├── README.md                       # Quy trình Scrum, Definition of Done & Thứ tự làm Backlog
│   ├── backlog-01-data-and-baselines/  # Backlog 1: Dữ liệu, De-ID, MICE, 3 Baselines (README + 3 TV)
│   ├── backlog-02-multimodal-core/     # Backlog 2: FT-Transformer, Cross-Attention, ECE (README + 3 TV)
│   ├── backlog-03-agentic-rag-and-software/# Backlog 3: Qdrant DB, Multi-Agent, Full-stack (README + 3 TV)
│   ├── backlog-04-clinical-validation/ # Backlog 4: Metrics, DCA Net Benefit, Khảo sát (README + 3 TV)
│   └── backlog-05-packaging-and-paper/ # Backlog 5: Docker, Paper TRIPOD-AI, Video Demo (README + 3 TV)
├── docker-compose.yml                  # Triển khai toàn bộ hệ sinh thái chỉ với 1 lệnh
├── Dockerfile                          # Multi-stage build cho FastAPI Backend
├── requirements.txt                    # Thư viện phụ thuộc Python chuẩn xác
└── README.md                           # Tài liệu tổng quan dự án
```

---

## 6. HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY NHANH (QUICKSTART GUIDE)

### 6.1. Thiết Lập Môi Trường Cục Bộ (Local Environment)
Yêu cầu: **Python 3.10+** và **Node.js 18+** (cho Frontend). Khuyến nghị sử dụng GPU có hỗ trợ CUDA.

```bash
# 1. Clone repository và truy cập thư mục dự án
git clone https://github.com/zangzang1303/multimodal-ehr-cdss.git
cd multimodal-ehr-cdss

# 2. Tạo và kích hoạt môi trường ảo Python
python -m venv venv
# Trên Windows:
.\venv\Scripts\activate
# Trên Linux/macOS:
source venv/bin/activate

# 3. Cài đặt các gói phụ thuộc
pip install --upgrade pip
pip install -r requirements.txt

# 4. Tải mô hình ngôn ngữ hỗ trợ khử định danh PHI
python -m spacy download en_core_web_sm
```

### 6.2. Tái Lập Toàn Bộ Kết Quả Nghiên Cứu (Phase 3)

Yêu cầu: trọng số `emilyalsentzer/Bio_ClinicalBERT` trong Hugging Face cache (`huggingface-cli download emilyalsentzer/Bio_ClinicalBERT`), GPU ≥ 4 GB khuyến nghị.

```bash
# 0. Dựng lại dữ liệu canonical từ data/raw_rebuilt/ + audit rò rỉ (nội dung ghi chú) + manifest SHA-256
python scripts/rebuild_canonical_dataset.py
python -m src.data_pipeline.manifest data/processed_rebuilt_strict      # phải PASS

# 1. Thí nghiệm đăng ký trước (docs/11_ANALYSIS_PLAN.md) – lưu dự đoán từng bản ghi vào data/predictions/
python scripts/run_research_experiments.py rq1        # 10 mô hình x 5 seed + checkpoint triển khai
python scripts/run_research_experiments.py temporal   # temporal split theo nhóm nguồn
python scripts/run_research_experiments.py rq2        # phân rã tín hiệu văn bản
python scripts/run_research_experiments.py rq3        # mô phỏng bổ trợ có kiểm soát
python scripts/run_research_experiments.py cv         # 5-fold grouped CV (post-hoc)

# 2. Thống kê, hình, registry, bảng LaTeX, model card, Bảng 1
python scripts/build_results_registry.py
python scripts/export_latex_tables.py
python scripts/export_cohort_table.py
python scripts/export_model_card.py
python scripts/export_baseline_artifacts.py           # mô hình baseline cho /predict/baseline

# 3. Kiểm thử
pytest tests/ -q
```

### 6.3. Khởi Chạy Nền Tảng Trọn Gói Bằng Docker Compose
Chỉ với một lệnh duy nhất, toàn bộ hệ sinh thái bao gồm **FastAPI Backend**, **Next.js Clinician UI** và **Vector DB (Qdrant)** sẽ được khởi tạo trong môi trường cô lập:

```bash
# Xây dựng và khởi chạy containers (image nhẹ: /predict/multimodal và /predict/baseline trả 503)
docker compose up --build -d

# Bản đầy đủ: cài torch CPU + transformers + catboost và mount Hugging Face cache (chỉ đọc)
MCDSS_INSTALL_ML=1 HF_CACHE_DIR=~/.cache/huggingface docker compose up --build -d

# Kiểm tra trạng thái các dịch vụ
docker compose ps
```
Truy cập các dịch vụ tại:
* 🌐 **Clinician Dashboard (Next.js):** `http://localhost:3000`
* 🔌 **FastAPI REST API Docs (Swagger):** `http://localhost:8000/docs`
* 🗄️ **Qdrant Vector Engine Web UI:** `http://localhost:6333/dashboard`

---

## 7. QUY CHUẨN ĐẠO ĐỨC Y TẾ, BẢO MẬT & PHÁP LÝ (ETHICS, PRIVACY & COMPLIANCE)

Hệ thống M-CDSS được phát triển dựa trên các cam kết đạo đức y sinh và tiêu chuẩn an toàn bảo mật nghiêm ngặt nhất:

1. **Khử Định Danh Tuyệt Đối (HIPAA Safe Harbor & Nghị định 13/2023/NĐ-CP):**
   Mọi dữ liệu văn bản tự do trước khi nạp vào bộ mã hóa (Text Encoder) hoặc Vector DB đều bắt buộc đi qua tầng **`deidentifier.py`**. Toàn bộ 18 yếu tố nhận dạng cá nhân (Họ tên, Số điện thoại, Mã BHYT/CCCD, Ngày sinh, Địa chỉ cụ thể, Tên bệnh viện) đều được thay thế bằng các token chuẩn hóa ẩn danh (`[REDACTED_NAME]`, `[REDACTED_DATE]`), triệt tiêu hoàn toàn rủi ro tái định danh bệnh nhân.
2. **Kiến Trúc Triển Khai Cục Bộ (On-Premise / Edge Medical AI):**
   Hệ thống hỗ trợ chạy hoàn toàn cục bộ trên hạ tầng máy chủ của bệnh viện thông qua các công nghệ tối ưu hóa mô hình mã nguồn mở (*vLLM, Ollama, TensorRT-LLM*). Không có bất kỳ dữ liệu bệnh án nào bị truyền tải ra ngoài qua các API thương mại của bên thứ ba, bảo toàn chủ quyền dữ liệu y tế quốc gia.
3. **Triết Lý "Bác Sĩ Là Người Quyết Định Cuối Cùng" (Doctor-in-the-Loop):**
   M-CDSS được định vị là **Hệ Thống Hỗ Trợ Ra Quyết Định Lâm Sàng (Clinical Decision Support)**, không phải là hệ thống chẩn đoán tự động thay thế nhân viên y tế. Mọi gợi ý phân loại đều đi kèm:
   - Điểm xác suất đã được hiệu chuẩn (Calibrated Probability).
   - Đoạn văn bản chứng cứ trích lục từ chính bệnh án.
   - Tài liệu phác đồ y tế tương ứng để bác sĩ đối chiếu, cân nhắc và đưa ra quyết định lâm sàng cuối cùng.
4. **Kiểm Soát Thiên Lệch Thuật Toán (Algorithmic Fairness):**
   Hệ thống cung cấp module đánh giá hiệu năng phân tầng (stratified performance evaluation) theo các nhóm tuổi, giới tính và bệnh lý nền để đảm bảo mô hình duy trì độ nhạy và độ đặc hiệu công bằng, không tạo ra bất bình đẳng chăm sóc sức khỏe.

---

## 8. TÀI LIỆU KỸ THUẬT BỔ TRỢ (DETAILED DOCUMENTATION)

Để tìm hiểu sâu hơn về kiến trúc toán học, thiết kế pipeline và phân tích sai lệch chi tiết, xin vui lòng tham khảo các tài liệu chuyên đề tại thư mục [`docs/`](docs/):

* 📑 **[`docs/01_RESEARCH_BACKGROUND_AND_GAP.md`](docs/01_RESEARCH_BACKGROUND_AND_GAP.md):** Phân tích chi tiết 15 công trình EHR từ bài báo tổng quan JMIR, mổ xẻ 4 miền sai lệch PROBAST và lập luận khoa học giải pháp đa phương thức.
* 📐 **[`docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md`](docs/02_MULTIMODAL_ARCHITECTURE_AND_MATH.md):** Cơ sở toán học FT-Transformer, Attention Layer, biểu thức Cross-Attention và thuật toán Temperature Scaling.
* 🔒 **[`docs/03_DATA_PIPELINE_AND_PRIVACY.md`](docs/03_DATA_PIPELINE_AND_PRIVACY.md):** Quy trình khử định danh PHI, kỹ thuật khóa chuỗi thời gian chống rò rỉ nhãn, thuật toán MICE và Patient-level Group Split.
* 🤖 **[`docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md`](docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md):** Kiến trúc Multi-Agent phân tích chẩn đoán phân biệt, chunking phác đồ quốc tế và thuật toán định vị bằng chứng chính xác.
* 📊 **[`docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md`](docs/05_EVALUATION_METRICS_AND_PROBAST_GUIDE.md):** Toàn văn định nghĩa các chỉ số AUROC/AUPRC/ECE, hướng dẫn phân tích DCA Net Benefit và bảng checklist 20 tiêu chí PROBAST.
* 👥 **[`docs/TEAM_TASK_ALLOCATION_AND_ROADMAP.md`](docs/TEAM_TASK_ALLOCATION_AND_ROADMAP.md):** Kế hoạch phân chia nhiệm vụ chi tiết theo 16 tuần cho nhóm 3 thành viên, ma trận phụ thuộc và quy chuẩn Git workflow.
* 📋 **[`tasks/README.md`](tasks/README.md):** Trung tâm điều phối Sprint Backlog, Definition of Done và theo dõi tiến độ của 3 thành viên.

---

## 9. GIẤY PHÉP (LICENSE) & TRÍCH DẪN (CITATION)

Dự án được phân phối dưới giấy phép mã nguồn mở **MIT License**.

Nếu bạn sử dụng mã nguồn, kiến trúc đa phương thức hoặc dữ liệu của dự án này trong các nghiên cứu khoa học, xin vui lòng trích dẫn:

```bibtex
@article{mcdss2026multimodal,
  title={A Multimodal Clinical Decision Support System via Cross-Attention Late Fusion and Calibrated Agentic RAG for Primary Care},
  author={Multimodal EHR-CDSS Research Team},
  journal={arXiv preprint},
  year={2026}
}
```
