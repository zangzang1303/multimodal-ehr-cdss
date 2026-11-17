# BÁO CÁO KIỂM TOÁN BẢO MẬT PHI, THÔNG TIN NHẠY CẢM VÀ GIẤY PHÉP BẢN QUYỀN
### M-CDSS Phase 2 / Backlog 07 - Nhiệm vụ 2.3 (Data Engineer & Biomedical Privacy)
**Ngày thực hiện kiểm toán:** 17/11/2026  
**Phạm vi kiểm toán:** Toàn bộ kho mã nguồn (`src/`), tệp cấu hình (`configs/`), kịch bản kiểm thử (`tests/`), scripts thực thi (`scripts/`), dữ liệu mẫu (`data/`), và lịch sử Git commit.  
**Công cụ kiểm toán:** `scripts/audit_phi_and_secrets.py`, Git history scanner, Regex Pattern Matcher (HIPAA Safe Harbor 18 yếu tố định danh).

---

## 1. KHẢO SÁT VÀ PHƯƠNG PHÁP LUẬN KIỂM TOÁN (AUDIT METHODOLOGY)

Quy trình kiểm toán bảo mật thông tin sức khỏe được bảo vệ (Protected Health Information - PHI) và thông tin định danh cá nhân (Personally Identifiable Information - PII) được tiến hành theo 3 cấp độ:
1. **Quét mẫu nhận dạng mật khẩu và khóa bí mật (Secret Scanner):** Quét phát hiện khóa API (OpenAI, HuggingFace, AWS), khóa bảo mật RSA/EC private keys, mật khẩu cứng (hardcoded passwords) trong mã nguồn và tệp cấu hình.
2. **Quét mẫu định danh y sinh học (HIPAA Safe-Harbor PHI Scanner):** Quét 18 trường định danh cá nhân bao gồm: Số Căn cước công dân/CMND (12 chữ số), Số điện thoại di động Việt Nam, Địa chỉ email cá nhân, Tên bệnh nhân/bác sĩ, Mã bệnh án (MRN), Số thẻ BHYT.
3. **Kiểm toán lịch sử Git (Git History & Diff Audit):** Rà soát các commit trong lịch sử kho lưu trữ để ngăn chặn nguy cơ rò rỉ secret hoặc PHI đã từng bị commit trong quá khứ.

---

## 2. KẾT QUẢ KIỂM TOÁN VÀ GIẢI TRÌNH XỬ LÝ (AUDIT FINDINGS & REMEDIATION)

### 2.1. Kiểm Toán Khóa Bí Mật & Thông Tin Xác Thực (Secrets & Credentials)
* **Số lượng tệp quét:** $215$ tệp tin văn bản trong toàn kho.
* **Số phát hiện trong `src/` và `configs/`:** **$0$ phát hiện (Tuyệt đối không có secret cứng).**
* **Tệp cấu hình môi trường:** Tệp `.env.example` chỉ chứa các giá trị cổng mặc định và URL dịch vụ cục bộ (`FRONTEND_PORT=3000`, `API_PORT=8000`, `QDRANT_HTTP_PORT=6333`). Không lưu trữ API token thương mại hoặc secret database.
* **Lịch sử Git commit:** **$0$ cảnh báo rò rỉ khóa bí mật.** Tệp `.gitignore` được cấu hình nghiêm ngặt loại trừ `.env`, `.env.local`, `*.log`, `.pem`.

### 2.2. Kiểm Toán Dữ Liệu Bệnh Nhân (PHI / PII Audit)
* **Mã nguồn ứng dụng (`src/`):** **$0$ phát hiện dữ liệu bệnh nhân thực tế.** Toàn bộ quy trình tiền xử lý sử dụng token thay thế tiêu chuẩn (`[REDACTED_NAME]`, `[REDACTED_PHONE]`, `[REDACTED_DATE]`, `[REDACTED_HOSPITAL]`, `[REDACTED_ID]`).
* **Tập dữ liệu thô sinh thử nghiệm (`data/raw/`):**
  - Ghi nhận 2.000 dòng chứa các chuỗi số điện thoại và CCCD giả định được sinh bởi `scripts/generate_synthetic_ehr.py`.
  - *Giải trình xử lý:* Đây là bộ dữ liệu thử nghiệm nhân tạo (Synthetic Test Fixtures) được cố tình tạo ra để kiểm thử năng lực làm sạch của `ClinicalDeidentifier`. Toàn bộ thư mục `data/raw/*` đã được loại trừ khỏi kho lưu trữ qua `.gitignore` và không bao giờ được đưa lên Git.
* **Tập dữ liệu đã xử lý (`data/processed/`, `data/processed_rebuilt_strict/`):**
  - Toàn bộ văn bản bệnh án đã được khử định danh 100% qua pipeline `ClinicalDeidentifier`. Các tệp `.parquet` được bảo vệ và loại trừ bởi `.gitignore`.
