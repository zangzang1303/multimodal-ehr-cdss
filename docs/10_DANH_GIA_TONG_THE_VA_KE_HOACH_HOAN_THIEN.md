# ĐÁNH GIÁ TỔNG THỂ DỰ ÁN M-CDSS & KẾ HOẠCH HOÀN THIỆN ĐẾN BUỔI BẢO VỆ

> Ngày rà soát: 2026-11-18 · Phạm vi: toàn bộ repo tại commit `2e84ebe` (sau "hoàn thành tuần 7").
> Mọi nhận định dưới đây đều kèm bằng chứng có thể chạy lại (đường dẫn file, lệnh, số liệu).

---

## 1. KẾT LUẬN NHANH

| Hạng mục | Trạng thái | Ghi chú ngắn |
| :--- | :---: | :--- |
| Giai đoạn 1 (Backlog 01–03) | ✅ Đạt | Pipeline, strict split (audit `passed: true`), 3 baseline có số liệu thật. |
| Backlog 04 – Multimodal core | ⚠️ Đạt một phần | Ablation thật (1 seed); **checkpoint đang dùng đã bị ghi đè bởi lần chạy 0 epoch**. |
| Backlog 05 – Agentic RAG & full-stack | ❌ Chưa đạt | **Endpoint `/agent/explain` đang lỗi**; agent là rule-based, chưa có LLM; KB chỉ 14 chunk. |
| Backlog 06 – Clinical validation | ❌ Chưa đạt | DCA/benchmark/fairness tính trên **mô hình sai** (AUROC 0,58) và **tập test sai** (N=287). Chưa có CI cho so sánh, chưa có leave-source-out. |
| Backlog 07 – Packaging & paper | ⚠️ Đạt một phần | Docker, LICENSE/NOTICE, PROBAST, PHI audit có; **bài báo còn 20 `[TODO]`**, kịch bản slide còn 21 placeholder, 12 tài liệu tham khảo. |
| `pytest tests/` | ❌ **13 failed, 2 errors, 76 passed** | DoD cuối cùng yêu cầu 100% pass. |

**Tóm lại:** phần "khung" (code, tài liệu, giao diện) đã rộng và khá đầy đủ, nhưng **chuỗi bằng chứng khoa học đang đứt** ở 3 chỗ: (1) checkpoint/kết quả đánh giá không nhất quán, (2) nhánh văn bản không mang thông tin độc lập với dữ liệu bảng, (3) lớp giải trình chưa chạy được end-to-end. Chưa thể bảo vệ như một bài nghiên cứu cho đến khi sửa 3 điểm này.

---

## 2. CÁC PHÁT HIỆN NGHIÊM TRỌNG (P0 – PHẢI SỬA TRƯỚC KHI VIẾT TIẾP)

### P0-1. Số liệu Giai đoạn 2 mâu thuẫn nhau: hai "mô hình M-CDSS" khác nhau
| Nguồn | N test | Macro AUROC | ECE |
| :--- | :---: | :---: | :---: |
| `data/ablation_results.json` → `cross_attention` (GPU, 2026-11-05) | 302 | **0,959** | 0,097 |
| `data/multimodal_training_results.json` (CPU, `best_epoch: 0`) | 286 | 0,552 | 0,334 |
| `data/benchmark_summary.json`, `clinical_utility_metrics.json`, `dca_curve.png` | 287 | 0,588 | 0,479 |
| `data/fairness_report.json` | 286 | 0,55–0,64 | – |

**Nguyên nhân (đã xác minh):**
1. `data/checkpoints/multimodal_best.pt` có `training_metadata = {best_epoch: 0, epochs_total: 0, best_val_loss: 0.0}` → bị ghi đè ở commit `01ffef7` bởi một lần chạy `train_multimodal.py` không huấn luyện.
2. Cả ba nơi đều **âm thầm fallback sang BERT khởi tạo ngẫu nhiên** (`AutoModel.from_config`) khi thiếu trọng số. *(Đính chính 2026-11-23: trên máy rà soát, snapshot `d5892b39…` thực ra có `pytorch_model.bin` đầy đủ, chỉ các blob tải dở là `.incomplete`; lần đánh giá AUROC 0,58 nhiều khả năng chạy trên máy khác thiếu trọng số. Lỗi fallback vẫn có thật và đã được sửa.)* Các vị trí:
   `src/models/text_encoder.py` (khối `except OSError`), `scripts/train_multimodal.py` (~dòng 160–165), `scripts/evaluate_clinical_utility.py` (dòng 276–283).
   → Embedding văn bản là nhiễu ⇒ AUROC ≈ 0,55–0,59.
3. Các file `.parquet` **không được git theo dõi** → mỗi thành viên có tập dữ liệu khác nhau. Phân bố lớp của tập test N=287 (69/72/74/72) **khác** strict test chính thức (71/71/106/54).

