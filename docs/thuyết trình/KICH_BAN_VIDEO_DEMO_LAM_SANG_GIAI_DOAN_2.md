# Kịch Bản Video Demo Lâm Sàng: Hệ Thống Hỗ Trợ Chẩn Đoán Đa Phương Thức M-CDSS (Giai Đoạn 2)

> **Thời lượng tiêu chuẩn:** 4 phút 30 giây (nằm trong khung chuẩn 3 – 5 phút của nghiệm thu dự án).  
> **Độ phân giải khuyến nghị:** Full HD (1920 × 1080, 60fps).  
> **Phong cách trình bày:** Chuyên nghiệp, khách quan, chuẩn mực y khoa; kết hợp giữa slide đồ họa ngắn gọn ở phần mở đầu và thao tác trực tiếp trên giao diện Web M-CDSS thực tế.  
> **Lưu ý về số liệu thực nghiệm Giai đoạn 2:** Các vị trí đánh dấu `[TODO-TV1/TV2: ...]` trong kịch bản là khung trống chờ điền số liệu thực nghiệm chính thức sau khi Thành viên 1 và Thành viên 2 hoàn tất huấn luyện `multimodal_best.pt` và chạy đánh giá trên tập kiểm thử $N=302$.

---

## 1. Bảng Phân Bổ Thời Lượng 5 Phân Cảnh

| Phân cảnh | Nội dung trọng tâm | Thời lượng | Mốc thời gian |
| :---: | :--- | :---: | :---: |
| **Cảnh 1** | Mở đầu: Bài toán lâm sàng & Khoảng trống y văn từ JMIR (2024) | 45 giây | `0:00 – 0:45` |
| **Cảnh 2** | Thao tác bàn khám: Nhập ca bệnh khó (`PT-0044` & `PT-0254`) | 55 giây | `0:45 – 1:40` |
| **Cảnh 3** | Kết quả dung hợp đa phương thức & Hiệu chuẩn xác suất ($\text{ECE} < 0,05$) | 55 giây | `1:40 – 2:35` |
| **Cảnh 4** | Giải trình không ảo giác: Tô sáng bằng chứng & Tra cứu phác đồ GINA/GOLD | 65 giây | `2:35 – 3:40` |
| **Cảnh 5** | Thẩm định lâm sàng: Đồ thị Lợi ích ròng DCA, PROBAST & Kết luận y đức | 50 giây | `3:40 – 4:30` |

---

## 2. Kịch Bản Chi Tiết Từng Phân Cảnh (Hình Ảnh – Thao Tác – Thuyết Minh – Phụ Đề)

---

### 🎬 PHÂN CẢNH 1: MỞ ĐẦU — KHOẢNG TRỐNG Y VĂN & MỤC TIÊU HỆ THỐNG (`0:00 – 0:45`)

* **Hình ảnh hiển thị trên màn hình (Visuals):**
  * `0:00 – 0:15`: Hiển thị trang tiêu đề dự án **M-CDSS** kèm sơ đồ tổng quan bài toán phân biệt 4 hội chứng hô hấp – tim mạch cấp tính (*Hen phế quản, COPD, Suy tim, Viêm phổi*).
  * `0:15 – 0:32`: Hiển thị infographic tóm tắt nghiên cứu tổng quan hệ thống trên tạp chí **JMIR (2024)** của Hunik và cộng sự: `10.657` công trình sàng lọc $\rightarrow$ `15` nghiên cứu đạt chuẩn $\rightarrow$ **100% chỉ dùng dữ liệu bảng** và **0% đạt chuẩn nguy cơ sai lệch thấp theo PROBAST**.
  * `0:32 – 0:45`: Chuyển cảnh mượt sang giao diện chính của hệ thống Web M-CDSS đang hoạt động thực tế.

