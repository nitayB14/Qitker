# Qitker

Qitker explores quantum computation with Fibonacci anyons. It connects a simple circuit interface `circuit`, `qubit`, and `qRegister` to a backend that represents states in fusion spaces and performs braiding through F- and R-moves. Circuits can also be exported to Qiskit.

## Current status

- The version 1 frontend and Qiskit export are implemented and tested.
- The anyonic backend models computational and leakage states and supports physical cross-qubit braiding.
- Normal backend execution includes stored braid sequences for CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT.
- Version 1 anyonic execution supports up to two controls per gate; this is not a limit on the total number of qubits in a circuit.
- The physical backend represents Fibonacci anyons in a fusion-tree basis and tracks both computational and leakage states.
- It applies physical braids through F and R moves, including braids across qubit boundaries, and reports fidelity and leakage relative to the ideal logical result.

## Installation

Qitker requires Python 3.11 or newer. Run the installation commands with the same Python interpreter that you use to run your programs. Installation is needed once per Python environment.

### Install the published TestPyPI release

Version `1.0.0a1` is available on [TestPyPI](https://test.pypi.org/project/qitker/1.0.0a1/). Install NumPy from the main PyPI index, then install Qitker from TestPyPI:

```powershell
python -m pip install "numpy>=2.4,<3"
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps "qitker==1.0.0a1"
python -m pip check
```

The `--no-deps` option keeps pip from looking for dependencies on TestPyPI. Qiskit is optional; to enable `exportCircuit("qiskit")`, also install:

```powershell
python -m pip install "qiskit==2.3.1"
```

### Install from source

From a checkout of this repository, install Qitker and its NumPy dependency with:

```powershell
python -m pip install .
```

For Qiskit export support, use this command instead:

```powershell
python -m pip install ".[qiskit]"
```

### Install dependencies for examples and plots

After installing Qitker by either method above, run the following from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m pip check
```

`requirements.txt` installs Qiskit with its visualization dependencies, Qiskit Aer for simulation, SciPy for optimization, and Matplotlib for plots. The `qiskit[visualization]` extra also installs `pylatexenc`, which is required by `draw("mpl")`. In Python, `plt` is an alias for `matplotlib.pyplot`, not a separate package.

The `qitker[qiskit]` extra provides circuit export; use `requirements.txt` for the simulation and plotting examples below. This requirements file installs dependencies only. Qitker itself must be installed separately using one of the commands above.

The example scripts and `requirements.txt` are available in this repository and are not included in the installed Qitker wheel. Download them or clone the repository to run the examples. For testing the published release on another computer, use the TestPyPI installation commands rather than installing from source.

## Quick start: anyonic execution

```python
from qitker import circuit, qubit

party = circuit()
aliza = qubit(party)
baruch = qubit(party)

aliza.mix()
baruch.flipIf(aliza)

result = party.measure(shots=1024)
print(result)
```

`measure()` executes the circuit through Qitker's anyonic backend and returns a report containing measurements, fidelity, and leakage.

## Export to Qiskit

With the Qiskit dependency installed, export a circuit as a Qiskit `QuantumCircuit`:

```python
from qitker import circuit, qubit

sample = circuit()
qubit(sample).mix()

qiskit_circuit = sample.exportCircuit("qiskit")
print(qiskit_circuit)
```

Export converts the circuit's gates; it does not run the anyonic backend or add Qiskit measurement instructions. Add those instructions explicitly before sampling with Qiskit Aer.

## Simulate and plot with Qiskit Aer

Install `requirements.txt` before running this example. It exports a Bell circuit, draws it with Matplotlib, samples it in Aer, and displays a histogram:

```python
from qitker import circuit, qubit
from qiskit import transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

party = circuit()
aliza = qubit(party)
baruch = qubit(party)
aliza.mix()
baruch.flipIf(aliza)

qc = party.exportCircuit("qiskit")
qc.measure(*party.getMeasuredLists())
qc.draw("mpl")

simulator = Aer.get_backend("qasm_simulator")
compiled = transpile(qc, simulator)
counts = simulator.run(compiled, shots=1024).result().get_counts()

# Display the first Qitker qubit on the left of each bitstring.
qitker_counts = {bits[::-1]: count for bits, count in counts.items()}
print(qitker_counts)
plot_histogram(qitker_counts)
plt.show()
```

Aer simulates the exported logical gates. Its results do not include Qitker's physical braiding fidelity or leakage. Use `party.measure()` for those quantities. `plt.show()` displays figures in a desktop environment with a graphical Matplotlib backend.

## Examples and tests

Start with the [project overview (D0)](https://github.com/nitayB14/Qitker/blob/main/Documentation/English/D0_Project_Overview.md) for the motivation, execution paths, and current limitations. The guides below explain each example.

After installing the example dependencies, run an example from the repository root:

```powershell
python -B Examples/EX3_advanced_grover.py
```

| Example | Guide | Execution and output |
| --- | --- | --- |
| [Bell and GHZ states](https://github.com/nitayB14/Qitker/blob/main/Examples/EX1_Bell_State.py) | [D1](https://github.com/nitayB14/Qitker/blob/main/Documentation/English/D1_Bell_and_GHZ_States.md) | Qitker anyonic execution, text circuit drawings, and measurement reports |
| [Simple Grover search](https://github.com/nitayB14/Qitker/blob/main/Examples/EX2_simple_grover.py) | [D2](https://github.com/nitayB14/Qitker/blob/main/Documentation/English/D2_Simple_Grover.md) | Qitker anyonic execution and text output |
| [Advanced Grover search](https://github.com/nitayB14/Qitker/blob/main/Examples/EX3_advanced_grover.py) | [D3](https://github.com/nitayB14/Qitker/blob/main/Documentation/English/D3_advanced_grover.md) | Qiskit Aer simulation, circuit drawing, and a Matplotlib histogram |
| [Sudoku with QAOA](https://github.com/nitayB14/Qitker/blob/main/Examples/EX4_sudoku3x3.py) | [D4](https://github.com/nitayB14/Qitker/blob/main/Documentation/English/D4_sudoku3x3.md) | Qiskit Aer simulation and SciPy optimization |

- [Frontend tests](https://github.com/nitayB14/Qitker/blob/main/version_testing/Frontend/README.md)
- [Backend tests](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/README.md)

Licensed under the [MIT License](https://github.com/nitayB14/Qitker/blob/main/LICENSE).
