"""Section 19: record the current anyonic-engine performance baseline."""

import csv
import json
import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker import circuit, qRegister


OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "T19_performance_baseline_afetr_cache.csv"
)



FULL_CASES = [
    # qubits, gates, shots
    (1, 0, 1),
    (1, 1, 1),
    (1, 2, 1),
    (1, 4, 1),
    (1, 8, 1),
    (1, 12, 1),
    (2, 0, 1),
    (2, 1, 1),
    (2, 2, 1),
    (2, 4, 1),
    (2, 8, 1),
    (2, 12, 1),
    (3, 0, 1),
    (3, 1, 1),
    (3, 2, 1),
    (3, 4, 1),
    (3, 8, 1),
    (3, 12, 1),
    (4, 0, 1),
    (4, 1, 1),
    (4, 2, 1),
    (4, 4, 1),
    (4, 8, 1),
    (4, 12, 1),
]

SMOKE_CASES = [
    (1, 0, 1),
    (1, 1, 1),
    (2, 0, 1),
    (2, 1, 1),
    (3, 0, 1),
    (3, 1, 1),
]

SHOTS_CASES = [
    (2, 4, 1),
    (2, 4, 10),
    (2, 4, 100),
    (2, 4, 1024),
]

COLUMNS = [
    "case_id",
    "qubits",
    "measured_qubits",
    "gate",
    "target",
    "gates",
    "shots",
    "braids",
    "hilbert_dimension",
    "execution_time_seconds",
    "state_fidelity",
    "leakage_probability",
    "state_norm",
    "measurement_counts",
]


def parse_fidelity(value):
    """Convert the reporter's percentage string into a numeric ratio."""
    if isinstance(value, str) and value.endswith("%"):
        return float(value[:-1]) / 100.0

    return float(value)


def run_case(qubits_num, gates_num, shots):
    """Run one H-gate benchmark case and return one table row."""
    party = circuit()
    register = qRegister(party, size=qubits_num)

    for _ in range(gates_num):
        register[0].h()

    result = party.measure(shots=shots)

    final_state_vector = result.getFinalStateVector()
    measurement_counts = result.getPercentageOpbject()
    state_norm = float(np.linalg.norm(final_state_vector))

    assert party.getQubitsNumber() == qubits_num
    assert len(party.getOperationVector()) == gates_num
    assert result.getTotalGates() == gates_num
    assert result.getShotsNumber() == shots
    assert sum(measurement_counts.values()) == shots
    assert np.isclose(state_norm, 1.0)

    return {
        "case_id": f"Q{qubits_num}-G{gates_num}-S{shots}",
        "qubits": party.getQubitsNumber(),
        "measured_qubits": party.getQubitsNumberToMeasure(),
        "gate": "H",
        "target": 0,
        "gates": result.getTotalGates(),
        "shots": result.getShotsNumber(),
        "braids": result.getTotalBraids(),
        "hilbert_dimension": len(final_state_vector),
        "execution_time_seconds": result.getExecutionTime(),
        "state_fidelity": parse_fidelity(result.getFidelity()),
        "leakage_probability": result.getLeakageProbability(),
        "state_norm": state_norm,
        "measurement_counts": json.dumps(
            measurement_counts,
            sort_keys=True,
        ),
    }


def run_benchmark(cases, output_path=OUTPUT_PATH):
    """Run cases and write an Excel-readable CSV beside this file."""
    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=COLUMNS,
        )
        writer.writeheader()
        i = 1
        for case in cases:
            print(f"case number: {i} / 24") 
            i = i+1
            row = run_case(*case)
            writer.writerow(row)
            output_file.flush()

    return output_path


def main():
    output_path = run_benchmark(FULL_CASES)
    print(f"Performance baseline saved to: {output_path}")


if __name__ == "__main__":
    main()
