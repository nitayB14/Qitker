"""Verify controlled-S and controlled-T operations and their aliases.

The tests use superposition so the conditional relative phase is retained in
the statevector and compared exactly with the corresponding Qiskit gate.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.circuit.library import SGate, TGate

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_controlled_phase_gates():
    """Compare controlled S/T names with explicitly controlled Qiskit gates."""
    cases = (
        ("halfPhaseIf", SGate),
        ("cs", SGate),
        ("quarterPhaseIf", TGate),
        ("ct", TGate),
    )

    for qitker_method, gate_type in cases:
        circ = circuit()
        control = qubit(circ)
        target = qubit(circ)
        control.H()
        target.H()
        getattr(target, qitker_method)(control)

        expected = QuantumCircuit(2)
        expected.h(0)
        expected.h(1)
        expected.append(gate_type().control(1), [0, 1])

        assert_same_state(circ, expected)


if __name__ == "__main__":
    test_controlled_phase_gates()
    print("T18_controlled_phase_gates: PASS")
