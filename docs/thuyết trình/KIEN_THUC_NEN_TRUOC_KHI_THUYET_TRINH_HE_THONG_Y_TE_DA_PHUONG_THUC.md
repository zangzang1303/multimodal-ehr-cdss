# Kiến thức nền trước khi thuyết trình

## Hệ thống hỗ trợ chẩn đoán y tế đa phương thức

Tài liệu này giúp các thành viên trong nhóm **hiểu bản chất đề tài trước khi học kịch bản thuyết trình**. Mục tiêu không phải là ghi nhớ thật nhiều thuật ngữ, mà là trả lời được bốn câu hỏi:

1. Đề tài đang giải quyết vấn đề gì?
2. Vì sao phải kết hợp dữ liệu bảng và văn bản?
3. Các mô hình và chỉ số thực sự có ý nghĩa gì?
4. Kết quả hiện tại chứng minh được điều gì và chưa chứng minh được điều gì?

---

# 1. Bức tranh tổng thể của đề tài

## 1.1. Bài toán nghiên cứu

Trong một hồ sơ sức khỏe điện tử, thông tin về bệnh nhân thường không nằm ở một chỗ duy nhất. Nó được phân tán trong nhiều loại dữ liệu:

- Sinh hiệu: huyết áp, nhịp tim, nhịp thở, nhiệt độ, SpO2.
- Xét nghiệm: bạch cầu, CRP và các chỉ số sinh hóa khác.
- Tiền sử: tăng huyết áp, tiểu đường, hút thuốc.
- Ghi chú của bác sĩ: triệu chứng, bệnh sử, diễn tiến, thuốc đang dùng và nhận định lâm sàng.

Nếu mô hình chỉ dùng sinh hiệu và xét nghiệm, nó có thể bỏ qua bệnh sử và ngữ cảnh. Nếu chỉ dùng ghi chú, nó có thể bị ảnh hưởng bởi từ ngữ gây nhiễu, thông tin thiếu hoặc bệnh đồng mắc.

Đề tài đặt ra giả thuyết:

> Dữ liệu bảng và ghi chú lâm sàng chứa các loại thông tin bổ sung cho nhau. Kết hợp hai phương thức có thể tạo ra mô hình ổn định hơn so với chỉ dùng một phương thức.

## 1.2. “Đa phương thức” nghĩa là gì?

Một **phương thức**, hay modality, là một dạng dữ liệu có cấu trúc và ý nghĩa riêng.

Trong đề tài này có hai phương thức chính:

| Phương thức | Ví dụ | Đặc điểm |
|---|---|---|
| Dữ liệu bảng | Tuổi, huyết áp, SpO2, WBC, CRP | Có cấu trúc, dễ chuẩn hóa, phản ánh phép đo cụ thể |
| Văn bản lâm sàng | Bệnh sử, triệu chứng, thuốc, khám lâm sàng | Giàu ngữ cảnh nhưng khó xử lý và có thể chứa nhiễu |

Hệ thống được gọi là đa phương thức khi nó có khả năng tiếp nhận, biểu diễn và kết hợp nhiều dạng dữ liệu như trên.

## 1.3. “Hỗ trợ quyết định” khác “thay thế bác sĩ” như thế nào?

Hệ thống hỗ trợ quyết định lâm sàng có thể:

- Đưa ra xác suất cho các nhóm bệnh.
- Gợi ý chẩn đoán phân biệt.
- Chỉ ra dữ liệu nào ảnh hưởng đến dự đoán.
- Truy xuất hướng dẫn chuyên môn liên quan.

Hệ thống không nên:

- Tự khẳng định chẩn đoán cuối cùng.
- Tự kê đơn hoặc quyết định điều trị.
- Bỏ qua ý kiến của bác sĩ.
- Được triển khai trên bệnh nhân thực nếu chưa được xác thực và phê duyệt.

Câu nói an toàn khi thuyết trình:

> Đây là nguyên mẫu nghiên cứu nhằm hỗ trợ bác sĩ tham khảo, không thay thế phán đoán chuyên môn và không tự động quyết định điều trị.

---

# 2. Hồ sơ sức khỏe điện tử và hai loại dữ liệu

## 2.1. EHR là gì?

EHR là viết tắt của **Electronic Health Record**, tức hồ sơ sức khỏe điện tử. EHR lưu trữ thông tin y tế của bệnh nhân trong quá trình khám và điều trị.

EHR có thể chứa:

- Thông tin nhân khẩu học.
- Chẩn đoán và mã bệnh.
- Sinh hiệu.
- Kết quả xét nghiệm.
- Thuốc và thủ thuật.
- Ghi chú khám bệnh.
- Báo cáo hình ảnh hoặc mô tả phẫu thuật.

## 2.2. Dữ liệu có cấu trúc

Dữ liệu có cấu trúc thường được biểu diễn thành bảng. Mỗi hàng là một hồ sơ, mỗi cột là một đặc trưng.

Ví dụ:

| Tuổi | Huyết áp tâm thu | SpO2 | WBC | CRP | Hút thuốc |
|---:|---:|---:|---:|---:|---|
| 65 | 115,9 | 95,6 | 4,30 | 7,14 | Không |

### Ưu điểm

- Dễ lưu trữ và kiểm tra.
- Dễ chuẩn hóa.
- Phù hợp với mô hình cây và mô hình học sâu cho dữ liệu bảng.
- Các giá trị thường có ý nghĩa lâm sàng rõ ràng.

### Nhược điểm

- Chỉ phản ánh những gì đã được đo và ghi thành trường dữ liệu.
- Một lần đo có thể không phản ánh diễn tiến dài hạn.
- Khi bệnh đang ổn định, các chỉ số có thể gần bình thường.
- Không chứa đầy đủ lý do dùng thuốc hoặc bối cảnh triệu chứng.

## 2.3. Văn bản lâm sàng

Văn bản lâm sàng là phần ghi chú tự do của bác sĩ hoặc nhân viên y tế.

Nó có thể chứa:

- Lý do nhập viện.
- Bệnh sử hiện tại.
- Tiền sử bệnh.
- Kết quả khám.
- Thuốc đang sử dụng.
- Diễn tiến và phản ứng điều trị.

### Ưu điểm

- Giàu ngữ cảnh.
- Có thể mô tả triệu chứng theo thời gian.
- Chứa thông tin về thuốc và tiền sử.
- Có thể giúp phân biệt các bệnh có sinh hiệu giống nhau.

### Nhược điểm

- Có lỗi viết tắt, lỗi chính tả hoặc cách diễn đạt không thống nhất.
- Chứa thông tin không liên quan đến mục tiêu dự đoán.
- Có thể bị nhiễu bởi bệnh đồng mắc.
- Có nguy cơ rò rỉ nhãn nếu tên chẩn đoán xuất hiện trực tiếp.
- Khó giải thích hơn dữ liệu bảng.

## 2.4. Vì sao hai phương thức bổ sung cho nhau?

Hãy tưởng tượng dữ liệu bảng là **một bức ảnh chụp tại một thời điểm**, còn văn bản lâm sàng là **câu chuyện về quá trình bệnh**.

