import copy
import unittest

import numpy as np

from q4 import run_q4 as q4
from q4.batch_evaluators import Q2_POLICIES, q2_profit_batch, q3_profit_batch
from q2 import model as q2_model
from q3 import model as q3_model


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

    def test_q2_batch_evaluator_matches_markov_solver(self):
        cases, config = q4.load_q2_inputs()
        for case in cases:
            parameters = np.array([[case["p1"], case["p2"], case["pf"]]])
            actual, _ = q2_profit_batch(case, parameters)
            expected = []
            for policy in Q2_POLICIES:
                row = q2_model.evaluate_policy(tuple(policy), case, config)
                expected.append(q4.valid_profit(row))
            expected = np.asarray(expected)
            mask = np.isfinite(expected)
            self.assertTrue(np.array_equal(np.isfinite(actual[0]), mask))
            self.assertLess(np.max(np.abs(actual[0, mask] - expected[mask])), 1e-10)

    def test_q3_batch_evaluator_matches_kernel_solver(self):
        names = tuple(q3_model.q3_nominal_parameters())
        parameters = np.array([[q3_model.q3_nominal_parameters()[name] for name in names]])
        ids = np.array([0, 7, 255, 4095, 32768, 47103, 63487, 65535])
        actual, _ = q3_profit_batch(parameters, ids)
        expected = np.asarray([q4.valid_profit(q3_model.evaluate(int(strategy))) for strategy in ids])
        mask = np.isfinite(expected)
        self.assertTrue(np.array_equal(np.isfinite(actual[0]), mask))
        self.assertLess(np.max(np.abs(actual[0, mask] - expected[mask])), 1e-9)

    def test_q3_batch_preserves_tiny_positive_nonabsorption(self):
        parameters = np.zeros((1, 12)); parameters[0, 0] = 1e-12; parameters[0, -1] = .1
        actual, feasible = q3_profit_batch(parameters, np.array([32768]))
        self.assertFalse(feasible[0, 0])
        self.assertTrue(np.isneginf(actual[0, 0]))

    def test_streaming_posterior_covers_q3_full_policy_domain(self):
        plan = q4.read_json(q4.CONFIG_PATH)["quick_plan"]["q3"]
        policies, evaluator = q4._batch_factory("q3")
        result = q4.posterior_run(policies, self.evidence["q3"], q4.Q3_NAMES,
                                  q4.PRIORS["uniform"], plan["explore_seed"], plan, evaluator, True)
        self.assertEqual(len(result["mean"]), 65536)
        self.assertAlmostEqual(np.nansum(result["optimal"]), 1.0)
        self.assertGreaterEqual(np.nanmin(result["regret"]), -q4.TOL)

    def test_robust_search_has_zero_gap_certificate(self):
        frame, audit = q4.robust_search("q2", self.evidence["q2"]["case_1"], q4.Q2_NAMES,
                                        90, "fixed_n", True, 1)
        certified = frame[frame.robust_status.eq("ROBUST_CERTIFIED")]
        self.assertTrue(audit["interval_certificate"])
        self.assertTrue((certified.inner_gap == 0).all())
        self.assertTrue((certified.worst_profit <= certified.nominal_profit + 1e-9).all())


if __name__ == "__main__":
    unittest.main()
