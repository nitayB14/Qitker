"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))



from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt





def main():
    """Build, display, export, and simulate"""

    #creating circuit
    party = circuit()
    alice = qubit(party)
    bob = qubit(party)
    josh = qubit(party)
    alice.mix()
    josh.flip()
    result = party.measure(1024)


    party.details()
    print(result.report(True))

    #parseToQiskit(party)
    



def parseToQiskit(circuit):
    """Export a Qitker circuit to Qiskit and plot measurement counts."""
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
