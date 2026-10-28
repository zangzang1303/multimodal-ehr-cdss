# Nội dung slide tự đọc — Báo cáo tiến độ đợt 1 đề tài M-CDSS

**Mục đích tài liệu:** Làm nội dung nền để xây dựng bộ slide gửi giáo viên đánh giá. Slide cần tự cung cấp đủ bối cảnh, bằng chứng, phương pháp, tiến độ và kế hoạch tiếp theo; không phụ thuộc lời thuyết trình miệng.  
**Đối tượng đọc:** Giáo viên/hội đồng đánh giá có thể không biết trước dự án.  
**Đề xuất:** 17 slide nội dung + 1 slide tài liệu tham khảo. Có thể chia thành 2 phần hoặc rút gọn khi thiết kế, nhưng không nên bỏ phần giới hạn và hiện trạng.

> **Phiên bản kết quả:** Số liệu thực nghiệm trong tài liệu này theo báo cáo strict split ngày 28/10/2026. Các điểm benchmark cũ gần tuyệt đối đã bị thay thế sau khi rà soát nguy cơ leakage; không dùng làm kết quả hiện tại.

## Nguyên tắc biên soạn slide tự đọc

- Viết thông tin chính thành câu ngắn có chủ ngữ và kết luận rõ; hạn chế chỉ để từ khóa rời rạc.
- Với biểu đồ/bảng, ghi đơn vị, cỡ mẫu, tập dữ liệu, ý nghĩa chỉ số và nguồn ngay trên slide.
- Tách rõ **đã hoàn thành**, **đang có trong mã nguồn nhưng chưa tích hợp**, và **đề xuất/chưa triển khai**.
- Không gọi benchmark trên dữ liệu tổng hợp là đánh giá lâm sàng hoặc bằng chứng triển khai.
- Có thể chuyển giải thích kỹ thuật dài, bảng phân bố lớp đầy đủ và lịch backlog sang phụ lục.

---

## Slide 1 — Trang bìa

**Tiêu đề:** Hệ thống hỗ trợ chẩn đoán lâm sàng đa phương thức từ hồ sơ sức khỏe điện tử (M-CDSS)

**Thông tin cần có**
- Báo cáo tiến độ đợt 1 — Giai đoạn nghiên cứu và đề xuất giải pháp.
- Đơn vị/lớp, tên nhóm và thành viên, giáo viên hướng dẫn, ngày nộp.
- Từ khóa: EHR, multimodal AI, clinical notes, clinical decision support.

**Hình đề xuất:** Sơ đồ tối giản gồm dữ liệu bảng + ghi chú → mô hình hỗ trợ phân loại → đầu ra có giải thích.

---

## Slide 2 — Tóm tắt dự án và tiến độ

**Nội dung chính**

M-CDSS nghiên cứu hỗ trợ phân loại bốn nhóm bệnh có biểu hiện hô hấp/tim mạch chồng lấp: hen phế quản (ASTHMA), COPD, suy tim (HEART_FAILURE) và viêm phổi (PNEUMONIA). Hệ thống dự kiến kết hợp dữ liệu bảng như sinh hiệu/xét nghiệm với ghi chú lâm sàng tự do.

Giai đoạn 1 tập trung xây nền tảng dữ liệu, kiểm soát nguy cơ leakage, xây ba baseline đơn phương thức và đề xuất kiến trúc Giai đoạn 2. Đến mốc báo cáo, pipeline được chạy lại bằng strict split theo nhóm nguồn; ba baseline đã có kết quả trên tập test nội bộ 302 mẫu. Bio_ClinicalBERT đạt AUROC macro 0,9735; kết quả này chỉ phản ánh dữ liệu tổng hợp/kho công khai và chưa xác nhận hiệu năng trên bệnh nhân thực.

**Trạng thái tổng quan**
- **Đã làm:** pipeline dữ liệu, split/audit, benchmark ba baseline, tài liệu đề xuất.
- **Tiếp theo:** mô hình fusion, RAG/giải thích, đánh giá mở rộng và tích hợp phần mềm.

