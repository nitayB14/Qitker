"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))



from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt



def oracle(reg1, reg2, marker):
    """Phase-mark states in which both registers contain the same value."""

    marker.flipIf(reg1, where=reg2)



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
    """Build, display, export, and simulate the register-search example."""

    #creating circuit
    party = circuit()
    aliceGroup = qRegister(party, size=3)
    bobGroup = qRegister(party, size=3)
    marker = qubit(party, measured=False)

    aliceGroup.superPosition()
    bobGroup.superPosition()



    marker.flip()
    marker.superPosition()

    searchSpace = aliceGroup[:]
    searchSpace.extend(bobGroup[:])
    
    oracle(aliceGroup, bobGroup, marker)
    diffuser(searchSpace)
    
    party.details()
    parseToQiskit(party)
    



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