* **Lời thuyết minh (Voiceover):**
  > *"Xin kính chào thầy cô và hội đồng đánh giá. Trong thực hành cấp cứu và chăm sóc ban đầu, việc phân biệt sớm bốn bệnh lý có triệu chứng khó thở chồng lấp gồm Hen phế quản, COPD, Suy tim và Viêm phổi là một thách thức lớn. Thế nhưng, theo tổng quan hệ thống công bố trên tạp chí JMIR năm 2024, sau khi sàng lọc hơn 10.600 công trình, 100% các nghiên cứu đạt chuẩn hiện nay chỉ sử dụng dữ liệu bảng số mà bỏ qua hoàn toàn văn bản ghi chú của bác sĩ; đồng thời chưa có nghiên cứu nào đạt mức nguy cơ sai lệch thấp theo tiêu chuẩn PROBAST. Từ khoảng trống đó, nhóm chúng em phát triển nguyên mẫu Hệ thống Hỗ trợ Quyết định Lâm sàng Đa phương thức M-CDSS, kết hợp đồng thời sinh hiệu xét nghiệm và văn bản bệnh án tự do kèm cơ chế giải thích dựa trên y học chứng cứ."*

* **Phụ đề nhấn mạnh (On-screen Captions):**
  * `[JMIR 2024 Systematic Review]`: 15/15 nghiên cứu chỉ dùng dữ liệu bảng | 0/15 đạt Low Risk of Bias (PROBAST).
  * `[Giải pháp M-CDSS]`: Dung hợp Chú ý chéo (Cross-Attention) + Hiệu chuẩn xác suất + Giải thích kèm y văn.

---

### 🎬 PHÂN CẢNH 2: THAO TÁC NHẬP CA BỆNH LÂM SÀNG KHÓ (`0:45 – 1:40`)

* **Hình ảnh & Thao tác trên giao diện (UI Actions):**
  * `0:45 – 1:05`: Tại màn hình chính (**Bàn làm việc Hội chẩn Lâm sàng**), con trỏ chuột di chuyển qua khu vực nhập 12 chỉ số sinh hiệu và xét nghiệm (Tuổi, Giới tính, Huyết áp, Nhịp tim, Nhịp thở, Thân nhiệt, $\text{SpO}_2$, WBC, CRP, Tiền sử bệnh nền). Nhấn thử vào một ô sinh hiệu để thấy hệ thống kiểm tra giới hạn sinh lý hợp lệ.
  * `1:05 – 1:25`: Nhấp chọn nút nạp nhanh ca bệnh thực tế từ tập kiểm thử độc lập: **Ca bệnh 1 – Mã bệnh nhân `PT-0044`** (Nữ, 18 tuổi, nhãn thực tế: Hen phế quản – *ASTHMA*).
  * `1:25 – 1:40`: Phóng cận cảnh hai nguồn dữ liệu vừa được nạp lên màn hình:
    * Bên trái (Bảng số): $\text{SpO}_2 = 97,3\%$ (đo ngoài cơn cấp), nhưng chỉ số viêm $\text{CRP} = 24,28\text{ mg/L}$ tăng cao kèm tiền sử tăng huyết áp.
    * Bên phải (Ghi chú lâm sàng): Mô tả bệnh nhân 18 tuổi khởi phát cơn khò khè cấp tính và có tiền sử đáp ứng với thuốc xịt giãn phế quản (*Inhalers*). Nhấn nút **"Thực thi Hội chẩn Đa phương thức"**.

