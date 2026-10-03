# Qitker: Project Overview

## Origin and motivation

Over the past two years, I have studied quantum computing and often found it difficult to connect an algorithm's ideas with its implementation in code. Managing qubit indices inside a circuit made it harder to follow the meaning of each operation. In one project, a single incorrect qubit index was enough to make the entire algorithm produce the wrong result. That experience helped motivate Qitker.

## What is Qitker?

Qitker is a Python library for building quantum circuits while reducing the need to manage qubit indices manually. Its interface centers on `circuit`, `qubit`, and `qRegister`, allowing users to express operations and relationships directly through qubit and register objects.

Alongside this interface, the project explores computation with Fibonacci anyons. Users describe an algorithm at the qubit level, then either simulate supported operations through the anyonic backend or export the logical circuit to Qiskit.

## From algorithm to execution

Qitker records operations and their relationships as a circuit description. Users do not need to specify each anyon braid themselves. The same circuit description provides a starting point for two execution paths:

| Path | What it simulates | Results |
| --- | --- | --- |
| Qitker anyonic backend | Stored braid sequences acting on fusion states | Measurement results, output-state fidelity, and leakage probability |
| Qiskit export | Logical gates, simulated with tools such as Qiskit Aer | Results from the external simulator |

Exporting a circuit does not execute it or add measurement instructions automatically. The Qiskit examples add measurements and run the exported circuit in Aer. This path does not simulate Qitker's braids or produce its anyonic fidelity and leakage report.

## Physical model

Qitker simulates a model of topological quantum computation based on Fibonacci anyons. Information is encoded in their possible fusion outcomes, with the system state expressed in a fusion-tree basis.

An R-move describes the exchange of anyons. F-moves change the fusion basis so that exchanges can be evaluated in the appropriate basis. Together, these operations determine the action of braids on the simulated state.

## Approximation and leakage

A logical gate can be approximated by a sequence of anyon braids. The sequence's action is calculated using F- and R-moves, but it may only approximate the desired gate. Braiding can also move part of the state outside the computational subspace that encodes the qubits; this is called leakage.

Qitker therefore reports both the output state's fidelity relative to the ideal logical result and the probability of leakage.

The research code in `Braids_search/` explores Solovay–Kitaev refinement for single-qubit gates, searches for controlled-gate braids using seed sequences and fidelity measures, and composition of existing gates into sequences with two controls. Normal execution uses previously stored sequences; it does not launch a new braid search for each gate. Research results are separate from capabilities integrated into the runtime.

## Current scope and limitations

Qitker is software for circuit construction and simulation. It does not operate quantum hardware.

- **Stored gates:** The version 1 anyonic backend supports gates with stored braid sequences, including CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT. The limit of two controls applies to an individual gate, not to the total number of qubits in a circuit.
- **Conditions:** The interface supports equality expressions (`==`) between qubits, between registers, and between a register and a pattern or integer. Other condition operators, such as inequality, ordering comparisons, and general logical combinations, have no dedicated support. An equality expression may generate a gate with more than two controls; such a circuit can be exported to Qiskit, but that gate is outside version 1 anyonic execution support.
- **Rotation angles:** The interface supports parameterized rotation gates and their Qiskit export. Automatically generating a braid sequence for an arbitrary requested angle is not implemented in the anyonic backend and is outside the version 1 scope. Algorithms using these rotations can be simulated through Qiskit.

## Documentation map

Start with the [project README](../../README.md) for installation, then follow the examples in order:

| Document | Focus | Execution |
| --- | --- | --- |
| [D1: Bell and GHZ States](D1_Bell_and_GHZ_States.md) | Create entangled states with qubits and registers, then measure them. | Qitker anyonic backend |
| [D2: Simple Grover Search](D2_Simple_Grover.md) | Mark a two-bit target, amplify it, and select a measurement result. | Qitker anyonic backend |
| [D3: Constrained Grover Search](D3_advanced_grover.md) | Combine register patterns, transformations, and equality constraints. | Qiskit Aer |
| [D4: 3x3 Sudoku with Hybrid QAOA](D4_sudoku3x3.md) | Encode a board, apply cost and mixer layers, and optimize circuit angles. | Qiskit Aer and SciPy |

## References

- Carnahan, C., Zeuch, D., and Bonesteel, N. E. (2016). *Systematically generated two-qubit anyon braids.*
- Reichardt, B. W. (2012). *Systematic distillation of composite Fibonacci anyons using one mobile quasiparticle.*
- Dawson, C. M., and Nielsen, M. A. (2006). *The Solovay–Kitaev algorithm.*
- Trebst, S., Troyer, M., Wang, Z., and Ludwig, A. W. W. (2008). *A short introduction to Fibonacci anyon models.*
- Pedersen, L. H., Møller, N. M., and Mølmer, K. (2007). *Fidelity of quantum operations.*
- Barenco, A., et al. (1995). *Elementary gates for quantum computation.*
- Bonesteel, N. E., Hormozi, L., Zikos, G., and Simon, S. H. (2005). *Braid Topologies for Quantum Computation.*
- Hormozi, L., Zikos, G., Bonesteel, N. E., and Simon, S. H. (2007). *Topological Quantum Compiling.*
- Nayak, C., Simon, S. H., Stern, A., Freedman, M., and Das Sarma, S. (2008). *Non-Abelian Anyons and Topological Quantum Computation.*
- Amy, M., Maslov, D., Mosca, M., and Roetteler, M. (2013). *A meet-in-the-middle algorithm for fast synthesis of depth-optimal quantum circuits.*
- Xu, H., and Wan, X. (2008). *Constructing Functional Braids for Low-Leakage Topological Quantum Computing.*
- Simon, S. H., Bonesteel, N. E., Freedman, M. H., Petrovic, N., and Hormozi, L. (2006). *Topological Quantum Computing with Only One Mobile Quasiparticle.*
- Wood, C. J., and Gambetta, J. M. (2018). *Quantification and Characterization of Leakage Errors.*
- Bennett, C. H. (1973). *Logical Reversibility of Computation.*
- Grover, L. K. (1996). *A fast quantum mechanical algorithm for database search.*
- Farhi, E., Goldstone, J., and Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm.*
- Powell, M. J. D. (1994). *A Direct Search Optimization Method That Models the Objective and Constraint Functions by Linear Interpolation.*
