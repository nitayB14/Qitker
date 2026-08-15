"""Build a 60-input condition oracle with Qitker.

The input is divided into three 20-qubit regions.  The oracle marks an input
when all three regions match their patterns.  An ``x`` in a pattern means
that the corresponding input qubit does not affect the condition.

This file only constructs the quantum circuit.  It does not export, execute,
or measure it.
"""

import sys
from pathlib import Path
from xml.dom import minicompat

sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qRegister


condition_oracle = circuit()

# The 60 qubits whose state is checked by the oracle.
inputs = qRegister(condition_oracle, size=60)

# Each pattern describes one independent 20-qubit condition.
first_pattern = "1x0x" * 5
second_pattern = "x11x" * 5
third_pattern = "0xx1" * 5

# One workspace qubit for each condition.
clauses = qRegister(condition_oracle, size=3, measured=False)
first_clause, second_clause, third_clause = (
    clauses[0],
    clauses[1],
    clauses[2],
)

# Compute whether each 20-qubit region matches its pattern.
first_clause.flipIf(inputs[0:20], where=first_pattern)
second_clause.flipIf(inputs[20:40], where=second_pattern)
third_clause.flipIf(inputs[40:60], where=third_pattern)

# Mark the state when all three conditions are true.
third_clause.phaseIf([first_clause, second_clause])

# Uncompute the conditions and restore all workspace qubits to |0>.
third_clause.flipIf(inputs[40:60], where=third_pattern)
second_clause.flipIf(inputs[20:40], where=second_pattern)
first_clause.flipIf(inputs[0:20], where=first_pattern)

condition_oracle.details()
