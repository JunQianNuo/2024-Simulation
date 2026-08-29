import copy
import unittest

import numpy as np

from q4 import run_q4 as q4


class Q4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = q4.read_evidence(q4.DEMO)

    def test_demo_schema_and_conditioning(self):
        self.assertEqual(set(self.evidence["q3"]), set(q4.Q3_NAMES))
        self.assertEqual(self.evidence["q2"]["case_1"]["pf"]["conditioning"], "all_inputs_good")

    def test_invalid_conditioning_fails_closed(self):
        bad = copy.deepcopy(self.evidence["q2"]["case_1"])
        bad["pf"]["conditioning"] = "component"
        with self.assertRaisesRegex(ValueError, "INVALID_CONDITIONING"):
            q4.validate_records(bad, {"p1": "component", "p2": "component", "pf": "all_inputs_good"}, "case", "fixed_n")

    def test_fixed_n_interval_contains_estimate(self):
        record = self.evidence["q2"]["case_1"]["p1"]
        lo, hi, method = q4.simultaneous_interval(record, .1 / 3, "fixed_n")
        self.assertLessEqual(lo, record["K"] / record["N"])
        self.assertGreaterEqual(hi, record["K"] / record["N"])
        self.assertEqual(method, "clopper_pearson_fixed_n")

    def test_posterior_metrics_probability_and_regret(self):
        values = np.array([[1., 1., -np.inf], [2., 1., -np.inf], [1., 2., -np.inf], [2., 2., -np.inf]])
        plan = {"epsilon_profit": 10., "epsilon_prob": 1.}
        result = q4.posterior_metrics(values, ["SUCCESS_EXACT", "SUCCESS_EXACT", "NON_ABSORBING"], plan, 4)
        self.assertAlmostEqual(np.nansum(result["optimal"]), 1.)
        self.assertGreaterEqual(np.nanmin(result["regret"]), 0.)
        self.assertTrue(np.isnan(result["mean"][2]))

    def test_q2_current_interface(self):
        records = self.evidence["q2"]["case_1"]
        row = q4.q2_evaluator(1, q4.point_estimates(records, q4.Q2_NAMES))((1, 1, 0, 1))
        self.assertIn(row["status"], {"SUCCESS_EXACT", "NEAR_NONABSORBING"})
        self.assertTrue(np.isfinite(row["expected_profit"]))


if __name__ == "__main__":
    unittest.main()
