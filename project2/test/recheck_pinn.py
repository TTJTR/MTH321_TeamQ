"""Re-evaluate frozen Direction 3 layered PINN evidence with NumPy only."""

import argparse
from collections import OrderedDict
import csv
import hashlib
import json
from pathlib import Path
import pickle
from zipfile import ZipFile

import numpy as np


CHECKPOINT_BLOBS = {
    "runs/server_interface/interface_c1_seed11": "e2ac9a89a883c3084afce77987aa4fd4436c66af",
    "runs/server_interface/interface_c1_seed22": "e98d121966b526357485580db0febcab13008089",
    "runs/server_interface/interface_c1_seed33": "36ed5fab502790334159abc0e45ee8e8d30f9f58",
    "runs/server_interface/interface_c10_seed11": "e535fe7ef4ceede43ab813a9a7611ae142ca6936",
    "local_validation/local_smoke/interface_c10_seed42": "c383aec7b66169e12fcc85ad5cdd663eeaffdce0",
    "local_validation/local_single/single_c10_seed42": "d89c8b93e1855bd401167f329bb2b453759393af",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def exact(x, contrast):
    resistance = np.minimum(x, 0.5) + np.maximum(x - 0.5, 0) / contrast
    total = 0.5 + 0.5 / contrast
    return resistance / total, -1.0 / total


def flux_metrics(left, right, reference):
    jump = float(np.max(abs(left - right)))
    return {
        "interface_flux_jump_max": jump,
        "interface_flux_relative_max": jump / abs(reference),
        "interface_flux_error_max": float(max(np.max(abs(left - reference)), np.max(abs(right - reference)))),
    }


def solution_metrics(prediction, reference):
    # Composite trapezoidal quadrature on [0, 1]^2 with endpoint-inclusive uniform grid.
    n = prediction.shape[0] - 1
    weights = np.ones(n + 1)
    weights[[0, -1]] = 0.5
    weights = np.outer(weights, weights) / n**2
    error = prediction - reference
    l2 = np.sqrt(np.sum(weights * error**2))
    return {
        "l2": float(l2),
        "relative_l2": float(l2 / np.sqrt(np.sum(weights * reference**2))),
        "linf": float(np.max(abs(error))),
        "boundary_linf": float(max(np.max(abs(error[[0, -1], :])), np.max(abs(error[:, [0, -1]])))),
    }


def check_saved(metrics, saved):
    differences = {key: abs(value - saved[key]) for key, value in metrics.items()}
    if max(differences.values()) > 5e-12:
        raise ValueError(f"Archive metric mismatch: {differences}")
    return max(differences.values())


def audit_arrays(supplement):
    stem = supplement / "data/c100_seed11_interface.npz"
    saved = load_json(supplement / "data/c100_seed11_metrics.json")
    with np.load(stem, allow_pickle=False) as data:
        t = np.arange(201) / 200
        x, y = np.meshgrid(t, t, indexing="ij")
        np.testing.assert_allclose(data["x"], x, atol=2e-16, rtol=0)
        np.testing.assert_allclose(data["y"], y, atol=2e-16, rtol=0)
        np.testing.assert_allclose(data["interface_y"], t, atol=2e-16, rtol=0)
        reference, q = exact(x, 100.0)
        np.testing.assert_allclose(data["exact"], reference, atol=3e-16, rtol=0)
        np.testing.assert_allclose(data["error"], data["u"] - reference, atol=3e-16, rtol=0)
        metrics = solution_metrics(data["u"], reference)
        metrics.update(flux_metrics(data["flux_left"], data["flux_right"], q))
        metrics["max_abs_difference_from_saved"] = check_saved(metrics, saved)
        metrics["flux_exact"] = q
        metrics["interface_flux_error_relative_max"] = metrics["interface_flux_error_max"] / abs(q)
        metrics["source_sha256"] = hashlib.sha256(stem.read_bytes()).hexdigest()
    return metrics


def audit_csv(supplement, config, snapshot):
    keys = ["relative_l2", "linf", "interface_value_max", "interface_flux_relative_max",
            "interface_flux_error_max", "train_seconds", "parameters"]
    source = supplement / "data/run_metrics.csv"
    with source.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    archive = {(r["method"], float(r["contrast"]), int(r["seed"])): r for r in rows}
    expected = {(m, c, s) for m in ("interface", "single") for c in config["contrasts"] for s in config["seeds"]}
    if len(rows) != len(expected) or archive.keys() != expected:
        raise ValueError("Unexpected run grid or duplicate rows")

    repo_comparisons = 0
    groups = []
    for method in ("interface", "single"):
        for contrast in config["contrasts"]:
            parsed = []
            for seed in config["seeds"]:
                row = archive[method, contrast, seed]
                metrics = {k: float(row[k]) for k in keys}
                accepted = all(metrics[k] <= v for k, v in config["acceptance"].items())
                if str(accepted) != row["accepted"]:
                    raise ValueError(f"Acceptance mismatch for {method}, c={contrast}, seed={seed}")
                if method == "single" and (metrics["interface_value_max"] != 0 or
                                           (contrast == 1 and metrics["interface_flux_relative_max"] != 0)):
                    raise ValueError("A structural zero of the single-network method was lost")
                record = snapshot / f"runs/server_{method}/{method}_c{contrast:g}_seed{seed}/metrics.json"
                if record.is_file():
                    saved = load_json(record)
                    check_saved(metrics, saved)
                    if saved["accepted"] != accepted or saved["adam_steps"] != config["adam_steps"]:
                        raise ValueError(f"Training metadata mismatch for {record}")
                    repo_comparisons += 1
                parsed.append(dict(seed=seed, **metrics, accepted=accepted))
            stats = {}
            for key in keys:
                values = np.array([item[key] for item in parsed])
                stats[key] = dict(mean=float(values.mean()), sample_std=float(values.std(ddof=1)),
                                  min=float(values.min()), max=float(values.max()))
            groups.append(dict(method=method, contrast=contrast, accepted=sum(r["accepted"] for r in parsed),
                               statistics=stats, rows=parsed))
    return dict(groups=groups, repo_comparisons=repo_comparisons, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())


def rebuild_tensor(storage, offset, shape, stride, requires_grad, hooks):
    array = storage.reshape(-1)
    start = int(offset)
    view = array[start:start + int(np.prod(shape))].reshape(shape)
    if tuple(s // view.itemsize for s in view.strides) != stride:
        raise ValueError("Unexpected noncontiguous tensor in state_dict")
    return view


def checkpoint(path):
    # Read the pinned ZIP state_dict format without importing PyTorch or executing arbitrary pickle globals.
    # This decoder intentionally supports only the simple contiguous float64 tensors in these archives.
    with ZipFile(path) as archive:
        if archive.read("checkpoint/byteorder") != b"little":
            raise ValueError("Expected little-endian archive")

        class StateReader(pickle.Unpickler):
            def find_class(self, module, name):
                return {
                    ("collections", "OrderedDict"): OrderedDict,
                    ("torch._utils", "_rebuild_tensor_v2"): rebuild_tensor,
                    ("torch", "DoubleStorage"): "float64",
                }[module, name]

            def persistent_load(self, identity):
                kind, dtype, index, _device, size = identity
                if kind != "storage" or dtype != "float64" or not index.isdecimal():
                    raise ValueError("Unexpected tensor storage record")
                raw = archive.read(f"checkpoint/data/{index}")
                if len(raw) != size * 8:
                    raise ValueError("Unexpected tensor storage length")
                return np.frombuffer(raw, dtype="<f8")

        with archive.open("checkpoint/data.pkl") as stream:
            return StateReader(stream).load()


def network(z, state, depth, side, derivatives=False):
    v = 2 * z - 1
    if derivatives:
        dx = np.broadcast_to((2.0, 0.0), v.shape)
        dy = np.broadcast_to((0.0, 2.0), v.shape)
        lap = np.zeros_like(v)
    for layer in range(depth + 1):
        name = f"networks.{side}.layers.{2 * layer}"
        wt, b = state[name + ".weight"].T, state[name + ".bias"]
        v = v @ wt + b
        if derivatives:
            dx, dy, lap = dx @ wt, dy @ wt, lap @ wt
        if layer < depth:
            v = np.tanh(v)
            if derivatives:
                first = 1 - v**2
                second = -2 * v * first
                lap = first * lap + second * (dx**2 + dy**2)
                dx, dy = first * dx, first * dy
    return (v.ravel(), dx.ravel(), lap.ravel()) if derivatives else v.ravel()


def traces(state, depth, right_side, contrast, t):
    interface = np.column_stack((np.full_like(t, 0.5), t))
    left, dx_left, _ = network(interface, state, depth, 0, True)
    right, dx_right, _ = network(interface, state, depth, right_side, True)
    q = exact(0.5, contrast)[1]
    return dict(interface_value_max=float(np.max(abs(left - right))),
                **flux_metrics(-dx_left, -contrast * dx_right, q))


def residuals(state, depth, right_side, contrast, n):
    t = (np.arange(n) + 0.5) / n
    results = {}
    for side, name, a in [(0, "left", 1.0), (1, "right", contrast)]:
        x, y = np.meshgrid(side / 2 + t / 2, t, indexing="ij")
        z = np.column_stack((x.ravel(), y.ravel()))
        _, _, lap = network(z, state, depth, side * right_side, True)
        results[f"heldout_pde_rms_{name}"] = float(a * np.sqrt(np.mean(lap**2)))
    return results


def audit_checkpoint(path, expected_blob):
    archive = path.read_bytes()
    git_blob_sha1 = hashlib.sha1(f"blob {len(archive)}\0".encode() + archive).hexdigest()
    if git_blob_sha1 != expected_blob:
        raise ValueError(f"Checkpoint differs from the pinned Git blob: {path}")
    ckpt = checkpoint(path)
    state, cfg, contrast = ckpt["model"], ckpt["config"], ckpt["contrast"]
    if cfg != load_json(path.parent.parent / "config.json") or cfg["case"] != "layered":
        raise ValueError(f"Checkpoint configuration mismatch: {path}")
    depth = cfg["depth"]
    right_side = int(cfg["method"] == "interface")
    t = np.linspace(0, 1, cfg["eval_intervals"] + 1)
    x, y = np.meshgrid(t, t, indexing="ij")
    z = np.column_stack((x.ravel(), y.ravel()))
    left = z[:, 0] <= 0.5
    prediction = np.empty(len(z))
    for selection, side in ((left, 0), (~left, right_side)):
        prediction[selection] = network(z[selection], state, depth, side)
    reference, _ = exact(x, contrast)
    metrics = solution_metrics(prediction.reshape(x.shape), reference)
    metrics.update(traces(state, depth, right_side, contrast, t))
    metrics.update(residuals(state, depth, right_side, contrast, 16))
    saved = load_json(path.with_name("metrics.json"))
    matches = check_saved(metrics, saved)
    if saved["parameters"] != sum(value.size for value in state.values()):
        raise ValueError(f"Unexpected parameter count: {path}")
    return dict(method=cfg["method"], contrast=contrast, seed=ckpt["seed"], git_blob_sha1=git_blob_sha1,
                recorded_grid=metrics, max_abs_difference_from_saved=matches,
                new_heldout_grids=dict(**residuals(state, depth, right_side, contrast, 29),
                                       **traces(state, depth, right_side, contrast, (np.arange(293) + 0.37) / 293)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supplement", type=Path, required=True, help="local I-PINNs_supplement directory")
    parser.add_argument("--snapshot", type=Path, required=True, help="pinned project2/I-PINNs directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.snapshot
    server = root / "runs/server_interface"
    archive_config = load_json(root / "configs/server.json")
    metadata = load_json(server / "environment.json")
    source_checks = {}
    for name, sha in metadata["source_sha256"].items():
        source_checks[name] = hashlib.sha256((root / name).read_bytes()).hexdigest() == sha
    if not all(source_checks.values()):
        raise ValueError(f"Pinned source differs from recorded server source: {source_checks}")
    checkpoints = {path: audit_checkpoint(root / path / "checkpoint.pt", sha)
                   for path, sha in CHECKPOINT_BLOBS.items()}
    results = dict(array_recomputation=audit_arrays(args.supplement), source_checks=source_checks,
                   acceptance=archive_config["acceptance"], cross_seed=audit_csv(args.supplement, archive_config, root),
                   checkpoint_re_evaluation=checkpoints)
    args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Checked 18 metric rows, one prediction archive and {len(checkpoints)} checkpoints. Wrote {args.output}")


if __name__ == "__main__":
    main()
