# EX4: 3x3 Sudoku with Hybrid QAOA

[Example source](../../Examples/EX4_sudoku3x3.py)

This example uses the Quantum Approximate Optimization Algorithm (QAOA) to search for a completion of this board:

```text
1 . .
. 2 .
. . 3
```

Each row and column must contain 1, 2, and 3 without repetitions. This example has no additional box constraints. Qitker builds the circuit, Qiskit Aer samples it, and SciPy optimizes its angles.

## Encode the board

Fixed clues remain classical integers. Each `None` in `BOARD_TEMPLATE` becomes a two-qubit `qRegister`:

| Bits | Cell value |
| --- | --- |
| `00` | Invalid |
| `01` | 1 |
| `10` | 2 |
| `11` | 3 |

The six unknown cells use 12 qubits, initialized in superposition with `superPosition()`. An additional, unmeasured marker starts in `0`.

## Apply QAOA layers

Each layer combines two operations:

- **Cost:** encode a phase penalty for each zero-valued cell and each equal pair in a row or column. `applyPenalty()` uses `marker.rotateZif(cell == other, angle=-2 * gamma)`, leaving the marker in `0`.
- **Mixer:** apply `rotateX(beta)` to every unknown cell's qubits.

`ITERATIONS = 5` sets the number of layers. All five share the same two angles, `gamma` and `beta`.

## Optimize the angles

`optimize()` uses COBYLA to minimize the measured mean number of violations. Each cost evaluation samples 1024 shots; the optimizer is configured for at most 50 evaluations.

`countViolations()` counts zeros and equal pairs, so three equal values in one row contribute three pair violations. `summarizeCounts()` weights these counts by measurement frequency and also calculates the fraction of valid boards.

The optimization evaluations update the angles; they are separate from the five QAOA layers within each circuit.

## Run and decode measurements

The optimizer varies the rotation angles in the cost and mixer layers. The version 1 anyonic backend does not automatically generate braid sequences for arbitrary requested angles, so this example uses Qiskit export and Aer simulation.

Install Qitker and the example dependencies using the [project instructions](../../README.md#installation), including `requirements.txt`. From the repository root, run:

```powershell
python -B Examples/EX4_sudoku3x3.py
```

The circuit is exported to Qiskit and sampled in Aer's `qasm_simulator`. The script reverses the returned bitstrings into Qitker order, then decodes pairs of bits into unknown cells in row order, preserving the fixed clues.

This explicit decoding is needed because external Aer execution does not populate a selected Qitker measurement result for `getValue()`. It also does not produce an anyonic fidelity or leakage report.

## Read the output

During optimization, the script prints `gamma`, `beta`, mean violations (`cost`), and the observed valid-board fraction (`success`). It then prints the returned angles and samples 16,000 shots.

`TOP_RESULTS = 3` displays the three most frequent boards, with their counts, percentages, and either `valid solution` or the number of violations. Boards are ranked by frequency, so invalid boards can appear. Here, `draw=True` prints boards as text.

The final success probability is the fraction of all final shots with zero violations. Optimization and finite sampling do not guarantee a valid board on every shot or an optimal set of angles.

## Try it

Change `ITERATIONS` to compare results with different circuit depths, or change `TOP_RESULTS` to display more or fewer boards. Both must be positive integers.