- Bức ảnh cho biết hiện tại các chỉ số đang như thế nào.
- Câu chuyện cho biết triệu chứng xuất hiện khi nào, đã dùng thuốc gì và bệnh diễn tiến ra sao.

Chỉ có ảnh thì thiếu lịch sử. Chỉ có câu chuyện thì có thể thiếu phép đo khách quan. Dung hợp nhằm tận dụng cả hai.

---

# 3. Bốn nhóm bệnh trong nghiên cứu

Đề tài phân loại bốn nhóm bệnh: hen phế quản, COPD, suy tim và viêm phổi. Phần dưới đây chỉ giải thích ở mức phục vụ thuyết trình, không phải hướng dẫn chẩn đoán y khoa.

## 3.1. Hen phế quản – ASTHMA

Hen là bệnh viêm mạn tính đường thở, thường có tình trạng co thắt đường thở biến thiên.

Thông tin thường có ích:

- Khò khè hoặc khó thở từng cơn.
- Ho, đặc biệt về đêm hoặc sáng sớm.
- Triệu chứng thay đổi theo thời gian.
- Có yếu tố khởi phát như dị ứng hoặc gắng sức.
- Có tiền sử sử dụng thuốc hít.

Điểm quan trọng cho đề tài: giữa các đợt, bệnh nhân có thể có sinh hiệu gần bình thường. Do đó, một bảng số tại thời điểm bệnh ổn định có thể không đủ để nhận biết hen.

## 3.2. Bệnh phổi tắc nghẽn mạn tính – COPD

COPD là bệnh hô hấp mạn tính có giới hạn luồng khí kéo dài, thường liên quan đến phơi nhiễm khói thuốc hoặc chất kích thích.

Thông tin có thể hữu ích:

- Tuổi thường cao hơn bệnh nhân hen.
- Khó thở mạn tính và tiến triển.
- Ho hoặc khạc đờm kéo dài.
- Tiền sử hút thuốc hoặc phơi nhiễm.
- Có các đợt cấp.

Hen và COPD có thể cùng biểu hiện bằng khó thở, ho và khò khè, nên dễ bị nhầm nếu chỉ nhìn một số chỉ số đơn lẻ.

## 3.3. Suy tim – HEART_FAILURE

Suy tim là tình trạng tim không đáp ứng đầy đủ nhu cầu tuần hoàn của cơ thể hoặc chỉ đáp ứng được khi áp lực đổ đầy tăng.

Thông tin có thể hữu ích:

- Khó thở khi gắng sức hoặc khi nằm.
- Phù ngoại biên.
- Mệt mỏi.
- Dấu hiệu ứ dịch.
- Tiền sử bệnh tim mạch.

Suy tim có thể gây khó thở và giảm oxy, nên về triệu chứng có thể bị nhầm với bệnh hô hấp.

## 3.4. Viêm phổi – PNEUMONIA

Viêm phổi là tình trạng nhiễm trùng nhu mô phổi.

Thông tin có thể hữu ích:

- Sốt.
- Ho, có thể có đờm.
- Khó thở.
- Tăng bạch cầu hoặc CRP.
- Dấu hiệu nhiễm trùng cấp.

CRP tăng là dấu hiệu viêm, nhưng không tự nó xác định nguyên nhân hoặc chẩn đoán cụ thể. Không nên nói “CRP tăng nghĩa là viêm phổi”.

## 3.5. Vì sao bốn bệnh này phù hợp để nghiên cứu?

Bốn nhóm có các biểu hiện chồng lấp:

- Đều có thể gây khó thở.
- Hen, COPD và viêm phổi có thể gây ho.
- Suy tim và bệnh phổi đều có thể làm giảm SpO2.
- Một số thuốc và dấu hiệu khám có thể xuất hiện trong nhiều bệnh.

Sự chồng lấp này tạo ra bài toán chẩn đoán phân biệt có ý nghĩa cho nghiên cứu đa phương thức.

---

# 4. Nguồn dữ liệu của đề tài

## 4.1. Synthea

Synthea là công cụ tạo dữ liệu bệnh nhân tổng hợp. Dữ liệu được mô phỏng theo các mô hình bệnh và quy trình chăm sóc sức khỏe.

### Lợi ích

- Không trực tiếp tiết lộ thông tin nhận dạng bệnh nhân thật.
- Có cấu trúc tương đối rõ.
- Hữu ích để phát triển và kiểm thử nguyên mẫu.

### Giới hạn

- Dữ liệu tổng hợp không thể tái hiện đầy đủ độ phức tạp của bệnh viện thực tế.
- Các mối quan hệ trong dữ liệu có thể phản ánh quy tắc của trình mô phỏng.
- Mô hình tốt trên Synthea chưa chắc tốt trên bệnh nhân thật.

## 4.2. MTSamples

MTSamples là nguồn các mẫu ghi chú và báo cáo y khoa thuộc nhiều chuyên khoa.

### Lợi ích

- Cung cấp văn bản gần với cách mô tả lâm sàng.
- Chứa bệnh sử, khám lâm sàng, thuốc và diễn tiến.

### Giới hạn

- Không nhất thiết đại diện cho phân bố bệnh nhân tại Việt Nam.
- Văn phong và cấu trúc có thể khác nhau giữa các mẫu.
- Có nguy cơ xuất hiện trực tiếp tên chẩn đoán.
- Không mặc nhiên là phần văn bản tương ứng tự nhiên với một bản ghi Synthea cụ thể.

## 4.3. Vấn đề ghép hai nguồn dữ liệu

Đây là điểm nhóm phải hiểu rõ để tránh trả lời quá mức.

Nếu dữ liệu bảng từ Synthea được ghép với ghi chú từ MTSamples dựa trên cùng nhãn bệnh, thì cặp dữ liệu đó là **cặp nghiên cứu được xây dựng**, không phải hai phương thức được thu tự nhiên từ cùng một bệnh nhân thật.

Điều đó có nghĩa:

- Phù hợp để chứng minh tính khả thi của quy trình.
- Phù hợp để so sánh baseline trong môi trường kiểm soát.
- Chưa đủ để khẳng định hiệu quả lâm sàng thực tế.
- Cần xác thực sau này trên dữ liệu bảng và văn bản thực sự thuộc cùng một lần khám hoặc cùng một bệnh nhân.

Câu trả lời nên dùng:

> Bộ dữ liệu hiện tại là bộ dữ liệu nghiên cứu được tổng hợp và chuẩn hóa từ nguồn mở. Nó phục vụ đánh giá nguyên mẫu, chưa thay thế cho xác thực trên dữ liệu đa phương thức được liên kết tự nhiên tại bệnh viện.

## 4.4. Cân bằng bốn lớp có ý nghĩa gì?

Nếu 2.000 hồ sơ được phân bố cân bằng, mỗi lớp có khoảng 500 hồ sơ.

Lợi ích:

- Giảm xu hướng mô hình luôn đoán lớp phổ biến.
- Accuracy dễ diễn giải hơn so với dữ liệu mất cân bằng mạnh.
- Mỗi nhóm bệnh có số mẫu tương đối tương đương để huấn luyện.

Giới hạn:

