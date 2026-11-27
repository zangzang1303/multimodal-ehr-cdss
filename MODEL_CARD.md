# MODEL CARD – M-CDSS cross-attention (BERT đóng băng)

> **Nguyên mẫu nghiên cứu trên dữ liệu tổng hợp. Không dùng cho quyết định lâm sàng.**
> Sinh tự động bởi `scripts/export_model_card.py` từ `results/registry.json` (2026-11-27T00:09:09Z).

## 1. Thông tin mô hình
- Checkpoint: `data/checkpoints/multimodal_best.pt` (SHA-256 `05bc3750315ba5a06126b77409fa3367495d3ef7a666679adca8f7651138cb55`)
- Kiến trúc: FT-Transformer (13 biến bảng) + Bio_ClinicalBERT đóng băng (`max_length` 512) + cross-attention có cổng, 4 lớp.
- Seed 101 – chọn theo NLL validation thấp nhất trong 5 seed (quy tắc đăng ký trước, docs/11_ANALYSIS_PLAN.md A.1).
- Temperature scaling T = 1.2117 (khớp trên validation N = 273).
- Dữ liệu: `data/processed_rebuilt_strict/` (manifest SHA-256 `7aafd62acd020992…`).

## 2. Mục đích sử dụng
- **Dự kiến:** minh hoạ nghiên cứu về dung hợp dữ liệu bảng + ghi chú lâm sàng cho 4 chẩn đoán (hen, COPD, suy tim, viêm phổi), giảng dạy, demo phần mềm.
- **Không dự kiến:** chẩn đoán, sàng lọc hay điều trị bệnh nhân thật; dữ liệu ngoài 4 nhóm bệnh; ghi chú tiếng Việt (mô hình huấn luyện trên ghi chú tiếng Anh).

## 3. Hiệu năng (test strict N = 302)
| Mô hình | Macro AUROC (TB ± SD) | Macro-F1 | ECE | Δ AUROC so với mô hình này [CI 95%], p Holm |
| :--- | :---: | :---: | :---: | :--- |
| Logistic Regression (bảng) | 0.945 ± 0.000 | 0.669 | 0.078 | -0.013 [-0.033; 0.005], p=0.456 |
| CatBoost (bảng) | 0.925 ± 0.003 | 0.647 | 0.061 | -0.033 [-0.053; -0.014], p=0.010 |
| FT-Transformer (bảng) | 0.929 ± 0.019 | 0.732 | 0.092 | -0.010 [-0.027; 0.008], p=0.516 |
| TF-IDF + LR (văn bản) | 0.917 ± 0.000 | 0.674 | 0.094 | -0.041 [-0.065; -0.019], p=0.009 |
| Bio_ClinicalBERT đóng băng (văn bản) | 0.899 ± 0.027 | 0.592 | 0.116 | -0.054 [-0.080; -0.029], p=0.009 |
| Bio_ClinicalBERT fine-tune (văn bản) | 0.975 ± 0.004 | 0.843 | 0.072 | +0.020 [0.008; 0.033], p=0.012 |
| Concat fusion (đóng băng) | 0.929 ± 0.021 | 0.742 | 0.116 | -0.066 [-0.086; -0.048], p=0.009 |
| Cross-attention (đóng băng) – triển khai | 0.956 ± 0.008 | 0.691 | 0.081 | (mô hình này) |
| Cross-attention (fine-tune) | 0.961 ± 0.015 | 0.726 | 0.106 | -0.000 [-0.010; 0.010], p=0.930 |
| Ensemble CatBoost + BERT-FT | 0.978 ± 0.003 | 0.801 | 0.116 | +0.024 [0.013; 0.035], p=0.009 |

Δ ở bảng trên là (mô hình so sánh − mô hình triển khai). **Mô hình triển khai không phải mô hình tốt nhất**: Bio_ClinicalBERT fine-tune và ensemble CatBoost + BERT có AUROC cao hơn có ý nghĩa thống kê. Mô hình này được chọn trước khi xem test vì tương thích với dịch vụ suy luận (BERT đầy đủ, đóng băng).

## 4. Hiệu chuẩn
- ECE (10 bins): không hiệu chuẩn 0.079, temperature 0.077 (CI [0.0504, 0.1243]), vector scaling 0.098, isotonic 0.094.
- Mục tiêu ECE < 0.05: **không đạt** với phương pháp nào.

## 5. Độ bền khi thiếu dữ liệu (macro AUROC, trung bình qua seed)
| Kịch bản | Mô hình này | CatBoost | BERT fine-tune |
| :--- | :---: | :---: | :---: |
| Đầy đủ | 0.956 | 0.925 | 0.975 |
| Thiếu 10% biến số | 0.936 | 0.897 | 0.975 |
| Thiếu 30% biến số | 0.908 | 0.856 | 0.975 |
| Thiếu 50% biến số | 0.888 | 0.823 | 0.975 |
| Mất toàn bộ bảng | 0.678 | 0.500 | 0.975 |
| Mất văn bản | 0.902 | 0.925 | 0.501 |

## 6. Phân nhóm (dữ liệu tổng hợp – chỉ mô tả pipeline)
| Nhóm | N | AUROC [CI 95%] | Ghi chú |
| :--- | :---: | :---: | :--- |
| gender_M | 206 | 0.951 [0.9262, 0.9705] |  |
| gender_F | 96 | 0.924 [0.8496, 0.9772] | one-vs-rest AUROC averaged over the classes present in this subgroup only |
| age_under_65 | 237 | 0.914 [0.8926, 0.9333] |  |
| age_65_and_older | 65 | 0.814 [0.6854, 0.9361] | one-vs-rest AUROC averaged over the classes present in this subgroup only |
| smoking_NEVER | 160 | 0.924 [0.8943, 0.9504] | one-vs-rest AUROC averaged over the classes present in this subgroup only |
| smoking_FORMER | 142 | 0.966 [0.9239, 0.996] | one-vs-rest AUROC averaged over the classes present in this subgroup only |
| smoking_CURRENT | 0 | –  | fewer than two classes present (or empty subgroup) - not estimable |

## 7. Giới hạn đã biết
- Dữ liệu bán tổng hợp (Synthea + MTSamples); nhãn không do bác sĩ xác định; chưa ngoại kiểm, chưa khảo sát bác sĩ.
- Ghi chú chứa lại sinh hiệu/xét nghiệm; tín hiệu văn bản phần lớn đến từ các con số này (xem RQ2 trong registry).
- Tập test strict có phân bố nhân khẩu học khác tập huấn luyện (106/106 ca suy tim là nam, không có người đang hút thuốc).
- Mô hình huấn luyện trên dữ liệu đầy đủ; mất toàn bộ dữ liệu bảng làm hiệu năng giảm mạnh.

## 8. Giấy phép
- Mã nguồn: xem `LICENSE`. Bio_ClinicalBERT: MIT. Synthea: Apache-2.0. MTSamples: điều khoản của mtsamples.com (chỉ nghiên cứu).
- Không phân phối lại toàn văn phác đồ GINA/GOLD/ESC (có bản quyền); KB chỉ chứa diễn giải ngắn có trích dẫn.
