# Kịch Bản Video Demo Lâm Sàng: Hệ Thống Hỗ Trợ Chẩn Đoán Đa Phương Thức M-CDSS (Cập nhật Giai Đoạn 3)

> **Thời lượng tiêu chuẩn:** 4 phút 30 giây (trong khung 3–5 phút theo Backlog 10 Nhiệm vụ 3.3).
>
> **Độ phân giải khuyến nghị:** Full HD (1920 × 1080, 60fps).
>
> **Phong cách trình bày:** Khách quan, trung thực khoa học; thao tác trực tiếp trên giao diện Web M-CDSS thực tế kết nối backend cục bộ.
>
> **Lưu ý về trạng thái số liệu `[TODO-TV1/TV2]`:** Các khung `[TODO-TV1/TV2: ...]` giữ nguyên làm vị trí chờ điền kết quả thực nghiệm đa seed chính thức (RQ1–RQ4) từ Thành viên 1 và Thành viên 2. Toàn bộ thông số hệ thống, truy xuất RAG (64 đoạn JSON phác đồ / 70 chỉ mục, 60 truy vấn, kiểm định 50 ca) và độ trễ CPU đã điền từ đo đạc thực tế tại `results/rag_evaluation_report.json` và `results/latency_report.json`.
>
> **Phương án dự phòng:** Xuất bản ghi hình MP4 cục bộ độ phân giải Full HD kèm ảnh chụp màn hình từng bước phòng trường hợp mạng/GPU trục trặc khi demo trực tiếp.

---

## 1. Bảng Phân Bổ Thời Lượng 5 Phân Cảnh (Khung Chuẩn Phase 3)

| Phân cảnh | Nội dung trọng tâm | Thời lượng | Mốc thời gian |
| :---: | :--- | :---: | :---: |
| **Cảnh 1** | Bài toán lâm sàng, Khoảng trống JMIR (2024) & Cảnh báo phạm vi nghiên cứu | 30 giây | `0:00 – 0:30` |
| **Cảnh 2** | Nhập ca tổng hợp → Xác suất hiệu chuẩn → Tô sáng bằng chứng → Ngăn kéo phác đồ | 90 giây | `0:30 – 2:00` |
| **Cảnh 3** | Minh họa RQ4 (Tắt phương thức văn bản / bảng) & Ca mô hình bất định (`< 55%`) | 60 giây | `2:00 – 3:00` |
| **Cảnh 4** | Trang đánh giá (`/evaluation`): CI đa seed, phân rã văn bản RQ2, DCA & Tab Phase 3 RAG/Latency | 60 giây | `3:00 – 4:00` |
| **Cảnh 5** | Giới hạn trung thực, PROBAST & Hướng phát triển | 30 giây | `4:00 – 4:30` |

---

## 2. Kịch Bản Chi Tiết Từng Phân Cảnh

---

### PHÂN CẢNH 1: BÀI TOÁN & CẢNH BÁO PHẠM VI NGHIÊN CỨU (`0:00 – 0:30`)

* **Hình ảnh hiển thị (Visuals):**
  * `0:00 – 0:15`: Màn hình tiêu đề **M-CDSS**, tóm tắt bài toán phân biệt 4 hội chứng hô hấp–tim mạch (*ASTHMA, COPD, CHF, CAP*) và phát hiện từ JMIR (2024): 15/15 nghiên cứu chỉ dùng dữ liệu bảng, 0/15 đạt chuẩn Low Risk of Bias theo PROBAST.
  * `0:15 – 0:30`: Phóng cận cảnh thanh **`ResearchDisclaimerBanner`** ở đầu giao diện Web (`/`) và **`ModelCardFooter`** ở chân trang (`checkpoint`, SHA-256 `723facc17e37`, `reasoning_mode = deterministic_template`).