- Phân bố cân bằng có thể không giống tỷ lệ bệnh ngoài thực tế.
- Khi triển khai ở bệnh viện, xác suất dự đoán có thể cần hiệu chỉnh lại theo tỷ lệ bệnh thực.

---

# 5. Ba mô hình baseline

## 5.1. Baseline là gì?

Baseline là mô hình làm mốc để so sánh. Một mô hình dung hợp mới chỉ có ý nghĩa nếu được so sánh công bằng với các baseline phù hợp.

Trong đề tài:

- CatBoost đại diện cho mô hình cây mạnh trên dữ liệu bảng.
- FT-Transformer đại diện cho mô hình học sâu trên dữ liệu bảng.
- Bio_ClinicalBERT đại diện cho mô hình ngôn ngữ trên ghi chú lâm sàng.

Ba baseline trả lời câu hỏi:

> Nếu chỉ dùng một phương thức, mức hiệu quả tốt nhất hiện tại là bao nhiêu?

## 5.2. CatBoost

CatBoost thuộc họ gradient boosting trên cây quyết định.

Cách hiểu đơn giản:

1. Mô hình tạo một cây quyết định để dự đoán.
2. Xem cây đó sai ở đâu.
3. Tạo cây tiếp theo để sửa phần sai.
4. Lặp lại và tổng hợp kết quả của nhiều cây.

### Điểm mạnh

- Hoạt động tốt trên dữ liệu bảng.
- Có thể mô hình hóa quan hệ phi tuyến.
- Ít đòi hỏi dữ liệu hơn nhiều mô hình học sâu.
- Có cơ chế xử lý biến phân loại tốt.

### Điểm yếu

- Không được thiết kế để hiểu văn bản dài.
- Khả năng khai thác quan hệ rất phức tạp phụ thuộc vào đặc trưng đầu vào.

## 5.3. XGBoost

XGBoost cũng là mô hình gradient boosting trên cây. Slide mục tiêu có nhắc “CatBoost/XGBoost”, nhưng bảng kết quả hiện tại báo cáo CatBoost.

Khi thuyết trình cần phân biệt:

- Nếu được hỏi mô hình đã có kết quả trong bảng: **CatBoost**.
- XGBoost có thể là phương án baseline bổ sung hoặc cách gọi khái quát trong kế hoạch.

Không nên nói rằng bảng đã báo cáo kết quả XGBoost nếu không có dòng kết quả tương ứng.

## 5.4. FT-Transformer

FT-Transformer là kiến trúc Transformer được điều chỉnh cho dữ liệu bảng.

Cách hiểu đơn giản:

- Mỗi trường dữ liệu được biến thành một vector biểu diễn.
- Cơ chế self-attention học xem các trường nào liên quan đến nhau.
- Ví dụ, ý nghĩa của SpO2 có thể được xét cùng tuổi, nhịp thở và CRP.

### Điểm mạnh

- Có khả năng học tương tác giữa các đặc trưng.
- Linh hoạt khi dữ liệu đủ lớn và được tối ưu tốt.

### Điểm yếu

- Có thể cần nhiều dữ liệu hơn mô hình cây.
- Nhạy với siêu tham số.
- Không mặc nhiên tốt hơn CatBoost trên dữ liệu bảng nhỏ.

Trong kết quả hiện tại, FT-Transformer thấp hơn CatBoost. Điều này không lạ vì tập dữ liệu 2.000 hồ sơ tương đối nhỏ đối với mô hình học sâu.

## 5.5. BERT

BERT là mô hình ngôn ngữ dựa trên Transformer. Nó học biểu diễn của từ dựa trên cả ngữ cảnh bên trái và bên phải.

Ví dụ, từ “âm tính” trong câu “xét nghiệm âm tính” không thể hiểu đúng nếu chỉ đọc riêng từng từ. BERT dùng ngữ cảnh để tạo biểu diễn phù hợp hơn.

## 5.6. Bio_ClinicalBERT

Bio_ClinicalBERT là biến thể BERT được thích nghi với ngôn ngữ y sinh và ghi chú lâm sàng.

### Vì sao phù hợp?

- Hiểu tốt hơn các thuật ngữ y khoa so với BERT tổng quát.
- Có thể nhận ra mẫu thông tin về triệu chứng, thuốc và bệnh sử.
- Có thể được fine-tune cho bài toán phân loại bốn bệnh.

### Vì sao vẫn có thể sai?

- Ghi chú có thể chứa nhiễu.
- Bệnh đồng mắc tạo ngữ cảnh phức tạp.
- Một số dấu hiệu xuất hiện trong nhiều bệnh.
- Nếu tên bệnh bị che, mô hình phải suy luận từ các dấu hiệu còn lại.
- Nếu dữ liệu huấn luyện nhỏ, mô hình có thể học các tương quan không bền vững.

---

# 6. Cách chia dữ liệu và tránh rò rỉ

## 6.1. Train, validation và test

- **Train set:** dùng để cập nhật trọng số mô hình.
- **Validation set:** dùng để chọn siêu tham số, ngưỡng và dừng huấn luyện.
- **Test set:** chỉ dùng để đánh giá cuối cùng.

Tập test “độc lập” có nghĩa là không được dùng nó để chọn mô hình hoặc điều chỉnh siêu tham số.

## 6.2. Rò rỉ dữ liệu là gì?

Rò rỉ dữ liệu xảy ra khi mô hình vô tình nhận được thông tin về đáp án mà ngoài thực tế nó không có.

Ví dụ:

- Ghi chú chứa trực tiếp dòng “Diagnosis: COPD”.
- Cùng một bệnh nhân xuất hiện ở cả train và test.
- Chuẩn hóa dữ liệu bằng trung bình và độ lệch chuẩn tính trên toàn bộ tập, gồm cả test.
- Chọn ngưỡng dựa trên kết quả của test.

## 6.3. Cách hạn chế rò rỉ

- Chia dữ liệu ở cấp bệnh nhân trước mọi bước xử lý.
- Che tên bệnh hoặc thông tin trực tiếp tiết lộ nhãn.
- Chỉ fit bộ chuẩn hóa trên tập train.
- Chỉ dùng validation để chọn ngưỡng và siêu tham số.
- Giữ test đến cuối quá trình.

## 6.4. Che tên bệnh chưa đủ

Ngay cả khi tên bệnh được che, văn bản vẫn có thể chứa dấu hiệu gần như tiết lộ nhãn, chẳng hạn tên thuốc quá đặc hiệu hoặc tên thủ thuật liên quan trực tiếp đến bệnh.

Do đó, cần kiểm tra cả:

- Rò rỉ trực tiếp: xuất hiện tên chẩn đoán.
- Rò rỉ gián tiếp: xuất hiện mã bệnh, tiêu đề hoặc cụm từ được tạo sau khi chẩn đoán đã biết.

---

# 7. Các chỉ số đánh giá

Tài liệu riêng `GIAI_THICH_CAC_CHI_SO_DANH_GIA_MO_HINH.md` đã giải thích chi tiết. Phần này tập trung vào cách hiểu nhanh để trả lời khi thuyết trình.

## 7.1. AUROC macro

AUROC đo khả năng mô hình xếp mẫu đúng lớp cao hơn mẫu không thuộc lớp đó trên nhiều ngưỡng.

