from qitker import qubit, circuit

from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator




def main():
    demo = circuit()

    q0 = qubit(demo)
    q1 = qubit(demo)

    # H H = I
    q0.h()
    q0.h()

    # H Z H = X
    q1.h()
    q1.z()
    q1.h()

    demo.details()

    result = demo.measure(shots=4096)
    print(result.report(True))




#export circuit to qiskit
#qiskitExport(demoCircuit)    
def qiskitExport(demoCircuit):
    qc = demoCircuit.exportCircuit("qiskit")

    """qiskit operations on circuit"""
    x, y = demoCircuit.getMeasuredLists()
    qc.measure(x, y)

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=4096)

    #get result
    result = job.result()
    counts = result.get_counts()
    
    plot_histogram(counts)
    #draw circuit
    qc.draw('mpl')
    plt.show() 







main()