* **Lời thuyết minh (Voiceover):**
  > *"Xin kính chào thầy cô và hội đồng. Trong chăm sóc ban đầu và cấp cứu, bốn hội chứng Hen phế quản, COPD, Suy tim và Viêm phổi có triệu chứng chồng lấp rất dễ nhầm lẫn. Theo tổng quan trên tạp chí JMIR năm 2024, cả 15 nghiên cứu đạt chuẩn đều chỉ dùng dữ liệu bảng mà bỏ qua ghi chú bác sĩ, và chưa có nghiên cứu nào đạt nguy cơ sai lệch thấp theo PROBAST. Nhóm xây dựng nguyên mẫu nghiên cứu M-CDSS để khảo sát câu hỏi đó. Xin lưu ý ngay từ đầu: dữ liệu huấn luyện–kiểm thử hiện tại là bộ dữ liệu tổng hợp từ Synthea và MTSamples, và M-CDSS là nguyên mẫu phục vụ nghiên cứu học thuật, tuyệt đối không dùng để ra quyết định điều trị tự động trên bệnh nhân thật."*

* **Phụ đề nhấn mạnh:**
  * `[Cảnh báo Phạm vi]`: Research Prototype | Synthesized Cohort (Synthea + MTSamples) | Không thay thế bác sĩ.

---

### PHÂN CẢNH 2: NHẬP CA TỔNG HỢP, XÁC SUẤT HIỆU CHUẨN, BẰNG CHỨNG & PHÁC ĐỒ (`0:30 – 2:00`)

* **Thao tác giao diện (UI Actions):**
  * `0:30 – 0:55`: Trên trang chính (`/`), trỏ vào `PatientDataForm.tsx` nhập hoặc nạp một ca bệnh tổng hợp điển hình (ví dụ `PT-0044`, nữ 18 tuổi, đo ngoài cơn cấp với $\text{SpO}_2 = 97,3\%$, $\text{CRP} = 24,28\text{ mg/L}$, kèm ghi chú bệnh sử dùng ống hít giãn phế quản và cơn khò khè). Kiểm tra validation biên sinh lý và nhấn nút hội chẩn.
  * `0:55 – 1:25`: Quan sát `DiagnosticCard.tsx` hiển thị phân phối xác suất đã hiệu chuẩn nhiệt độ (`[TODO-TV1/TV2: Điền % dự đoán đa phương thức chính thức trên ca mẫu tổng hợp]`, $\text{ECE} = \text{[TODO-TV2: Điền ECE chính thức]}$) cùng huy hiệu **`reasoning_mode = deterministic_template`**, đặt cạnh dự đoán đối chứng của các baseline đơn phương thức (nhấn mạnh tắt mặc định mock fallback khi `NEXT_PUBLIC_DEMO_MOCK` không bật).
  * `1:25 – 2:00`: Cuộn xuống **`EvidenceViewer.tsx`** cho thấy các cụm từ bằng chứng được tô sáng khớp chính xác vị trí ký tự (`[start_char, end_char]`) ngay trên bệnh án gốc. Mở **`GuidelineDrawer.tsx`** bên phải màn hình, đối chiếu trích đoạn phác đồ **GINA 2024 / GOLD 2024 / ESC 2023 / Bộ Y tế 2020** truy xuất từ kho **64 đoạn JSON chuẩn hóa** (cộng 6 hạt giống = **70 vector** trong Qdrant).

* **Lời thuyết minh (Voiceover):**
  > *"Trên bàn làm việc hội chẩn, bác sĩ nhập đồng thời 13 biến bảng số có kiểm soát giới hạn sinh lý và ghi chú lâm sàng tự do. Với ca tổng hợp mẫu PT-0044, mô hình bảng số đơn thuần dễ bị nhiễu bởi chỉ số CRP cao và SpO2 bình thường ngoài cơn cấp. Khi đi qua kiến trúc dung hợp đa phương thức kết hợp tầng hiệu chuẩn Temperature Scaling, hệ thống đưa ra phân phối xác suất hiệu chuẩn (`[TODO-TV1/TV2: %]`) và ghi rõ chế độ giải trình deterministic_template. Tiếp theo, hệ thống Agentic RAG vừa neo chính xác từng cụm từ bằng chứng theo chỉ số ký tự trên ghi chú gốc để chống bịa đặt triệu chứng, vừa mở ngăn kéo phác đồ từ kho 64 đoạn tri thức chuẩn hóa GINA, GOLD, ESC và Bộ Y tế Việt Nam."*