Với bài toán nhiều lớp:

1. Xem từng bệnh là lớp dương tính, các bệnh còn lại là lớp âm tính.
2. Tính AUROC riêng cho từng bệnh.
3. Lấy trung bình không trọng số.

“Macro” nghĩa là mỗi bệnh có một lá phiếu ngang nhau.

### Cách nhớ

> AUROC trả lời: mô hình có xếp đúng thứ tự nguy cơ không?

### Lưu ý

AUROC cao không có nghĩa xác suất được hiệu chỉnh tốt và cũng không bảo đảm mô hình có Precision cao.

## 7.2. AUPRC macro

AUPRC tổng hợp quan hệ giữa Precision và Recall qua nhiều ngưỡng.

- Precision: trong những mẫu được dự đoán là bệnh X, bao nhiêu mẫu thật sự là X?
- Recall: trong toàn bộ mẫu thật sự là bệnh X, mô hình tìm được bao nhiêu?

### Cách nhớ

> AUPRC trả lời: danh sách cảnh báo có vừa đúng vừa đủ không?

## 7.3. Macro-F1

F1 kết hợp Precision và Recall. Macro-F1 tính F1 riêng cho từng lớp rồi lấy trung bình.

### Cách nhớ

> Macro-F1 cho biết mô hình có làm tốt tương đối đồng đều trên bốn bệnh không?

Macro-F1 thấp hơn Accuracy nhiều có thể là dấu hiệu mô hình làm tốt ở một số lớp nhưng yếu ở lớp khác.

## 7.4. Accuracy

Accuracy là tỷ lệ tổng số dự đoán đúng.

Vì dữ liệu nghiên cứu được cân bằng tương đối giữa bốn lớp, Accuracy có ý nghĩa hơn so với trường hợp một lớp chiếm gần toàn bộ dữ liệu. Tuy nhiên, vẫn không nên dùng Accuracy một mình.

## 7.5. Brier Score

Brier Score đo sai số bình phương giữa xác suất dự đoán và kết quả thật.

- Dự đoán tự tin và đúng → sai số nhỏ.
- Dự đoán tự tin và sai → sai số lớn.
- Brier càng thấp càng tốt.

Với bài toán nhiều lớp, cần nói rõ cách triển khai Brier, chẳng hạn trung bình tổng sai số trên vector xác suất. Khi so sánh các mô hình trong cùng thí nghiệm, điều quan trọng nhất là dùng cùng một cách tính.

## 7.6. ECE

ECE đo độ lệch giữa độ tin cậy dự đoán và tỷ lệ đúng thực tế.

Ví dụ:

- Mô hình có 100 dự đoán với độ tin cậy khoảng 80%.
- Nếu chỉ 50 dự đoán đúng, mô hình đang quá tự tin.
- Nếu khoảng 80 dự đoán đúng, mô hình được hiệu chỉnh tốt hơn.

ECE càng thấp càng tốt.

### Lưu ý quan trọng

ECE phụ thuộc vào số bin và cách chia bin. Không nên nói ECE dưới 5% là một chuẩn y tế phổ quát nếu không có tài liệu quy định cụ thể.

## 7.7. Phân biệt discrimination và calibration

Đây là câu hỏi phản biện rất thường gặp.

- **Discrimination:** mô hình có phân biệt và xếp hạng đúng các bệnh nhân không? AUROC phản ánh khía cạnh này.
- **Calibration:** xác suất mô hình đưa ra có phù hợp với tần suất đúng thực tế không? ECE và Brier phản ánh khía cạnh này.

Một mô hình có thể xếp hạng rất tốt nhưng xác suất quá tự tin. Vì vậy cần đánh giá cả hai.

---

# 8. Đọc kết quả thực nghiệm đúng cách

## 8.1. Bảng kết quả

| Mô hình | Dữ liệu | AUROC (M) | AUPRC (M) | Macro-F1 | Accuracy | Brier | ECE |
|---|---|---:|---:|---:|---:|---:|---:|
| CatBoost | Bảng | 0,9223 | 0,7872 | 0,6083 | 0,6854 | 0,3844 | 6,63% |
| FT-Transformer | Bảng | 0,8976 | 0,7023 | 0,5789 | 0,6589 | 0,4725 | 11,52% |
| Bio_ClinicalBERT | Văn bản | 0,9735 | 0,9314 | 0,8421 | 0,8543 | 0,2329 | 3,73% |

## 8.2. Kết luận trực tiếp từ bảng

Trên tập test 302 mẫu của nghiên cứu:

- Bio_ClinicalBERT có kết quả tốt nhất ở tất cả chỉ số được báo cáo.
- CatBoost tốt hơn FT-Transformer trên dữ liệu bảng.
- FT-Transformer có ECE cao nhất, cho thấy chất lượng hiệu chỉnh xác suất thấp hơn.
- Văn bản chứa tín hiệu phân biệt mạnh trong bộ dữ liệu hiện tại.

## 8.3. Điều bảng chưa chứng minh

Bảng chưa đủ để kết luận rằng:

- Bio_ClinicalBERT tốt hơn trong mọi bệnh viện.
- Văn bản luôn tốt hơn dữ liệu bảng.
- Mô hình đã sẵn sàng triển khai lâm sàng.
- Kiến trúc dung hợp chắc chắn tốt hơn baseline.
- Chênh lệch giữa các mô hình có ý nghĩa thống kê.

Muốn kết luận mạnh hơn, cần:

- Khoảng tin cậy 95%.
- Kiểm định hoặc so sánh thống kê phù hợp.
- Xác thực ngoài trên dữ liệu độc lập.
- Phân tích theo từng lớp bệnh.
- Đánh giá công bằng và calibration.

## 8.4. Vì sao AUROC cao nhưng Accuracy chỉ khoảng 66–69% ở mô hình bảng?

AUROC đánh giá khả năng xếp hạng trên nhiều ngưỡng, còn Accuracy phụ thuộc vào quyết định lớp cuối cùng. Một mô hình có thể xếp xác suất tương đối đúng nhưng vẫn nhầm giữa hai lớp gần nhau khi chọn lớp có xác suất cao nhất.

Ngoài ra, macro-AUROC theo cách one-vs-rest có thể cao trong khi khả năng phân biệt trực tiếp giữa hai lớp khó, ví dụ hen và COPD, vẫn còn hạn chế.

## 8.5. Vì sao FT-Transformer không thắng CatBoost?

Một số lý do hợp lý:

- Cỡ dữ liệu 2.000 mẫu còn nhỏ.
- Mô hình học sâu có nhiều tham số hơn.
- CatBoost có inductive bias rất phù hợp cho dữ liệu bảng.
- Siêu tham số hoặc quy trình huấn luyện có thể chưa tối ưu.

Không nên kết luận FT-Transformer luôn kém CatBoost; chỉ nên nói nó kém hơn trong thiết lập thí nghiệm hiện tại.

---

# 9. Hiểu hai ca bệnh

## 9.1. Ca PT-0044 – bảng số sai, văn bản đúng

### Nhãn thực tế

Hen phế quản.

### Dữ liệu bảng đáng chú ý

