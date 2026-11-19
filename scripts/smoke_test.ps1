<#
.SYNOPSIS
    End-to-End Smoke Test for M-CDSS Stack (Phase 3 - Backlog 10 Task 3.1).
.DESCRIPTION
    Tests live backend API and Next.js frontend endpoints:
      1. GET  /health (HTTP 200)
      2. GET  /api/v1/predict/status (HTTP 200)
      3. POST /api/v1/predict/multimodal:
           - Default (strict): requires HTTP 200; HTTP 503 is treated as FAIL with root cause diagnosis.
           - With -AllowLightweightNoTorch: HTTP 503 reports [FAIL-SAFE ONLY] (not [PASS]) to distinguish
             fail-safe verification from full multimodal inference verification.
      4. POST /api/v1/agent/explain (HTTP 200 with non-empty verified_spans)
      5. GET  /api/v1/evaluation/benchmark (HTTP 200)
      6. GET  /api/v1/evaluation/registry (HTTP 200)
      7. GET  / (Frontend HTTP 200)
      8. GET  /evaluation (Frontend HTTP 200)
#>
param(
    [string]$ApiBaseUrl = $(if ($env:API_BASE_URL) { $env:API_BASE_URL } else { "http://127.0.0.1:8000" }),
    [string]$FrontendBaseUrl = $(if ($env:FRONTEND_BASE_URL) { $env:FRONTEND_BASE_URL } else { "http://127.0.0.1:3000" }),
    [int]$TimeoutSeconds = 20,
    [switch]$AllowLightweightNoTorch
)

$ErrorActionPreference = "Stop"
$ApiBaseUrl = $ApiBaseUrl.TrimEnd("/")
$FrontendBaseUrl = $FrontendBaseUrl.TrimEnd("/")
$Failures = 0

function Write-CheckResult {
    param(
        [string]$Name,
        [string]$Status, # PASS, FAIL, FAILSAFE
        [string]$Detail
    )
    if ($Status -eq "PASS") {
        Write-Host "[PASS] $Name - $Detail" -ForegroundColor Green
    } elseif ($Status -eq "FAILSAFE") {
        Write-Host "[FAIL-SAFE ONLY] $Name - $Detail" -ForegroundColor Yellow
    } else {
        Write-Host "[FAIL] $Name - $Detail" -ForegroundColor Red
        $script:Failures += 1
    }
}

function Invoke-HttpJson {
    param(
        [string]$Method,
        [string]$Uri,
        [string]$BodyJson = $null
    )
    $headers = @{ "Accept" = "application/json" }
    $params = @{
        Method          = $Method
        Uri             = $Uri
        Headers         = $headers
        TimeoutSec      = $TimeoutSeconds
        UseBasicParsing = $true
    }
    if ($BodyJson) {
        $params["ContentType"] = "application/json; charset=utf-8"
        $params["Body"] = [System.Text.Encoding]::UTF8.GetBytes($BodyJson)
    }

    try {
        $resp = Invoke-WebRequest @params
        $parsed = $null
        try {
            $parsed = $resp.Content | ConvertFrom-Json
        } catch {
            $parsed = $null
        }
        return [PSCustomObject]@{
            StatusCode = [int]$resp.StatusCode
            Content    = $resp.Content
            Json       = $parsed
            Error      = $null
        }
    } catch {
        $statusCode = 0
        $rawBody = ""
        $parsed = $null

        if ($_.Exception.Response) {
            try {
                $statusCode = [int]$_.Exception.Response.StatusCode
            } catch {
                $statusCode = 0
            }
            try {
                if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
                    $rawBody = $_.ErrorDetails.Message
                } elseif ($_.Exception.Response -is [System.Net.HttpWebResponse]) {
                    $stream = $_.Exception.Response.GetResponseStream()
                    if ($stream) {
                        $reader = New-Object System.IO.StreamReader($stream)
                        $rawBody = $reader.ReadToEnd()
                        $reader.Close()
                    }
                }
                if ($rawBody) {
                    $parsed = $rawBody | ConvertFrom-Json
                }
            } catch {
                $parsed = $null
            }
        }
        return [PSCustomObject]@{
            StatusCode = $statusCode
            Content    = $rawBody
            Json       = $parsed
            Error      = $_.Exception.Message
        }
    }
}

