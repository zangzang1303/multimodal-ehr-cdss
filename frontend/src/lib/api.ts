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
    evaluation_date: '2026-10-20T14:25:12Z',
    test_samples: 286,
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
      macro_auroc: 0.998766,
      macro_auprc: 0.996335,
      macro_f1: 0.975568,
      accuracy: 0.975524,
      brier_score: 0.044971,
      ece: 0.026451
    },
    baseline_2_tabular_deep: {
      model_type: 'FT-Transformer (Tabular DL)',
      data_modality: 'Structured Tabular Only',
      macro_auroc: 0.990263,
      macro_auprc: 0.972376,
      macro_f1: 0.943586,
      accuracy: 0.944056,
      brier_score: 0.087843,
      ece: 0.022285
    },
    baseline_3_text_only: {
      model_type: 'Bio_ClinicalBERT',
      data_modality: 'Unstructured Clinical Notes Only',
      macro_auroc: 0.996036,
      macro_auprc: 0.989071,
      macro_f1: 0.936311,
      accuracy: 0.937063,
      brier_score: 0.078930,
      ece: 0.018085
    }
  },
  summary_findings: {
    highest_auroc_model: 'CatBoost',
    highest_macro_auroc: 0.998766,
    calibration_finding: 'Cả ba ECE đều dưới 0.05 trên tập hold-out tổng hợp.',
    clinical_blindspot: 'Mô hình bảng và văn bản quan sát các nguồn bằng chứng bổ sung cho nhau.',
    external_validity_warning: 'Cần thẩm định trên dữ liệu bệnh viện độc lập.'
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


export interface TopKPrediction {
  disease: string;
  disease_name: string;
  probability: number;
  percentage: number;
  risk_level: "low" | "moderate" | "high";
}

export interface ModalityStreamResult {
  stream_name: string;
  predicted_disease: string;
  confidence: number;
}

export interface MultimodalMockResponse {
  patient_id: string;
  prediction_source: "mock" | "checkpoint";
  model_version?: string | null;
  predicted_disease: string;
  predicted_disease_name: string;
  confidence: number;
  calibrated: boolean;
  temperature: number | null;
  ece_score: number | null;
  top_k_predictions: TopKPrediction[];
  modality_streams: {
    tabular_stream?: ModalityStreamResult;
    text_stream?: ModalityStreamResult;
    multimodal_fusion?: ModalityStreamResult;
    [key: string]: ModalityStreamResult | undefined;
  };
  fusion_gate_weights?: {
    g_tabular: number;
    g_text: number;
    [key: string]: number;
  };
  timestamp: string;
}

/**
 * Call backend to predict using the Multimodal Core mock endpoint
 */
export async function predictMultimodalMock(
  payload: PatientInferenceRequest
): Promise<MultimodalMockResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict/mock`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Multimodal mock prediction failed (${response.status}): ${errorText}`);
  }

  return response.json();
}

export async function predictMultimodal(
  payload: PatientInferenceRequest
): Promise<MultimodalMockResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/predict/multimodal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Multimodal inference unavailable (${response.status}): ${detail}`);
  }
  return response.json();
}

export interface AblationModelMetrics {
  id: string;
  name: string;
  modality: string;
  macro_auroc: number;
  macro_auprc: number;
  macro_f1: number;
  accuracy: number;
  brier_score: number;
  ece: number;
  net_gain_auroc?: number;
  description: string;
}

export interface AblationStudyResponse {
  experiment_metadata: {
    evaluation_date: string;
    test_samples: number;
    num_classes: number;
    split_strategy: string;
    classes: string[];
  };
  models: {
    tabular_only: AblationModelMetrics;
    text_only: AblationModelMetrics;
    concat_fusion: AblationModelMetrics;
    cross_attention_fusion: AblationModelMetrics;
    [key: string]: AblationModelMetrics;
  };
  key_findings: {
    auroc_gain_over_tabular: number;
    ece_reduction: string;
    best_configuration: string;
    conclusion: string;
  };
}

export const FALLBACK_ABLATION_RESULTS: AblationStudyResponse = {
  experiment_metadata: {
    evaluation_date: "2026-11-05T08:28:03.150032+00:00",
    test_samples: 302,
    num_classes: 4,
    split_strategy: "Strict group split",
    classes: ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"],
  },
  models: {
    tabular_only: {
      id: "tabular_only",
      name: "FT-Transformer (Tabular-only)",
      modality: "Structured Tabular Only",
      macro_auroc: 0.8987648505679356,
      macro_auprc: 0.699662654972183,
      macro_f1: 0.5386303167338636,
      accuracy: 0.6556291390728477,
      brier_score: 0.47632452825211136,
      ece: 0.10129639901072772,
      net_gain_auroc: 0.0,
      description: "Học sâu dạng bảng đơn thuần, nhạy với sinh hiệu tức thời nhưng thiếu ngữ cảnh bệnh sử.",
    },
    text_only: {
      id: "text_only",
      name: "Bio_ClinicalBERT (Text-only)",
      modality: "Unstructured Clinical Notes Only",
      macro_auroc: 0.6605452038124725,
      macro_auprc: 0.40144397350597044,
      macro_f1: 0.1483843537414966,
      accuracy: 0.2152317880794702,
      brier_score: 0.7674891804251837,
      ece: 0.07728824621399505,
      net_gain_auroc: -0.2382196467554631,
      description: "Mô hình ngôn ngữ y sinh nắm bắt sâu sắc bệnh sử nhưng dễ bị nhiễu ngữ nghĩa ở ca phức tạp.",
    },
    concat_fusion: {
      id: "concat_fusion",
      name: "Concat Late Fusion",
      modality: "Tabular + Text (Concatenation)",
      macro_auroc: 0.9119578375795265,
      macro_auprc: 0.7416809525442074,
      macro_f1: 0.6379864068410037,
      accuracy: 0.7152317880794702,
      brier_score: 0.41475167988102635,
      ece: 0.10494911463450121,
      net_gain_auroc: 0.0131929870115909,
      description: "Ghép nối đơn giản h_tab || h_text, không có tương tác ngữ nghĩa chéo giữa chỉ số và từ khóa.",
    },
    cross_attention_fusion: {
      id: "cross_attention_fusion",
      name: "Cross-Attention Gated Fusion (Ours)",
      modality: "Multimodal Late Fusion (Q_tab -> KV_text)",
      macro_auroc: 0.9594141527959706,
      macro_auprc: 0.8536225677057602,
      macro_f1: 0.6503384600981267,
      accuracy: 0.7748344370860927,
      brier_score: 0.34959917250530276,
      ece: 0.097339602594344,
      net_gain_auroc: 0.060649302228035,
      description: "Dung hợp tương tác chú ý liên phương thức có cổng thích ứng và hiệu chuẩn Temperature Scaling.",
    },
  },
  key_findings: {
    auroc_gain_over_tabular: 0.060649302228035,
    ece_reduction: "ECE: 0.1013 → 0.0973 (strict test)",
    best_configuration: "Cross-Attention Gated Fusion",
    conclusion: "Kết quả chỉ áp dụng cho tập kiểm thử strict split hiện hành.",
  },
};

export async function getAblationBenchmarks(): Promise<AblationStudyResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/benchmarks/ablation`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      cache: "no-store",
    });
    if (!response.ok) {
      return FALLBACK_ABLATION_RESULTS;
    }
    return response.json();
  } catch {
    return FALLBACK_ABLATION_RESULTS;
  }
}