- Tuổi: 18.
- Huyết áp: 106,2/78,0 mmHg.
- Nhịp tim: 70,6 bpm.
- Nhịp thở: 12,8.
- SpO2: 97,3%.
- WBC: 4,78.
- CRP: 24,28 mg/L, tăng.

Nhiều sinh hiệu còn tương đối ổn định. Vì vậy, bảng số tại một thời điểm không cung cấp dấu hiệu đặc hiệu rõ cho hen.

### Kết quả

- CatBoost dự đoán COPD: 78,82%.
- FT-Transformer dự đoán COPD: 74,10%.
- Bio_ClinicalBERT dự đoán đúng hen: 85,80%.

### Vì sao văn bản có lợi?

Ghi chú chứa:

- Ho.
- Khó thở.
- Mệt mỏi.
- Thông tin sử dụng thuốc hít.

Thuốc và diễn tiến triệu chứng cung cấp ngữ cảnh mà bảng số không thể hiện.

### Bài học

> Dữ liệu bảng có thể bỏ sót bệnh khi phép đo được thực hiện lúc bệnh tương đối ổn định; văn bản giúp bổ sung diễn tiến và lịch sử điều trị.

### Điều không nên nói

Không nên nói chỉ cần “thuốc hít” là đủ chẩn đoán hen. Thuốc hít cũng có thể được dùng trong COPD và các tình huống khác. Kết quả đến từ tổng hợp ngữ cảnh, không phải một từ khóa duy nhất.

## 9.2. Ca PT-0254 – văn bản sai, bảng số đúng

### Nhãn thực tế

COPD.

### Dữ liệu bảng đáng chú ý

- Tuổi: 65.
- Huyết áp: 115,9/80,1 mmHg.
- Nhịp tim: 64,3 bpm.
- SpO2: 95,6%.
- WBC: 4,30.
- CRP: 7,14 mg/L.

### Kết quả

- CatBoost dự đoán đúng COPD: 75,22%.
- FT-Transformer dự đoán đúng COPD: 71,30%.
- Bio_ClinicalBERT dự đoán sai suy tim: 58,99%.

### Vì sao văn bản có thể bị nhiễu?

Ghi chú mô tả bệnh cảnh phức tạp:

- Mở khí quản.
- Từng cần hỗ trợ máy thở.
- Có ran phổi.
- Sử dụng nhiều loại thuốc.
- Tên chẩn đoán trực tiếp đã được che.

Các chi tiết về bệnh nặng, điều trị và thuốc có thể làm biểu diễn ngữ nghĩa nghiêng sang một bệnh khác.

### Bài học

> Văn bản giàu thông tin nhưng cũng giàu nhiễu. Dữ liệu bảng có thể cung cấp tín hiệu khách quan để giúp mô hình không bị chệch hướng hoàn toàn bởi ngữ cảnh phức tạp.

## 9.3. Hai ca bệnh có chứng minh dung hợp tốt hơn không?

Chưa.

Hai ca bệnh chỉ cung cấp **luận cứ định tính** rằng hai phương thức có lỗi khác nhau và có khả năng bổ sung cho nhau. Muốn chứng minh dung hợp tốt hơn, cần:

- Triển khai mô hình dung hợp.
- Đánh giá trên cùng tập test.
- So sánh chỉ số và khoảng tin cậy với các baseline.
- Phân tích thống kê chênh lệch.

Cách nói đúng:

> Hai case study tạo cơ sở khoa học cho việc thử nghiệm dung hợp ở giai đoạn tiếp theo.

---

# 10. Kiến trúc dung hợp đa phương thức

## 10.1. Luồng xử lý tổng quát

```text
Dữ liệu bảng ──> FT-Transformer ──┐
                                  ├─> Cross-Attention Late Fusion
Ghi chú ───────> ClinicalBERT ────┘
                                      │
                                      v
                              Classification Head
                                      │
                                      v
                              Temperature Scaling
                                      │
                                      v
                         Xác suất của bốn nhóm bệnh
```

## 10.2. Bộ mã hóa là gì?

Bộ mã hóa biến dữ liệu đầu vào thành vector đặc trưng mà mô hình có thể sử dụng.

- FT-Transformer mã hóa các trường dữ liệu bảng.
- Bio_ClinicalBERT mã hóa ý nghĩa của ghi chú.

Hai vector này không nhất thiết có cùng kích thước hoặc cùng ý nghĩa, nên cần lớp chiếu hoặc lớp dung hợp thích hợp.

## 10.3. Early fusion và late fusion

### Early fusion

Ghép dữ liệu hoặc đặc trưng từ rất sớm.

Ưu điểm:

- Kiến trúc đơn giản.
- Cho mô hình học tương tác từ đầu.

Nhược điểm:

- Khó ghép dữ liệu có bản chất rất khác nhau.
- Dễ làm mất đặc trưng riêng của từng phương thức.

### Late fusion

Mỗi phương thức được xử lý riêng trước, sau đó mới kết hợp các biểu diễn.

Ưu điểm:

- Tận dụng bộ mã hóa chuyên biệt.
- Linh hoạt khi một phương thức bị thiếu.
- Dễ kiểm soát đóng góp của từng nhánh.

Nhược điểm:

- Có thể bỏ lỡ tương tác mức thấp.
- Kiến trúc và quá trình huấn luyện phức tạp hơn.

## 10.4. Cross-attention là gì?

Attention là cơ chế cho phép mô hình gán trọng số khác nhau cho các phần thông tin.

Cross-attention cho phép biểu diễn của phương thức này “nhìn” sang phương thức còn lại.

Ví dụ khái niệm:

- Văn bản nhắc “sốt và ho kéo dài”.
- Dữ liệu bảng có CRP tăng.
- Cross-attention có thể học rằng hai tín hiệu này cần được xem xét cùng nhau.

Cross-attention không tự động tạo ra giải thích lâm sàng đáng tin. Trọng số attention chỉ là một tín hiệu nội bộ và không nên được xem là bằng chứng nhân quả.

## 10.5. Classification Head

Classification Head nhận biểu diễn đã dung hợp và tạo ra điểm cho bốn lớp bệnh.

Sau hàm softmax, ta nhận vector xác suất, ví dụ:

```text
ASTHMA        0,10
COPD          0,65
HEART_FAILURE 0,15
PNEUMONIA     0,10
```

Mô hình sẽ chọn COPD vì có xác suất cao nhất, nhưng bác sĩ cần xem cả mức độ tin cậy và bằng chứng đi kèm.

## 10.6. Nếu thiếu một phương thức thì sao?

Đây là vấn đề thực tế quan trọng. Một hồ sơ có thể thiếu xét nghiệm hoặc thiếu ghi chú.

Các hướng xử lý gồm:

- Huấn luyện với modality dropout: chủ động che ngẫu nhiên một phương thức khi huấn luyện.
- Dùng mặt nạ cho dữ liệu thiếu.
- Có nhánh fallback đơn phương thức.
- Chỉ xuất dự đoán khi dữ liệu đáp ứng yêu cầu tối thiểu.

Kiến trúc trên slide chưa chứng minh đã xử lý hoàn chỉnh trường hợp thiếu phương thức; đây là hướng cần phát triển thêm.

---

