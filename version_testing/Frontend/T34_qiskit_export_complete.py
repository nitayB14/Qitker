"""Verify that every currently supported operation exports in one circuit.

The test combines fixed gates, rotations, controlled gates, multi-controls,
controlled rotations, and a barrier, then compares the complete final state
with an independently assembled Qiskit circuit.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.circuit.library import SGate, TGate, RXGate, RYGate, RZGate

from frontend_test_helpers import assert_same_state, export_to_qiskit
from qitker import circuit, qubit


def build_qitker_circuit():
    """Build one circuit containing every operation family in the frontend."""
    circ = circuit()
    q = [qubit(circ) for _ in range(5)]

    q[0].H()
    q[1].X()
    q[2].Y()
    q[3].Z()
    q[4].S()
    q[0].T()
    q[1].rotateX(math.pi / 3)
    q[2].rotateY(-math.pi / 4)
    q[3].rotateZ(math.pi / 5)
    q[1].flipIf(q[0])
    q[2].flipPhaseIf(q[1])
    q[3].phaseIf(q[2])
    q[4].halfPhaseIf(q[3])
    q[0].quarterPhaseIf(q[4])
    q[4].flipIf([q[0], q[1]])
    q[3].rotateXif(q[0], math.pi / 7)
    q[2].rotateYif([q[0], q[1]], -math.pi / 6)
    q[1].rotateZif([q[3], q[4]], math.pi / 8)
    circ.barrier()

    return circ


def build_expected_circuit():
    """Build the direct Qiskit equivalent in exactly the same operation order."""
    expected = QuantumCircuit(5)
    expected.h(0)
    expected.x(1)
    expected.y(2)
    expected.z(3)
    expected.s(4)
    expected.t(0)
    expected.rx(math.pi / 3, 1)
    expected.ry(-math.pi / 4, 2)
    expected.rz(math.pi / 5, 3)
    expected.cx(0, 1)
    expected.cy(1, 2)
    expected.cz(2, 3)
    expected.append(SGate().control(1), [3, 4])
    expected.append(TGate().control(1), [4, 0])
    expected.mcx([0, 1], 4)
    expected.append(RXGate(math.pi / 7).control(1), [0, 3])
    expected.append(RYGate(-math.pi / 6).control(2), [0, 1, 2])
    expected.append(RZGate(math.pi / 8).control(2), [3, 4, 1])
    expected.barrier()
    return expected


def test_qiskit_export_complete():
    """Compare the complete export and verify its structural metadata."""
    circ = build_qitker_circuit()
    exported = export_to_qiskit(circ)

    assert exported.num_qubits == 5
    assert exported.num_clbits == 5
    assert exported.count_ops().get("barrier", 0) == 1
    assert_same_state(circ, build_expected_circuit())


if __name__ == "__main__":
    test_qiskit_export_complete()
    print("T34_qiskit_export_complete: PASS")
