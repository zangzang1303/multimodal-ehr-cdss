# HƯỚNG DẪN QUẢN TRỊ SNAPSHOT VÀ PHỤC HỒI QDRANT OFFLINE
### M-CDSS Phase 2 / Backlog 07 - Nhiệm vụ 2.1 (Data Engineer & Privacy)

---

## 1. MỤC ĐÍCH & PHẠM VI NGHIỆM THU
Nhiệm vụ 2.1 yêu cầu đóng gói kho dữ liệu tri thức phác đồ (Vector Database) theo quy trình chuẩn khoa học và bảo vệ quyền sở hữu trí tuệ:
- Đảm bảo tính tái lập 100% trên môi trường ngoại tuyến (Offline-first).
- Rà soát nguồn gốc bản quyền, chỉ phân phối dữ liệu được phép theo các công ước học thuật (Fair Use / Educational).
- Cung cấp manifest kỹ thuật với SHA-256 checksum và kịch bản restore tự động.

---

## 2. KIẾN TRÚC KHO VECTOR VÀ PHÁC ĐỒ
Cơ sở dữ liệu vector lưu trữ 14 phân đoạn lâm sàng chuẩn mực, chia đều cho 4 nhóm bệnh mục tiêu:
1. **Hen phế quản (ASTHMA):** GINA 2024 & Hướng dẫn Bộ Y tế (QĐ 1851/QĐ-BYT).
2. **Bệnh phổi tắc nghẽn mạn tính (COPD):** GOLD 2024 & Hướng dẫn Bộ Y tế (QĐ 1856/QĐ-BYT).
3. **Suy tim (CONGESTIVE_HEART_FAILURE):** ESC 2023 Guidelines on Acute and Chronic Heart Failure.
4. **Viêm phổi mắc phải cộng đồng (PNEUMONIA):** Hướng dẫn Bộ Y tế (QĐ 4815/QĐ-BYT) & ATS/IDSA.

---

## 3. CÁC TỆP ĐẦU RA (DELIVERABLES)
1. **Bộ quản trị Snapshot:** `scripts/qdrant_snapshot_manager.py` (hỗ trợ các lệnh `create`, `restore`, `verify`).
2. **Tệp lưu trữ snapshot nén:** `data/vector_store/qdrant_snapshot.tar.gz`.
3. **Tệp Manifest kỹ thuật:** `data/vector_store/manifest.json`.
4. **Tài liệu hướng dẫn khôi phục:** `data/vector_store/README.md` và `docs/QDRANT_SNAPSHOT_AND_RESTORE_GUIDE.md`.

---

## 4. QUY TRÌNH KIỂM TOÁN VÀ KHÔI PHỤC (VERIFICATION & RESTORATION)

### 4.1. Kiểm Toán Tính Toàn Vẹn Mã Băm SHA-256
Chạy lệnh:
```bash
python scripts/qdrant_snapshot_manager.py verify
```
Kết quả kỳ vọng:
```
[✓] Guideline verified: byt_pneumonia.json
[✓] Guideline verified: CATALOG.yaml
[✓] Guideline verified: esc_heart_failure.json
[✓] Guideline verified: gina_asthma.json
[✓] Guideline verified: gold_copd.json
[✓] Snapshot archive verified: qdrant_snapshot.tar.gz
```

### 4.2. Khôi Phục Cơ Sở Dữ Liệu
Khi khởi động hệ thống trên máy mới hoặc sau khi xóa thư mục `data/vector_store/qdrant`:
```bash
python scripts/qdrant_snapshot_manager.py restore
```
Hoặc nếu muốn tái tạo lại hoàn toàn từ tệp nguồn:
```bash
python scripts/qdrant_snapshot_manager.py restore --force-reingest
```

Sau khi khôi phục, kiểm tra lại với bộ kiểm thử tự động:
```bash
pytest tests/test_knowledge_ingest.py
```
Toàn bộ 3 bài kiểm tra đều vượt qua thành công (`3 passed`).
