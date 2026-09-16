"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import time



from qitker import circuit, qubit, qRegister

def main():    
    runCircuit()


    

def runCircuit():
    party = circuit()
    
    alice = qubit(party)
    bob = qubit(party)
    charlie = qubit(party)

    alice.h()
    bob.flipIf(alice)
    charlie.flipIf(bob)



    result = party.measure(shots=1024)

    print(party.getCircuitDraw())
    print(result)



main()
