# Giải thích các chỉ số đánh giá mô hình phân loại

Tài liệu này giải thích các chỉ số **AUROC (M), AUPRC (M), Macro-F1, Accuracy, Brier** và **ECE (%)** theo cách dễ hiểu, dễ nhớ, kèm ví dụ trong bối cảnh dự đoán bệnh.

## Ví dụ chung

Giả sử mô hình dự đoán bệnh tim cho **1.000 bệnh nhân**:

- 50 người thật sự mắc bệnh.
- 950 người không mắc bệnh.
- Mô hình trả về xác suất, ví dụ `0,90` nghĩa là nguy cơ mắc bệnh 90%.
- Nếu chọn ngưỡng `0,50`, xác suất từ 0,50 trở lên được coi là “có bệnh”.

Tại ngưỡng 0,50, giả sử kết quả là:

| Kết quả dự đoán | Thực sự có bệnh | Thực sự không bệnh |
|---|---:|---:|
| Dự đoán có bệnh | TP = 40 | FP = 20 |
| Dự đoán không bệnh | FN = 10 | TN = 930 |

Trong đó:

| Ký hiệu | Tên | Ý nghĩa |
|---|---|---|
| **TP** | True Positive | Có bệnh và mô hình dự đoán có bệnh |
| **FP** | False Positive | Không bệnh nhưng mô hình báo có bệnh |
| **FN** | False Negative | Có bệnh nhưng mô hình bỏ sót |
| **TN** | True Negative | Không bệnh và mô hình dự đoán không bệnh |

---

## 1. AUROC (M)

### AUROC đo điều gì?

AUROC đo khả năng mô hình **xếp bệnh nhân mắc bệnh ở mức nguy cơ cao hơn bệnh nhân không mắc bệnh**.

Nói đơn giản:

> Nếu lấy ngẫu nhiên một người có bệnh và một người không bệnh, mô hình có cho người có bệnh điểm nguy cơ cao hơn không?

Ví dụ:

- Bệnh nhân A thật sự có bệnh: mô hình dự đoán 85%.
- Bệnh nhân B không có bệnh: mô hình dự đoán 20%.

Mô hình đã xếp đúng vì 85% cao hơn 20%.

Nếu `AUROC = 0,90`, có thể hiểu gần đúng rằng:

> Trong 90% các cặp gồm một người có bệnh và một người không bệnh, mô hình xếp người có bệnh ở mức nguy cơ cao hơn.

### Cách đọc AUROC

| AUROC | Cách hiểu tương đối |
|---:|---|
| 0,50 | Gần giống đoán ngẫu nhiên |
| 0,60–0,70 | Khả năng phân biệt còn yếu |
| 0,70–0,80 | Khá |
| 0,80–0,90 | Tốt |
| 0,90–1,00 | Rất tốt |
| 1,00 | Phân biệt hoàn hảo |

Các mức trên chỉ mang tính tham khảo. Trong y tế, mức chấp nhận được còn phụ thuộc loại bệnh, mục đích sử dụng và hậu quả của việc bỏ sót hoặc báo nhầm.

### Tại sao gọi là diện tích dưới đường cong?

Khi thay đổi ngưỡng dự đoán từ 0 đến 1, ta nhận được nhiều cặp giá trị:

- **Sensitivity/Recall:** tìm được bao nhiêu người thật sự mắc bệnh.
- **False Positive Rate:** báo nhầm bao nhiêu người không mắc bệnh.

Đường ROC biểu diễn sự đánh đổi giữa hai đại lượng trên. AUROC là diện tích nằm dưới đường ROC.

### AUROC không cho biết điều gì?

AUROC cao không nhất thiết có nghĩa rằng:

- Xác suất 90% thật sự tương ứng với nguy cơ 90%.
- Mô hình có Precision cao.
- Ngưỡng 0,50 là ngưỡng tốt nhất.
- Mô hình hoạt động tốt trên dữ liệu cực kỳ mất cân bằng.

Ví dụ, nếu chỉ có 5 người mắc bệnh trong 10.000 người, mô hình vẫn có thể đạt AUROC cao nhưng tạo ra rất nhiều cảnh báo giả.

### Cách nhớ

> **AUROC = Mô hình có xếp đúng người nguy cơ cao hay không?**

---

## 2. AUPRC (M)

### AUPRC đo điều gì?

AUPRC đo sự đánh đổi giữa **Precision** và **Recall**:

