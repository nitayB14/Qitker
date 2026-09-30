#==============================================
#        Fibonacci Anyons Quantum DSL
#==============================================
#creator: Nitay Bahliker
#Date: 29/09/2026
#Rule: Independent researcher

"""Solve a partially filled 3x3 Sudoku with Qitker and hybrid QAOA.

Fixed cells stay classical; each unknown uses a two-qubit qRegister with
01 -> 1, 10 -> 2, 11 -> 3. Penalize 00 and every equal pair in a row or
column. ITERATIONS sets the number of QAOA layers sharing gamma and beta,
optimized with COBYLA. TOP_RESULTS selects how many outcomes to reconstruct
and print as separate boards, ranked by measurement frequency.

Qitker builds the circuit; Qiskit Aer supplies measurement counts. Decode
those counts explicitly: getValue() requires a selected Qitker measurement
result, which external Aer execution does not populate.
"""

import math
import sys
from itertools import combinations
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from scipy.optimize import minimize
from qiskit import transpile
from qiskit_aer import Aer
from qitker import circuit, qubit, qRegister


BOARD_TEMPLATE = [
    [1, None, None],
    [None, 2, None],
    [None, None, 3],
]

ITERATIONS = 5  # QAOA layers per circuit, during optimization and final sampling.
TOP_RESULTS = 3  # Number of most frequent measurement outcomes to print as boards.

def applyPenalty(cell, other, marker, gamma):
    """Apply a relative phase exp(i * gamma) when cell equals other.

    other may be a register or an integer. The marker must start in |0>
    and remains there; controlled RZ(-2 * gamma) supplies the phase.
    """

    marker.rotateZif(cell == other, angle = -2 * gamma)


def applyConstraint(cell1, cell2, marker, gamma):
    """Penalize quantum equality or reject conflicting fixed clues."""
    if isinstance(cell1, qRegister):
        applyPenalty(cell1, cell2, marker, gamma)
    elif isinstance(cell2, qRegister):
        applyPenalty(cell2, cell1, marker, gamma)
    elif cell1 == cell2:
        raise ValueError("invalid Sudoku: equal fixed values share a row or column")


def mixer(quantumCells, beta):
    """Apply RX to both qubits of each unknown cell."""
    for cell in quantumCells:
        cell.rotateX(beta)


def costLayer(cells, quantumCells, marker, gamma):
    """Penalize invalid encodings, then equal pairs in rows and columns."""
    for cell in quantumCells:
        applyPenalty(cell, 0, marker, gamma)

    for line in [*cells, *zip(*cells)]:
        for cell1, cell2 in combinations(line, 2):
            applyConstraint(cell1, cell2, marker, gamma)


def runCircuit(gamma, beta, shots=2048, draw=False):
    """Build ITERATIONS QAOA layers with shared gamma and beta and sample in Aer.

    Return counts in Qitker bit order. If draw is True, print the
    most frequent reconstructed boards.
    """

    if isinstance(ITERATIONS, bool) or not isinstance(ITERATIONS, int) or ITERATIONS < 1:
        raise ValueError("ITERATIONS must be a positive integer")
    sudoku = circuit()
    cells = [
        [value if value is not None else qRegister(sudoku, size=2) for value in row]
        for row in BOARD_TEMPLATE
    ]
    marker = qubit(sudoku, measured=False)

    quantumCells = [
        cell for row in cells for cell in row if isinstance(cell, qRegister)
    ]

    for cell in quantumCells:
        cell.superPosition()

    for _ in range(ITERATIONS):
        costLayer(cells, quantumCells, marker, gamma)
        mixer(quantumCells, beta)

    return parseToQiskit(sudoku, shots, draw)


def decodeBoard(bitstring):
    """Decode Qitker-ordered bit pairs into unknown cells in row order."""
    measuredValues = iter(
        int(bitstring[index:index + 2], 2)
        for index in range(0, len(bitstring), 2)
    )
    return [
        [value if value is not None else next(measuredValues) for value in row]
        for row in BOARD_TEMPLATE
    ]


def countViolations(bitstring):
    """Count zeros and equal pairs; three equal values contribute three pairs."""
    grid = decodeBoard(bitstring)
    invalid = sum(value == 0 for row in grid for value in row)
    duplicates = sum(
        a == b
        for line in [*grid, *zip(*grid)]
        for a, b in combinations(line, 2)
    )
    return invalid + duplicates


def summarizeCounts(counts):
    """Return shot-weighted mean violations and probability of a valid board."""
    weightedViolations = validShots = 0
    for bitstring, count in counts.items():
        violations = countViolations(bitstring)
        weightedViolations += count * violations
        if violations == 0:
            validShots += count
    totalShots = sum(counts.values())
    return weightedViolations / totalShots, validShots / totalShots


def costFunction(params):
    """Sample the circuit and return its mean violations for optimization."""
    gamma, beta = params
    averageViolations, successProbability = summarizeCounts(
        runCircuit(gamma, beta, shots=1024)
    )
    print(
        f"gamma={gamma:.4f}, beta={beta:.4f}, "
        f"cost={averageViolations:.4f}, success={successProbability:.4f}"
    )
    return averageViolations


def optimize():
    """Optimize the two shared angles with at most 50 COBYLA evaluations."""
    result = minimize(
        costFunction,
        x0=[math.pi / 2, math.pi / 4],
        method="COBYLA",
        bounds=[(0, 2 * math.pi), (0, math.pi)],
        options={"maxiter": 50},
    )
    return result.x


def parseToQiskit(sudoku, shots=2048, draw=False):
    """Export to Qiskit, sample in Aer, and return counts in Qitker bit order.

    If draw is True, print up to TOP_RESULTS reconstructed boards.
    """
    qc = sudoku.exportCircuit("qiskit")
    qc.measure(*sudoku.getMeasuredLists())
    simulation = Aer.get_backend("qasm_simulator")
    transpiled = transpile(qc, simulation)
    counts = simulation.run(transpiled, shots=shots).result().get_counts()
    # Qiskit displays classical bits in reverse order to Qitker's allocation.
    counts = {bitstring[::-1]: count for bitstring, count in counts.items()}

    if draw:
        printBoards(counts, TOP_RESULTS)
    return counts


def printBoards(counts, limit):
    """Reconstruct the most frequent outcomes; report validity for each board."""
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("The number of displayed results must be a positive integer")
    topResults = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    totalShots = sum(counts.values())
    for rank, (bitstring, count) in enumerate(topResults, start=1):
        board = decodeBoard(bitstring)
        violations = countViolations(bitstring)
        status = "valid solution" if violations == 0 else f"{violations} violations"
        print(f"\nResult {rank}: {count} shots ({count / totalShots:.2%}) - {status}")
        border = "+" + "---+" * len(board[0])
        print(border)
        for row in board:
            print("| " + " | ".join(str(value) for value in row) + " |")
            print(border)


def main():
    """Optimize gamma and beta, print the top sampled boards, and report the observed valid-board fraction."""

    bestGamma, bestBeta = optimize()
    print(f"\nBest gamma: {bestGamma}")
    print(f"Best beta: {bestBeta}")
    counts = runCircuit(bestGamma, bestBeta, shots=16000, draw=True)
    _, successProbability = summarizeCounts(counts)
    print(f"Final success probability: {successProbability:.2%}")


if __name__ == "__main__":
    main()
