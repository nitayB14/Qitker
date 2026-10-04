#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 29/09/2026
#Rule: Independent researcher
#
#

"""Demonstrate Bell and GHZ state preparation and measurement with Qitker."""

from qitker import circuit, qRegister, qubit

def bellState():
    """Prepare a two-qubit Bell state, draw the circuit, and print Qitker's measurement report."""
    party = circuit()

    aliza = qubit(party)
    baruch = qubit(party)

    #hadamard gate
    aliza.mix()

    #create entanglement
    baruch.flipIf(aliza)

    #print circuit    
    party.draw()

    #measure
    result = party.measure()

    #print measurments details
    print(result)


def GHZ():
    """Prepare an n-qubit GHZ state using a register and measure it with Qitker."""
    party = circuit()

    n=3

    #create group of qubits
    entangleGroup = qRegister(party, size=n)

    #hadamard gate for first item
    entangleGroup[0].mix()

    #create entanglement 
    for i in range(n-1):
        entangleGroup[i+1].flipIf(entangleGroup[i])

    #print circuit    
    party.draw()

    #measure
    result = party.measure(shots=1024)

    #print measurments details
    print(result)



def main():
    """Run the Bell-state and GHZ-state examples."""
    bellState()
    print("#"*70)
    GHZ()


main()