- **Precision:** trong những người mô hình báo có bệnh, bao nhiêu người thật sự có bệnh?
- **Recall:** trong những người thật sự có bệnh, mô hình tìm ra được bao nhiêu người?

### Precision

$$
Precision = \frac{TP}{TP + FP}
$$

Với ví dụ chung:

$$
Precision = \frac{40}{40 + 20} = 66,7\%
$$

Nghĩa là trong 60 người được cảnh báo, khoảng 67% thật sự mắc bệnh.

### Recall

$$
Recall = \frac{TP}{TP + FN}
$$

Với ví dụ chung:

$$
Recall = \frac{40}{40 + 10} = 80\%
$$

Nghĩa là mô hình tìm thấy 80% số người thật sự mắc bệnh và bỏ sót 20%.

### AUPRC được tạo ra như thế nào?

Khi thay đổi ngưỡng dự đoán:

- **Ngưỡng cao**, ví dụ 0,90: mô hình chỉ cảnh báo những trường hợp rất chắc chắn. Precision thường cao nhưng có thể bỏ sót nhiều người, khiến Recall thấp.
- **Ngưỡng thấp**, ví dụ 0,20: mô hình phát hiện được nhiều ca bệnh hơn, Recall tăng, nhưng cảnh báo nhầm cũng tăng và Precision có thể giảm.

Đường Precision–Recall thể hiện sự đánh đổi này. AUPRC là diện tích dưới đường Precision–Recall.

### Tại sao AUPRC quan trọng với dữ liệu mất cân bằng?

Giả sử trong 1.000 bệnh nhân chỉ có 50 người mắc bệnh, tức tỷ lệ bệnh là 5%. Một mô hình ngẫu nhiên có mức AUPRC cơ sở khoảng 0,05.

Vì vậy:

- `AUPRC = 0,10` đã cao gấp đôi tỷ lệ nền.
- `AUPRC = 0,60` là kết quả khá mạnh trong bối cảnh này.

AUPRC nên được so sánh với **tỷ lệ lớp dương tính**, không nên luôn diễn giải theo cùng một thang như AUROC.

### AUROC và AUPRC khác nhau thế nào?

- **AUROC:** mô hình có xếp ca bệnh cao hơn ca không bệnh không?
- **AUPRC:** khi mô hình đi tìm ca bệnh, kết quả tìm được có chính xác và đầy đủ không?

Trong bài toán bệnh hiếm:

- AUROC có thể đạt 0,90 và trông rất tốt.
- AUPRC có thể chỉ đạt 0,25, cho thấy danh sách dự đoán dương tính vẫn chứa nhiều cảnh báo giả.

### Cách nhớ

> **AUPRC = Danh sách cảnh báo có vừa đúng, vừa đủ không?**

- **Đúng** tương ứng với Precision.
- **Đủ** tương ứng với Recall.

---

## 3. Macro-F1

### F1-score đo điều gì?

F1 kết hợp Precision và Recall thành một giá trị:

$$
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
$$

Với `Precision = 66,7%` và `Recall = 80%`:

$$
F1 \approx 72,7\%
$$

F1 chỉ cao khi **cả Precision và Recall đều tương đối cao**.

| Precision | Recall | F1 gần đúng | Nhận xét |
|---:|---:|---:|---|
| 90% | 90% | 90% | Cả hai đều tốt |
| 90% | 20% | 33% | Ít báo nhầm nhưng bỏ sót nhiều |
| 20% | 90% | 33% | Tìm được nhiều ca bệnh nhưng báo nhầm nhiều |
| 60% | 60% | 60% | Hai mặt đều ở mức trung bình |

### Tại sao không lấy trung bình thông thường?

Nếu Precision là 100% nhưng Recall là 0%, trung bình cộng bằng 50% và nghe có vẻ không quá tệ. Tuy nhiên, Recall bằng 0% nghĩa là mô hình không tìm được ca bệnh nào.

F1 sử dụng **trung bình điều hòa**, nên phạt mạnh khi một trong hai thành phần quá thấp.

### “Macro” nghĩa là gì?

Giả sử mô hình phân loại ba bệnh:

| Lớp bệnh | Số bệnh nhân | F1 |
|---|---:|---:|
| Tiểu đường | 800 | 0,90 |
| Suy tim | 150 | 0,70 |
| Bệnh hiếm | 50 | 0,20 |

