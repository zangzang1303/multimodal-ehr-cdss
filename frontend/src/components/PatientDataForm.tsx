"use client";

import React, { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Database,
  FileSpreadsheet,
  FileText,
  Info,
  Play,
  RotateCcw,
  Sparkles,
  Stethoscope,
} from "lucide-react";
import {
  BaselineInferenceResponse,
  PatientInferenceRequest,
  predictBaselines,
  TabularFeatures,
} from "@/lib/api";

interface FieldMeta {
  key: keyof Pick<
    TabularFeatures,
    | "age"
    | "systolic_bp"
    | "diastolic_bp"
    | "heart_rate"
    | "respiratory_rate"
    | "spo2"
    | "temperature"
    | "wbc_count"
    | "crp"
  >;
  label: string;
  unit: string;
  min: number;
  max: number;
  normalMin: number;
  normalMax: number;
  step?: string;
}

const NUMERICAL_FIELDS: FieldMeta[] = [
  {
    key: "age",
    label: "Tuổi (Age)",
    unit: "năm",
    min: 18,
    max: 110,
    normalMin: 18,
    normalMax: 65,
    step: "1",
  },
  {
    key: "systolic_bp",
    label: "Huyết áp tâm thu (Systolic BP)",
    unit: "mmHg",
    min: 60,
    max: 240,
    normalMin: 90,
    normalMax: 130,
    step: "1",
  },
  {
    key: "diastolic_bp",
    label: "Huyết áp tâm trương (Diastolic BP)",
    unit: "mmHg",
    min: 40,
    max: 140,
    normalMin: 60,
    normalMax: 85,
    step: "1",
  },
  {
    key: "heart_rate",
    label: "Nhịp tim (Heart Rate)",
    unit: "bpm",
    min: 30,
    max: 220,
    normalMin: 60,
    normalMax: 100,
    step: "1",
  },
  {
    key: "respiratory_rate",
    label: "Nhịp thở (Respiratory Rate)",
    unit: "lần/phút",
    min: 8,
    max: 50,
    normalMin: 12,
    normalMax: 20,
    step: "1",
  },
  {
    key: "spo2",
    label: "Độ bão hòa oxy (SpO2)",
    unit: "%",
    min: 60,
    max: 100,
    normalMin: 95,
    normalMax: 100,
    step: "0.5",
  },
  {
    key: "temperature",
    label: "Nhiệt độ (Temperature)",
    unit: "°C",
    min: 35.0,
    max: 42.0,
    normalMin: 36.5,
    normalMax: 37.5,
    step: "0.1",
  },
  {
    key: "wbc_count",
    label: "Bạch cầu (WBC Count)",
    unit: "10⁹/L",
    min: 1.0,
    max: 50.0,
    normalMin: 4.0,
    normalMax: 10.0,
    step: "0.1",
  },
  {
    key: "crp",
    label: "Chỉ số viêm (CRP)",
    unit: "mg/L",
    min: 0.0,
    max: 300.0,
    normalMin: 0.0,
    normalMax: 5.0,
    step: "0.1",
  },
];

const INITIAL_TABULAR: TabularFeatures = {
  age: 45,
  systolic_bp: 120,
  diastolic_bp: 80,
  heart_rate: 75,
  respiratory_rate: 16,
  spo2: 98,
  temperature: 36.8,
  wbc_count: 6.5,
  crp: 1.5,
  gender: "M",
  smoking_status: "NEVER",
  history_hypertension: 0,
  history_diabetes: 0,
};

const SAMPLE_PATIENT_TABULAR: TabularFeatures = {
  age: 65,
  systolic_bp: 145,
  diastolic_bp: 90,
  heart_rate: 94,
  respiratory_rate: 24,
  spo2: 91,
  temperature: 37.2,
  wbc_count: 8.8,
  crp: 16.5,
  gender: "M",
  smoking_status: "CURRENT",
  history_hypertension: 1,
  history_diabetes: 0,
};

const SAMPLE_PATIENT_NOTES =
  "Bệnh nhân nam 65 tuổi, tiền sử hút thuốc lá 30 bao-năm, tăng huyết áp điều trị không thường xuyên. Vào viện vì khó thở tăng dần khi gắng sức kèm ho khạc đờm trắng đục kéo dài 1 tuần nay, khó thở nhiều hơn khi nằm ngửa.\n\n" +
  "Khám thực thể: Lồng ngực hình thùng, rì rào phế nang giảm hai đáy phổi, rale rít và rale ngáy thì thở ra rải rác. Nhịp tim nhanh đều, tiếng T1 T2 rõ, không tiếng thổi bệnh lý. Phù nhẹ hai chi dưới.";

