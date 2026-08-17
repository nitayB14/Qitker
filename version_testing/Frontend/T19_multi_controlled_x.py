"""Verify multi-controlled X with two, three, and four controls.

Every computational-basis control pattern is tested. The target must flip only
when all controls are one, matching Qiskit's MCX truth table.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_multi_controlled_x():
    """Compare Qitker and Qiskit for all basis inputs at each control width."""
    for controls_number in (2, 3, 4):
        for control_value in range(2 ** controls_number):
            bits = format(control_value, f"0{controls_number}b")

            circ = circuit()
            controls = [qubit(circ, initialize=int(bit)) for bit in bits]
            target = qubit(circ)
            target.flipIf(controls)

            expected = QuantumCircuit(controls_number + 1)
            for index, bit in enumerate(bits):
                if bit == "1":
                    expected.x(index)
            expected.mcx(list(range(controls_number)), controls_number)

            assert_same_state(circ, expected)


if __name__ == "__main__":
    test_multi_controlled_x()
    print("T19_multi_controlled_x: PASS")