Macro-F1 là:

$$
Macro\text{-}F1 = \frac{0,90 + 0,70 + 0,20}{3} = 0,60
$$

Mỗi bệnh có trọng số như nhau, bất kể có 800 hay 50 bệnh nhân. Nhờ đó, Macro-F1 giúp phát hiện trường hợp mô hình rất tốt với bệnh phổ biến nhưng gần như thất bại với bệnh hiếm.

### Điểm cần chú ý

F1 phụ thuộc vào ngưỡng phân loại. Nếu đổi ngưỡng từ 0,50 xuống 0,30:

- Recall có thể tăng.
- Precision có thể giảm.
- F1 có thể tăng hoặc giảm.

Do đó, khi báo cáo F1 nên nói rõ ngưỡng được lựa chọn như thế nào.

F1 cũng không sử dụng TN trực tiếp, nên nó tập trung vào khả năng phát hiện lớp dương tính hơn là tổng số dự đoán đúng.

### Cách nhớ

> **F1 = Cảnh báo vừa đúng, vừa không bỏ sót.**

> **Macro-F1 = Chấm điểm từng bệnh, sau đó cho mỗi bệnh một lá phiếu ngang nhau.**

---

## 4. Accuracy

### Accuracy đo điều gì?

Accuracy là tỷ lệ dự đoán đúng trên toàn bộ dữ liệu:

$$
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
$$

Với ví dụ chung:

$$
Accuracy = \frac{40 + 930}{1000} = 97\%
$$

Mô hình dự đoán đúng 970 trong 1.000 bệnh nhân.

### Tại sao Accuracy có thể gây hiểu nhầm?

Trong 1.000 bệnh nhân chỉ có 50 người mắc bệnh. Giả sử một mô hình luôn nói rằng không ai mắc bệnh:

- Dự đoán đúng 950 người không bệnh.
- Bỏ sót toàn bộ 50 người mắc bệnh.
- Accuracy vẫn bằng 95%.

Mô hình có Accuracy 95% nhưng vô dụng trong việc phát hiện bệnh. Đây là vấn đề thường gặp khi dữ liệu **mất cân bằng lớp**.

### Khi nào Accuracy hữu ích?

Accuracy dễ hiểu và hữu ích khi:

- Các lớp tương đối cân bằng.
- Chi phí của các loại sai lầm gần giống nhau.
- Dự đoán sai ca bệnh và sai ca không bệnh có mức nghiêm trọng tương đương.

Trong y tế, các điều kiện này thường không hoàn toàn đúng. Bỏ sót một bệnh nhân nguy hiểm có thể nghiêm trọng hơn việc yêu cầu một người khỏe mạnh làm thêm xét nghiệm.

### Cách nhớ

> **Accuracy = Tổng cộng mô hình làm đúng bao nhiêu câu?**

Nhưng cần hỏi thêm:

> **Mô hình có phải chỉ làm tốt ở lớp chiếm đa số không?**

---

## 5. Brier score

### Brier đo điều gì?

Brier score đo mức sai lệch giữa:

- Xác suất mô hình dự đoán.
- Kết quả thật: có bệnh bằng 1, không bệnh bằng 0.

Với bài toán nhị phân:

$$
Brier = \frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2
$$

Trong đó:

- $p_i$ là xác suất mô hình dự đoán.
- $y_i$ là kết quả thật, bằng 0 hoặc 1.

### Ví dụ cho một bệnh nhân có bệnh

Kết quả thật là 1.

Nếu mô hình dự đoán 90%:

$$
(0,90-1)^2=0,01
$$

Sai số nhỏ vì mô hình tự tin và đúng.

Nếu mô hình dự đoán 60%:

$$
(0,60-1)^2=0,16
$$

Nếu mô hình dự đoán 10%:

$$
(0,10-1)^2=0,81
$$

Sai số rất lớn vì mô hình tự tin nhưng sai.

### Ví dụ cho một bệnh nhân không bệnh

Kết quả thật là 0.

- Nếu mô hình dự đoán nguy cơ 10%: $(0,10-0)^2=0,01$.
- Nếu mô hình dự đoán nguy cơ 90%: $(0,90-0)^2=0,81$.

Brier phạt đặc biệt mạnh những dự đoán **rất tự tin nhưng sai**.

### Cách đọc

