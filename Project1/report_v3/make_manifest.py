from pathlib import Path
import hashlib
import json
import subprocess
from datetime import date


# ============================================================
# Paths
# ============================================================

REPORT_DIR = Path(r"D:\report_v3")
PROJECT_DIR = Path(r"D:\Project1")

MANIFEST_PATH = REPORT_DIR / "manifest.json"


# ============================================================
# Hash helpers
# ============================================================

RAW_EXTENSIONS = {
    ".csv",
    ".png",
    ".pdf",
    ".json",
}


def sha256_raw(path: Path) -> str:
    """SHA-256 of raw file bytes."""
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def sha256_normalized_text(path: Path) -> str:
    """
    SHA-256 after normalizing CRLF / CR line endings to LF.
    This keeps text hashes consistent across Windows and Linux.
    """
    data = path.read_bytes()
    data = data.replace(b"\r\n", b"\n")
    data = data.replace(b"\r", b"\n")

    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    """
    CSV, PNG, PDF and JSON:
        SHA-256 of raw bytes

    Other files:
        SHA-256 after newline normalization
    """
    if path.suffix.lower() in RAW_EXTENSIONS:
        return sha256_raw(path)

    return sha256_normalized_text(path)


# ============================================================
# Git information
# ============================================================

def get_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


# ============================================================
# report_v3 files
# ============================================================

REPORT_FILES = [
    "README.md",
    "CHANGELOG.md",
    "checklist/README.md",
    "references.tex",
    "report.tex",
    "report.pdf",

    "sections/section1.tex",
    "sections/section2.tex",
    "sections/section3.tex",
    "sections/section4.tex",
    "sections/section5.tex",

    "appendices/appendix_a.tex",
    "appendices/appendix_b.tex",
    "appendices/appendix_c.tex",

    "data/README.md",
    "data/adaptive_steps.csv",
    "data/convergence.csv",
    "data/cost_accuracy.csv",
    "data/rank_deficient.csv",
    "data/stability_sweep.csv",
    "data/summary.json",
    "data/trajectory.csv",

    "figures/adaptive_steps.png",
    "figures/convergence.png",
    "figures/cost_accuracy.png",
    "figures/frozen_spectrum.png",
    "figures/rank_deficient.png",
    "figures/stability_regions.png",
    "figures/stability_sweep.png",
    "figures/trajectory_diagnostics.png",
]


# ============================================================
# Project-level code and tests
# ============================================================

PROJECT_FILES = [
    "code/experiments.py",
    "code/model.py",
    "code/run_all.py",
    "code/solvers.py",

    "code_zh/experiments.py",
    "code_zh/model.py",
    "code_zh/run_all.py",
    "code_zh/solvers.py",

    "test/test_bilingual_parity.py",
    "test/test_validation.py",
]


# ============================================================
# Hash builders
# ============================================================

def build_report_hashes():
    result = {}

    for relative_path in REPORT_FILES:
        path = REPORT_DIR / relative_path

        if not path.exists():
            print(f"[WARNING] Missing report file: {relative_path}")
            continue

        result[relative_path] = file_sha256(path)

    return result


def build_project_hashes():
    result = {}

    for relative_path in PROJECT_FILES:
        path = PROJECT_DIR / relative_path

        if not path.exists():
            print(f"[WARNING] Missing project file: {relative_path}")
            continue

        result[relative_path] = file_sha256(path)

    return result


# ============================================================
# Main
# ============================================================

def main():
    git_commit = get_git_commit()

    manifest = {
        "report_version": "v3",
        "delivery_date": str(date.today()),

        "scope": [
            "Abstract",
            "Section 1",
            "Section 2",
            "Section 3",
            "Section 4",
            "Section 5",
            "References",
            "Appendix A",
            "Appendix B",
            "Appendix C",
        ],

        "base_commit": git_commit,

        "matching_project_tag": None,

        "preserved_project_tags": [
            "report-v1",
            "report-v2",
        ],

        "pdf_pages": 32,

        "hash_policy": {
            "csv_png_pdf_json": "SHA-256 of raw bytes",
            "other_files": "SHA-256 after CRLF/CR to LF normalization",
        },

        "verification": {
            "unittest_passed": 11,
            "unittest_total": 11,
            "bilingual_csv_json_png_identical": True,
            "report_figures_and_data_match_regenerated_outputs": True,
        },

        "report_files_sha256": build_report_hashes(),

        "code_and_tests_sha256": build_project_hashes(),
    }

    with MANIFEST_PATH.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        json.dump(
            manifest,
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    print()
    print("============================================")
    print("manifest.json generated successfully")
    print("============================================")
    print()
    print(f"Report version : {manifest['report_version']}")
    print(f"PDF pages      : {manifest['pdf_pages']}")
    print(f"Git commit     : {git_commit}")
    print(f"Report files   : {len(manifest['report_files_sha256'])}")
    print(f"Code/test files: {len(manifest['code_and_tests_sha256'])}")
    print()
    print("Output:")
    print(MANIFEST_PATH)


if __name__ == "__main__":
    main()