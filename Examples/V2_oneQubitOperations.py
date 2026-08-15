"""Demonstrate the aliases for Qitker's basic single-qubit gates."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit



def main():
    """Apply every basic gate alias, then execute and report the circuit."""
    #create circuit - named party
    party = circuit()
    
    #create qubit - named alice
    alice = qubit(party, 0)


    #H Gate
    alice.superPosition()
    alice.H()
    alice.h()

    #Y Gate
    alice.flip()
    alice.X()
    alice.x()

    #Y Gate
    alice.flipPhase()
    alice.Y()
    alice.y()

    #Z Gate
    alice.phase()
    alice.Z()
    alice.z()

    #S Gate
    alice.halfPhase()
    alice.S()
    alice.s()

    #T Gate
    alice.quarterPhase()
    alice.T()
    alice.t()

    
    #execute program
    party.execute()

    #measure
    result = party.measure()

    #print circuit details
    party.details()

    #print measurments details
    print(result)



main()