---

## Slide 3 — Bài toán lâm sàng và lý do chọn đề tài

**Nội dung chính**

Khó thở, ho, giảm SpO₂ và các dấu hiệu viêm có thể gặp ở nhiều bệnh khác nhau. Trong giai đoạn tiếp nhận ban đầu, thông tin lâm sàng còn chưa đầy đủ nên việc phân biệt hen, COPD, suy tim và viêm phổi có thể khó khăn.

Hai nguồn dữ liệu EHR bổ sung cho nhau:

| Dữ liệu bảng | Ghi chú lâm sàng tự do |
|---|---|
| Định lượng sinh hiệu và xét nghiệm; dễ chuẩn hóa và đưa vào thuật toán. | Ghi nhận triệu chứng, tiền sử, diễn tiến và bối cảnh chưa được cấu trúc thành trường dữ liệu. |
| Có thể thiếu xét nghiệm hoặc không thể hiện diễn tiến bệnh. | Có cách viết không đồng nhất, viết tắt và khó định lượng tự động. |

**Lý do chọn đề tài:** Khảo sát liệu mô hình có thể sử dụng cả tín hiệu định lượng lẫn ngữ cảnh trong văn bản, đồng thời đánh giá trong quy trình hạn chế rò rỉ dữ liệu và thể hiện giới hạn một cách minh bạch hay không.

**Hình đề xuất:** Hai cột đầu vào cùng hội tụ vào câu hỏi “Thông tin bổ sung có cải thiện phân loại không?”.

---

## Slide 4 — Literature review: phạm vi và kết quả tổng quan

**Nguồn chính:** Hunik et al., *Diagnostic prediction models for primary care, based on artificial intelligence and electronic health records: a systematic review* (tài liệu JMIR Preprints 62862, 2024; xem nguồn trong thư mục `docs/`).

**Các con số được nhóm tổng hợp từ tài liệu**
- 10.657 công trình được rà soát qua các cơ sở dữ liệu học thuật.
- 15 nghiên cứu đáp ứng tiêu chí đưa vào tổng quan.
- Theo phần phân tích của nhóm, 15/15 nghiên cứu sử dụng dữ liệu có cấu trúc; không nghiên cứu nào trong tập được tổng quan khai thác ghi chú tự do bằng mô hình ngôn ngữ.
- PROBAST tổng thể: 9/15 (60%) nguy cơ sai lệch cao; 6/15 (40%) chưa rõ; 0/15 nguy cơ thấp.

**Diễn giải:** Tổng quan gợi ý khoảng trống về khai thác văn bản và chất lượng phương pháp luận trong tập nghiên cứu được chọn. Những tỷ lệ này thuộc phạm vi 15 nghiên cứu của tổng quan, không đại diện cho toàn bộ AI y tế.

**Hình đề xuất:** Funnel 10.657 → 15; bên cạnh là thanh 9 High / 6 Unclear / 0 Low risk.

**Chú thích bắt buộc:** Số liệu theo tổng quan Hunik et al. và phần trích xuất trong `docs/01_RESEARCH_BACKGROUND_AND_GAP.md`.

---

## Slide 5 — Các rủi ro phương pháp luận trong y văn

**Nội dung chính**

Các vấn đề được nhấn mạnh trong tài liệu tổng quan và tài liệu nền của dự án gồm:

- **Rò rỉ nhãn/không đúng thời điểm:** biến đầu vào có thể chứa thông tin phát sinh sau chẩn đoán hoặc gần như chính là tiêu chuẩn chẩn đoán.
- **Dữ liệu khuyết:** cách xử lý không được mô tả hoặc có thể làm thay đổi thành phần mẫu.
- **Hiệu chuẩn:** độ phân biệt tốt không đồng nghĩa xác suất dự đoán đáng tin cậy.
- **Tổng quát hóa:** kết quả trên một nguồn/cơ sở không tự động áp dụng được ở nguồn khác; ngoại kiểm thường còn hạn chế.