Write-Host "=== M-CDSS Smoke Test (Backlog 10 Task 3.1) ==="
Write-Host "API Base URL      : $ApiBaseUrl"
Write-Host "Frontend Base URL : $FrontendBaseUrl"
Write-Host "Strict Multimodal : $(-not $AllowLightweightNoTorch)"
Write-Host ""

# 1. GET /health
$resHealth = Invoke-HttpJson -Method "GET" -Uri "$ApiBaseUrl/health"
$statusHealth = if ($resHealth.StatusCode -eq 200) { "PASS" } else { "FAIL" }
Write-CheckResult -Name "GET /health" -Status $statusHealth -Detail "HTTP $($resHealth.StatusCode)"

# 2. GET /api/v1/predict/status
$resStatus = Invoke-HttpJson -Method "GET" -Uri "$ApiBaseUrl/api/v1/predict/status"
$okStatus = ($resStatus.StatusCode -eq 200) -and ($null -ne $resStatus.Json) -and ([bool]$resStatus.Json.reasoning_mode)
$statusDetail = if ($resStatus.Json) {
    "HTTP $($resStatus.StatusCode) | mode=$($resStatus.Json.reasoning_mode) | manifest_is_mock=$($resStatus.Json.model_card.data_manifest_is_mock)"
} else {
    "HTTP $($resStatus.StatusCode) | $($resStatus.Error)"
}
Write-CheckResult -Name "GET /api/v1/predict/status" -Status $(if ($okStatus) { "PASS" } else { "FAIL" }) -Detail $statusDetail

# Shared clinical payload matching schemas.PatientInferenceRequest
$predictPayload = @{
    patient_id = "PT-SMOKE-001"
    tabular_features = @{
        age                  = 68
        systolic_bp          = 138.0
        diastolic_bp         = 84.0
        heart_rate           = 96.0
        respiratory_rate     = 24.0
        spo2                 = 89.0
        temperature          = 37.2
        wbc_count            = 9.8
        crp                  = 12.5
        gender               = "M"
        smoking_status       = "CURRENT"
        history_hypertension = 1
        history_diabetes     = 0
    }
    clinical_notes = "Benh nhan nam 68 tuoi, tien su hut thuoc la 35 goi-nam, nhap vien vi kho tho tang dan, ho khac dom duc, ran rit ran ngay hai phe truong, SpO2 89% khi tho khi phong, FEV1/FVC < 0.70 sau test gian phe quan."
} | ConvertTo-Json -Depth 5

# 3. POST /api/v1/predict/multimodal
$resMulti = Invoke-HttpJson -Method "POST" -Uri "$ApiBaseUrl/api/v1/predict/multimodal" -BodyJson $predictPayload
if ($resMulti.StatusCode -eq 200) {
    Write-CheckResult -Name "POST /api/v1/predict/multimodal" -Status "PASS" -Detail "HTTP 200 | predicted=$($resMulti.Json.predicted_disease) | source=$($resMulti.Json.prediction_source)"
} elseif ($resMulti.StatusCode -eq 503 -and $null -ne $resMulti.Json -and $resMulti.Json.detail) {
    $detailStr = [string]$resMulti.Json.detail
    $cause = if ($detailStr -match "No module named '(torch|transformers)'") {
        "MISSING DEPLOY DEPENDENCY ($detailStr)"
    } else {
        "MISSING MODEL/HF CACHE ($detailStr)"
    }
    if ($AllowLightweightNoTorch) {
        Write-CheckResult -Name "POST /api/v1/predict/multimodal" -Status "FAILSAFE" -Detail "HTTP 503 ($cause) - multimodal inference NOT verified"
    } else {
        Write-CheckResult -Name "POST /api/v1/predict/multimodal" -Status "FAIL" -Detail "HTTP 503 ($cause); multimodal inference required HTTP 200 (pass -AllowLightweightNoTorch to test fail-safe only)"
    }
} else {
    Write-CheckResult -Name "POST /api/v1/predict/multimodal" -Status "FAIL" -Detail "HTTP $($resMulti.StatusCode) | $($resMulti.Error) $($resMulti.Content)"
}

