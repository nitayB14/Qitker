import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, export_to



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator


def main():

    party = circuit()
    
    alice = qubit(party, 0)

    #H Gate
    alice.superPosition()
    alice.H()
    alice.h()

    #Y Gate
    alice.flip()
    alice.X()
    alice.x()

    #Y Gate
    alice.flipPhase()
    alice.Y()
    alice.y()

    #Z Gate
    alice.phase()
    alice.Z()
    alice.z()

    #S Gate
    alice.halfPhase()
    alice.S()
    alice.s()

    #T Gate
    alice.quarterPhase()
    alice.T()
    alice.t()

    qc = export_to("qiskit", party)

    qc.draw('mpl')

    qc.measure([0], [0])

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
