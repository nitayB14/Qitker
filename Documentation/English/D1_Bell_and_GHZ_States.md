# EX1: Bell and GHZ States

[Example source](../../Examples/EX1_Bell_State.py)

This example prepares entangled states with Qitker: a two-qubit Bell state and a three-qubit GHZ state. Each individual measurement is random, but the qubit outcomes are correlated.

## Bell state

`bellState()` creates a `circuit` and two `qubit` objects, then applies:

```python
aliza.mix()
baruch.flipIf(aliza)
```

`mix()` applies a Hadamard gate, placing the first qubit in an equal superposition. `flipIf()` applies a controlled X gate, entangling the second qubit with the first. The ideal result is:

$$
|\mathrm{Bell}\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}.
$$

The function draws the circuit with `party.draw()` and prints the report returned by `party.measure()`.

## GHZ state

`GHZ()` groups `n=3` qubits in a `qRegister` and extends the same idea:

```python
entangleGroup[0].mix()
for i in range(n-1):
    entangleGroup[i+1].flipIf(entangleGroup[i])
```

The chain of controlled X gates prepares the ideal state:

$$
|\mathrm{GHZ}\rangle = \frac{|000\rangle + |111\rangle}{\sqrt{2}}.
$$

The function draws the circuit and measures it using `shots=1024`.

## Run the example

Install Qitker following the [project installation instructions](../../README.md#installation), then run from the repository root:

```powershell
python -B Examples/EX1_Bell_State.py
```

`main()` runs Bell first, followed by GHZ. This example uses Qitker's anyonic backend; Qiskit is not required.

## Expected results

| State | Ideal outcomes | Ideal probability per outcome |
| --- | --- | --- |
| Bell | `00`, `11` | 50% |
| GHZ | `000`, `111` | 50% |

Finite sampling causes counts to fluctuate. Qitker's report also includes fidelity and leakage: physical braid execution can differ from the ideal states above, so exact 50/50 counts are not guaranteed.

## Try it

Change `shots` to compare sampling fluctuations, or remove Bell's `flipIf()` to see how the outcomes change without entanglement. You can also change GHZ's `n`, keeping in mind that larger circuits increase simulation cost.
