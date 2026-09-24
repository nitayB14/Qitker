
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path

from numpy import diff, where
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister
import math


def oracle(q1, q2, marker):
    marker.halfPhaseIf(q1==q2)
    

def diffuser(q1, q2):
    q1.mix()
    q2.mix()

    q1.flip()
    q2.flip()

    q2.halfPhaseIf(q1)

    q1.flip()
    q2.flip()

    q1.mix()
    q2.mix()



def main():
    party = circuit()

    alice = qubit(party)
    bob = qubit(party)
    marker = qubit(party, measured=False)

    alice.mix()
    bob.mix()

    marker.flip()

    oracle(alice, bob, marker)
    diffuser(alice, bob)


    # Visualize the circuit
    party.draw()   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)

main()
