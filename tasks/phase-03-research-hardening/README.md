# GIAI ĐOẠN 3: CỦNG CỐ NGHIÊN CỨU, HOÀN THIỆN ỨNG DỤNG & BẢO VỆ
### Từ "hệ thống có khung đầy đủ" đến "bài nghiên cứu bảo vệ được + ứng dụng chạy thật"

Giai đoạn 3 được lập sau đợt rà soát ngày 2026-11-18. Lý do và bằng chứng chi tiết:
👉 [`docs/10_DANH_GIA_TONG_THE_VA_KE_HOACH_HOAN_THIEN.md`](../../docs/10_DANH_GIA_TONG_THE_VA_KE_HOACH_HOAN_THIEN.md)

Nguyên tắc quản trị giữ nguyên: **nghiệm thu xong backlog trước mới chuyển backlog sau** – riêng Backlog 08 là điều kiện cứng, vì mọi số liệu của Backlog 09–10 phụ thuộc vào nó.

---

## 1. CẤU TRÚC

```
phase-03-research-hardening/
├── backlog-08-integrity-and-reproducibility/   # Tuần 1 – sửa P0, test xanh, nguồn dữ liệu/kết quả duy nhất
├── backlog-09-research-strengthening/          # Tuần 2 – RQ1–RQ5, thống kê, robustness, đánh giá RAG
└── backlog-10-paper-app-and-defense/           # Tuần 3 – bài báo, demo, video, slide, tổng duyệt
```

Mỗi backlog có `README.md` (mục tiêu, phụ thuộc, DoD) và `MEMBER_1/2/3.md` (vai trò như Giai đoạn 1–2):
- **Thành viên 1** – Lead ML / Modeling & Evaluation
- **Thành viên 2** – Biomedical Data Engineer & Privacy
- **Thành viên 3** – Full-Stack AI & System Integrator

---

## 2. LỘ TRÌNH

```
 TUẦN 1 ─ BACKLOG 08: TOÀN VẸN & TÁI LẬP
   M2: dữ liệu chuẩn duy nhất + sửa de-ID ──┐
   M3: sửa /agent/explain, bỏ mock, CI    │ (song song)
   M1: chặn fallback BERT ngẫu nhiên ─────┴─► M1: huấn luyện lại 5 seed + lưu dự đoán
                                                   └─► M2: sinh lại DCA/fairness/confusion
                     ▼  Gate: pytest 100% · manifest dữ liệu · results registry
 TUẦN 2 ─ BACKLOG 09: NÂNG TẦM NGHIÊN CỨU
   RQ1 so sánh công bằng + CI · RQ2 phân rã tín hiệu văn bản · RQ3 mô phỏng bổ trợ
   RQ4 hiệu chuẩn/DCA/missing-modality · RQ5 đánh giá RAG & grounding
                     ▼  Gate: results registry đóng băng (freeze) – không chạy thêm thí nghiệm
 TUẦN 3 ─ BACKLOG 10: BẢN THẢO, ỨNG DỤNG & BẢO VỆ
   Paper sinh bảng tự động từ registry · Docker clean-run · Video · Slide · 2 buổi tổng duyệt
```

---

## 3. TRUY CẬP NHANH

| Backlog | Trọng tâm | Ưu tiên | Link |
| :---: | :--- | :---: | :--- |
| **08** | Sửa checkpoint/đánh giá sai, fallback BERT ngẫu nhiên, endpoint lỗi, mock gán cứng, rò PHI, PROBAST | **Bắt buộc** | [Backlog 08](backlog-08-integrity-and-reproducibility/README.md) |
| **09** | So sánh công bằng, CI bootstrap, phân rã tín hiệu văn bản, mô phỏng bổ trợ, DCA, robustness, RAG eval | Core + Optional | [Backlog 09](backlog-09-research-strengthening/README.md) |
| **10** | Bài báo TRIPOD+AI, demo, video, slide, Q&A, phát hành | **Bắt buộc** | [Backlog 10](backlog-10-paper-app-and-defense/README.md) |

## 4. QUY TẮC SỐ LIỆU (ÁP DỤNG TOÀN GIAI ĐOẠN 3)
1. **Một nguồn sự thật:** mọi con số trong paper/slide/UI phải đọc từ `results/registry.json` (Backlog 08 – M1). Không gõ tay số liệu.
2. **Một tập dữ liệu:** mọi script đánh giá phải kiểm tra SHA-256 và số dòng theo `data/DATA_MANIFEST.json` trước khi chạy.
3. **Không chọn mô hình theo test.** Chọn trên validation; test chỉ dùng để báo cáo.
4. **Báo cáo cả kết quả âm.** Nếu fusion không vượt baseline, đó vẫn là kết quả – viết đúng như vậy.
5. **Nhãn trung thực:** ghi "mô phỏng", "dữ liệu tổng hợp", "kiểm tra độ bền nội bộ (không phải ngoại kiểm)" ở mọi nơi tương ứng.
