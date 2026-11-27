# Kịch Bản Video Demo Lâm Sàng: Hệ Thống Hỗ Trợ Chẩn Đoán Đa Phương Thức M-CDSS (Cập nhật Giai Đoạn 3)

> **Thời lượng tiêu chuẩn:** 4 phút 30 giây (trong khung 3–5 phút theo Backlog 10 Nhiệm vụ 3.3).
>
> **Độ phân giải khuyến nghị:** Full HD (1920 × 1080, 60fps).
>
> **Phong cách trình bày:** Khách quan, trung thực khoa học; thao tác trực tiếp trên giao diện Web M-CDSS thực tế kết nối backend cục bộ.
>
> **Lưu ý về trạng thái số liệu (cập nhật 2026-11-27):** Các khung số liệu trước đây để trống nay đã điền từ results/registry.json; phần còn lại giữ nguyên làm vị trí chờ điền kết quả thực nghiệm đa seed chính thức (RQ1–RQ4) từ Thành viên 1 và Thành viên 2. Toàn bộ thông số hệ thống, truy xuất RAG (64 đoạn JSON phác đồ xác minh đọc-chỉ chiều 768/`chunk_id`/SHA-256 nội dung/8 metadata trong Qdrant sống nhưng dùng vector băm 768-D ngoại tuyến do thiếu `all-mpnet-base-v2`, 60 truy vấn, kiểm định sơ bộ khớp chuỗi 50 ca trên `data/processed/test.parquet` $N=287$ chưa phải `strict 302`) và độ trễ HTTP Docker end-to-end đã điền từ đo đạc thực tế tại `results/rag_evaluation_report.json` và `results/latency_report.json`.
>
> **Phương án dự phòng:** Xuất bản ghi hình MP4 cục bộ độ phân giải Full HD kèm ảnh chụp màn hình từng bước phòng trường hợp mạng/GPU trục trặc khi demo trực tiếp.

---

## 1. Bảng Phân Bổ Thời Lượng 5 Phân Cảnh (Khung Chuẩn Phase 3)

| Phân cảnh  | Nội dung trọng tâm                                                                             | Thời lượng | Mốc thời gian |
| :--------: | :--------------------------------------------------------------------------------------------- | :--------: | :-----------: |
| **Cảnh 1** | Bài toán lâm sàng, Khoảng trống JMIR (2024) & Cảnh báo phạm vi nghiên cứu                      |  30 giây   | `0:00 – 0:30` |
| **Cảnh 2** | Nhập ca tổng hợp → Xác suất hiệu chuẩn → Tô sáng bằng chứng → Ngăn kéo phác đồ                 |  90 giây   | `0:30 – 2:00` |
| **Cảnh 3** | Minh họa RQ4 (Tắt phương thức văn bản / bảng) & Ca mô hình bất định (`< 55%`)                  |  60 giây   | `2:00 – 3:00` |
| **Cảnh 4** | Trang đánh giá (`/evaluation`): CI đa seed, phân rã văn bản RQ2, DCA & Tab Phase 3 RAG/Latency |  60 giây   | `3:00 – 4:00` |
| **Cảnh 5** | Giới hạn trung thực, PROBAST & Hướng phát triển                                                |  30 giây   | `4:00 – 4:30` |

---

## 2. Kịch Bản Chi Tiết Từng Phân Cảnh

---

### PHÂN CẢNH 1: BÀI TOÁN & CẢNH BÁO PHẠM VI NGHIÊN CỨU (`0:00 – 0:30`)

