from __future__ import annotations

import copy
import unittest

import numpy as np

from q2 import model as q2_model
from q3 import model as q3_model
from q4 import run_q4 as q4
from q4.batch_evaluators import Q2_POLICIES, q2_profit_batch, q3_profit_batch
from q4.belief_state import BeliefState, from_records, marginal_cost
from q4.exact_voi_dp import Q2VoiDP
from q4.kg_rollout import rollout_with_oracle
from q4.kg_rollout import q3_knowledge_gradient
from q4.simultaneous_cs import simultaneous_interval
from q4.terminal_value import q2_terminal_value


class Q4Tests(unittest.TestCase):
    def test_q3_kg_requires_multiple_scrambles(self):
        belief = BeliefState(q4.Q3_NAMES, tuple([11.0] * 12), tuple([91.0] * 12))
        with self.assertRaises(ValueError):
            q3_knowledge_gradient(belief, tuple([1.0] * 12), 2, 1, 1, 2, .95, .01)

    @classmethod
    def setUpClass(cls):
        cls.config = q4.read_json(q4.CONFIG_PATH)
        cls.evidence = q4.read_evidence(q4.DEMO)

    def test_schema_conditioning_and_costs(self):
        record = self.evidence["q2"]["case_1"]["pf"]
        self.assertEqual(record["conditioning"], "all_inputs_good")
        self.assertGreater(marginal_cost(record), record["sample_test_cost"])
        bad = copy.deepcopy(self.evidence)
        bad["q3"]["semi_1"]["conditioning"] = "component"
        with self.assertRaisesRegex(ValueError, "INVALID_CONDITIONING"):
            q4.read_evidence_from_object(bad) if hasattr(q4, "read_evidence_from_object") else q4.validate_records(
                bad["q3"], {**{f"part_{i}": "component" for i in range(1, 9)},
                            **{f"semi_{i}": "all_inputs_good" for i in range(1, 4)},
                            "final": "all_inputs_good"}, "q3", "fixed_n")

    def test_fixed_and_sequential_intervals(self):
        record = self.evidence["q2"]["case_1"]["p1"]
        lo, hi, method = simultaneous_interval(record, .1 / 3, "fixed_n")
        self.assertLessEqual(lo, .1); self.assertGreaterEqual(hi, .1)
        self.assertEqual(method, "clopper_pearson_fixed_n")
        sequential = {**record, "stopping_rule": "sequential_cs", "t_opt": 100}
        lo2, hi2, method2 = simultaneous_interval(sequential, .1 / 3, "fixed_n")
        self.assertLessEqual(lo2, .1); self.assertGreaterEqual(hi2, .1)
        self.assertIn("time_uniform", method2)

    def test_q2_terminal_quadrature_converges(self):
        cases, _ = q4.load_q2_inputs()
        records = self.evidence["q2"]["case_1"]
        belief = from_records(records, q4.Q2_NAMES, (1, 1))
        result = q2_terminal_value(cases[0], belief, [8, 12, 16, 24], 1e-5)
        self.assertEqual(result.status, "VALUE_INTEGRATION_CONVERGED")
        self.assertGreaterEqual(result.evpi, 0)
        self.assertGreaterEqual(result.best_optimal_probability, 0)

    def test_q2_dp_degenerates_at_zero_horizon(self):
        cases, _ = q4.load_q2_inputs()
        records = self.evidence["q2"]["case_1"]
        belief = from_records(records, q4.Q2_NAMES, (1, 1))
        solver = Q2VoiDP(cases[0], belief, tuple(marginal_cost(records[n]) for n in q4.Q2_NAMES),
                         0, [8, 12, 16], 1e-5, 1000)
        result = solver.solve()
        self.assertEqual(result.initial_action, "STOP")
        self.assertAlmostEqual(result.value, result.stop_value)
        self.assertEqual(result.expected_samples, 0)

    def test_q2_batch_matches_markov_solver(self):
        cases, config = q4.load_q2_inputs()
        case = cases[0]
        actual, _ = q2_profit_batch(case, np.array([[case["p1"], case["p2"], case["pf"]]]))
        expected = np.array([q2_model.evaluate_policy(tuple(policy), case, config)["expected_profit"]
                             if q2_model.evaluate_policy(tuple(policy), case, config)["status"] == "SUCCESS_EXACT"
                             else -np.inf for policy in Q2_POLICIES])
        mask = np.isfinite(expected)
        self.assertLess(np.max(np.abs(actual[0, mask] - expected[mask])), 1e-9)

    def test_q3_batch_matches_kernel_on_declared_subset(self):
        parameters = np.array([[q3_model.q3_nominal_parameters()[name] for name in q4.Q3_NAMES]])
        ids = np.array([0, 255, 4095, 32768, 63487, 65535])
        actual, _ = q3_profit_batch(parameters, ids)
        expected = []
        for strategy in ids:
            row = q3_model.evaluate(int(strategy))
            expected.append(row["expected_profit"] if row["status"] == "SUCCESS_EXACT" else -np.inf)
        expected = np.asarray(expected); mask = np.isfinite(expected)
        self.assertLess(np.max(np.abs(actual[0, mask] - expected[mask])), 1e-8)

    def test_generic_rollout_micro_oracle(self):
        terminal = lambda state: max(state)
        predictive = lambda state, action: .5
        update = lambda state, action, bad: tuple(x + (1 if i == action and bad else 0)
                                                  for i, x in enumerate(state))
        base = lambda state: "STOP"
        cost = lambda state, action: .1
        result = rollout_with_oracle((0, 0), ["STOP", 0, 1], 1, 1000, 2024,
                                     predictive, update, terminal, base, cost)
        self.assertAlmostEqual(result["STOP"]["mean"], 0)
        self.assertGreater(result[0]["mean"], result["STOP"]["mean"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
