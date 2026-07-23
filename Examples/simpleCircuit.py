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
    bob = qubit(party)

    alice.superPosition()
    bob.halfPhase()

    party.execute()

    shots = 2000

    results = party.measure(shots)

    party.details()
    print(results)

    x, y = party.getMeasuredLists()

    qc = party.exportCircuit("qiskit")

    """qiskit operations on circuit"""
    qc.draw('mpl')

    qc.measure(x, y)

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=shots)

    #get result
    result = job.result()
    counts = result.get_counts()
    
    plot_histogram(counts)
    #draw circuit
    #qc.draw('mpl')
    plt.show() 

main()