**Hàm ý cho thiết kế M-CDSS:** khóa mốc thời gian, split có nhóm, audit leakage, báo cáo nhiều chỉ số và đặt ngoại kiểm trong kế hoạch tiếp theo.

**Hình đề xuất:** Bốn khối PROBAST (Participants, Predictors, Outcome, Analysis) cùng ví dụ lỗi tương ứng.

---

## Slide 6 — Khoảng trống và câu hỏi nghiên cứu

**Khoảng trống dự án hướng tới**
1. Đánh giá kết hợp ghi chú tự do và dữ liệu bảng, thay vì chỉ dùng từng nguồn riêng.
2. Kiểm soát rò rỉ nguồn và trình tự thời gian khi xây dựng benchmark.
3. Đánh giá cả phân biệt, phân loại và hiệu chuẩn xác suất; công bố giới hạn dữ liệu.
4. Đề xuất giải thích có truy xuất guideline và gắn bằng chứng với ghi chú ở giai đoạn phát triển tiếp theo.

**Câu hỏi nghiên cứu chính**

> Trên dữ liệu nghiên cứu hiện có, việc kết hợp thông tin bảng và ghi chú lâm sàng có cải thiện kết quả so với baseline đơn phương thức trong một quy trình chia tập và audit nghiêm ngặt hơn hay không?

**Phạm vi kết luận:** Giai đoạn hiện tại mới thiết lập baseline và câu hỏi thực nghiệm. Chưa có kết quả fusion để trả lời khẳng định câu hỏi trên.

---

## Slide 7 — Mục tiêu, phạm vi và nhãn phân loại

**Mục tiêu tổng quát:** Xây dựng và đánh giá một nguyên mẫu CDSS nghiên cứu đa phương thức, hỗ trợ phân loại bốn nhóm bệnh và cung cấp đầu ra có thể kiểm tra.

**Bốn lớp mục tiêu**
- ASTHMA — hen phế quản.
- COPD — bệnh phổi tắc nghẽn mạn tính.
- HEART_FAILURE — suy tim.
- PNEUMONIA — viêm phổi.

**Phạm vi Giai đoạn 1**
- Dữ liệu tổng hợp/kho công khai và ghi chú đã xử lý; chưa phải cohort bệnh viện.
- Xây pipeline và benchmark ba mô hình riêng: CatBoost, FT-Transformer, Bio_ClinicalBERT.
- Đề xuất kiến trúc fusion/RAG cho giai đoạn sau.

**Ngoài phạm vi kết luận hiện tại:** chẩn đoán xác nhận, quyết định điều trị, hiệu quả trên bệnh nhân thực hoặc triển khai lâm sàng.

---

## Slide 8 — Kế hoạch tổng thể theo hai giai đoạn

| Giai đoạn / backlog | Công việc chính | Sản phẩm/tiêu chí đầu ra |
|---|---|---|
| **Giai đoạn 1, backlog 1 (tuần 1)** | Môi trường, schema dữ liệu, dữ liệu ban đầu, khung API/frontend. | Data contract, cấu hình, dữ liệu nghiên cứu, khung ứng dụng. |
| **Giai đoạn 1, backlog 2 (tuần 2)** | De-ID, temporal lock, missing data, khung baseline. | Pipeline và kiểm thử dữ liệu. |
| **Giai đoạn 1, backlog 3 (tuần 3)** | Group split, benchmark, error analysis, đề xuất giải pháp. | Báo cáo baseline và thiết kế Giai đoạn 2. |
| **Giai đoạn 2, backlog 4** | Encoder bảng/văn bản, fusion, calibration, ablation. | Mô hình fusion và kết quả so sánh trên strict split. |
| **Giai đoạn 2, backlog 5** | RAG, vector store, evidence grounding, tích hợp phần mềm. | Luồng truy xuất guideline và giải thích có bằng chứng. |
| **Giai đoạn 2, backlog 6** | DCA, phân tích lỗi, fairness, chuyên gia/ngoại kiểm khi khả thi. | Đánh giá lâm sàng mở rộng và giới hạn tổng quát hóa. |
| **Giai đoạn 2, backlog 7** | Đóng gói, báo cáo và demo. | Bản bàn giao tái lập được. |

