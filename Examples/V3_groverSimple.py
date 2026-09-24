"""Implement a small Grover search with qubit-comparison conditions."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))



from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt



def diffuser(search):
    """Grover diffuser over the four search qubits."""

    for current_qubit in search:
        current_qubit.superPosition()
        current_qubit.flip()

    # Apply a phase when all four transformed qubits are 1.
    search[-1].phaseIf(search[:-1])

    for current_qubit in search:
        current_qubit.flip()
        current_qubit.superPosition()





def main():
    """Build a four-qubit Grover iteration and simulate it with Qiskit."""

    #creating circuit
    party = circuit()

    reg1 = qRegister(party, size=3)
    reg2 = qRegister(party, size=3)

    reg1.mix()
    reg2.mix()

    marker = qubit(party, measured=False)

    marker.flip()
    marker.mix()

    marker.flipIf(reg1[:] + reg2[:], where= "1x1001")

    diffuser([reg1[0],reg1[1],reg1[2], reg2[0],reg2[1],reg2[2]])


    parseToQiskit(party)
    
    



def parseToQiskit(circuit):
    """Export the Grover circuit and plot its measurement distribution."""
    #export circuit to qiskit
    qc = circuit.exportCircuit("qiskit")

    """qiskit operations on circuit"""
    qc.draw('mpl')

    qc.measure(*(circuit.getMeasuredLists()))

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=2048)

    #get result
    result = job.result()
    counts = result.get_counts()
    
    plot_histogram(counts)
    #draw circuit
    #qc.draw('mpl')
    plt.show() 




main()
