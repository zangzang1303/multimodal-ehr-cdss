# QUẢN LÝ TIẾN ĐỘ THEO TỪNG BACKLOG DỰ ÁN M-CDSS
### Quy Trình Thực Thi 2 Giai Đoạn Cho Nhóm 3 Thành Viên

Dự án được tái cấu trúc thành **2 Giai đoạn chiến lược**:
* **Giai đoạn 1 (Nghiên cứu & Đề xuất - Tuần 1 đến Tuần 3):** Tập trung xây dựng nền tảng dữ liệu y tế chuẩn mực (chống rò rỉ nhãn, khử định danh PHI, gán khuyết MICE), huấn luyện và đo đạc toàn diện **3 Mô hình Nền tảng (Baselines)** đại diện cho dữ liệu đơn phương thức, phân tích điểm mù lâm sàng và hoàn thiện **Báo Cáo Đề Xuất Phương Án Tối Ưu**.
* **Giai đoạn 2 (Phát triển & Hiện thực hóa - Tuần 4 trở đi):** Hiện thực hóa kiến trúc đề xuất (Multimodal Cross-Attention Late Fusion), hiệu chuẩn xác suất lâm sàng ($ECE < 0.05$), tích hợp Agentic RAG giải trình, xây dựng Full-Stack Clinician Dashboard, phân tích lợi ích DCA và đóng gói Docker.

Nguyên tắc quản trị cốt tử:
> **"Làm xong nghiệm thu đầy đủ từng Backlog thì mới chuyển sang Backlog kế tiếp."**

> 📖 **CẨM NANG KỸ THUẬT CHI TIẾT GIAI ĐOẠN 1:**
> Trước khi bắt tay vào code, toàn bộ 3 thành viên bắt buộc phải đọc tệp đặc tả chi tiết:
> 👉 [`docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md`](../docs/PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md)
> Tệp này quy định chi tiết: cấu trúc từng file code, class, function signature, cách lưu file kết quả (`.parquet`, `.json`, `.png`) và danh mục tài liệu tham khảo khoa học (JMIR, FT-Transformer, ClinicalBERT, PROBAST).

Trong mỗi thư mục Backlog luôn bao gồm đúng **4 tệp tiêu chuẩn**:
1. `README.md`: Bối cảnh kỹ thuật, mục tiêu tuần, điều kiện đầu vào (Prerequisites) và Tiêu chuẩn nghiệm thu (Definition of Done).
2. `MEMBER_1.md`: Nhiệm vụ chi tiết cho **Thành viên 1** (Lead ML / Modeling & Evaluation).
3. `MEMBER_2.md`: Nhiệm vụ chi tiết cho **Thành viên 2** (Biomedical Data Engineer & Privacy).
4. `MEMBER_3.md`: Nhiệm vụ chi tiết cho **Thành viên 3** (Full-Stack AI & System Integrator).

---

## 1. CẤU TRÚC THƯ MỤC CÁC BACKLOG

```
tasks/
├── README.md                                                 # Hướng dẫn tổng thể quy trình tuần tự (File này)
│
├── 🌟 GIAI ĐOẠN 1: NGHIÊN CỨU 3 BASELINES & ĐỀ XUẤT PHƯƠNG ÁN TỐI ƯU
│   ├── backlog-01-week-01-setup-and-data/                    # BACKLOG 01 (TUẦN 1): Môi trường, Data Contract & Dữ liệu thô
│   │   ├── README.md                                         # Hướng dẫn & Tiêu chuẩn nghiệm thu Tuần 1
│   │   ├── MEMBER_1.md                                       # Cấu hình siêu tham số & chuẩn bị framework GPU
│   │   ├── MEMBER_2.md                                       # Schema dữ liệu lâm sàng & sinh tập dữ liệu thô
│   │   └── MEMBER_3.md                                       # Khung FastAPI, Next.js 14 & Pydantic Schemas
│   │
│   ├── backlog-02-week-02-data-pipeline-and-privacy/         # BACKLOG 02 (TUẦN 2): Data Pipeline, De-ID, Temporal Lock & Khung Baselines
│   │   ├── README.md                                         # Hướng dẫn & Tiêu chuẩn nghiệm thu Tuần 2
│   │   ├── MEMBER_1.md                                       # Khung 3 Baselines (XGBoost, FT-Tabular, Bio_ClinicalBERT)
│   │   ├── MEMBER_2.md                                       # De-identification, Temporal Aligner & MICE Imputer
│   │   └── MEMBER_3.md                                       # Unit Tests Pipeline dữ liệu & Giao diện Form nhập liệu
│   │
│   └── backlog-03-week-03-baselines-and-proposal/            # BACKLOG 03 (TUẦN 3): Patient Split, Benchmark & Đề Xuất Tối Ưu
│       ├── README.md                                         # Hướng dẫn & Tiêu chuẩn nghiệm thu Tuần 3 (Mốc chuyển giao)
│       ├── MEMBER_1.md                                       # Huấn luyện 3 Baselines, đo chỉ số & xuất baseline_results.json
│       ├── MEMBER_2.md                                       # Patient-Level Group Split, PyTorch Dataset & Error Analysis
│       └── MEMBER_3.md                                       # Dashboard so sánh Baselines & Biên soạn Báo cáo Đề xuất Tối ưu
│
└── 🚀 GIAI ĐOẠN 2: HIỆN THỰC HÓA PHƯƠNG ÁN ĐỀ XUẤT (PHÁT TRIỂN & XÁC THỰC)
    └── phase-02-development/
        ├── backlog-04-multimodal-core/                       # Backlog 4: FT-Transformer, Cross-Attention & Calibration
        ├── backlog-05-agentic-rag-and-software/              # Backlog 5: Qdrant Vector DB, Evidence Grounder & Full-stack Web
        ├── backlog-06-clinical-validation/                   # Backlog 6: Đo đạc AUROC, DCA Net Benefit & Kiểm toán PROBAST
        └── backlog-07-packaging-and-paper/                   # Backlog 7: Đóng gói Docker Compose, Báo cáo TRIPOD-AI & Demo
```