**Trạng thái:** Giai đoạn 1 là phần báo cáo hiện tại; Giai đoạn 2 là kế hoạch, chưa được trình bày như kết quả đã hoàn tất.

---

## Slide 9 — Kiến trúc hệ thống đề xuất

```text
Dữ liệu bảng ─> FT-Transformer ───────┐
                                      ├─> Cross-Attention / Fusion ─> Classification Head
Ghi chú ─────> Clinical Text Encoder ─┘                                │
                                                                       v
                                                         Temperature Scaling / xác suất
                                                                       │
Hướng dẫn y khoa ─> Vector Store/Retriever ─> Agent giải thích <───────┘
                                                │
                                                v
                                 trích dẫn guideline + vị trí bằng chứng
```

**Mô tả thành phần**
- **Pipeline đầu vào:** khử định danh, khóa thời gian, xử lý dữ liệu khuyết và giữ thông tin nhóm nguồn.
- **Hai encoder:** FT-Transformer biểu diễn biến bảng; ClinicalBERT/Bio_ClinicalBERT biểu diễn ghi chú.
- **Fusion:** Cross-Attention dự kiến cho phép biểu diễn bảng truy vấn thông tin từ token văn bản; classification head tạo điểm số cho bốn lớp.
- **Calibration:** Temperature Scaling dự kiến điều chỉnh xác suất dựa trên validation; ngưỡng ECE là mục tiêu cần kiểm tra, không phải kết quả đã đạt của mô hình fusion.
- **Agentic RAG:** truy xuất guideline và neo giải thích vào văn bản nguồn; là kế hoạch Giai đoạn 2.

**Trạng thái hiện thực:** Baseline bảng/văn bản đã có; mô hình Cross-Attention hoàn chỉnh, hiệu chuẩn fusion, vector DB và agent chưa hoàn thành.

**Nguồn thiết kế:** `DEVELOPMENT_SPEC_MULTIMODAL_EHR_AI.md`, `docs/PROPOSED_OPTIMAL_SOLUTION.md`.

---

## Slide 10 — Dữ liệu và pipeline xây dựng lại

**Dữ liệu**
- Nguồn đầu vào: cohort tổng hợp Synthea và MTSamples.
- Bộ raw được tái tạo gồm 2.000 bản ghi, 500 mỗi lớp.
- Hai modality: dữ liệu bảng (nhân khẩu, sinh hiệu, xét nghiệm, tiền sử) và ghi chú lâm sàng đã xử lý.
- Tỷ lệ thiếu được báo cáo: WBC 20,5%; CRP 22,4%.

**Các bước chính**

```text
CSV nguồn → converter mới → khử/loại tín hiệu nhãn rủi ro → gắn nhóm nguồn
         → strict split → leakage audit → baseline và đánh giá
```

Converter mới loại ghi chú MTSamples trùng giữa nhãn, không tái sử dụng ghi chú theo vòng lặp khi hết nguồn, loại transcription/assessment khỏi đầu vào, che tên chẩn đoán đích và lưu `source_patient_group`, `source_note_group` phục vụ truy vết.

**Lưu ý:** Dataset là dữ liệu tổng hợp/kho công khai; các tỷ lệ này không mô tả tỷ lệ trong bệnh viện thực.

---

## Slide 11 — Chia tập strict và audit leakage

**Phương pháp:** Dùng connected components trên `source_patient_group` và `source_note_group`, giữ các mẫu liên kết bởi bệnh nhân nguồn hoặc ghi chú nguồn trong cùng một split.

