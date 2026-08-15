"""Create two Qitker qubits and measure a simple superposition."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))


from qitker import circuit, qubit


def main():
    """Place the first of two qubits in superposition and measure both."""
    party = circuit()

    alice = qubit(party)
    bob = qubit(party)

    alice.superPosition()
    
    result = party.measure()

    print(result)


main()
