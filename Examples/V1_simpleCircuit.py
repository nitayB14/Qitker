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
    party = circuit()

    alice = qubit(party)
    
    #hadamard gate
    alice.superPosition()
    
    #execution
    party.execute()

    #measure
    result = party.measure()

    #print circuit details
    party.details()

    #print measurments details
    print(result)




main()