| Tập | Số mẫu | ASTHMA | COPD | HEART_FAILURE | PNEUMONIA |
|---|---:|---:|---:|---:|---:|
| Huấn luyện | 1.425 | 358 | 358 | 340 | 369 |
| Xác thực | 273 | 71 | 71 | 54 | 77 |
| Kiểm thử | 302 | 71 | 71 | 106 | 54 |

**Kết quả audit**
- Giao nhau train/validation/test theo `patient_id`: **0**.
- Giao nhau theo `source_patient_group`: **0**.
- Giao nhau theo `source_note_group`: **0**.
- Tất cả tập có đủ bốn lớp; phân bố test không hoàn toàn cân bằng.

**Ý nghĩa và giới hạn:** Audit hỗ trợ kết luận không có giao nhau trên các khóa đã kiểm tra. Nó không chứng minh hết mọi dạng bias hoặc đảm bảo khả năng tổng quát hóa sang nguồn dữ liệu khác.

**Nguồn:** `data/rebuilt_strict_split_audit.json` và báo cáo strict split.

---

## Slide 12 — Thiết lập benchmark

**Ba baseline đơn phương thức**
- **CatBoost:** dữ liệu bảng; được chọn giữa CatBoost và XGBoost theo AUROC macro trên validation (0,9084 so với 0,8895).
- **FT-Transformer:** baseline deep learning trên dữ liệu bảng; hoàn thành 19 epochs.
- **Bio_ClinicalBERT:** ghi chú đã khử định danh; fine-tune block encoder cuối và classification head, tối đa 512 tokens, learning rate 2e-5, 5 epochs.

**Thiết lập chung được báo cáo**
- Seed 42; chạy bằng CUDA.
- Test strict: 302 mẫu, bốn lớp.
- Chỉ số: macro AUROC, macro AUPRC, macro-F1, accuracy, Brier score và ECE.
- AUROC/AUPRC macro cho phép tổng hợp hiệu năng theo lớp; F1/accuracy phản ánh phân loại tại ngưỡng quyết định; Brier/ECE phản ánh khía cạnh xác suất/calibration.

**Nguồn:** `data/rebuilt_strict_results_2026-10-28.json`.

---

## Slide 13 — Kết quả benchmark strict split

| Baseline | AUROC macro | AUPRC macro | F1 macro | Accuracy | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|
| CatBoost (bảng) | 0,9223 | 0,7872 | 0,6083 | 0,6854 | 0,3844 | 0,0663 |
| FT-Transformer (bảng) | 0,8976 | 0,7023 | 0,5789 | 0,6589 | 0,4725 | 0,1152 |
| Bio_ClinicalBERT (văn bản) | **0,9735** | **0,9314** | **0,8421** | **0,8543** | **0,2329** | **0,0373** |

**Diễn giải**
- Bio_ClinicalBERT là baseline tốt nhất trên tập strict test trong lần chạy này.
- CatBoost cao hơn FT-Transformer trong nhánh bảng ở các chỉ số được trình bày.
- ECE của ba mô hình lần lượt là 0,0663; 0,1152; 0,0373. Không phải cả ba đều dưới 0,05.
- Đây là kết quả trên test nội bộ của dữ liệu tổng hợp/kho công khai, không phải hiệu năng lâm sàng.

**Biểu đồ đề xuất:** ROC/PR curves và confusion matrix từ `data/rebuilt_strict_curves_2026-10-28.png`, `data/rebuilt_strict_confusion_2026-10-28.png`. Khi đặt hình, ghi rõ n=302 và tên tập test.

---

## Slide 14 — Điều chỉnh kết luận sau phát hiện leakage

**Nội dung chính**