- **Hình ảnh hiển thị (Visuals):**
    - `0:00 – 0:15`: Màn hình tiêu đề **M-CDSS**, tóm tắt bài toán phân biệt 4 hội chứng hô hấp–tim mạch (_ASTHMA, COPD, CHF, CAP_) và phát hiện từ JMIR (2024): 15/15 nghiên cứu chỉ dùng dữ liệu bảng, 0/15 đạt chuẩn Low Risk of Bias theo PROBAST.
    - `0:15 – 0:30`: Phóng cận cảnh thanh **`ResearchDisclaimerBanner`** ở đầu giao diện Web (`/`) và **`ModelCardFooter`** ở chân trang (hiển thị SHA-256 của checkpoint, nhãn **`MOCK — chờ TV2`** cho `data_manifest_sha256` placeholder hiện tại, và `reasoning_mode = deterministic_template`).

- **Lời thuyết minh (Voiceover):**

    > _"Xin kính chào thầy cô và hội đồng. Trong chăm sóc ban đầu và cấp cứu, bốn hội chứng Hen phế quản, COPD, Suy tim và Viêm phổi có triệu chứng chồng lấp rất dễ nhầm lẫn. Theo tổng quan trên tạp chí JMIR năm 2024, cả 15 nghiên cứu đạt chuẩn đều chỉ dùng dữ liệu bảng mà bỏ qua ghi chú bác sĩ, và chưa có nghiên cứu nào đạt nguy cơ sai lệch thấp theo PROBAST. Nhóm xây dựng nguyên mẫu nghiên cứu M-CDSS để khảo sát câu hỏi đó. Xin lưu ý ngay từ đầu: dữ liệu huấn luyện–kiểm thử hiện tại là bộ dữ liệu tổng hợp từ Synthea và MTSamples, và M-CDSS là nguyên mẫu phục vụ nghiên cứu học thuật, tuyệt đối không dùng để ra quyết định điều trị tự động trên bệnh nhân thật."_

- **Phụ đề nhấn mạnh:**
    - `[Cảnh báo Phạm vi]`: Research Prototype | Synthesized Cohort (Synthea + MTSamples) | Không thay thế bác sĩ.

---

### PHÂN CẢNH 2: NHẬP CA TỔNG HỢP, XÁC SUẤT HIỆU CHUẨN, BẰNG CHỨNG & PHÁC ĐỒ (`0:30 – 2:00`)

- **Thao tác giao diện (UI Actions):**
    - `0:30 – 0:55`: Trên trang chính (`/`), trỏ vào `PatientDataForm.tsx` nhập hoặc nạp một ca bệnh tổng hợp điển hình (ví dụ `PT-0044`, nữ 18 tuổi, đo ngoài cơn cấp với $\text{SpO}_2 = 97,3\%$, $\text{CRP} = 24,28\text{ mg/L}$, kèm ghi chú bệnh sử dùng ống hít giãn phế quản và cơn khò khè). Kiểm tra validation biên sinh lý và nhấn nút hội chẩn.
    - `0:55 – 1:25`: Quan sát `DiagnosticCard.tsx` hiển thị phân phối xác suất đã hiệu chuẩn nhiệt độ (`PT-0254: COPD 92.7%; PT-0044: ASTHMA 58.0%`, $\text{ECE} = 0.077$) cùng huy hiệu **`reasoning_mode = deterministic_template`**, đặt cạnh dự đoán đối chứng của các baseline đơn phương thức (nhấn mạnh tắt mặc định mock fallback khi `NEXT_PUBLIC_DEMO_MOCK` không bật).
    - `1:25 – 2:00`: Cuộn xuống **`EvidenceViewer.tsx`** cho thấy các cụm từ bằng chứng được tô sáng khớp chính xác vị trí ký tự (`[start_char, end_char]`) ngay trên bệnh án gốc. Mở **`GuidelineDrawer.tsx`** bên phải màn hình, đối chiếu trích đoạn phác đồ **GINA 2024 / GOLD 2024 / ESC 2023 / Bộ Y tế 2020** truy xuất từ kho **64 đoạn JSON chuẩn hóa** đồng bộ trực tiếp trong Qdrant `v1.20.0`.

