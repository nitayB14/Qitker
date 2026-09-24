"""Section 21: validate symbolic equality conditions in the frontend DSL."""

import math
import sys
from pathlib import Path

import numpy as np
from qiskit.quantum_info import Operator, Statevector


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker import circuit, qRegister, qubit


def run_test(name, test_function) -> None:
    """Run one test and report success."""

    test_function()
    print(f"{name}: PASS")


def assert_same_unitary(first, second) -> None:
    """Assert that two Qitker circuits describe the same unitary."""

    first_unitary = Operator(first.exportCircuit("qiskit"))
    second_unitary = Operator(second.exportCircuit("qiskit"))

    assert first_unitary.equiv(second_unitary)


def assert_deterministic_state(qitker_circuit, expected_bits) -> None:
    """Assert one deterministic output, written in Qitker qubit order."""

    state = Statevector.from_instruction(
        qitker_circuit.exportCircuit("qiskit")
    )

    probabilities = state.probabilities_dict()
    populated_states = {
        qiskit_bits[::-1]: probability
        for qiskit_bits, probability in probabilities.items()
        if not np.isclose(probability, 0.0)
    }

    assert set(populated_states) == {expected_bits}
    assert np.isclose(populated_states[expected_bits], 1.0)


def assert_raises(error_type, message_fragment, operation) -> None:
    """Assert an operation raises the requested error and message."""

    try:
        operation()
    except error_type as error:
        assert message_fragment in str(error)
        return

    raise AssertionError(
        f"Expected {error_type.__name__} containing "
        f"{message_fragment!r}."
    )


def build_pattern_circuit(initial_value, pattern):
    """Build a deterministic register-pattern condition circuit."""

    party = circuit()
    controls = qRegister(
        party,
        size=2,
        initialize=initial_value,
    )
    marker = qubit(party)
    marker.flipIf(controls == pattern)

    return party


def build_register_equality_circuit(left_value, right_value):
    """Build a deterministic register-equality condition circuit."""

    party = circuit()
    left = qRegister(party, size=2, initialize=left_value)
    right = qRegister(party, size=2, initialize=right_value)
    marker = qubit(party)
    marker.flipIf(left == right)

    return party


def test_string_pattern_conditions() -> None:
    """Check matching and non-matching string patterns with don't-care bits."""

    cases = (
        ("10", "1x", "101"),
        ("11", "1x", "111"),
        ("01", "1x", "010"),
        ("00", "1x", "000"),
    )

    for initial_value, pattern, expected_bits in cases:
        assert_deterministic_state(
            build_pattern_circuit(initial_value, pattern),
            expected_bits,
        )


def test_integer_pattern_conditions() -> None:
    """Check matching and non-matching integer conditions."""

    assert_deterministic_state(
        build_pattern_circuit(2, 2),
        "101",
    )

    assert_deterministic_state(
        build_pattern_circuit(1, 2),
        "010",
    )


def test_register_equality_conditions() -> None:
    """Check equal and unequal computational-basis registers."""

    assert_deterministic_state(
        build_register_equality_circuit("10", "10"),
        "10101",
    )

    assert_deterministic_state(
        build_register_equality_circuit("10", "01"),
        "10010",
    )


def test_gate_syntax_equivalence() -> None:
    """Check old and new syntax for every controlled named gate."""

    gate_names = (
        "flipIf",
        "flipPhaseIf",
        "phaseIf",
        "halfPhaseIf",
        "quarterPhaseIf",
    )

    for gate_name in gate_names:
        old_party = circuit()
        old_controls = qRegister(old_party, size=2)
        old_marker = qubit(old_party)
        getattr(old_marker, gate_name)(old_controls, where="1x")

        new_party = circuit()
        new_controls = qRegister(new_party, size=2)
        new_marker = qubit(new_party)
        getattr(new_marker, gate_name)(new_controls == "1x")

        assert_same_unitary(old_party, new_party)


def test_rotation_syntax_equivalence() -> None:
    """Check that equality conditions preserve every rotation angle."""

    angle = math.pi / 6
    rotation_names = (
        "rotateXif",
        "rotateYif",
        "rotateZif",
    )

    for rotation_name in rotation_names:
        old_party = circuit()
        old_controls = qRegister(old_party, size=2)
        old_marker = qubit(old_party)
        getattr(old_marker, rotation_name)(
            old_controls,
            angle=angle,
            where="1x",
        )

        new_party = circuit()
        new_controls = qRegister(new_party, size=2)
        new_marker = qubit(new_party)
        getattr(new_marker, rotation_name)(
            new_controls == "1x",
            angle=angle,
        )

        assert_same_unitary(old_party, new_party)


