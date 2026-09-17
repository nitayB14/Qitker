
"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister

def main():
    party = circuit()
    
    alice = qubit(party)
    bob = qubit(party)
    
    # Create a Bell state
    alice.mix()
    bob.flipIf(alice)

    

    # Visualize the circuit
    print(party.getCircuitDraw())   

    # Run on the Fibonacci-anyon backend
    result = party.measure(shots=1024)
    print(result)


main()


