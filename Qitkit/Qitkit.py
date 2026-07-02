from compiler.qubit import qubit
from compiler.circuit import circuit
from ExportCode.exportCode import exportCode

from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def main():
    party = circuit()
    
    alice = qubit(party, 0)
    alice.S_gate()
    alice.S_gate()
    alice.S_gate()
    alice.S_gate()
    

    runOnFibonacci(party)
    
    runOnQiskit(party)
    


    

def runOnFibonacci(cirq):
    cirq.details()
    cirq.execute()

    comp, results = cirq.measure(1000)
    
    print(comp)
    print(results)

    


def runOnQiskit(qc):

    qc = exportCode.exportToQiskit(qc)
    qc.draw('mpl')

    qc.measure([0], [0])

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




if __name__ == "__main__":
    main()