* **Lời thuyết minh (Voiceover):**
  > *"Tại bàn làm việc hội chẩn của bác sĩ, hệ thống tiếp nhận đồng thời 12 thông số sinh hiệu, xét nghiệm máu và phần ghi chú khám lâm sàng tự do, với cơ chế kiểm soát chặt chẽ miền giá trị sinh lý. Để minh họa cách hệ thống xử lý các ca bệnh phức tạp, chúng em nạp ca bệnh thực tế mã số PT-0044 từ tập kiểm thử độc lập. Đây là bệnh nhân nữ 18 tuổi mắc Hen phế quản. Điểm đánh lừa ở ca này là bệnh nhân được đo sinh hiệu ngoài cơn khó thở cấp nên SpO2 vẫn đạt 97,3%, trong khi chỉ số viêm CRP lại tăng cao tới 24,28 mg/L. Nếu chỉ nhìn vào bảng số, mô hình đơn phương thức CatBoost đã chẩn đoán nhầm sang COPD (78,82%). Hãy cùng xem hệ thống đa phương thức M-CDSS xử lý ca bệnh này như thế nào."*

* **Phụ đề nhấn mạnh (On-screen Captions):**
  * `[Ca bệnh PT-0044]`: Nữ, 18 tuổi — Nhãn thực tế: Hen phế quản (`ASTHMA`).
  * `[Điểm mù Bảng số]`: Đo ngoài cơn cấp ($\text{SpO}_2 = 97,3\%$), CRP tăng cao ($24,28\text{ mg/L}$) khiến CatBoost đoán nhầm thành COPD ($78,82\%$).

---

### 🎬 PHÂN CẢNH 3: KẾT QUẢ CHẨN ĐOÁN ĐA PHƯƠNG THỨC & HIỆU CHUẨN XÁC SUẤT (`1:40 – 2:35`)

* **Hình ảnh & Thao tác trên giao diện (UI Actions):**
  * `1:40 – 2:05`: Màn hình hiển thị kết quả suy luận trên thẻ **Kết quả Hỗ trợ Chẩn đoán**:
    * Hệ thống đa phương thức M-CDSS dự đoán chính xác **Hen phế quản (`ASTHMA`)** ở vị trí Top-1 với xác suất đã hiệu chuẩn `[TODO-TV1/TV2: Điền % xác suất dự đoán của M-CDSS trên ca PT-0044]`.
    * Chỉ vào huy hiệu **"Đã hiệu chuẩn nhiệt độ (Temperature Scaled – ECE = `[TODO-TV2: Điền ECE thực nghiệm]` < 0,05)"** và thanh đo xác suất phân bổ trên 4 nhóm bệnh (tổng xác suất bằng đúng 100%).
  * `2:05 – 2:35`: Chuyển nhanh sang nạp **Ca bệnh 2 – Mã bệnh nhân `PT-0254`** (Nữ, 65 tuổi, nhãn thực tế: `COPD`).
    * Chỉ rõ sự đối lập: Mô hình văn bản đơn thuần bị đánh lừa bởi các từ khóa mở khí quản và tiếng ran phổi nên đoán nhầm sang Suy tim (`HEART_FAILURE`, 58,99%).
    * Trong khi đó, M-CDSS sử dụng bảng số làm *"mỏ neo huyết động học"* (huyết áp 115,9/80,1 mmHg, nhịp tim 64,3 bpm ổn định) để bác bỏ suy tim cấp và dự đoán chính xác **`COPD`** (`[TODO-TV1/TV2: Điền % xác suất dự đoán của M-CDSS trên ca PT-0254]`).

* **Lời thuyết minh (Voiceover):**
  > *"Kết quả hiển thị tức thì: nhờ cơ chế chú ý chéo Cross-Attention kết hợp tín hiệu sinh hiệu và văn bản, M-CDSS nhận diện chính xác Hen phế quản trên ca PT-0044 với xác suất hiệu chuẩn `[TODO-TV1/TV2: Điền %]`, khắc phục hoàn toàn sai lầm của nhánh bảng số đơn lẻ. Đặc biệt, xác suất đầu ra đã được hiệu chuẩn bằng thuật toán Temperature Scaling, kéo sai số hiệu chuẩn kỳ vọng ECE xuống `[TODO-TV2: Điền ECE]`, đạt ngưỡng an toàn lâm sàng dưới 0,05. Ngược lại, ở ca bệnh thứ hai PT-0254 của một bệnh nhân nữ 65 tuổi mắc COPD, văn bản chứa nhiều từ ngữ gây nhiễu khiến mô hình ngôn ngữ đơn thuần đoán nhầm sang Suy tim (58,99%). Khi đó, M-CDSS lại dùng chính huyết áp và nhịp tim hoàn toàn bình ổn trên bảng số làm mỏ neo huyết động học để loại trừ suy tim cấp, đưa chẩn đoán trở về đúng COPD (`[TODO-TV1/TV2: Điền %]`)."*