Benchmark trước đó ghi nhận accuracy khoảng 94–98% hoặc cao hơn. Rà soát pipeline phát hiện nguy cơ ghi chú/cụm nguồn trùng giữa các tập, tín hiệu nhãn trực tiếp trong văn bản và một số quy tắc sinh dữ liệu phụ thuộc nhãn. Vì vậy, các điểm cũ không còn là kết luận khoa học chính.

Sanity check cây quyết định độ sâu 4 đạt accuracy **0,7285** trên strict test, thấp hơn rõ so với mức cũ khoảng 0,955. Đây là phép kiểm tra hỗ trợ nghi ngờ pipeline cũ được hưởng lợi từ leakage/lặp nguồn; hai con số không phải so sánh trực tiếp cùng mô hình hay cùng thiết lập.

**Thông điệp đánh giá:** Điểm số giảm sau khi làm chặt quy trình không đồng nghĩa mô hình mới kém hơn; nó phản ánh benchmark đã thay đổi để kiểm soát nguồn tốt hơn. Các kết luận hiện tại cần dựa trên lần chạy strict split mới.

---

## Slide 15 — Tiến độ hiện thực hệ thống

| Hạng mục | Trạng thái tại mốc báo cáo | Bằng chứng trong repository |
|---|---|---|
| Data schema/cấu hình và sinh dữ liệu nghiên cứu | Đã có | `configs/`, `scripts/generate_synthetic_ehr.py` |
| De-identification, temporal alignment, imputation, dataset loader | Có module mã nguồn | `src/data_pipeline/` |
| Chuyển đổi nguồn, strict split và audit | Đã chạy lại; audit strict hiện tại pass | `scripts/convert_sources_to_raw.py`, `scripts/audit_data_leakage.py`, `data/rebuilt_strict_split_audit.json` |
| Baseline và script benchmark | Đã có kết quả strict test | `src/models/baselines.py`, `scripts/run_baselines.py`, `data/rebuilt_strict_results_2026-10-28.json` |
| API và giao diện nền tảng | Có khung API, form và trang baseline | `src/api/`, `frontend/src/` |
| Cross-Attention fusion đã huấn luyện | Chưa hoàn thành | Giai đoạn 2, backlog 4 |
| RAG, guideline retrieval, evidence grounding | Chưa hoàn thành | Giai đoạn 2, backlog 5 |
| DCA, ngoại kiểm, đánh giá chuyên gia | Chưa hoàn thành | Giai đoạn 2, backlog 6 |
| Đóng gói end-to-end và demo hoàn chỉnh | Chưa hoàn thành | Giai đoạn 2, backlog 7 |

**Lưu ý trạng thái:** Có một module/khung phần mềm trong repository không đồng nghĩa luồng sản phẩm end-to-end đã tích hợp và nghiệm thu.

---

## Slide 16 — Giới hạn, rủi ro và kế hoạch Giai đoạn 2

**Giới hạn hiện tại**
- Dữ liệu tổng hợp/kho công khai không đại diện đầy đủ cho cohort bệnh viện hoặc quy trình ghi chép tại Việt Nam.
- Strict split giảm leakage theo nhóm nguồn đã biết nhưng không loại bỏ hoàn toàn domain/style bias.
- Chưa có bootstrap confidence interval, phân tích fairness đầy đủ, chọn ngưỡng theo chi phí lâm sàng hay đánh giá tiến cứu.
- Chưa có ngoại kiểm trên dữ liệu bệnh viện độc lập; không dùng mô hình để quyết định điều trị.

**Kế hoạch theo backlog**
1. **Backlog 4 — Multimodal core:** hiện thực encoder, Cross-Attention và calibration; so sánh tabular/text/concat/cross-attention trên cùng strict split; kiểm tra ablation.
2. **Backlog 5 — RAG và phần mềm:** ingest guideline, đánh giá retrieval, xây agent và evidence grounding; tích hợp API/UI.
3. **Backlog 6 — Đánh giá:** phân tích lỗi và calibration theo lớp, DCA, fairness; tổ chức chuyên gia/ngoại kiểm chỉ khi dữ liệu và phê duyệt phù hợp.
4. **Backlog 7 — Bàn giao:** Docker, tài liệu tái lập, báo cáo theo TRIPOD-AI và demo.

