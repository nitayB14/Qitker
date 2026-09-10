"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))



from qitker import circuit, qubit, qRegister

def main():    
    runCircuit()


    

def runCircuit():
    party = circuit()
    
    #q1 = qubit(party)
    q2 = qRegister(party, size=2)


    q2.h()
    #2.phase()
    #q2.quarterPhase()

    #q1.mix()
    
    result = party.measure()
    
    print(party.getCircuitDraw())
    print(result.report(True))




main()
