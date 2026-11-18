# BACKLOG 10: BẢN THẢO NGHIÊN CỨU, ỨNG DỤNG HOÀN CHỈNH & BẢO VỆ
### Giai đoạn 3 – Tuần 3 | Mục tiêu: một bài báo nhất quán, một demo chạy thật, một buổi thuyết trình thuyết phục

---

## 1. NGUYÊN TẮC
- **Đóng băng kết quả:** chỉ dùng registry tại tag `results-freeze`. Không chạy thí nghiệm mới tuần này (trừ sửa lỗi).
- Mọi bảng số trong LaTeX được `\input{generated/...}` từ registry; mọi số trên slide được chép từ bảng sinh tự động.
- Kết luận chỉ trong phạm vi dữ liệu tổng hợp & đánh giá nội bộ.

## 2. CẤU TRÚC BÀI BÁO ĐỀ XUẤT (TRIPOD+AI)
| Mục | Nội dung chính | Phụ trách |
| :--- | :--- | :---: |
| Abstract | Viết lại theo RQ1–RQ5; nêu cả phát hiện dư thừa phương thức | M1 |
| 1. Introduction | Khoảng trống (JMIR 2024), câu hỏi nghiên cứu, 4 đóng góp | M1 |
| 2. Data & Cohort | Nguồn Synthea + MTSamples, cách ghép, de-ID, temporal lock, strict split, **flow diagram**, bảng đặc điểm đoàn hệ | M2 |
| 3. Methods | FT-Transformer, text encoder, cross-attention, calibration, kế hoạch phân tích, thống kê | M1 |
| 4. System | Kiến trúc 3 tầng, RAG + grounding, API, UI | M3 |
| 5. Results | RQ1 → RQ5 theo đúng thứ tự, mỗi RQ một bảng/hình | M1 + M2 + M3 |
| 6. Discussion | Diễn giải, so sánh y văn, **giới hạn** (dữ liệu tổng hợp, template, N nhỏ, chưa ngoại kiểm, chưa khảo sát bác sĩ nếu chưa làm) | Cả nhóm |
| 7. Ethics & Reproducibility | PHI, giấy phép, mã nguồn, artefact | M2 |
| Phụ lục | TRIPOD+AI checklist (số trang), PROBAST+AI, siêu tham số, model card | M2 + M1 |

## 3. PHÂN CÔNG
* 🧬 **Thành viên 1:** Abstract/Intro/Methods/Results, hình kết quả, release notes. 👉 [MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2:** Data/Cohort, Ethics, TRIPOD+AI & PROBAST+AI, tài liệu tham khảo. 👉 [MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3:** System section, Docker clean-run, video demo, slide, kịch bản demo trực tiếp. 👉 [MEMBER_3.md](MEMBER_3.md)

## 4. LỊCH TUẦN 3
| Ngày | Mốc |
| :---: | :--- |
| 1–2 | Bản nháp đầy đủ mọi section (0 `[TODO]`), slide v1 |
| 3 | Đọc chéo nội bộ (mỗi người review 2 section không phải của mình); video quay thô |
| 4 | **Tổng duyệt lần 1** (bấm giờ, có người đóng vai hội đồng), sửa |
| 5 | Docker clean-run trên máy thứ 2; video final; **tổng duyệt lần 2**; tag `v1.0-research` (sau khi nhóm đồng ý) |

## 5. DEFINITION OF DONE (NGHIỆM THU CUỐI)
- [ ] `grep -r "TODO" docs/paper_latex` = 0; PDF biên dịch không lỗi; ≥ 35 tài liệu tham khảo đã kiểm tra tồn tại.
- [ ] TRIPOD+AI checklist điền đủ số trang; PROBAST+AI có lý do từng miền.
- [ ] `docker compose up --build -d` trên máy sạch → 3 dịch vụ healthy; `scripts/smoke_test` pass.
- [ ] `pytest tests/` 100% pass; CI xanh.
- [ ] Video 3–5 phút có thuyết minh; slide 15–20 trang; 2 buổi tổng duyệt đã thực hiện.
- [ ] Mọi số trên slide/video khớp registry (một người kiểm tra chéo từng số).
