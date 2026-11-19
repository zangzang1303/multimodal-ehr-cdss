# Tài Liệu Q&A Bảo Vệ Hệ Thống & Kiến Trúc (Thành Viên 3 — Backlog 10 Nhiệm Vụ 3.5)

> Tài liệu chuẩn bị câu trả lời ngắn gọn, dựa trên số liệu đo đạc thực tế của hệ thống cho buổi bảo vệ đề tài **M-CDSS** (Phase 3 Research Hardening).  
> Các giá trị thực nghiệm về RAG và Latency dưới đây trích trực tiếp từ `results/rag_evaluation_report.json` và `results/latency_report.json` (`is_mock: false`).

---

## Câu hỏi 1: Vì sao nhóm chọn Qdrant thay vì chỉ tìm kiếm bằng vòng lặp Python hoặc BM25 đơn thuần?

**Trả lời ngắn:**
1. **Tách biệt dịch vụ & Khả năng mở rộng chỉ mục vector:** Qdrant chạy như một container độc lập (được ghim cố định phiên bản **`qdrant/qdrant:v1.20.0`** trong `docker-compose.yml`), tách trạng thái vector index (`clinical_guidelines`, 768 chiều, 70 vector từ 64 đoạn JSON phác đồ + 6 đoạn hạt giống) khỏi tầng API FastAPI không trạng thái (`stateless`).
2. **Truy vấn có lọc metadata & Hybrid RRF:** Qdrant hỗ trợ lọc có cấu trúc theo siêu dữ liệu nguồn (`source_id`, `disease_entity`, `evidence_level` — đặc biệt bảo toàn `evidence_level: null` cho tài liệu Bộ Y tế VN 2020 thay vì gán tùy tiện), rồi kết hợp với BM25 qua *Reciprocal Rank Fusion* (RRF).
3. **Dự phòng an toàn & Kết quả thực nghiệm trung thực:** Trong trường hợp ngoại tuyến thiếu trọng số `all-mpnet-base-v2`, `retriever.py` / `knowledge_ingest.py` tự động chuyển sang vector băm 768 chiều tất định để hệ thống không treo. Thực nghiệm trên **60 truy vấn gán nhãn kép ($\kappa = 0,9725$)** cho thấy ở chế độ ngoại tuyến băm 768 chiều, `bm25_only` đạt `Recall@1 = 0,9500` (`MRR = 0,9750`) còn `hybrid_rrf` đạt `Recall@1 = 0,8667`, `MRR = 0,9067` và **`Recall@5 = 1,0000`**. Khi nạp trọng số dense y sinh đầy đủ ở môi trường trực tuyến, nhánh Qdrant dense phát huy vai trò xử lý đồng nghĩa lâm sàng mà từ khóa thưa dễ bỏ sót.

---

## Câu hỏi 2: Cơ chế Grounding chống ảo giác (`EvidenceGrounder`) bảo đảm độ an toàn đến mức nào?

**Trả lời ngắn:**
1. **Cơ chế hoạt động:** Mọi nhận định bằng chứng sau bước suy luận đều phải đi qua cổng kiểm chứng tọa độ ký tự `EvidenceGrounder` (`src/agent/evidence_grounder.py`) với độ phức tạp tuyến tính $\mathcal{O}(N)$. Một nhận định chỉ được gắn nhãn `verified` và cấp cặp chỉ số `[start_char, end_char]` khi khớp trực tiếp (hoặc khớp chuẩn hóa có kiểm soát qua `difflib` kèm ngưỡng tương đồng chặt) với văn bản bệnh án gốc $T$.
2. **Kết quả kiểm định định lượng trên 50 ca lâm sàng (`results/rag_evaluation_report.json`):**
   * **Tỷ lệ neo đúng nhận định thật:** **100 / 100 (`1,00`)** nhận định hợp lệ đều khớp vị trí ký tự thực (`span_substring_match_rate = 1,00`).
   * **Tỷ lệ chặn ảo giác tiêm nhiễu:** **50 / 50 (`1,00`)** nhận định giả mạo (*injected hallucination probes*) bị phát hiện và bác bỏ hoàn toàn trước khi trả về API/UI.
   * **Độ chính xác ngữ nghĩa kiểm tra thủ công:** **20 / 20 (`1,00`)** đoạn trích mẫu đều bảo toàn ngữ cảnh bệnh sử (không cắt cụt phủ định hoặc đảo nghĩa).
3. **Giới hạn trung thực của Grounding:** Hiện hệ thống mặc định chạy ở chế độ **`reasoning_mode = "deterministic_template"`** để đảm bảo 0% tự bịa nội dung mới. Grounding chứng minh **bằng chứng trích dẫn thực sự tồn tại trong ghi chú đầu vào**, nhưng không thay thế trách nhiệm thẩm định tính xác thực của bản thân ghi chú do người nhập gõ sai.

---

## Câu hỏi 3: Độ trễ thực tế của hệ thống là bao nhiêu và có chạy thuần CPU (không GPU) được không?

