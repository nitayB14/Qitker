"""Verify Y, Z, S, and T gates with multiple quantum controls.

Unitary comparison covers every possible input state, including all phases,
without requiring a separate loop over computational-basis preparations.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.circuit.library import YGate, ZGate, SGate, TGate

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_multi_controlled_phase_gates():
    """Compare each multi-controlled operation with a Qiskit controlled gate."""
    cases = (
        ("flipPhaseIf", YGate),
        ("phaseIf", ZGate),
        ("halfPhaseIf", SGate),
        ("quarterPhaseIf", TGate),
    )

    for controls_number in (2, 3):
        for qitker_method, gate_type in cases:
            circ = circuit()
            controls = [qubit(circ) for _ in range(controls_number)]
            target = qubit(circ)
            getattr(target, qitker_method)(controls)

            expected = QuantumCircuit(controls_number + 1)
            expected.append(
                gate_type().control(controls_number),
                list(range(controls_number + 1)),
            )

            assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_multi_controlled_phase_gates()
    print("T20_multi_controlled_phase_gates: PASS")
