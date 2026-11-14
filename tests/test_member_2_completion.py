"""
Unit & Integration Test Suite: Member 2 Task Completion Verification
Verifies 100% completion of tasks/phase-02-development/backlog-06-clinical-validation/MEMBER_2.md
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
MEMBER_2_MD = ROOT_DIR / "tasks" / "phase-02-development" / "backlog-06-clinical-validation" / "MEMBER_2.md"


class TestMember2Task1ConfusionMatrixAndErrorAnalysis:
    """Verifies Nhiệm vụ 2.1: Ma Trận Nhầm Lẫn & Phân Tích Ca Bệnh Sai Biệt."""

    def test_confusion_matrix_image_exists(self):
        cm_path = ROOT_DIR / "data" / "confusion_matrix.png"
        assert cm_path.exists(), f"Deliverable missing: {cm_path}"
        assert cm_path.stat().st_size > 50_000, f"File too small or corrupted: {cm_path.stat().st_size} bytes"

    def test_error_analysis_document_contents(self):
        doc_path = ROOT_DIR / "docs" / "06_ERROR_ANALYSIS_AND_CLINICAL_DISCREPANCIES.md"
        assert doc_path.exists(), f"Deliverable missing: {doc_path}"
        content = doc_path.read_text(encoding="utf-8")

        # 1. 4 disease classes
        for disease in ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"]:
            assert disease in content, f"Disease {disease} missing from error analysis"

        # 2. Key clinical error clusters
        assert "ACOS" in content or "chồng lấp" in content.lower(), "Missing ACOS clinical discussion"
        assert "suy tim" in content.lower(), "Missing heart failure clinical discussion"
        assert "viêm phổi" in content.lower(), "Missing pneumonia clinical discussion"

        # 3. Specific patient cases
        assert "PT-0025" in content, "Case PT-0025 missing from error analysis"
        assert "PT-0201" in content, "Case PT-0201 missing from error analysis"


class TestMember2Task2ClinicalUtilityScriptAndOutputs:
    """Verifies Nhiệm vụ 2.2: Tự Động Hóa Kịch Bản Đánh Giá Lâm Sàng."""

    def test_evaluate_script_exists(self):
        script_path = ROOT_DIR / "scripts" / "evaluate_clinical_utility.py"
        assert script_path.exists(), f"Script missing: {script_path}"

    def test_dca_analysis_module_functional(self):
        from src.evaluation.dca_analysis import calculate_net_benefit, plot_dca_curve

        y_true = np.array([0, 1, 2, 3, 2, 2, 0, 1])
        y_prob = np.array([
            [0.7, 0.1, 0.1, 0.1],
            [0.1, 0.6, 0.2, 0.1],
            [0.1, 0.1, 0.7, 0.1],
            [0.1, 0.2, 0.1, 0.6],
            [0.2, 0.1, 0.6, 0.1],
            [0.1, 0.1, 0.5, 0.3],
            [0.6, 0.2, 0.1, 0.1],
            [0.2, 0.7, 0.05, 0.05],
        ])

        df_dca = calculate_net_benefit(y_true, y_prob, target_class=2)
        assert not df_dca.empty
        assert "net_benefit_model" in df_dca.columns
        assert "net_benefit_all" in df_dca.columns
        assert "net_benefit_none" in df_dca.columns

    def test_all_evaluation_plots_exist(self):
        plots_dir = ROOT_DIR / "data" / "evaluation_plots"
        assert plots_dir.exists()

        expected_plots = [
            "confusion_matrix.png",
            "roc_curves.png",
            "pr_curves.png",
            "dca_curve.png",
            "calibration_curve.png",
        ]
        for plot_name in expected_plots:
            plot_file = plots_dir / plot_name
            assert plot_file.exists(), f"Expected plot missing: {plot_name}"
            assert plot_file.stat().st_size > 20_000, f"Plot {plot_name} is too small"

    def test_clinical_utility_metrics_json_schema(self):
        metrics_file = ROOT_DIR / "data" / "evaluation_plots" / "clinical_utility_metrics.json"
        assert metrics_file.exists()

        with open(metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "overall_metrics" in data
        assert "calibrated" in data["overall_metrics"]
        cal = data["overall_metrics"]["calibrated"]
        for key in ["macro_auroc", "macro_auprc", "macro_f1", "accuracy", "brier_score", "ece"]:
            assert key in cal, f"Metric key {key} missing from calibrated metrics"

        assert "per_class_metrics" in data
        assert len(data["per_class_metrics"]) == 4

        assert "dca_analysis" in data
        assert "dca_table" in data["dca_analysis"]
        assert len(data["dca_analysis"]["dca_table"]) > 0

    def test_cli_execution(self):
        cmd = [
            sys.executable,
            str(ROOT_DIR / "scripts" / "evaluate_clinical_utility.py"),
            "--model_path", "data/checkpoints/multimodal_best.pt",
            "--test_data", "data/processed_rebuilt_strict/test.parquet",
            "--output_plots", "data/evaluation_plots",
        ]
        result = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True)
        assert result.returncode == 0, f"CLI execution failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert "[✓] Clinical validation automated execution completed successfully." in result.stdout


class TestMember2Task3PhysicianSurveyProtocol:
    """Verifies Nhiệm vụ 2.3: Tổ Chức Khảo Sát Đánh Giá Định Tính Với Bác Sĩ."""

    def test_survey_protocol_document_exists(self):
        protocol_path = ROOT_DIR / "docs" / "07_CLINICAL_EXPERT_SURVEY_PROTOCOL.md"
        assert protocol_path.exists(), f"Survey protocol missing: {protocol_path}"
        content = protocol_path.read_text(encoding="utf-8")

        # 1. Likert scale 1-5
        assert "Likert" in content, "Missing Likert scale definition"
        assert "1 (" in content and "5 (" in content, "Missing 1-5 scale anchors"

        # 2. 3 core evaluation dimensions
        assert "chính xác" in content.lower(), "Missing accuracy dimension"
        assert "highlight" in content.lower() or "bằng chứng" in content.lower(), "Missing highlight/evidence dimension"
        assert "phác đồ" in content.lower() or "gina" in content.lower() or "gold" in content.lower(), "Missing guideline dimension"

        # 3. Case governance & synthetic disclosure
        assert "tổng hợp" in content.lower(), "Missing synthetic case disclosure"
        assert "làm mù" in content.lower() or "blind" in content.lower(), "Missing blinding protocol"

        # 4. Honest reporting of survey status
        assert "chưa thực hiện" in content.lower(), "Missing transparent status stating survey is pending"


class TestMember2TrackingStatus:
    """Verifies MEMBER_2.md task list status."""

    def test_member_2_tasks_all_done(self):
        assert MEMBER_2_MD.exists()
        content = MEMBER_2_MD.read_text(encoding="utf-8")

        assert content.count("[x] DONE") == 3, f"Expected 3 tasks with [x] DONE, found {content.count('[x] DONE')}"
        assert "[ ] TODO" not in content, "There are still uncompleted [ ] TODO tasks in MEMBER_2.md"

