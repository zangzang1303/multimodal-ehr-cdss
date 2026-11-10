# BACKLOG 05: AGENTIC RAG, EVIDENCE GROUNDING & PHẦN MỀM FULL-STACK
### Giai đoạn 2 (Tuần 8–10) | Mục tiêu: giải trình có thể kiểm chứng và hoàn thiện ứng dụng nghiên cứu

---

## 1. MỤC TIÊU CỐT LÕI CỦA BACKLOG 05
Xây dựng tầng trí tuệ tác tử (Agentic Layer) đối chiếu phác đồ điều trị chuẩn và liên kết toàn bộ hệ thống từ Backend tới Frontend:
1. **Cơ sở tri thức Phác đồ Y tế (Vector DB):** Phân mảnh theo cấu trúc y khoa (*GINA, GOLD, ESC, Bộ Y tế*) và nạp vào Qdrant Vector Store.
2. **Tìm kiếm lai (Hybrid Retriever):** Kết hợp khoảng cách Cosine từ vector dense với lọc từ khóa chính xác BM25.
3. **Multi-Agent Hội chẩn Lâm sàng:** Phân tích chẩn đoán phân biệt đối kháng 2 chiều giữa 2 bệnh có xác suất cao nhất, rà soát dấu hiệu cờ đỏ (Red Flags).
4. **Định vị bằng chứng (Evidence Grounding):** Trả về offset có thể kiểm chứng trong ghi chú đã khử định danh. Claim thiếu nguồn phải bị từ chối hoặc gắn nhãn chưa xác minh; trùng chuỗi không tự chứng minh diễn giải lâm sàng đúng.
5. **Hệ thống Full-Stack hoàn chỉnh:** Tích hợp Backend FastAPI bất đồng bộ và Giao diện Bác sĩ Next.js 14 với bộ 4 components cốt lõi: `PatientDataForm`, `DiagnosticCard`, `EvidenceViewer`, `GuidelineDrawer`.

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT (PREREQUISITES)
- Đã nghiệm thu Backlog 04, có checkpoint được chọn trên validation và kết quả strict test được báo cáo trung thực.
- Tệp checkpoint tối ưu `data/checkpoints/multimodal_best.pt` đã sẵn sàng.
- Chốt danh mục phác đồ được phép sử dụng, phiên bản/ngày truy cập, quyền lưu trữ và metadata trích dẫn trước khi nạp Qdrant; không gắn tài liệu chưa kiểm tra nguồn vào lời khuyên.
- Đã đọc [tài liệu Agentic RAG](../../../docs/04_AGENTIC_RAG_AND_EXPLAINABILITY.md).

---

## 3. PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN TRONG BACKLOG 05

* 🧬 **Thành viên 1 (Lead ML / Modeling):** Phụ trách đánh giá embedding model (`rag_config.yaml`), thiết kế đầu ra giải trình có cấu trúc cho `DiagnosticAgent`, và đo độ trễ suy luận trên môi trường ghi rõ cấu hình. 👉 [Xem chi tiết MEMBER_1.md](MEMBER_1.md)
* 🗄️ **Thành viên 2 (Biomedical Data & Privacy):** Phụ trách phân mảnh phác đồ (`knowledge_ingest.py`), nạp Qdrant, hiện thực thuật toán `evidence_grounder.py` và viết route `POST /api/v1/agent/explain`. 👉 [Xem chi tiết MEMBER_2.md](MEMBER_2.md)
* 💻 **Thành viên 3 (Full-Stack AI & Agent):** Phụ trách Hybrid Retriever (`retriever.py`), `GuidelineDrawer.tsx`, `EvidenceViewer.tsx` (highlight văn bản), bộ Unit Tests `tests/test_agent_rag.py` và nối API client `lib/api.ts`. 👉 [Xem chi tiết MEMBER_3.md](MEMBER_3.md)

---

## 4. TIÊU CHUẨN NGHIỆM THU ĐỂ CHUYỂN SANG BACKLOG 06 (DEFINITION OF DONE)
Backlog 05 hoàn thành khi:
- [ ] `pytest tests/test_agent_rag.py -v` kiểm tra offset trên đúng phiên bản ghi chú đã khử định danh, từ chối claim không có nguồn và không xuất trích dẫn phác đồ thiếu định danh tài liệu/mục/phiên bản.
- [ ] Qdrant chứa tập phác đồ đã kiểm nguồn và quyền sử dụng; mỗi chunk có định danh tài liệu, phiên bản, mục/trang và nội dung có thể truy ngược. Báo cáo số chunk thực tế, không lấy số lượng làm thước đo chất lượng.
- [ ] Giao diện Web Next.js tại `http://localhost:3000` hoạt động trơn tru:
  1. Nhập ca bệnh $\rightarrow$ Bấm phân tích.
  2. Hiển thị xác suất đã hiệu chuẩn.
  3. Tự động highlight màu các câu chứng cứ trong bệnh án.
  4. Bấm xem phác đồ trượt mở drawer hiển thị đúng nội dung GINA/GOLD/ESC tương ứng.
- [ ] Các API có test cho cả yêu cầu hợp lệ và lỗi (4xx/5xx); đo p50/p95 độ trễ với phần cứng, kích thước đầu vào và phạm vi đo được công bố. UI hiển thị rõ trường hợp thiếu bằng chứng hoặc dịch vụ RAG không sẵn sàng.
