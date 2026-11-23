# [CANONICAL] Canonical Processed EHR Dataset (M-CDSS Phase 3)

> [!IMPORTANT]
> **BỘ DỮ LIỆU CHUẨN DUY NHẤT (SINGLE SOURCE OF TRUTH FOR DATA)**
> Thư mục này lưu trữ bộ dữ liệu đã tiền xử lý chính thức phục vụ toàn bộ quá trình huấn luyện, đánh giá lâm sàng, và công bố khoa học của dự án M-CDSS.
> Mọi tệp trong thư mục này được giám sát tính toàn vẹn thông qua tệp kê khai [`data/DATA_MANIFEST.json`](../DATA_MANIFEST.json).

---

## 1. Cấu Trúc Phân Chia Dữ Liệu (Split Specifications)

Phân chia theo phương pháp **Stratified Group Splitting** nhằm đảm bảo không rò rỉ bệnh nhân (*Zero Patient Leakage*) và không rò rỉ nhóm nguồn ghi chú (*Zero Provenance Leakage*):

| Tệp Dữ Liệu | Vai Trò | Số Mẫu ($N$) | Tỷ Lệ | Phân Bố 4 Lớp Bệnh (ASTHMA / COPD / HF / PNEUMONIA) |
| :--- | :--- | :---: | :---: | :--- |
| `train.parquet` | Huấn luyện mô hình & gán khuyết MICE | **1.425** | 71.25% | `358 / 358 / 340 / 369` |
| `val.parquet` | Kiểm định mô hình, dừng sớm & hiệu chuẩn nhiệt độ | **273** | 13.65% | `71 / 71 / 54 / 77` |
| `test.parquet` | Kiểm thử độc lập nghiêm ngặt (*Strict Holdout Test*) | **302** | 15.10% | `71 / 71 / 106 / 54` |
| **Tổng Cộng** | **Đoàn hệ lâm sàng chuẩn hóa** | **2.000** | 100.0% | **`500 / 500 / 500 / 500` (Cân bằng tuyệt đối)** |

---

## 2. Các Biện Pháp Bảo Đảm Tính Toàn Vẹn & Quyền Riêng Tư

1. **Khử định danh mở rộng (Deep De-Identification):**
   - 100% che mã BHYT (`\b[A-Z]{2}\d{1,2}\d{10,13}\b` và các nhãn).
   - 100% che học hàm/học vị và tên bác sĩ Việt Nam (GS, PGS, TS, ThS, BS, BSCK, CKI, CKII).
   - 100% che tên bệnh viện viết HOA (`BỆNH VIỆN ...`).
   - Giữ nguyên toàn bộ giá trị sinh hiệu và xét nghiệm (`BP`, `HR`, `SpO2`, `WBC`, `CRP`).
2. **Kiểm toán Chống Rò Rỉ:**
   - Đạt 100% tiêu chuẩn theo [`data/rebuilt_strict_split_audit.json`](../rebuilt_strict_split_audit.json).
   - Giao tập hợp bệnh nhân $\mathcal{P}_{\text{train}} \cap \mathcal{P}_{\text{val}} \cap \mathcal{P}_{\text{test}} = \emptyset$.
3. **Xác thực trước khi chạy (Manifest Lock):**
   - Tất cả script gọi `verify_manifest("data/processed_rebuilt_strict")` ngay dòng đầu tiên; nếu SHA-256 hoặc số dòng sai lệch, script sẽ từ chối thực thi.
