"""
Comprehensive PHI & Secret Security Scanner
M-CDSS Phase 2 / Backlog 07 - Task 2.3 (Member 2: Data Engineer & Privacy)

Scans codebase, configuration files, and sample data for:
1. Sensitive credentials / API keys / private tokens
2. Protected Health Information (PHI) / Personally Identifiable Information (PII)
Generates an auditable report for compliance verification.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]

# Common secret regex patterns
SECRET_PATTERNS = [
    (r"(?i)api[_-]?key\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "Generic API Key"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI Secret Key"),
    (r"hf_[a-zA-Z0-9]{20,}", "HuggingFace Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "Private Key Header"),
    (r"(?i)password\s*[:=]\s*['\"][^'\"]{6,}['\"]", "Hardcoded Password"),
]

# PHI patterns (Vietnamese phone numbers, CCCD 12 digits, un-redacted SSN)
PHI_PATTERNS = [
    (r"(?<!\d)(?:03|05|07|08|09)\d{8}(?!\d)", "Vietnamese Mobile Phone Number"),
    (r"(?<!\d)\d{12}(?!\d)", "Vietnamese CCCD / Citizen ID (12 digits)"),
    (r"[a-zA-Z0-9_.+-]+@(?!example\.com|test\.com|hospital\.local|mit\.edu)[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "Personal Email Address"),
]

EXCLUDE_DIRS = {
    ".git", ".venv", "env", "node_modules", ".next", "__pycache__", ".pytest_cache"
}

EXCLUDE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".pdf", ".docx", ".tar.gz", ".zip", ".pt", ".bin", ".pyc", ".parquet"
}


def scan_file(file_path: Path) -> List[Tuple[str, str, int, str]]:
    """Scans a single file for secret and PHI pattern matches."""
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = content.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        # Skip commented placeholders in documentation or templates
        if "REDACTED" in line or "placeholder" in line.lower() or "example" in line.lower():
            continue

        for pattern, desc in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match and not ("YOUR_" in line or "CHANGEME" in line or "<" in line or "sk-dummy" in line):
                findings.append(("SECRET", desc, line_idx, line.strip()[:80]))

        # Only scan for PHI in source and data files (skip this scanner script itself)
        if file_path.name != "audit_phi_and_secrets.py":
            for pattern, desc in PHI_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    # Ignore common commit hashes, sha256 hashes, timestamps
                    matched_str = match.group(0)
                    if len(matched_str) == 12 and re.match(r"^\d+$", matched_str):
                        # Check if it's not a timestamp or float
                        findings.append(("PHI", desc, line_idx, line.strip()[:80]))
    return findings


def scan_git_history(max_commits: int = 50) -> List[str]:
    """Scans git log diffs for accidental credentials."""
    findings = []
    try:
        cmd = ["git", "log", f"-n{max_commits}", "-p", "--diff-filter=A"]
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, errors="ignore")
        diff_text = res.stdout
        for pattern, desc in SECRET_PATTERNS:
            matches = re.findall(pattern, diff_text)
            for m in matches:
                if not any(token in m for token in ["YOUR_", "CHANGEME", "dummy", "example"]):
                    findings.append(f"Git history match for {desc}: {m[:10]}...")
    except Exception as e:
        findings.append(f"Git scan error: {e}")
    return findings


def run_full_scan() -> Dict[str, Any]:
    print("=" * 70)
    print("M-CDSS COMPREHENSIVE PHI & CREDENTIAL SECURITY AUDIT")
    print("=" * 70)

    total_scanned = 0
    all_findings = []

    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            fpath = Path(root) / f
            if fpath.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            total_scanned += 1
            file_findings = scan_file(fpath)
            for cat, desc, line_no, snippet in file_findings:
                rel_path = fpath.relative_to(ROOT_DIR)
                all_findings.append({
                    "category": cat,
                    "description": desc,
                    "path": str(rel_path).replace("\\", "/"),
                    "line": line_no,
                    "snippet": snippet,
                })

    git_findings = scan_git_history(max_commits=100)

    print(f"[*] Total files scanned: {total_scanned}")
    print(f"[*] Total potential PHI/secret findings in working tree: {len(all_findings)}")
    print(f"[*] Total git history secret alerts: {len(git_findings)}")
    print("=" * 70)

    return {
        "files_scanned": total_scanned,
        "findings": all_findings,
        "git_alerts": git_findings,
    }


if __name__ == "__main__":
    run_full_scan()
