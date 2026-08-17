# Qitker Frontend Correctness Tests

This directory contains 35 correctness tests for Qitker's frontend, covering everything from qubit and register creation to exporting a complete algorithm to Qiskit.

The tests use deterministic assertions and statevector or unitary comparisons against Qiskit. They do not depend on shots, plotting, or Qitker's anyonic execution engine.

## Part A - Construction, Registers, and Bit Order

- `T1_qubit_creation.py` - Verifies that creating qubits registers the same objects in the circuit with the correct order, indexes, and measurement flags.
- `T2_qubit_initialization.py` - Verifies that initializing a qubit to `0` or `1` produces the corresponding basis state after Qiskit export.
- `T3_register_integer_initialization.py` - Verifies that integer initialization produces the correct binary state in Qitker's register order.
- `T4_register_string_initialization.py` - Verifies that binary-string initialization preserves bit order, width, and leading zeroes.
- `T5_register_inferred_size.py` - Verifies register-size inference from integers and binary strings when `size` is omitted.
- `T6_register_indexing_and_slicing.py` - Verifies indexing, slicing, reversal, and that slices reference the original qubit objects without allocating new ones.
- `T7_measurement_selection.py` - Verifies measured-qubit selection and its mapping to consecutive classical bits.
- `T8_qiskit_bit_order.py` - Verifies that Qitker and Qiskit differ only in displayed bitstring order, not in the exported quantum circuit.

## Part B - Basic Gates

- `T9_h_gate.py` - Verifies that `H`, `h`, and `superPosition` match Qiskit's Hadamard gate.
- `T10_pauli_gates.py` - Verifies `X`, `Y`, `Z`, and all their public aliases, including relative phases.
- `T11_phase_gates.py` - Verifies `S`, `T`, `halfPhase`, and `quarterPhase` on a phase-sensitive superposition.
- `T12_rotation_gates.py` - Verifies `RX`, `RY`, `RZ`, and their aliases for zero, positive, negative, and full-turn angles.
- `T13_register_elementwise_gates.py` - Verifies that a register operation is applied exactly once to every contained qubit.
- `T14_swap.py` - Verifies SWAP on every basis input and on a complex superposition containing relative phase.
- `T15_register_shifts.py` - Verifies cyclic left and right shifts, modulo behavior, and preservation of the register's Python object order.

## Part C - Controlled Gates

- `T16_controlled_x.py` - Verifies controlled-X on every basis input and through coherent Bell-state creation.
- `T17_controlled_pauli_gates.py` - Verifies controlled-Y, controlled-Z, and their aliases.
- `T18_controlled_phase_gates.py` - Verifies controlled-S and controlled-T on phase-sensitive superpositions.
- `T19_multi_controlled_x.py` - Verifies MCX with two, three, and four controls across every possible control input.
- `T20_multi_controlled_phase_gates.py` - Verifies the complete unitary of multi-controlled Y, Z, S, and T gates.
- `T21_controlled_rotations.py` - Verifies controlled-RX, controlled-RY, and controlled-RZ with one to three controls and several angles.

## Part D - `where` Conditions

- `T22_where_default_and_one.py` - Verifies that the default condition, `where="1"`, and `where=1` produce the same positive control.
- `T23_where_zero.py` - Verifies activation on `|0>` and restoration of the control after temporary X gates.
- `T24_where_dont_care.py` - Verifies that `where="x"` ignores the control and applies the target operation unconditionally.
- `T25_where_bitstring_patterns.py` - Verifies complete truth tables for three-bit patterns containing `0`, `1`, and `x`.
- `T26_where_integer_patterns.py` - Verifies that each integer condition matches its zero-padded binary-string form.
- `T27_where_all_dont_care.py` - Verifies that an all-`x` pattern produces one unconditional operation rather than a controlled gate with no controls.
- `T28_qubit_equality_condition.py` - Verifies coherent equality between two qubits and the special case of comparing a qubit with itself.
- `T29_register_equality_condition.py` - Verifies equality between two- and three-qubit registers against explicit Qiskit decompositions.
- `T30_quantum_equality_uncompute.py` - Verifies equality on phase-sensitive register superpositions and checks that uncomputation leaves no XOR garbage.

## Part E - Integration, Validation, and Export

- `T31_controlled_register_target.py` - Verifies controlled gates and rotations applied to every qubit in a target register.
- `T32_controlled_register_with_ancilla.py` - Verifies that the ancilla-assisted path matches the direct path and restores the ancilla to `|0>`.
- `T33_validation_errors.py` - Verifies that invalid controls, comparisons, conditions, and ancillas raise clear exceptions.
- `T34_qiskit_export_complete.py` - Verifies all currently supported operation families together in one exported Qiskit circuit.
- `T35_full_grover_register_equality.py` - Runs a complete Grover search with a register-equality oracle and verifies the result, phases, and clean workspace.

## Shared Helper

- `frontend_test_helpers.py` - Provides Qiskit export, statevector and unitary comparison with global-phase tolerance, and bitstring conversion to Qitker display order.

## Running the Tests

Every test can run independently without `pytest`:

```powershell
python -B version_testing/Frontend/T1_qubit_creation.py
```

Run all 35 tests in numerical order with PowerShell:

```powershell
$tests = Get-ChildItem version_testing/Frontend/T*.py | Sort-Object { [int]([regex]::Match($_.BaseName, '^T(\d+)').Groups[1].Value) }
foreach ($test in $tests) { python -B $test.FullName; if ($LASTEXITCODE -ne 0) { break } }
```

A successful run prints `PASS` from all 35 test files.
