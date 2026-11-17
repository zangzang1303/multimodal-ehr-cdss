# QDRANT VECTOR STORE & CLINICAL GUIDELINE SNAPSHOT REGISTRY
### M-CDSS Phase 2 / Backlog 07 (Task 2.1 - Data Engineer & Privacy)

---

## 1. TỔNG QUAN VÀ NGUỒN GỐC PHÁC ĐỒ LÂM SÀNG (PROVENANCE & RIGHTS)
Cơ sở dữ liệu vector Qdrant lưu trữ các phân đoạn phác đồ lâm sàng chuẩn hóa phục vụ cơ chế **Agentic RAG & Evidence Grounding** của hệ thống M-CDSS.
Tất cả các tài liệu phác đồ được tuyển chọn và số hóa dựa trên các hướng dẫn điều trị quốc tế và quốc gia đã được công bố công khai, phục vụ mục đích nghiên cứu học thuật phi thương mại và hỗ trợ quyết định lâm sàng:

| Nguồn Phác Đồ | Cơ Quan Ban Hành | Phiên Bản | Bệnh Lý Mục Tiêu | Giấy Phép & Quyền Phân Phối |
| :--- | :--- | :---: | :--- | :--- |
| **GINA 2024** | Global Initiative for Asthma | 2024 | Hen phế quản (ASTHMA) | Sử dụng phi thương mại hỗ trợ quyết định y tế & nghiên cứu giáo dục theo FAIR. |
| **GOLD 2024** | Global Initiative for Chronic Obstructive Lung Disease | 2024 | Bệnh phổi tắc nghẽn mạn (COPD) | Trích dẫn nghiên cứu lâm sàng và hướng dẫn chẩn đoán phi lợi nhuận. |
| **ESC 2023** | European Society of Cardiology | 2023 | Suy tim sung huyết (HEART_FAILURE) | Dẫn chiếu chuyên môn y khoa phục vụ nghiên cứu lâm sàng. |
| **BYT VN 2020** | Bộ Y tế Việt Nam (QĐ 4815, 1856, 1851) | 2020 | Viêm phổi (CAP), COPD, Hen | Văn bản quy phạm kỹ thuật chuyên môn y tế quốc gia công khai. |

> [!IMPORTANT]
> **Tuyên bố bản quyền & Tuân thủ Git:** Toàn văn gốc các phác đồ thuộc bản quyền của GINA, GOLD, ESC và Bộ Y tế Việt Nam. Kho mã nguồn chỉ phân phối các vector embedding 768 chiều và các trích đoạn văn bản tóm tắt phục vụ trích dẫn bằng chứng minh bạch (Fair Use / Evidence Citation), không phân phối lại ấn bản thương mại.

---

## 2. THÔNG SỐ KỸ THUẬT VECTOR DATABASE (TECHNICAL SPECIFICATIONS)

* **Engine:** Qdrant Vector Search Engine (tương thích `qdrant/qdrant:latest`, `qdrant-client >= 1.20.0`).
* **Collection Name:** `clinical_guidelines`
* **Vector Dimension:** $768$ (phù hợp với đầu ra của mô hình embedding).
* **Khoảng cách Vector (Distance Metric):** Cosine Similarity.
* **Mô hình Embedding:** `sentence-transformers/all-mpnet-base-v2` (L2-normalized).
* **Tổng số phân đoạn lưu trữ:** $14$ clinical chunks (bao gồm tiêu chuẩn chẩn đoán, chẩn đoán phân biệt, yếu tố nguy cơ và phác đồ xử trí ban đầu).
* **Payload Fields:** `chunk_id`, `source_id`, `version`, `target_disease`, `section_title`, `page_or_section`, `clinical_category`, `text_content`, `evidence_level`.

---

## 3. BẢNG MANIFEST VÀ CHECKSUM TOÀN VẸN (INTEGRITY CHECKSUMS)

Tất cả các thành phần dữ liệu được kiểm toán bằng thuật toán băm mật mã học **SHA-256**:

```json
{
  "snapshot_archive": "data/vector_store/qdrant_snapshot.tar.gz",
  "manifest": "data/vector_store/manifest.json",
  "guidelines_catalog": "data/guidelines/CATALOG.yaml"
}
```

Tra cứu mã băm chi tiết tại [`manifest.json`](file:///e:/multimodal-ehr-cdss/data/vector_store/manifest.json).

---

## 4. HƯỚNG DẪN RESTORE VÀ TÁI LẬP (REPRODUCTION & RESTORE GUIDE)

### Phương Án 1: Khôi Phục Nhanh Từ Snapshot Offline
Khi tải kho mã nguồn hoặc chuyển giao máy chủ mới, thực hiện khôi phục trực tiếp từ tệp snapshot:
```bash
python scripts/qdrant_snapshot_manager.py restore
```
Script sẽ tự động:
1. Đọc `manifest.json`.
2. Kiểm tra checksum SHA-256 của tệp `qdrant_snapshot.tar.gz`.
3. Giải nén vào thư mục `data/vector_store/qdrant`.

### Phương Án 2: Tái Lập Từ Đầu Bằng Ingestion Script (Deterministic Re-Ingestion)
Nếu cần tạo lại từ đầu hoặc thay đổi mô hình embedding:
```bash
python scripts/qdrant_snapshot_manager.py restore --force-reingest
# Hoặc chạy trực tiếp pipeline:
python -c "import os; os.environ['HF_HUB_OFFLINE']='1'; from src.agent.knowledge_ingest import run_ingest; run_ingest()"
```

### Phương Án 3: Đồng Bộ Vào Docker Compose Qdrant Container
Khi triển khai trọn gói 3 dịch vụ bằng Docker Compose:
1. Thư mục `data/vector_store/qdrant` hoặc `data/guidelines` được mount trực tiếp vào container.
2. Kiểm tra trạng thái dịch vụ Qdrant:
   ```bash
   curl http://localhost:6333/collections/clinical_guidelines
   ```
3. Kiểm tra kiểm toán toàn vẹn:
   ```bash
   python scripts/qdrant_snapshot_manager.py verify
   ```
