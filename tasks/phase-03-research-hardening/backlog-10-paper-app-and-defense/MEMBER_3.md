# BACKLOG 10 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **Cập nhật trạng thái thực hiện (Phase 3 — Bản chuẩn hóa sau rà soát):** Đã siết script `smoke_test`, đổi tên trường kiểm probe sang `out_of_note_probe_rejection_rate`, sửa `eval_rag.py` sang chế độ chỉ đọc trên Qdrant từ xa (xác minh chiều 768, `chunk_id`, `SHA-256` và 8 metadata; *chưa xác nhận ngữ nghĩa vector*), đánh dấu audit 50 ca trên `data/processed/test.parquet` ($N=287$) là **sơ bộ** (`preliminary_non_strict_holdout`, chưa phải `strict 302`), và đồng bộ lại LaTeX (`04`, `05`, `06`), slide/video, Q&A, UI để không khẳng định quá mức. Backlog **chưa hoàn thành 100%** do chưa có `HTTP 200` trên `/predict/multimodal` trong Docker nhẹ, chưa có encoder `all-mpnet-base-v2`, chưa chấm tay 20 mẫu grounding, chưa kiểm thử trên máy thứ hai và còn chờ số liệu RQ1–RQ4 của TV1 & TV2.

## Nhiệm vụ 3.1 – Docker clean-run & smoke test
- [x] Cập nhật `scripts/smoke_test.ps1` và `scripts/smoke_test.sh`: chế độ mặc định (strict) yêu cầu `/predict/multimodal` trả `HTTP 200` và báo `[FAIL]` nếu gặp `503` (nêu rõ thiếu `torch` hay cache HF); chế độ `-AllowLightweightNoTorch` / `--allow-lightweight-no-torch` tách riêng kết quả `503` thành `[FAIL-SAFE ONLY]` thay vì `[PASS]`.
- [x] Đã chạy `docker compose up --build -d --wait` trên máy phát triển với `qdrant/qdrant:v1.20.0`, `api` và `frontend` đều đạt `healthy` (frontend tạm chạy trên cổng `3001` do cổng `3000` đang bị container `clinic_frontend` của dự án khác chiếm dụng), và xác nhận `7 PASS + 1 FAIL-SAFE ONLY` ở chế độ lightweight.
- [ ] **Chạy kiểm chứng strict `smoke_test` (bao gồm `/predict/multimodal` trả `HTTP 200`) và chạy trên máy thứ hai (hoặc VM sạch):** **Chưa hoàn thành** — *Lý do:* Image `requirements-deploy.txt` không cài `torch` và chưa có cache `Bio_ClinicalBERT`, nên strict `smoke_test.ps1` báo `[FAIL]` (exit code 1) ở bước 3; đồng thời chưa có máy vật lý thứ hai hay VM sạch để thử cài mới hoàn toàn.
- [ ] **Cập nhật root `README.md` mục "Quick start 5 phút" & liên kết tải checkpoint + data + Qdrant snapshot kèm SHA-256:** **Chưa hoàn thành** — *Lý do:* Chờ TV1 & TV2 chốt bản đóng băng cuối của `multimodal_best.pt`, `DATA_MANIFEST.json` và `results/registry.json`.

## Nhiệm vụ 3.2 – Section System & hình vẽ
- [x] Cập nhật `docs/paper_latex/sections/04_software_architecture.tex`, `05_multi_agent_rag.tex`, `06_frontend_dca_ux.tex` với số liệu trung thực và không khẳng định quá mức: `64` chunk xác minh đọc-chỉ chiều 768/ID/SHA-256/8 metadata trong Qdrant Docker (`v1.20.0`, *vector băm 768-D — chưa xác nhận chất lượng ngữ nghĩa vector*), bảng RAG qua `--require-qdrant` ($\kappa = 0,9449$), bảng HTTP Docker end-to-end latency thật (`p50=62,92 ms`, `p95=84,23 ms`), đánh dấu audit 50 ca trên `data/processed/test.parquet` ($N=287$) là **sơ bộ** (chưa phải `strict 302`) dùng `out_of_note_probe_rejection_rate`, giữ `[TODO-HUMAN-REVIEW]` cho 20 mẫu ngữ nghĩa và `[TODO-TV1/TV2]` cho số liệu RQ1–RQ4.
- [ ] **Xuất lại sơ đồ SVG/PDF đồng bộ & ảnh chụp màn hình UI thật (không dính badge mock):** **Chưa hoàn thành** — *Lý do:* Đang chờ TV1/TV2 bàn giao số liệu đa seed thật cho `results/registry.json` và manifest thật để UI không còn nhãn `[MOCK]`.

## Nhiệm vụ 3.3 – Video demo 3–5 phút
- [x] Cập nhật kịch bản chi tiết 5 phân cảnh (`0:00–4:30`) tại `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md` theo đúng phạm vi kiểm tra sơ bộ khớp ký tự trên `data/processed/test.parquet` ($N=287$, chưa phải `strict 302`), giới hạn Qdrant đọc-chỉ + vector băm ngoại tuyến, `pending_human_review` 20 mẫu, và giữ khung `[TODO-TV1/TV2]`.
- [ ] **Quay và xuất bản video MP4 Full HD hoàn chỉnh:** **Chưa hoàn thành** — *Lý do:* Cần TV1 & TV2 hoàn tất checkpoint + cache + số liệu RQ1–RQ4 và khắc phục suy luận multimodal `HTTP 200` mới quay demo sống hoàn chỉnh.

## Nhiệm vụ 3.4 – Slide thuyết trình (15–20 trang) & demo trực tiếp
- [x] Cập nhật kịch bản nội dung 20 slide tại `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md` theo mạch RQ1–RQ5, bỏ các cụm từ khẳng định tuyệt đối (`tuyệt đối không ảo giác`, `loại bỏ hoàn toàn`), phản ánh trung thực kết quả Qdrant đọc-chỉ `64` điểm (giới hạn ở ID/SHA-256/8 metadata & vector băm 768-D ngoại tuyến), đánh dấu audit 50 ca là **sơ bộ** + `out_of_note_probe_rejection_rate` + `[TODO-HUMAN-REVIEW]` 20 mẫu, HTTP Docker latency và giữ `[TODO-TV1/TV2]`.
- [ ] **Xuất tệp trình chiếu (PowerPoint/PDF), ghép ảnh UI/video dự phòng và diễn tập bấm giờ 3 thành viên:** **Chưa hoàn thành** — *Lý do:* Chờ TV1 & TV2 hoàn thành kết quả RQ1–RQ4 điền hết `[TODO-TV1/TV2]` và hoàn tất chấm thủ công 20 mẫu grounding.

## Nhiệm vụ 3.5 – Q&A phần hệ thống
- [x] Cập nhật tài liệu hỏi–đáp kỹ thuật hệ thống với dẫn chứng số liệu và giới hạn trung thực tại `docs/thuyết trình/QA_HE_THONG_VA_KIEN_TRUC_MEMBER_3.md`.

**Trạng thái nghiệm thu Backlog 10 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Tài liệu, script kiểm thử chặt chẽ và số đo HTTP Docker/Qdrant của TV3 đã chuẩn hóa; còn chờ strict multimodal `HTTP 200`, chấm tay 20 mẫu grounding, máy thứ hai chạy Docker sạch và số liệu thật từ TV1/TV2 để chốt slide/video/ảnh UI.
