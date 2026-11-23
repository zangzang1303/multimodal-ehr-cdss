# BỘ CÂU HỎI & TRẢ LỜI BẢO VỆ ĐỀ TÀI (Q&A DEFENSE)
## CHUYÊN ĐỀ: DỮ LIỆU LÂM SÀNG, BẢO MẬT PHI & Y ĐỨC NGHIÊN CỨU
### Phụ trách: Thành viên 2 (Biomedical Data Engineer & Privacy)

---

### Câu 1: Dữ liệu của đề tài có phải là dữ liệu thật từ bệnh nhân không?
> **Trả lời ngắn (Súc tích, số liệu & chuẩn TRIPOD-AI):**  
> "Thưa Hội đồng, đoàn hệ nghiên cứu là **dữ liệu bán tổng hợp (semi-synthetic cohort)** gồm đúng $2.000$ hồ sơ: các đặc trưng dạng bảng (nhân khẩu, 6 sinh hiệu, xét nghiệm và tiền sử) được trích xuất từ bộ sinh bệnh nhân sinh lý học **Synthea EHR**, còn văn bản lâm sàng là các đoạn trích bệnh sử thực tế từ kho **MTSamples** được ghép nối có chọn lọc. Trong văn bản có chèn lại khối sinh hiệu lúc tiếp nhận và các thông tin định danh (PHI) giả lập để kiểm thử kỹ thuật. Nhóm nghiên cứu hoàn toàn minh bạch bản chất bán tổng hợp này theo chuẩn quốc tế TRIPOD+AI và PROBAST+AI, chủ động tự chấm mức **High Risk ở miền Participants và Outcome** thay vì ngụy tạo đây là dữ liệu bệnh nhân thực."

---

### Câu 2: Vì sao nhóm không thu thập và sử dụng dữ liệu bệnh án thực tế tại các bệnh viện Việt Nam?
> **Trả lời ngắn (Khía cạnh pháp lý & ranh giới y đức):**  
> "Thưa Hội đồng, theo **Nghị định 13/2023/NĐ-CP** về Bảo vệ dữ liệu cá nhân và **Luật Khám bệnh, chữa bệnh số 15/2023/QH15**, việc khai thác hồ sơ bệnh án điện tử tại bệnh viện phục vụ huấn luyện AI bắt buộc phải trải qua Đánh giá tác động xử lý dữ liệu cá nhân (DPIA) và được phê duyệt chính thức bằng văn bản của **Hội đồng Đạo đức trong Nghiên cứu Y sinh học (IRB)**. Trong phạm vi một đề tài tiền lâm sàng nhằm hoàn thiện phương pháp luận và kiến trúc phần mềm, việc sử dụng dữ liệu bán tổng hợp là lựa chọn liêm chính, an toàn tuyệt đối về mặt pháp lý và đạo đức, giúp nhóm đóng băng và kiểm định toàn diện pipeline trước khi bước vào quy trình xin cấp phép thử nghiệm trên bệnh nhân thực tế."

---

### Câu 3: Quy trình khử định danh (De-identification) được thực hiện và đánh giá như thế nào?
> **Trả lời ngắn (Kỹ thuật lai ghép, tỷ lệ trước/sau & kiểm thử âm tính):**  
> "Thưa Hội đồng, module `ClinicalDeidentifier` kết hợp Biểu thức chính quy nâng cao và mô hình Biomedical NER theo chuẩn **HIPAA Safe Harbor 18 yếu tố**. Để đánh giá thực nghiệm, nhóm đã cài cắm có chủ đích các định danh giả lập đặc thù Việt Nam vào toàn bộ 2.000 hồ sơ. Đợt kiểm toán Backlog 08 cho thấy hệ thống đã đưa tỷ lệ rò rỉ còn sót từ $72\% - 100\%$ (mã thẻ BHYT dạng `DN4...`, học hàm/học vị bác sĩ `PGS.TS.`, `BS.CKII.`, tên bệnh viện viết HOA) về **chính xác $0,0\%$ (0/2.000)** sau cải tiến. Đặc biệt, bộ kiểm thử âm tính tự động xác nhận **bảo toàn $100\%$ các chỉ số sinh hiệu** viết tắt (`BP`, `HR`, `SpO2`, `WBC`, `CRP`) mà không bị che nhầm."

