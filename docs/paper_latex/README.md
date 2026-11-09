# Bản Thảo Bài Báo Khoa Học M-CDSS (LaTeX Đa Phân Mục Chuẩn TRIPOD-AI)

Thư mục này chứa toàn bộ mã nguồn **LaTeX** của bài báo khoa học dự án **M-CDSS**, được thiết kế theo kiến trúc đa file (Modular Multi-file Structure) kèm gói định dạng học thuật tùy chỉnh (`templates/mcdss_article.sty`) và các sơ đồ vector độ nét cao (`TikZ` & `SVG`).

---

## 1. Cấu Trúc Thư Mục Rõ Ràng (Dễ Theo Dõi & Chỉnh Sửa)

```text
docs/paper_latex/
├── main.tex                           # [FILE GỐC] Nạp template và ghép nối các phân mục bằng lệnh \input{}
├── references.bib                     # Cơ sở dữ liệu tài liệu tham khảo chuẩn BibTeX
├── templates/
│   └── mcdss_article.sty              # Gói định dạng (Template) chuẩn bài báo y sinh: bảng màu, TikZ styles, hộp lâm sàng
├── figures/
│   ├── fig01_system_architecture.tex  # Sơ đồ Vector TikZ 1: Kiến trúc phần mềm 3 tầng đóng gói Docker
│   ├── fig02_multi_agent_rag_flow.tex # Sơ đồ Vector TikZ 2: Đồ thị trạng thái hội chẩn đa tác tử (Agentic RAG)
│   ├── fig03_evidence_grounding.tex   # Sơ đồ Vector TikZ 3: Thuật toán đối sánh vị trí ký tự O(N) chống ảo giác
│   └── svg/                           # Bản xuất Vector SVG độc lập phục vụ chèn vào Slide / Word / Web
│       ├── fig01_system_architecture.svg
│       └── fig02_multi_agent_rag_flow.svg
└── sections/
    ├── 00_abstract.tex                # Tóm tắt có cấu trúc (Background, Objective, Methods, Results, Conclusions)
    ├── 01_introduction.tex            # Mở đầu & Khoảng trống nghiên cứu (dẫn chiếu JMIR 2024)
    ├── 02_clinical_cohort.tex         # Đoàn hệ lâm sàng 2.000 ca & Quy trình chống rò rỉ dữ liệu
    ├── 03_methodology_fusion.tex      # Kiến trúc FT-Transformer + Bio_ClinicalBERT + Cross-Attention + Temp Scaling
    ├── 04_software_architecture.tex   # ★ [Nhiệm vụ 3.2] Kiến trúc phần mềm 3 tầng & Giao thức RESTful API
    ├── 05_multi_agent_rag.tex         # ★ [Nhiệm vụ 3.2] Hệ thống Đa tác tử LangGraph & Evidence Grounding O(N)
    ├── 06_frontend_dca_ux.tex         # ★ [Nhiệm vụ 3.2] Giao diện Bác sĩ, Đồ thị DCA tương tác & Docker Compose
    ├── 07_empirical_results.tex       # Kết quả thực nghiệm (N=302), Ablation Study, Case Study PT-0044 & PT-0254
    └── 08_discussion_ethics.tex       # Thảo luận, Bảng kiểm 4 miền PROBAST & Tuyên bố Y đức
```

---

## 2. Hướng Dẫn Chỉnh Sửa Nhanh Cho Từng Thành Viên

- **Khi muốn chỉnh sửa phần của Thành viên 3 (*Software Architecture, Multi-Agent RAG, UI/DCA, Docker*):**
  Chỉ cần mở và sửa trực tiếp 3 file:
  1. `sections/04_software_architecture.tex`
  2. `sections/05_multi_agent_rag.tex`
  3. `sections/06_frontend_dca_ux.tex`
- **Khi muốn tinh chỉnh màu sắc, kích thước chữ hoặc khung sơ đồ:**
  Mở file `templates/mcdss_article.sty` (các màu chủ đạo `mcdssPrimary`, `mcdssSecondary`, `mcdssAccent` được định nghĩa tập trung tại Mục 5).
- **Khi muốn chỉnh sửa nội dung các hình vẽ sơ đồ trong bài báo:**
  Mở trực tiếp `figures/fig01_system_architecture.tex`, `figures/fig02_multi_agent_rag_flow.tex` hoặc `figures/fig03_evidence_grounding.tex`. Vì sử dụng thư viện vector **TikZ**, sơ đồ sẽ tự động co giãn độ nét vô cực khi xuất ra PDF mà không cần phần mềm vẽ ngoài.

---

## 3. Hướng Dẫn Biên Dịch Sang PDF

### Cách 1: Biên dịch trên Overleaf (Khuyên dùng - Không cần cài đặt)
1. Nén toàn bộ thư mục `docs/paper_latex/` thành file `mcdss_paper_latex.zip`.
2. Tải lên [Overleaf](https://www.overleaf.com/) (`New Project` $\rightarrow$ `Upload Project`).
3. Chọn trình biên dịch **pdfLaTeX** (hoặc **XeLaTeX**) và nhấn **Recompile**.

### Cách 2: Biên dịch trên máy cá nhân (TeX Live / MiKTeX)
Chạy chuỗi lệnh sau tại thư mục `docs/paper_latex/`:
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

