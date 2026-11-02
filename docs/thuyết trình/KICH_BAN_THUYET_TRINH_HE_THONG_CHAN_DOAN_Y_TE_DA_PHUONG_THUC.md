# Kịch bản thuyết trình: Hệ thống chẩn đoán y tế đa phương thức

> Kịch bản được viết theo nội dung 18 slide trong file `slide-nhóm-6 (1).pdf`.
>
> Thời lượng gợi ý: **14–16 phút**, chưa tính phần hỏi đáp.
>
> Cách sử dụng: không cần học thuộc từng chữ. Hãy nhớ câu mở đầu, ý chính in đậm và câu chuyển ở cuối mỗi slide.

---

## Phân bổ thời gian

| Slide | Nội dung | Thời lượng gợi ý |
|---:|---|---:|
| 1–2 | Giới thiệu và bố cục | 1 phút |
| 3–4 | Khoảng trống nghiên cứu | 1 phút 30 giây |
| 5–6 | Mục tiêu và phạm vi giai đoạn 1 | 1 phút 20 giây |
| 7–8 | Dữ liệu và thiết kế thực nghiệm | 2 phút |
| 9 | Kết quả tổng hợp | 2 phút |
| 10–12 | Hai ca bệnh và kết luận | 3 phút |
| 13–14 | Kiến trúc đề xuất và Agentic RAG | 2 phút 30 giây |
| 15–16 | Đánh giá mở rộng và giới hạn | 1 phút 30 giây |
| 17–18 | Tài liệu tham khảo và kết thúc | 30–45 giây |

---

## Slide 1 – Trang tiêu đề

**Thời lượng:** 35–45 giây

### Lời nói gợi ý

> Em xin kính chào thầy cô và các bạn. Em xin đại diện Nhóm 6 trình bày đề tài **“Hệ thống chẩn đoán y tế đa phương thức”**.
>
> Nhóm em gồm ba thành viên: Nguyễn Nho Dương, Lê Tuấn Cảnh và Nguyễn Văn Cường.
>
> Ý tưởng cốt lõi của đề tài là kết hợp hai nguồn thông tin thường xuất hiện đồng thời trong hồ sơ sức khỏe điện tử: thứ nhất là **dữ liệu bảng**, chẳng hạn sinh hiệu và kết quả xét nghiệm; thứ hai là **ghi chú lâm sàng dạng văn bản tự do**. Nhóm muốn kiểm tra xem hai nguồn này bổ sung cho nhau như thế nào trong bài toán hỗ trợ chẩn đoán.

### Câu chuyển

> Trước tiên, em xin trình bày ngắn gọn bố cục của bài báo cáo.

---

## Slide 2 – Tóm tắt nội dung

**Thời lượng:** 30–40 giây

### Lời nói gợi ý

> Bài trình bày gồm năm phần chính.
>
> Đầu tiên là **khoảng trống nghiên cứu** trong các mô hình AI y tế hiện nay. Tiếp theo là **mục tiêu đề tài** và **nguồn dữ liệu**. Sau đó, nhóm trình bày thiết kế thực nghiệm với ba mô hình baseline đơn phương thức, kết quả định lượng và hai ca bệnh điển hình. Cuối cùng, từ các kết quả này, nhóm đề xuất định hướng **dung hợp đa phương thức trong giai đoạn 2**.

### Câu chuyển

> Vậy tại sao cần một hệ thống đa phương thức? Câu trả lời bắt đầu từ khoảng trống của các nghiên cứu hiện có.

---

## Slide 3 – Khoảng trống nghiên cứu trong AI y tế

**Thời lượng:** 55–70 giây

### Lời nói gợi ý

> Nhóm tham khảo nghiên cứu tổng quan hệ thống của Hunik và cộng sự về các mô hình dự đoán chẩn đoán từ hồ sơ sức khỏe điện tử, công bố năm 2024.
>
> Điểm đáng chú ý là từ **10.657 công trình** được sàng lọc, chỉ có **15 nghiên cứu** đáp ứng đầy đủ tiêu chuẩn để đưa vào phân tích tổng quan. Điều đó cho thấy số lượng nghiên cứu rất lớn, nhưng số nghiên cứu có thiết kế phương pháp luận đủ chặt chẽ còn khá hạn chế.
>
> Trong 15 nghiên cứu này, **100% chỉ sử dụng dữ liệu có cấu trúc dạng bảng**, ví dụ mã ICD hoặc chỉ số xét nghiệm. Phần ghi chú tự do của bác sĩ, vốn chứa bệnh sử, triệu chứng, thuốc đang dùng và diễn tiến bệnh, chưa được khai thác bằng mô hình ngôn ngữ lâm sàng.
>
> Ngoài ra, khi đánh giá bằng công cụ PROBAST, 60% nghiên cứu có nguy cơ sai lệch cao, 40% chưa rõ ràng và không có nghiên cứu nào đạt mức nguy cơ sai lệch thấp. Đây là dấu hiệu cho thấy kết quả tốt về mặt kỹ thuật chưa chắc đã đủ tin cậy để ứng dụng lâm sàng.