**Trả lời ngắn:**
1. **Có thể chạy hoàn toàn trên CPU** cho luồng giải trình RAG + Grounding và suy luận nhẹ, với kết quả đo thực tế bởi `scripts/benchmark_latency.py` (200 lượt gọi ấm sau 1 lượt khởi động nguội, bệnh án 340 ký tự, CPU *Windows 11 AMD64, 16 logical cores*):
   * `POST /api/v1/agent/explain` (**HTTP 200**): Cold = `192,54 ms` | Warm Mean = `9,46 ms` | **$p_{50} = 9,15\text{ ms}$** | **$p_{95} = 11,46\text{ ms}$** | $p_{99} = 15,08\text{ ms}$.
   * `POST /api/v1/predict/baseline` (**HTTP 200** fallback): Cold = `4,19 ms` | Warm Mean = `3,75 ms` | $p_{50} = 3,66\text{ ms}$ | $p_{95} = 4,74\text{ ms}$.
   * `POST /api/v1/predict/multimodal`: Trên máy thiếu bộ nhớ đệm ngoại tuyến của `emilyalsentzer/Bio_ClinicalBERT`, điểm cuối trả **HTTP 503** an toàn có cấu trúc (`cold = 68,16 ms`, `mean = 83,79 ms`, $p_{50} = 81,81\text{ ms}$, $p_{95} = 102,52\text{ ms}$) thay vì lặng lẽ trả về dự đoán giả.
2. **Thời gian thực thi đầy đủ `Bio_ClinicalBERT` + `FT-Transformer` khi nạp đủ trọng số:** `[TODO-TV1/TV2: Bổ sung số đo latency HTTP 200 của /api/v1/predict/multimodal trên CPU và GPU mục tiêu]`. Nhờ sử dụng kiến trúc *Cross-Attention Late Fusion* trên bộ mã hóa BERT kích thước vừa (~110M tham số) và giải trình không phụ thuộc LLM 7B–70B, hệ thống không yêu cầu cụm GPU lớn khi triển khai phòng khám.

---

## Câu hỏi 4: Nếu triển khai thực tế tại bệnh viện, hệ thống hiện tại còn thiếu những hạ tầng kỹ thuật nào?

**Trả lời ngắn:** Nguyên mẫu nghiên cứu hiện tại đạt chuẩn demo học thuật nhưng cần bổ sung tối thiểu **5 lớp hạ tầng bệnh viện chuẩn y tế** trước khi thí điểm lâm sàng:
1. **Chuẩn liên thông dữ liệu y tế (HL7 FHIR R4 / OpenEHR):** Ánh xạ các tài nguyên `Patient`, `Observation` (LOINC cho $\text{SpO}_2$, WBC, CRP, huyết áp), `Condition` (ICD-10) và `DocumentReference` thay cho payload JSON phẳng hiện nay.
2. **Bảo mật, Phân quyền & Khử định danh chuẩn HIPAA/Nghị định bảo vệ dữ liệu cá nhân:** Tích hợp SSO/OAuth2/OIDC (Smart-on-FHIR), phân quyền RBAC theo vai trò (*Bác sĩ điều trị / Điều dưỡng / Quản trị viên*), mã hóa đường truyền TLS nội bộ và khử định danh chuyên sâu thực thể y tế tiếng Việt trước khi ghi log.
3. **Nhật ký kiểm toán bất biến (Immutable Audit Log):** Lưu vết có chữ ký thời gian cho mọi phiên hội chẩn: mã phiên bản checkpoint (`SHA-256`), đầu vào đã chuẩn hóa, xác suất trước/sau hiệu chuẩn, các `EvidenceSpan` đã hiển thị và quyết định cuối cùng của bác sĩ (*clinician override*).
4. **Giám sát trôi dữ liệu & trôi hiệu chuẩn theo thời gian (*Data & Calibration Drift Monitoring*):** Theo dõi PSI (*Population Stability Index*) trên sinh hiệu/xét nghiệm, tỷ lệ khuyết thiếu biến theo mùa dịch và cảnh báo tự động khi ECE vượt ngưỡng $0,05$ hoặc tỷ lệ ca bất định ($< 55\%$) tăng đột biến.
5. **Quy trình thẩm định pháp lý & ngoại kiểm đa trung tâm:** Thực hiện nghiên cứu tiến cứu, *External Validation* trên dữ liệu bệnh án thực tế tại Việt Nam (và MIMIC-IV cho đối chiếu quốc tế), phân loại thiết bị y tế phần mềm (*SaMD*) và phê duyệt Hội đồng Đạo đức trước khi sử dụng hỗ trợ thật.

---

## Câu hỏi 5: Hệ thống xử lý thế nào khi thiếu trọng số mô hình hoặc dữ liệu mock để tránh đánh lừa người dùng?

**Trả lời ngắn:** Sau giai đoạn củng cố nghiên cứu (Phase 3 Backlog 08):
1. **Frontend (`frontend/src/lib/api.ts`, `DiagnosticCard.tsx`):** Không còn âm thầm rơi về dữ liệu giả lập khi backend lỗi; nhánh `predictMultimodalMock` chỉ được phép kích hoạt khi đặt tường minh biến môi trường `NEXT_PUBLIC_DEMO_MOCK=1`, và khi đó giao diện bắt buộc hiện thanh cảnh báo đỏ **`MOCK MODE`**.
2. **Backend (`inference.py`, `benchmarks.py`):** Mọi nhánh rẽ cứng theo ID bệnh nhân (`PT-0044`, `PT-0254`) trong `/predict/baseline` đã được xóa bỏ; cờ `MCDSS_STRICT_NO_MOCK_BASELINE=1` ép hệ thống trả lỗi `503` khi thiếu trọng số baseline thật, còn `/predict/multimodal` luôn báo HTTP `503` nếu thiếu `Bio_ClinicalBERT` hoặc `multimodal_best.pt`.
3. **Nguồn sự thật duy nhất (`results/registry.json` & `GET /api/v1/evaluation/registry`):** Mọi bảng biểu trên trang `/evaluation` đều đọc từ `results/registry.json`, phân tách minh bạch khối nào mang cờ `"is_mock": false` (như `rag` và `latency`) và khối nào đang chờ số liệu đa seed từ các thành viên khác (`"is_mock": true`).