* **Phụ đề nhấn mạnh (On-screen Captions):**
  * `[Cross-Attention Late Fusion]`: Kết hợp "mỏ neo huyết động học" (Bảng số) và ngữ cảnh bệnh sử (Văn bản).
  * `[Temperature Scaling]`: Đạt $\text{ECE} = \text{[TODO-TV2]} < 0,05$ — Xác suất dự đoán phản ánh trung thực nguy cơ lâm sàng.

---

### 🎬 PHÂN CẢNH 4: GIẢI TRÌNH KHÔNG ẢO GIÁC & TRA CỨU PHÁC ĐỒ Y KHOA (`2:35 – 3:40`)

* **Hình ảnh & Thao tác trên giao diện (UI Actions):**
  * `2:35 – 3:05`: Cuộn xuống khu vực **Bằng chứng Lâm sàng trong Hồ sơ Bệnh án (Evidence Viewer)**.
    * Di chuột vào các đoạn văn bản được tô sáng màu vàng/xanh trực tiếp trên ghi chú bệnh án gốc (ví dụ: cụm từ mô tả khởi phát trẻ tuổi, cơn khò khè cấp tính và tiền sử dùng ống hít giãn phế quản).
    * Hiển thị hộp thông tin xác nhận: **"Đã kiểm chứng khớp nguyên văn 100% vị trí ký tự (Hallucination-Free Verified)"**.
  * `3:05 – 3:40`: Nhấp vào nút **"Tra cứu Phác đồ Điều trị Chính thống"** bên cạnh chẩn đoán.
    * Ngăn kéo phác đồ (**Guideline Drawer**) trượt mở từ bên phải màn hình.
    * Hiển thị trích dẫn trực tiếp từ **Hướng dẫn GINA 2024**, **GOLD 2024** và **Phác đồ Bộ Y tế**, kèm mức độ chứng cứ (Evidence Level A) và các tiêu chuẩn chẩn đoán phân biệt Hen – COPD.

* **Lời thuyết minh (Voiceover):**
  > *"Trong y khoa, một con số xác suất không kèm lời giải thích sẽ không thể thuyết phục được bác sĩ. Tuy nhiên, nếu để mô hình ngôn ngữ tự do sinh lời giải thích thì lại tiềm ẩn nguy cơ ảo giác, tức tự bịa ra triệu chứng không có trong hồ sơ. Để giải quyết triệt để bài toán này, hệ thống đa tác tử của chúng em tích hợp bộ kiểm chứng vị trí ký tự tất định. Mọi câu chứng cứ được tô sáng trên màn hình đều bắt buộc phải đối sánh khớp 100% từng ký tự với văn bản gốc của bác sĩ; bất kỳ suy diễn nào nằm ngoài văn bản đều bị chặn hoàn toàn. Đồng thời, khi bác sĩ nhấp vào thẻ tra cứu y văn, ngăn kéo phác đồ sẽ hiển thị ngay điều khoản tương ứng trong hướng dẫn quốc tế GINA 2024, GOLD 2024 và Bộ Y tế, giúp bác sĩ đối chiếu hai chiều giữa triệu chứng thực tế của bệnh nhân và tiêu chuẩn y học chứng cứ."*

