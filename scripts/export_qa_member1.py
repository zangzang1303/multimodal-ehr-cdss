"""Write the Member 1 defence Q&A (model & results) from results/registry.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "thuyết trình" / "QA_MO_HINH_VA_KET_QUA_MEMBER_1.md"


def main() -> None:
    r = json.loads((ROOT / "results" / "registry.json").read_text(encoding="utf-8"))
    m = {x["model"]: x for x in r["rq1_multiseed_comparison"]["models"]}
    c = {x["comparator"]: x for x in r["rq1_multiseed_comparison"]["comparisons_vs_deployment_model"]}
    cv = {x["model"]: x for x in r["sensitivity_grouped_cv_posthoc"]["models"]}
    v = {x["variant"]: x for x in r["rq2_text_signal_decomposition"]["variants"]}
    cal = r["rq4_calibration"]["methods"]
    prov = r["data_provenance"]
    x, b, e, lr = m["xattn_frozen"], m["bert_ft"], m["ensemble_cb_bertft"], m["lr_tabular"]
    qa = [
        ("Vì sao cross-attention không vượt BERT fine-tune và ensemble?",
         f"Trên test strict, BERT-FT đạt {b['auroc_mean']:.3f} ± {b['auroc_sd']:.3f}, ensemble {e['auroc_mean']:.3f}, cross-attention "
         f"{x['auroc_mean']:.3f} ± {x['auroc_sd']:.3f} (Δ {c['bert_ft']['delta']:+.3f}, p Holm {c['bert_ft']['holm_adjusted_p']:.3f}). "
         f"RQ2 cho thấy ghi chú chép lại sinh hiệu và tuổi, nên nhánh văn bản đã chứa gần đủ thông tin; fusion không có gì thêm. "
         f"Trong grouped CV, cross-attention lại ổn định nhất ({cv['xattn_frozen']['auroc_mean']:.3f} ± {cv['xattn_frozen']['auroc_sd']:.3f} "
         f"so với BERT-FT {cv['bert_ft']['auroc_mean']:.3f} ± {cv['bert_ft']['auroc_sd']:.3f}) – thứ hạng không bền trên dữ liệu ít bệnh nhân gốc."),
        ("Làm sao biết không rò rỉ nhãn?",
         "Bốn lớp kiểm tra: (1) chia theo nhóm bệnh nhân gốc và nhóm ghi chú nguồn, audit 0 giao nhau; (2) tên chẩn đoán được che "
         "([REDACTED_DIAGNOSIS]) và audit tự động đếm 0% ghi chú còn tên chẩn đoán; (3) audit ghi chú nguồn bị dùng lại mang thông tin nhãn = 0%; "
         f"(4) RQ2: che mọi con số thì TF-IDF chỉ còn {v['num_masked']['tfidf_lr']:.3f}. Chính các kiểm tra này đã phát hiện và loại bộ dữ liệu "
         "trung gian 2026-11-18 (TF-IDF che số đạt 0.962 – dấu hiệu rò rỉ)."),
        ("ECE là gì, vì sao chưa < 0.05, temperature khớp trên đâu?",
         f"ECE là chênh lệch trung bình giữa độ tin cậy dự đoán và tỷ lệ đúng thực tế theo bin. Temperature scaling khớp trên validation "
         f"(N=273), giảm ECE từ {cal['uncalibrated']['ece_10_equal_width']:.3f} xuống {cal['temperature']['ece_10_equal_width']:.3f}; vector "
         f"scaling ({cal['vector_scaling']['ece_10_equal_width']:.3f}) và isotonic ({cal['isotonic_ovr']['ece_10_equal_width']:.3f}) không tốt hơn. "
         "Validation nhỏ và test có phân bố khác validation nên chưa đạt mục tiêu – báo cáo đúng như vậy."),
        ("Vì sao AUROC cao mà Macro-F1/accuracy thấp?",
         f"AUROC đo khả năng xếp hạng ở mọi ngưỡng; F1 dùng argmax tại một ngưỡng. Cross-attention: AUROC {x['auroc_mean']:.3f} nhưng F1 "
         f"{x['f1_mean']:.3f} vì lỗi tập trung ở một bệnh nhân viêm phổi gốc (42/62 lỗi) bị đoán thành hen do lối tắt tuổi."),
        ("Mô hình chỉ dùng dữ liệu bảng đơn giản có tốt không?",
         f"Logistic Regression đạt {lr['auroc_mean']:.3f}, không khác cross-attention (p Holm {c['lr_tabular']['holm_adjusted_p']:.3f}). "
         "Trên dữ liệu này, mô hình đơn giản là baseline rất mạnh."),
        ("Dữ liệu có đủ lớn không?",
         f"2.000 bản ghi nhưng chỉ {sum(prov[s]['distinct_source_patients'] for s in ('train','val','test'))} bệnh nhân Synthea gốc; tập test có "
         f"{prov['test']['distinct_source_patients']} bệnh nhân gốc, trong đó suy tim và viêm phổi mỗi lớp 1 bệnh nhân. CI bootstrap theo bản ghi "
         "vì vậy hẹp hơn độ bất định thực; đây là giới hạn lớn nhất của nghiên cứu."),
        ("Nếu có MIMIC-IV, kỳ vọng thay đổi thế nào?",
         "Ghi chú thật chứa mô tả triệu chứng, bệnh sử, đáp ứng điều trị không có trong dữ liệu bảng – đúng điều kiện RQ3 cho thấy cross-attention có lợi. "
         "Kỳ vọng hiệu năng tuyệt đối thấp hơn (không còn lối tắt tuổi/bệnh nhân lặp lại) nhưng đóng góp của văn bản thật sự đo được. Cần tái kiểm tra RQ2 "
         "(che số) trên dữ liệu đó."),
        ("Checkpoint triển khai được chọn thế nào, có cherry-pick không?",
         f"Quy tắc đăng ký trước: cross-attention BERT đóng băng, seed có NLL validation thấp nhất (seed {r['metadata']['deployment_seed']}); "
         "chọn trước khi xem test. Hash kế hoạch phân tích được đóng băng tại results/preregistration/."),
    ]
    lines = ["# Q&A PHẦN MÔ HÌNH & KẾT QUẢ (THÀNH VIÊN 1)", "",
             "> Sinh tự động từ `results/registry.json` bằng `scripts/export_qa_member1.py`. Trả lời ≤ 3 câu, có số liệu.", ""]
    for i, (q, a) in enumerate(qa, 1):
        lines += [f"**{i}. {q}**", "", a, ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("[OK]", OUT)


if __name__ == "__main__":
    main()
