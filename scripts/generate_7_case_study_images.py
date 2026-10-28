"""
Script to generate 7 high-resolution, professionally styled images for M-CDSS Phase 1 Report:
1. 01_benchmark_metrics_post_train.png - Post-train Benchmark Metrics Table
2. 02_case1_pt0044_tabular_data.png    - Case 1 (PT-0044) Tabular Vitals & Features
3. 03_case1_pt0044_clinical_text.png    - Case 1 (PT-0044) Clinical EHR Note
4. 04_case2_pt0254_tabular_data.png    - Case 2 (PT-0254) Tabular Vitals & Features
5. 05_case2_pt0254_clinical_text.png    - Case 2 (PT-0254) Clinical EHR Note
6. 06_case1_pt0044_model_predictions.png - Case 1 Model Predictions (Tabular vs Text)
7. 07_case2_pt0254_model_predictions.png - Case 2 Model Predictions (Tabular vs Text)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set global typography
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'

OUTPUT_DIR = "docs/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_card(ax, xy, width, height, bg_color='#ffffff', border_color='#e2e8f0', corner_radius=0.03, lw=1.5):
    """Draw a rounded rectangular card on axis."""
    box = patches.FancyBboxPatch(
        xy, width, height,
        boxstyle=f"round,pad=0.0,rounding_size={corner_radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=lw,
        transform=ax.transAxes,
        zorder=2
    )
    ax.add_patch(box)
    return box


def draw_badge(ax, xy, text, bg_color='#0284c7', text_color='#ffffff', font_size=10):
    """Draw a pill-shaped badge with text."""
    ax.text(
        xy[0], xy[1], f"  {text}  ",
        fontsize=font_size, fontweight='bold', color=text_color,
        ha='left', va='center', transform=ax.transAxes, zorder=5,
        bbox=dict(boxstyle="round,pad=0.32", facecolor=bg_color, edgecolor="none")
    )


# ==============================================================================
# IMAGE 1: BENCHMARK METRICS POST-TRAIN
# ==============================================================================
def create_image_1():
    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    # Main Card
    draw_card(ax, (0.02, 0.02), 0.96, 0.96, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Top Header Banner
    draw_badge(ax, (0.05, 0.92), "M-CDSS GIAI ĐOẠN 1 • BENCHMARK EVALUATION", bg_color='#1e293b', text_color='#38bdf8', font_size=10)
    ax.text(0.05, 0.865, "KẾT QUẢ BENCHMARK CÁC MÔ HÌNH SAU HUẤN LUYỆN (STRICT SPLIT)", 
            fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.05, 0.825, "Đánh giá độc lập trên 302 mẫu test — Tách biệt nhóm nguồn chống rò rỉ dữ liệu (Seed: 42)", 
            fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.05, 0.95], [0.79, 0.79], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # Table Layout
    headers = ["Baseline Mô hình", "Phương thức dữ liệu", "Macro AUROC", "Macro AUPRC", "Macro F1", "Accuracy", "Brier Score", "ECE"]
    col_x =   [0.06,              0.25,                  0.48,          0.57,          0.66,       0.75,       0.83,          0.90]
    
    # Table Header Box
    draw_card(ax, (0.045, 0.71), 0.91, 0.06, bg_color='#f1f5f9', border_color='#cbd5e1', corner_radius=0.01)
    for h, x in zip(headers, col_x):
        ax.text(x, 0.74, h, fontsize=10.5, fontweight='bold', color='#334155', va='center', transform=ax.transAxes)

    # Rows Data
    rows = [
        ("CatBoost", "Bảng số học (Tabular)", "0.9223", "0.7872", "0.6083", "68.54%", "0.3844", "0.0663", False),
        ("FT-Transformer", "Bảng số học sâu (Tabular Deep)", "0.8976", "0.7023", "0.5789", "65.89%", "0.4725", "0.1152", False),
        ("Bio_ClinicalBERT", "Văn bản lâm sàng (Clinical Notes)", "0.9735", "0.9314", "0.8421", "85.43%", "0.2329", "0.0373", True),
    ]

    row_y = [0.63, 0.53, 0.43]
    for (m_name, m_mod, auroc, auprc, f1, acc, brier, ece, is_best), y in zip(rows, row_y):
        bg = '#eff6ff' if is_best else '#ffffff'
        border = '#2563eb' if is_best else '#e2e8f0'
        lw = 2.0 if is_best else 1.0
        draw_card(ax, (0.045, y - 0.035), 0.91, 0.075, bg_color=bg, border_color=border, corner_radius=0.01, lw=lw)

        color = '#1d4ed8' if is_best else '#0f172a'
        fw = 'bold' if is_best else 'normal'

        ax.text(col_x[0], y, m_name, fontsize=11, fontweight='bold', color='#0f172a', va='center', transform=ax.transAxes)
        ax.text(col_x[1], y, m_mod, fontsize=10, color='#475569', va='center', transform=ax.transAxes)
        ax.text(col_x[2], y, auroc, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)
        ax.text(col_x[3], y, auprc, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)
        ax.text(col_x[4], y, f1, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)
        ax.text(col_x[5], y, acc, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)
        ax.text(col_x[6], y, brier, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)
        ax.text(col_x[7], y, ece, fontsize=11, fontweight=fw, color=color, va='center', transform=ax.transAxes)

    # 3 Summary Cards at Bottom with proper vertical breathing room
    card_y = 0.08
    card_h = 0.26

    # Card 1: Best Model
    draw_card(ax, (0.045, card_y), 0.285, card_h, bg_color='#f0fdf4', border_color='#86efac', corner_radius=0.015, lw=1.5)
    draw_badge(ax, (0.065, 0.30), "MÔ HÌNH XUẤT SẮC NHẤT", bg_color='#16a34a', font_size=9)
    ax.text(0.065, 0.245, "Bio_ClinicalBERT", fontsize=13, fontweight='bold', color='#14532d', transform=ax.transAxes)
    ax.text(0.065, 0.13, "• AUROC: 0.9735 | Acc: 85.43%\n• Macro F1: 0.8421\n• Brier Score thấp nhất (0.2329)\n• Nắm bắt xuất sắc bệnh sử văn bản", 
            fontsize=9.8, color='#15803d', linespacing=1.4, transform=ax.transAxes)

    # Card 2: Tabular Comparison
    draw_card(ax, (0.355, card_y), 0.285, card_h, bg_color='#f8fafc', border_color='#cbd5e1', corner_radius=0.015, lw=1.5)
    draw_badge(ax, (0.375, 0.30), "SO SÁNH NHÁNH BẢNG SỐ", bg_color='#475569', font_size=9)
    ax.text(0.375, 0.245, "CatBoost > FT-Transformer", fontsize=13, fontweight='bold', color='#1e293b', transform=ax.transAxes)
    ax.text(0.375, 0.13, "• CatBoost vượt trội +2.65% Acc\n• AUROC cao hơn (0.9223 vs 0.8976)\n• Gradient Boosted Trees tối ưu hơn\n  mạng nơ-ron sâu trên tabular y sinh", 
            fontsize=9.8, color='#475569', linespacing=1.4, transform=ax.transAxes)

    # Card 3: Calibration
    draw_card(ax, (0.665, card_y), 0.29, card_h, bg_color='#fefce8', border_color='#fde047', corner_radius=0.015, lw=1.5)
    draw_badge(ax, (0.685, 0.30), "HIỆU CHUẨN XÁC SUẤT (ECE)", bg_color='#ca8a04', font_size=9)
    ax.text(0.685, 0.245, "Độ tin cậy xác suất dự đoán", fontsize=13, fontweight='bold', color='#713f12', transform=ax.transAxes)
    ax.text(0.685, 0.13, "• BERT đạt ECE thấp nhất: 0.0373\n• CatBoost đạt ECE: 0.0663\n• FT-Transformer kém nhất: 0.1152\n• Đánh giá calibration tin cậy", 
            fontsize=9.8, color='#854d0e', linespacing=1.4, transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "01_benchmark_metrics_post_train.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 2: CASE 1 (PT-0044) TABULAR DATA
# ==============================================================================
def create_image_2():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 1 • DỮ LIỆU ĐẦU VÀO PHƯƠNG THỨC BẢNG SỐ", bg_color='#0284c7', text_color='#ffffff', font_size=10)
    ax.text(0.06, 0.85, "Hồ sơ Bảng số học (Structured EHR Tabular) — PT-0044", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Mã bệnh nhân: PT-0044 | Mã đợt khám: ENC-0044 | Cơ sở tiếp nhận: Bệnh viện Thống Nhất", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # Grid of Tabular Values
    items = [
        ("Tuổi & Giới tính", "18 tuổi • Nữ (F)", "Nhân khẩu học vị thành niên", '#f1f5f9', '#475569'),
        ("Huyết áp (Blood Pressure)", "106.2 / 78.0 mmHg", "Giới hạn sinh lý bình thường", '#f1f5f9', '#475569'),
        ("Nhịp tim (Heart Rate)", "70.6 bpm", "Nhịp xoang đều, bình thường", '#f1f5f9', '#475569'),
        ("Nhịp thở (Respiratory Rate)", "12.8 lần/phút", "Không có thở nhanh nông", '#f1f5f9', '#475569'),
        ("Độ bão hòa Oxy (SpO2)", "97.3 %", "Bình thường ngoài cơn co thắt", '#f0fdf4', '#16a34a'),
        ("Thân nhiệt (Body Temp)", "37.7 °C", "Sốt nhẹ không có nhiễm trùng cấp", '#f1f5f9', '#475569'),
        ("Bạch cầu (WBC Count)", "4.78 × 10⁹/L", "Trong khoảng chuẩn [4.0 - 10.0]", '#f1f5f9', '#475569'),
        ("Chỉ số Viêm CRP (C-Reactive)", "24.28 mg/L  (!) TĂNG CAO", "Phản ứng viêm tăng mạnh gây nhiễu", '#fef2f2', '#dc2626'),
        ("Tiền sử Hút thuốc", "NEVER (Không bao giờ)", "Loại trừ yếu tố nguy cơ thuốc lá", '#f0fdf4', '#16a34a'),
        ("Bệnh nền (Comorbidities)", "Tăng HA: 1 (CÓ) | Đái tháo đường: 0", "Có cờ bệnh lý tim mạch", '#fffbeb', '#b45309'),
    ]

    coords = [
        (0.06, 0.63), (0.51, 0.63),
        (0.06, 0.49), (0.51, 0.49),
        (0.06, 0.35), (0.51, 0.35),
        (0.06, 0.21), (0.51, 0.21),
        (0.06, 0.07), (0.51, 0.07),
    ]

    for (label, val, note, bg, bcolor), (x, y) in zip(items, coords):
        draw_card(ax, (x, y), 0.43, 0.11, bg_color=bg, border_color=bcolor, corner_radius=0.015, lw=1.2)
        ax.text(x + 0.02, y + 0.075, label, fontsize=10, fontweight='bold', color='#64748b', transform=ax.transAxes)
        ax.text(x + 0.02, y + 0.040, val, fontsize=13, fontweight='bold', color='#0f172a', transform=ax.transAxes)
        ax.text(x + 0.02, y + 0.015, note, fontsize=9.5, color='#475569', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "02_case1_pt0044_tabular_data.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 3: CASE 1 (PT-0044) CLINICAL TEXT NOTE
# ==============================================================================
def create_image_3():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 1 • DỮ LIỆU ĐẦU VÀO PHƯƠNG THỨC VĂN BẢN", bg_color='#8b5cf6', text_color='#ffffff', font_size=10)
    ax.text(0.06, 0.85, "Ghi chú Lâm sàng Tự do (Unstructured Clinical Note) — PT-0044", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Trích xuất từ hệ thống bệnh án điện tử EHR | Đã khử định danh tuân thủ HIPAA Safe Harbor", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # EHR Document Container
    draw_card(ax, (0.06, 0.20), 0.88, 0.54, bg_color='#fafafa', border_color='#94a3b8', corner_radius=0.015, lw=1.5)

    # EHR Header inside
    draw_card(ax, (0.07, 0.63), 0.86, 0.09, bg_color='#1e293b', border_color='#0f172a', corner_radius=0.01)
    ax.text(0.09, 0.69, "CLINICAL ENCOUNTER NOTE - BỆNH VIỆN THỐNG NHẤT", fontsize=12, fontweight='bold', color='#38bdf8', transform=ax.transAxes)
    ax.text(0.09, 0.65, "Patient ID: PT-0044 | Encounter ID: ENC-0044 | Patient Name: Đặng Thu Mai | Age: 18 | Gender: F | Attending: ThS.BS. Trần Thị Mai", 
            fontsize=9.5, color='#cbd5e1', transform=ax.transAxes)

    # Sections inside EHR
    ehr_text = [
        ("CHIEF COMPLAINT:", "Patient Đặng Thu Mai presents for evaluation of acute/subacute respiratory condition."),
        ("HISTORY OF PRESENT ILLNESS:", "Patient 18yo presents on 12/05/1984 with cough, shortness of breath, and fatigue."),
        ("PHYSICAL EXAMINATION:", "BP: 106.2/78.0 mmHg, HR: 70.6 bpm, SpO2: 97.3%. Auscultation of lungs reveals bilateral breath sounds."),
        ("MEDICATIONS (ĐƠN THUỐC):", "Inhalers and cardiovascular medications as prescribed. (Đang dùng ống hít định liều)")
    ]

    y_pos = [0.55, 0.45, 0.35, 0.25]
    for (sec_title, sec_content), y in zip(ehr_text, y_pos):
        is_med = "MEDICATIONS" in sec_title
        color_title = '#b91c1c' if is_med else '#0369a1'
        ax.text(0.09, y + 0.035, sec_title, fontsize=10.5, fontweight='bold', color=color_title, transform=ax.transAxes)
        
        if is_med:
            draw_card(ax, (0.085, y - 0.015), 0.83, 0.045, bg_color='#fef2f2', border_color='#fca5a5', corner_radius=0.008)
            ax.text(0.09, y, sec_content, fontsize=11, fontweight='bold', color='#991b1b', transform=ax.transAxes)
        else:
            ax.text(0.09, y, sec_content, fontsize=10.5, color='#1e293b', transform=ax.transAxes)

    # Bottom Tag Summary
    draw_card(ax, (0.06, 0.06), 0.88, 0.11, bg_color='#eff6ff', border_color='#93c5fd', corner_radius=0.012)
    ax.text(0.08, 0.13, "CÁC THỰC THỂ NGỮ NGHĨA THEN CHỐT ĐƯỢC BIO_CLINICALBERT TRÍCH XUẤT:", fontsize=10.5, fontweight='bold', color='#1e40af', transform=ax.transAxes)
    ax.text(0.08, 0.09, "• [Độ tuổi]: 18yo (Thanh thiếu niên)   • [Triệu chứng]: Ho (Cough), Khó thở (Shortness of breath)   • [Thuốc]: Inhalers (Thuốc hít cắt cơn Hen)", 
            fontsize=11, fontweight='bold', color='#1d4ed8', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "03_case1_pt0044_clinical_text.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 4: CASE 2 (PT-0254) TABULAR DATA
# ==============================================================================
def create_image_4():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 2 • DỮ LIỆU ĐẦU VÀO PHƯƠNG THỨC BẢNG SỐ", bg_color='#0284c7', text_color='#ffffff', font_size=10)
    ax.text(0.06, 0.85, "Hồ sơ Bảng số học (Structured EHR Tabular) — PT-0254", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Mã bệnh nhân: PT-0254 | Mã đợt khám: ENC-0254 | Cơ sở tiếp nhận: Bệnh viện Chợ Rẫy", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # Grid of Tabular Values
    items = [
        ("Tuổi & Giới tính", "65 tuổi • Nữ (F)", "Nhân khẩu học người cao tuổi", '#f1f5f9', '#475569'),
        ("Huyết áp (Blood Pressure)", "115.9 / 80.1 mmHg", "Hoàn toàn ổn định, không có cơn tăng HA", '#f0fdf4', '#16a34a'),
        ("Nhịp tim (Heart Rate)", "64.3 bpm", "Nhịp chậm/bình thường, không có nhịp nhanh phản xạ", '#f0fdf4', '#16a34a'),
        ("Nhịp thở (Respiratory Rate)", "11.5 lần/phút", "Nhịp thở bình thường ở bệnh nhân mở khí quản", '#f1f5f9', '#475569'),
        ("Độ bão hòa Oxy (SpO2)", "95.6 %", "Oxy máu ở ngưỡng ổn định mạn tính", '#f0fdf4', '#16a34a'),
        ("Thân nhiệt (Body Temp)", "37.8 °C", "Sốt nhẹ không có hội chứng nhiễm trùng cấp", '#f1f5f9', '#475569'),
        ("Bạch cầu (WBC Count)", "4.30 × 10⁹/L", "Bạch cầu bình thường [4.0 - 10.0]", '#f0fdf4', '#16a34a'),
        ("Chỉ số Viêm CRP", "7.14 mg/L", "Tăng nhẹ phản ứng mạn tính", '#f1f5f9', '#475569'),
        ("Tiền sử Hút thuốc", "NEVER (Không)", "Không có tiền sử thuốc lá trực tiếp", '#f1f5f9', '#475569'),
        ("Bệnh nền (Comorbidities)", "Tăng HA: 0 (KHÔNG) | Đái tháo đường: 0", "Không ghi nhận tiền sử tăng huyết áp", '#f0fdf4', '#16a34a'),
    ]

    coords = [
        (0.06, 0.63), (0.51, 0.63),
        (0.06, 0.49), (0.51, 0.49),
        (0.06, 0.35), (0.51, 0.35),
        (0.06, 0.21), (0.51, 0.21),
        (0.06, 0.07), (0.51, 0.07),
    ]

    for (label, val, note, bg, bcolor), (x, y) in zip(items, coords):
        draw_card(ax, (x, y), 0.43, 0.11, bg_color=bg, border_color=bcolor, corner_radius=0.015, lw=1.2)
        ax.text(x + 0.02, y + 0.075, label, fontsize=10, fontweight='bold', color='#64748b', transform=ax.transAxes)
        ax.text(x + 0.02, y + 0.040, val, fontsize=13, fontweight='bold', color='#0f172a', transform=ax.transAxes)
        ax.text(x + 0.02, y + 0.015, note, fontsize=9.5, color='#475569', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "04_case2_pt0254_tabular_data.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 5: CASE 2 (PT-0254) CLINICAL TEXT NOTE
# ==============================================================================
def create_image_5():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 2 • DỮ LIỆU ĐẦU VÀO PHƯƠNG THỨC VĂN BẢN", bg_color='#8b5cf6', text_color='#ffffff', font_size=10)
    ax.text(0.06, 0.85, "Ghi chú Lâm sàng Tự do (Unstructured Clinical Note) — PT-0254", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Trích xuất từ Bệnh viện Chợ Rẫy | Áp dụng che nhãn bệnh [REDACTED_DIAGNOSIS] chống rò rỉ dữ liệu", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # EHR Document Container
    draw_card(ax, (0.06, 0.20), 0.88, 0.54, bg_color='#fafafa', border_color='#94a3b8', corner_radius=0.015, lw=1.5)

    # EHR Header inside
    draw_card(ax, (0.07, 0.63), 0.86, 0.09, bg_color='#1e293b', border_color='#0f172a', corner_radius=0.01)
    ax.text(0.09, 0.69, "ELECTRONIC HEALTH RECORD - BỆNH VIỆN CHỢ RẪY", fontsize=12, fontweight='bold', color='#38bdf8', transform=ax.transAxes)
    ax.text(0.09, 0.65, "Patient ID: PT-0254 | Encounter ID: ENC-0254 | Name: Huỳnh Phương Mai | Age: 65 | Gender: F | Physician: BS.CKI. Đỗ Quốc Tuấn", 
            fontsize=9.5, color='#cbd5e1', transform=ax.transAxes)

    # Sections inside EHR - text wrapped properly
    ehr_text = [
        ("CHIEF COMPLAINT:", "Patient referred for evaluation of tracheostomy tube placement and treatment recommendations."),
        ("HISTORY OF PRESENT ILLNESS:", "Suffering from end-stage [REDACTED_DIAGNOSIS], required tracheostomy tube placement 3 months ago\nwhen being treated for acute exacerbation. Resides in extended care facility with capped tube..."),
        ("PHYSICAL EXAMINATION:", "Vital signs recorded. Auscultation of lungs reveals bilateral breath sounds with intermittent crackles/wheezes.\nHeart shows regular rhythm. (Nghe phổi có rale rít/rale ẩm rải rác)"),
        ("MEDICATIONS LIST:", "Prevacid, folic acid, aspirin, morphine sulfate, Pulmicort, Risperdal, Colace, clonazepam, prednisone...")
    ]

    y_pos = [0.55, 0.43, 0.31, 0.21]
    for (sec_title, sec_content), y in zip(ehr_text, y_pos):
        ax.text(0.09, y + 0.04, sec_title, fontsize=10.5, fontweight='bold', color='#0369a1', transform=ax.transAxes)
        ax.text(0.09, y, sec_content, fontsize=9.8, color='#1e293b', linespacing=1.3, transform=ax.transAxes)

    # Bottom Tag Summary
    draw_card(ax, (0.06, 0.06), 0.88, 0.11, bg_color='#fef2f2', border_color='#fca5a5', corner_radius=0.012)
    ax.text(0.08, 0.13, "CÁC YẾU TỐ NGỮ NGHĨA GÂY NHIỄU (SEMANTIC CONFUSION) CHO BIO_CLINICALBERT:", fontsize=10.5, fontweight='bold', color='#991b1b', transform=ax.transAxes)
    ax.text(0.08, 0.09, "• Tên bệnh bị che [REDACTED]   • Nghe phổi có rale ẩm/rale rít (crackles/wheezes)   • Nằm viện dưỡng lão & dùng aspirin -> Bị nhầm sang SUY TIM", 
            fontsize=10.2, fontweight='bold', color='#b91c1c', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "05_case2_pt0254_clinical_text.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 6: CASE 1 (PT-0044) MODEL PREDICTIONS
# ==============================================================================
def create_image_6():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 1 • KẾT QUẢ DỰ ĐOÁN ĐỐI CHỨNG", bg_color='#1e293b', text_color='#38bdf8', font_size=10)
    ax.text(0.06, 0.85, "So sánh Dự đoán Mô hình — Bệnh nhân PT-0044", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Bệnh án: PT-0044 | ENC-0044 | Cơ sở: Bệnh viện Thống Nhất | Tập kiểm thử độc lập (Strict Test)", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # Ground Truth Banner
    draw_card(ax, (0.06, 0.67), 0.88, 0.08, bg_color='#ecfdf5', border_color='#10b981', corner_radius=0.01, lw=2)
    ax.text(0.08, 0.71, "NHÃN CHẨN ĐOÁN THỰC TẾ (GROUND TRUTH):", fontsize=12, fontweight='bold', color='#065f46', va='center', transform=ax.transAxes)
    ax.text(0.48, 0.71, "ASTHMA  (Hen phế quản)", fontsize=14, fontweight='bold', color='#047857', va='center', transform=ax.transAxes)

    # Comparison Columns: Left = Tabular (Wrong), Right = Text (Correct)
    # Left Box: Tabular (CatBoost) - WRONG
    draw_card(ax, (0.06, 0.18), 0.42, 0.46, bg_color='#fef2f2', border_color='#ef4444', corner_radius=0.015, lw=2)
    draw_badge(ax, (0.08, 0.59), "MÔ HÌNH BẢNG SỐ • DỰ ĐOÁN SAI", bg_color='#dc2626', text_color='#ffffff', font_size=10)
    ax.text(0.08, 0.53, "Mô hình: CatBoost (Tabular)", fontsize=13, fontweight='bold', color='#7f1d1d', transform=ax.transAxes)
    ax.text(0.08, 0.47, "Kết quả dự đoán:", fontsize=11, color='#991b1b', transform=ax.transAxes)
    ax.text(0.08, 0.42, "COPD", fontsize=20, fontweight='bold', color='#b91c1c', transform=ax.transAxes)
    ax.text(0.20, 0.42, "(Độ tin cậy: 78.82%)", fontsize=12, fontweight='bold', color='#7f1d1d', transform=ax.transAxes)

    ax.plot([0.08, 0.46], [0.38, 0.38], color='#fca5a5', lw=1, transform=ax.transAxes)
    ax.text(0.08, 0.34, "Nguyên nhân điểm mù số học:", fontsize=10.5, fontweight='bold', color='#991b1b', transform=ax.transAxes)
    ax.text(0.08, 0.20, "• CRP tăng cao (24.28 mg/L) + tiền sử tăng HA\n  khiến cây quyết định thiên lệch sang COPD.\n• Thiếu hô hấp ký (FEV1), bảng số không thể\n  nhận diện tính chất co thắt có hồi phục.\n• SpO2 97.3% bình thường gây nhầm lẫn.", 
            fontsize=9.8, color='#7f1d1d', linespacing=1.35, transform=ax.transAxes)

    # Right Box: Clinical Text (Bio_ClinicalBERT) - CORRECT
    draw_card(ax, (0.52, 0.18), 0.42, 0.46, bg_color='#f0fdf4', border_color='#22c55e', corner_radius=0.015, lw=2)
    draw_badge(ax, (0.54, 0.59), "MÔ HÌNH VĂN BẢN • DỰ ĐOÁN ĐÚNG", bg_color='#16a34a', text_color='#ffffff', font_size=10)
    ax.text(0.54, 0.53, "Mô hình: Bio_ClinicalBERT (Text)", fontsize=13, fontweight='bold', color='#14532d', transform=ax.transAxes)
    ax.text(0.54, 0.47, "Kết quả dự đoán:", fontsize=11, color='#166534', transform=ax.transAxes)
    ax.text(0.54, 0.42, "ASTHMA", fontsize=20, fontweight='bold', color='#15803d', transform=ax.transAxes)
    ax.text(0.70, 0.42, "(Độ tin cậy: 85.80%)", fontsize=12, fontweight='bold', color='#14532d', transform=ax.transAxes)

    ax.plot([0.54, 0.92], [0.38, 0.38], color='#86efac', lw=1, transform=ax.transAxes)
    ax.text(0.54, 0.34, "Cơ chế thành công của mô hình ngôn ngữ:", fontsize=10.5, fontweight='bold', color='#166534', transform=ax.transAxes)
    ax.text(0.54, 0.20, "• Nắm bắt thực thể tuổi trẻ (18yo) trong văn bản.\n• Bắt trúng từ khóa điều trị then chốt: 'Inhalers'\n  (thuốc hít định liều - phác đồ chuẩn của Hen).\n• Hiểu ngữ cảnh cơn ho khó thở ngoại trú,\n  đưa ra dự đoán chính xác với xác suất 85.80%.", 
            fontsize=9.8, color='#14532d', linespacing=1.35, transform=ax.transAxes)

    # Bottom Takeaway Banner
    draw_card(ax, (0.06, 0.05), 0.88, 0.10, bg_color='#eff6ff', border_color='#93c5fd', corner_radius=0.01)
    ax.text(0.08, 0.11, "ĐỀ XUẤT FUSION GIAI ĐOẠN 2:", fontsize=11, fontweight='bold', color='#1e40af', transform=ax.transAxes)
    ax.text(0.08, 0.07, "Cơ chế Cross-Attention sẽ dùng vector ngữ nghĩa 'Inhalers' từ ghi chú bác sĩ để triệt tiêu sự ngộ nhận do chỉ số CRP từ bảng số.", 
            fontsize=10.5, color='#1e3a8a', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "06_case1_pt0044_model_predictions.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


# ==============================================================================
# IMAGE 7: CASE 2 (PT-0254) MODEL PREDICTIONS
# ==============================================================================
def create_image_7():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
    ax.set_facecolor('#f8fafc')
    ax.axis('off')

    draw_card(ax, (0.03, 0.03), 0.94, 0.94, bg_color='#ffffff', border_color='#cbd5e1', corner_radius=0.02, lw=2)

    # Header
    draw_badge(ax, (0.06, 0.91), "CASE STUDY 2 • KẾT QUẢ DỰ ĐOÁN ĐỐI CHỨNG", bg_color='#1e293b', text_color='#38bdf8', font_size=10)
    ax.text(0.06, 0.85, "So sánh Dự đoán Mô hình — Bệnh nhân PT-0254", fontsize=18, fontweight='bold', color='#0f172a', transform=ax.transAxes)
    ax.text(0.06, 0.81, "Bệnh án: PT-0254 | ENC-0254 | Cơ sở: Bệnh viện Chợ Rẫy | Tập kiểm thử độc lập (Strict Test)", fontsize=11, color='#64748b', transform=ax.transAxes)

    ax.plot([0.06, 0.94], [0.77, 0.77], color='#e2e8f0', lw=1.5, transform=ax.transAxes)

    # Ground Truth Banner
    draw_card(ax, (0.06, 0.67), 0.88, 0.08, bg_color='#ecfdf5', border_color='#10b981', corner_radius=0.01, lw=2)
    ax.text(0.08, 0.71, "NHÃN CHẨN ĐOÁN THỰC TẾ (GROUND TRUTH):", fontsize=12, fontweight='bold', color='#065f46', va='center', transform=ax.transAxes)
    ax.text(0.48, 0.71, "COPD  (Bệnh phổi tắc nghẽn mạn tính)", fontsize=14, fontweight='bold', color='#047857', va='center', transform=ax.transAxes)

    # Comparison Columns: Left = Text (Wrong), Right = Tabular (Correct)
    # Left Box: Clinical Text (Bio_ClinicalBERT) - WRONG
    draw_card(ax, (0.06, 0.18), 0.42, 0.46, bg_color='#fef2f2', border_color='#ef4444', corner_radius=0.015, lw=2)
    draw_badge(ax, (0.08, 0.59), "MÔ HÌNH VĂN BẢN • DỰ ĐOÁN SAI", bg_color='#dc2626', text_color='#ffffff', font_size=10)
    ax.text(0.08, 0.53, "Mô hình: Bio_ClinicalBERT (Text)", fontsize=13, fontweight='bold', color='#7f1d1d', transform=ax.transAxes)
    ax.text(0.08, 0.47, "Kết quả dự đoán:", fontsize=11, color='#991b1b', transform=ax.transAxes)
    ax.text(0.08, 0.42, "HEART_FAILURE", fontsize=18, fontweight='bold', color='#b91c1c', transform=ax.transAxes)
    ax.text(0.30, 0.42, "(Độ tin cậy: 58.99%)", fontsize=11, fontweight='bold', color='#7f1d1d', transform=ax.transAxes)

    ax.plot([0.08, 0.46], [0.38, 0.38], color='#fca5a5', lw=1, transform=ax.transAxes)
    ax.text(0.08, 0.34, "Nguyên nhân điểm mù ngôn ngữ:", fontsize=10.5, fontweight='bold', color='#991b1b', transform=ax.transAxes)
    ax.text(0.08, 0.20, "• Tên bệnh bị che [REDACTED_DIAGNOSIS]\n  để kiểm soát rò rỉ dữ liệu.\n• Văn bản có từ vựng nặng nề: mở khí quản,\n  suy hô hấp mạn, viện dưỡng lão, rale ẩm/rít.\n• Bối cảnh này trùng lặp với suy tim mạn,\n  khiến NLP bị 'nhiễu từ vựng' đoán sai.", 
            fontsize=9.8, color='#7f1d1d', linespacing=1.35, transform=ax.transAxes)

    # Right Box: Tabular (CatBoost) - CORRECT
    draw_card(ax, (0.52, 0.18), 0.42, 0.46, bg_color='#f0fdf4', border_color='#22c55e', corner_radius=0.015, lw=2)
    draw_badge(ax, (0.54, 0.59), "MÔ HÌNH BẢNG SỐ • DỰ ĐOÁN ĐÚNG", bg_color='#16a34a', text_color='#ffffff', font_size=10)
    ax.text(0.54, 0.53, "Mô hình: CatBoost (Tabular)", fontsize=13, fontweight='bold', color='#14532d', transform=ax.transAxes)
    ax.text(0.54, 0.47, "Kết quả dự đoán:", fontsize=11, color='#166534', transform=ax.transAxes)
    ax.text(0.54, 0.42, "COPD", fontsize=20, fontweight='bold', color='#15803d', transform=ax.transAxes)
    ax.text(0.66, 0.42, "(Độ tin cậy: 75.22%)", fontsize=12, fontweight='bold', color='#14532d', transform=ax.transAxes)

    ax.plot([0.54, 0.92], [0.38, 0.38], color='#86efac', lw=1, transform=ax.transAxes)
    ax.text(0.54, 0.34, "Cơ chế thành công của mô hình bảng số:", fontsize=10.5, fontweight='bold', color='#166534', transform=ax.transAxes)
    ax.text(0.54, 0.20, "• Đóng vai trò 'mỏ neo huyết động học' chuẩn xác.\n• Huyết áp (115.9/80.1) & nhịp tim (64.3 bpm) ổn định,\n  hoàn toàn loại trừ cơn tăng áp hay nhịp nhanh suy tim.\n• SpO2 95.6%, thân nhiệt 37.8°C, CRP 7.14 mg/L\n  khớp chính xác bệnh cảnh COPD mạn tính ổn định.", 
            fontsize=9.8, color='#14532d', linespacing=1.35, transform=ax.transAxes)

    # Bottom Takeaway Banner
    draw_card(ax, (0.06, 0.05), 0.88, 0.10, bg_color='#eff6ff', border_color='#93c5fd', corner_radius=0.01)
    ax.text(0.08, 0.11, "ĐỀ XUẤT FUSION GIAI ĐOẠN 2:", fontsize=11, fontweight='bold', color='#1e40af', transform=ax.transAxes)
    ax.text(0.08, 0.07, "Bảng số học đóng vai trò 'mỏ neo sinh lý' (physiological anchor), ngăn mô hình ngôn ngữ không bị lạc hướng khi gặp từ vựng bệnh nặng.", 
            fontsize=10.5, color='#1e3a8a', transform=ax.transAxes)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "07_case2_pt0254_model_predictions.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Created: {out_path}")


if __name__ == "__main__":
    print("Generating 7 images for M-CDSS Phase 1 Report...")
    create_image_1()
    create_image_2()
    create_image_3()
    create_image_4()
    create_image_5()
    create_image_6()
    create_image_7()
    print("ALL 7 IMAGES SUCCESSFULLY GENERATED IN docs/images/!")