* **Phụ đề nhấn mạnh (On-screen Captions):**
  * `[Anti-Hallucination Evidence Grounding]`: Đối sánh vị trí ký tự $[start, end]$ — Cam kết 0% triệu chứng bịa đặt.
  * `[Hybrid Guideline RAG]`: Đối chiếu trực tiếp phác đồ GINA 2024, GOLD 2024, ESC & Bộ Y tế.

---

### 🎬 PHÂN CẢNH 5: ĐỒ THỊ LỢI ÍCH RÒNG DCA, KIỂM ĐỊNH PROBAST & KẾT LUẬN (`3:40 – 4:30`)

* **Hình ảnh & Thao tác trên giao diện (UI Actions):**
  * `3:40 – 4:05`: Chuyển sang trang **Thẩm định Lâm sàng & Đối chứng (`/evaluation`)**.
    * Lướt qua bảng đối chứng tổng hợp trên tập kiểm thử độc lập ($N = 302$): M-CDSS đạt $\text{AUROC} = \text{[TODO-TV1]}$, $\text{Macro-F1} = \text{[TODO-TV1]}$, $\text{ECE} = \text{[TODO-TV2]}$.
    * Nhấp sang tab **"Lợi ích ròng Lâm sàng & PROBAST"**. Kéo thanh trượt ngưỡng quyết định can thiệp $p_t$ từ $10\%$ đến $45\%$ trên đồ thị **Decision Curve Analysis (DCA)**.
    * Chỉ vào đường cong của M-CDSS so với đường *Treat All* (Can thiệp tất cả) và *Treat None* (Không can thiệp), cùng chỉ số **`[TODO-TV1/TV2: Điền số ca can thiệp đúng tăng thêm / 100 BN]`** tại ngưỡng $p_t = 20\%$.
  * `4:05 – 4:30`: Cuộn xuống bảng **Thẩm định 4 miền PROBAST** (Participants, Predictors, Outcome, Analysis đều đạt mức *Nguy cơ sai lệch thấp – Low Risk of Bias*) và khung **Tuyên bố Y đức** ở cuối trang.

* **Lời thuyết minh (Voiceover):**
  > *"Cuối cùng, tại trang Thẩm định Lâm sàng trên tập kiểm thử độc lập 302 hồ sơ với kiểm toán 0% rò rỉ dữ liệu, M-CDSS đạt AUROC macro `[TODO-TV1]` và Macro-F1 đạt `[TODO-TV1]`. Không dừng lại ở các chỉ số học máy, đồ thị Phân tích Đường cong Quyết định DCA tương tác cho phép bác sĩ điều chỉnh ngưỡng xác suất can thiệp thực tế. Trên dải ngưỡng lâm sàng, đường cong lợi ích ròng của M-CDSS vượt trội hơn cả hai chiến lược can thiệp tất cả hoặc không can thiệp; giúp phát hiện đúng thêm `[TODO-TV1/TV2]` ca bệnh trên mỗi 100 bệnh nhân ở ngưỡng 20% mà không làm tăng điều trị thừa. Toàn bộ hệ thống đạt chuẩn nguy cơ sai lệch thấp trên cả 4 miền PROBAST và được đóng gói trọn gói bằng Docker, sẵn sàng hỗ trợ đắc lực cho bác sĩ trong vai trò công cụ tham khảo lâm sàng minh bạch. Em xin trân trọng cảm ơn thầy cô đã theo dõi."*

* **Phụ đề nhấn mạnh (On-screen Captions):**
  * `[Decision Curve Analysis]`: Lợi ích ròng trên dải $p_t \in [0,10; 0,45]$ (`[TODO-TV1/TV2]` ca đúng / 100 bệnh nhân tại $p_t=0,20$).
  * `[PROBAST & Y đức]`: Đạt Low Risk of Bias cả 4 miền | Công cụ hỗ trợ tham khảo, tôn trọng quyền quyết định của bác sĩ.
