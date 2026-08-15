"""Solve a partially filled 3x3 Sudoku with Qitker and hybrid QAOA.

Fixed cells remain classical integers, while only unknown cells allocate
two-qubit qRegisters.  The encoding is 01 -> 1, 10 -> 2, 11 -> 3, with
00 treated as an invalid value and penalized by the cost Hamiltonian.
"""

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


BOARD_TEMPLATE = [
    [1, None, None],
    [None, 2, None],
    [None, None, 3],
]


def applyPenalty(cell1, cell2, marker, gamma):
    """Apply an equality phase penalty between two quantum registers."""
    marker.flipIf(cell1, where=cell2)
    marker.rotateZ(gamma)
    marker.flipIf(cell1, where=cell2)


def applyFixedPenalty(cell, value, marker, gamma):
    """Apply a phase penalty when a register equals a fixed classical value."""
    marker.flipIf(cell, where=value)
    marker.rotateZ(gamma)
    marker.flipIf(cell, where=value)


def applyConstraint(cell1, cell2, marker, gamma):
    """Dispatch a row/column constraint for quantum or fixed cells."""
    cell1IsRegister = isinstance(cell1, qRegister)
    cell2IsRegister = isinstance(cell2, qRegister)

    if cell1IsRegister and cell2IsRegister:
        applyPenalty(cell1, cell2, marker, gamma)
    elif cell1IsRegister and isinstance(cell2, int):
        applyFixedPenalty(cell1, cell2, marker, gamma)
    elif isinstance(cell1, int) and cell2IsRegister:
        applyFixedPenalty(cell2, cell1, marker, gamma)
    elif cell1 == cell2:
        raise ValueError(
            "invalid Sudoku: equal fixed values share a row or column"
        )


def applyOwnPenalty(cell, marker, gamma):
    """Penalize the invalid two-qubit encoding 00."""
    marker.flipIf(cell, where=0)
    marker.rotateZ(gamma)
    marker.flipIf(cell, where=0)
    
    
def mixer(cells, beta):
    """Apply RX mixing only to the unknown quantum cells."""
    for row in cells:
        for cell in row:
            if isinstance(cell, qRegister):
                cell.rotateX(beta)

def costLayer(cells, marker, gamma):
    """Apply encoding, row, and column penalties for one QAOA layer."""
    rows = len(cells)
    columns = len(cells[0])

    # Self-penalty for the invalid value 0.
    for row in cells:
        for cell in row:
            if isinstance(cell, qRegister):
                applyOwnPenalty(cell, marker, gamma)

    # Every pair in each row.
    for row in range(rows):
        for first in range(columns):
            for second in range(first + 1, columns):
                applyConstraint(
                    cells[row][first],
                    cells[row][second],
                    marker,
                    gamma,
                )

    # Every pair in each column.
    for column in range(columns):
        for first in range(rows):
            for second in range(first + 1, rows):
                applyConstraint(
                    cells[first][column],
                    cells[second][column],
                    marker,
                    gamma,
                )

def runCircuit(gamma, beta, shots=2048, draw=False):
    """Build five tied-parameter QAOA layers for the hybrid Sudoku board.

    1 | x | x
    x | 2 | x
    x | x | 3
    """
    sudoku = circuit()


    cells = [
        [
            value
            if value is not None
            else qRegister(sudoku, size=2)
            for value in row
        ]
        for row in BOARD_TEMPLATE
    ]
    marker = qubit(sudoku, measured=False)

    


    for row in cells:
        for cell in row:
            if isinstance(cell, qRegister):
                cell.superPosition()


    for i in range(5):
        costLayer(cells, marker, gamma)
        mixer(cells, beta)

    return parseToQiskit(sudoku, shots, draw)



def decodeBoard(bitstring):
    """Merge measured register values with the fixed board entries."""
    measuredValues = iter(
        int(bitstring[index:index + 2], 2)
        for index in range(0, len(bitstring), 2)
    )

    return [
        [
            value if value is not None else next(measuredValues)
            for value in row
        ]
        for row in BOARD_TEMPLATE
    ]


def countViolations(bitstring):
    """Count invalid encodings and duplicate row or column values."""
    grid = decodeBoard(bitstring)

    violations = 0

    # Invalid value 0.
    for row in grid:
        for value in row:
            if value == 0:
                violations += 1

    # Equal values in rows.
    for row in grid:
        for first in range(3):
            for second in range(first + 1, 3):
                if row[first] == row[second]:
                    violations += 1

    # Equal values in columns.
    for column in range(3):
        for first in range(3):
            for second in range(first + 1, 3):
                if grid[first][column] == grid[second][column]:
                    violations += 1

    return violations


def costFunction(params):
    """Return the shot-weighted average number of Sudoku violations."""
    gamma, beta = params

    counts = runCircuit(gamma, beta, shots=1024)
    totalShots = sum(counts.values())

    averageViolations = sum(
        count * countViolations(bitstring)
        for bitstring, count in counts.items()
    ) / totalShots

    validShots = sum(
        count
        for bitstring, count in counts.items()
        if countViolations(bitstring) == 0
    )

    successProbability = validShots / totalShots

    print(
        f"gamma={gamma:.4f}, beta={beta:.4f}, "
        f"cost={averageViolations:.4f}, "
        f"success={successProbability:.4f}"
    )

    return averageViolations


def optimize():
    """Optimize the shared gamma and beta values with COBYLA."""
    result = minimize(
        costFunction,
        x0=[math.pi / 2, math.pi / 4],
        method="COBYLA",
        bounds=[
            (0, 2 * math.pi),
            (0, math.pi),
        ],
        options={"maxiter": 50},
    )

    return result.x



def parseToQiskit(circuit, shots=2048, draw=False):
    """Export and simulate the circuit, optionally printing its top results."""
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
        topResults = sorted(
            counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]

        print("\nTop 10 measurement results:")
        for position, (bitstring, count) in enumerate(topResults, start=1):
            values = decodeBoard(bitstring)
            board = " | ".join(
                " ".join(str(value) for value in row)
                for row in values
            )
            print(f"{position}. {board}: {count}")

    return counts

def main():
    """Optimize the Sudoku circuit and print its final solution probability."""
    bestGamma, bestBeta = optimize()

    print(f"\nBest gamma: {bestGamma}")
    print(f"Best beta: {bestBeta}")

    counts = runCircuit(
        bestGamma,
        bestBeta,
        shots=16000,
        draw=True,
    )

    validShots = sum(
        count
        for bitstring, count in counts.items()
        if countViolations(bitstring) == 0
    )
    successProbability = validShots / sum(counts.values())

    print(f"Final success probability: {successProbability:.2%}")


main()
