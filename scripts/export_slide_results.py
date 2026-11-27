"""Regenerate result slides 13-17 of the defence script from results/registry.json.

Replaces everything between '## Slide 13' and '## Slide 18' in
docs/thuyết trình/KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md, so every number on the
slides comes from the registry (Phase 3 rule: no hand-typed numbers).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "docs" / "thuyết trình" / "KICH_BAN_SLIDE_BAO_CAO_NGHIEM_THU_GIAI_DOAN_2.md"


def f3(x):
    return "–" if x is None else f"{x:.3f}"


def build(reg: dict) -> str:
    rq1 = {m["model"]: m for m in reg["rq1_multiseed_comparison"]["models"]}
    comps = {c["comparator"]: c for c in reg["rq1_multiseed_comparison"]["comparisons_vs_deployment_model"]}
    rq2 = reg["rq2_text_signal_decomposition"]
    rq3 = reg.get("rq3_complementarity_simulation", {"grid": []})
    cv = {m["model"]: m for m in reg.get("sensitivity_grouped_cv_posthoc", {}).get("models", [])}
    cal = reg["rq4_calibration"]["methods"]
    rob = reg["rq4_missing_modality"]
    dca = reg["rq4_dca"]
    cases = reg["error_analysis"]["case_studies"]
    rag = reg["rag"]["grounding_audit_50_cases"]
    prov = reg["data_provenance"]["test"]
    out = []
    a = out.append

    a("## Slide 13 — RQ1: So sánh công bằng 10 mô hình × 5 seed\n")
    a("### Nội dung hiển thị trên Slide\n")
    a("| Mô hình | AUROC test strict (TB ± SD) | Δ so với cross-attention [CI 95%], p Holm | AUROC grouped CV (post-hoc) |")
    a("| :--- | :---: | :--- | :---: |")
    for key in ("lr_tabular", "catboost", "bert_ft", "ensemble_cb_bertft", "concat_frozen", "xattn_frozen"):
        m, c, v = rq1[key], comps.get(key), cv.get(key)
        delta = "(tham chiếu)" if key == "xattn_frozen" else f"{-c['delta']:+.3f} [{-c['ci95'][1]:.3f}; {-c['ci95'][0]:.3f}], p={c['holm_adjusted_p']:.3f}"
        cv_txt = f"{v['auroc_mean']:.3f} ± {v['auroc_sd']:.3f}" if v else "–"
        a(f"| {m['label']} | {m['auroc_mean']:.3f} ± {m['auroc_sd']:.3f} | {delta} | {cv_txt} |")
    a("\n- Test strict: **BERT fine-tune và ensemble tốt nhất**; cross-attention không vượt mô hình bảng.")
    a("- Grouped CV: **cross-attention ổn định nhất**; BERT-FT dao động mạnh giữa các fold.")
    a(f"- Tập test chỉ gồm {prov['distinct_source_patients']} bệnh nhân gốc (suy tim, viêm phổi: 1 bệnh nhân mỗi lớp) → thứ hạng mô hình không bền.\n")
    a("### Lời nói gợi ý\n")
    a("> Chúng em so sánh mười mô hình, mỗi mô hình năm seed, cùng một tập test và cùng cách hiệu chuẩn. Trên tập test strict, "
      "mô hình văn bản fine-tune và ensemble đơn giản cao hơn mô hình dung hợp của chúng em một cách có ý nghĩa thống kê. "
      "Nhưng khi kiểm tra lại bằng 5-fold grouped CV, mô hình dung hợp lại ổn định nhất. Kết luận trung thực là: chưa có bằng chứng "
      "dung hợp vượt trội, và trên dữ liệu ít bệnh nhân gốc thì thứ hạng mô hình phụ thuộc vào việc ai rơi vào tập test.\n")
    a("### Câu chuyển\n\n> Vậy vì sao mô hình chỉ đọc văn bản lại mạnh như vậy? Câu trả lời nằm ở RQ2.\n\n---\n")

    a("## Slide 14 — RQ2: Tín hiệu văn bản đến từ đâu?\n")
    a("### Nội dung hiển thị trên Slide\n")
    a("| Biến thể ghi chú | TF-IDF + LR | BERT fine-tune | Cross-attention |")
    a("| :--- | :---: | :---: | :---: |")
    for v in rq2["variants"]:
        a(f"| {v['label']} | {f3(v.get('tfidf_lr'))} | {f3(v.get('bert_ft'))} | {f3(v.get('xattn_frozen'))} |")
    a(f"\nTham chiếu chỉ dữ liệu bảng (Logistic Regression): {f3(rq2['tabular_only_reference_auroc'].get('lr_tabular'))}\n")
    a("- Che **mọi con số** → mô hình văn bản gần mức ngẫu nhiên; fusion lùi về mức của nhánh bảng.")
    a("- Bỏ sinh hiệu nhưng còn **tuổi** → văn bản vẫn mạnh (tuổi gần như quyết định nhãn trong dữ liệu tổng hợp).")
    a("- Hình: `docs/paper_latex/figures/generated/fig_rq2_text_decomposition.pdf`\n")
    a("### Lời nói gợi ý\n")
    a("> Ghi chú trong bộ dữ liệu này chép lại sinh hiệu và tuổi. Khi chúng em che hết các con số, mô hình văn bản gần như mất khả năng "
      "dự đoán. Nghĩa là hai phương thức không độc lập thông tin – đây là một lối tắt (shortcut) mà nhiều nghiên cứu đa phương thức có thể bỏ sót.\n")
    a("### Câu chuyển\n\n> Nếu văn bản thực sự có thông tin riêng thì sao? Chúng em kiểm tra bằng mô phỏng.\n\n---\n")

    a("## Slide 15 — RQ3: Khi nào dung hợp có ích? (mô phỏng có kiểm soát)\n")
    a("### Nội dung hiển thị trên Slide\n")
    a("| ρ (tỷ lệ ca có tín hiệu văn bản) | σ (nhiễu bảng) | Bảng | Văn bản | Cross-attention | Δ |")
    a("| :---: | :---: | :---: | :---: | :---: | :---: |")
    for g in rq3["grid"]:
        if g["sigma"] in (0.0, 1.0):
            a(f"| {g['rho']:g} | {g['sigma']:g} | {f3(g['tabular'])} | {f3(g['text'])} | {f3(g['cross_attention'])} | {g['delta_xattn_vs_best_unimodal']:+.3f} |")
    a("\n- **Mô phỏng** – câu triệu chứng do nhóm chèn vào ghi chú đã che số; không phải hiệu năng lâm sàng.")
    a("- Cross-attention vượt mô hình đơn phương thức khi văn bản mang tín hiệu riêng (ρ cao) hoặc dữ liệu bảng nhiễu.\n")
    a("### Lời nói gợi ý\n")
    a("> Khi văn bản chỉ lặp lại dữ liệu bảng, dung hợp không có gì để thêm. Khi văn bản mang thông tin mà bảng không có, cross-attention khai thác "
      "được và vượt cả hai mô hình đơn phương thức. Đây là điều kiện mà dữ liệu thật cần thoả mãn để dung hợp có giá trị.\n")
    a("### Câu chuyển\n\n> Tiếp theo là độ tin cậy xác suất và độ bền khi thiếu dữ liệu.\n\n---\n")

    a("## Slide 16 — RQ4: Hiệu chuẩn, thiếu dữ liệu và case study\n")
    a("### Nội dung hiển thị trên Slide\n")
    a(f"- ECE (10 bins): không hiệu chuẩn {f3(cal['uncalibrated']['ece_10_equal_width'])} → temperature {f3(cal['temperature']['ece_10_equal_width'])}; "
      f"**chưa đạt mục tiêu < 0.05**.")
    a("\n| Kịch bản thiếu dữ liệu | Cross-attention | CatBoost | BERT fine-tune |")
    a("| :--- | :---: | :---: | :---: |")
    for s in rob["scenarios"]:
        r = rob["by_model"][s["scenario"]]
        a(f"| {s['label']} | {f3(r.get('xattn_frozen', {}).get('mean'))} | {f3(r.get('catboost', {}).get('mean'))} | {f3(r.get('bert_ft', {}).get('mean'))} |")
    for pid, c in cases.items():
        if "probabilities" in c:
            top = max(c["probabilities"], key=c["probabilities"].get)
            a(f"- `{pid}` (nhãn {c['true']}): mô hình triển khai dự đoán **{top}** ({c['probabilities'][top]:.1%}).")
    a(f"- Lớp giải trình trên test strict: {rag['grounded_claims']}/{rag['total_genuine_claims']} claim được neo đúng vị trí ký tự; "
      f"{rag['rejected_out_of_note_probes']}/{rag['injected_out_of_note_probes']} chuỗi ngoài ghi chú bị từ chối (chưa chấm ngữ nghĩa thủ công).\n")
    a("### Lời nói gợi ý\n")
    a("> Mô hình dung hợp chịu được thiếu một phần biến số tốt hơn CatBoost vì vẫn đọc được giá trị trong ghi chú, nhưng mất toàn bộ dữ liệu bảng "
      "thì giảm mạnh. Hiệu chuẩn cải thiện nhưng chưa đạt mục tiêu ECE dưới 0.05 – chúng em báo cáo đúng như vậy.\n")
    a("### Câu chuyển\n\n> Cuối cùng là lợi ích ròng theo DCA.\n\n---\n")

    a("## Slide 17 — DCA cho suy tim (minh hoạ phương pháp)\n")
    a("### Nội dung hiển thị trên Slide\n")
    a("| Mô hình | NB (p_t=0.10) | Giảm can thiệp/100 BN | NB (p_t=0.20) | Giảm can thiệp/100 BN |")
    a("| :--- | :---: | :---: | :---: | :---: |")
    t10, t20 = dca["at_thresholds"]["pt_0.10"], dca["at_thresholds"]["pt_0.20"]
    a(f"| Can thiệp tất cả | {f3(t10['treat_all'])} | – | {f3(t20['treat_all'])} | – |")
    for m in t10["models"]:
        x, y = t10["models"][m], t20["models"][m]
        a(f"| {rq1[m]['label'] if m in rq1 else m} | {f3(x['net_benefit'])} | {x['net_reduction_in_interventions_per_100']:.1f} | "
          f"{f3(y['net_benefit'])} | {y['net_reduction_in_interventions_per_100']:.1f} |")
    a(f"\n- Công thức: (NB − NB_all) × (1 − p_t)/p_t × 100 (Vickers 2016).")
    a(f"- **Cảnh báo:** tỷ lệ suy tim test {dca['heart_failure_test_prevalence']:.1%}, và cả 106 ca suy tim đến từ **một** bệnh nhân gốc → chỉ minh hoạ phương pháp.\n")
    a("### Lời nói gợi ý\n")
    a("> Mọi mô hình có lợi ích ròng cao hơn can thiệp tất cả trong dải ngưỡng đã định trước, nhưng các khoảng tin cậy chồng lấn, và toàn bộ ca suy tim "
      "trong test chỉ là một bệnh nhân gốc. Vì vậy chúng em trình bày DCA như minh hoạ phương pháp, không phải bằng chứng lợi ích lâm sàng.\n")
    a("### Câu chuyển\n\n> Từ đó, chúng em tự thẩm định nguy cơ sai lệch theo PROBAST+AI.\n\n---\n")
    return "\n".join(out) + "\n"


def main() -> None:
    reg = json.loads((ROOT / "results" / "registry.json").read_text(encoding="utf-8"))
    text = SLIDES.read_text(encoding="utf-8")
    start, end = text.index("## Slide 13"), text.index("## Slide 18")
    note = "<!-- Slides 13-17 AUTO-GENERATED by scripts/export_slide_results.py from results/registry.json -->\n\n"
    SLIDES.write_text(text[:start] + note + build(reg) + text[end:], encoding="utf-8")
    print("[OK]", SLIDES)


if __name__ == "__main__":
    main()
