
"""
Synthetic Clinical EHR Generator for Multimodal Clinical Decision Support System (M-CDSS)
Generates semi-synthetic EHR data for >= 2,000 patients including:
  1. Tabular clinical features (9 numerical + 4 categorical + diagnosis target)
  2. Free-text clinical notes with realistic pathology profiles and synthetic PHI/PII tokens
     for testing De-identification, Time-locking, and MICE Imputation pipelines.

Author: Member 2 (Biomedical Data & Privacy)
Date: Week 1, Phase 1
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


FIRST_NAMES_M = ["Văn", "Đức", "Minh", "Hồng", "Tuấn", "Hoàng", "Quốc", "Thành", "Bảo", "Hải"]
FIRST_NAMES_F = ["Thị", "Thu", "Ngọc", "Mai", "Phương", "Hương", "Lan", "Thảo", "Hà", "Trang"]
LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ"]
MIDDLE_NAMES = ["Văn", "Thị", "Hải", "Đăng", "Minh", "Khánh", "Thanh", "Hoài", "Gia", "Xuân"]

HOSPITALS = [
    "Bệnh viện Bạch Mai",
    "Bệnh viện Chợ Rẫy",
    "Bệnh viện Phổi Trung ương",
    "Bệnh viện Thống Nhất",
    "Bệnh viện Nhân dân Gia Định",
    "Bệnh viện Đại học Y Dược TP.HCM",
    "Bệnh viện Hữu nghị Việt Đức",
    "Bệnh viện Đa khoa Trung ương Cần Thơ"
]

DOCTORS = [
    "BS. Nguyễn Văn Hùng",
    "BS. CKII. Trần Thu Hà",
    "Bác sĩ Lê Minh Tâm",
    "BS. Phạm Hoàng Long",
    "ThS. BS. Vũ Quốc Tuấn",
    "BS. Đỗ Thị Mai Anh"
]

CITIES = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Huế", "Nha Trang"]


def generate_synthetic_data(num_patients: int = 2000, seed: int = 42) -> tuple[pd.DataFrame, list[dict]]:
    """
    Generate paired tabular EHR features and unstructured clinical notes with realistic clinical
    correlations, laboratory missingness, and HIPAA/Safe Harbor PHI entities.

    Args:
        num_patients: Total number of independent patient encounters to generate.
        seed: Random seed for reproducibility.

    Returns:
        tuple[pd.DataFrame, list[dict]]: (tabular_dataframe, clinical_notes_list)
    """
    np.random.seed(seed)
    random.seed(seed)

    records = []
    clinical_notes = []

    class_probs = [0.23, 0.27, 0.25, 0.25]
    diagnosis_labels = np.random.choice([0, 1, 2, 3], size=num_patients, p=class_probs)

    base_date = datetime(2026, 6, 1, 8, 0, 0)

    for i in range(num_patients):
        pid_num = i + 1
        patient_id = f"PT-{pid_num:05d}"
        encounter_id = f"ENC-{pid_num:05d}"
        diag_label = int(diagnosis_labels[i])

        enc_offset_days = random.randint(0, 90)
        enc_offset_hours = random.randint(7, 21)
        enc_offset_mins = random.randint(0, 59)
        enc_dt = base_date + timedelta(days=enc_offset_days, hours=enc_offset_hours, minutes=enc_offset_mins)
        
        diag_delay_mins = random.randint(90, 270)
        diag_dt = enc_dt + timedelta(minutes=diag_delay_mins)

        enc_str = enc_dt.isoformat()
        diag_str = diag_dt.isoformat()

        gender = np.random.choice(["M", "F", "OTHER"], p=[0.52, 0.46, 0.02])

       
        if gender == "M":
            full_name = f"{random.choice(LAST_NAMES)} {random.choice(FIRST_NAMES_M)} {random.choice(FIRST_NAMES_M)}"
        elif gender == "F":
            full_name = f"{random.choice(LAST_NAMES)} {random.choice(FIRST_NAMES_F)} {random.choice(FIRST_NAMES_F)}"
        else:
            full_name = f"{random.choice(LAST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(FIRST_NAMES_M)}"

        phone_prefix = random.choice(["090", "091", "098", "097", "088", "077", "036"])
        phone_num = f"{phone_prefix}{random.randint(1000000, 9999999)}"
        cccd_id = f"0{random.randint(10, 96):02d}{random.randint(0, 9)}{random.randint(10000000, 99999999)}"
        bhyt_code = f"DN4{random.randint(10, 99):02d}{random.randint(100000000, 999999999)}"
        hospital = random.choice(HOSPITALS)
        doctor = random.choice(DOCTORS)
        city = random.choice(CITIES)
        visit_date_formatted = enc_dt.strftime("%d/%m/%Y")

       
        if diag_label == 0: 
            age = int(np.clip(np.random.normal(38, 12), 18, 70))
            smoking_status = np.random.choice(["NEVER", "FORMER", "CURRENT"], p=[0.72, 0.18, 0.10])
            history_htn = int(np.random.choice([0, 1], p=[0.85, 0.15]))
            history_dm = int(np.random.choice([0, 1], p=[0.92, 0.08]))

            systolic_bp = float(np.clip(np.random.normal(118, 10), 90, 160))
            diastolic_bp = float(np.clip(np.random.normal(76, 7), 60, 95))
            heart_rate = float(np.clip(np.random.normal(86, 12), 60, 130))
            respiratory_rate = float(np.clip(np.random.normal(22, 3), 14, 34))
            spo2 = float(np.clip(np.random.normal(94.5, 2.2), 85, 99))
            temperature = float(np.clip(np.random.normal(36.8, 0.3), 36.2, 37.5))
            wbc_count = float(np.clip(np.random.normal(7.2, 1.8), 4.2, 13.0))
            crp = float(np.clip(np.random.exponential(2.5), 0.2, 15.0))

            chief_complaint = (
                f"Bệnh nhân {full_name} đến khám vì lên cơn khó thở dữ dội, rít cổ, khò khè tăng dần "
                f"sau khi hít phải bụi phấn hoặc thời tiết thay đổi đột ngột."
            )
            history_of_present_illness = (
                f"Bệnh nhân có tiền sử hen phế quản từ nhỏ và cơ địa dị ứng thời tiết. "
                f"Cách nhập viện 4 giờ, bệnh nhân xuất hiện khó thở thì thở ra, ho khan từng cơn, "
                f"phải dùng bình xịt cắt cơn nhưng đỡ ít. Không sốt, không đau tức ngực kiểu mạch vành. "
                f"Hồ sơ ghi nhận tại {hospital}, mã BHYT {bhyt_code}."
            )
            physical_examination = (
                f"Bệnh nhân tỉnh, tiếp xúc được, co kéo nhẹ cơ hô hấp phụ. "
                f"Khám tim mạch: Nhịp tim đều, T1 T2 rõ, tần số {int(heart_rate)} bpm, không tiếng thổi bệnh lý. "
                f"Khám phổi: Rì rào phế nang hai bên êm, nghe rải rác rale rít và rale ngáy cả hai phế trường thì thở ra. "
                f"Họng sạch, không phù ngoại vi."
            )
            prior_medications = "Salbutamol xịt 100mcg khi khó thở, Budesonide khí dung ngắt quãng."

        elif diag_label == 1:  
            age = int(np.clip(np.random.normal(67, 8), 45, 95))
            smoking_status = np.random.choice(["NEVER", "FORMER", "CURRENT"], p=[0.05, 0.55, 0.40])
            history_htn = int(np.random.choice([0, 1], p=[0.45, 0.55]))
            history_dm = int(np.random.choice([0, 1], p=[0.75, 0.25]))

            systolic_bp = float(np.clip(np.random.normal(132, 14), 100, 180))
            diastolic_bp = float(np.clip(np.random.normal(82, 9), 60, 105))
            heart_rate = float(np.clip(np.random.normal(88, 12), 65, 125))
            respiratory_rate = float(np.clip(np.random.normal(24, 4), 16, 38))
            spo2 = float(np.clip(np.random.normal(90.5, 3.2), 78, 96))
            temperature = float(np.clip(np.random.normal(37.0, 0.4), 36.4, 38.2))
            wbc_count = float(np.clip(np.random.normal(9.0, 2.5), 4.5, 17.0))
            crp = float(np.clip(np.random.exponential(8.0) + 2.0, 1.0, 45.0))

            chief_complaint = (
                f"Bệnh nhân {full_name} khó thở tiến triển khi gắng sức, ho khạc đờm nhầy trắng đục mạn tính, "
                f"đợt này khó thở tăng nặng hơn thường ngày."
            )
            history_of_present_illness = (
                f"Bệnh nhân có tiền sử hút thuốc lá hơn 30 bao-năm, được chẩn đoán COPD nhiều năm trước. "
                f"Trong 3 ngày gần đây xuất hiện khạc đờm tăng số lượng, đờm đổi màu vàng nhạt, "
                f"khó thở ngay cả khi đi bộ chậm trong nhà. Bệnh nhân có SĐT người nhà {phone_num}, "
                f"địa chỉ thường trú tại {city}. Thăm khám trực tiếp bởi {doctor} ngày {visit_date_formatted}."
            )
            physical_examination = (
                f"Thể trạng gầy, ngực hình thùng, lồng ngực di động kém theo nhịp thở. "
                f"Khám phổi: Rì rào phế nang giảm toàn bộ hai phế trường, nghe nhiều rale ngáy và rale rít lan tỏa thì thở ra. "
                f"Khám tim: T1, T2 mờ do khí phế thũng, không thấy rung miêu. Móng tay hơi khum, không phù chi."
            )
            prior_medications = "Tiotropium (Spiriva Respimat 2.5mcg), Formoterol/Budesonide xịt, Amlodipine 5mg."

        elif diag_label == 2:  
            age = int(np.clip(np.random.normal(71, 9), 48, 98))
            smoking_status = np.random.choice(["NEVER", "FORMER", "CURRENT"], p=[0.45, 0.35, 0.20])
            history_htn = int(np.random.choice([0, 1], p=[0.12, 0.88]))
            history_dm = int(np.random.choice([0, 1], p=[0.55, 0.45]))

            systolic_bp = float(np.clip(np.random.normal(152, 22), 110, 220))
            diastolic_bp = float(np.clip(np.random.normal(92, 12), 65, 125))
            heart_rate = float(np.clip(np.random.normal(96, 16), 65, 150))
            respiratory_rate = float(np.clip(np.random.normal(25, 4), 16, 40))
            spo2 = float(np.clip(np.random.normal(91.8, 3.0), 80, 97))
            temperature = float(np.clip(np.random.normal(36.7, 0.35), 36.1, 37.4))
            wbc_count = float(np.clip(np.random.normal(7.8, 2.0), 4.0, 14.0))
            crp = float(np.clip(np.random.exponential(6.0) + 1.0, 0.5, 35.0))

            chief_complaint = (
                f"Bệnh nhân {full_name} nhập viện vì khó thở kịch phát về đêm phải ngồi dậy để thở, "
                f"kèm phù hai chi dưới tăng nhanh trong tuần qua."
            )
            history_of_present_illness = (
                f"Bệnh nhân có tiền sử tăng huyết áp và đái tháo đường typ 2 trên 10 năm kiểm soát không đều. "
                f"Khoảng 5 ngày nay cảm thấy nặng ngực, khó thở tăng khi nằm ngửa, phải kê 2-3 gối đầu cao. "
                f"Hai mắt cá chân và cẳng chân sưng phù rõ, tăng cân 3kg trong 1 tuần. "
                f"Số CCCD đăng ký khám: {cccd_id}, tiếp nhận tại Khoa Cấp cứu {hospital}."
            )
            physical_examination = (
                f"Bệnh nhân khó thở, thở nhanh nông, tĩnh mạch cổ nổi tự nhiên ở tư thế Fowler 45 độ. "
                f"Phù mềm ấn lõm hai chi dưới đối xứng từ bàn chân đến 1/3 dưới cẳng chân. "
                f"Khám tim: Mỏm tim đập lệch ngoài đường giữa đòn trái liên sườn VI, tiếng T3 gallop nhẹ ở mỏm. "
                f"Khám phổi: Nghe rale ẩm nhỏ hạt và vừa hạt rải rác hai đáy phổi dâng lên 1/3 dưới phế trường."
            )
            prior_medications = "Furosemide 40mg/ngày, Enalapril 10mg, Metformin 850mg, Bisoprolol 2.5mg."

        else:  
            age = int(np.clip(np.random.normal(59, 16), 18, 94))
            smoking_status = np.random.choice(["NEVER", "FORMER", "CURRENT"], p=[0.45, 0.30, 0.25])
            history_htn = int(np.random.choice([0, 1], p=[0.60, 0.40]))
            history_dm = int(np.random.choice([0, 1], p=[0.78, 0.22]))

            systolic_bp = float(np.clip(np.random.normal(122, 16), 85, 175))
            diastolic_bp = float(np.clip(np.random.normal(75, 10), 50, 100))
            heart_rate = float(np.clip(np.random.normal(104, 15), 75, 155))
            respiratory_rate = float(np.clip(np.random.normal(26, 4), 18, 42))
            spo2 = float(np.clip(np.random.normal(91.0, 3.4), 78, 97))
            temperature = float(np.clip(np.random.normal(38.8, 0.7), 37.6, 40.8))
            wbc_count = float(np.clip(np.random.normal(16.5, 4.5), 10.5, 36.0))
            crp = float(np.clip(np.random.exponential(45.0) + 30.0, 15.0, 240.0))

            chief_complaint = (
                f"Bệnh nhân {full_name} sốt cao liên tục kèm rét run, ho khạc đờm màu gỉ sắt và đau nhói ngực khi hít sâu."
            )
            history_of_present_illness = (
                f"Bệnh khởi phát cấp tính 2 ngày trước với triệu chứng sốt nóng lạnh thất thường (nhiệt độ cặp nách lên tới 39.5 độ C), "
                f"ho nhiều kèm đờm đặc màu vàng sẫm hoặc gỉ sắt, đau ngực bên phải tăng khi ho hoặc hít sâu. "
                f"Bệnh nhân đã tự uống thuốc hạ sốt nhưng không đỡ. Đăng ký khám bởi người nhà (SĐT {phone_num}), "
                f"bác sĩ điều trị ban đầu: {doctor} tại {hospital} vào ngày {visit_date_formatted}."
            )
            physical_examination = (
                f"Bệnh nhân vẻ mặt nhiễm trùng rõ, môi khô, lưỡi bẩn, sốt cao vã mồ hôi. "
                f"Khám phổi: Rung thanh tăng ở vùng đáy phổi phải, gõ đục nhẹ liên sườn VIII-IX đường nách sau. "
                f"Nghe phổi thấy tiếng cọ màng phổi nhẹ và rất nhiều rale ẩm to hạt, vừa hạt khu trú đáy phổi phải. "
                f"Khám tim: Tim đập nhanh nhịp xoang tần số {int(heart_rate)} bpm, tiếng tim rõ, không tiếng thổi."
            )
            prior_medications = "Paracetamol 500mg uống ngắt quãng, Cefuroxime axetil 500mg."

        if np.random.rand() < 0.20:
            crp = np.nan
        if np.random.rand() < 0.15:
            wbc_count = np.nan
        raw_text = (
            f"HỒ SƠ BỆNH ÁN ĐIỆN TỬ - {hospital.upper()}\n"
            f"Ngày tiếp nhận: {visit_date_formatted} | Bác sĩ khám: {doctor}\n"
            f"Bệnh nhân: {full_name} | Giới tính: {gender} | Tuổi: {age}\n"
            f"Số CMND/CCCD: {cccd_id} | Thẻ BHYT: {bhyt_code} | Điện thoại liên hệ: {phone_num}\n"
            f"Nơi cư trú: {city}, Việt Nam\n\n"
            f"1. LÝ DO KHÁM BỆNH (CHIEF COMPLAINT):\n{chief_complaint}\n\n"
            f"2. BỆNH SỬ (HISTORY OF PRESENT ILLNESS):\n{history_of_present_illness}\n\n"
            f"3. KHÁM LÂM SÀNG (PHYSICAL EXAMINATION):\n{physical_examination}\n\n"
            f"4. TIỀN SỬ VÀ THUỐC ĐANG DÙNG (PRIOR MEDICATIONS):\n{prior_medications}\n"
            f"Dự kiến hội chẩn lúc: {diag_dt.strftime('%H:%M %d/%m/%Y')}."
        )

        record = {
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "encounter_timestamp": enc_str,
            "diagnostic_confirmed_timestamp": diag_str,
            "age": int(round(age)),
            "systolic_bp": round(float(systolic_bp), 1),
            "diastolic_bp": round(float(diastolic_bp), 1),
            "heart_rate": round(float(heart_rate), 1),
            "respiratory_rate": round(float(respiratory_rate), 1),
            "spo2": round(float(spo2), 1),
            "temperature": round(float(temperature), 1),
            "wbc_count": round(float(wbc_count), 2) if not np.isnan(wbc_count) else np.nan,
            "crp": round(float(crp), 2) if not np.isnan(crp) else np.nan,
            "gender": str(gender),
            "smoking_status": str(smoking_status),
            "history_hypertension": int(history_htn),
            "history_diabetes": int(history_dm),
            "diagnosis_label": int(diag_label)
        }
        records.append(record)

        clinical_note = {
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "encounter_timestamp": enc_str,
            "diagnostic_confirmed_timestamp": diag_str,
            "raw_text": raw_text,
            "chief_complaint": chief_complaint,
            "history_of_present_illness": history_of_present_illness,
            "physical_examination_notes": physical_examination,
            "prior_medications": prior_medications
        }
        clinical_notes.append(clinical_note)

    df = pd.DataFrame(records)
    return df, clinical_notes


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic EHR data for M-CDSS Phase 1")
    parser.add_argument("--num_samples", type=int, default=2000, help="Number of patient samples to generate")
    parser.add_argument("--output_dir", type=str, default="data/raw", help="Output directory for raw data")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    parquet_path = os.path.join(args.output_dir, "patients_raw.parquet")
    jsonl_path = os.path.join(args.output_dir, "clinical_notes_raw.jsonl")

    print(f"[*] Generating {args.num_samples} synthetic patient records (seed={args.seed})...")
    df, notes = generate_synthetic_data(num_patients=args.num_samples, seed=args.seed)

    print(f"[*] Saving tabular data to: {parquet_path}")
    df.to_parquet(parquet_path, index=False, engine="pyarrow")

    print(f"[*] Saving clinical notes to: {jsonl_path}")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(json.dumps(note, ensure_ascii=False) + "\n")

    print("[+] Data generation completed successfully:")
    print(f"    - Patients DataFrame shape: {df.shape}")
    print(f"    - Target class distribution: \n{df['diagnosis_label'].value_counts().to_dict()}")
    print(f"    - Missingness rate in WBC: {df['wbc_count'].isna().mean():.1%}")
    print(f"    - Missingness rate in CRP: {df['crp'].isna().mean():.1%}")
    print(f"    - Total clinical notes: {len(notes)}")


if __name__ == "__main__":
    main()
