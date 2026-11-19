#!/usr/bin/env bash
# End-to-End Smoke Test for M-CDSS Stack (Phase 3 - Backlog 10 Task 3.1).
# Tests:
#   1. GET  /health (HTTP 200)
#   2. GET  /api/v1/predict/status (HTTP 200)
#   3. POST /api/v1/predict/multimodal (HTTP 200 or explicit HTTP 503 structured safeguard)
#   4. POST /api/v1/agent/explain (HTTP 200 with non-empty verified_spans)
#   5. GET  /api/v1/evaluation/benchmark (HTTP 200)
#   6. GET  /api/v1/evaluation/registry (HTTP 200)
#   7. GET  / (Frontend HTTP 200)
#   8. GET  /evaluation (Frontend HTTP 200)

set -u

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
FRONTEND_BASE_URL="${FRONTEND_BASE_URL:-http://127.0.0.1:3000}"
API_BASE_URL="${API_BASE_URL%/}"
FRONTEND_BASE_URL="${FRONTEND_BASE_URL%/}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"

FAILURES=0

pass_check() {
    echo "[PASS] $1 - $2"
}

fail_check() {
    echo "[FAIL] $1 - $2"
    FAILURES=$((FAILURES + 1))
}

json_check() {
    local expr="$1"
    python3 -c "$expr" 2>/dev/null
}

echo "=== M-CDSS Smoke Test (Backlog 10 Task 3.1) ==="
echo "API Base URL      : ${API_BASE_URL}"
echo "Frontend Base URL : ${FRONTEND_BASE_URL}"
echo ""

# 1. GET /health
code=$(curl -sS -m "${TIMEOUT_SECONDS}" -o /tmp/mcdss_health.json -w "%{http_code}" "${API_BASE_URL}/health" || echo "000")
if [ "$code" = "200" ]; then
    pass_check "GET /health" "HTTP ${code}"
else
    fail_check "GET /health" "HTTP ${code}"
fi

# 2. GET /api/v1/predict/status
code=$(curl -sS -m "${TIMEOUT_SECONDS}" -o /tmp/mcdss_status.json -w "%{http_code}" "${API_BASE_URL}/api/v1/predict/status" || echo "000")
if [ "$code" = "200" ] && json_check "import json; d=json.load(open('/tmp/mcdss_status.json')); assert bool(d.get('reasoning_mode'))"; then
    pass_check "GET /api/v1/predict/status" "HTTP ${code}"
else
    fail_check "GET /api/v1/predict/status" "HTTP ${code}"
fi

# 3. POST /api/v1/predict/multimodal (200 or explicit 503 structured error)
read -r -d '' PREDICT_PAYLOAD <<'EOF' || true
{
  "patient_id": "PT-SMOKE-001",
  "tabular_features": {
    "age": 68,
    "systolic_bp": 138.0,
    "diastolic_bp": 84.0,
    "heart_rate": 96.0,
    "respiratory_rate": 24.0,
    "spo2": 89.0,
    "temperature": 37.2,
    "wbc_count": 9.8,
    "crp": 12.5,
    "gender": "M",
    "smoking_status": "CURRENT",
    "history_hypertension": 1,
    "history_diabetes": 0
  },
  "clinical_notes": "Benh nhan nam 68 tuoi, tien su hut thuoc la 35 goi-nam, nhap vien vi kho tho tang dan, ho khac dom duc, SpO2 89%, FEV1/FVC < 0.70 sau test gian phe quan."
}
EOF

code=$(curl -sS -m "${TIMEOUT_SECONDS}" -X POST -H "Content-Type: application/json" -d "${PREDICT_PAYLOAD}" -o /tmp/mcdss_multi.json -w "%{http_code}" "${API_BASE_URL}/api/v1/predict/multimodal" || echo "000")
if [ "$code" = "200" ]; then
    pass_check "POST /api/v1/predict/multimodal" "HTTP 200"
elif [ "$code" = "503" ] && json_check "import json; d=json.load(open('/tmp/mcdss_multi.json')); assert bool(str(d.get('detail', '')).strip())"; then
    pass_check "POST /api/v1/predict/multimodal" "HTTP 503 explicit structured safeguard (missing offline HF cache)"
else
    fail_check "POST /api/v1/predict/multimodal" "HTTP ${code}"
fi

# 4. POST /api/v1/agent/explain (200 with non-empty verified_spans)
read -r -d '' EXPLAIN_PAYLOAD <<'EOF' || true
{
  "patient_id": "PT-SMOKE-001",
  "clinical_notes": "Patient has progressive dyspnea, wheezing on expiration, chronic productive cough, SpO2 89%, smoking history 35 pack-years, and FEV1/FVC 0.62 consistent with COPD exacerbation.",
  "target_diagnosis": "COPD",
  "differential_diagnosis": "ASTHMA",
  "calibrated_probabilities": {
    "COPD": 0.74,
    "ASTHMA": 0.14,
    "COMMUNITY_ACQUIRED_PNEUMONIA": 0.08,
    "CONGESTIVE_HEART_FAILURE": 0.04
  }
}
EOF

code=$(curl -sS -m "${TIMEOUT_SECONDS}" -X POST -H "Content-Type: application/json" -d "${EXPLAIN_PAYLOAD}" -o /tmp/mcdss_explain.json -w "%{http_code}" "${API_BASE_URL}/api/v1/agent/explain" || echo "000")
if [ "$code" = "200" ] && json_check "import json; d=json.load(open('/tmp/mcdss_explain.json')); spans = d.get('verified_spans') or d.get('evidence_spans') or []; assert len(spans) > 0"; then
    pass_check "POST /api/v1/agent/explain" "HTTP ${code} with non-empty verified_spans"
else
    fail_check "POST /api/v1/agent/explain" "HTTP ${code}"
fi

# 5. GET /api/v1/evaluation/benchmark
code=$(curl -sS -m "${TIMEOUT_SECONDS}" -o /tmp/mcdss_bench.json -w "%{http_code}" "${API_BASE_URL}/api/v1/evaluation/benchmark" || echo "000")
if [ "$code" = "200" ] && json_check "import json; json.load(open('/tmp/mcdss_bench.json'))"; then
    pass_check "GET /api/v1/evaluation/benchmark" "HTTP ${code}"
else
    fail_check "GET /api/v1/evaluation/benchmark" "HTTP ${code}"
fi

# 6. GET /api/v1/evaluation/registry
code=$(curl -sS -m "${TIMEOUT_SECONDS}" -o /tmp/mcdss_reg.json -w "%{http_code}" "${API_BASE_URL}/api/v1/evaluation/registry" || echo "000")
if [ "$code" = "200" ] && json_check "import json; json.load(open('/tmp/mcdss_reg.json'))"; then
    pass_check "GET /api/v1/evaluation/registry" "HTTP ${code}"
else
    fail_check "GET /api/v1/evaluation/registry" "HTTP ${code}"
fi

# 7 & 8. Frontend GET / and GET /evaluation
for route in "/" "/evaluation"; do
    code=$(curl -sS -m "${TIMEOUT_SECONDS}" -o /dev/null -w "%{http_code}" "${FRONTEND_BASE_URL}${route}" || echo "000")
    if [ "$code" = "200" ]; then
        pass_check "Frontend GET ${route}" "HTTP ${code}"
    else
        fail_check "Frontend GET ${route}" "HTTP ${code}"
    fi
done

echo ""
if [ "${FAILURES}" -gt 0 ]; then
    echo "Smoke test finished with ${FAILURES} failure(s)."
    exit 1
fi
echo "All 8 smoke test checks passed."
exit 0