- **Lời thuyết minh (Voiceover):**

    > _"Trên bàn làm việc hội chẩn, bác sĩ nhập đồng thời 13 biến bảng số có kiểm soát giới hạn sinh lý và ghi chú lâm sàng tự do. Với ca tổng hợp mẫu PT-0044, mô hình bảng số đơn thuần dễ bị nhiễu bởi chỉ số CRP cao và SpO2 bình thường ngoài cơn cấp. Khi đi qua kiến trúc dung hợp đa phương thức kết hợp tầng hiệu chuẩn Temperature Scaling, hệ thống đưa ra phân phối xác suất hiệu chuẩn (`COPD 92.7%`) và ghi rõ chế độ giải trình deterministic_template. Tiếp theo, hệ thống Agentic RAG vừa neo chính xác từng cụm từ bằng chứng theo chỉ số ký tự trên ghi chú gốc để chống bịa đặt triệu chứng, vừa mở ngăn kéo phác đồ từ kho 64 đoạn tri thức chuẩn hóa GINA, GOLD, ESC và Bộ Y tế Việt Nam."_

- **Phụ đề nhấn mạnh:**
    - `[Evidence Grounding — Sơ bộ]`: Khớp vị trí ký tự (`200/200` claim pipeline trên tập `test.parquet` $N=287$, chưa phải `strict 302`) | Từ chối `50/50` đầu dò ngoài ghi chú _(chưa thay thế kiểm tra ngữ nghĩa)_.
    - `[Guideline KB]`: 64 đoạn JSON (xác minh đọc-chỉ chiều 768/`chunk_id`/SHA-256/8 metadata trong Qdrant `v1.20.0`; vector băm 768-D ngoại tuyến, chưa xác nhận ngữ nghĩa vector).

---

### PHÂN CẢNH 3: MÔ PHỎNG THIẾU PHƯƠNG THỨC (RQ4) & CA BẤT ĐỊNH (`2:00 – 3:00`)

- **Thao tác giao diện (UI Actions):**
    - `2:00 – 2:30`: Quay lại `PatientDataForm.tsx`, bật công tắc **RQ4 Missing-Modality Toggle** ("Tắt phương thức văn bản / chỉ giữ sinh hiệu" hoặc ngược lại), nhấn chạy lại hội chẩn để thấy trực tiếp xác suất dự đoán thay đổi rõ rệt và trạng thái thiếu phương thức được ghi nhận trong luồng đối chứng (`AUROC cross-attention 0.956 → 0.902 khi mất văn bản`).
    - `2:30 – 3:00`: Nạp một ca bệnh có triệu chứng chồng lấp hoặc dữ liệu nghèo nàn làm xác suất Top-1 hạ xuống dưới **$55\%$** (`confidence < 0.55`), quay cận cảnh hộp **Cảnh báo Bất định Lâm sàng** màu hổ phách trên `DiagnosticCard.tsx` khuyến cáo bác sĩ hội chẩn chuyên khoa bổ sung thay vì tin cậy tự động.

- **Lời thuyết minh (Voiceover):**

    > _"Để minh họa trực tiếp câu hỏi nghiên cứu RQ4 về độ bền khi thiếu phương thức lâm sàng, giao diện tích hợp công tắc giả lập thiếu văn bản hoặc thiếu sinh hiệu. Khi tắt phần ghi chú bệnh án, bác sĩ quan sát ngay mức dịch chuyển phân phối xác suất của mô hình (`AUROC 0.956 → 0.678 khi mất toàn bộ dữ liệu bảng`). Đặc biệt, với những ca khó mà xác suất Top-1 xuống dưới ngưỡng an toàn 55%, thẻ chẩn đoán tự động kích hoạt cảnh báo bất định lâm sàng, nhắc bác sĩ không dựa vào gợi ý AI một cách máy móc."_

- **Phụ đề nhấn mạnh:**
    - `[RQ4 Live Toggle]`: Bỏ phương thức văn bản $\rightarrow$ Quan sát biến thiên xác suất trực tiếp.
    - `[Uncertainty Guardrail]`: Top-1 $< 55\%$ $\rightarrow$ Hiển thị cảnh báo bất định bắt buộc.