# 11. Hiệu chỉnh xác suất và Temperature Scaling

## 11.1. Vì sao xác suất cần được hiệu chỉnh?

Trong y tế, 90% và 60% dẫn đến mức độ tin cậy khác nhau. Nếu mô hình thường xuyên nói 90% nhưng chỉ đúng 60%, nó có thể khiến người dùng quá tin tưởng.

Một mô hình tốt cần:

- Dự đoán đúng lớp.
- Xác suất phù hợp với tần suất đúng thực tế.

## 11.2. Temperature Scaling hoạt động thế nào?

Trước softmax, mô hình tạo ra các logit. Temperature Scaling chia các logit cho một tham số nhiệt độ `T`:

```text
softmax(logits / T)
```

- Nếu `T > 1`, phân bố xác suất thường mềm hơn, mô hình bớt tự tin.
- Nếu `T < 1`, phân bố xác suất thường sắc hơn, mô hình tự tin hơn.

`T` được học trên tập validation, không phải tập test.

## 11.3. Temperature Scaling có tăng Accuracy không?

Thông thường không. Nó thường không thay đổi lớp có logit lớn nhất, nên Accuracy giữ nguyên. Mục tiêu chính là cải thiện calibration, chẳng hạn giảm ECE hoặc NLL.

## 11.4. Giới hạn

- Chỉ dùng một tham số nhiệt độ nên khả năng sửa sai có giới hạn.
- Calibration có thể thay đổi khi dữ liệu triển khai khác dữ liệu huấn luyện.
- Cần đánh giá lại khi chuyển sang bệnh viện hoặc quần thể mới.

---

# 12. Agentic RAG và giải thích dựa trên bằng chứng

## 12.1. RAG là gì?

RAG là viết tắt của **Retrieval-Augmented Generation**, tức sinh nội dung có hỗ trợ truy xuất.

Thay vì yêu cầu mô hình ngôn ngữ trả lời chỉ dựa trên kiến thức trong trọng số, hệ thống:

1. Nhận câu hỏi hoặc dự đoán cần giải thích.
2. Truy xuất đoạn tài liệu liên quan.
3. Đưa các đoạn đó vào ngữ cảnh.
4. Sinh câu trả lời dựa trên nguồn vừa truy xuất.

## 12.2. Vector Store là gì?

Tài liệu được chia thành các đoạn. Mỗi đoạn được biến thành vector embedding và lưu trong kho vector.

Khi có truy vấn, hệ thống tìm các vector gần nhất về mặt ngữ nghĩa. Ví dụ, truy vấn về tiêu chí kiểm soát hen sẽ tìm các đoạn liên quan trong GINA.

## 12.3. Semantic Retriever là gì?

Semantic Retriever là bộ truy xuất theo ý nghĩa, không chỉ dựa trên từ khóa trùng khớp.

Ví dụ, truy vấn “bệnh nhân khó thở từng cơn” vẫn có thể tìm đoạn nói về “variable respiratory symptoms”, dù từ ngữ không giống hoàn toàn.

## 12.4. Agentic RAG là gì?

“Agentic” cho thấy mô hình hoặc tác tử có thể thực hiện nhiều bước:

- Xác định cần tìm loại bằng chứng nào.
- Truy xuất tài liệu.
- Đánh giá nguồn có đủ liên quan hay không.
- Tìm bổ sung nếu cần.
- Tạo giải thích và gắn trích dẫn.
- Kiểm tra lại bằng chứng trước khi trả kết quả.

## 12.5. Hai loại bằng chứng cần có

### Bằng chứng từ hồ sơ

- Chỉ số bất thường.
- Triệu chứng cụ thể.
- Thuốc đang dùng.
- Đoạn ghi chú liên quan.

### Bằng chứng từ y văn

- Tên hướng dẫn.
- Phiên bản hoặc năm.
- Mục và số trang.
- Đoạn nội dung thực sự hỗ trợ nhận định.

## 12.6. GINA và GOLD

- **GINA:** Global Initiative for Asthma, cung cấp chiến lược quản lý và dự phòng hen.
- **GOLD:** Global Initiative for Chronic Obstructive Lung Disease, cung cấp chiến lược chẩn đoán và quản lý COPD.

Cần chú ý phiên bản tài liệu vì hướng dẫn có thể được cập nhật theo thời gian.

## 12.7. RAG có loại bỏ hallucination không?

Không thể bảo đảm tuyệt đối.

RAG vẫn có thể:

- Truy xuất đoạn không liên quan.
- Bỏ sót nguồn tốt hơn.
- Trích dẫn nguồn có thật nhưng diễn giải sai.
- Sinh kết luận mạnh hơn điều nguồn cho phép.
- Gắn trích dẫn không thực sự hỗ trợ câu trả lời.

Câu nói đúng:

> RAG giúp giảm và kiểm soát nguy cơ hallucination bằng cách yêu cầu mọi nhận định phải gắn với nguồn có thể kiểm tra.

## 12.8. Cách kiểm chứng trích dẫn

Một hệ thống tốt cần kiểm tra:

1. Tài liệu có tồn tại không?
2. Đúng phiên bản không?
3. Trang hoặc mục trích dẫn có tồn tại không?
4. Đoạn trích có liên quan đến nhận định không?
5. Nhận định có vượt quá nội dung nguồn không?

---

# 13. Đánh giá lâm sàng mở rộng

## 13.1. Khoảng tin cậy bootstrap 95%

Một chỉ số như AUROC 0,9735 chỉ là ước lượng trên một tập test cụ thể. Nếu đổi mẫu bệnh nhân, chỉ số có thể thay đổi.

Bootstrap thực hiện:

1. Lấy mẫu lại từ tập test có hoàn lại.
2. Tính lại chỉ số.
3. Lặp 1.000 lần.
4. Dùng phân bố kết quả để tạo khoảng tin cậy 95%.

Ví dụ minh họa:

```text
AUROC = 0,973; 95% CI: 0,952–0,988
```

Khoảng hẹp cho thấy ước lượng ổn định hơn. Khoảng rộng cho thấy còn nhiều bất định.

## 13.2. Decision Curve Analysis

Decision Curve Analysis đánh giá **Net Benefit**, tức lợi ích ròng của việc sử dụng mô hình tại các ngưỡng quyết định khác nhau.

Nó so sánh mô hình với các chiến lược đơn giản:

- Can thiệp cho tất cả.
- Không can thiệp cho ai.
- Can thiệp theo dự đoán của mô hình.

Ý nghĩa:

> Một mô hình có AUROC tốt chưa chắc tạo ra quyết định lâm sàng tốt. Decision Curve Analysis đưa hậu quả của dương tính giả và âm tính giả vào đánh giá.

## 13.3. Kiểm định công bằng

Cần kiểm tra hiệu quả theo các nhóm:

- Tuổi.
- Giới tính.
- Cơ sở y tế.
- Nhóm dân số hoặc đặc điểm liên quan khác, nếu dữ liệu cho phép.

Các chỉ số quan trọng:

- Sensitivity theo nhóm.
- Specificity theo nhóm.
- Calibration theo nhóm.

Accuracy tổng thể tốt có thể che giấu việc mô hình hoạt động kém ở một nhóm nhỏ.