- Brier càng thấp càng tốt.
- Giá trị hoàn hảo là 0.
- Với bài toán nhị phân, Brier nằm trong khoảng từ 0 đến 1.
- Nên so sánh Brier với một mô hình cơ sở, không nên chỉ nhìn vào giá trị riêng lẻ.

Ví dụ, nếu tỷ lệ mắc bệnh là 5%, mô hình luôn dự đoán 5% cho mọi bệnh nhân có thể có Brier tương đối thấp dù không phân biệt được bệnh nhân nào nguy hiểm hơn.

### Brier khác AUROC như thế nào?

Giả sử:

- Người có bệnh được dự đoán 51%.
- Người không bệnh được dự đoán 49%.

Mô hình xếp đúng thứ tự, nên có lợi cho AUROC. Tuy nhiên, khoảng cách phân biệt còn rất yếu.

Nếu dự đoán thay đổi thành:

- Người có bệnh: 99%.
- Người không bệnh: 1%.

Thứ tự xếp hạng vẫn giống nhau, nhưng xác suất tốt hơn rất nhiều. Brier sẽ phản ánh sự khác biệt này rõ hơn.

### Cách nhớ

> **Brier = Xác suất dự đoán cách sự thật bao xa?**

> **Brier càng thấp càng tốt.**

---

## 6. ECE (%)

ECE là viết tắt của **Expected Calibration Error**, nghĩa là sai số hiệu chỉnh xác suất kỳ vọng.

### Calibration là gì?

Một mô hình được hiệu chỉnh tốt nếu:

> Trong những trường hợp được dự đoán có 70% nguy cơ, khoảng 70% thật sự xảy ra bệnh.

Ví dụ, có 100 bệnh nhân được dự đoán nguy cơ khoảng 80%:

- Nếu khoảng 80 người thật sự mắc bệnh, mô hình được hiệu chỉnh tốt.
- Nếu chỉ 40 người mắc bệnh, mô hình quá tự tin.
- Nếu 95 người mắc bệnh, mô hình đánh giá nguy cơ quá thấp.

### ECE được tính như thế nào?

Các dự đoán thường được chia thành các nhóm xác suất, ví dụ:

- 0–10%
- 10–20%
- ...
- 90–100%

Trong mỗi nhóm, ta so sánh:

1. Xác suất trung bình mô hình dự đoán.
2. Tỷ lệ bệnh thực tế.

Ví dụ:

| Nhóm | Xác suất dự đoán trung bình | Tỷ lệ mắc bệnh thực tế | Độ lệch |
|---|---:|---:|---:|
| Nguy cơ thấp | 10% | 8% | 2% |
| Nguy cơ vừa | 50% | 40% | 10% |
| Nguy cơ cao | 80% | 60% | 20% |

ECE lấy trung bình có trọng số của các độ lệch này.

Nếu `ECE = 6%`, có thể hiểu gần đúng rằng:

> Trung bình, độ tin cậy dự đoán lệch khoảng 6 điểm phần trăm so với tần suất thực tế.

### Cách đọc

- `ECE = 0%`: hiệu chỉnh hoàn hảo theo cách chia nhóm đang sử dụng.
- ECE càng thấp càng tốt.
- `ECE = 3%` thường tốt hơn `ECE = 12%` nếu được tính trên cùng dữ liệu và cùng phương pháp.

### Hạn chế của ECE

ECE phụ thuộc vào:

- Số lượng nhóm xác suất.
- Cách chia nhóm.
- Kích thước tập kiểm tra.
- Lớp được đánh giá.
- Cách mở rộng cho bài toán nhiều lớp.

Hai nghiên cứu có thể báo cáo ECE khác nhau dù dùng cùng dự đoán nếu cách chia nhóm khác nhau.

ECE thấp cũng không đảm bảo mô hình phân biệt tốt. Ví dụ, mô hình dự đoán 5% cho tất cả bệnh nhân trong quần thể có tỷ lệ bệnh 5% có thể được hiệu chỉnh tốt, nhưng không biết bệnh nhân nào nguy hiểm hơn.

### Cách nhớ

> **ECE = Mô hình nói 80% thì thực tế có xảy ra gần 80% không?**

> **ECE càng thấp càng tốt.**

---

## 7. “M” trong AUROC (M) và AUPRC (M) là gì?

Trong bảng kết quả nhiều lớp hoặc nhiều nhãn, **M thường có nghĩa là Macro-average**.

Cách tính:

1. Tính AUROC hoặc AUPRC riêng cho từng bệnh.
2. Cộng các kết quả lại.
3. Chia cho số bệnh.

Ví dụ:

| Bệnh | AUROC |
|---|---:|
| Tiểu đường | 0,90 |
| Suy tim | 0,80 |
| Bệnh hiếm | 0,60 |

$$
AUROC(M)=\frac{0,90+0,80+0,60}{3}=0,767
$$

Bệnh hiếm và bệnh phổ biến có trọng số bằng nhau.

Tuy nhiên, ký hiệu **M không hoàn toàn thống nhất** giữa các bài báo. Đôi khi M có thể mang nghĩa “Mean”. Cần kiểm tra chú thích bảng hoặc phần phương pháp để xác nhận. Trong nhiều trường hợp, “mean” cũng là trung bình trên các lớp hoặc trên nhiều lần chạy.

---

## 8. So sánh bằng một tình huống dễ nhớ

Hãy tưởng tượng mô hình tạo một danh sách bệnh nhân cần bác sĩ kiểm tra:

- **AUROC:** người bệnh có được xếp gần đầu danh sách hơn người không bệnh không?
- **AUPRC:** danh sách cảnh báo có ít người bị báo nhầm và vẫn tìm đủ người bệnh không?
- **Macro-F1:** mô hình có làm tốt đồng đều cho từng loại bệnh không?
- **Accuracy:** trong toàn bộ bệnh nhân, mô hình kết luận đúng bao nhiêu người?
- **Brier:** các con số 10%, 60% và 90% cách kết quả thật bao xa?
- **ECE:** khi mô hình nói 80%, thực tế có xảy ra khoảng 80% không?

## 9. Hướng tốt của từng chỉ số

| Chỉ số | Hướng tốt nhất | Giá trị hoàn hảo |
|---|---|---:|
| AUROC (M) | Càng cao càng tốt | 1,00 |
| AUPRC (M) | Càng cao càng tốt | 1,00 |
| Macro-F1 | Càng cao càng tốt | 1,00 |
| Accuracy | Càng cao càng tốt | 1,00 hoặc 100% |
| Brier | Càng thấp càng tốt | 0 |
| ECE | Càng thấp càng tốt | 0% |

## 10. Không nên chọn mô hình chỉ bằng một chỉ số

Ví dụ:

| Mô hình | AUROC | AUPRC | Macro-F1 | Accuracy | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|
| A | 0,92 | 0,55 | 0,60 | 96% | 0,08 | 12% |
| B | 0,89 | 0,61 | 0,66 | 95% | 0,06 | 4% |

Mô hình A có AUROC và Accuracy cao hơn. Tuy nhiên, mô hình B:

- Có AUPRC cao hơn, nên phát hiện lớp dương tính hiệu quả hơn.
- Có Macro-F1 cao hơn, nên cân bằng giữa các lớp tốt hơn.
- Có Brier và ECE thấp hơn, nên xác suất dự đoán đáng tin hơn.

Trong một hệ thống hỗ trợ quyết định lâm sàng, mô hình B có thể hữu ích hơn dù Accuracy và AUROC thấp hơn một chút.

Lựa chọn cuối cùng phụ thuộc vào mục tiêu:

- **Sàng lọc bệnh nguy hiểm:** ưu tiên Recall cao để hạn chế bỏ sót.
- **Tránh xét nghiệm không cần thiết:** ưu tiên Precision.
- **Ước lượng nguy cơ để hỗ trợ điều trị:** chú trọng Brier và ECE.
- **Dự đoán nhiều bệnh, bao gồm bệnh hiếm:** chú trọng Macro-F1 và macro-AUPRC.

## 11. Bảng ghi nhớ nhanh

| Chỉ số | Câu hỏi dễ nhớ | Hướng tốt |
|---|---|---|
| **AUROC** | Có xếp người bệnh cao hơn người không bệnh không? | Cao |
| **AUPRC** | Danh sách cảnh báo có vừa đúng vừa đủ không? | Cao |
| **Macro-F1** | Có làm tốt đồng đều trên từng loại bệnh không? | Cao |
| **Accuracy** | Tổng cộng dự đoán đúng bao nhiêu? | Cao |
| **Brier** | Xác suất dự đoán cách sự thật bao xa? | Thấp |
| **ECE** | Nói 80% thì thực tế có gần 80% không? | Thấp |