**Hệ quả:** DCA, fairness, confusion matrix, benchmark endpoint và mọi biểu đồ Backlog 06 hiện **không dùng được** trong báo cáo.

### P0-2. Nhánh văn bản không mang thông tin độc lập (shortcut / dư thừa phương thức)
- Ghi chú lâm sàng được **sinh theo template** (trung vị 94 từ) và **chứa lại sinh hiệu/xét nghiệm** (`BP: 126.8/80.7 mmHg, HR…, SpO2…`).
- Thử nghiệm đối chứng nhanh (TF-IDF + Logistic Regression, train → strict test, chạy lại được):

| Biến thể đầu vào | Macro AUROC |
| :--- | :---: |
| Văn bản gốc | 0,922 |
| Văn bản đã thay mọi con số bằng `<NUM>` | **0,553** (≈ đoán ngẫu nhiên) |
| Chỉ 9 biến số dạng bảng (Logistic Regression) | 0,920 |

- Phần văn bản tự sự lấy từ MTSamples **không khớp chẩn đoán** (từ khoá có trọng số cao: *testis, cystoscopy, hand, hip…*).

**Hệ quả:** Kết luận hiện tại "văn bản bổ trợ cho dữ liệu bảng" / "Bio_ClinicalBERT 0,973 vượt trội" **không được dữ liệu ủng hộ**. Mô hình text đang đọc lại các con số. Đây vừa là rủi ro lớn nhất khi bị phản biện, vừa là **cơ hội biến thành đóng góp khoa học** (xem mục 4).

### P0-3. Lớp giải trình (Agentic RAG) không chạy end-to-end
- `src/api/routes/agent_chat.py:233` gọi `EvidenceGrounder.ground_evidence_claims` – **phương thức không tồn tại** → `POST /api/v1/agent/explain` lỗi 500.
- `src/agent/evidence_grounder.py:254` dùng `difflib` nhưng không import.
- Schema `AgentExplainRequest` lệch với test (pydantic ValidationError).
- `diagnostic_agent.py` / `diagnostic_graph.py`: suy luận là **template theo luật**, chưa có LLM; header file vẫn ghi "MOCK / STAND-IN".

### P0-4. Kết quả "giả lập" trong luồng demo
- `POST /api/v1/predict/baseline` (`src/api/routes/inference.py`) **gán cứng** kết quả cho `PT-0044`, `PT-0254` và dùng luật từ khoá cho các ca khác. Frontend gọi endpoint này (`frontend/src/lib/api.ts:116`) và `/predict/mock` (`api.ts:284`).
- Nếu trình chiếu case study bằng các endpoint này mà gọi là "dự đoán của mô hình" → vi phạm liêm chính nghiên cứu.

### P0-5. Khử định danh chưa đạt trên dữ liệu đã xử lý
Trên `data/processed_rebuilt_strict/*.parquet` (PHI là giả lập, nhưng mâu thuẫn với tuyên bố trong báo cáo):

| Mẫu còn sót | train | val | test |
| :--- | :---: | :---: | :---: |
| Mã BHYT/Insurance chưa che | 85,4% | 83,2% | 83,1% |
| Tên bác sĩ có học hàm (BS., ThS.BS., PGS.TS., BS.CKI/II) | 71,8% | 72,2% | 72,8% |

### P0-6. Tự đánh giá PROBAST+AI quá lạc quan
`docs/08_PROBAST_AI_AUDIT_REPORT.md` chấm **Low risk ở cả 4 miền**. Với dữ liệu tổng hợp (Synthea), ghi chú ghép ngẫu nhiên từ MTSamples, một split duy nhất, N test = 302, chưa có CI → miền Participants/Outcome nên là **High**, Analysis ít nhất **Unclear**. Hội đồng có kinh nghiệm sẽ bắt lỗi này ngay.

---

## 3. CÁC THIẾU HỤT P1 (ẢNH HƯỞNG CHẤT LƯỢNG NGHIÊN CỨU)

