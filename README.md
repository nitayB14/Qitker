# Qitker

Qitker explores quantum computation with Fibonacci anyons. It connects a simple circuit interface `circuit`, `qubit`, and `qRegister` to a backend that represents states in fusion spaces and performs braiding through F- and R-moves. Circuits can also be exported to Qiskit.

## Current status

- The version 1 frontend and Qiskit export are implemented and tested.
- The anyonic backend models computational and leakage states and supports physical cross-qubit braiding.
- Normal backend execution includes stored braid sequences for CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT. 
- Version 1 supports up to two controls per gate; this is not a limit on the total number of qubits in a circuit.
- The physical backend represents Fibonacci anyons in a fusion-tree basis and tracks both computational and leakage states.
- It applies physical braids through F and R moves, including braids across qubit boundaries, and reports fidelity and leakage relative to the ideal logical result.


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

## Examples and tests

- [Examples](Examples/)
- [Frontend tests](version_testing/Frontend/README.md)
- [Backend tests](version_testing/Backend/README.md)

Licensed under the [MIT License](LICENSE).
