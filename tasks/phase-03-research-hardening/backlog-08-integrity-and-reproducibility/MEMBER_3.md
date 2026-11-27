# BACKLOG 08 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **RÀ SOÁT CỦA THÀNH VIÊN 1 (2026-11-23):** ✅ Chấp nhận. `/agent/explain` hoạt động, mock gán cứng đã gỡ, CI + pin Qdrant có. Bổ sung của TV1: `/predict/baseline` nay phục vụ mô hình baseline thật (`src/api/baseline_service.py`); `/evaluation/benchmark` không còn số liệu gán cứng trong mã nguồn; model card đọc metadata từ checkpoint.


> **Cập nhật trạng thái thực hiện (Phase 3 — Bản sửa sau rà soát):** Đã khắc phục các sai lệch thuộc phạm vi Thành viên 3 (xóa hardcode `PT-0044`/`PT-0254` trong `agent_chat.py`, đổi mặc định `/predict/baseline` sang `HTTP 503`, gắn nhãn `MOCK — chờ TV2` cho `DATA_MANIFEST.json`, nâng `docker-compose.yml` về `qdrant/qdrant:v1.20.0`, lazy-import `torch` trong `inference.py`). Tổng thể backlog **chưa nghiệm thu 100%** vì còn phụ thuộc model thật & manifest thật từ TV1/TV2 và chạy CI trên GitHub PR runner.

## Nhiệm vụ 3.1 – Sửa `/agent/explain` và đưa test về xanh (ngày 1–2)
- [x] Khôi phục đầy đủ API công khai của `EvidenceGrounder` (`ground_single_claim`, `ground_evidence_claims`, `import difflib`) trong `src/agent/evidence_grounder.py` mà vẫn tương thích với các hàm của TV2.
- [x] Đồng bộ schema `AgentExplainRequest` / `EvidenceSpan` / `ClaimAudit` giữa `src/api/schemas.py`, `src/api/routes/agent_chat.py`, bộ test và `frontend/src/lib/api.ts`.
- [x] Cập nhật `src/agent/knowledge_ingest.py` hỗ trợ `QDRANT_URL` / `--qdrant-url`, bổ sung metadata chuẩn và kiểm tra đồng bộ `64` chunk / `768` chiều khi khởi tạo; cập nhật `src/agent/retriever.py` ghi cảnh báo và hỗ trợ `strict_qdrant=True` không nuốt lỗi khi Qdrant lỗi.
- [x] Gỡ bỏ chú thích `"MOCK / STAND-IN FILE"` khỏi đầu tệp `src/agent/evidence_grounder.py`.
- [x] Cập nhật và bổ sung kiểm thử âm tính cho `data_source` (`dca_status`) trong `tests/test_api_endpoints.py` (vẫn giữ lưu ý rà soát lại nếu TV1/TV2 đổi schema registry cuối cùng).

## Nhiệm vụ 3.2 – Gỡ kết quả gán cứng khỏi luồng demo (ngày 2–3)
- [x] Xóa toàn bộ nhánh rẽ gán cứng `PT-0044`, `PT-0254` trong **cả** `POST /api/v1/predict/baseline` (`src/api/routes/inference.py`) lẫn `POST /api/v1/agent/explain` (`src/api/routes/agent_chat.py`, thay bằng bộ trích câu lâm sàng động có lọc tiêu đề hành chính Anh/Việt).
- [x] Đổi hành vi mặc định của `POST /api/v1/predict/baseline` sang **`HTTP 503 baseline_models_unavailable`** (chỉ cho phép fallback heuristic khi đặt tường minh `MCDSS_ALLOW_HEURISTIC_BASELINE=1`).
- [ ] **Thay thế hoàn toàn heuristic fallback bằng artifact model baseline thật của TV1 (Nhiệm vụ 1.3):** **Chưa hoàn thành** — *Lý do:* Thành viên 1 chưa xuất tệp mô hình baseline đã huấn luyện cho Phase 3; hiện endpoint mặc định trả `HTTP 503` an toàn.
- [x] Khóa `predictMultimodalMock` trong `frontend/src/lib/api.ts`: chỉ cho phép chạy khi đặt tường minh `NEXT_PUBLIC_DEMO_MOCK=1` và hiển thị thanh cảnh báo đỏ **`MOCK MODE`** trên `DiagnosticCard.tsx`.
- [x] Dọn bỏ chú thích mock lỗi thời trong `src/api/routes/benchmarks.py`.
- [x] Gắn rõ trường `reasoning_mode = "deterministic_template"` trong phản hồi `/api/v1/predict/status` và `/api/v1/agent/explain`.

## Nhiệm vụ 3.3 – Minh bạch phiên bản trên UI (ngày 3)
- [x] Tạo `ResearchDisclaimerBanner` và `ModelCardFooter` (`frontend/src/components/ResearchBannerAndFooter.tsx`) gắn cố định trên `/`, `/baselines`, `/evaluation`, lấy siêu dữ liệu checkpoint (`multimodal_best.pt`, SHA-256 `723facc17e37`, temperature `1.3541`, `reasoning_mode`) và cờ `data_manifest_is_mock` từ `/api/v1/predict/status`, hiển thị rõ nhãn **`MOCK — chờ TV2`** bên cạnh `Manifest SHA` khi dùng file giả lập.
- [ ] **Hiển thị `data_manifest_sha` từ dữ liệu đóng băng chính thức của TV2/TV1:** **Chưa hoàn thành với dữ liệu thật** — *Lý do:* TV2/TV1 chưa bàn giao `data/DATA_MANIFEST.json` chính thức; hệ thống đang dùng file mock (`manifest_sha256: "e3b0c44298fc..."`) có gắn badge `[MOCK — chờ TV2]`.

## Nhiệm vụ 3.4 – CI & pin phiên bản (ngày 4–5)
- [x] Tạo `.github/workflows/ci.yml` (Python 3.12, `requirements.txt`, `flake8`, `pytest -m "not gpu and not slow"`, frontend `npm ci && npm run build && npm run lint`) và đăng ký marker `gpu`, `slow` trong `pytest.ini`.
- [x] Ghim phiên bản cố định `image: qdrant/qdrant:v1.20.0` (khớp `manifest.json` và volume `mcdss-qdrant-storage`), mount `./results:/app/results:ro` trong `docker-compose.yml`, thêm `matplotlib>=3.8.0` vào `requirements-deploy.txt`, và lazy-import `predict_checkpoint` trong `inference.py` để stack Docker chạy `healthy`.
- [ ] **Xác nhận workflow CI xanh trực tiếp trên GitHub Actions PR runner:** **Chưa hoàn thành** — *Lý do:* Đã kiểm tra test & build cục bộ và trên Docker local, chưa push PR lên remote GitHub Actions ở bước Phase 3 này.

**Trạng thái nghiệm thu Backlog 08 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Cần TV1/TV2 bàn giao baseline artifact thật, `DATA_MANIFEST.json` thật, cache `Bio_ClinicalBERT` trong container và chạy PR trên GitHub Actions.