### Điểm cần nhấn

- `10.657` là số công trình được sàng lọc, không phải số nghiên cứu cuối cùng.
- Chỉ `15` nghiên cứu được đưa vào tổng quan.
- Khoảng trống chính là **bỏ qua văn bản lâm sàng** và **nguy cơ sai lệch cao**.

### Câu chuyển

> Từ các con số này, nhóm rút ra một vấn đề rất cụ thể.

---

## Slide 4 – Khoảng trống cốt lõi

**Thời lượng:** 30–40 giây

### Lời nói gợi ý

> Khoảng trống cốt lõi là phần lớn giải pháp hiện tại đang bỏ quên một nguồn tri thức rất giàu thông tin: **ghi chú lâm sàng tự do**.
>
> Hai bệnh nhân có thể có sinh hiệu tương đối giống nhau tại thời điểm đo, nhưng bệnh sử, triệu chứng kéo dài, thuốc đã dùng hoặc mô tả của bác sĩ lại rất khác. Nếu chỉ nhìn vào bảng số, mô hình có thể bỏ lỡ phần ngữ cảnh này.
>
> Tuy nhiên, văn bản cũng không hoàn hảo vì có thể chứa từ ngữ gây nhiễu. Do đó, câu hỏi của nhóm không phải là chọn bảng số hay văn bản, mà là xem hai phương thức có thể bù trừ cho nhau như thế nào.

### Câu chuyển

> Từ đó, nhóm xác định mục tiêu nghiên cứu như sau.

---

## Slide 5 – Mục tiêu tổng quát

**Thời lượng:** 35–45 giây

### Lời nói gợi ý

> Mục tiêu tổng quát của đề tài là nghiên cứu, phát triển và đánh giá thực nghiệm một nguyên mẫu hệ thống hỗ trợ quyết định lâm sàng đa phương thức.
>
> Hệ thống sử dụng đồng thời **dữ liệu bảng số**, gồm sinh hiệu và xét nghiệm, với **văn bản bệnh án tự do**. Đầu ra hướng tới là dự đoán nhóm bệnh và cung cấp thông tin hỗ trợ bác sĩ tham khảo.
>
> Nhóm nhấn mạnh đây là hệ thống **hỗ trợ quyết định**, không phải hệ thống thay thế bác sĩ và cũng không tự động đưa ra quyết định điều trị.

### Câu chuyển

> Để đi đến mục tiêu đó, nghiên cứu được chia thành các giai đoạn; trong bài này, nhóm tập trung vào giai đoạn 1.

---

## Slide 6 – Mục tiêu giai đoạn 1

**Thời lượng:** 45–55 giây

### Lời nói gợi ý

> Giai đoạn 1 có ba nhiệm vụ chính.
>
> Thứ nhất, nhóm xây dựng kho dữ liệu gồm **2.000 hồ sơ đã chuẩn hóa**.
>
> Thứ hai, nhóm thực nghiệm đối chứng ba mô hình baseline đơn phương thức. Với dữ liệu bảng, nhóm sử dụng CatBoost hoặc XGBoost và FT-Transformer. Với văn bản, nhóm sử dụng Bio_ClinicalBERT.
>
> Thứ ba, nhóm không chỉ so sánh chỉ số tổng hợp mà còn phân tích các ca dự đoán sai biệt giữa các mô hình. Mục tiêu là tìm bằng chứng thực nghiệm cho câu hỏi: **khi nào bảng số tốt hơn, khi nào văn bản tốt hơn, và vì sao cần dung hợp?**

### Câu chuyển

> Tiếp theo là nguồn gốc và cấu trúc của bộ dữ liệu nghiên cứu.

---

## Slide 7 – Nguồn gốc và cấu trúc dữ liệu

**Thời lượng:** 55–70 giây

### Lời nói gợi ý

