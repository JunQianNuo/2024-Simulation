"""Q3 状态核、全枚举与参数化接口验收。"""

from __future__ import annotations

import itertools
import unittest

import pandas as pd

from component_state import inspect_component as shared_inspect
from q2.model import inspect_component as q2_inspect
from q3.model import (
    BATCH_CACHE, CONFIG, LEAVES, evaluate, input_batch, make_q3_evaluator,
    q3_nominal_parameters,
)
from q3.run_q3 import audit, select_best


class Q3AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = pd.DataFrame(evaluate(i) for i in range(65536))
        cls.ok, cls.balances = audit(cls.frame)

    def test_shared_q2_q3_information_state_primitive(self):
        self.assertIs(shared_inspect, q2_inspect)

    def test_full_enumeration_and_optimum(self):
        self.assertEqual(self.frame.strategy_id.nunique(), 65536)
        self.assertEqual(self.frame.status.value_counts().to_dict(), {"NON_ABSORBING": 48476, "SUCCESS_EXACT": 17060})
        best = select_best(self.frame)
        self.assertEqual(best.strategy_id.tolist(), [63487])
        self.assertAlmostEqual(best.iloc[0].expected_profit, 57.6666666667, places=8)
        self.assertAlmostEqual(best.iloc[0].expected_total_cost, 142.3333333333, places=8)
        self.assertAlmostEqual(best.iloc[0].expected_part_inspections, 9.7777777778, places=8)
        second = self.ok.nlargest(2, "expected_profit")
        self.assertAlmostEqual(second.iloc[0].expected_profit - second.iloc[1].expected_profit, 1.8395061728, places=8)

    def test_independent_closed_form_batch_crosscheck(self):
        for ids in ((1, 2), (1, 2, 3)):
            for inspections in itertools.product((0, 1), repeat=len(ids)):
                batch = input_batch(ids, inspections, cache={})
                expected_good = 1.0
                for leaf_id, inspected in zip(ids, inspections):
                    defect, buy, test = LEAVES[leaf_id]
                    purchases = 1 / (1 - defect) if inspected else 1.0
                    tests = purchases if inspected else 0.0
                    scraps = defect / (1 - defect) if inspected else 0.0
                    expected_good *= 1.0 if inspected else 1 - defect
                    from q3.model import ci, ei
                    self.assertAlmostEqual(batch.reward[ei(f"expected_part_purchases_{leaf_id}")], purchases, places=10)
                    self.assertAlmostEqual(batch.reward[ei(f"expected_part_inspections_{leaf_id}")], tests, places=10)
                    self.assertAlmostEqual(batch.reward[ei(f"expected_part_scraps_{leaf_id}")], scraps, places=10)
                self.assertAlmostEqual(batch.good, expected_good, places=10)

    def test_known_good_retention_removes_order_bias(self):
        row = self.frame.loc[self.frame.strategy_id.eq(63487)].iloc[0]
        counts = [row[f"expected_part_inspections_{i}"] for i in range(1, 9)]
        for value in counts:
            self.assertAlmostEqual(value, 1.2222222222, places=9)

    def test_no_inspection_closed_form(self):
        row = self.frame.loc[self.frame.strategy_id.eq(0)].iloc[0]
        q = 0.9 ** 12
        expected_cost = (96 + (1 - q) * 40) / q
        self.assertAlmostEqual(row.expected_total_cost, expected_cost, places=9)
        self.assertAlmostEqual(row.one_pass_success_no_inspection, q, places=12)

    def test_material_balance_all_feasible(self):
        self.assertLessEqual(self.balances.abs().to_numpy().max(), CONFIG["probability_tolerance"])

    def test_zero_and_one_boundary_probabilities(self):
        zero = {name: 0.0 for name in q3_nominal_parameters()}
        evaluator = make_q3_evaluator(zero)
        for strategy_id in (0, 1, 255, 4095, 63487, 65535):
            self.assertIn(evaluator(strategy_id)["status"], {"SUCCESS_EXACT", "NON_ABSORBING"})
        endpoint = {**zero, "part_1": 1.0}
        self.assertEqual(make_q3_evaluator(endpoint)(1)["status"], "NON_ABSORBING")

    def test_near_nonabsorption_and_dynamic_baseline(self):
        parameters = q3_nominal_parameters()
        parameters["part_1"] = 1 - 1e-12
        row = make_q3_evaluator(parameters)(1)
        self.assertEqual(row["status"], "NEAR_NONABSORBING")
        self.assertIn("spectral_radius_high_precision", row)
        expected = (1 - parameters["part_1"])
        for name, value in parameters.items():
            if name != "part_1":
                expected *= 1 - value
        self.assertAlmostEqual(row["one_pass_success_no_inspection"], expected, delta=1e-25)

        parameters = q3_nominal_parameters()
        parameters["final"] = 1 - 1e-12
        row = make_q3_evaluator(parameters)(63487)
        self.assertEqual(row["status"], "NEAR_NONABSORBING")

    def test_parameterized_interface_random_slice(self):
        parameters = q3_nominal_parameters()
        for i, name in enumerate(parameters):
            parameters[name] = (i + 1) / 20
        evaluator = make_q3_evaluator(parameters)
        for strategy_id in (0, 7, 255, 4095, 32768, 47103, 63487, 65535):
            row = evaluator(strategy_id)
            self.assertNotEqual(row["status"], "INVALID_PROBABILITY")
            if row["status"] in {"SUCCESS_EXACT", "NEAR_NONABSORBING"}:
                self.assertLessEqual(row["max_local_equation_residual"], CONFIG["probability_tolerance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