export interface EvidenceSpan {
  start_char: number;
  end_char: number;
  text: string;
  category: "supporting" | "counter" | "red_flag" | string;
  label: string;
  reason?: string;
  confidence?: number;
  is_exact?: boolean;
}

export interface GuidelineReference {
  chunk_id: string;
  source_id?: string;
  version?: string;
  section_locator?: string;
  source_verified?: boolean;
  guideline_source: string;
  disease_entity: string;
  section_title: string;
  clinical_category: string;
  evidence_level: string;
  text_content: string;
  relevance_score?: number;
}

export interface AgentExplainRequest {
  patient_id?: string;
  clinical_notes: string;
  target_diagnosis?: string;
  differential_diagnosis?: string;
  calibrated_probabilities?: Record<string, number>;
}

export interface AgentExplainResponse {
  patient_id: string;
  display_note: string;
  primary_diagnosis: string;
  primary_diagnosis_name: string;
  differential_diagnosis?: string;
  differential_diagnosis_name?: string;
  differential_reasoning: string;
  grounded_spans: EvidenceSpan[];
  guideline_references: GuidelineReference[];
  red_flags: string[];
  recommended_investigations: string[];
  hallucination_filtered_count: number;
  execution_time_ms: number;
}

/**
 * Call backend to trigger Agentic RAG clinical differential explanation and evidence grounding
 */
export async function explainClinicalCase(
  payload: AgentExplainRequest
): Promise<AgentExplainResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/agent/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Agent explain failed (${response.status}): ${errorText}`);
  }

  return response.json();
}


export interface DCAPoint {
  threshold: number;
  net_benefit_mcdss: number;
  net_benefit_tabular: number;
  net_benefit_text: number;
  net_benefit_treat_all: number;
  net_benefit_treat_none: number;
  net_tp_gained_per_100?: number;
}

export interface EvaluationBenchmarkResponse {
  evaluation_metadata: {
    evaluation_cohort: string;
    test_samples: number;
    classes: string[];
    prevalence_per_class: number;
    validation_standard: string;
  };
  model_benchmarks: Record<
    string,
    {
      name: string;
      modality: string;
      macro_auroc: number;
      macro_auprc: number;
      macro_f1: number;
      accuracy: number;
      brier_score: number;
      ece: number;
      net_gain_auroc_over_tabular?: number;
    }
  >;
  decision_curve_analysis: {
    threshold_points: DCAPoint[];
    optimal_clinical_threshold_range: [number, number];
    dca_conclusion: string;
  };
  probast_compliance_summary: {
    participants_risk: string;
    predictors_risk: string;
    outcome_risk: string;
    analysis_risk: string;
    overall_bias_risk: string;
  };
}

export async function getClinicalEvaluationBenchmark(): Promise<EvaluationBenchmarkResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/evaluation/benchmark`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch evaluation benchmark: ${response.status}`);
  }

  return response.json();
}