* **Phụ đề nhấn mạnh:**
  * `[Evidence Grounding]`: Khớp chính xác vị trí ký tự gốc | Reject 100% nhận định giả mạo (50/50 probes).
  * `[Guideline KB]`: 64 đoạn JSON phác đồ (70 vector chỉ mục trong Qdrant v1.20.0).

---

### PHÂN CẢNH 3: MÔ PHỎNG THIẾU PHƯƠNG THỨC (RQ4) & CA BẤT ĐỊNH (`2:00 – 3:00`)

* **Thao tác giao diện (UI Actions):**
  * `2:00 – 2:30`: Quay lại `PatientDataForm.tsx`, bật công tắc **RQ4 Missing-Modality Toggle** ("Tắt phương thức văn bản / chỉ giữ sinh hiệu" hoặc ngược lại), nhấn chạy lại hội chẩn để thấy trực tiếp xác suất dự đoán thay đổi rõ rệt và trạng thái thiếu phương thức được ghi nhận trong luồng đối chứng (`[TODO-TV1/TV2: Nêu độ lệch dự đoán / Macro-F1 thực nghiệm RQ4 khi khuyết văn bản]`).
  * `2:30 – 3:00`: Nạp một ca bệnh có triệu chứng chồng lấp hoặc dữ liệu nghèo nàn làm xác suất Top-1 hạ xuống dưới **$55\%$** (`confidence < 0.55`), quay cận cảnh hộp **Cảnh báo Bất định Lâm sàng** màu hổ phách trên `DiagnosticCard.tsx` khuyến cáo bác sĩ hội chẩn chuyên khoa bổ sung thay vì tin cậy tự động.

* **Lời thuyết minh (Voiceover):**
  > *"Để minh họa trực tiếp câu hỏi nghiên cứu RQ4 về độ bền khi thiếu phương thức lâm sàng, giao diện tích hợp công tắc giả lập thiếu văn bản hoặc thiếu sinh hiệu. Khi tắt phần ghi chú bệnh án, bác sĩ quan sát ngay mức dịch chuyển phân phối xác suất của mô hình (`[TODO-TV1/TV2: Nêu mức suy giảm định lượng]`). Đặc biệt, với những ca khó mà xác suất Top-1 xuống dưới ngưỡng an toàn 55%, thẻ chẩn đoán tự động kích hoạt cảnh báo bất định lâm sàng, nhắc bác sĩ không dựa vào gợi ý AI một cách máy móc."*

* **Phụ đề nhấn mạnh:**
  * `[RQ4 Live Toggle]`: Bỏ phương thức văn bản $\rightarrow$ Quan sát biến thiên xác suất trực tiếp.
  * `[Uncertainty Guardrail]`: Top-1 $< 55\%$ $\rightarrow$ Hiển thị cảnh báo bất định bắt buộc.

---

### PHÂN CẢNH 4: TRANG ĐÁNH GIÁ (`/evaluation`) — CI ĐA SEED, RQ2, DCA & RAG/LATENCY (`3:00 – 4:00`)

* **Thao tác giao diện (UI Actions):**
  * `3:00 – 3:20`: Chuyển sang `/evaluation`. Ở Tab 1, lướt qua bảng đối chứng đa seed kèm khoảng tin cậy 95% (95% CI) của **RQ1** (`[TODO-TV1/TV2: Điền AUROC & Macro-F1 đa seed ± std / 95% CI]`) và phân rã đóng góp văn bản **RQ2** (`[TODO-TV1/TV2: Điền kết quả nguyên văn bản vs che nhãn/từ khóa]`).
  * `3:20 – 3:40`: Chuyển sang Tab 2 (**DCA & PROBAST**), kéo thanh trượt ngưỡng quyết định can thiệp trong dải lâm sàng $p_t \in [0,10; 0,45]$ trên `DCACurveChart.tsx` (`[TODO-TV1/TV2: Điền Net Benefit & ca phát hiện đúng thêm / 100 BN tại p_t = 0,20]`).
  * `3:40 – 4:00`: Chuyển sang **Tab 3 (Phase 3 Research Hardening — Registry)** tải trực tiếp từ `/api/v1/evaluation/registry`, trình chiếu số liệu **đo thực tế** của Thành viên 3:
    * **RQ5 RAG (60 truy vấn, $\kappa = 0,9725$):** `bm25_only` (`R@1 = 0,9500`, `MRR = 0,9750`), `dense_only` 768-D fallback ngoại tuyến (`R@1 = 0,7500`), `hybrid_rrf` (`R@1 = 0,8667`, `R@5 = 1,0000`, `MRR = 0,9067`); Kiểm định chống ảo giác 50 ca: neo đúng `100/100` nhận định thật, chặn `50/50` nhận định giả mạo.
    * **Độ trễ CPU thực tế (200 lượt gọi ấm):** `/api/v1/agent/explain` đạt $p_{50} = 9,15\text{ ms}$, $p_{95} = 11,46\text{ ms}$ (HTTP 200); `/api/v1/predict/multimodal` trả HTTP 503 an toàn trong $p_{95} = 102,52\text{ ms}$ khi thiếu bộ nhớ đệm `Bio_ClinicalBERT` ngoại tuyến.

