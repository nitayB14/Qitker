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

    alice.h()
    bob.flipIf(alice)


    start = time.perf_counter()
    print("start executing...")
    result = party.measure(shots=1024)
    print("finish executing...")
    end = time.perf_counter()

    print(party.getCircuitDraw())
    print(result)
    print(f"Runtime: {end - start:.6f} seconds")



main()
