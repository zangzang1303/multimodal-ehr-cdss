# Multimodal Clinical Decision Support System (M-CDSS) - Data Directory

> [!IMPORTANT]
> **QUY CHUẨN DỮ LIỆU GIAI ĐOẠN 3 (PHASE 3 DATA GOVERNANCE)**
> Kể từ Backlog 08, toàn bộ mô hình và kịch bản thực nghiệm tuân thủ nguyên tắc:
> **"Một nguồn sự thật duy nhất (Single Source of Truth) — Không gõ tay số liệu — Xác thực SHA-256 trước khi chạy."**
> 
> - **Bộ dữ liệu chuẩn chính thức (Canonical):** 👉 [`data/processed_rebuilt_strict/`](processed_rebuilt_strict/)
> - **Tệp kê khai toàn vẹn dữ liệu:** 👉 [`data/DATA_MANIFEST.json`](DATA_MANIFEST.json)
> - **Các thư mục dữ liệu cũ (`data/processed/`, `data/processed_strict/`):** Đã đánh dấu là **LEGACY / DEPRECATED**.

---

## 1. Cấu Trúc Thư Mục Dữ Liệu

```
data/
├── DATA_MANIFEST.json         # Tệp kê khai SHA-256, số dòng, phân bố lớp và lệnh tái tạo
├── processed_rebuilt_strict/  # [CANONICAL] Dữ liệu chuẩn (Train 1.425, Val 273, Test 302)
│   ├── train.parquet
│   ├── val.parquet
│   └── test.parquet
├── processed/                 # [LEGACY] Dữ liệu cũ trước kiểm soát rò rỉ nguồn
├── raw/                       # Dữ liệu sinh thô (chưa khử định danh)
│   ├── patients_raw.parquet   # Bảng số 2.000 bệnh nhân
│   └── clinical_notes_raw.jsonl # Ghi chú thô chứa PHI giả định phục vụ test
├── checkpoints/               # Trọng số mô hình đã huấn luyện
├── evaluation_plots/          # Biểu đồ và chỉ số đánh giá lâm sàng
└── guidelines/                # Hướng dẫn y khoa phục vụ RAG
```

---

## 2. Kênh Phân Phối Dữ Liệu Có Kiểm Soát Cho Nhóm Nghiên Cứu

Do các tệp `.parquet` có dung lượng nhị phân và bị loại khỏi Git commit thông thường (`.gitignore`), nhóm nghiên cứu sử dụng **kênh phân phối có kiểm soát** theo một trong các phương án sau:

### Phương án A: Tải từ GitHub Release Asset (Khuyến nghị cho nhóm)
1. Tải gói lưu trữ dữ liệu `mcdss-data-canonical-strict-v1.0.0.tar.gz` từ GitHub Releases (kênh riêng tư của nhóm nghiên cứu).
2. Giải nén vào thư mục `data/processed_rebuilt_strict/`:
   ```bash
   tar -xzf mcdss-data-canonical-strict-v1.0.0.tar.gz -C data/processed_rebuilt_strict/
   ```
3. Chạy xác thực tính toàn vẹn SHA-256:
   ```bash
   python -m src.data_pipeline.manifest data/processed_rebuilt_strict
   ```

### Phương án B: Tái tạo tự động từ mã nguồn (Reproducible Pipeline)
Nếu cần sinh lại bộ dữ liệu canonical từ dữ liệu thô:
```bash
python scripts/rebuild_canonical_dataset.py
```
Lệnh này sẽ tự động:
1. Nạp dữ liệu thô từ `data/raw/`.
2. Áp dụng pipeline khử định danh sâu (`ClinicalDeidentifier`).
3. Khớp phân chia Stratified Group Split bảo đảm không rò rỉ bệnh nhân và nhóm nguồn.
4. Gán khuyết MICE chỉ fit trên Train và transform sang Val/Test.
5. Cập nhật mã băm SHA-256 vào `data/DATA_MANIFEST.json`.

---

## 3. Quy Tắc Xác Thực Bắt Buộc Trong Code (Manifest Verification Rule)

Mọi script huấn luyện (`train_multimodal.py`, `run_baselines.py`, `run_multimodal_ablation.py`) và đánh giá (`evaluate_clinical_utility.py`) **bắt buộc phải gọi hàm `verify_manifest()` ngay khi khởi động**:

```python
from src.data_pipeline.manifest import verify_manifest

# Dừng chương trình ngay lập tức nếu dữ liệu bị thay đổi hoặc không khớp SHA-256
verify_manifest("data/processed_rebuilt_strict")
```

Nếu bất kỳ tệp dữ liệu nào bị sửa đổi, thiếu dòng, lệch phân bố nhãn hoặc sai khác mã SHA-256, chương trình sẽ báo lỗi `RuntimeError` và từ chối thực thi nhằm ngăn chặn tình trạng sai lệch số liệu khoa học.