> Bộ dữ liệu được xây dựng từ hai nguồn mở.
>
> Nguồn thứ nhất là **Synthea EHR**, cung cấp dữ liệu có cấu trúc như sinh hiệu và xét nghiệm theo định dạng hồ sơ y tế. Nguồn thứ hai là **MTSamples**, cung cấp các mẫu ghi chú lâm sàng của bác sĩ.
>
> Sau bước tổng hợp và chuẩn hóa, bộ dữ liệu gồm **2.000 hồ sơ**, được phân bố cân bằng cho bốn nhóm bệnh: hen phế quản, COPD hay bệnh phổi tắc nghẽn mạn tính, suy tim và viêm phổi.
>
> Việc cân bằng bốn lớp giúp giảm hiện tượng mô hình thiên lệch về lớp có nhiều mẫu. Tuy nhiên, do dữ liệu đến từ nguồn mở và được ghép, chuẩn hóa phục vụ nghiên cứu, kết quả hiện tại chỉ nên được hiểu là đánh giá trên **nguyên mẫu học thuật**, chưa đại diện cho dữ liệu bệnh viện thực tế.

### Điểm cần nhấn

- Hai nguồn dữ liệu đóng hai vai trò khác nhau.
- Tổng cộng 2.000 hồ sơ, bốn nhóm bệnh cân bằng.
- Không mô tả dữ liệu là hồ sơ bệnh nhân thực tế được thu trực tiếp từ một bệnh viện.

### Câu chuyển

> Trên bộ dữ liệu này, nhóm thiết kế ba baseline để đo riêng năng lực của từng phương thức.

---

## Slide 8 – Thiết kế thực nghiệm và ba mô hình baseline

**Thời lượng:** 60–75 giây

### Lời nói gợi ý

> Với dữ liệu bảng, nhóm sử dụng hai hướng tiếp cận.
>
> **CatBoost hoặc XGBoost** đại diện cho nhóm mô hình cây tăng cường, vốn thường hoạt động tốt trên dữ liệu bảng. **FT-Transformer** đại diện cho hướng học sâu sử dụng cơ chế attention để biểu diễn các trường dữ liệu bảng.
>
> Với ghi chú lâm sàng, nhóm dùng **Bio_ClinicalBERT**, là mô hình ngôn ngữ đã được huấn luyện trên dữ liệu y sinh và lâm sàng.
>
> Các mô hình được đánh giá đồng thời bằng sáu nhóm chỉ số. AUROC đo khả năng xếp hạng và phân biệt các lớp. AUPRC quan tâm nhiều hơn đến chất lượng phát hiện lớp dương tính. Macro-F1 cho mỗi lớp trọng số ngang nhau. Accuracy là tỷ lệ dự đoán đúng. Brier Score và ECE đánh giá chất lượng và độ hiệu chỉnh của xác suất dự đoán.
>
> Với AUROC, AUPRC, Macro-F1 và Accuracy, giá trị càng cao càng tốt. Ngược lại, Brier và ECE càng thấp càng tốt.

### Câu chuyển

> Sau đây là kết quả tổng hợp trên tập kiểm thử độc lập gồm 302 mẫu.

---

## Slide 9 – Kết quả thực nghiệm tổng hợp

**Thời lượng:** 1 phút 45 giây–2 phút 15 giây

### Lời nói gợi ý

> Bảng này là kết quả quan trọng nhất của giai đoạn 1. Đánh giá được thực hiện trên tập kiểm thử độc lập gồm **302 mẫu**.
>
> Trước hết, với CatBoost, mô hình đạt AUROC macro là **0,9223**, AUPRC macro **0,7872**, Macro-F1 **0,6083** và Accuracy **68,54%**. ECE của mô hình là **6,63%**.
>
> FT-Transformer có kết quả thấp hơn: AUROC macro **0,8976**, AUPRC macro **0,7023**, Macro-F1 **0,5789** và Accuracy **65,89%**. Đặc biệt, ECE lên tới **11,52%**, cho thấy xác suất dự đoán có độ lệch hiệu chỉnh lớn hơn và mô hình có nguy cơ quá tự tin.
>
> Bio_ClinicalBERT cho kết quả tốt nhất trên tất cả các chỉ số trong thí nghiệm này: AUROC macro **0,9735**, AUPRC macro **0,9314**, Macro-F1 **0,8421** và Accuracy **85,43%**. Brier Score giảm xuống **0,2329** và ECE còn **3,73%**.
>
> Như vậy, ghi chú lâm sàng mang lại lợi thế rõ rệt trong bộ dữ liệu hiện tại. Nhưng điều quan trọng là **kết quả trung bình tốt nhất không có nghĩa mô hình văn bản luôn đúng trên từng bệnh nhân**. Hai ca bệnh tiếp theo sẽ cho thấy giới hạn của từng phương thức.