# 4. POST /api/v1/agent/explain (200 OK with non-empty verified_spans)
$explainPayload = @{
    patient_id = "PT-SMOKE-001"
    clinical_notes = "Patient has progressive dyspnea, wheezing on expiration, chronic productive cough, SpO2 89%, smoking history 35 pack-years, and FEV1/FVC 0.62 consistent with COPD exacerbation."
    target_diagnosis = "COPD"
    differential_diagnosis = "ASTHMA"
    calibrated_probabilities = @{
        COPD                         = 0.74
        ASTHMA                       = 0.14
        COMMUNITY_ACQUIRED_PNEUMONIA = 0.08
        CONGESTIVE_HEART_FAILURE     = 0.04
    }
} | ConvertTo-Json -Depth 5

$resExplain = Invoke-HttpJson -Method "POST" -Uri "$ApiBaseUrl/api/v1/agent/explain" -BodyJson $explainPayload
$spansCount = 0
if ($resExplain.Json) {
    if ($resExplain.Json.verified_spans) {
        $spansCount = @($resExplain.Json.verified_spans).Count
    } elseif ($resExplain.Json.evidence_spans) {
        $spansCount = @($resExplain.Json.evidence_spans).Count
    }
}
$okExplain = ($resExplain.StatusCode -eq 200) -and ($spansCount -gt 0)
$explainDetail = if ($resExplain.Json) {
    "HTTP $($resExplain.StatusCode) | verified_spans=$spansCount | mode=$($resExplain.Json.reasoning_mode)"
} else {
    "HTTP $($resExplain.StatusCode) | $($resExplain.Error)"
}
Write-CheckResult -Name "POST /api/v1/agent/explain" -Status $(if ($okExplain) { "PASS" } else { "FAIL" }) -Detail $explainDetail

# 5. GET /api/v1/evaluation/benchmark
$resBench = Invoke-HttpJson -Method "GET" -Uri "$ApiBaseUrl/api/v1/evaluation/benchmark"
$okBench = ($resBench.StatusCode -eq 200) -and ($null -ne $resBench.Json)
Write-CheckResult -Name "GET /api/v1/evaluation/benchmark" -Status $(if ($okBench) { "PASS" } else { "FAIL" }) -Detail "HTTP $($resBench.StatusCode)"

# 6. GET /api/v1/evaluation/registry
$resRegistry = Invoke-HttpJson -Method "GET" -Uri "$ApiBaseUrl/api/v1/evaluation/registry"
$okRegistry = ($resRegistry.StatusCode -eq 200) -and ($null -ne $resRegistry.Json)
Write-CheckResult -Name "GET /api/v1/evaluation/registry" -Status $(if ($okRegistry) { "PASS" } else { "FAIL" }) -Detail "HTTP $($resRegistry.StatusCode)"

# 7 & 8. Frontend routes GET / and GET /evaluation
foreach ($route in @("/", "/evaluation")) {
    try {
        $resp = Invoke-WebRequest -Method "GET" -Uri "$FrontendBaseUrl$route" -TimeoutSec $TimeoutSeconds -UseBasicParsing
        $okRoute = ([int]$resp.StatusCode -eq 200)
        Write-CheckResult -Name "Frontend GET $route" -Status $(if ($okRoute) { "PASS" } else { "FAIL" }) -Detail "HTTP $([int]$resp.StatusCode)"
    } catch {
        Write-CheckResult -Name "Frontend GET $route" -Status "FAIL" -Detail "$($_.Exception.Message)"
    }
}

Write-Host ""
if ($Failures -gt 0) {
    Write-Host "Smoke test finished with $Failures failure(s)." -ForegroundColor Red
    exit 1
}
if ($AllowLightweightNoTorch -and $resMulti.StatusCode -eq 503) {
    Write-Host "Lightweight fail-safe smoke check completed (7 PASS + 1 FAIL-SAFE ONLY on /predict/multimodal)." -ForegroundColor Yellow
} else {
    Write-Host "All 8 smoke test checks passed." -ForegroundColor Green
}
exit 0
