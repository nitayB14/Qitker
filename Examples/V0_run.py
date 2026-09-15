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
    
    q1 = qRegister(party, size=5)

    for i in range(1):
        q1[0].h()
    
    start = time.perf_counter()
    print("start executing...")
    result = party.measure(shots=1)
    print("finish executing...")
    end = time.perf_counter()

    print(party.getCircuitDraw())
    print(result)
    print(f"Runtime: {end - start:.6f} seconds")



main()
