# Purpose

This repository contains Qitker, a quantum computing project.

For the current stage of development, focus only on understanding and analyzing the frontend and export layers of the project.

Do not work on the backend execution layer unless the user explicitly asks for it.


# Read-only mode

Unless the user explicitly requests otherwise:

- Do NOT modify any file.
- Do NOT create new files.
- Do NOT delete files.
- Do NOT refactor code.
- Do NOT run commands that change the repository.
- Do NOT automatically implement suggested changes.

Your role is currently analysis, discussion, planning, and code review only.

You may explain what should be changed and suggest code, but wait for the user before making any modification.


# Current scope

For now, focus on the files related to the frontend and export system.

The main relevant areas include:

- qitker/compiler/circuit.py
- qitker/compiler/qubit.py
- qitker/compiler/operation.py
- qitker/compiler/reporter/
- ExportCode/exportCode.py

You may inspect additional files when required to understand dependencies between these components.

However, avoid analyzing or changing the backend execution system unless it is necessary to understand the frontend interface.

The backend layer currently begins around the execution/parser layer and is outside the current development scope.


# Development approach

Work together with the user incrementally.

Do not try to redesign the entire architecture at once.

Before suggesting a change:

1. Understand the existing implementation.
2. Explain how the relevant classes interact.
3. Identify the smallest required change.
4. Discuss the proposed design with the user.
5. Only implement it if the user explicitly asks you to.


# Current development goals

The current major goal is to design and implement the `where` condition system used by `flipIf`.

`flipIf` already exists as a frontend operation. The purpose of `where` is to extend it so the user can describe more complex control conditions at a high level, without manually constructing the required lower-level quantum gates.

The `where` system should:

- define which states of the control qubit or register should activate the target operation
- remain part of the frontend abstraction
- allow Qitker to translate high-level conditions into the required lower-level controlled gate operations
- be designed so additional condition types can be added later without rewriting the core `flipIf` architecture

The main focus at this stage is the design of the `where` API, its accepted input types, and how each condition should be translated internally.

The exact supported behaviors are still being defined.

Do not assume behavior that has not been explicitly specified.
Do not implement additional condition types unless they are defined by the user.
When a case is ambiguous, discuss the intended behavior with the user before making architectural changes.

Examples and expected behaviors will be defined below:

# Expected behavior

ancilla.flipIf(bob)
# Existing behavior.
# Flip ancilla if bob is in state |1>.

ancilla.flipIf(bob, where='0')
# Flip ancilla if bob is in state |0>.

ancilla.flipIf(bob, where='1')
# Flip ancilla if bob is in state |1>.

ancilla.flipIf(bob, where='x')
# Ignore bob as a condition.
# 'x' means "don't care".

ancilla.flipIf(bob, where=dan)
# Use another qubit as the condition reference.
# Exact semantics should follow the behavior defined by the user during implementation.

ancilla.flipIf([bob, dan, alice], where="1x0")
# Multi-qubit condition.
# bob must be |1>.
# dan is ignored.
# alice must be |0>.

ancilla.flipIf([bob, dan, alice], where=4)
# Numeric condition for the supplied control qubits.
# Exact integer-to-bitstring interpretation should be defined explicitly before implementation.

# For the current architecture, these cases are sufficient.
# Do not add additional `where` forms yet.


# Future goal: qRegister

After the initial `flipIf` functionality is designed, a new `qRegister` class is planned.

For now, only remember this architectural direction.

Do NOT implement `qRegister` unless the user explicitly asks to begin working on it.

The intended purpose of `qRegister` is to represent and manage groups of qubits as a higher-level frontend object.

Its exact API and behavior will be designed later together with the user.


# Architecture principle

Qitker aims to provide a higher-level object-oriented interface for quantum programming.

The user should primarily interact with objects such as:

- circuit
- qubit
- future qRegister objects

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