---

### PHÂN CẢNH 4: TRANG ĐÁNH GIÁ (`/evaluation`) — CI ĐA SEED, RQ2, DCA & RAG/LATENCY (`3:00 – 4:00`)

- **Thao tác giao diện (UI Actions):**
    - `3:00 – 3:20`: Chuyển sang `/evaluation`. Ở Tab 1, lướt qua bảng đối chứng đa seed kèm khoảng tin cậy 95% (95% CI) của **RQ1** (`cross-attention AUROC 0.956 ± 0.008, F1 0.691; BERT-FT 0.975 ± 0.004; ensemble 0.978; grouped CV cross-attention 0.949 ± 0.016`) và phân rã đóng góp văn bản **RQ2** (`BERT-FT 0.974 (gốc) → 0.679 (che mọi con số)`).
    - `3:20 – 3:40`: Chuyển sang Tab 2 (**DCA & PROBAST**), kéo thanh trượt ngưỡng quyết định can thiệp trong dải lâm sàng $p_t \in [0,10; 0,45]$ trên `DCACurveChart.tsx` (`NB cross-attention 0.344 vs can thiệp tất cả 0.189; giảm 61.9 can thiệp/100 BN – chỉ minh hoạ (106 ca suy tim test từ 1 bệnh nhân gốc)`).
    - `3:40 – 4:00`: Chuyển sang **Tab 3 (Phase 3 Research Hardening — Registry)** tải trực tiếp từ `/api/v1/evaluation/registry`, trình chiếu số liệu **đo thực tế** của Thành viên 3:
        - **RQ5 RAG qua Qdrant Docker sống (60 truy vấn, $\kappa = 0,9449$ — vector băm 768-D ngoại tuyến, chưa dùng `all-mpnet-base-v2`):** `dense_only` (`R@1 = 0,7833`, `R@3 = 0,9167`, `MRR = 0,8688`), `bm25_only` & `hybrid_rrf` (`R@1 = 0,9000`, `R@3 = 0,9500`, `R@5 = 1,0000`, `MRR = 0,9319`); Kiểm tra sơ bộ trên 50 ca từ `data/processed/test.parquet` ($N=287$, trạng thái `preliminary_non_strict_holdout` — chưa phải `strict 302`, 0 template fallback): `200/200` claim pipeline thỏa mãn bất biến cắt chuỗi (`1,00`), `50/50` đầu dò chuỗi ngoài ghi chú bị loại (`out_of_note_probe_rejection_rate = 1,00` — *chỉ chứng minh khớp chuỗi, chưa chứng minh độ đúng ngữ nghĩa*); 20 mẫu span xuất ra `grounding_manual_audit_20_samples.json` đang hiển thị **`Chờ chấm tay (20 mẫu)`**.
        - **Độ trễ HTTP Docker đầu-cuối (200 lượt gọi ấm):** `/api/v1/agent/explain` (**HTTP 200**) đạt $p_{50} = 62,92\text{ ms}$, $p_{95} = 84,23\text{ ms}$; `/api/v1/predict/baseline` và `/predict/multimodal` trả HTTP 503 an toàn ($p_{95} = 51,24\text{ ms}$ và $50,55\text{ ms}$) khi thiếu model/PyTorch.

