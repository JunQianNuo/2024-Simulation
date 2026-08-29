"""Q4 使用的 Q2/Q3 全策略向量化利润评价器。"""

from __future__ import annotations

import numpy as np

from q3 import model as q3_model


Q2_POLICIES = np.asarray(
    [(x1, x2, y, z) for x1 in (0, 1) for x2 in (0, 1) for y in (0, 1) for z in (0, 1)],
    dtype=np.int8,
)
Q3_POLICY_IDS = np.arange(65536, dtype=np.int64)
Q3_BITS = ((Q3_POLICY_IDS[:, None] >> np.arange(16)) & 1).astype(np.int8)


def q2_profit_batch(case: dict, parameters: np.ndarray, policies: np.ndarray = Q2_POLICIES):
    """返回 shape=(参数样本数, 策略数) 的利润和可吸收标记。"""
    p = np.asarray(parameters, dtype=float)
    d = np.asarray(policies, dtype=np.int8)
    if p.ndim != 2 or p.shape[1] != 3 or d.ndim != 2 or d.shape[1] != 4:
        raise ValueError("Q2 batch shape 必须为 (B,3) 与 (D,4)")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("Q2 缺陷率必须位于 [0,1]")

    p1, p2, pf = (p[:, i, None] for i in range(3))
    x1, x2, y, z = (d[None, :, i].astype(bool) for i in range(4))
    with np.errstate(divide="ignore", invalid="ignore"):
        c1 = np.where(x1, (case["buy1"] + case["test1"]) / (1 - p1), case["buy1"])
        c2 = np.where(x2, (case["buy2"] + case["test2"]) / (1 - p2), case["buy2"])
        g1 = np.where(x1, 1.0, 1 - p1)
        g2 = np.where(x2, 1.0, 1 - p2)
        guaranteed = (x1 | (p1 == 0)) & (x2 | (p2 == 0))
        q = (1 - pf) * g1 * g2
        rebuild = np.where(
            y,
            (c1 + c2 + case["assembly"] + case["test_product"]) / q,
            (c1 + c2 + case["assembly"] + (1 - q) * case["replacement"]) / q,
        )
        retained = c1 + c2 + (
            case["assembly"]
            + y * case["test_product"]
            + pf * (case["disassembly"] + (1 - y) * case["replacement"]
                    + x1 * case["test1"] + x2 * case["test2"])
        ) / (1 - pf)
    feasible = np.where(z, guaranteed & (pf < 1), np.isfinite(rebuild))
    cost = np.where(z, retained, rebuild)
    profit = np.where(feasible, case["price"] - cost, -np.inf)
    return profit, feasible


def q3_profit_batch(parameters: np.ndarray, policy_ids: np.ndarray = Q3_POLICY_IDS):
    """按题给三级装配树批量评价全部或指定 Q3 固定策略。"""
    p = np.asarray(parameters, dtype=float)
    ids = np.asarray(policy_ids, dtype=np.int64)
    if p.ndim != 2 or p.shape[1] != 12 or ids.ndim != 1:
        raise ValueError("Q3 batch shape 必须为 (B,12) 与 (D,)")
    if np.any((p < 0) | (p > 1)) or np.any((ids < 0) | (ids >= 65536)):
        raise ValueError("Q3 参数或策略编号越界")

    bits = Q3_BITS[ids]
    leaf_p = p[:, :8]
    semi_p = p[:, 8:11]
    final_p = p[:, 11, None]
    batch = p.shape[0]
    semi_costs, semi_goods, semi_guaranteed, feasible_parts = [], [], [], []
    groups = ((0, 1, 2), (3, 4, 5), (6, 7))

    with np.errstate(divide="ignore", invalid="ignore"):
        for semi_index, children in enumerate(groups):
            cost = np.zeros((batch, len(ids)))
            good = np.ones_like(cost)
            guaranteed = np.ones((batch, len(ids)), dtype=bool)
            retest = np.zeros_like(cost)
            for child in children:
                defect = leaf_p[:, child, None]
                inspect = bits[None, :, child].astype(bool)
                _, buy, test = q3_model.LEAVES[child + 1]
                cost += np.where(inspect, (buy + test) / (1 - defect), buy)
                good *= np.where(inspect, 1.0, 1 - defect)
                guaranteed &= inspect | (defect == 0)
                retest += inspect * test

            defect = semi_p[:, semi_index, None]
            tested = bits[None, :, 8 + semi_index].astype(bool)
            dismantle = bits[None, :, 12 + semi_index].astype(bool)
            node_name = f"s{semi_index + 1}"
            _, _, assembly, inspection, disassembly = q3_model.NODES[node_name]
            q = (1 - defect) * good
            first = cost + assembly
            untested_cost = first
            tested_scrap_cost = (first + inspection) / q
            retained_cost = cost + (assembly + inspection + defect * (disassembly + retest)) / (1 - defect)
            local_feasible = np.where(
                tested & dismantle,
                guaranteed & (defect < 1),
                np.where(tested, q > 0, np.isfinite(first)),
            )
            local_cost = np.where(tested & dismantle, retained_cost,
                                  np.where(tested, tested_scrap_cost, untested_cost))
            local_good = np.where(tested, 1.0, q)
            local_guaranteed = np.where(tested, True, guaranteed & (defect == 0))
            semi_costs.append(local_cost)
            semi_goods.append(local_good)
            semi_guaranteed.append(local_guaranteed)
            feasible_parts.append(local_feasible)

        children_cost = semi_costs[0] + semi_costs[1] + semi_costs[2]
        children_good = semi_goods[0] * semi_goods[1] * semi_goods[2]
        children_guaranteed = semi_guaranteed[0] & semi_guaranteed[1] & semi_guaranteed[2]
        feasible = feasible_parts[0] & feasible_parts[1] & feasible_parts[2]
        yf = bits[None, :, 11].astype(bool)
        zf = bits[None, :, 15].astype(bool)
        _, _, assembly, inspection, disassembly = q3_model.NODES["root"]
        q = (1 - final_p) * children_good
        rebuild = np.where(
            yf,
            (children_cost + assembly + inspection) / q,
            (children_cost + assembly + (1 - q) * q3_model.REPLACEMENT) / q,
        )
        semi_retests = sum(bits[None, :, 8 + i] * q3_model.NODES[f"s{i + 1}"][3] for i in range(3))
        retained = children_cost + (
            assembly + yf * inspection
            + final_p * (disassembly + (1 - yf) * q3_model.REPLACEMENT + semi_retests)
        ) / (1 - final_p)
    feasible &= np.where(zf, children_guaranteed & (final_p < 1), np.isfinite(rebuild))
    cost = np.where(zf, retained, rebuild)
    profit = np.where(feasible, q3_model.PRICE - cost, -np.inf)
    return profit, feasible

