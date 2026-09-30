# Qitker

Qitker explores quantum computation with Fibonacci anyons. It connects a simple circuit interface `circuit`, `qubit`, and `qRegister` to a backend that represents states in fusion spaces and performs braiding through F- and R-moves. Circuits can also be exported to Qiskit.

## Current status

- The version 1 frontend and Qiskit export are implemented and tested.
- The anyonic backend models computational and leakage states and supports physical cross-qubit braiding.
- Normal backend execution includes stored braid sequences for CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT. 
- Version 1 supports up to two controls per gate; this is not a limit on the total number of qubits in a circuit.
- The physical backend represents Fibonacci anyons in a fusion-tree basis and tracks both computational and leakage states.
- It applies physical braids through F and R moves, including braids across qubit boundaries, and reports fidelity and leakage relative to the ideal logical result.


## Installation

Qitker requires Python 3.11 or newer. NumPy is installed automatically with the package. Qiskit is optional and is needed only for `exportCircuit("qiskit")`.

To install from a checkout of this repository:

```powershell
python -m pip install .
```

To install the Qiskit export dependency as well:

```powershell
python -m pip install ".[qiskit]"
```

The advanced examples in `Examples/` may also require `qiskit-aer`, `scipy`, or `matplotlib`; these are not needed to use the Qitker library itself.

After version `1.0.0a1` is uploaded to TestPyPI, you can test the published package on another computer without cloning this repository. In an empty directory, create a virtual environment and install the dependencies from the main PyPI index before installing Qitker from TestPyPI:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install "numpy>=2.4,<3" "qiskit>=2.3.1,<3"
.\.venv\Scripts\python.exe -m pip install --index-url https://test.pypi.org/simple/ --no-deps "qitker==1.0.0a1"
.\.venv\Scripts\python.exe -m pip check
```

The `--no-deps` option prevents pip from looking for NumPy and Qiskit on TestPyPI, where they may be unavailable. If you only want to test the anyonic backend, omit `qiskit` from the dependency installation.

## Quick start

```python
from qitker import circuit, qubit
# Create circuit
party = circuit()

# Create 2 qubits
aliza = qubit(party)
baruch = qubit(party)

# Apply Hadamard gate
aliza.mix()

# Create entangled state
baruch.flipIf(aliza)

# Measure
result = party.measure(shots=1024)

# Print measurements details
print(result)
```

To check Qiskit export after installing its optional dependency:

```python
from qitker import circuit, qubit

sample = circuit()
qubit(sample).mix()
qiskit_circuit = sample.exportCircuit("qiskit")
print(qiskit_circuit)
```

## Examples and tests

- [Examples](Examples/)
- [Frontend tests](version_testing/Frontend/README.md)
- [Backend tests](version_testing/Backend/README.md)

Licensed under the [MIT License](LICENSE).
