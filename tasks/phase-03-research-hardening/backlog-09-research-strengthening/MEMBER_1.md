# BACKLOG 09 – THÀNH VIÊN 1 (Lead ML / Modeling & Evaluation)

> **Trạng thái 2026-11-27: HOÀN THÀNH** – mọi số liệu trong `results/registry.json` (sinh bởi `scripts/build_results_registry.py`).
>
> | Nhiệm vụ | Kết quả |
> | :--- | :--- |
> | 1.1 [CORE] Ma trận so sánh công bằng | ✅ 10 mô hình × 5 seed (`scripts/run_research_experiments.py rq1`); fine-tune khối BERT cuối dùng chung cho text-only và fusion (`src/models/text_tail.py`). Kết quả: BERT-FT và ensemble > cross-attention trên test strict; cross-attention ≈ mô hình bảng. |
> | 1.2 [CORE] Thống kê | ✅ `src/evaluation/stats.py` (paired bootstrap, Holm, DCA Vickers, ECE equal-mass, vector scaling, isotonic) + unit test. Bootstrap theo bản ghi – có cảnh báo vì chỉ 478 bệnh nhân gốc. |
> | 1.3 [CORE] Phân rã tín hiệu văn bản | ✅ 4 biến thể (`src/data_pipeline/note_variants.py`) × 4 mô hình × 3 seed. Che mọi con số → văn bản sụp về ~0.54–0.68; bỏ sinh hiệu nhưng giữ tuổi → văn bản vẫn ~0.9. Attribution (IG) **không làm** – thay bằng phân tích lỗi theo bệnh nhân gốc. |
> | 1.4 [OPTIONAL] Mô phỏng bổ trợ | ✅ lưới ρ×σ = 5×3, 2 seed (`results/rq3_simulation.json`); fusion có lợi khi văn bản mang tín hiệu riêng hoặc bảng nhiễu. |
> | 1.5 [CORE] Hiệu chuẩn | ✅ 4 phương pháp; temperature tốt nhất (ECE ≈ 0.077), **chưa đạt < 0.05**. |
> | Bổ sung | DCA, missing-modality, temporal (theo nhóm), fairness, error analysis trên mô hình triển khai (thay kết quả thu hồi của TV2); 5-fold grouped CV post-hoc (`A.6`). |


## Nhiệm vụ 1.1 [CORE] – Ma trận so sánh công bằng (RQ1)
Hiện tại so sánh lệch: text-only baseline **fine-tune** khối cuối, nhánh text trong fusion **đóng băng**. Chạy cùng split, cùng seed (≥ 3, lý tưởng 5):

| Nhóm | Mô hình |
| :--- | :--- |
| Baseline đơn giản | Logistic Regression (9 biến số + one-hot), TF-IDF(1–2 gram) + LR |
| Baseline mạnh | CatBoost, FT-Transformer, Bio_ClinicalBERT (frozen + linear head), Bio_ClinicalBERT (fine-tune khối cuối) |
| Fusion đơn giản | **Ensemble trung bình xác suất CatBoost + BERT** (baseline phản biện chắc chắn hỏi), Concat |
| Đề xuất | Cross-attention (frozen) và Cross-attention (fine-tune khối cuối) |

Đầu ra: `results/registry.json` mục `rq1`, bảng `docs/paper_latex/generated/tab_main.tex`.

## Nhiệm vụ 1.2 [CORE] – Thống kê suy luận
- `src/evaluation/stats.py`:
  - `paired_bootstrap(pred_a, pred_b, metric, n=2000, group=patient_id)` → Δ, CI 95%, p.
  - CI cho từng metric (AUROC, AUPRC, F1, Brier, ECE).
  - Hiệu chỉnh Holm cho nhiều so sánh.
  - (Tuỳ chọn) DeLong cho AUROC one-vs-rest từng lớp.
- Báo cáo mean ± SD qua seed **và** CI bootstrap trên seed được chọn.
- Unit test với dữ liệu tổng hợp có đáp án biết trước.

## Nhiệm vụ 1.3 [CORE] – Phân rã tín hiệu văn bản (RQ2) – thí nghiệm then chốt
Tạo 4 biến thể ghi chú (hàm thuần trong `src/data_pipeline/note_variants.py`, có test):
| Biến thể | Mô tả |
| :--- | :--- |
| `full` | Ghi chú hiện tại |
| `num_masked` | Mọi con số → `<NUM>` |
| `no_vitals` | Bỏ khối `VITALS`/`PHYSICAL EXAMINATION` chứa sinh hiệu |
| `narrative_only` | Chỉ CHIEF COMPLAINT + HPI + MEDICATIONS |

Huấn luyện TF-IDF+LR, BERT (frozen & fine-tune), cross-attention trên từng biến thể. Đo AUROC + CI.
**Kỳ vọng (từ sơ bộ):** text-only sụp về ~0,55 khi che số; fusion ≈ tabular. Viết đúng như kết quả – đây là phát hiện chính của bài.

Thêm: phân tích attribution (Integrated Gradients hoặc attention rollout) trên 20 ca để xem token nào được dùng (số sinh hiệu vs từ ngữ lâm sàng).

## Nhiệm vụ 1.4 [OPTIONAL] – Mô phỏng bổ trợ có kiểm soát (RQ3)
Mục đích: chỉ ra *điều kiện* để cross-attention có ích, thay vì tuyên bố chung chung.
- Dùng biến thể `num_masked` làm nền (không còn rò số).
- Với tỷ lệ ρ ∈ {0; 0,25; 0,5; 0,75; 1} số ca, chèn một câu triệu chứng đặc hiệu theo lớp, lấy từ từ điển xây từ phác đồ (GINA/GOLD/ESC/BYT), có phủ định ("không sốt") và nhiễu gây nhầm với tỷ lệ ε = 0,1.
- Thêm nhiễu Gauss σ ∈ {0; 0,5; 1} SD vào các biến bảng phân biệt nhất.
- Đo Δ = AUROC(fusion) − max(AUROC đơn phương thức) theo (ρ, σ) → heatmap.
- **Ghi rõ là mô phỏng**, tín hiệu do nhóm thiết kế; mục đích là cơ chế, không phải hiệu năng lâm sàng.

## Nhiệm vụ 1.5 [CORE] – Hiệu chuẩn (RQ4a)
- So sánh trên checkpoint được chọn: không hiệu chuẩn / temperature / vector scaling / isotonic one-vs-rest (fit trên val).
- Báo cáo ECE (15 bins, equal-mass) + CI, classwise ECE, Brier, reliability diagram 4 lớp.
- Nếu không đạt ECE < 0,05: báo cáo đúng; thảo luận do N val = 273 nhỏ.

**Nghiệm thu Thành viên 1:** registry có mục `rq1`, `rq2`, `calibration` (và `rq3` nếu làm); hình `fig_rq2_text_decomposition.pdf`, `fig_calibration.pdf`, (`fig_rq3_heatmap.pdf`).
