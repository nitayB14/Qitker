
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path

from numpy import diff, where
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister
import math


def main():
    party = circuit()

    alice = qubit(party)
    bob = qubit(party)
    net = qubit(party)
    marker = qubit(party)

    marker.rotateYif(alice, math.pi / 2)


    # Visualize the circuit
    print(party.getCircuitDraw())   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)


main()