* **Lời thuyết minh (Voiceover):**
  > *"Trên trang Đánh giá hợp nhất lấy dữ liệu từ Registry chuẩn hóa, hội đồng có thể kiểm tra kết quả đa seed kèm khoảng tin cậy cho RQ1, phân tích đóng góp văn bản ở RQ2 (`[TODO-TV1/TV2]`), và đường cong lợi ích ròng DCA giới hạn trên dải ngưỡng 10 đến 45 phần trăm. Đặc biệt ở thẻ Phase 3, các phép đo hệ thống thực tế ghi nhận trên 60 truy vấn gán nhãn kép với độ đồng thuận kappa 0,9725 cho thấy hệ thống RAG đạt Recall@5 bằng 1,0, chặn đứng 50 trên 50 nhận định giả mạo, và API giải trình đa tác tử vận hành trên CPU chỉ mất 9,15 mili-giây ở mức trung vị và 11,46 mili-giây ở phân vị 95."*

* **Phụ đề nhấn mạnh:**
  * `[RQ5 RAG Thực nghiệm]`: 60 queries ($\kappa=0,9725$) | `hybrid_rrf` R@5=1,00 | Grounding 100/100 thật, 50/50 chặn ảo.
  * `[CPU Latency]`: `/agent/explain` $p_{50} = 9,15\text{ ms}$, $p_{95} = 11,46\text{ ms}$.

---

### PHÂN CẢNH 5: GIỚI HẠN TRUNG THỰC & HƯỚNG PHÁT TRIỂN (`4:00 – 4:30`)

* **Hình ảnh hiển thị (Visuals):**
  * `4:00 – 4:15`: Hiển thị bảng tổng hợp kiểm toán 4 miền **PROBAST** (*Low Risk*) đặt cạnh thẻ **Giới hạn Trung thực**.
  * `4:15 – 4:30`: Màn hình kết thúc nêu 3 hướng phát triển: ngoại kiểm trên **MIMIC-IV**, khảo sát đánh giá hữu dụng của bác sĩ lâm sàng, và tích hợp mô hình ngôn ngữ cục bộ có ràng buộc qua cổng `EvidenceGrounder`.

* **Lời thuyết minh (Voiceover):**
  > *"Cuối cùng, nhóm nhìn nhận thẳng thắn ba giới hạn hiện tại: bộ dữ liệu còn mang tính tổng hợp chưa qua ngoại kiểm bệnh viện thật, mô hình mới dừng ở phân loại đơn nhãn 4 bệnh, và ở chế độ ngoại tuyến không có trọng số all-mpnet-base-v2 hay Bio_ClinicalBERT cục bộ, hệ thống chủ động lùi về dense băm 768 chiều hoặc trả HTTP 503 thay vì giả lập kết quả. Hướng đi tiếp theo của nhóm là thẩm định ngoại kiểm trên MIMIC-IV, lấy ý kiến bác sĩ nội trú và tích hợp LLM cục bộ được kiểm soát chặt chẽ bởi cổng chống ảo giác. Em xin trân trọng cảm ơn."*

* **Phụ đề nhấn mạnh:**
  * `[Trung thực Khoa học]`: Chưa ngoại kiểm MIMIC-IV/BV | Safeguard 503 khi thiếu weight thật | Định hướng: MIMIC-IV + Clinician Survey + Constrained LLM.