* **Kịch bản kiểm thử (`tests/test_data_pipeline.py`):**
  - Ghi nhận 5 chuỗi số điện thoại mẫu (ví dụ: `0912345678`) nằm trong các mệnh đề `assert deid.deidentify_text(...) == "[REDACTED_PHONE]"`. Đây là các ca kiểm thử đơn vị hợp lệ nhằm thẩm định độ chính xác của biểu thức chính quy.

---

## 3. HOÀN THIỆN DATA DICTIONARY (TỪ ĐIỂN DỮ LIỆU ĐA PHƯƠNG THỨC)

Toàn bộ hợp đồng dữ liệu được đặc tả chi tiết tại tài liệu chuyên môn [`docs/DATA_DICTIONARY.md`](DATA_DICTIONARY.md), định nghĩa đầy đủ:
- $9$ biến số sinh hiệu và cận lâm sàng liên tục: đơn vị đo chuẩn, khoảng giá trị sinh lý hợp lệ, tỷ lệ khuyết thiếu thực nghiệm (WBC khuyết 20.5\%, CRP khuyết 22.4\%) và phương pháp gán MICE.
- $4$ biến phân loại nhân khẩu học và tiền sử bệnh nền.
- $2$ biến nhị phân chỉ báo khuyết thiếu (`wbc_missing`, `crp_missing`).
- Cấu trúc văn bản ghi chú bệnh án tự do và $4$ nhóm nhãn chẩn đoán mục tiêu.

---

## 4. MA TRẬN GIẤY PHÉP BẢN QUYỀN (MULTI-TIERED LICENSING ARCHITECTURE)

Nhằm tuân thủ quyền sở hữu trí tuệ và điều kiện cấp phép của từng thành phần phần mềm, nghiên cứu thiết lập cấu trúc giấy phép phân tầng rõ ràng:

| Thành Phần Hệ Thống | Bản Quyền & Nguồn Gốc | Giấy Phép Áp Dụng (License) | Phạm Vi Sử Dụng Hợp Pháp |
| :--- | :--- | :---: | :--- |
| **Mã Nguồn M-CDSS** | Nhóm tác giả dự án M-CDSS | **MIT License** | Tự do sử dụng, chỉnh sửa và phân phối cho mục đích học thuật và nghiên cứu y tế. |
| **Mô hình Bio\_ClinicalBERT** | Emily Alsentzer et al. (MIT / Beth Israel Deaconess) | **Apache 2.0 / PhysioNet Credentialed** | Sử dụng nghiên cứu NLP y sinh theo điều ước PhysioNet Credentialed Access. |
| **Mô hình all-mpnet-base-v2** | Microsoft / HuggingFace Sentence Transformers | **Apache 2.0** | Tự do sử dụng mô hình nhúng ngữ nghĩa câu phi thương mại. |
| **Bộ Sinh Dữ Liệu Synthea** | The MITRE Corporation | **Apache 2.0** | Tạo dữ liệu hồ sơ bệnh nhân tổng hợp phục vụ nghiên cứu tin học y tế. |
| **Văn Bản Ghi Chú MTSamples** | MTSamples Public Clinical Transcription Collection | **Academic Research Reference Terms** | Phục vụ đối chiếu văn phong y khoa, phi phân phối thương mại. |
| **Phác Đồ Hướng Dẫn Điều Trị** | GINA, GOLD, ESC, Bộ Y tế Việt Nam | **Copyright by Respective Authorities** | Dẫn chiếu trích đoạn bằng chứng phục vụ đào tạo và hỗ trợ quyết định lâm sàng (Fair Use); không bán lại ấn phẩm. |

> Tệp [`LICENSE`](../LICENSE) và tệp [`NOTICE`](../NOTICE) tại thư mục gốc của repository đã được cập nhật đồng bộ phản ánh chính xác ma trận trên.

---

## 5. GIỚI HẠN VÀ TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM (AUDIT DISCLAIMER)

> [!WARNING]
> **Tuyên Bố Ranh Giới Kỹ Thuật:** Báo cáo rà soát này là kết quả kiểm toán kỹ thuật nội bộ (Internal Engineering Due-Diligence) do Thành viên 2 thực hiện nhằm đảm bảo các thực hành tốt nhất về bảo mật dữ liệu y tế và quản trị mã nguồn.
> Báo cáo này **tuyệt đối không được coi là một chứng chỉ bảo mật độc lập từ bên thứ ba (Third-Party Security Certification)** hoặc một sự bảo đảm an toàn tuyệt đối trước mọi nguy cơ an ninh mạng. Khi triển khai hệ thống trên dữ liệu bệnh nhân thực tế tại các cơ sở y tế, đơn vị vận hành bắt buộc phải tiến hành đánh giá tác động quyền riêng tư dữ liệu (DPIA) theo Nghị định 13/2023/NĐ-CP và thẩm định an toàn thông tin theo cấp độ của cơ quan quản lý y tế có thẩm quyền.
