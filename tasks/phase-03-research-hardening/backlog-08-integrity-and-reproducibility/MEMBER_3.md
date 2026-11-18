# BACKLOG 08 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

## Nhiệm vụ 3.1 – Sửa `/agent/explain` và đưa test về xanh (ngày 1–2)
Kết quả `pytest` 2026-11-18: **13 failed, 2 errors**. Nguyên nhân gốc:
| Lỗi | Vị trí | Cách sửa |
| :--- | :--- | :--- |
| `EvidenceGrounder` không có `ground_evidence_claims` | `src/api/routes/agent_chat.py:233` | Chốt **một** API công khai cho grounder (`ground_single_claim`, `ground_claims`) và cập nhật mọi nơi gọi |
| `EvidenceGrounder` không có `ground_single_claim` | `tests/test_agent_rag.py` (4 test) | như trên |
| `NameError: difflib` | `src/agent/evidence_grounder.py:254` | `import difflib` |
| `ValidationError AgentExplainRequest` | `tests/test_agent_explain_api.py:79` | Đồng bộ schema `src/api/schemas.py` ↔ test ↔ `frontend/src/lib/api.ts` |
| `data_source` sai chuỗi | `tests/test_api_endpoints.py:442` | Chốt giá trị sau khi M1 làm registry |
| Collection `clinical_guidelines` không tồn tại | `tests/test_knowledge_ingest.py` | Fixture tự ingest vào Qdrant in-memory trước khi query |

Gỡ header "MOCK / STAND-IN" khỏi `evidence_grounder.py` khi đã chốt bản chính thức.

## Nhiệm vụ 3.2 – Gỡ kết quả gán cứng khỏi luồng demo (ngày 2–3)
- `POST /api/v1/predict/baseline` (`src/api/routes/inference.py`) đang gán cứng `PT-0044`, `PT-0254` và dùng luật từ khoá.
  → Thay bằng suy luận thật từ các mô hình baseline do M1 lưu (Nhiệm vụ 1.3). Nếu chưa kịp: trả `503 baseline_models_unavailable` – **không** trả số giả.
- Xoá `POST /api/v1/predict/mock` khỏi luồng frontend (`frontend/src/lib/api.ts:284`) hoặc chỉ bật khi `NEXT_PUBLIC_DEMO_MOCK=1` và UI hiển thị nhãn đỏ "DỮ LIỆU GIẢ LẬP".
- Dọn chú thích lỗi thời: `src/api/routes/benchmarks.py` dòng 1–9 ghi ablation là mock (thực tế là kết quả thật).
- `diagnostic_agent.py`/`diagnostic_graph.py`: ghi rõ chế độ hiện tại là "deterministic template reasoning" trong response (`reasoning_mode`), để UI và paper không gọi nhầm là LLM.

## Nhiệm vụ 3.3 – Minh bạch phiên bản trên UI (ngày 3)
- Banner cố định: *"Nguyên mẫu nghiên cứu trên dữ liệu tổng hợp – không dùng cho quyết định lâm sàng."*
- Footer/Model card: tên checkpoint, SHA-256 rút gọn, ngày huấn luyện, temperature, data manifest SHA (lấy từ `/api/v1/predict/status`).

## Nhiệm vụ 3.4 – CI & pin phiên bản (ngày 4–5)
- `.github/workflows/ci.yml`: Python 3.12, cài `requirements.txt` (CPU), `flake8`, `pytest -m "not gpu and not slow"`; job frontend `npm ci && npm run build && npm run lint`.
- Đánh dấu test nặng (tải HF model, Qdrant thật) bằng marker `slow`/`gpu`; test nhẹ dùng backbone nhỏ có cờ `allow_random_backbone=True`.
- `docker-compose.yml:11` – thay `qdrant/qdrant:latest` bằng phiên bản cụ thể (khớp `manifest.json`, client 1.20.x).

**Nghiệm thu Thành viên 3:** CI xanh trên PR; `curl -X POST /api/v1/agent/explain` trả 200 với ca test; không endpoint nào frontend gọi trả số gán cứng.
