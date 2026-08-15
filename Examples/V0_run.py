import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))



from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt







def main():

    #creating circuit
    party = circuit()

    g1 = qRegister(party, size=3, measured=True)
    g2 = qRegister(party, size=5, initialize=2, measured=False)
    g3 = qRegister(party, size=5, initialize=2, measured=False)
    
    
    ancilla = qubit(party, measured=False)
    
    g1.flipIf(g2[:], where="xxx10", ancilla=ancilla)#, ancilla=ancilla)



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
