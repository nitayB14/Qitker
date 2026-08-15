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

    alice = qubit(party)
    bob = qubit(party)
    dan = qubit(party)
    joni = qubit(party)


    alice.h()
    bob.h()
    dan.h()
    joni.h()

    marker = qubit(party, measured=False)

    marker.flip()
    marker.superPosition()

    marker.flipIf([alice,bob], where=[dan, joni])

    diffuser([alice,bob,dan,joni])

    party.details()
    parseToQiskit(party)
    
    



def parseToQiskit(circuit):
    """Export the Grover circuit and plot its measurement distribution."""
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
    
    plot_histogram(counts)
    #draw circuit
    #qc.draw('mpl')
    plt.show() 




main()
