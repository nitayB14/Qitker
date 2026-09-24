"""Section 1: Fibonacci fusion-rule tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge, fusion_outcomes


def assert_raises(expected_exception, function):
    """Verify that calling function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return
    raise AssertionError(f"Expected {expected_exception.__name__} to be raised.")


def test_fibonacci_fusion_rules():
    """Check all four fusion rules of the Fibonacci anyon model."""
    # Vacuum leaves the other charge unchanged.
    assert fusion_outcomes(Charge.VACUUM, Charge.VACUUM) == (Charge.VACUUM,)
    assert fusion_outcomes(Charge.VACUUM, Charge.TAU) == (Charge.TAU,)
    assert fusion_outcomes(Charge.TAU, Charge.VACUUM) == (Charge.TAU,)
    assert fusion_outcomes(Charge.TAU, Charge.TAU) == (
        Charge.VACUUM,
        Charge.TAU,
    )


def test_fusion_rule_validation():
    """Reject fusion inputs that are not Charge enum values."""
    assert_raises(TypeError, lambda: fusion_outcomes("tau", Charge.TAU))
    assert_raises(TypeError, lambda: fusion_outcomes(Charge.TAU, "tau"))


def main():
    """Run all section 1 checks when this file is executed directly."""
    test_fibonacci_fusion_rules()
    test_fusion_rule_validation()
    print("Section 1 fusion-rule tests passed.")


if __name__ == "__main__":
    main()
