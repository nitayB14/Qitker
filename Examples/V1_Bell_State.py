"""Create and execute the smallest Qitker superposition example."""

import sys
from pathlib import Path

from qiskit import result
sys.path.append(str(Path(__file__).resolve().parent.parent))


from qitker import circuit, qubit

from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt 



def main():
    """Prepare one qubit in superposition and measure it with Qitker."""
    party = circuit()

    aliza = qubit(party)
    baruch = qubit(party)

    #hadamard gate
    aliza.mix()
    baruch.flipIf(aliza)
    

    #print circuit    
    party.draw()

    #measure
    result = party.measure(shots=1024)

    #print measurments details
    print(result)




main()
