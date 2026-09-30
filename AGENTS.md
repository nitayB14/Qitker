# Qitker agent instructions

## Project and current scope

Qitker is a Python quantum-circuit project with a Fibonacci-anyon backend. Its public interface centers on circuit, qubit, and qRegister; Qiskit export is supported.

- The version 1 frontend and Qiskit export interfaces are established. Limit changes there to tests, documentation, and small fixes unless the user explicitly requests a feature.
- The anyonic backend models computational and leakage states and supports physical cross-qubit braiding, including tested sigma_global(4) behavior. Normal execution also routes logical controlled gates with up to two controls through stored braid sequences. The two-control limit applies to an individual gate, not to the total number of qubits in a circuit.
- Braids_search/ contains the braid research: search, approximation, composition, and evaluation of candidate gate sequences. Treat research results separately from capabilities integrated into qitker/.

## Repository permissions

The repository, including AGENTS.md, is read-only by default. Requests to inspect, explain, review, debug, or propose changes do not authorize editing files.

Before making a change, inspect the relevant code and tests, explain what files would change and why, and obtain the user's explicit authorization for that change. Do not treat agreement with an analysis or a proposed plan as authorization to edit.

After an authorized change, run the relevant checks or tests and report their results. If a check cannot be run, state that clearly. Do not make additional changes beyond the authorized scope without asking first.

## Backend workflow
For changes to physical braiding, fusion-space behavior, or leakage, follow these steps:

1. Start with the relevant implementation and trace its execution path; keep the investigation focused.
2. Establish the fusion tree, basis, computational subspace, and physical F/R-move model before changing leakage or braiding behavior.
3. Separate implementation defects from unresolved mathematics. State uncertainty instead of hiding it behind code.
4. Reuse existing abstractions, identify the smallest blocking component, and explain the smallest proposed change before implementation.
5. Do not invent APIs or assume Qiskit-style internals. Preserve the architecture unless a specific problem justifies changing it.

For version 1, normal backend execution supports the stored CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT gate sequences. Gates with more than two controls are outside the required version 1 scope. Keep future research plans separate from these instructions, and do not change anyonic engine behavior unless the user explicitly requests it.

## Tests and side effects

- See version_testing/Frontend/README.md and version_testing/Backend/README.md for test coverage and run commands.
- Backend T19 is a performance benchmark, not a normal assertion test. Both T19 scripts write CSV files beside themselves; check syntax only unless the user explicitly requests a benchmark run.
- Before running any other script, check whether it writes files. Use python -B for read-only test runs to avoid bytecode files.