### Cách trình bày bảng

Không cần đọc toàn bộ 18 con số. Khi nói, hãy chỉ vào:

1. Accuracy: 68,54% – 65,89% – 85,43%.
2. Macro-F1: 0,6083 – 0,5789 – 0,8421.
3. ECE: 6,63% – 11,52% – 3,73%.

Sau đó kết luận bằng AUROC/AUPRC và Brier nếu còn thời gian.

### Lưu ý diễn đạt khoa học

Thay vì nói “ECE 3,73% đáp ứng chuẩn y tế dưới 5%”, nên nói:

> ECE 3,73% thấp hơn ngưỡng mục tiêu 5% mà nhóm sử dụng trong nghiên cứu, cho thấy độ hiệu chỉnh tốt hơn hai baseline còn lại.

Không nên khẳng định `<5%` là một chuẩn y tế phổ quát nếu chưa có tài liệu quy định cụ thể.

### Câu chuyển

> Để hiểu vì sao các mô hình tạo ra kết quả khác nhau, nhóm phân tích hai ca bệnh cụ thể.

---

## Slide 10 – Ca bệnh 1: Điểm yếu của dữ liệu bảng

**Thời lượng:** 1 phút 15 giây–1 phút 30 giây

### Lời nói gợi ý

> Ca thứ nhất là bệnh nhân mã PT-0044, có nhãn thực tế là **hen phế quản**.
>
> Nếu chỉ nhìn vào bảng số tại thời điểm đo, phần lớn chỉ số tương đối ổn định: nhịp tim 70,6; nhịp thở 12,8; SpO2 97,3%; bạch cầu 4,78. Điểm nổi bật là CRP tăng lên 24,28 miligam trên lít. Những số liệu này chưa thể hiện rõ kiểu bệnh hen, đặc biệt nếu bệnh nhân đang ở giai đoạn triệu chứng không điển hình hoặc tương đối ổn định.
>
> Vì vậy, hai mô hình bảng đều dự đoán nhầm thành COPD: CatBoost với xác suất **78,82%** và FT-Transformer với **74,10%**.
>
> Ngược lại, ghi chú lâm sàng chứa các thông tin như ho, khó thở, mệt mỏi và đặc biệt là việc sử dụng thuốc hít. Bio_ClinicalBERT khai thác được ngữ cảnh này và dự đoán đúng hen phế quản với xác suất **85,80%**.
>
> Ca này minh họa điểm mù của bảng số: một lần đo sinh hiệu chỉ là ảnh chụp tại một thời điểm, trong khi văn bản có thể chứa diễn tiến và lịch sử điều trị.

### Câu chuyển

> Tuy nhiên, ở ca thứ hai, ưu thế lại đảo chiều.

---

## Slide 11 – Ca bệnh 2: Điểm yếu của ghi chú văn bản

**Thời lượng:** 1 phút 15 giây–1 phút 30 giây

### Lời nói gợi ý

> Ca thứ hai là bệnh nhân PT-0254, có nhãn thực tế là **COPD**.
>
> Dữ liệu bảng cho thấy bệnh nhân 65 tuổi, SpO2 95,6%, các chỉ số huyết động tương đối ổn định. Hai mô hình bảng đều dự đoán đúng COPD: CatBoost đạt xác suất **75,22%**, còn FT-Transformer đạt **71,30%**.
>
> Trong ghi chú lâm sàng, tên chẩn đoán đã được che để tránh rò rỉ nhãn. Phần văn bản còn lại mô tả một bệnh cảnh khá phức tạp: mở khí quản, từng phụ thuộc máy thở, có ran phổi và sử dụng nhiều loại thuốc. Một số từ ngữ liên quan đến điều trị và bệnh cảnh nặng đã làm mô hình văn bản bị chệch hướng.
>
> Kết quả là Bio_ClinicalBERT dự đoán nhầm thành suy tim với xác suất **58,99%**.
>
> Ca này cho thấy mô hình văn bản có thể bị ảnh hưởng bởi nhiễu ngữ nghĩa, bệnh đồng mắc hoặc những dấu hiệu không đặc hiệu. Trong khi đó, dữ liệu bảng đóng vai trò như một nguồn tín hiệu độc lập giúp giữ chẩn đoán ổn định hơn.

