# Qitker Backend Tests

This directory contains numbered tests T1-T21 for Qitker's Fibonacci-anyon backend. T1-T18 cover the fusion-space model and physical braiding; T20 covers the runtime cache. T21 checks frontend equality syntax through Qitker circuits and Qiskit export. T19 is a performance benchmark that writes CSV files, so it is excluded from the normal test run.

## Part A - Fusion Space and Leakage

- [T1_fusion_rules.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T1_fusion_rules.py) - Checks the Fibonacci fusion rules and invalid charge inputs.
- [T2_qubit_path_metadata.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T2_qubit_path_metadata.py) - Checks fusion-tree paths for logical qubits in systems of different sizes.
- [T3_fusion_state_enumeration.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T3_fusion_state_enumeration.py) - Checks recursive enumeration of valid fusion states.
- [T4_total_charge_filtering.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T4_total_charge_filtering.py) - Checks global vacuum-charge filtering and physical-space dimensions.
- [T5_stable_state_index_mapping.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T5_stable_state_index_mapping.py) - Checks stable state keys, index round trips, and invalid mappings.
- [T6_computational_leakage_classification.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T6_computational_leakage_classification.py) - Checks the split between computational and leakage states.
- [T7_fusion_basis_integration.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T7_fusion_basis_integration.py) - Checks FusionBasis ownership and its use by FusionSystem and HilbertSpace.
- [T8_physical_hilbert_space.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T8_physical_hilbert_space.py) - Checks physical-space dimensions, the initial logical state, and normalization.
- [T9_leakage_probability_and_measurement.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T9_leakage_probability_and_measurement.py) - Checks computational and leakage probabilities, measurement decoding, and deterministic logical measurement.

## Part B - F-Moves, R-Moves, and Braiding

- [T10_braiding_convention.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T10_braiding_convention.py) - Checks moving anyon identities, positional qubit blocks, and basis reindexing.
- [T11_quantum_r_move.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T11_quantum_r_move.py) - Checks Fibonacci R phases, inverse R moves, norm preservation, validation, and rollback.
- [T12_quantum_f_move.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T12_quantum_f_move.py) - Checks F-move unitarity, amplitude mixing, temporary bases, inverse sequences, validation, and rollback.
- [T13_atomic_f_r_operations.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T13_atomic_f_r_operations.py) - Checks that public F/R operations update the tree, basis, state, and history atomically.
- [T14_single_qubit_sigma_regression.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T14_single_qubit_sigma_regression.py) - Checks local sigma generators, inverses, stored single-qubit gate sequences, and rollback.
- [T15_braid_relations.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T15_braid_relations.py) - Checks Yang-Baxter, commutation, and inverse relations on physical states.
- [T16_global_sigma_api.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T16_global_sigma_api.py) - Checks global sigma indices, routing to local braids, and cross-qubit boundary handling.
- [T17_adjacent_anyon_recoupling.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T17_adjacent_anyon_recoupling.py) - Checks reversible F-move plans for adjacent anyons, including cross-qubit boundaries and rollback.
- [T18_cross_qubit_sigma.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T18_cross_qubit_sigma.py) - Checks sigma4 in the full two-qubit physical space, leakage, inverses, braid relations, history, and rollback.

## Part C - Performance, Cache, and Equality Syntax

- [T19_performance_baseline.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T19_performance_baseline.py) - Runs an anyonic-engine benchmark and writes a CSV beside the script. A second copy and its CSV files are in [T19/](https://github.com/nitayB14/Qitker/tree/main/version_testing/Backend/T19). Both copies are excluded from the normal test run.
- [T20_cache_behavior.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T20_cache_behavior.py) - Checks cache ownership, statistics, enabled and disabled behavior, physical equivalence, and rejection of foreign basis objects.
- [T21_equality_condition_syntax.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T21_equality_condition_syntax.py) - Checks symbolic `==` conditions, pattern values, equivalent gate and rotation syntax, validation, and object identity behavior.
- [T22_barrier_execution.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T22_barrier_execution.py) - Checks barrier behavior didnt change the logic circuit.
- [T23_controlled_gate_execution.py](https://github.com/nitayB14/Qitker/blob/main/version_testing/Backend/T23_controlled_gate_execution.py) - Controlled-gate execution through Qitker's anyonic backend.

## Running the Tests

Run an individual assertion-based test from the repository root without writing Python bytecode:

```powershell
python -B version_testing/Backend/T1_fusion_rules.py
```

Run T1-T18 and T20-T21 in numerical order. The filter deliberately skips T19:

```powershell
$tests = Get-ChildItem version_testing/Backend -Filter 'T*.py' -File |
    Where-Object { $_.BaseName -notmatch '^T19_' } |
    Sort-Object { [int]([regex]::Match($_.BaseName, '^T(\d+)').Groups[1].Value) }
foreach ($test in $tests) {
    python -B $test.FullName
    if ($LASTEXITCODE -ne 0) { break }
}
```

This runs 20 scripts. Check T19 syntax without executing its benchmark or writing bytecode:

```powershell
@'
import ast
from pathlib import Path

for path in (
    Path('version_testing/Backend/T19_performance_baseline.py'),
    Path('version_testing/Backend/T19/T19_performance_baseline.py'),
):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    print(f'{path}: syntax PASS')
'@ | python -B -
```

Running either T19 script executes the benchmark and writes or overwrites its CSV output in the same directory as that script.
