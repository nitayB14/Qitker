# Qitker agent instructions

## Project and current scope

Qitker is a Python quantum-circuit project with a Fibonacci-anyon backend. Its public interface centers on circuit, qubit, and qRegister; Qiskit export is supported.

- The version 1 frontend and export layer are stable. Limit work there to testing, documentation, and small fixes unless the user explicitly requests a feature.
- The anyonic backend supports single-qubit logical execution. Its fusion-space model represents computational and leakage states, and physical cross-qubit braiding such as sigma_global(4) is implemented and tested. Multi-qubit logical gates are not yet integrated into normal backend execution.
- Braids_search/ contains the braid research: search, approximation, composition, and evaluation of candidate gate sequences. Treat research results separately from capabilities integrated into qitker/.

## Repository permissions

The repository is read-only by default. Inspecting, explaining, debugging, reviewing, or proposing a change does not authorize modifying files.

Do not create, edit, delete, rename, or move repository files, run formatters or commands that write to the repository, or commit changes unless the user explicitly authorizes the specific modification. If authorization is unclear, remain read-only and ask before editing. An explicit request to implement or edit a named file authorizes that requested work.

## Backend workflow

1. Start with the relevant implementation and trace its execution path; keep the investigation focused.
2. Establish the fusion tree, basis, computational subspace, and physical F/R-move model before changing leakage or braiding behavior.
3. Separate implementation defects from unresolved mathematics. State uncertainty instead of hiding it behind code.
4. Reuse existing abstractions, identify the smallest blocking component, and explain the smallest proposed change before implementation.
5. Do not invent APIs or assume Qiskit-style internals. Preserve the architecture unless a specific problem justifies changing it.

The next development step is to define and validate leakage behavior for logical operations that cross qubit boundaries, then build two-qubit logical gates on the tested physical braiding machinery. After that, extend to the version 1 controlled-gate target: CX, CY, CZ, CS, CT, CCX, CCY, CCZ, CCS, and CCT. More than two controls are outside the required version 1 scope.

## Tests and side effects

- See version_testing/Frontend/README.md and version_testing/Backend/README.md for test coverage and run commands.
- Backend T19 is a performance benchmark, not a normal assertion test. Both T19 scripts write CSV files beside themselves; check syntax only unless the user explicitly requests a benchmark run.
- Before running any other script, check whether it writes files. Use python -B for read-only test runs to avoid bytecode files.
