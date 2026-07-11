from compiler.qubit import qubit
from compiler.circuit import circuit
from ExportCode.exportCode import exportToQiskit

from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator

def main():
    party = circuit()
    alice = qubit(party, 0)

    alice.superPosition()
    alice.flip()
    alice.phase()

    runOnFibonacci(party)
    
    #runOnQiskit(party)
    


    

def runOnFibonacci(cirq):
    cirq.execute()

    comp, results = cirq.measure(1000)
    cirq.details()
    print(comp)
    print(results)

    




def runOnQiskit(qc):
    print("qiskit:")

    qc = exportToQiskit(qc)

    matrix = Operator(qc).data
    print(matrix)

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




if __name__ == "__main__":
    main()