### Câu chuyển

> Hai ca bệnh có kết quả trái ngược, nhưng cùng dẫn đến một kết luận chung.

---

## Slide 12 – Kết luận từ hai case study

**Thời lượng:** 50–65 giây

### Lời nói gợi ý

> Kết luận quan trọng là **không có phương thức đơn lẻ nào chiếm ưu thế tuyệt đối trong mọi tình huống**.
>
> Văn bản lâm sàng mạnh ở khả năng khai thác bệnh sử, thuốc đã dùng và diễn tiến triệu chứng. Tuy nhiên, nó có thể bị nhiễu khi bệnh cảnh phức tạp, khi có nhiều bệnh đồng mắc hoặc khi tên bệnh đã được che.
>
> Dữ liệu bảng ít bị ảnh hưởng bởi từ vựng gây nhiễu và cung cấp các phép đo khách quan. Nhưng nó có điểm mù khi các chỉ số được đo lúc bệnh đang ổn định hoặc khi một lần đo không phản ánh được diễn tiến dài hạn.
>
> Vì vậy, dung hợp không đơn giản là dùng thêm dữ liệu. Mục tiêu là để mỗi phương thức **bù cho điểm yếu của phương thức còn lại**.

### Câu chuyển

> Từ luận cứ đó, nhóm đề xuất kiến trúc dung hợp cho giai đoạn tiếp theo.

---

## Slide 13 – Kiến trúc dung hợp đa phương thức

**Thời lượng:** 1 phút 10 giây–1 phút 30 giây

### Lời nói gợi ý

> Kiến trúc đề xuất gồm ba khối chính.
>
> Khối thứ nhất là **dữ liệu đầu vào**, gồm dữ liệu bảng như sinh hiệu, xét nghiệm và ghi chú lâm sàng dạng tự do.
>
> Khối thứ hai là **hai bộ mã hóa chuyên biệt**. FT-Transformer biến dữ liệu bảng thành biểu diễn số; Bio_ClinicalBERT biến văn bản thành biểu diễn ngữ nghĩa. Việc dùng hai bộ mã hóa riêng giúp mỗi loại dữ liệu được xử lý theo đúng đặc trưng của nó.
>
> Hai biểu diễn sau đó đi vào lớp **Cross-Attention Late Fusion**. “Late fusion” nghĩa là nhóm không ghép dữ liệu thô ngay từ đầu, mà để mỗi nhánh học đặc trưng riêng trước rồi mới dung hợp. Cross-attention cho phép mô hình học xem thông tin nào trong bảng số cần được đối chiếu với thông tin nào trong ghi chú.
>
> Sau lớp dung hợp là Classification Head để dự đoán một trong bốn nhóm bệnh. Cuối cùng, Temperature Scaling được dùng để hiệu chỉnh xác suất, với mục tiêu giảm ECE xuống dưới 5% theo ngưỡng thiết kế của nhóm.

### Cách chỉ vào sơ đồ

Chỉ theo chiều từ trái sang phải:

1. Hai nguồn dữ liệu.
2. Hai bộ mã hóa.
3. Cross-attention late fusion.
4. Classification head.
5. Temperature scaling.

### Câu chuyển

> Bên cạnh dự đoán đúng, một hệ thống y tế còn cần giải thích được căn cứ của dự đoán.

---

## Slide 14 – Giải thích lâm sàng dựa trên y học chứng cứ

**Thời lượng:** 1 phút 15 giây–1 phút 35 giây

### Lời nói gợi ý

> Nhóm đề xuất thêm một tầng giải thích lâm sàng theo hướng Agentic RAG.
>
> Các hướng dẫn chuyên môn như hướng dẫn của Bộ Y tế, GINA cho hen và GOLD cho COPD được lập chỉ mục trong kho vector. Khi cần giải thích, bộ truy hồi ngữ nghĩa tìm các đoạn hướng dẫn liên quan. Diagnostic Agent sử dụng những bằng chứng này cùng thông tin hồ sơ để tạo phần giải thích.
>
> Mỗi khuyến nghị chẩn đoán phân biệt phải đi kèm hai loại căn cứ. Thứ nhất là **căn cứ từ hồ sơ bệnh nhân**, ví dụ một đoạn ghi chú hoặc một chỉ số bất thường cụ thể. Thứ hai là **căn cứ y văn**, gồm tài liệu, mục hoặc số trang tương ứng trong hướng dẫn chính thức.
>
> Thiết kế này nhằm giảm nguy cơ mô hình sinh ra giải thích không có căn cứ, đồng thời giúp bác sĩ kiểm tra lại nguồn thông tin. Tuy nhiên, RAG không thể bảo đảm loại bỏ tuyệt đối hallucination; hệ thống vẫn cần cơ chế kiểm chứng trích dẫn và bác sĩ phải là người đưa ra quyết định cuối cùng.

