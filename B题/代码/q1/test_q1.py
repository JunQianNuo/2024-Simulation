from __future__ import annotations

import itertools
import unittest
from pathlib import Path

import numpy as np

from .confidence_sequence import crosscheck_endpoints, fixed_sample_baselines, official_boundaries
from .run_q1 import candidates, evaluate_cutoffs, load_config


class Q1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config(Path(__file__).with_name("config.json"))

    def test_fixed_sample_baselines(self):
        values = fixed_sample_baselines()
        self.assertAlmostEqual(values["U_0.90(22,0)"], 1 - 0.1 ** (1 / 22), places=12)
        self.assertAlmostEqual(values["L_0.95(2,2)"], 0.05 ** 0.5, places=12)

    def test_declared_grid_has_34_candidates(self):
        self.assertEqual(len(candidates(self.cfg)), 34)

    def test_official_reference_value(self):
        from confseq import boundaries

        value = boundaries.beta_binomial_log_mixture(10, 100, 100, 0.2, 0.8)
        self.assertAlmostEqual(value, -0.07134019, places=7)

    def test_endpoint_crosscheck(self):
        rows = crosscheck_endpoints(100, [(25, 0), (50, 5), (200, 20), (800, 100)], 0.05, 0.10)
        self.assertLess(max(row["max_abs_error"] for row in rows), 1e-8)

    def test_boundaries_are_disjoint_and_monotone(self):
        accept, reject = official_boundaries(400, 0.1, 0.05, 0.10, 100)
        self.assertTrue(np.all(accept < reject))
        self.assertGreaterEqual(np.flatnonzero(accept >= 0)[0], 22)

    def test_probability_conservation_and_error_constraints(self):
        accept, reject = official_boundaries(800, 0.1, 0.05, 0.10, 100)
        for p in (0.01, 0.05, 0.10, 0.100001, 0.15, 0.30):
            row = evaluate_cutoffs(p, accept, reject, [800])[800]
            self.assertLess(row["mass_residual"], 1e-10)
            if p <= 0.10:
                self.assertLessEqual(row["P_reject"], 0.05 + 1e-10)
            else:
                self.assertLessEqual(row["P_accept"], 0.10 + 1e-10)

    def test_dp_against_path_enumeration(self):
        n_max, p = 10, 0.23
        accept = np.full(n_max + 1, -1)
        reject = np.full(n_max + 1, n_max + 1)
        accept[4:] = 0
        reject[3:] = np.arange(3, n_max + 1)
        got = evaluate_cutoffs(p, accept, reject, [n_max])[n_max]
        acc = rej = und = asn = 0.0
        prefixes = set()
        for bits in itertools.product((0, 1), repeat=n_max):
            k = 0
            for t, bit in enumerate(bits, 1):
                k += bit
                if k <= accept[t] or k >= reject[t] or t == n_max:
                    prefix = bits[:t]
                    if prefix in prefixes:
                        break
                    prefixes.add(prefix)
                    prob = p ** sum(prefix) * (1 - p) ** (t - sum(prefix))
                    asn += prob * t
                    if k <= accept[t]:
                        acc += prob
                    elif k >= reject[t]:
                        rej += prob
                    else:
                        und += prob
                    break
        self.assertAlmostEqual(got["P_accept"], acc, places=12)
        self.assertAlmostEqual(got["P_reject"], rej, places=12)
        self.assertAlmostEqual(got["P_undecided"], und, places=12)
        self.assertAlmostEqual(got["ASN"], asn, places=12)


if __name__ == "__main__":
    unittest.main()
