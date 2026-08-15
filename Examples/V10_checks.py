"""Solve a 2x2 binary Sudoku with a small hybrid QAOA workflow."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import math
from scipy.optimize import minimize


from qitker import circuit, qubit, qRegister



from qiskit_aer import Aer
from qiskit import *
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


def applyPenalty(cell1, cell2, marker, gamma):
    """Apply a phase penalty when two one-qubit cells are equal."""
    marker.flipIf(cell1, where=cell2)
    marker.rotateZ(gamma)
    marker.flipIf(cell1, where=cell2)
    
    
def mixer(cells, beta):
    """Mix all cell states with an RX rotation."""
    cells.rotateX(beta)
    

def costLayer(cells, marker, gamma):
    """Penalize equal horizontal and vertical neighbors in the 2x2 board."""
    applyPenalty(cells[0], cells[1], marker, gamma)
    applyPenalty(cells[0], cells[2], marker, gamma)
    applyPenalty(cells[1], cells[3], marker, gamma)
    applyPenalty(cells[2], cells[3], marker, gamma)



def runCircuit(gamma, beta, shots=2048, draw=False):
    """Build four tied-parameter QAOA layers and return measurement counts."""

    sudoku = circuit()

    cells = qRegister(sudoku, size=4)
    marker = qubit(sudoku, measured=False)

    cells.superPosition()

    for i in range(4):
        costLayer(cells, marker, gamma)
        mixer(cells, beta)

    return parseToQiskit(sudoku, shots, draw)

def costFunction(params):
    """Return the negative probability of measuring a valid 2x2 board."""
    gamma, beta = params

    counts = runCircuit(gamma, beta, shots=1024)

    valid_states = {"0110", "1001"}

    success_probability = sum(
        counts.get(state, 0)
        for state in valid_states
    ) / sum(counts.values())

    print(
        f"gamma={gamma:.4f}, beta={beta:.4f}, "
        f"success={success_probability:.4f}"
    )

    return -success_probability


def optimize():
    """Find shared gamma and beta values with the COBYLA optimizer."""
    result = minimize(
        costFunction,
        x0=[math.pi / 2, math.pi / 4],
        method="COBYLA",
        bounds=[
            (0, 2 * math.pi),
            (0, math.pi),
        ],
        options={"maxiter": 30},
    )

    return result.x



def parseToQiskit(circuit, shots=2048, draw=False):
    """Export, simulate, and optionally visualize the Qitker circuit."""
    #export circuit to qiskit
    qc = circuit.exportCircuit("qiskit")

    x,y = circuit.getMeasuredLists()

    qc.measure(x, y)

    simulation = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, simulation)
    
    #run the simulation
    job = simulation.run(transpiled_qc, shots=shots)

    #get result
    result = job.result()
    counts = result.get_counts()
    counts = {
        bitstring[::-1]: count
        for bitstring, count in counts.items()
    }
    
    if draw:
        qc.draw('mpl')
        plot_histogram(counts)
        plt.show()

    return counts

def main():
    """Optimize the QAOA parameters and report the final success rate."""
    bestGamma, bestBeta = optimize()

    print(f"\nBest gamma: {bestGamma}")
    print(f"Best beta: {bestBeta}")

    counts = runCircuit(
        bestGamma,
        bestBeta,
        shots=8192,
        draw=True,
    )

    validShots = counts.get("0110", 0) + counts.get("1001", 0)
    successProbability = validShots / sum(counts.values())

    print(f"Final success probability: {successProbability:.2%}")


main()
