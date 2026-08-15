"""Demonstrate controlled RX, RY, and RZ gates with register controls."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import math


from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


def test_rotate_x():
    """Apply RX(pi) when all eight control qubits are one."""
    party = circuit()

    alice = qRegister(party, size=8)
    marker = qubit(party)

    # Set all eight controls to |1>.
    alice.flip()

    # RX(pi) acts like X up to a global phase.
    marker.rotateXif(alice, math.pi)

    party.details()
    parseToQiskit(party)




def test_rotate_y():
    """Apply RY(pi) when all eight control qubits are one."""
    party = circuit()

    alice = qRegister(party, size=8)
    marker = qubit(party)

    alice.flip()

    # RY(pi) transforms |0> into |1>.
    marker.rotateYif(alice, math.pi)

    party.details()
    parseToQiskit(party)



def test_rotate_z():
    """Convert a controlled RZ(pi) phase into a measurable target bit."""
    party = circuit()

    alice = qRegister(party, size=8)
    marker = qubit(party)

    alice.flip()

    marker.superPosition()
    marker.rotateZif(alice, math.pi)
    marker.superPosition()

    party.details()
    parseToQiskit(party)


def main():
    """Run all controlled-rotation demonstrations."""

    print("check X")
    test_rotate_x()
    
    print("check Y")
    test_rotate_y()

    print("check Z")
    test_rotate_z()



def parseToQiskit(circuit):
    """Export and simulate one controlled-rotation circuit."""
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