---

### Câu 4: Việc đánh giá tính công bằng (Fairness) có ý nghĩa gì khi thực hiện trên một bộ dữ liệu tổng hợp?
> **Trả lời ngắn (Kiểm toán thuật toán & tính sẵn sàng triển khai):**  
> "Thưa Hội đồng, đánh giá công bằng trên dữ liệu bán tổng hợp không nhằm phản ánh bất bình đẳng xã hội trên quần thể thực, mà là một **phép kiểm toán thuật toán (algorithmic fairness audit)** bắt buộc theo TRIPOD+AI Mục 12: nhằm chứng minh rằng hàm mất mát và cơ chế Cross-Attention không tự phát sinh thiên lệch nội tại bất thường giữa các nhóm nhân khẩu học. Kết quả kiểm định trên 7 phân nhóm (Nam AUROC $0,9645$ vs Nữ $0,9749$; Tuổi $<65$ AUROC $0,9829$ vs $\ge 65$ AUROC $0,9587$; Hút thuốc AUROC $0,9587 - 0,9806$) chứng minh pipeline xử lý ổn định, không làm suy thoái hiệu năng trên các nhóm yếu thế, đảm bảo tính sẵn sàng kỹ thuật trước khi nạp dữ liệu lâm sàng thực tế."

---

### Câu 5: Nhóm có kế hoạch ngoại kiểm độc lập và xin phê duyệt đạo đức (IRB) như thế nào trong tương lai?
> **Trả lời ngắn (Lộ trình 2 giai đoạn: MIMIC-IV & Bệnh viện đối tác):**  
> "Thưa Hội đồng, nhóm đã xây dựng lộ trình mở rộng gồm 2 giai đoạn:  
> 1. **Ngoại kiểm trên cơ sở dữ liệu mở MIMIC-IV (Hoa Kỳ):** Các thành viên đã hoàn thành chứng chỉ CITI (*Data or Specimens Only Research*) và ký thỏa thuận DUA trên PhysioNet để trích xuất 4 mã ICD-10 tương đương (Asthma `J45`, COPD `J44`, Heart Failure `I50`, Pneumonia `J18`), thực hiện kiểm định Zero-shot Transportability mà không huấn luyện lại mô hình.  
> 2. **Ngoại kiểm lâm sàng tại Việt Nam:** Nhóm đã hoàn thiện đề cương nghiên cứu hồi cứu đa trung tâm, dự kiến nộp Hội đồng Đạo đức (IRB) tại bệnh viện đối tác để thu thập tối thiểu 1.000 hồ sơ thật, áp dụng giao thức khảo sát chuyên gia đã thiết kế sẵn (đảm bảo $\ge 2$ bác sĩ độc lập, độ đồng thuận Fleiss' $\kappa \ge 0,75$) và thử nghiệm ở chế độ ngầm (*Silent-mode*) trước khi hỗ trợ lâm sàng chính thức."

---

### TÓM TẮT THÔNG ĐIỆP CỐT LÕI (CORE TAKEAWAY KHI BẢO VỆ)
> "M-CDSS không cố gắng ngụy tạo một mô hình hoàn hảo trên dữ liệu giả, mà là một công trình tiên phong về **liêm chính học thuật và kỷ luật phương pháp luận**: nhận diện đúng hiện tượng dư thừa phương thức (RQ2), thực hiện khử định danh triệt để $0\%$ sót, áp dụng nghiêm ngặt khóa chuỗi thời gian chống rò rỉ, và phân định trung thực theo chuẩn quốc tế PROBAST+AI."
