# Tài Liệu Q&A Bảo Vệ Hệ Thống & Kiến Trúc (Thành Viên 3 — Backlog 10 Nhiệm Vụ 3.5)

> Tài liệu chuẩn bị câu trả lời ngắn gọn, dựa trên số liệu đo đạc thực tế của hệ thống cho buổi bảo vệ đề tài **M-CDSS** (Phase 3 Research Hardening).  
> Các giá trị thực nghiệm về RAG và Latency dưới đây trích trực tiếp từ `results/rag_evaluation_report.json` và `results/latency_report.json` (`is_mock: false`).

---

## Câu hỏi 1: Vì sao nhóm chọn Qdrant thay vì chỉ tìm kiếm bằng vòng lặp Python hoặc BM25 đơn thuần?

**Trả lời ngắn:**

1. **Tách biệt dịch vụ & Phạm vi xác minh chỉ đọc trên Qdrant:** Qdrant chạy như một container độc lập (ghim phiên bản **`qdrant/qdrant:v1.20.0`** trong `docker-compose.yml`), tách trạng thái vector index (`clinical_guidelines`) khỏi tầng API FastAPI không trạng thái (`stateless`). Phép kiểm tra chỉ đọc đối với `data/guidelines/*.json` đã xác minh **chiều vector `768`, đủ 64 `chunk_id`, mã băm `SHA-256` của `text_content` và 8 trường metadata truy nguyên** (`source_id`, `version`, `target_disease`, `section_title`, `page_or_section`, `clinical_category`, `evidence_level`, `source_verified`) khớp **64/64**; tuy nhiên phép kiểm này **chưa** xác nhận chất lượng ngữ nghĩa của các vector băm ngoại tuyến.
2. **Truy vấn có lọc metadata & Hybrid RRF (không nuốt lỗi):** Qdrant hỗ trợ lọc có cấu trúc theo siêu dữ liệu nguồn (`source_id`, `disease_entity`, `evidence_level` — bảo toàn `evidence_level: null` cho tài liệu Bộ Y tế VN 2020), kết hợp với BM25 qua _Reciprocal Rank Fusion_ (RRF). Khi lỗi kết nối/chiều vector, retriever ghi log cảnh báo và hỗ trợ chế độ `strict_qdrant=True` để báo lỗi thay vì âm thầm lùi về BM25 không báo trước.
3. **Dự phòng an toàn & Kết quả thực nghiệm trên Qdrant sống kèm giới hạn encoder (`http://127.0.0.1:6333`):** Thực nghiệm trên **60 truy vấn gán nhãn kép ($\kappa = 0,9449$)** chạy với `--require-qdrant` (`dense_queries = 60/60`) đo với **vector băm 768 chiều ngoại tuyến** (do chưa có cache trọng số `all-mpnet-base-v2`, *không phải encoder ngữ nghĩa thật*): `dense_only` đạt `Recall@1 = 0,7833`, `Recall@3 = 0,9167`, `Recall@5 = 0,9833` (`MRR = 0,8688`), còn `hybrid_rrf` (Qdrant hash + BM25) đạt `Recall@1 = 0,9000`, **`Recall@3 = 0,9500`**, **`Recall@5 = 1,0000`** (`MRR = 0,9319`). Toàn bộ phần đánh giá chất lượng `all-mpnet-base-v2` thật vẫn giữ ở trạng thái chờ.

---

## Câu hỏi 2: Cơ chế Grounding ký tự (`EvidenceGrounder`) hoạt động đến mức nào và có loại bỏ được hết ảo giác không?

**Trả lời ngắn:**

