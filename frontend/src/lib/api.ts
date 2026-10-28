/**
 * API Client for Multimodal EHR CDSS Backend
 * Connects to FastAPI backend at http://localhost:8000
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface TabularFeatures {
  age: number;
  systolic_bp: number;
  diastolic_bp: number;
  heart_rate: number;
  respiratory_rate: number;
  spo2: number;
  temperature: number;
  wbc_count: number;
  crp: number;
  gender: "M" | "F" | "OTHER";
  smoking_status: "NEVER" | "FORMER" | "CURRENT";
  history_hypertension: 0 | 1;
  history_diabetes: 0 | 1;
}

export interface ClinicalNoteInput {
  patient_id: string;
  encounter_timestamp: string;
  raw_text: string;
}

export interface PredictionProbabilities {
  ASTHMA: number;
  COPD: number;
  CONGESTIVE_HEART_FAILURE: number;
  COMMUNITY_ACQUIRED_PNEUMONIA: number;
}

export interface BaselinePredictionResult {
  baseline_name: string;
  disease_name: keyof PredictionProbabilities;
  probability: number;
  probabilities?: PredictionProbabilities | null;
  model_version?: string | null;
}

/**
 * Perform a GET request to verify backend health
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch baseline inference engine status
 */
export async function getInferenceStatus(): Promise<{ status: string; supported_baselines: string[] }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict/status`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Inference status check failed with status: ${response.status}`);
  }

  return response.json();
}

export interface BaselineModelResult {
  predicted_class: string;
  confidence: number;
}

export interface PatientInferenceRequest {
  patient_id?: string;
  tabular_features: TabularFeatures;
  clinical_notes?: string;
}

export interface BaselineInferenceResponse {
  patient_id: string;
  baseline_results: {
    classical_tabular: BaselineModelResult;
    tabular_deep: BaselineModelResult;
    text_only: BaselineModelResult;
    [key: string]: BaselineModelResult;
  };
}

/**
 * Call backend to predict across 3 baseline models
 */
export async function predictBaselines(
  payload: PatientInferenceRequest
): Promise<BaselineInferenceResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict/baseline`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Inference failed (${response.status}): ${errorText}`);
  }

  return response.json();
}


export interface BaselineBenchmarkMetrics {
  model_type: string;
  data_modality: string;
  macro_auroc: number;
  macro_auprc: number;
  macro_f1: number;
  accuracy: number;
  brier_score: number;
  ece: number;
}

export interface BenchmarkResultsResponse {
  benchmark_metadata: {
    evaluation_date: string;
    test_samples: number;
    num_classes: number;
    classes: string[];
  };
  results: {
    baseline_1_classical_tabular: BaselineBenchmarkMetrics;
    baseline_2_tabular_deep: BaselineBenchmarkMetrics;
    baseline_3_text_only: BaselineBenchmarkMetrics;
    [key: string]: BaselineBenchmarkMetrics;
  };
  summary_findings: {
    highest_auroc_model: string;
    highest_macro_auroc?: number;
    calibration_finding?: string;
    clinical_blindspot: string;
    external_validity_warning?: string;
  };
}

export const FALLBACK_BENCHMARK_RESULTS: BenchmarkResultsResponse = {
  benchmark_metadata: {
    evaluation_date: '2026-10-28T03:39:58Z',
    test_samples: 302,
    num_classes: 4,
    classes: [
      'ASTHMA',
      'COPD',
      'HEART_FAILURE',
      'PNEUMONIA'
    ]
  },
  results: {
    baseline_1_classical_tabular: {
      model_type: 'CatBoost',
      data_modality: 'Structured Tabular Only',
      macro_auroc: 0.922315,
      macro_auprc: 0.787219,
      macro_f1: 0.608266,
      accuracy: 0.685430,
      brier_score: 0.384386,
      ece: 0.066278
    },
    baseline_2_tabular_deep: {
      model_type: 'FT-Transformer (Tabular DL)',
      data_modality: 'Structured Tabular Only',
      macro_auroc: 0.897621,
      macro_auprc: 0.702308,
      macro_f1: 0.578943,
      accuracy: 0.658940,
      brier_score: 0.472502,
      ece: 0.115186
    },
    baseline_3_text_only: {
      model_type: 'Bio_ClinicalBERT',
      data_modality: 'Unstructured Clinical Notes Only',
      macro_auroc: 0.973453,
      macro_auprc: 0.931369,
      macro_f1: 0.842071,
      accuracy: 0.854305,
      brier_score: 0.232878,
      ece: 0.037293
    }
  },
  summary_findings: {
    highest_auroc_model: 'Bio_ClinicalBERT',
    highest_macro_auroc: 0.973453,
    calibration_finding: 'Bio_ClinicalBERT đạt ECE 0.0373 (< 0.05). CatBoost đạt ECE 0.0663, FT-Transformer đạt ECE 0.1152.',
    clinical_blindspot: 'Mô hình bảng và văn bản quan sát các nguồn bằng chứng bổ trợ cho nhau; giai đoạn 2 triển khai Multimodal Late Fusion.',
    external_validity_warning: 'Cần thẩm định ngoại kiểm trên dữ liệu bệnh viện độc lập.'
  }
};

export async function getBaselineBenchmarks(): Promise<BenchmarkResultsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/benchmarks/baselines`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      cache: 'no-store',
    });
    if (!response.ok) {
      return FALLBACK_BENCHMARK_RESULTS;
    }
    const data = await response.json();
    return data;
  } catch {
    return FALLBACK_BENCHMARK_RESULTS;
  }
}
