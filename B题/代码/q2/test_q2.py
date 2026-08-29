"""Q2 模型的独立验收测试。"""

from __future__ import annotations

import itertools
import random
import unittest

import pandas as pd

try:
    from .model import (
        BAD, GOOD, INFO_MISSING, KNOWN_GOOD, MISSING, NEW, SRC_MISSING, UNKNOWN,
        State, evaluate_policy, state_transitions,
    )
    from .run_q2 import POLICIES, audit_accounting, load_inputs, select_best
except ImportError:
    from model import (
        BAD, GOOD, INFO_MISSING, KNOWN_GOOD, MISSING, NEW, SRC_MISSING, UNKNOWN,
        State, evaluate_policy, state_transitions,
    )
    from run_q2 import POLICIES, audit_accounting, load_inputs, select_best


class Q2AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.config = load_inputs()

    def test_nominal_96_policies_and_regression_values(self):
        frame = pd.DataFrame(
            evaluate_policy(policy, case, self.config)
            for case in self.cases for policy in POLICIES
        )
        self.assertEqual(len(frame), 96)
        self.assertEqual(frame.groupby("status").size().to_dict(), {"NON_ABSORBING": 36, "SUCCESS_EXACT": 60})
        best = select_best(frame, self.config)
        actual = {
            case: (
                {tuple(map(int, row[["x1", "x2", "y", "z"]])) for _, row in group.iterrows()},
                group["expected_profit"].max(),
            )
            for case, group in best.groupby("case")
        }
        expected = {
            1: ({(1, 1, 0, 1)}, 17.5555555556),
            2: ({(1, 1, 0, 1)}, 10.75),
            3: ({(1, 1, 0, 1), (1, 1, 1, 1)}, 14.8888888889),
            4: ({(1, 1, 1, 1)}, 14.25),
            5: ({(0, 1, 0, 0)}, 11.9876543210),
            6: ({(0, 0, 0, 0)}, 21.6786703601),
        }
        for case, (policies, profit) in expected.items():
            self.assertEqual(actual[case][0], policies)
            self.assertAlmostEqual(actual[case][1], profit, places=8)
        audit_accounting(frame[frame.status == "SUCCESS_EXACT"], self.cases, self.config)

    def test_retained_known_good_component_is_not_reinspected(self):
        case, policy = self.cases[0], (1, 1, 0, 1)
        state = State("inspect1", GOOD, BAD, UNKNOWN, UNKNOWN, NEW, NEW)
        transitions, _, _, events = state_transitions(state, policy, case)
        self.assertEqual(events["expected_inspections_1"], 1.0)
        state = transitions[0][0]
        transitions, _, _, _ = state_transitions(state, policy, case)
        state = transitions[0][0]
        self.assertEqual((state.phase, state.z1, state.z2, state.k1), ("prepare", GOOD, MISSING, KNOWN_GOOD))
        transitions, _, _, _ = state_transitions(state, policy, case)
        retained = next(s for s, p in transitions if s.z2 == GOOD and p > 0)
        transitions, _, _, events = state_transitions(retained, policy, case)
        self.assertEqual(events["expected_inspections_1"], 0.0)
        self.assertEqual(transitions[0][0].phase, "inspect2")

    def test_disassembled_parts_keep_truth_and_are_retested(self):
        case, policy = self.cases[0], (1, 0, 1, 1)
        known_bad = State("known_bad", GOOD, BAD, KNOWN_GOOD, UNKNOWN, NEW, NEW)
        transitions, _, _, events = state_transitions(known_bad, policy, case)
        recovered = transitions[0][0]
        self.assertEqual((recovered.z1, recovered.z2), (GOOD, BAD))
        self.assertEqual((recovered.k1, recovered.k2, recovered.o1, recovered.o2), (UNKNOWN, UNKNOWN, "R", "R"))
        _, _, _, events = state_transitions(recovered, policy, case)
        self.assertEqual(events["expected_inspections_1"], 1.0)

    def test_micro_closed_form(self):
        case = {**self.cases[0], "case": 99, "p1": 0.0, "p2": 0.0, "pf": 0.2}
        result = evaluate_policy((0, 0, 0, 0), case, self.config)
        self.assertEqual(result["status"], "SUCCESS_EXACT")
        self.assertAlmostEqual(result["expected_assemblies"], 1.25, places=10)
        self.assertAlmostEqual(result["expected_purchases_1"], 1.25, places=10)
        self.assertAlmostEqual(result["expected_replacements"], 0.25, places=10)

    def test_boundary_probabilities_do_not_create_missing_edges(self):
        for p1, p2, pf in itertools.product((0.0, 1.0), repeat=3):
            case = {**self.cases[0], "case": 98, "p1": p1, "p2": p2, "pf": pf}
            for policy in POLICIES:
                result = evaluate_policy(policy, case, self.config)
                self.assertLessEqual(result["row_sum_error"], self.config["probability_tolerance"])
                self.assertIn(result["status"], {"SUCCESS_EXACT", "NON_ABSORBING", "NEAR_NONABSORBING"})

    def test_graph_closed_class_is_main_nonabsorption_rule(self):
        result = evaluate_policy((0, 0, 0, 1), self.cases[0], self.config)
        self.assertEqual(result["status"], "NON_ABSORBING")
        self.assertGreaterEqual(result["closed_class_count"], 1)

    def test_near_nonabsorbing_gets_high_precision_recheck(self):
        case = {**self.cases[0], "case": 97, "p1": 0.0, "p2": 0.0, "pf": 1 - 1e-12}
        result = evaluate_policy((0, 0, 0, 0), case, self.config)
        self.assertEqual(result["status"], "NEAR_NONABSORBING")
        self.assertIn("spectral_radius_high_precision", result)
        self.assertLess(result["spectral_radius_high_precision"], 1.0)

    def test_random_parameters_remain_well_formed(self):
        rng = random.Random(20240829)
        for index in range(12):
            case = {
                **self.cases[index % 6], "case": 200 + index,
                "p1": rng.random(), "p2": rng.random(), "pf": rng.random(),
            }
            for policy in POLICIES:
                result = evaluate_policy(policy, case, self.config)
                self.assertLessEqual(result["row_sum_error"], self.config["probability_tolerance"])
                self.assertNotEqual(result["status"], "INVALID_PROBABILITY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