## 13.4. TRIPOD-AI

TRIPOD-AI là hướng dẫn báo cáo nghiên cứu mô hình dự đoán sử dụng AI. Mục tiêu là tăng tính minh bạch về:

- Nguồn và tiêu chí chọn dữ liệu.
- Định nghĩa đầu ra.
- Xử lý dữ liệu thiếu.
- Chia tập dữ liệu.
- Phát triển và đánh giá mô hình.
- Hiệu chỉnh và xác thực.
- Giới hạn và khả năng áp dụng.

Tuân thủ hướng dẫn báo cáo không tự động làm mô hình tốt, nhưng giúp người đọc đánh giá nghiên cứu rõ ràng hơn.

## 13.5. PROBAST và nguy cơ sai lệch

PROBAST là công cụ đánh giá nguy cơ sai lệch và khả năng áp dụng của nghiên cứu mô hình dự đoán.

Các nguồn sai lệch có thể đến từ:

- Cách chọn người tham gia.
- Cách định nghĩa biến dự đoán.
- Cách xác định kết quả thật.
- Phân tích thống kê và đánh giá mô hình.

Ví dụ nguy cơ sai lệch cao:

- Cỡ mẫu quá nhỏ.
- Quá nhiều đặc trưng so với số mẫu.
- Đánh giá trên dữ liệu đã dùng để điều chỉnh mô hình.
- Không xử lý dữ liệu thiếu phù hợp.
- Không kiểm soát rò rỉ dữ liệu.

---

# 14. Giới hạn và ranh giới khoa học

## 14.1. Dữ liệu tổng hợp và nguồn mở

Kết quả trên dữ liệu tổng hợp có giá trị cho phát triển nguyên mẫu, nhưng không đủ để chứng minh hiệu quả lâm sàng.

Cần xác thực trên:

- Dữ liệu bệnh viện thực.
- Nhiều cơ sở y tế.
- Nhiều nhóm dân số.
- Dữ liệu được thu ở các thời điểm khác nhau.

## 14.2. Tập test 302 mẫu

302 mẫu cho phép đánh giá ban đầu, nhưng còn hạn chế khi:

- Ước lượng chỉ số theo từng lớp.
- Tạo khoảng tin cậy hẹp.
- Đánh giá theo nhóm tuổi và giới.
- Phân tích lỗi hiếm.

## 14.3. Distribution shift

Distribution shift xảy ra khi dữ liệu triển khai khác dữ liệu huấn luyện.

Ví dụ:

- Bệnh viện mới sử dụng quy trình xét nghiệm khác.
- Tỷ lệ bệnh khác.
- Cách bác sĩ viết ghi chú khác.
- Ngôn ngữ hoặc viết tắt khác.

Mô hình có thể giảm hiệu quả và mất calibration khi gặp distribution shift.

## 14.4. Tương quan không phải quan hệ nhân quả

Mô hình học các mẫu tương quan trong dữ liệu. Nó không tự chứng minh rằng một đặc trưng gây ra bệnh.

Ví dụ, một thuốc thường xuất hiện cùng một bệnh không có nghĩa thuốc đó gây ra bệnh hoặc đủ để chẩn đoán bệnh.

## 14.5. Kết quả nghiên cứu hiện tại nên được mô tả thế nào?

Cách nói phù hợp:

> Kết quả cung cấp bằng chứng ban đầu rằng ghi chú lâm sàng có tín hiệu dự đoán mạnh và hai phương thức có lỗi bổ sung cho nhau trên bộ dữ liệu nghiên cứu.

Cách nói quá mức cần tránh:

> Hệ thống đã chứng minh chẩn đoán chính xác trong thực tế.

---

# 15. Các điểm dễ bị phản biện

## 15.1. “Hệ thống chẩn đoán” hay “hệ thống hỗ trợ chẩn đoán”?

Nên dùng “hệ thống hỗ trợ chẩn đoán” hoặc “hỗ trợ quyết định lâm sàng”. Từ “hệ thống chẩn đoán” có thể khiến người nghe hiểu rằng mô hình tự đưa ra quyết định cuối cùng.

## 15.2. “Bio_ClinicalBERT áp đảo” có quá mạnh không?

Có thể dùng trong phần nói không chính thức, nhưng phát biểu khoa học nên là:

> Bio_ClinicalBERT đạt kết quả cao nhất trên tất cả chỉ số được báo cáo trong tập kiểm thử hiện tại.

## 15.3. ECE dưới 5% có phải chuẩn y tế không?

Không có một ngưỡng ECE phổ quát áp dụng cho mọi mô hình y tế. Nên gọi đây là **ngưỡng mục tiêu thiết kế của nhóm** nếu chưa có nguồn quy định cụ thể.

## 15.4. RAG có loại bỏ hoàn toàn hallucination không?

Không. Chỉ nên nói giảm thiểu, kiểm soát và làm cho nhận định có thể kiểm chứng.

## 15.5. Hai ca bệnh có đủ chứng minh dung hợp không?

Không. Chúng chỉ minh họa lỗi bổ sung. Cần kết quả định lượng của mô hình dung hợp.

## 15.6. Mô hình văn bản có thể học tên bệnh không?

Có nguy cơ. Cần che nhãn trực tiếp, kiểm tra rò rỉ gián tiếp và chia dữ liệu đúng quy trình.

## 15.7. Vì sao chỉ 302 mẫu test?

Đây là đánh giá ban đầu trong phạm vi bộ dữ liệu 2.000 hồ sơ. Nhóm cần thừa nhận cỡ mẫu còn hạn chế và đề xuất bootstrap cùng xác thực ngoài.

## 15.8. Có thể khẳng định công bằng khi dữ liệu cân bằng theo bệnh không?

Không. Cân bằng nhãn bệnh khác với công bằng theo tuổi, giới hoặc nhóm dân số. Cần đánh giá riêng theo từng nhóm.

---

# 16. Từ điển thuật ngữ nhanh

| Thuật ngữ | Cách hiểu ngắn |
|---|---|
| EHR | Hồ sơ sức khỏe điện tử |
| Modality | Một dạng dữ liệu, ví dụ bảng hoặc văn bản |
| Multimodal | Sử dụng nhiều dạng dữ liệu |
| Baseline | Mô hình làm mốc để so sánh |
| Feature | Đặc trưng đầu vào |
| Label | Nhãn cần dự đoán |
| Encoder | Bộ biến dữ liệu thành biểu diễn vector |
| Embedding | Vector biểu diễn ý nghĩa hoặc đặc trưng |
| Transformer | Kiến trúc dùng attention để xử lý quan hệ trong dữ liệu |
| Attention | Cơ chế gán mức quan trọng cho các phần thông tin |
| Cross-attention | Attention giữa hai nguồn biểu diễn khác nhau |
| Fusion | Dung hợp nhiều phương thức |
| Classification Head | Lớp tạo điểm dự đoán cho các lớp |
| Logit | Điểm thô trước khi chuyển thành xác suất |
| Softmax | Hàm chuyển các logit thành phân bố xác suất |
| Calibration | Mức phù hợp giữa độ tin cậy và tỷ lệ đúng thực tế |
| Overconfidence | Mô hình tự tin hơn mức chính xác thực tế |
| Fine-tuning | Điều chỉnh mô hình đã huấn luyện trước cho nhiệm vụ mới |
| Data leakage | Thông tin từ đáp án hoặc test lọt vào quá trình huấn luyện |
| RAG | Sinh câu trả lời có hỗ trợ truy xuất tài liệu |
| Vector Store | Kho lưu vector của các đoạn tài liệu |
| Semantic Retrieval | Tìm kiếm theo ý nghĩa |
| Hallucination | Nội dung mô hình tạo ra nhưng không được bằng chứng hỗ trợ |
| External Validation | Xác thực trên dữ liệu độc lập từ nguồn khác |
| Bootstrap | Lấy mẫu lại để ước lượng độ bất định |
| Confidence Interval | Khoảng tin cậy của một ước lượng |
| Distribution Shift | Phân bố dữ liệu triển khai khác dữ liệu huấn luyện |

