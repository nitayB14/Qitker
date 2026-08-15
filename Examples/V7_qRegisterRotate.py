import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import math


from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


def main():
    party = circuit()
    alice = qRegister(party, size=8)

    # First create a superposition so RZ changes its relative phase.
    alice.superPosition()
    alice.rotateZ(math.pi)
    alice.rotateY(math.pi)
    alice.rotateX(math.pi)

    # Convert the phase difference back into a measurable difference.
    alice.superPosition()

    # H -> RZ(pi) -> H should produce |1>.
    party.details()
    parseToQiskit(party)




def parseToQiskit(circuit):
    #export circuit to qiskit
    qc = circuit.exportCircuit("qiskit")

    """qiskit operations on circuit"""
    qc.draw('mpl')

    x,y = circuit.getMeasuredLists()

    qc.measure(x, y)

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=2048)

    #get result
    result = job.result()
    counts = result.get_counts()
    counts = {
        bitstring[::-1]: count
        for bitstring, count in counts.items()
    }
    
    plot_histogram(counts)
    #draw circuit
    #qc.draw('mpl')
    plt.show() 




main()
