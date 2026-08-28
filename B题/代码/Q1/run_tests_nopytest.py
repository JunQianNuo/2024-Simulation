"""在没有 pytest 的环境里跑 tests/test_q1.py。

比赛机上装了 pytest 就直接用 `python -m pytest tests/ -v`，
这个脚本只是没网/没装包时的等价回退：注入一个最小 pytest 垫片，
再逐个执行 test_* 函数（含 parametrize 展开）。

用法：python tests/run_tests_nopytest.py
"""

from __future__ import annotations

import itertools
import sys
import traceback
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# --------------------------------------------------------------------------
# 最小 pytest 垫片
# --------------------------------------------------------------------------
class _Approx:
    def __init__(self, expected, abs_=None, rel=None):
        self.expected = expected
        self.abs = abs_
        self.rel = rel if rel is not None else 1e-6

    def __eq__(self, other):
        tol = self.abs if self.abs is not None else self.rel * max(1.0, abs(self.expected))
        return abs(other - self.expected) <= tol

    def __repr__(self):
        return f"approx({self.expected!r}, abs={self.abs}, rel={self.rel})"


def _approx(expected, abs=None, rel=None):  # noqa: A002
    return _Approx(expected, abs_=abs, rel=rel)


class _Mark:
    @staticmethod
    def parametrize(argnames, argvalues):
        names = [s.strip() for s in argnames.split(",")]

        def deco(fn):
            fn._params = (names, list(argvalues))
            return fn

        return deco


_pytest = types.ModuleType("pytest")
_pytest.approx = _approx
_pytest.mark = _Mark()
_pytest.fail = lambda msg="": (_ for _ in ()).throw(AssertionError(msg))
sys.modules["pytest"] = _pytest


# --------------------------------------------------------------------------
# 执行
# --------------------------------------------------------------------------
def main() -> int:
    import tests.test_q1 as mod  # noqa: E402

    passed = failed = 0
    failures: list[tuple[str, str]] = []

    for name in sorted(vars(mod)):
        if not name.startswith("test_"):
            continue
        fn = getattr(mod, name)
        if not callable(fn):
            continue

        cases: list[tuple[str, tuple]] = []
        params = getattr(fn, "_params", None)
        if params:
            names, values = params
            for v in values:
                v = v if isinstance(v, (tuple, list)) else (v,)
                label = ",".join(f"{n}={x}" for n, x in zip(names, v))
                cases.append((f"{name}[{label}]", tuple(v)))
        else:
            cases.append((name, ()))

        for label, args in cases:
            try:
                fn(*args)
                passed += 1
                print(f"  PASS  {label}")
            except Exception:
                failed += 1
                failures.append((label, traceback.format_exc()))
                print(f"  FAIL  {label}")

    print("-" * 78)
    print(f"{passed} passed, {failed} failed")
    for label, tb in failures:
        print("=" * 78)
        print(label)
        print(tb)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
