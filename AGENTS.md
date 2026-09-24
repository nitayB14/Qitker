# Purpose

This repository contains Qitker, a quantum computing project.

Qitker v1 frontend is considered complete.

The current primary development focus is the Fibonacci-anyon backend,
especially leakage analysis, cross-qubit braiding, and multi-qubit gates.

The frontend and export layers should now be treated as stable unless the user
explicitly asks to modify or extend them.

The backend may be freely inspected, analyzed, tested conceptually, and discussed.

However, NO repository file may be modified without explicit user approval.

# STRICT READ-ONLY DEFAULT

The repository is READ-ONLY by default.

You may inspect files, trace execution, analyze architecture, reason about the
physics and mathematics, identify bugs, propose algorithms, suggest code changes,
and design tests.

You MUST NOT modify the repository unless the user explicitly authorizes a
specific modification.

This includes:

- Do NOT edit existing files.
- Do NOT create files.
- Do NOT delete files.
- Do NOT rename or move files.
- Do NOT automatically fix bugs.
- Do NOT apply patches.
- Do NOT refactor code.
- Do NOT change tests.
- Do NOT change documentation.
- Do NOT run formatting tools that modify files.
- Do NOT run commands that may modify repository state.
- Do NOT commit changes.

A request to:
- analyze
- inspect
- review
- explain
- debug
- investigate
- find the problem
- propose a solution
- design an implementation

is NOT permission to modify files.

Permission must be explicit.

Examples of valid permission:

"Implement this."
"Change this file."
"Fix this bug."
"Add this test."
"Edit x"


If permission is ambiguous, remain READ-ONLY and ask the user before modifying anything.

# Backend investigation workflow

When investigating a backend problem:

1. Inspect the existing implementation first.
2. Trace the relevant execution path.
3. Identify the mathematical / physical model being used.
4. Separate implementation bugs from physics / mathematical questions.
5. Reuse existing abstractions before proposing new ones.
6. Identify the smallest component that blocks progress.
7. Report findings to the user.
8. Propose the smallest next step.
9. Wait for explicit approval before modifying anything.

Do not start by writing code.

For physics-heavy problems such as leakage, fusion spaces, F-moves,
R-moves, or cross-qubit braiding, first establish the mathematical model
and basis being used by the existing implementation.

Do not hide uncertainty behind code.

If the mathematics is unresolved, say so and investigate the mathematics
before proposing an implementation.

# Efficiency

Keep investigations focused.

Do not scan or analyze the entire repository when the problem is localized.

Start from the files and classes directly involved in the current question,
then follow dependencies only when necessary.

Prefer understanding the existing execution path over proposing a new architecture.

Do not repeat analysis that has already been established during the current task.

When enough information exists to answer the user's question, stop investigating
and report the result.

# Development approach

Work together with the user incrementally.

Do not try to redesign the entire architecture at once.

Before suggesting a change:

1. Understand the existing implementation.
2. Explain how the relevant classes interact.
3. Identify the smallest required change.
4. Discuss the proposed design with the user.
5. Only implement it if the user explicitly asks you to.


# Current development status

Qitker v1 frontend is now considered complete.

The frontend architecture, including the high-level qubit/register interface,
conditional operations, rotations, and export layer, has reached the required
scope for version 1.

Only final testing, edge-case validation, documentation, and small fixes should
be performed on the frontend.

Do NOT add new frontend features unless the user explicitly decides that they
are required.

The main development focus now moves to the anyonic backend.


# Current backend status

The Qitker backend is based on Fibonacci anyons and currently supports
single-qubit execution.

Single-qubit gates can already be represented and executed through the anyonic
backend using the existing F-move and R-move machinery.

The next major milestone is multi-qubit execution.

However, multi-qubit gates should NOT be implemented immediately without first
understanding and handling leakage correctly.


# Backend development order

The current backend work should proceed in the following order:

1. Leakage

   Understand how computational states and leakage states behave when operations
   begin interacting across logical qubit boundaries.

   Before implementing two-qubit gates, determine how leakage is represented,
   detected, measured, and handled by the current Hilbert-space / fusion-tree
   architecture.

2. Cross-qubit braiding / sigma operations

   After leakage is understood, implement the ability to perform braids between
   anyons belonging to different logical qubits.

   A key example is sigma_4 in an 8-anyon / two-logical-qubit system:
   the braid exchanging the boundary anyons between the two logical qubits.

   This requires understanding how the fusion tree must be transformed using
   F-moves so that the relevant anyons can become braidable, applying the
   appropriate R-move, and then transforming the tree back correctly.

3. Two-qubit gates

   Once cross-qubit braiding works correctly and leakage behavior is understood,
   begin constructing and validating two-qubit logical gates.

4. Multi-controlled gates

   Extend the backend from two-qubit interactions toward the controlled gates
   required by the Qitker frontend.


# Version 1 backend target

The goal of Qitker v1 is NOT to support arbitrarily large controlled gates.

The maximum required controlled-gate scope for version 1 is:

- CX / CY / CZ / CS / CT
- CCX
- CCY
- CCZ
- CCS
- CCT

Supporting gates with more than two control qubits is outside the required
scope of version 1.

If a general automatic method for constructing larger controlled gates emerges
naturally from the backend architecture, it may be considered later, but it
should not delay completion of version 1.


# Current priority

The immediate priority is therefore:

LEAKAGE
    ↓
CROSS-QUBIT BRAIDING (for example sigma_4)
    ↓
TWO-QUBIT LOGICAL GATES
    ↓
CCX / CCY / CCZ / CCS / CCT
    ↓
BACKEND V1 COMPLETE

Do not expand the scope beyond this unless the user explicitly decides to do so.

The objective is to finish a stable and understandable version 1 backend,
not to solve every possible multi-qubit gate construction problem.


# Architecture principle

Qitker aims to provide a higher-level object-oriented interface for quantum programming.

The user should primarily interact with objects such as:

- circuit
- qubit
- qRegister 

The frontend should hide unnecessary index management and low-level circuit construction whenever possible.

The export layer should translate this higher-level representation into external quantum frameworks.


# Important constraints

Do not invent APIs that do not exist.

Do not assume that common Qiskit-style architecture applies to Qitker.

Always inspect the existing code before suggesting how a feature should integrate.

Preserve the current architecture unless there is a clear reason to change it.

If you notice architectural problems, explain them first instead of refactoring them automatically.


# If information is unclear

Never invent missing information.

Explain what is unclear.

Ask the user how they want the behavior to work.

When multiple implementations are possible, present the tradeoffs and let the user choose.

# Fusture example of how the code could look like

######################################################
from qitker import circuit, qubit

party = circuit()

alice = qubit(party)
bob = qubit(party)

alice.superPosition()
bob.flipIf(alice)

result = party.measure()
print(result)
######################################################