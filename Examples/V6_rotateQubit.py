"""Verify RX, RY, and RZ rotations on an individual Qitker qubit."""

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
    """Show that RX(pi/2) produces an approximately balanced measurement."""
    party = circuit()
    alice = qubit(party)

    # RX(pi/2) should produce approximately 50% |0> and 50% |1>.
    alice.rotateX(math.pi / 2)

    party.details()
    parseToQiskit(party)

def test_rotate_y():
    """Show that RY(pi/2) produces an approximately balanced measurement."""
    party = circuit()
    alice = qubit(party)

    # RY(pi/2) should produce approximately 50% |0> and 50% |1>.
    alice.rotateY(math.pi / 2)

    party.details()
    parseToQiskit(party)

def test_rotate_z():
    """Expose an RZ phase through an H-RZ-H interference sequence."""
    party = circuit()
    alice = qubit(party)

    # First create a superposition so RZ changes its relative phase.
    alice.superPosition()
    alice.rotateZ(math.pi)

    # Convert the phase difference back into a measurable difference.
    alice.superPosition()

    # H -> RZ(pi) -> H should produce |1>.
    party.details()
    parseToQiskit(party)



def main():
    """Run the three single-qubit rotation demonstrations."""

    print("check X")
    test_rotate_x()
    
    print("check Y")
    test_rotate_y()

    print("check Z")
    test_rotate_z()


def parseToQiskit(circuit):
    """Export and simulate one rotation demonstration with Qiskit."""
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
