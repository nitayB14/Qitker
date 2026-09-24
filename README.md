# Qitker

Qitker explores quantum computation with Fibonacci anyons. It connects a simple circuit interface `circuit`, `qubit`, and `qRegister` to a backend that represents states in fusion spaces and performs braiding through F- and R-moves. Circuits can also be exported to Qiskit.

## Current status

- The version 1 frontend and Qiskit export are implemented and tested.
- The anyonic backend supports single-qubit execution, leakage analysis, and physical cross-qubit braiding, including sigma4.
- Multi-qubit logical gates above 3 qubits are still in development.

## Quick start

Run from the repository root with Qiskit installed:

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
