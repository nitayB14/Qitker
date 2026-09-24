"""Export a simple Qitker circuit and simulate it with Qiskit Aer."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator


def main():
    """Build a one-qubit circuit, export it, and plot its measurements."""

    #creating circuit
    party = circuit()
    
    #creating one qubit
    alice = qubit(party, 0)

    #Gates
    alice.superPosition()    
    alice.flip()
  

    #export circuit to qiskit
    qc = party.exportCircuit("qiskit")

    """qiskit operations on circuit"""
    qc.draw('mpl')

    qc.measure(*(party.getMeasuredLists()))

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=1000)

    #get result
    result = job.result()
    counts = result.get_counts()
    
    plot_histogram(counts)
    #draw circuit
    #qc.draw('mpl')
    plt.show() 




main()
