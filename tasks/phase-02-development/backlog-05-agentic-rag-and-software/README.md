# BACKLOG 03: AGENTIC RAG, EVIDENCE GROUNDING & PHẦN MỀM FULL-STACK
### Giai Đoạn 3 (Tuần 8 – Tuần 10) | Mục Tiêu: Triệt Tiêu Ảo Giác Bằng Tri Thức Y Khoa & Hoàn Thiện Web App Bác Sĩ

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 03
Xây dựng tầng trí tuệ tác tử (Agentic Layer) đối chiếu phác đồ điều trị chuẩn và liên kết toàn bộ hệ thống từ Backend tới Frontend:
1. **Cơ sở tri thức Phác đồ Y tế (Vector DB):** Phân mảnh theo cấu trúc y khoa (*GINA, GOLD, ESC, Bộ Y tế*) và nạp vào Qdrant Vector Store.
2. **Tìm kiếm lai (Hybrid Retriever):** Kết hợp khoảng cách Cosine từ vector dense với lọc từ khóa chính xác BM25.
3. **Multi-Agent Hội chẩn Lâm sàng:** Phân tích chẩn đoán phân biệt đối kháng 2 chiều giữa 2 bệnh có xác suất cao nhất, rà soát dấu hiệu cờ đỏ (Red Flags).
4. **Định vị bằng chứng (Evidence Grounding):** Thuật toán tìm vị trí chuỗi ký tự `[start_char, end_char]` trong bệnh án gốc, loại bỏ hoàn toàn các câu bịa đặt (Zero-Hallucination).
5. **Hệ thống Full-Stack hoàn chỉnh:** Tích hợp Backend FastAPI bất đồng bộ và Giao diện Bác sĩ Next.js 14 với bộ 4 components cốt lõi: `PatientDataForm`, `DiagnosticCard`, `EvidenceViewer`, `GuidelineDrawer`.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- **Đã hoàn thành nghiệm thu 100% Backlog 02.**
- Tệp checkpoint tối ưu `data/checkpoints/multimodal_best.pt` đã sẵn sàng.
- Đã đọc kỹ tài liệu: [`docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md`](../../docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 03

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách đánh giá embedding model (`rag_config.yaml`), thiết kế Prompt CoT đối kháng cho `DiagnosticAgent`, và tối ưu hóa thời gian suy luận GPU trên FastAPI (<150ms). 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách phân mảnh phác đồ (`knowledge_ingest.py`), nạp Qdrant, hiện thực thuật toán `evidence_grounder.py` và viết route `POST /api/v1/agent/explain`. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách Hybrid Retriever (`retriever.py`), `GuidelineDrawer.tsx`, `EvidenceViewer.tsx` (highlight văn bản), bộ Unit Tests `tests/test_agent_rag.py` và nối API client `lib/api.ts`. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 04 (DEFINITION OF DONE)
Backlog 03 chỉ được xem là hoàn thành khi:
- [ ] Chạy `pytest tests/test_agent_rag.py -v` vượt qua 100% test cases: Xác thực 100% câu trích dẫn bằng chứng đều map đúng chuỗi ký tự trong văn bản bệnh án gốc.
- [ ] Cơ sở dữ liệu Qdrant chứa tối thiểu 100 chunks phác đồ lâm sàng chuẩn hóa có metadata rõ ràng.
- [ ] Giao diện Web Next.js tại `http://localhost:3000` hoạt động trơn tru:
  1. Nhập ca bệnh $\rightarrow$ Bấm phân tích.
  2. Hiển thị xác suất đã hiệu chuẩn.
  3. Tự động highlight màu các câu chứng cứ trong bệnh án.
  4. Bấm xem phác đồ trượt mở drawer hiển thị đúng nội dung GINA/GOLD/ESC tương ứng.
- [ ] Toàn bộ API endpoints phản hồi với mã trạng thái HTTP 200 và thời gian phản hồi hợp lý.