def test_qubit_equality_syntax_equivalence() -> None:
    """Check symbolic equality between individual qubits."""

    old_party = circuit()
    old_left = qubit(old_party)
    old_right = qubit(old_party)
    old_marker = qubit(old_party)
    old_marker.flipIf(old_left, where=old_right)

    new_party = circuit()
    new_left = qubit(new_party)
    new_right = qubit(new_party)
    new_marker = qubit(new_party)
    new_marker.flipIf(new_left == new_right)

    assert_same_unitary(old_party, new_party)


def test_register_equality_syntax_equivalence() -> None:
    """Check old and new syntax for coherent register equality."""

    old_party = circuit()
    old_left = qRegister(old_party, size=2)
    old_right = qRegister(old_party, size=2)
    old_marker = qubit(old_party)
    old_marker.flipIf(old_left, where=old_right)

    new_party = circuit()
    new_left = qRegister(new_party, size=2)
    new_right = qRegister(new_party, size=2)
    new_marker = qubit(new_party)
    new_marker.flipIf(new_left == new_right)

    assert_same_unitary(old_party, new_party)


def test_ancilla_syntax_equivalence() -> None:
    """Check that symbolic conditions do not consume the ancilla argument."""

    angle = math.pi / 6

    old_party = circuit()
    old_controls = qRegister(old_party, size=2)
    old_targets = qRegister(old_party, size=2)
    old_ancilla = qubit(old_party, measured=False)
    old_targets.rotateZif(
        old_controls,
        angle=angle,
        where="1x",
        ancilla=old_ancilla,
    )

    new_party = circuit()
    new_controls = qRegister(new_party, size=2)
    new_targets = qRegister(new_party, size=2)
    new_ancilla = qubit(new_party, measured=False)
    new_targets.rotateZif(
        new_controls == "1x",
        angle=angle,
        ancilla=new_ancilla,
    )

    assert_same_unitary(old_party, new_party)


def test_validation_errors() -> None:
    """Check malformed symbolic conditions still use existing validation."""

    party = circuit()
    controls = qRegister(party, size=2)
    marker = qubit(party)

    assert_raises(
        ValueError,
        "length must match",
        lambda: marker.flipIf(controls == "1"),
    )

    assert_raises(
        TypeError,
        "where cannot be used together",
        lambda: marker.flipIf(
            controls == "1x",
            where="11",
        ),
    )

    second_party = circuit()
    short_register = qRegister(second_party, size=2)
    long_register = qRegister(second_party, size=3)
    second_marker = qubit(second_party)

    assert_raises(
        ValueError,
        "same length",
        lambda: second_marker.flipIf(
            short_register == long_register
        ),
    )

    foreign_party = circuit()
    foreign_controls = qRegister(foreign_party, size=2)

    assert_raises(
        ValueError,
        "same circuit",
        lambda: marker.flipIf(foreign_controls == "1x"),
    )


def test_hashes_and_indexes() -> None:
    """Check equality overloading preserves identity hashes and indexes."""

    party = circuit()
    controls = qRegister(party, size=2)
    marker = qubit(party)

    assert isinstance(hash(controls), int)
    assert isinstance(hash(controls[0]), int)
    assert controls.getIndex() == [0, 1]
    assert marker.getIndex() == 2
    assert party.getQubitsArray() == [
        controls[0],
        controls[1],
        marker,
    ]


def main() -> None:
    """Run all symbolic equality syntax tests."""

    run_test(
        "String pattern conditions",
        test_string_pattern_conditions,
    )
    run_test(
        "Integer pattern conditions",
        test_integer_pattern_conditions,
    )
    run_test(
        "Register equality conditions",
        test_register_equality_conditions,
    )
    run_test(
        "Controlled gate syntax equivalence",
        test_gate_syntax_equivalence,
    )
    run_test(
        "Controlled rotation syntax equivalence",
        test_rotation_syntax_equivalence,
    )
    run_test(
        "Qubit equality syntax equivalence",
        test_qubit_equality_syntax_equivalence,
    )
    run_test(
        "Register equality syntax equivalence",
        test_register_equality_syntax_equivalence,
    )
    run_test(
        "Ancilla syntax equivalence",
        test_ancilla_syntax_equivalence,
    )
    run_test(
        "Validation errors",
        test_validation_errors,
    )
    run_test(
        "Identity hashes and indexes",
        test_hashes_and_indexes,
    )

    print("All section 21 symbolic equality tests passed.")


if __name__ == "__main__":
    main()