---

# 17. Cách ôn tập cho cả nhóm

## Vòng 1 – Hiểu câu chuyện trong 10 phút

Mỗi người phải kể lại được:

1. Nghiên cứu hiện tại bỏ qua văn bản lâm sàng.
2. Nhóm tạo bộ dữ liệu hai phương thức và so sánh ba baseline.
3. Bio_ClinicalBERT tốt nhất về tổng thể.
4. Hai ca bệnh cho thấy mỗi phương thức có điểm mù riêng.
5. Nhóm đề xuất dung hợp và giải thích có bằng chứng.

## Vòng 2 – Nhớ các con số quan trọng

Chỉ cần nhớ chính xác:

- 10.657 công trình được sàng lọc.
- 15 nghiên cứu được đưa vào tổng quan.
- 2.000 hồ sơ.
- Bốn nhóm bệnh.
- 302 mẫu test.
- Bio_ClinicalBERT: Accuracy 85,43%; Macro-F1 0,8421; ECE 3,73%.
- CatBoost: Accuracy 68,54%; ECE 6,63%.
- FT-Transformer: Accuracy 65,89%; ECE 11,52%.

## Vòng 3 – Mỗi người giải thích một khối kỹ thuật

- Người 1: dữ liệu và bốn bệnh.
- Người 2: ba baseline và sáu chỉ số.
- Người 3: dung hợp, calibration và Agentic RAG.

Sau đó đổi vai để bảo đảm mọi thành viên đều trả lời được toàn bộ đề tài.

## Vòng 4 – Phản biện chéo

Một người đóng vai giảng viên và hỏi:

- Dữ liệu được ghép như thế nào?
- Làm sao tránh rò rỉ nhãn?
- Vì sao không chỉ dùng Bio_ClinicalBERT?
- ECE dưới 5% dựa trên tiêu chuẩn nào?
- RAG có thực sự hết hallucination không?
- Hai case study có đủ chứng minh dung hợp không?
- Vì sao FT-Transformer thua CatBoost?
- Mô hình đã dùng được cho bệnh nhân thật chưa?

Người trả lời cần bắt đầu bằng kết luận ngắn, sau đó mới giải thích.

---

# 18. Bài kiểm tra nhanh

## Câu hỏi

1. Vì sao dữ liệu bảng có thể bỏ sót bệnh hen?
2. Vì sao văn bản có thể dự đoán sai trong bệnh cảnh phức tạp?
3. Macro-F1 khác Accuracy ở điểm nào?
4. AUROC cao có bảo đảm ECE thấp không?
5. Temperature Scaling nhằm cải thiện chỉ số nào?
6. Hai ca bệnh đã chứng minh mô hình dung hợp tốt hơn chưa?
7. Vì sao dữ liệu từ Synthea không đủ để xác nhận ứng dụng lâm sàng?
8. RAG có thể thất bại ở những bước nào?
9. Tại sao cần xác thực ngoài?
10. Hệ thống đóng vai trò gì đối với bác sĩ?

## Đáp án ngắn

1. Vì sinh hiệu có thể được đo lúc bệnh ổn định và không phản ánh diễn tiến dài hạn.
2. Vì văn bản chứa nhiễu, bệnh đồng mắc, nhiều thuốc và dấu hiệu không đặc hiệu.
3. Accuracy tính tổng tỷ lệ đúng; Macro-F1 cho mỗi lớp trọng số ngang nhau và kết hợp Precision với Recall.
4. Không. Phân biệt tốt và hiệu chỉnh tốt là hai thuộc tính khác nhau.
5. Calibration, thường được theo dõi bằng ECE, NLL hoặc Brier.
6. Chưa; chúng chỉ tạo luận cứ định tính cho việc thử nghiệm dung hợp.
7. Vì dữ liệu tổng hợp không tái hiện đầy đủ phân bố và độ phức tạp của bệnh viện thật.
8. Truy xuất sai, bỏ sót nguồn, hiểu sai nguồn, sinh kết luận quá mức hoặc gắn trích dẫn không hỗ trợ nhận định.
9. Để kiểm tra mô hình có khái quát sang bệnh viện, thời gian và quần thể khác hay không.
10. Hỗ trợ cung cấp dự đoán và bằng chứng; bác sĩ vẫn quyết định cuối cùng.

---

# 19. Một phút tóm tắt toàn bộ đề tài

> Các nghiên cứu AI y tế hiện tại thường tập trung vào dữ liệu bảng và chưa khai thác đầy đủ ghi chú lâm sàng. Nhóm xây dựng bộ dữ liệu nghiên cứu gồm 2.000 hồ sơ thuộc bốn nhóm bệnh và so sánh ba baseline đơn phương thức. Trên tập test 302 mẫu, Bio_ClinicalBERT sử dụng văn bản cho kết quả tổng thể cao nhất, với Accuracy 85,43%, Macro-F1 0,8421 và ECE 3,73%. Tuy nhiên, hai ca bệnh cho thấy mô hình văn bản vẫn có thể sai khi ngữ cảnh bị nhiễu, trong khi mô hình bảng có thể sai khi sinh hiệu được đo lúc bệnh ổn định. Vì vậy, nhóm đề xuất kiến trúc dung hợp dùng FT-Transformer, Bio_ClinicalBERT và cross-attention late fusion, kết hợp Temperature Scaling để hiệu chỉnh xác suất. Hệ thống giải thích dự kiến sử dụng RAG để gắn dự đoán với bằng chứng từ hồ sơ và hướng dẫn chuyên môn. Đây mới là nguyên mẫu học thuật và cần được xác thực ngoài trước bất kỳ ứng dụng lâm sàng nào.

---

# 20. Ba nguyên tắc cần nhớ khi trả lời phản biện

1. **Không nói quá kết quả:** luôn giới hạn kết luận trong bộ dữ liệu và thí nghiệm hiện tại.
2. **Phân biệt kết quả đã có với định hướng:** baseline đã được đánh giá; kiến trúc dung hợp và Agentic RAG là bước phát triển tiếp theo nếu chưa có kết quả thực nghiệm tương ứng.
3. **Đặt bác sĩ ở vị trí quyết định cuối cùng:** mô hình cung cấp hỗ trợ và bằng chứng, không thay thế chuyên môn lâm sàng.
