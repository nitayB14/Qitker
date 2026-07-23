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
    flipper = circuit()

    coin1 = qubit(flipper)
    coin2 = qubit(flipper, measured=False)
    coin3 = qubit(flipper)
    coin1.superPosition()
    

    flipper.execute()


    shots = 2000

    results = flipper.measure(shots)
    
    flipper.details()
    print(results)

    x, y = flipper.getMeasuredLists()

    print(x)
    print(y)


    qc = flipper.exportCircuit("qiskit")

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