- **Lời thuyết minh (Voiceover):**

    > _"Trên trang Đánh giá hợp nhất lấy dữ liệu từ Registry chuẩn hóa, hội đồng có thể kiểm tra kết quả đa seed kèm khoảng tin cậy cho RQ1, phân tích đóng góp văn bản ở RQ2 (`số liệu RQ2 trong results/registry.json`), và đường cong lợi ích ròng DCA Macro One-vs-Rest 4 lớp giới hạn trong dải ngưỡng 10 đến 45 phần trăm. Đặc biệt ở thẻ Phase 3, phép kiểm tra chỉ đọc qua Qdrant Docker 64 điểm đã xác minh khớp chiều 768, 64 chunk_id, SHA-256 nội dung và 8 trường metadata — dù chưa xác nhận chất lượng ngữ nghĩa của vector do vẫn đang dùng vector băm 768 chiều ngoại tuyến (Recall@3 bằng 0,95 và Recall@5 bằng 1,0 trên 60 truy vấn, còn `all-mpnet-base-v2` vẫn ở trạng thái chờ). Về phần grounding 50 ca trên tập `data/processed/test.parquet` N=287, chúng em ghi rõ đây mới là kết quả kiểm tra sơ bộ (chưa phải hold-out strict N=302): pipeline khớp tọa độ cắt chuỗi 200 trên 200 đoạn và từ chối 50 trên 50 đầu dò ngoài bệnh án, 20 mẫu ngữ nghĩa đang chờ chấm tay, và độ trễ HTTP đầu-cuối qua Docker của /agent/explain đạt trung vị 62,92 mili-giây và p95 đạt 84,23 mili-giây."_

- **Phụ đề nhấn mạnh:**
    - `[RQ5 RAG Sơ bộ]`: 60 queries ($\kappa=0,9449$, hash 768-D — chờ `mpnet`) | `hybrid_rrf` R@3=0,95, R@5=1,00 | Sơ bộ chuỗi `200/200` + ngoài note `50/50` (`test.parquet` N=287, chưa phải `strict 302`) | 20 mẫu `chấm ngữ nghĩa thủ công: chưa thực hiện`.
    - `[Docker HTTP Latency]`: `/agent/explain` $p_{50} = 62,92\text{ ms}$, $p_{95} = 84,23\text{ ms}$.

---

### PHÂN CẢNH 5: GIỚI HẠN TRUNG THỰC & HƯỚNG PHÁT TRIỂN (`4:00 – 4:30`)

- **Hình ảnh hiển thị (Visuals):**
    - `4:00 – 4:15`: Hiển thị bảng tổng hợp kiểm toán 4 miền **PROBAST** (_Low Risk_) đặt cạnh thẻ **Giới hạn Trung thực**.
    - `4:15 – 4:30`: Màn hình kết thúc nêu 3 hướng phát triển: ngoại kiểm trên **MIMIC-IV**, khảo sát đánh giá hữu dụng của bác sĩ lâm sàng, và tích hợp mô hình ngôn ngữ cục bộ có ràng buộc đối chiếu tọa độ qua `EvidenceGrounder` kết hợp kiểm duyệt của bác sĩ.

- **Lời thuyết minh (Voiceover):**

    > _"Cuối cùng, nhóm nhìn nhận thẳng thắn các giới hạn hiện tại: bộ dữ liệu còn mang tính tổng hợp chưa qua ngoại kiểm bệnh viện thật, mô hình mới dừng ở phân loại đơn nhãn 4 bệnh, cơ chế grounding ký tự giúp giảm trích dẫn vô căn cứ nhưng không loại bỏ hết sai lệch ngữ nghĩa, và ở chế độ ngoại tuyến không có trọng số all-mpnet-base-v2 hay Bio_ClinicalBERT cục bộ, hệ thống chủ động lùi về dense băm 768 chiều hoặc trả HTTP 503 thay vì giả lập kết quả. Hướng đi tiếp theo của nhóm là thẩm định ngoại kiểm trên MIMIC-IV, lấy ý kiến bác sĩ nội trú và tích hợp LLM cục bộ có kiểm tra trích dẫn. Em xin trân trọng cảm ơn."_

- **Phụ đề nhấn mạnh:**
    - `[Trung thực Khoa học]`: Chưa ngoại kiểm MIMIC-IV/BV | Safeguard 503 khi thiếu weight thật | Định hướng: MIMIC-IV + Clinician Survey + Constrained LLM.
