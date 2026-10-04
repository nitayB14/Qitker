# EX3: Constrained Grover Search

[Example source](../../Examples/EX3_advanced_grover.py)

This example searches 256 pairs of four-bit messages for pairs satisfying three constraints. Qitker builds the Grover circuit, and Qiskit Aer simulates it.

## Prepare the registers

`build_circuit()` creates two four-qubit registers, `message_a` and `message_b`, plus three flag qubits with `measured=False`. Applying `mix()` to both message registers prepares an equal superposition of all message pairs. The flags start in `000`.

## Oracle: combine three constraints

The oracle marks pairs where all of these conditions hold:

| Condition | Meaning |
| --- | --- |
| A matches `1xx0` | A starts with `1` and ends with `0`. |
| B matches `x0x1` | B's second bit is `0` and its last bit is `1`. |
| A equals transformed B | Shift B cyclically left by one, then swap its first two qubits. |

In a pattern, `x` accepts either bit value. Two flags record the pattern matches; the third records equality after transforming B:

```python
message_b.shiftLeft(1)
message_b[0].swap(message_b[1])
flag_equal.flipIf(message_a == message_b)
```

`flag_equal.phaseIf([flag_a, flag_b])` reverses the phase only when all three flags are `1`.

## Restore and repeat

The oracle then undoes the equality check, restores B, and resets the pattern flags. This uncomputation returns the flags to `000` while preserving the phase marking.

The diffuser acts on all eight search qubits: `mix()` and `flip()`, a controlled phase, then `flip()` and `mix()` again. `ITERATIONS = 5` repeats the oracle and diffuser five times to amplify matching pairs.

## Run with Qiskit Aer

The diffuser's controlled phase has seven controls, exceeding the version 1 anyonic backend's limit of two controls per gate. This example therefore uses Qiskit export and Aer simulation.

Install Qitker and the example dependencies using the [project instructions](../../README.md#installation), including `requirements.txt`. From the repository root, run:

```powershell
python -B Examples/EX3_advanced_grover.py
```

The script exports the circuit and adds measurements:

```python
qc = network.exportCircuit("qiskit")
qc.measure(*network.getMeasuredLists())
```

It transpiles the circuit for Aer's `qasm_simulator` and samples `SHOTS = 2048` times. This runs the exported logical circuit, so it does not produce an anyonic fidelity or leakage report.

## Read the output

The script reverses Aer's bitstrings into Qitker's allocation order, `AAAABBBB`. It prints the most frequent pair as separate A and B values, together with its count out of 2048 shots, and displays the circuit and a histogram.

Matching pairs should be amplified, but sampling does not guarantee that every outcome satisfies the constraints. The script selects the most frequent pair without validating it; check it against the three conditions above.

## Try it

Change `ITERATIONS` and compare the histogram. More Grover iterations do not always improve success: amplification can overshoot. Change `SHOTS` to compare sampling fluctuations.
