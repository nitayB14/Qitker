# Qitker

Qitker explores quantum computation with Fibonacci anyons. It connects a simple circuit interface `circuit`, `qubit`, and `qRegister` to a backend that represents states in fusion spaces and performs braiding through F- and R-moves. Circuits can also be exported to Qiskit.

## Current status

- The version 1 frontend and Qiskit export are implemented and tested.
- The anyonic backend supports single-qubit execution, leakage analysis, and physical cross-qubit braiding, including sigma4.
- Multi-qubit logical gates are still in development.

## Quick start

Run from the repository root with Qiskit installed:

```python
from qitker import circuit, qubit

party = circuit()
alice = qubit(party)
bob = qubit(party)

alice.superPosition()
bob.flipIf(alice)

exported = party.exportCircuit("qiskit")
```

## Examples and tests

- [Examples](Examples/)
- [Frontend tests](version_testing/Frontend/README.md)
- [Backend tests](version_testing/Backend/README.md)

Licensed under the [MIT License](LICENSE).
