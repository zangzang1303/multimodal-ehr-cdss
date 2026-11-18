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

### 2.2. Kiểm Toán Dữ Liệu Bệnh Nhân (PHI / PII Audit) & Đánh Giá Trước/Sau Cải Tiến

Trong đợt rà soát chất lượng toàn diện ngày 18/11/2026 (Backlog 08), nhóm nghiên cứu đã tiến hành đánh giá chi tiết tỷ lệ rò rỉ thông tin nhận dạng cá nhân (PHI) trên tập dữ liệu lâm sàng và ghi nhận các khiếm khuyết trong biểu thức chính quy cũ.

#### Bảng Thống Kê Tỷ Lệ Rò Rỉ PHI Trước Và Sau Khi Cải Tiến `ClinicalDeidentifier`:

| Loại Thực Thể PHI (Entity) | Biểu Thức Nhận Dạng Bổ Sung / Sửa Đổi | Tỷ Lệ Sót Trước Cải Tiến (Phiên bản cũ) | Tỷ Lệ Sót Sau Cải Tiến (Canonical Split) | Đánh Giá Khắc Phục |
| :--- | :--- | :---: | :---: | :---: |
| **Mã Thẻ BHYT Việt Nam** | `\b[A-Z]{2}\d{1,2}\d{10,13}\b` & nhãn BHYT/Insurance | **~84.0%** (Sót mã `DN4...` do regex cũ yêu cầu đủ 13 số) | **0.0% (0 / 2.000)** | ✅ Khắc phục triệt để |
| **Bác Sĩ & Học Hàm/Học Vị VN** | `(?:GS\|PGS\|TS\|ThS\|BS\|BSCK\|CKI{1,2})\.?(?:\s*[A-Z]+\.)*\s+[A-ZĐ][\wÀ-ỹ]+...` | **~72.0%** (Sót `PGS.TS.`, `BS.CKII.` do regex cũ chỉ khớp tên thường) | **0.0% (0 / 2.000)** | ✅ Khắc phục triệt để |
| **Tên Bệnh Viện Viết HOA** | `\bBỆNH VIỆN(?:\s+[A-ZĐÀ-Ỹ0-9]+)+\b` | **100.0%** (Sót `BỆNH VIỆN BẠCH MAI` vì chữ HOA toàn bộ) | **0.0% (0 / 2.000)** | ✅ Khắc phục triệt để |
| **Số Điện Thoại / CCCD / Ngày** | Regex Safe Harbor chuẩn hóa | 0.0% | **0.0% (0 / 2.000)** | ✅ Duy trì an toàn tuyệt đối |
| **Bảo Toàn Chỉ Số Sinh Hiệu** | Kiểm thử âm tính (`BP`, `HR`, `SpO2`, `WBC`, `CRP`) | Không ảnh hưởng | **100% Bảo toàn (Không che nhầm)** | ✅ Đã kiểm chứng qua unit test |

* **Bộ kiểm thử đơn vị tự động:** Đã bổ sung bộ kiểm thử chuyên dụng tại `tests/test_deidentifier.py` bao gồm 5 nhóm test case dương tính và âm tính, xác nhận 100% ca kiểm thử vượt qua.
* **Tập dữ liệu chuẩn hóa (`data/processed_rebuilt_strict/`):** Toàn bộ 2.000 bản ghi trên cả 3 tập (Train 1.425, Val 273, Test 302) đã được tái tạo ghi chú lâm sàng với tỷ lệ rò rỉ PHI đạt **0.0%**. Các tệp Parquet được bảo vệ an toàn bởi `.gitignore` và quản lý phiên bản qua `data/DATA_MANIFEST.json`.

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
