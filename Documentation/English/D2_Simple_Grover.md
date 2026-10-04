# EX2: Simple Grover Search

[Example source](../../Examples/EX2_simple_grover.py)

This example searches for `01` among four possible two-bit values using one Grover iteration: an oracle marks the target, then a diffuser amplifies its probability.

## Prepare the qubits

`main()` creates two search qubits and applies `mix()` (Hadamard) to each, preparing an equal superposition of `00`, `01`, `10`, and `11`.

The helper qubit starts in `1` and is excluded from measurement:

```python
marker = qubit(network, initialize=1, measured=False)
marker.mix()
```

This prepares the marker in the state $|-\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$.

## Oracle: mark the target

```python
marker.flipIf(search, where="01")
```

The controlled flip acts when the first search qubit is `0` and the second is `1`. Flipping a marker in $|-\rangle$ introduces a minus sign, so this operation reverses the target's phase while leaving the marker in the same state. This is called phase kickback.

## Diffuser: amplify the target

`diffuser()` applies `mix()` followed by `flip()` to each search qubit, then:

```python
search[-1].phaseIf(search[:-1])
```

It finishes with `flip()` followed by `mix()` on each qubit. Together, these operations implement Grover diffusion, increasing the marked state's probability after the oracle.

## Run and read the result

Install Qitker following the [project installation instructions](../../README.md#installation), then run from the repository root:

```powershell
python -B Examples/EX2_simple_grover.py
```

The example draws the circuit and measures it using Qitker's anyonic backend; Qiskit is not required.

```python
result = network.measure(shots=1024)
print(result)
best = result.selectResult(rank=1)
```

`selectResult(rank=1)` selects the most frequent non-leakage outcome. The subsequent calls to `first_network.getValue()` and `second_network.getValue()` read the bits of that selected outcome; they do not perform new measurements.

## Expected result

For an ideal circuit, one Grover iteration finds `01` with 100% probability: first bit `0`, second bit `1`. Physical braid execution can introduce deviations and leakage. The printed report includes fidelity and leakage alongside the measurement results.

## Try it

Change `where="01"` to another two-bit pattern, such as `"10"`, and compare the selected result.
