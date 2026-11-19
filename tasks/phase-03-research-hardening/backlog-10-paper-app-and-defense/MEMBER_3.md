# BACKLOG 10 – THÀNH VIÊN 3 (Full-Stack AI & System Integrator)

> **Cập nhật trạng thái thực hiện (Phase 3 — Chưa commit):** Đã hoàn thành script `smoke_test`, cập nhật bộ section LaTeX (`04`, `05`, `06`), kịch bản video/slide và bộ tài liệu Q&A. Backlog **chưa hoàn thành 100%** do chưa có máy thứ hai kiểm chứng clean Docker run, chưa xuất ảnh UI/video/slide bản cuối vì còn chờ số liệu đa seed RQ1–RQ4 của TV1 & TV2.

## Nhiệm vụ 3.1 – Docker clean-run & smoke test
- [x] Tạo `scripts/smoke_test.ps1` (Windows) và `scripts/smoke_test.sh` (Linux/macOS) kiểm tra 8 điểm cuối (`/health`, `/api/v1/predict/status`, `/api/v1/predict/multimodal` [chấp nhận HTTP 200 hoặc HTTP 503 có cấu trúc khi thiếu HF cache], `/api/v1/agent/explain` kiểm tra non-empty `verified_spans`, `/api/v1/evaluation/benchmark`, `/api/v1/evaluation/registry`, Frontend `/` và `/evaluation` trả 200).
- [ ] **Chạy kiểm chứng trên máy thứ hai (hoặc VM sạch) từ đầu với `docker compose up --build -d` (3 dịch vụ healthy):** **Chưa hoàn thành** — *Lý do:* Workspace hiện tại không kết nối tới máy vật lý thứ hai hay VM sạch độc lập để chạy thử nghiệm cài mới hoàn toàn từ đầu.
- [ ] **Cập nhật root `README.md` mục "Quick start 5 phút" & liên kết tải checkpoint + data + Qdrant snapshot kèm SHA-256:** **Chưa hoàn thành** — *Lý do:* Đang giữ nguyên `README.md` gốc cho đến khi TV1 & TV2 chốt bản đóng băng cuối cùng của `multimodal_best.pt`, `DATA_MANIFEST.json` và `results/registry.json` để ghi đúng SHA-256 phát hành.

## Nhiệm vụ 3.2 – Section System & hình vẽ
- [x] Cập nhật `docs/paper_latex/sections/04_software_architecture.tex`, `05_multi_agent_rag.tex`, `06_frontend_dca_ux.tex`: xóa toàn bộ `[TODO-TV3]`, mô tả chính xác chế độ `deterministic_template`, bổ sung bảng Latency thực tế (`p50/p95/p99`) và bảng RAG (`Recall@1/3/5`, `MRR`, `nDCG@5`, grounding 50 ca), giữ lại các `[TODO-TV1]` / `[TODO-TV2]` ở những chỗ chờ số liệu đa seed từ TV1/TV2.
- [ ] **Xuất lại toàn bộ sơ đồ SVG/PDF đồng bộ & ảnh chụp màn hình UI thật (không dính badge mock):** **Chưa hoàn thành** — *Lý do:* Trang `/evaluation` và dự đoán đa seed vẫn đang hiển thị khối dữ liệu mock từ `results/registry.json` (`is_mock: true`) do TV1/TV2 chưa bàn giao kết quả cuối, nên chưa thể chụp ảnh UI không mock để đưa vào bài báo.

## Nhiệm vụ 3.3 – Video demo 3–5 phút
- [x] Cập nhật kịch bản chi tiết 5 phân cảnh (`0:00–4:30`) tại `docs/thuyết trình/KICH_BAN_VIDEO_DEMO_LAM_SANG_GIAI_DOAN_2.md` gồm cảnh báo dữ liệu tổng hợp ở mở đầu, RQ4 Missing-Modality Toggle, cảnh báo bất định `< 55%`, số liệu RAG 60 truy vấn & độ trễ CPU thật; giữ nguyên các placeholder `[TODO-TV1/TV2]` cho kết quả mô hình đa seed.
- [ ] **Quay và xuất bản video MP4 Full HD hoàn chỉnh:** **Chưa hoàn thành** — *Lý do:* Chỉ mới hoàn tất kịch bản; cần có số liệu và checkpoint/HF cache chạy thật từ TV1 & TV2 để quay demo trực tiếp không còn `[TODO-TV1/TV2]` hay cờ `HTTP 503`/`MOCK`.

## Nhiệm vụ 3.4 – Slide thuyết trình (15–20 trang) & demo trực tiếp
- [x] Cập nhật kịch bản nội dung 20 slide tại `docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md` theo mạch RQ1–RQ5, cập nhật số liệu RAG/Grounding/Latency thật của TV3, giới hạn trung thực, hướng phát triển (MIMIC-IV, khảo sát bác sĩ, LLM có ràng buộc) và phương án dự phòng; giữ `[TODO-TV1/TV2]` ở bảng kết quả RQ1–RQ4.
- [ ] **Xuất tệp trình chiếu (PowerPoint/PDF), ghép ảnh UI/video dự phòng và diễn tập bấm giờ 3 thành viên:** **Chưa hoàn thành** — *Lý do:* Chờ TV1 & TV2 hoàn thành kết quả RQ1–RQ4 để lấp đầy các khung `[TODO-TV1/TV2]` trước khi xuất bản slide cuối cùng.

## Nhiệm vụ 3.5 – Q&A phần hệ thống
- [x] Xây dựng tài liệu hỏi–đáp kỹ thuật hệ thống với dẫn chứng số liệu đo đạc thực tế tại `docs/thuyết trình/QA_HE_THONG_VA_KIEN_TRUC_MEMBER_3.md` (Qdrant `v1.20.0`, Grounding 50 ca, CPU Latency `p50=9,15 ms / p95=11,46 ms`, 5 lớp hạ tầng triển khai thực tế, và xử lý thiếu weight/mock).

**Trạng thái nghiệm thu Backlog 10 (TV3):** `[ ] Chưa hoàn thành toàn phần` — Các tài liệu kịch bản, LaTeX hệ thống, Q&A và script `smoke_test` thuộc phần viết/cấu hình đã xong; các sản phẩm cần kết quả thật từ TV1/TV2 (video quay thật, ảnh UI không mock, slide xuất bản, README SHA-256, máy thứ hai chạy Docker) vẫn giữ trạng thái chờ nghiệm thu.
