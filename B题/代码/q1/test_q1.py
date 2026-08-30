from __future__ import annotations

import itertools
import unittest

import numpy as np

from .exact_path_dp import BoundaryPlan, evaluate, fixed_plan_as_boundary, llr_boundaries
from .fixed_binomial_plan import minimum_plan, risks


class Q1Tests(unittest.TestCase):
    def test_fixed_plan_oracles(self):
        expected = {
            .12: (2096, 232, .0493657550, .0995398380),
            .13: (968, 112, .0486497073, .0997558579),
            .15: (368, 46, .0496448526, .0999328161),
            .20: (109, 16, .0432080762, .0990770489),
        }
        for p1, oracle in expected.items():
            plan = minimum_plan(.10, p1, .05, .10)
            self.assertEqual((plan["n_fixed"], plan["c_fixed"]), oracle[:2])
            self.assertAlmostEqual(plan["producer_risk"], oracle[2], places=9)
            self.assertAlmostEqual(plan["consumer_risk"], oracle[3], places=9)

    def test_fixed_plan_is_binary_and_exact(self):
        plan = fixed_plan_as_boundary(.1, .13, 968, 112)
        for p in (0, .1, .13, .5, 1):
            row = evaluate(plan, p)
            self.assertLess(row["mass_residual"], 1e-12)
            self.assertAlmostEqual(row["P_accept"] + row["P_reject"], 1, places=12)
            self.assertEqual(row["ASN"], 968)
        oracle = risks(968, 112, .1, .13)
        actual = evaluate(plan, .1)["P_reject"], evaluate(plan, .13)["P_accept"]
        self.assertAlmostEqual(oracle[0], actual[0], places=12)
        self.assertAlmostEqual(oracle[1], actual[1], places=12)

    def test_llr_boundaries_are_disjoint(self):
        accept, reject = llr_boundaries(200, .1, .13, -2.3, 2.9)
        self.assertTrue(all(a < r for a, r in zip(accept[:-1], reject[:-1])))

    def test_path_dp_against_complete_enumeration(self):
        n, p = 8, .23
        accept = [-1] * (n + 1); reject = [n + 1] * (n + 1)
        accept[3:5] = [0, 0]; reject[3:5] = [3, 4]
        plan = BoundaryPlan(.1, .2, n, 1, tuple(accept), tuple(reject), -2, 3, "test")
        got = evaluate(plan, p)
        accepted = rejected = asn = 0.0
        for bits in itertools.product((0, 1), repeat=n):
            k = 0
            probability = 1.0
            for t, bit in enumerate(bits, 1):
                k += bit; probability *= p if bit else 1 - p
                decision = None
                if t == n:
                    decision = "A" if k <= plan.terminal_cutoff else "R"
                elif k <= plan.accept_max[t]:
                    decision = "A"
                elif k >= plan.reject_min[t]:
                    decision = "R"
                if decision:
                    suffix_probability = p ** sum(bits[t:]) * (1 - p) ** (n - t - sum(bits[t:]))
                    path_probability = probability * suffix_probability
                    asn += t * path_probability
                    accepted += path_probability if decision == "A" else 0
                    rejected += path_probability if decision == "R" else 0
                    break
        self.assertAlmostEqual(got["P_accept"], accepted, places=12)
        self.assertAlmostEqual(got["P_reject"], rejected, places=12)
        self.assertAlmostEqual(got["ASN"], asn, places=12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