1. **Không loại bỏ hoàn toàn ảo giác; chỉ kiểm chứng vị trí chuỗi:** Mọi nhận định sau bước lập luận đi qua `EvidenceGrounder` (`src/agent/evidence_grounder.py`) với độ phức tạp tuyến tính $\mathcal{O}(N)$. Một đoạn chỉ được cấp cặp chỉ số `[start_char, end_char]` khi khớp trực tiếp (hoặc khớp chuẩn hóa khoảng trắng/ký tự có kiểm soát qua `difflib`) với văn bản đầu vào $T$.
2. **Kết quả kiểm tra sơ bộ trên 50 bệnh án (`50/50` lấy từ `data/processed/test.parquet`, tổng $N=287$, trạng thái `preliminary_non_strict_holdout` — chưa phải tập hold-out chuẩn `strict N=302`, không dùng bản ghi mẫu tổng hợp):**
    - **Bất biến cắt chuỗi từ `explain_clinical_case()`:** **200 / 200 (`1,00`)** đoạn ứng viên thỏa mãn `display_note[start_char:end_char] == span.text`.
    - **Từ chối chuỗi ngoài văn bản (`out_of_note_probe_rejection_rate`):** **50 / 50 (`1,00`)** đầu dò chuỗi không nằm trong ghi chú bị bộ lọc từ chối (tên trường báo cáo phản ánh đúng phép kiểm chuỗi ngoài ghi chú, không gọi là đo lường hallucination ngữ nghĩa).
    - **Đánh giá ngữ nghĩa thủ công 20 mẫu span:** Đã xuất 20 câu lâm sàng thực tế sang `results/grounding_manual_audit_20_samples.json` với `"human_verified": null` (`manual_semantic_precision_20_spans = null` — **`[TODO-HUMAN-REVIEW]`**).
3. **Giới hạn trung thực bắt buộc phải nêu rõ:** Các chỉ số tự động trên chỉ là **kiểm tra sơ bộ** về **khớp chuỗi và lọc chuỗi nằm ngoài bệnh án** trên split `N=287`; chúng **không** đại diện cho hold-out `strict N=302`, **không** chứng minh được độ đúng ngữ nghĩa, không phát hiện lỗi đảo ngược phủ định (_"không khó thở"_ bị trích thành _"khó thở"_) và **không phải xác nhận lâm sàng**. Hệ thống mặc định vận hành ở `reasoning_mode = "deterministic_template"` (đã xóa các nhánh hardcode `PT-0044`/`PT-0254`) và luôn yêu cầu bác sĩ kiểm chứng lại nội dung.

---

## Câu hỏi 3: Độ trễ thực tế của hệ thống là bao nhiêu và có chạy thuần CPU (không GPU) được không?

**Trả lời ngắn:**

1. **Đo thực tế qua HTTP/TCP Docker (`measurement_mode = "http_docker_end_to_end"`, `--base-url http://127.0.0.1:8000`):** Ghi nhận trọn vẹn chi phí HTTP Uvicorn và mạng Docker ↔ Qdrant (200 lượt gọi ấm sau 1 cold request, bệnh án 340 ký tự, CPU _Windows 11 AMD64, 16 logical cores_):
    - `POST /api/v1/agent/explain` (**HTTP 200**): Cold = `169,03 ms` | Warm Mean = `63,49 ms` | **$p_{50} = 62,92\text{ ms}$** | **$p_{95} = 84,23\text{ ms}$** | $p_{99} = 92,25\text{ ms}$.
    - `POST /api/v1/predict/baseline` (**HTTP 503** safeguard mặc định `baseline_models_unavailable`): Cold = `32,76 ms` | Warm Mean = `47,57 ms` | $p_{50} = 47,77\text{ ms}$ | $p_{95} = 51,24\text{ ms}$ | $p_{99} = 52,40\text{ ms}$.
    - `POST /api/v1/predict/multimodal` (**HTTP 503** safeguard trong image Docker triển khai nhẹ do không đóng gói `torch` và thiếu cache `Bio_ClinicalBERT`): Cold = `54,87 ms` | Warm Mean = `48,30 ms` | $p_{50} = 48,16\text{ ms}$ | $p_{95} = 50,55\text{ ms}$ | $p_{99} = 52,45\text{ ms}$. _(Phép đo này mới xác nhận cơ chế fail-safe 503, chưa đo suy luận PyTorch thực)._
2. **Thời gian thực thi đầy đủ `Bio_ClinicalBERT` + `FT-Transformer` khi nạp đủ trọng số:** `[TODO-TV1/TV2: Bổ sung số đo latency HTTP 200 của /api/v1/predict/multimodal và /baseline trên môi trường có torch + cache Bio_ClinicalBERT và GPU/CPU mục tiêu]`.

---

## Câu hỏi 4: Nếu triển khai thực tế tại bệnh viện, hệ thống hiện tại còn thiếu những hạ tầng kỹ thuật nào?

**Trả lời ngắn:** Nguyên mẫu nghiên cứu hiện tại mới dừng ở mức demo học thuật, còn thiếu tối thiểu **5 lớp hạ tầng bệnh viện chuẩn y tế** trước khi thí điểm lâm sàng:

