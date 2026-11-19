# BACKLOG 08 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **Cập nhật trạng thái thực hiện (Phase 3 — Chưa commit):** Đã hoàn thành phần mã nguồn, CI config và UI thuộc phạm vi Thành viên 3. Tổng thể backlog **chưa nghiệm thu 100%** vì còn chờ artifact thật từ Thành viên 1 & Thành viên 2 và chưa chạy PR trên GitHub Actions runner từ xa.

## Nhiệm vụ 3.1 – Sửa `/agent/explain` và đưa test về xanh (ngày 1–2)
- [x] Khôi phục đầy đủ API công khai của `EvidenceGrounder` (`ground_single_claim`, `ground_evidence_claims`, `import difflib`) trong `src/agent/evidence_grounder.py` mà vẫn tương thích với các hàm của TV2.
- [x] Đồng bộ schema `AgentExplainRequest` / `EvidenceSpan` / `ClaimAudit` giữa `src/api/schemas.py`, `src/api/routes/agent_chat.py`, bộ test và `frontend/src/lib/api.ts`.
- [x] Bổ sung auto-ingest fallback vào `src/agent/knowledge_ingest.py` (`get_qdrant_client` / `generate_embeddings`) để `tests/test_knowledge_ingest.py` chạy xanh ngoại tuyến.
- [x] Gỡ bỏ chú thích `"MOCK / STAND-IN FILE"` khỏi đầu tệp `src/agent/evidence_grounder.py`.
- [x] Cập nhật và bổ sung kiểm thử âm tính cho `data_source` (`dca_status`) trong `tests/test_api_endpoints.py` (vẫn giữ lưu ý sẽ rà soát lại nếu TV1/TV2 đổi schema registry cuối cùng).

## Nhiệm vụ 3.2 – Gỡ kết quả gán cứng khỏi luồng demo (ngày 2–3)
- [x] Xóa toàn bộ nhánh rẽ gán cứng `PT-0044`, `PT-0254` trong `POST /api/v1/predict/baseline` (`src/api/routes/inference.py`), bổ sung `prediction_source` và cờ `MCDSS_STRICT_NO_MOCK_BASELINE=1` trả `HTTP 503` khi yêu cầu chế độ nghiêm ngặt.
- [ ] **Thay thế hoàn toàn heuristic fallback bằng artifact model baseline thật của TV1 (Nhiệm vụ 1.3):** **Chưa hoàn thành** — *Lý do:* Thành viên 1 chưa xuất tệp mô hình baseline đã huấn luyện cho Phase 3, nên khi không bật `MCDSS_STRICT_NO_MOCK_BASELINE=1`, `/predict/baseline` vẫn dùng uniform fallback an toàn kèm nhãn `prediction_source` minh bạch.
- [x] Khóa `predictMultimodalMock` trong `frontend/src/lib/api.ts`: chỉ cho phép chạy khi đặt tường minh `NEXT_PUBLIC_DEMO_MOCK=1` và hiển thị thanh cảnh báo đỏ **`MOCK MODE`** trên `DiagnosticCard.tsx`.
- [x] Dọn bỏ chú thích mock lỗi thời trong `src/api/routes/benchmarks.py`.
- [x] Gắn rõ trường `reasoning_mode = "deterministic_template"` trong phản hồi `/api/v1/predict/status` và `/api/v1/agent/explain`.

## Nhiệm vụ 3.3 – Minh bạch phiên bản trên UI (ngày 3)
- [x] Tạo `ResearchDisclaimerBanner` và `ModelCardFooter` (`frontend/src/components/ResearchBannerAndFooter.tsx`) gắn cố định trên `/`, `/baselines`, `/evaluation`, lấy siêu dữ liệu checkpoint (`multimodal_best.pt`, SHA-256 `723facc17e37`, temperature `1.3541`, `reasoning_mode`) từ `/api/v1/predict/status`.
- [ ] **Hiển thị `data_manifest_sha` từ dữ liệu đóng băng chính thức của TV1:** **Chưa hoàn thành với dữ liệu thật** — *Lý do:* TV1 chưa tạo `data/DATA_MANIFEST.json`; hệ thống đang đọc tạm file **mock** `data/DATA_MANIFEST.json` (`_mock_notice`) do TV3 tạo để khớp giao diện và API.

## Nhiệm vụ 3.4 – CI & pin phiên bản (ngày 4–5)
- [x] Tạo `.github/workflows/ci.yml` (Python 3.12, `requirements.txt`, `flake8`, `pytest -m "not gpu and not slow"`, frontend `npm ci && npm run build && npm run lint`) và đăng ký marker `gpu`, `slow` trong `pytest.ini`.
- [x] Ghim phiên bản cố định `image: qdrant/qdrant:v1.20.0` trong `docker-compose.yml`.
- [ ] **Xác nhận workflow CI xanh trực tiếp trên GitHub Actions PR runner:** **Chưa hoàn thành** — *Lý do:* Đã kiểm tra test & build cục bộ trên máy cá nhân, chưa tạo commit/push mở Pull Request lên remote GitHub Actions ở bước Phase 3 này.

**Trạng thái nghiệm thu Backlog 08 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Cần TV1 bàn giao baseline artifact thật (Nhiệm vụ 1.3), `DATA_MANIFEST.json` thật và chạy PR trên GitHub Actions.
