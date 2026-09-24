
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path

from numpy import diff, where
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister
import math


def oracle(reg, marker):
    marker.halfPhaseIf(reg[0]==reg[1])
    

def diffuser(reg):
    """Grover diffuser over the four search qubits."""

    for current_qubit in reg:
        current_qubit.superPosition()
        current_qubit.flip()

    # Apply a phase when all four transformed qubits are 1.
    reg[-1].halfPhaseIf(reg[:-1])

    for current_qubit in reg:
        current_qubit.flip()
        current_qubit.superPosition()




def main():
    party = circuit()

    reg = qRegister(party, size=2)
    marker = qubit(party, measured=False)

    reg.mix()

    marker.flip()

    oracle(reg, marker)
    diffuser(reg)


    # Visualize the circuit
    party.draw()   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)

    result.selectResult(1)

    print(f"reg: {reg.getBitstring()}") 

main()