1. **Chuẩn liên thông dữ liệu y tế (HL7 FHIR R4 / OpenEHR):** Ánh xạ các tài nguyên `Patient`, `Observation` (LOINC cho $\text{SpO}_2$, WBC, CRP, huyết áp), `Condition` (ICD-10) và `DocumentReference` thay cho payload JSON phẳng hiện nay.
2. **Bảo mật, Phân quyền & Khử định danh chuẩn HIPAA/Nghị định bảo vệ dữ liệu cá nhân:** Tích hợp SSO/OAuth2/OIDC (Smart-on-FHIR), phân quyền RBAC theo vai trò (_Bác sĩ điều trị / Điều dưỡng / Quản trị viên_), mã hóa đường truyền TLS nội bộ và khử định danh chuyên sâu thực thể y tế tiếng Việt trước khi ghi log.
3. **Nhật ký kiểm toán bất biến (Immutable Audit Log):** Lưu vết có chữ ký thời gian cho mọi phiên hội chẩn: mã phiên bản checkpoint (`SHA-256`), đầu vào đã chuẩn hóa, xác suất trước/sau hiệu chuẩn, các `EvidenceSpan` đã hiển thị và quyết định cuối cùng của bác sĩ (_clinician override_).
4. **Giám sát trôi dữ liệu & trôi hiệu chuẩn theo thời gian (_Data & Calibration Drift Monitoring_):** Theo dõi PSI (_Population Stability Index_) trên sinh hiệu/xét nghiệm, tỷ lệ khuyết thiếu biến theo mùa dịch và cảnh báo tự động khi ECE vượt ngưỡng $0,05$ hoặc tỷ lệ ca bất định ($< 55\%$) tăng đột biến.
5. **Quy trình thẩm định pháp lý & ngoại kiểm đa trung tâm:** Thực hiện nghiên cứu tiến cứu, _External Validation_ trên dữ liệu bệnh án thực tế tại Việt Nam (và MIMIC-IV cho đối chiếu quốc tế), phân loại thiết bị y tế phần mềm (_SaMD_) và phê duyệt Hội đồng Đạo đức trước khi sử dụng hỗ trợ thật.

---

## Câu hỏi 5: Hệ thống xử lý thế nào khi thiếu trọng số mô hình hoặc dữ liệu mock để tránh đánh lừa người dùng?

**Trả lời ngắn:** Sau giai đoạn củng cố nghiên cứu và rà soát đối chiếu thực tế:

1. **Frontend (`frontend/src/lib/api.ts`, `DiagnosticCard.tsx`, `ResearchBannerAndFooter.tsx`):** Không âm thầm rơi về dữ liệu giả lập khi backend lỗi (`predictMultimodalMock` chỉ bật khi đặt `NEXT_PUBLIC_DEMO_MOCK=1` kèm cảnh báo đỏ **`MOCK MODE`**). Khi `DATA_MANIFEST.json` còn là file mock, `ModelCardFooter` hiển thị rõ huy hiệu **`MOCK — chờ TV2`** bên cạnh `Manifest SHA`. Biểu đồ DCA gắn nhãn trung thực là **Macro One-vs-Rest trung bình 4 lớp**.
2. **Backend (`inference.py`, `agent_chat.py`, `benchmarks.py`):** Mọi nhánh gán cứng `PT-0044`/`PT-0254` trong `/predict/baseline` và `/agent/explain` đã được xóa bỏ. Cả `/predict/baseline` (trừ khi bật tường minh `MCDSS_ALLOW_HEURISTIC_BASELINE=1`) và `/predict/multimodal` đều mặc định trả `HTTP 503` có cấu trúc khi thiếu trọng số/dependency thật; đồng thời `smoke_test.ps1` bản mặc định yêu cầu `HTTP 200` (tách riêng kiểm tra fail-safe qua `-AllowLightweightNoTorch`).
3. **Nguồn sự thật duy nhất (`results/registry.json` & `GET /api/v1/evaluation/registry`):** Phân tách minh bạch khối `"is_mock": false` (`rag`, `latency`) và khối `"is_mock": true` (RQ1, RQ2, RQ4 chờ TV1/TV2), ghi rõ giới hạn kiểm định chuỗi và để `"pending_human_review"` cho phần chấm ngữ nghĩa thủ công.