### Lưu ý diễn đạt khoa học

Slide ghi “loại bỏ hoàn toàn nguy cơ hallucination”. Khi nói nên thay bằng:

> Giảm thiểu và kiểm soát nguy cơ hallucination bằng cách buộc mọi nhận định phải có bằng chứng truy xuất được.

Không nên hứa hẹn loại bỏ hoàn toàn hallucination vì RAG vẫn có thể truy xuất sai nguồn, hiểu sai nguồn hoặc tạo kết luận không được nguồn hỗ trợ đầy đủ.

### Câu chuyển

> Để đánh giá hệ thống theo hướng gần với nhu cầu lâm sàng hơn, nhóm đề xuất bốn lớp đánh giá mở rộng.

---

## Slide 15 – Phương pháp đánh giá lâm sàng mở rộng

**Thời lượng:** 55–70 giây

### Lời nói gợi ý

> Thứ nhất là **Decision Curve Analysis**, hay phân tích đường cong quyết định. Phương pháp này đo lợi ích ròng của mô hình tại các ngưỡng can thiệp khác nhau, giúp trả lời câu hỏi mô hình có mang lại giá trị thực tế hơn so với chiến lược điều trị tất cả hoặc không điều trị ai hay không.
>
> Thứ hai, nhóm sử dụng bootstrap 1.000 lần để xây dựng khoảng tin cậy 95% cho các chỉ số như AUROC, AUPRC và Macro-F1. Nhờ đó, ta đánh giá được độ ổn định thống kê, thay vì chỉ nhìn một con số điểm.
>
> Thứ ba là kiểm định công bằng theo tuổi và giới, tập trung vào độ nhạy và độ đặc hiệu giữa các nhóm.
>
> Cuối cùng, nhóm định hướng báo cáo theo TRIPOD-AI để tăng tính minh bạch, khả năng tái lập và chất lượng công bố.

### Câu chuyển

> Bên cạnh những kết quả ban đầu, nghiên cứu vẫn có các giới hạn cần được trình bày rõ ràng.

---

## Slide 16 – Giới hạn nghiên cứu và tuyên bố y đức

**Thời lượng:** 55–70 giây

### Lời nói gợi ý

> Giới hạn đầu tiên nằm ở đặc điểm dữ liệu. Dữ liệu được tổng hợp và chuẩn hóa từ hai nguồn mở là Synthea và MTSamples, chưa phải dữ liệu được thu thập tiến cứu từ nhiều bệnh viện. Do đó, khả năng khái quát sang môi trường lâm sàng thực tế chưa được xác nhận.
>
> Giới hạn thứ hai là quy mô tập kiểm thử gồm 302 mẫu. Dù bốn nhóm bệnh được phân bổ tương đối cân bằng, cỡ mẫu này vẫn cần được mở rộng để đánh giá trên nhiều phân bố bệnh nhân, cơ sở y tế và nhóm dân số khác nhau.
>
> Về ranh giới sử dụng, đây là nghiên cứu học thuật nhằm phát triển nguyên mẫu hỗ trợ quyết định. Hệ thống không thay thế bác sĩ, không tự động quyết định điều trị và chưa được sử dụng trực tiếp trên bệnh nhân thật. Mọi bước ứng dụng lâm sàng trong tương lai đều cần thẩm định độc lập và phê duyệt của hội đồng đạo đức.

### Câu chuyển

> Các mô hình, phương pháp đánh giá và hướng dẫn chuyên môn trong nghiên cứu được xây dựng dựa trên những tài liệu sau.

---

## Slide 17 – Tài liệu tham khảo

**Thời lượng:** 15–25 giây

### Lời nói gợi ý

> Đây là các tài liệu tham khảo chính của nhóm, gồm nghiên cứu tổng quan của Hunik và cộng sự, các công trình nền tảng về ClinicalBERT, FT-Transformer và CatBoost, hướng dẫn báo cáo TRIPOD-AI, cùng hai hướng dẫn chuyên môn GOLD và GINA.
>
> Nhóm không trình bày chi tiết từng tài liệu tại đây, nhưng toàn bộ nguồn đã được liệt kê để bảo đảm khả năng kiểm tra và đối chiếu.

