# RELEASE NOTES – M-CDSS `v1.0-research` (bản nháp, chờ nhóm duyệt)

> **Chưa gắn tag.** Theo Backlog 10, tag/release công khai chỉ thực hiện sau khi cả nhóm đồng ý phạm vi phát hành.
> Nguyên mẫu nghiên cứu trên dữ liệu bán tổng hợp – **không dùng cho quyết định lâm sàng**.

## Nội dung phát hành
| Thành phần | Vị trí | Ghi chú |
| :--- | :--- | :--- |
| Mã nguồn (pipeline, mô hình, API, UI) | `src/`, `scripts/`, `frontend/` | MIT (xem `LICENSE`, `NOTICE`) |
| Dữ liệu canonical (strict split) | tái tạo bằng `python scripts/rebuild_canonical_dataset.py` từ `data/raw_rebuilt/` | Kiểm bằng `data/DATA_MANIFEST.json` (`content_sha256`) |
| Checkpoint triển khai | `data/checkpoints/multimodal_best.pt` | Cross-attention, BERT đóng băng; seed, temperature, provenance trong file |
| Baseline phục vụ API | `data/checkpoints/baselines/` (+ `manifest.json` SHA-256) | CatBoost, FT-Transformer, BERT fine-tune khối cuối (seed 42); ~31 MB – **không commit vào git**, phân phối qua release asset |
| Kết quả nghiên cứu | `results/registry.json` | Nguồn số liệu duy nhất cho bài báo, slide, UI, `MODEL_CARD.md` |
| Kế hoạch phân tích đăng ký trước | `docs/11_ANALYSIS_PLAN.md`, `results/preregistration/` | Hash đóng băng trước lần chạy đầu |
| Snapshot Qdrant | `data/vector_store/` (manifest SHA-256) | 64 chunk phác đồ diễn giải ngắn có trích dẫn |

## Thay đổi chính so với Phase 2
- Bộ dữ liệu canonical dựng lại đúng pipeline Phase 1 + khử định danh Phase 3; audit rò rỉ ở mức nội dung ghi chú.
- Không còn fallback BERT ngẫu nhiên; checkpoint không thể bị ghi đè bởi lần chạy không huấn luyện.
- So sánh 10 mô hình × 5 seed, CI bootstrap, Holm; phân rã tín hiệu văn bản; mô phỏng bổ trợ; DCA; độ bền thiếu dữ liệu; temporal split; grouped CV (post-hoc).
- `/predict/baseline` và `/predict/multimodal` phục vụ mô hình thật; `/evaluation/benchmark` không còn số liệu gán cứng.
- Kết quả Backlog 09 dựa trên bộ dữ liệu rò rỉ được thu hồi (`data/legacy_invalid_2026-11-19/`).

## Điều kiện phân phối
- **Bio_ClinicalBERT** (MIT) – không đóng gói lại trọng số; người dùng tải từ Hugging Face.
- **Synthea** (Apache-2.0); **MTSamples** – chỉ dùng cho nghiên cứu theo điều khoản của mtsamples.com; cân nhắc **không** phát hành công khai ghi chú đã xử lý (phát hành script tái tạo thay thế).
- **Phác đồ GINA/GOLD/ESC** có bản quyền – chỉ diễn giải ngắn kèm trích dẫn; không phân phối toàn văn.
- Checkpoint huấn luyện trên dữ liệu bán tổng hợp: có thể phát hành kèm `MODEL_CARD.md`.

## Việc còn mở trước khi gắn tag
- [ ] Nhóm duyệt phạm vi phát hành (dữ liệu xử lý có công khai hay không).
- [ ] Docker clean-run trên máy thứ hai với `MCDSS_INSTALL_ML=1` (strict smoke test `/predict/multimodal` = 200).
- [ ] Chấm thủ công 20 đoạn grounding (`results/grounding_manual_audit_20_samples.json`).
- [ ] Biên dịch PDF bài báo trên máy có TeX (Overleaf) và kiểm tra lỗi.
