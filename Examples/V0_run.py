
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path

from numpy import diff, where
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister


def oracle(marker, q1, q2):
    marker.halfPhaseIf([q1, q2])

def diffuser(search):
    """Grover diffuser over the four search qubits."""

    for current_qubit in search:
        current_qubit.superPosition()
        current_qubit.flip()

    # Apply a phase when all four transformed qubits are 1.
    search[-1].halfPhaseIf(search[:-1])

    for current_qubit in search:
        current_qubit.flip()
        current_qubit.superPosition()


def main():
    party = circuit()

    alice = qubit(party)
    bob = qubit(party)
    marker = qubit(party, measured=False)

    alice.mix()
    bob.mix()

    marker.flip()

    oracle(marker, alice, bob)
    diffuser([alice, bob])

    # Visualize the circuit
    print(party.getCircuitDraw())   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)


main()


