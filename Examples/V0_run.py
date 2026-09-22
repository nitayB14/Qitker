
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path

from numpy import diff
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister


def oracle(q1, q2):
    q2.phaseIf(q1)

def diffuser(q1, q2):
    q1.mix()
    q2.mix()

    q1.flip()
    q2.flip()

    q2.phaseIf(q1)

    q2.flip()
    q1.flip()

    q2.mix()
    q1.mix()


def main():
    party = circuit()

    alice = qubit(party)
    bob = qubit(party)
    
    alice.mix()
    bob.mix()


    oracle(alice, bob)
    diffuser(alice, bob)

    # Visualize the circuit
    print(party.getCircuitDraw())   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)


main()