1. **Một seed, một split** – không có mean ± SD, không có CI 95% cho chênh lệch AUROC giữa các mô hình; chưa lưu dự đoán từng mẫu (`.npz`) nên không làm paired bootstrap/DeLong/DCA so sánh được.
2. **So sánh chưa công bằng** – text-only baseline fine-tune khối cuối, còn nhánh text trong fusion bị đóng băng (ghi chú ngay trong `ablation_results.json`). Thiếu các baseline đơn giản mà phản biện sẽ hỏi: LR trên bảng, TF-IDF+LR, **ensemble trung bình xác suất CatBoost + BERT**.
3. **Fusion chưa vượt text-only**: 0,959 (cross-attn, frozen) < 0,973 (BERT fine-tune). ECE 0,097 không đạt mục tiêu < 0,05.
4. **Chưa có kiểm tra tổng quát hoá** (leave-source-out / temporal) và **kiểm tra thiếu phương thức** (missing modality) – đây là lợi thế thực tế quan trọng nhất của fusion.
5. **RAG chưa được đánh giá**: `data/retrieval_queries_member3.json` chỉ có vài truy vấn; chưa có Recall@k / MRR; KB 14 chunk diễn giải; phần giấy phép ghi GINA/GOLD "FAIR guidelines permit" là không chính xác (đây là tài liệu có bản quyền – chỉ trích dẫn ngắn & diễn giải).
6. **Chưa đo latency p50/p95**, chưa có CI (GitHub Actions), `qdrant/qdrant:latest` chưa pin phiên bản.
7. **Bài báo**: 20 `[TODO]`, 12 tài liệu tham khảo (một bài nghiên cứu y sinh AI thường 35–60), chưa có checklist TRIPOD+AI điền số trang, chưa có flow diagram dữ liệu.

---

## 4. ĐỊNH HƯỚNG LẠI CÂU CHUYỆN NGHIÊN CỨU (KHUYẾN NGHỊ)

Thay vì cố chứng minh "M-CDSS vượt trội" (dữ liệu không ủng hộ), hãy trình bày **một nghiên cứu trung thực, có phương pháp chặt chẽ** – loại bài hội đồng đánh giá cao hơn:

**Tên đề xuất:** *"Dung hợp đa phương thức EHR cho hỗ trợ chẩn đoán bệnh hô hấp – tim mạch: đánh giá có kiểm soát rò rỉ, dư thừa phương thức và một nguyên mẫu CDSS có hiệu chuẩn & giải trình kiểm chứng được."*

**Câu hỏi nghiên cứu:**
- **RQ1** – Dưới so sánh công bằng (cùng backbone, nhiều seed, CI), cross-attention có vượt mô hình đơn phương thức tốt nhất và các cách dung hợp đơn giản không?
- **RQ2** – Tín hiệu của nhánh văn bản đến từ đâu? (phân rã: văn bản gốc / che số / bỏ khối sinh hiệu / chỉ phần tự sự)
- **RQ3** – Khi nào fusion thực sự có ích? (thí nghiệm mô phỏng có kiểm soát mức độ bổ trợ ρ giữa văn bản và bảng)
- **RQ4** – Mô hình có hiệu chuẩn, có lợi ích ròng (DCA) và bền vững khi thiếu một phương thức không?
- **RQ5** – Lời giải trình có được neo vào bằng chứng (grounding) và truy xuất đúng phác đồ không?

**Đóng góp có thể bảo vệ:**
1. Pipeline dữ liệu kiểm toán rò rỉ + strict patient split (đã có).
2. Phân tích phát hiện **dư thừa phương thức/shortcut** trong benchmark EHR tổng hợp – bài học phương pháp luận có giá trị chung.
3. Thí nghiệm bổ trợ có kiểm soát cho thấy điều kiện để cross-attention mang lại lợi ích.
4. Nguyên mẫu CDSS mã nguồn mở: xác suất hiệu chuẩn, giải trình có offset kiểm chứng, đóng gói Docker tái lập được.

---

## 5. KẾ HOẠCH HÀNH ĐỘNG

Chi tiết từng nhiệm vụ, người phụ trách và tiêu chí nghiệm thu nằm trong
[`tasks/phase-03-research-hardening/`](../tasks/phase-03-research-hardening/README.md):

| Backlog | Thời lượng | Mục tiêu | Mức ưu tiên |
| :---: | :---: | :--- | :---: |
| **08** – Toàn vẹn & tái lập | Tuần 1 | Sửa P0-1…P0-6, test xanh 100%, một nguồn dữ liệu/kết quả duy nhất | **Bắt buộc** |
| **09** – Nâng tầm nghiên cứu | Tuần 2 | RQ1–RQ5: so sánh công bằng, CI, phân rã tín hiệu văn bản, mô phỏng bổ trợ, DCA, robustness, đánh giá RAG | Bắt buộc (lõi) + tuỳ chọn |
| **10** – Bản thảo, ứng dụng & bảo vệ | Tuần 3 | Điền bài báo từ registry kết quả, demo, video, slide, tổng duyệt | **Bắt buộc** |

> Nếu thời gian đến buổi bảo vệ < 3 tuần: làm toàn bộ Backlog 08, phần **[CORE]** của Backlog 09 (M1-1.1, 1.2, 1.3; M2-2.1, 2.2; M3-3.1) và Backlog 10. Các mục **[OPTIONAL]** chuyển thành "Hướng phát triển".