### Câu chuyển

> Em xin chuyển sang phần kết luận của bài trình bày.

---

## Slide 18 – Kết thúc và mời đặt câu hỏi

**Thời lượng:** 25–35 giây

### Lời nói gợi ý

> Tóm lại, kết quả giai đoạn 1 cho thấy ghi chú lâm sàng mang lại hiệu quả tổng thể cao hơn trên bộ dữ liệu nghiên cứu, nhưng hai ca bệnh cụ thể chứng minh cả văn bản và bảng số đều có điểm mù riêng.
>
> Đây là cơ sở để nhóm phát triển kiến trúc dung hợp đa phương thức, kết hợp với hiệu chỉnh xác suất và giải thích dựa trên y học chứng cứ trong giai đoạn tiếp theo.
>
> Phần trình bày của Nhóm 6 đến đây là kết thúc. Nhóm em xin cảm ơn thầy cô và các bạn đã lắng nghe, và xin tiếp nhận câu hỏi.

---

# Bản ghi nhớ cực ngắn trước khi thuyết trình

Nếu không thể nhớ toàn bộ kịch bản, hãy nhớ chuỗi logic sau:

1. **Khoảng trống:** nghiên cứu hiện tại chủ yếu chỉ dùng dữ liệu bảng, bỏ qua ghi chú lâm sàng.
2. **Mục tiêu:** so sánh từng phương thức và tạo luận cứ cho dung hợp.
3. **Dữ liệu:** 2.000 hồ sơ, bốn nhóm bệnh, hai nguồn Synthea và MTSamples.
4. **Baseline:** CatBoost, FT-Transformer và Bio_ClinicalBERT.
5. **Kết quả:** Bio_ClinicalBERT tốt nhất về tổng thể; Accuracy 85,43%, Macro-F1 0,8421, ECE 3,73%.
6. **Ca 1:** bảng số sai, văn bản đúng vì văn bản có bệnh sử và thuốc.
7. **Ca 2:** văn bản sai, bảng số đúng vì văn bản có nhiễu ngữ nghĩa.
8. **Kết luận:** không phương thức nào luôn thắng; cần dung hợp.
9. **Kiến trúc:** hai bộ mã hóa → cross-attention late fusion → phân loại → hiệu chỉnh xác suất.
10. **An toàn:** giải thích phải có căn cứ hồ sơ và y văn; hệ thống chỉ hỗ trợ bác sĩ.

---

# Các câu hỏi phản biện có thể gặp

## 1. Vì sao chọn bốn bệnh hen, COPD, suy tim và viêm phổi?

**Trả lời gợi ý:**

> Bốn bệnh này có thể cùng biểu hiện bằng các triệu chứng hô hấp như khó thở, ho hoặc giảm oxy, nên có ý nghĩa cho bài toán chẩn đoán phân biệt. Đồng thời, chúng có cả thông tin hữu ích trong dữ liệu bảng và trong ghi chú lâm sàng, phù hợp để đánh giá lợi ích của dung hợp đa phương thức.

## 2. Tại sao Bio_ClinicalBERT tốt hơn nhiều so với mô hình bảng?

**Trả lời gợi ý:**

> Trong bộ dữ liệu hiện tại, ghi chú chứa nhiều thông tin về bệnh sử, triệu chứng và thuốc điều trị, trong khi bảng số chủ yếu phản ánh một thời điểm đo. Vì vậy, văn bản có tín hiệu phân biệt mạnh hơn. Tuy nhiên, kết quả này phụ thuộc vào cách xây dựng bộ dữ liệu và cần được xác nhận trên dữ liệu bệnh viện độc lập.

## 3. Tại sao không dùng luôn Bio_ClinicalBERT mà vẫn cần dung hợp?

**Trả lời gợi ý:**

> Bio_ClinicalBERT tốt nhất về trung bình nhưng không đúng trong mọi ca. Ca PT-0254 cho thấy văn bản có thể bị nhiễu và mô hình dự đoán sai, trong khi hai mô hình bảng đều đúng. Dung hợp nhằm tăng tính ổn định trên từng bệnh nhân, không chỉ tối ưu chỉ số trung bình.

## 4. Dữ liệu từ Synthea và MTSamples được ghép như thế nào?

**Trả lời gợi ý an toàn:**

