# Q&A PHẦN MÔ HÌNH & KẾT QUẢ (THÀNH VIÊN 1)

> Sinh tự động từ `results/registry.json` bằng `scripts/export_qa_member1.py`. Trả lời ≤ 3 câu, có số liệu.

**1. Vì sao cross-attention không vượt BERT fine-tune và ensemble?**

Trên test strict, BERT-FT đạt 0.975 ± 0.004, ensemble 0.978, cross-attention 0.956 ± 0.008 (Δ -0.020, p Holm 0.012). RQ2 cho thấy ghi chú chép lại sinh hiệu và tuổi, nên nhánh văn bản đã chứa gần đủ thông tin; fusion không có gì thêm. Trong grouped CV, cross-attention lại ổn định nhất (0.949 ± 0.016 so với BERT-FT 0.894 ± 0.148) – thứ hạng không bền trên dữ liệu ít bệnh nhân gốc.

**2. Làm sao biết không rò rỉ nhãn?**

Bốn lớp kiểm tra: (1) chia theo nhóm bệnh nhân gốc và nhóm ghi chú nguồn, audit 0 giao nhau; (2) tên chẩn đoán được che ([REDACTED_DIAGNOSIS]) và audit tự động đếm 0% ghi chú còn tên chẩn đoán; (3) audit ghi chú nguồn bị dùng lại mang thông tin nhãn = 0%; (4) RQ2: che mọi con số thì TF-IDF chỉ còn 0.541. Chính các kiểm tra này đã phát hiện và loại bộ dữ liệu trung gian 2026-11-18 (TF-IDF che số đạt 0.962 – dấu hiệu rò rỉ).

**3. ECE là gì, vì sao chưa < 0.05, temperature khớp trên đâu?**

ECE là chênh lệch trung bình giữa độ tin cậy dự đoán và tỷ lệ đúng thực tế theo bin. Temperature scaling khớp trên validation (N=273), giảm ECE từ 0.079 xuống 0.077; vector scaling (0.098) và isotonic (0.094) không tốt hơn. Validation nhỏ và test có phân bố khác validation nên chưa đạt mục tiêu – báo cáo đúng như vậy.

**4. Vì sao AUROC cao mà Macro-F1/accuracy thấp?**

AUROC đo khả năng xếp hạng ở mọi ngưỡng; F1 dùng argmax tại một ngưỡng. Cross-attention: AUROC 0.956 nhưng F1 0.691 vì lỗi tập trung ở một bệnh nhân viêm phổi gốc (42/62 lỗi) bị đoán thành hen do lối tắt tuổi.

**5. Mô hình chỉ dùng dữ liệu bảng đơn giản có tốt không?**

Logistic Regression đạt 0.945, không khác cross-attention (p Holm 0.456). Trên dữ liệu này, mô hình đơn giản là baseline rất mạnh.

**6. Dữ liệu có đủ lớn không?**

2.000 bản ghi nhưng chỉ 478 bệnh nhân Synthea gốc; tập test có 62 bệnh nhân gốc, trong đó suy tim và viêm phổi mỗi lớp 1 bệnh nhân. CI bootstrap theo bản ghi vì vậy hẹp hơn độ bất định thực; đây là giới hạn lớn nhất của nghiên cứu.

**7. Nếu có MIMIC-IV, kỳ vọng thay đổi thế nào?**

Ghi chú thật chứa mô tả triệu chứng, bệnh sử, đáp ứng điều trị không có trong dữ liệu bảng – đúng điều kiện RQ3 cho thấy cross-attention có lợi. Kỳ vọng hiệu năng tuyệt đối thấp hơn (không còn lối tắt tuổi/bệnh nhân lặp lại) nhưng đóng góp của văn bản thật sự đo được. Cần tái kiểm tra RQ2 (che số) trên dữ liệu đó.

**8. Checkpoint triển khai được chọn thế nào, có cherry-pick không?**

Quy tắc đăng ký trước: cross-attention BERT đóng băng, seed có NLL validation thấp nhất (seed 101); chọn trước khi xem test. Hash kế hoạch phân tích được đóng băng tại results/preregistration/.
