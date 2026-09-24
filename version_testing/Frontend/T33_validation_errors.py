"""Verify that invalid controlled-gate inputs fail clearly and immediately.

These cases protect circuit ownership, unique controls, valid condition widths,
comparison structure, and safe ancilla usage at the frontend boundary.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker import circuit, qubit, qRegister


def assert_raises(error_type, message_fragment, operation):
    """Run an operation and verify both its exception type and useful message."""
    try:
        operation()
    except error_type as error:
        assert message_fragment in str(error)
    else:
        raise AssertionError(f"Expected {error_type.__name__}: {message_fragment}")


def test_control_validation_errors():
    """Reject invalid controls, circuits, patterns, and integer conditions."""
    circ = circuit()
    other_circuit = circuit()
    control = qubit(circ)
    second_control = qubit(circ)
    target = qubit(circ)
    foreign = qubit(other_circuit)

    cases = (
        (ValueError, "target qubit cannot also be a control", lambda: target.flipIf(target)),
        (ValueError, "duplicate control", lambda: target.flipIf([control, control])),
        (ValueError, "same circuit", lambda: target.flipIf(foreign)),
        (ValueError, "at least one control", lambda: target.flipIf([])),
        (ValueError, "length must match", lambda: target.flipIf([control, second_control], where="1")),
        (ValueError, "only '0', '1', or 'x'", lambda: target.flipIf(control, where="a")),
        (ValueError, "between 0 and 3", lambda: target.flipIf([control, second_control], where=4)),
        (ValueError, "between 0 and 3", lambda: target.flipIf([control, second_control], where=-1)),
        (TypeError, "must not be a boolean", lambda: target.flipIf(control, where=True)),
    )

    for error_type, message, operation in cases:
        assert_raises(error_type, message, operation)


def test_comparison_validation_errors():
    """Reject malformed, overlapping, and cross-circuit comparisons."""
    circ = circuit()
    other_circuit = circuit()
    controls = qRegister(circ, size=2)
    references = qRegister(circ, size=2)
    target = qubit(circ)
    foreign = qubit(other_circuit)

    cases = (
        (TypeError, "qubit with qubit", lambda: target.flipIf(controls[0], where=references[::])),
        (ValueError, "same length", lambda: target.flipIf(controls[::], where=[references[0]])),
        (ValueError, "same circuit", lambda: target.flipIf(controls[0], where=foreign)),
        (ValueError, "cannot also be a reference", lambda: target.flipIf(controls[0], where=target)),
        (ValueError, "partially overlap", lambda: target.flipIf(controls[::], where=[controls[0], references[1]])),
    )

    for error_type, message, operation in cases:
        assert_raises(error_type, message, operation)


def test_ancilla_validation_errors():
    """Reject an ancilla that is a target or has an unsupported type."""
    circ = circuit()
    control = qubit(circ)
    targets = qRegister(circ, size=2)

    assert_raises(
        ValueError,
        "ancilla cannot also be a target",
        lambda: targets.flipIf(control, ancilla=targets[0]),
    )
    assert_raises(
        TypeError,
        "ancilla must be a qubit or None",
        lambda: targets.flipIf(control, ancilla="workspace"),
    )

def test_export_target_validation_errors():
    """Reject unsupported export targets with clear exceptions."""
    circ = circuit()
    qubit(circ)

    for name in ("cirq", "unknown"):
        assert_raises(
            ValueError,
            "Unsupported export target",
            lambda name=name: circ.exportCircuit(name),
        )

    assert_raises(
        TypeError,
        "export target must be a string",
        lambda: circ.exportCircuit(None),
    )

if __name__ == "__main__":
    test_control_validation_errors()
    test_comparison_validation_errors()
    test_ancilla_validation_errors()
    test_export_target_validation_errors()
    print("T33_validation_errors: PASS")