export default function PatientDataForm() {
  const [tabular, setTabular] = useState<TabularFeatures>(INITIAL_TABULAR);
  const [patientId, setPatientId] = useState<string>("PT-001");
  const [clinicalNotes, setClinicalNotes] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [predictionResponse, setPredictionResponse] =
    useState<BaselineInferenceResponse | null>(null);

  const handleNumericalChange = (key: keyof TabularFeatures, value: string) => {
    const num = parseFloat(value);
    setTabular((prev) => ({
      ...prev,
      [key]: isNaN(num) ? 0 : num,
    }));
  };

  const isOutOfNormalRange = (meta: FieldMeta): boolean => {
    const val = tabular[meta.key] as number;
    return val < meta.normalMin || val > meta.normalMax;
  };

  const handleLoadSample = () => {
    setPatientId("PT-001");
    setTabular(SAMPLE_PATIENT_TABULAR);
    setClinicalNotes(SAMPLE_PATIENT_NOTES);
    setError(null);
  };

  const handleReset = () => {
    setTabular(INITIAL_TABULAR);
    setClinicalNotes("");
    setPredictionResponse(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate systolic > diastolic
    if (tabular.systolic_bp <= tabular.diastolic_bp) {
      setError("Huyết áp tâm thu phải lớn hơn huyết áp tâm trương!");
      setLoading(false);
      return;
    }

    try {
      const payload: PatientInferenceRequest = {
        patient_id: patientId,
        tabular_features: tabular,
        clinical_notes: clinicalNotes,
      };

      const result = await predictBaselines(payload);
      setPredictionResponse(result);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Không thể kết nối với Backend API");
      }
    } finally {
      setLoading(false);
    }
  };

  const getDiseaseLabelBadge = (disease: string) => {
    switch (disease) {
      case "COPD":
        return {
          name: "COPD (Bệnh phổi tắc nghẽn mạn)",
          color: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
        };
      case "ASTHMA":
        return {
          name: "ASTHMA (Hen phế quản)",
          color: "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20",
        };
      case "CONGESTIVE_HEART_FAILURE":
        return {
          name: "CHF (Suy tim sung huyết)",
          color: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
        };
      case "COMMUNITY_ACQUIRED_PNEUMONIA":
        return {
          name: "CAP (Viêm phổi mắc phải cộng đồng)",
          color: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
        };
      default:
        return {
          name: disease,
          color: "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20",
        };
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Form Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold">
            <Stethoscope className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              Nhập Liệu Lâm Sàng Cho Bác Sĩ (Clinical Data Intake)
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Nhập song song chỉ số sinh hiệu, xét nghiệm và ghi chú diễn tiến lâm sàng
            </p>
          </div>
        </div>

        {/* Demo Controls */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleLoadSample}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-sky-200 dark:border-sky-800 bg-sky-50 hover:bg-sky-100 dark:bg-sky-950/40 dark:hover:bg-sky-900/40 text-sky-700 dark:text-sky-300 text-xs font-semibold transition-all shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-500" />
            Load Sample Patient
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition-all shadow-sm"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main 2-Column Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* CỘT TRÁI: Dữ Liệu Bảng Số (Tabular Features) */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-slate-900 dark:text-white font-semibold text-sm">
                <FileSpreadsheet className="w-4 h-4 text-sky-500" />
                <span>Dữ Liệu Bảng Số (9 Chỉ Số & 4 Phân Loại)</span>
              </div>
              <span className="text-[11px] text-slate-400 font-mono">
                ID: {patientId}
              </span>
            </div>

            {/* 9 Numerical Inputs with Dynamic Normal-Range Borders */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {NUMERICAL_FIELDS.map((field) => {
                const outOfRange = isOutOfNormalRange(field);
                const val = tabular[field.key] as number;
                return (
                  <div key={field.key} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <label className="font-medium text-slate-700 dark:text-slate-300">
                        {field.label}
                      </label>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono transition-colors ${
                          outOfRange
                            ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 font-semibold"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                        }`}
                      >
                        {field.normalMin} - {field.normalMax} {field.unit}
                      </span>
                    </div>

                    <div className="relative">
                      <input
                        type="number"
                        min={field.min}
                        max={field.max}
                        step={field.step || "any"}
                        value={val}
                        onChange={(e) =>
                          handleNumericalChange(field.key, e.target.value)
                        }
                        className={`w-full px-3 py-2 rounded-xl text-sm font-mono border transition-all outline-none bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white ${
                          outOfRange
                            ? "border-amber-500 dark:border-rose-500 ring-2 ring-amber-500/20 dark:ring-rose-500/20"
                            : "border-slate-200 dark:border-slate-700 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20"
                        }`}
                        required
                      />
                      <span className="absolute right-3 top-2.5 text-xs text-slate-400 pointer-events-none">
                        {field.unit}
                      </span>
                    </div>

                    {outOfRange && (
                      <p className="text-[11px] text-amber-600 dark:text-rose-400 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                        Ngoài dải bình thường
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            {/* 4 Categorical Dropdowns */}
            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-4">
              <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Yếu Tố Dịch Tễ & Tiền Căn
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                {/* Gender */}
                <div className="space-y-1">
                  <label className="font-medium text-slate-700 dark:text-slate-300">
                    Giới tính (Gender)
                  </label>
                  <select
                    value={tabular.gender}
                    onChange={(e) =>
                      setTabular((p) => ({
                        ...p,
                        gender: e.target.value as "M" | "F" | "OTHER",
                      }))
                    }
                    className="w-full px-3 py-2 rounded-xl text-xs border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white outline-none focus:border-sky-500"
                  >
                    <option value="M">Nam (Male)</option>
                    <option value="F">Nữ (Female)</option>
                    <option value="OTHER">Khác (Other)</option>
                  </select>
                </div>

                {/* Smoking Status */}
                <div className="space-y-1">
                  <label className="font-medium text-slate-700 dark:text-slate-300">
                    Hút thuốc lá (Smoking)
                  </label>
                  <select
                    value={tabular.smoking_status}
                    onChange={(e) =>
                      setTabular((p) => ({
                        ...p,
                        smoking_status: e.target.value as
                          | "NEVER"
                          | "FORMER"
                          | "CURRENT",
                      }))
                    }
                    className="w-full px-3 py-2 rounded-xl text-xs border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white outline-none focus:border-sky-500"
                  >
                    <option value="NEVER">Chưa từng hút (Never)</option>
                    <option value="FORMER">Đã từng hút / Cai (Former)</option>
                    <option value="CURRENT">Đang hút thuốc (Current)</option>
                  </select>
                </div>

                {/* History of Hypertension */}
                <div className="space-y-1">
                  <label className="font-medium text-slate-700 dark:text-slate-300">
                    Tiền sử tăng huyết áp (HTN)
                  </label>
                  <select
                    value={tabular.history_hypertension}
                    onChange={(e) =>
                      setTabular((p) => ({
                        ...p,
                        history_hypertension: parseInt(e.target.value) as 0 | 1,
                      }))
                    }
                    className="w-full px-3 py-2 rounded-xl text-xs border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white outline-none focus:border-sky-500"
                  >
                    <option value={0}>Không (No)</option>
                    <option value={1}>Có (Yes)</option>
                  </select>
                </div>

                {/* History of Diabetes */}
                <div className="space-y-1">
                  <label className="font-medium text-slate-700 dark:text-slate-300">
                    Tiền sử đái tháo đường (DM)
                  </label>
                  <select
                    value={tabular.history_diabetes}
                    onChange={(e) =>
                      setTabular((p) => ({
                        ...p,
                        history_diabetes: parseInt(e.target.value) as 0 | 1,
                      }))
                    }
                    className="w-full px-3 py-2 rounded-xl text-xs border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white outline-none focus:border-sky-500"
                  >
                    <option value={0}>Không (No)</option>
                    <option value={1}>Có (Yes)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* CỘT PHẢI: Ghi Chú Bệnh Án Tự Do (Clinical Notes) */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-4">
            <div className="space-y-4 flex-1 flex flex-col">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-slate-900 dark:text-white font-semibold text-sm">
                  <FileText className="w-4 h-4 text-emerald-500" />
                  <span>Ghi Chú Bệnh Án Tự Do (Clinical Notes)</span>
                </div>
                <span className="text-[11px] text-slate-400">
                  {clinicalNotes.length} ký tự
                </span>
              </div>

              <div className="p-3 rounded-xl bg-sky-500/5 border border-sky-500/10 text-xs text-sky-700 dark:text-sky-300 flex items-start gap-2">
                <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>
                  Bác sĩ có thể dán hoặc gõ nội dung bệnh sử, tiền căn, kết quả
                  khám thực thể. Pipeline De-ID sẽ tự động ẩn danh hóa trước khi
                  đưa vào Text Encoder.
                </span>
              </div>

              <div className="flex-1 flex flex-col min-h-[320px]">
                <textarea
                  value={clinicalNotes}
                  onChange={(e) => setClinicalNotes(e.target.value)}
                  placeholder="Gõ hoặc dán bệnh sử, lý do vào viện, diễn biến lâm sàng tại đây..."
                  className="w-full flex-1 p-4 rounded-xl text-sm leading-relaxed border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/60 text-slate-900 dark:text-white outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 resize-none font-sans"
                />
              </div>
            </div>

            {/* Action Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-sky-600 via-indigo-600 to-emerald-600 hover:from-sky-500 hover:to-emerald-500 text-white font-semibold text-sm shadow-lg shadow-sky-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>Đang gửi dự đoán tới 3 Baselines...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>Chạy Dự Đoán 3 Baselines</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Hiển Thị Kết Quả 3 Baselines */}
      {predictionResponse && (
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-5 animate-in fade-in duration-300">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white text-base">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              <span>Kết Quả Đối Chứng 3 Baselines (Mock Inference Output)</span>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-mono">
              Bệnh nhân: {predictionResponse.patient_id}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Baseline 1: Classical Tabular */}
            {predictionResponse.baseline_results.classical_tabular && (
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
                  <Database className="w-4 h-4 text-sky-500" />
                  <span>Baseline 1: Classical Tabular</span>
                </div>
                <div className="text-xs text-slate-400">
                  Mô hình: XGBoost (Dữ liệu bảng số)
                </div>

                <div className="space-y-1">
                  <div className="text-xs text-slate-500">Chẩn đoán dự báo:</div>
                  <div
                    className={`text-xs px-2 py-1 rounded-lg border font-semibold inline-block ${
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.classical_tabular
                          .predicted_class
                      ).color
                    }`}
                  >
                    {
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.classical_tabular
                          .predicted_class
                      ).name
                    }
                  </div>
                </div>

                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-500">Độ tin cậy:</span>
                    <span className="font-mono text-slate-900 dark:text-white">
                      {(
                        predictionResponse.baseline_results.classical_tabular
                          .confidence * 100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-sky-500 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.round(
                          predictionResponse.baseline_results.classical_tabular
                            .confidence * 100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Baseline 2: Tabular Deep */}
            {predictionResponse.baseline_results.tabular_deep && (
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
                  <Cpu className="w-4 h-4 text-indigo-500" />
                  <span>Baseline 2: Tabular Deep Learning</span>
                </div>
                <div className="text-xs text-slate-400">
                  Mô hình: FT-Transformer (Dữ liệu bảng số)
                </div>

                <div className="space-y-1">
                  <div className="text-xs text-slate-500">Chẩn đoán dự báo:</div>
                  <div
                    className={`text-xs px-2 py-1 rounded-lg border font-semibold inline-block ${
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.tabular_deep
                          .predicted_class
                      ).color
                    }`}
                  >
                    {
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.tabular_deep
                          .predicted_class
                      ).name
                    }
                  </div>
                </div>

                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-500">Độ tin cậy:</span>
                    <span className="font-mono text-slate-900 dark:text-white">
                      {(
                        predictionResponse.baseline_results.tabular_deep
                          .confidence * 100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.round(
                          predictionResponse.baseline_results.tabular_deep
                            .confidence * 100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Baseline 3: Clinical NLP Text Only */}
            {predictionResponse.baseline_results.text_only && (
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40 space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
                  <FileText className="w-4 h-4 text-emerald-500" />
                  <span>Baseline 3: Clinical NLP</span>
                </div>
                <div className="text-xs text-slate-400">
                  Mô hình: Bio_ClinicalBERT (Ghi chú tự do)
                </div>

                <div className="space-y-1">
                  <div className="text-xs text-slate-500">Chẩn đoán dự báo:</div>
                  <div
                    className={`text-xs px-2 py-1 rounded-lg border font-semibold inline-block ${
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.text_only
                          .predicted_class
                      ).color
                    }`}
                  >
                    {
                      getDiseaseLabelBadge(
                        predictionResponse.baseline_results.text_only
                          .predicted_class
                      ).name
                    }
                  </div>
                </div>

                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-500">Độ tin cậy:</span>
                    <span className="font-mono text-slate-900 dark:text-white">
                      {(
                        predictionResponse.baseline_results.text_only
                          .confidence * 100
                      ).toFixed(1)}
                      %
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.round(
                          predictionResponse.baseline_results.text_only
                            .confidence * 100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

