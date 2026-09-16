"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import time



from qitker import circuit, qubit, qRegister

def main():
    party = circuit()
    
    alice = qubit(party)
    bob = qubit(party)
    
    alice.mix()
    bob.mix()

    bob.phaseIf(alice)

    alice.mix()
    bob.mix()

    alice.flip()
    bob.flip()

    bob.phaseIf(alice)

    bob.flip()
    alice.flip()

    bob.mix()
    alice.mix()


    result = party.measure(shots=1024)

    print(party.getCircuitDraw())
    print(result)


main()
