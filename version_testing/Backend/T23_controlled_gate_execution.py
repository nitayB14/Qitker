"""Section 23: controlled-gate execution through Qitker's anyonic backend."""

import sys
from pathlib import Path

import numpy as np
from qiskit.quantum_info import Statevector


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker import circuit, qubit


GATES = ("X", "Y", "Z", "S", "T")


def build_circuit(gate, initial_bits, hadamards, target, controls, measured=False):
    """Prepare a circuit and apply one public controlled-gate method."""
    circ = circuit()
    qubits = [
        qubit(circ, initialize=int(bit), measured=measured)
        for bit in initial_bits
    ]
    for index in hadamards:
        qubits[index].H()

    selected_controls = [qubits[index] for index in controls]
    control = selected_controls[0] if len(selected_controls) == 1 else selected_controls
    getattr(qubits[target], f"c{gate.lower()}")(control)
    return circ


def assert_logical_execution(circ, minimum_fidelity, maximum_leakage):
    """Compare physical output with an independent Qiskit logical state."""
    expected_qiskit = Statevector.from_instruction(
        circ.exportCircuit("qiskit")
    ).data

    circ.execute()
    system = circ._ex._fusionSystem
    space = system.hilbertSpace
    labels = space.logical_labels
    expected = np.asarray(
        [expected_qiskit[int(label[::-1], 2)] for label in labels]
    )
    actual = np.asarray(
        [space.state_vector[system.basis.logical_to_physical[label]] for label in labels]
    )

    # The overlap is insensitive to global phase but detects relative phases,
    # wrong control conditions, and amplitudes lost to leakage.
    fidelity = float(abs(np.vdot(expected, actual)) ** 2)
    leakage = system.hilbertSpace.leakage_probability()
    assert fidelity >= minimum_fidelity, (
        f"logical fidelity {fidelity:.8f} is below {minimum_fidelity:.8f}"
    )
    assert leakage <= maximum_leakage, (
        f"leakage {leakage:.8f} exceeds {maximum_leakage:.8f}"
    )
    assert np.isclose(np.linalg.norm(space.state_vector), 1.0, atol=1e-8)
    assert np.isclose(np.vdot(actual, actual).real + leakage, 1.0, atol=1e-8)
    assert np.isclose(space.state_fidelity(), fidelity, atol=1e-8)
    assert circ._ex._braidsNumber > 0


def test_one_control_gate_families():
    """Exercise CX, CY, CZ, CS, and CT on phase-sensitive inputs."""
    for gate in GATES:
        circ = build_circuit(
            gate,
            initial_bits="01",
            hadamards=(0,),
            target=1,
            controls=(0,),
        )
        assert_logical_execution(circ, minimum_fidelity=0.999, maximum_leakage=0.001)


def test_two_control_gate_families():
    """Exercise CCX, CCY, CCZ, CCS, and CCT on coherent controls."""
    for gate in GATES:
        circ = build_circuit(
            gate,
            initial_bits="001",
            hadamards=(0, 1),
            target=2,
            controls=(0, 1),
        )
        assert_logical_execution(circ, minimum_fidelity=0.995, maximum_leakage=0.005)


def test_control_target_routing():
    """Check reversed two-qubit roles and a target between two controls."""
    reversed_cx = build_circuit(
        "X", initial_bits="10", hadamards=(1,), target=0, controls=(1,)
    )
    assert_logical_execution(reversed_cx, minimum_fidelity=0.999, maximum_leakage=0.001)

    middle_ccz = build_circuit(
        "Z", initial_bits="010", hadamards=(0, 2), target=1, controls=(2, 0)
    )
    assert_logical_execution(middle_ccz, minimum_fidelity=0.995, maximum_leakage=0.005)


def test_measurement_report():
    """Check that a controlled gate also passes through public measure()."""
    circ = build_circuit(
        "X", initial_bits="10", hadamards=(), target=1,
        controls=(0,), measured=True,
    )
    report = circ.measure(shots=16)
    assert sum(report.getPercentageOpbject().values()) == 16
    assert report.getTotalBraids() > 0
    assert float(report.getFidelity().rstrip("%")) >= 99.9
    assert report.getLeakageProbability() <= 0.001


if __name__ == "__main__":
    test_one_control_gate_families()
    test_two_control_gate_families()
    test_control_target_routing()
    test_measurement_report()
    print("T23_controlled_gate_execution: PASS")
