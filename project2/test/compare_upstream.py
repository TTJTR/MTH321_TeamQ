"""Compare the pinned algorithm archive with the output of its unmodified run_all.py."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def load_rows(directory, filename, key_fields):
    rows = read_csv(directory / "results" / filename)
    by_key = {tuple(row[k] for k in key_fields): row for row in rows}
    if len(rows) != len(by_key):
        raise ValueError(f"Duplicate keys in {directory / 'results' / filename}")
    return by_key


def compare(archive, rerun, output):
    groups = {
        "smooth.csv": ("method", "N"),
        "layered.csv": ("method", "face_rule", "N"),
        "conditioning.csv": ("contrast", "N"),
        "tolerance_sweep.csv": ("method", "N", "rtol"),
        "timing_repeats.csv": ("case", "method", "face_rule", "N", "repeat"),
    }
    summaries = []
    for filename, keys in groups.items():
        baseline = load_rows(archive, filename, keys)
        current = load_rows(rerun, filename, keys)
        if baseline.keys() != current.keys():
            raise ValueError(f"Row keys differ in {filename}")
        if not baseline:
            raise ValueError(f"No rows in {filename}")
        fields = next(iter(baseline.values())).keys() - set(keys)
        for key, row in baseline.items():
            if row.keys() != current[key].keys():
                raise ValueError(f"Columns differ for {filename}, {key}")
        for field in sorted(fields):
            pairs = [(key, row[field], current[key][field]) for key, row in baseline.items()]
            pairs = [(key, old, new) for key, old, new in pairs if old or new]
            if not pairs:
                continue
            try:
                numbers = [(key, float(old), float(new)) for key, old, new in pairs]
            except ValueError:
                if any(old != new for _, old, new in pairs):
                    raise ValueError(f"Non-numeric metadata differ in {filename}, {field}")
                continue
            key, old, new = max(numbers, key=lambda row: abs(row[2] - row[1]))
            summaries.append({
                "file": filename, "field": field, "rows": len(numbers),
                "unit": "seconds" if "seconds" in field else "as_in_archive",
                "max_abs_difference": abs(new - old), "worst_row": "/".join(key),
                "archive_value": old, "rerun_value": new,
            })
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    for root in (archive, rerun):
        environment = json.loads((root / "results" / "environment.json").read_text(encoding="utf-8"))
        for path, expected in environment["source_sha256"].items():
            data = (root / path).read_bytes()
            lf = data.replace(b"\r\n", b"\n")
            variants = (("exact", data), ("LF", lf), ("CRLF", lf.replace(b"\n", b"\r\n")))
            match = next((mode for mode, value in variants if hashlib.sha256(value).hexdigest() == expected), "DIFFERENT")
            print(root.name, path, match)
    for root in (archive, rerun):
        rows = read_csv(root / "results" / "smooth.csv")
        for method in ("FDM", "FEM"):
            selected = sorted((row for row in rows if row["method"] == method), key=lambda row: int(row["N"]))[-3:]
            hs = np.log([float(row["h"]) for row in selected])
            fits = {
                field: np.polyfit(hs, np.log([float(row[field]) for row in selected]), 1)[0]
                for field in ("l2_nodal", "linf_nodal", "l2_common")
            }
            print(root.name, method, [int(row["N"]) for row in selected], fits)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="untouched algorithm_section with committed results")
    parser.add_argument("rerun", type=Path, help="separate copy after run_all.py")
    parser.add_argument("output", type=Path, help="CSV path for the difference summary")
    args = parser.parse_args()
    compare(args.archive, args.rerun, args.output)