**Điều kiện để tiến tới đánh giá ứng dụng:** kết quả fusion ổn định, kiểm tra nguồn độc lập, đánh giá lâm sàng phù hợp, quản trị dữ liệu và phê duyệt cần thiết.

---

## Slide 17 — Kết luận và đề nghị đánh giá

**Kết luận**
- Đề tài xuất phát từ khoảng trống về khai thác đồng thời dữ liệu bảng và ghi chú, trong bối cảnh literature review nhấn mạnh rủi ro sai lệch và thiếu ngoại kiểm.
- Giai đoạn 1 đã hoàn thành nền tảng dữ liệu, pipeline và ba baseline; quy trình benchmark được xây dựng lại theo strict split và audit không phát hiện giao nhau trên các khóa nguồn đã kiểm tra.
- Bio_ClinicalBERT đứng đầu trong benchmark nội bộ hiện tại, nhưng chưa chứng minh giá trị lâm sàng.
- Giai đoạn 2 sẽ hiện thực và kiểm tra fusion, sau đó mới xây tầng RAG/giải thích và mở rộng đánh giá.

**Đề nghị giáo viên đánh giá**
- Tính phù hợp và khả thi của câu hỏi nghiên cứu/phạm vi bệnh mục tiêu.
- Tính hợp lý của thiết kế strict split và kế hoạch so sánh fusion với baseline.
- Mức ưu tiên các hạng mục Giai đoạn 2 và tiêu chí đánh giá đầu ra.

---

## Slide 18 — Tài liệu và artefact tham chiếu

**Tài liệu dự án**
- `docs/01_RESEARCH_BACKGROUND_AND_GAP.md` — literature review và khoảng trống nghiên cứu.
- `DEVELOPMENT_SPEC_MULTIMODAL_EHR_AI.md` — đặc tả hệ thống và module kỹ thuật mục tiêu.
- `docs/PROPOSED_OPTIMAL_SOLUTION.md` — kiến trúc đề xuất và luận cứ từ baseline.
- `tasks/README.md` — kế hoạch hai giai đoạn và backlog.
- `tasks/phase-01/` — kế hoạch Giai đoạn 1.
- `tasks/phase-02-development/` — kế hoạch backlog Giai đoạn 2.
- `docs/Bao cao M-CDSS - strict split 2026-10-28.docx` — báo cáo kết quả strict split.

**Artefact kết quả**
- `data/rebuilt_strict_results_2026-10-28.json` — kết quả benchmark.
- `data/rebuilt_strict_split_audit.json` — kết quả audit split.
- `data/rebuilt_strict_curves_2026-10-28.png` — ROC/PR curves.
- `data/rebuilt_strict_confusion_2026-10-28.png` — confusion matrix.

**Nguồn literature review:** Hunik et al., “Diagnostic prediction models for primary care, based on artificial intelligence and electronic health records: a systematic review,” JMIR Preprints 62862 (2024), tài liệu PDF trong `docs/`. Kiểm tra thông tin thư mục cuối cùng theo chính trang tiêu đề/bản xuất bản được sử dụng trước khi nộp slide.

---

## Phụ lục đề xuất

Nếu giáo viên cần xem sâu hơn, có thể thêm phụ lục sau Slide 18:

- Phân bố chi tiết từng lớp giữa train/validation/test.
- Định nghĩa AUROC, AUPRC, macro-F1, Brier score, ECE.
- Sơ đồ connected components và ví dụ split theo nhóm nguồn.
- Confusion matrix và các ca bất đồng giữa baseline bảng/văn bản đã khử định danh.
- Danh sách file/mã lệnh tái lập converter, audit và benchmark.
- Ma trận backlog: mục tiêu, phụ thuộc, deliverable, tiêu chí hoàn tất.

