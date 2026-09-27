"""Confirm the separately runnable English and Chinese source trees agree."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PROBE = """
import json
import numpy as np
from model import benchmark, exact_matrix, jacobian, rhs, vectorize
from solvers import solve_adaptive, solve_fixed

x0 = benchmark()
y0 = vectorize(x0)
result = {
    'x0': x0.tolist(),
    'rhs': rhs(0, y0).tolist(),
    'jacobian': jacobian(0, y0).tolist(),
    'exact_t2': exact_matrix(2, x0).tolist(),
    'fixed': {},
}
for method in ('euler', 'rk4', 'implicit_euler'):
    solution = solve_fixed(method, rhs, jacobian, y0, (0, 2), 80)
    result['fixed'][method] = solution.y[-1].tolist()
adaptive = solve_adaptive('rk4', rhs, jacobian, y0, (0, 2), 0.15,
                          atol=1e-8, rtol=1e-6)
result['adaptive'] = {
    'time': adaptive.t.tolist(),
    'final': adaptive.y[-1].tolist(),
    'errors': adaptive.error_ratios.tolist(),
    'rejected': adaptive.rejected,
}
print(json.dumps(result))
"""


def probe(folder: str) -> dict:
    output = subprocess.check_output(
        [sys.executable, "-c", PROBE], cwd=ROOT / folder, text=True,
        encoding="utf-8")
    return json.loads(output)


class BilingualParity(unittest.TestCase):
    def test_english_and_chinese_sources_agree(self):
        english = probe("code")
        chinese = probe("code_zh")
        for key in ("x0", "rhs", "jacobian", "exact_t2"):
            with self.subTest(quantity=key):
                np.testing.assert_allclose(english[key], chinese[key], rtol=0, atol=1e-14)
        for method in ("euler", "rk4", "implicit_euler"):
            with self.subTest(method=method):
                np.testing.assert_allclose(english["fixed"][method],
                                           chinese["fixed"][method], rtol=0, atol=1e-14)
        self.assertEqual(english["adaptive"]["rejected"], chinese["adaptive"]["rejected"])
        for key in ("time", "final", "errors"):
            np.testing.assert_allclose(english["adaptive"][key],
                                       chinese["adaptive"][key], rtol=0, atol=1e-14)


if __name__ == "__main__":
    unittest.main()
