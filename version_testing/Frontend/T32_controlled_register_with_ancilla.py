"""Verify the optional ancilla path for controlled register operations.

The direct and ancilla-assisted constructions must produce the same final
state. The ancilla starts in |0> and must be restored to |0> after uncompute.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit
from qitker import circuit, qubit, qRegister


def build_register_operation(use_ancilla, operation_name):
    """Build the same logical operation through the direct or ancilla path."""
    circ = circuit()
    controls = qRegister(circ, size=3)
    targets = qRegister(circ, size=2, initialize="10")
    marker = qubit(circ, measured=False)

    # Nontrivial superposition checks coherent compute/use/uncompute behavior.
    controls[0].H()
    controls[1].rotateY(math.pi / 3)
    controls[2].H()

    ancilla = marker if use_ancilla else None
    if operation_name == "flipIf":
        targets.flipIf(controls, where="1x0", ancilla=ancilla)
    else:
        targets.rotateZif(
            controls,
            math.pi / 4,
            where="1x0",
            ancilla=ancilla,
        )

    return circ, marker.getIndex()


def test_controlled_register_with_ancilla():
    """Compare direct and ancilla paths for X and parameterized rotation."""
    for operation_name in ("flipIf", "rotateZif"):
        direct, marker_index = build_register_operation(False, operation_name)
        assisted, _ = build_register_operation(True, operation_name)

        direct_state = Statevector.from_instruction(export_to_qiskit(direct))
        assisted_state = Statevector.from_instruction(export_to_qiskit(assisted))

        assert direct_state.equiv(assisted_state)

        # The marker is the highest-index qubit; no populated state may contain
        # a 1 at that position after the assisted circuit finishes.
        marker_mask = 1 << marker_index
        assert all(
            probability < 1e-12 or (basis_index & marker_mask) == 0
            for basis_index, probability in enumerate(assisted_state.probabilities())
        )


if __name__ == "__main__":
    test_controlled_register_with_ancilla()
    print("T32_controlled_register_with_ancilla: PASS")
