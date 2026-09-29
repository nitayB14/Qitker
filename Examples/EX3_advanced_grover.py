#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 29/09/2026
#Rule: Independent researcher
#
#

"""Demonstrate Grover search with register patterns and equality, simulated in Qiskit Aer."""


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qRegister

from qiskit import transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


ITERATIONS = 5
SHOTS = 2048


def oracle(message_a, message_b, flags):
    """Phase-mark message pairs satisfying all three constraints.

    A must match "1xx0", B must match "x0x1", and A must equal B after
    a cyclic left shift by one and a swap of its first two qubits.
    The flags must start in |000>; restore them and B after marking.
    """

    flag_a, flag_b, flag_equal = flags[:]

    # Check the original messages.
    flag_a.flipIf(message_a, where="1xx0")
    flag_b.flipIf(message_b, where="x0x1")

    # Transform B into the form that must equal A.
    message_b.shiftLeft(1)
    message_b[0].swap(message_b[1])

    # Compare the complete four-bit messages.
    flag_equal.flipIf(message_a == message_b)

    # Flip the phase only when all three flags are 1.
    flag_equal.phaseIf([flag_a, flag_b])

    # Undo the comparison.
    flag_equal.flipIf(message_a == message_b)

    # Restore B before checking its original pattern again.
    message_b[0].swap(message_b[1])
    message_b.shiftRight(1)

    # Return the remaining flags to 0.
    flag_b.flipIf(message_b, where="x0x1")
    flag_a.flipIf(message_a, where="1xx0")


def diffuser(search):
    """Apply Grover's diffusion operator to the combined search qubits."""
    for current_qubit in search:
        current_qubit.mix()
        current_qubit.flip()

    search[-1].phaseIf(search[:-1])

    for current_qubit in search:
        current_qubit.flip()
        current_qubit.mix()


def build_circuit():
    """Return a Qitker circuit with two four-qubit messages, three flags, and ITERATIONS Grover iterations."""

    network = circuit()

    message_a = qRegister(network, size=4)
    message_b = qRegister(network, size=4)
    flags = qRegister(network, size=3, measured=False)

    # Prepare all 256 pairs of messages.
    message_a.mix()
    message_b.mix()

    search = message_a[:] + message_b[:]

    for _ in range(ITERATIONS):
        network.barrier()
        oracle(message_a, message_b, flags)
        network.barrier()
        diffuser(search)

    return network


def main():
    """Export to Qiskit Aer, sample the circuit, and display the most frequent message pair and histogram."""

    network = build_circuit()

    qc = network.exportCircuit("qiskit")
    qc.draw('mpl')

    qc.measure(*network.getMeasuredLists())

    simulator = Aer.get_backend("qasm_simulator")
    compiled = transpile(qc, simulator)
    raw_counts = simulator.run(
        compiled,
        shots=SHOTS,
    ).result().get_counts()

    # Display bits in Qitker's register order: AAAABBBB.
    counts = {
        bitstring[::-1]: count
        for bitstring, count in raw_counts.items()
    }

    best_pair = max(counts, key=counts.get)
    print(f"A = {best_pair[:4]}")
    print(f"B = {best_pair[4:]}")
    print(f"Measured {best_pair} in {counts[best_pair]}/{SHOTS} shots")

    plot_histogram(counts)
    plt.show()

if __name__ == "__main__":
    main()
