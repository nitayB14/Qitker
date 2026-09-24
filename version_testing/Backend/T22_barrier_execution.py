"""Section 22: validate barrier."""

import math
import sys
from pathlib import Path

import numpy as np
from qiskit.quantum_info import Operator, Statevector


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker import circuit, qRegister, qubit


def build_circuit(with_barrier):
    circ = circuit()
    q = qRegister(circ, size=2)
    q.H()
    if with_barrier:
        circ.barrier()
    q.X()
    return circ

def test_barrier_does_not_change_execution():
    plain = build_circuit(False)
    marked = build_circuit(True)

    plain.execute()
    marked.execute()

    plain_system = plain._ex._fusionSystem
    marked_system = marked._ex._fusionSystem

    np.testing.assert_allclose(
        marked_system.hilbertSpace.state_vector,
        plain_system.hilbertSpace.state_vector,
    )
    assert marked._ex._braidsNumber == plain._ex._braidsNumber
    assert marked._ex.getFidelity() == plain._ex.getFidelity()
    assert (
        marked._ex.getLeakageProbability()
        == plain._ex.getLeakageProbability()
    )


def test_barrier_only():
    circ = circuit()
    qRegister(circ, size=1)
    circ.barrier()

    circ.execute()
    assert circ._ex._braidsNumber == 0
    assert circ._ex._fusionSystem.hilbertSpace.state_fidelity() == 1.0
    assert circ._ex.getLeakageProbability() == 0.0

    result = circ.measure(shots=1)
    assert result.getTotalGates() == 0
    assert result.getTotalBraids() == 0
    assert result.getPercentageOpbject() == {"0": 1}



def test_barrier_is_not_counted_as_a_gate():
    plain = build_circuit(False)
    marked = build_circuit(True)

    plain_result = plain.measure(shots=1)
    marked_result = marked.measure(shots=1)

    assert plain_result.getTotalGates() == 4
    assert marked_result.getTotalGates() == 4
    assert marked_result.getTotalBraids() == plain_result.getTotalBraids()


if __name__ == "__main__":
    test_barrier_does_not_change_execution()
    test_barrier_only()
    test_barrier_is_not_counted_as_a_gate()
    print("T22_barrier_execution: PASS")