---

## 2. LỘ TRÌNH 3 TUẦN GIAI ĐOẠN 1 (PHASE 1 SPRINT MILESTONES)

```
   ┌────────────────────────────────────────────────────────┐
   │ BACKLOG 01 (TUẦN 1): SETUP, CONTRACT & RAW DATA        │
   │ • CUDA GPU, Python env, configs/model_config.yaml      │
   │ • configs/data_schema.yaml (9 biến số, 4 phân loại)    │
   │ • data/raw/patients_raw.parquet + clinical_notes.jsonl │
   │ • Khung FastAPI /health & Next.js 14 khởi động         │
   └───────────────────────────┬────────────────────────────┘
                               │ Pass kiểm tra môi trường & Data contract hoàn tất
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ BACKLOG 02 (TUẦN 2): DATA PIPELINE, DE-ID & 3 BASELINES│
   │ • De-ID HIPAA Regex + spaCy NER ([REDACTED_*])         │
   │ • Temporal Aligner: t_event < t_diag & Blacklist FEV1  │
   │ • MICE Imputer: IterativeImputer + Binary Indicators   │
   │ • Khung 3 Baselines: XGBoost, FT-Tabular, ClinicalBERT │
   │ • Pytest tests/test_data_pipeline.py pass 100%         │
   └───────────────────────────┬────────────────────────────┘
                               │ Pass 100% tests dữ liệu & Khung baseline sẵn sàng
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ BACKLOG 03 (TUẦN 3): BENCHMARK & ĐỀ XUẤT TỐI ƯU        │
   │ • Patient-Level Group Split 70/15/15 (data/processed/) │
   │ • Huấn luyện xong 3 Baselines -> baseline_results.json │
   │ • Error Analysis: Phân tích các ca bệnh dự đoán sai    │
   │ • Soạn thảo Báo cáo Đề Xuất Kiến Trúc Multimodal Tối Ưu│
   └───────────────────────────┬────────────────────────────┘
                               │ NGHIỆM THU HOÀN TẤT GIAI ĐOẠN 1
                               ▼
            CHUYỂN SANG GIAI ĐOẠN 2: PHÁT TRIỂN MÔ HÌNH
```

---

## 3. TRUY CẬP NHANH CÁC BACKLOG GIAI ĐOẠN 1

| Backlog | Thư Mục | Trọng Tâm Nghiên Cứu & Kỹ Thuật | Trạng Thái | Link Điều Hướng |
| :---: | :--- | :--- | :---: | :--- |
| **01** | `backlog-01-week-01-setup-and-data` | Thiết lập môi trường, hợp đồng dữ liệu lâm sàng, dữ liệu thô và khung ứng dụng | **SẴN SÀNG LÀM** | [Xem Backlog 1](backlog-01-week-01-setup-and-data/README.md) |
| **02** | `backlog-02-week-02-data-pipeline-and-privacy` | Pipeline khử định danh PHI, khóa chuỗi thời gian chống rò rỉ nhãn, MICE và dựng khung 3 Baselines | *Chờ Tuần 1* | [Xem Backlog 2](backlog-02-week-02-data-pipeline-and-privacy/README.md) |
| **03** | `backlog-03-week-03-baselines-and-proposal` | Patient Split, huấn luyện 3 Baselines, đo đạc benchmark, phân tích sai số và Báo cáo Đề xuất Tối ưu | *Chờ Tuần 2* | [Xem Backlog 3](backlog-03-week-03-baselines-and-proposal/README.md) |