> Nhóm chuẩn hóa hai nguồn về cùng cấu trúc nghiên cứu và ghép theo nhóm bệnh phục vụ thí nghiệm đối chứng. Đây là dữ liệu nghiên cứu tổng hợp, không phải hai phần của cùng một hồ sơ bệnh nhân được thu trực tiếp tại bệnh viện. Vì vậy, nhóm xem đây là bước chứng minh tính khả thi và sẽ cần xác thực trên dữ liệu đa phương thức được liên kết tự nhiên trong thực tế.

## 5. Làm sao tránh rò rỉ nhãn từ tên bệnh trong ghi chú?

**Trả lời gợi ý:**

> Các cụm từ chỉ trực tiếp tên chẩn đoán cần được che hoặc loại bỏ trước khi huấn luyện và đánh giá. Đồng thời, việc chia train, validation và test phải thực hiện ở cấp bệnh nhân trước các bước biến đổi dữ liệu để tránh cùng một bệnh nhân xuất hiện ở nhiều tập.

## 6. ECE thấp có nghĩa mô hình an toàn để sử dụng không?

**Trả lời gợi ý:**

> Không. ECE thấp chỉ cho thấy xác suất dự đoán được hiệu chỉnh tốt hơn theo cách đo hiện tại. Nó không thay thế đánh giá độ chính xác, độ nhạy, công bằng, lợi ích lâm sàng hay xác thực ngoài. Đây chỉ là một phần của bộ tiêu chí an toàn.

## 7. Vì sao dùng Cross-Attention Late Fusion?

**Trả lời gợi ý:**

> Hai loại dữ liệu có cấu trúc rất khác nhau, nên nhóm để hai bộ mã hóa học đặc trưng riêng trước. Cross-attention sau đó học mối liên hệ giữa các biểu diễn, ví dụ liên hệ một chỉ số CRP bất thường với đoạn ghi chú về triệu chứng. Cách này linh hoạt hơn việc nối trực tiếp dữ liệu thô.

## 8. Temperature Scaling có làm tăng Accuracy không?

**Trả lời gợi ý:**

> Thông thường Temperature Scaling chủ yếu hiệu chỉnh độ tin cậy của xác suất, không nhằm thay đổi thứ tự lớp dự đoán. Vì vậy, mục tiêu chính là giảm ECE hoặc cải thiện calibration, chứ không phải trực tiếp tăng Accuracy.

## 9. RAG có loại bỏ hoàn toàn hallucination không?

**Trả lời gợi ý:**

> Không thể bảo đảm tuyệt đối. RAG giúp giảm và kiểm soát rủi ro bằng cách giới hạn nguồn tri thức và yêu cầu trích dẫn. Hệ thống vẫn cần kiểm tra xem trích dẫn có tồn tại, có đúng ngữ cảnh và có thực sự hỗ trợ kết luận hay không. Quyết định cuối cùng vẫn thuộc về bác sĩ.

## 10. Bước tiếp theo quan trọng nhất của nghiên cứu là gì?

**Trả lời gợi ý:**

> Ba bước quan trọng là triển khai và so sánh mô hình dung hợp với các baseline; xác thực trên bộ dữ liệu đa phương thức độc lập từ nhiều cơ sở; và đánh giá lâm sàng bằng khoảng tin cậy, Decision Curve Analysis, calibration và kiểm định công bằng.

---

# Mẹo trình bày

- Không đọc nguyên văn chữ trên slide; hãy nhìn khán giả và chỉ dùng slide để dẫn ý.
- Khi trình bày slide 9, chỉ nhấn ba nhóm số: Accuracy, Macro-F1 và ECE.
- Khi trình bày slide 10–11, kể thành một câu chuyện: **dữ liệu có gì → mô hình nào sai → vì sao sai → bài học là gì**.
- Với slide 13–14, dùng tay hoặc con trỏ đi từ trái sang phải theo luồng hệ thống.
- Nói “hỗ trợ chẩn đoán” hoặc “hỗ trợ quyết định lâm sàng”, tránh nói hệ thống tự chẩn đoán thay bác sĩ.
- Nếu bị hỏi về hạn chế, chủ động thừa nhận giới hạn dữ liệu tổng hợp và tập kiểm thử nhỏ; sau đó nêu kế hoạch xác thực ngoài.
- Không khẳng định ECE dưới 5% là chuẩn y tế phổ quát.
- Không khẳng định RAG loại bỏ hoàn toàn hallucination.
