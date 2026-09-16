"""Compose and evaluate a three-qubit CCX braid from saved primitives.

The single-qubit H, T and X words come from ``braid_sequences_sk.json``.
The controlled-X word comes from ``braid_sequences.json`` because the SK
library contains only single-qubit gates.

Logical qubits use four Fibonacci anyons each, so q[0], q[1], q[2] occupy
positions 1--4, 5--8 and 9--12. Signed braid indices are chronological:
``i`` means sigma_i and ``-i`` means sigma_i inverse. Twelve anyons have
eleven adjacent braid generators, sigma_1 through sigma_11.

The standard ancilla-free Toffoli decomposition needs CX(q[0], q[2]). The
saved CX acts on adjacent qubits, so the non-neighbour operation is expanded
as CX(0,1), CX(1,2), CX(0,1), CX(1,2). This preserves q[1].

The saved SK T word has a nonidentity endpoint permutation. The standard
decomposition contains one unmatched T on q[0], so two saved X words are
inserted immediately afterwards. Ideally X^2=I, while the three identical
endpoint three-cycles (T, X, X) compose to the identity. The complete word
is still scored against CCX; this correction is never assumed to be exact.
"""

import json
import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEARCH_DIRECTORY = str(Path(__file__).resolve().parent)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if SEARCH_DIRECTORY not in sys.path:
    sys.path.insert(0, SEARCH_DIRECTORY)

from search_engine import braid_searching
from qitker.QuantumMath.constant import math_constant


SK_SEQUENCE_FILE = PROJECT_ROOT / "qitker" / "parser" / "braid_sequences_sk.json"
CONTROLLED_SEQUENCE_FILE = PROJECT_ROOT / "qitker" / "parser" / "braid_sequences.json"
QUBITS = 3
ANYONS_PER_QUBIT = 4
ANYON_COUNT = QUBITS * ANYONS_PER_QUBIT
MAX_SIGMA = ANYON_COUNT - 1


def _load_json(path):
    with path.open(encoding="utf-8-sig") as source:
        contents = json.load(source)
    if not isinstance(contents, dict):
        raise ValueError(f"{path.name} must contain a JSON object.")
    return contents


def _validated_word(record, gate, source):
    if not isinstance(record, dict) or "sequence" not in record:
        raise ValueError(f"Gate {gate!r} in {source.name} has no sequence.")
    word = tuple(record["sequence"])
    if not word:
        raise ValueError(f"Gate {gate!r} in {source.name} has an empty sequence.")
    if any(isinstance(index, bool) or not isinstance(index, int) or index == 0
           for index in word):
        raise ValueError(f"Gate {gate!r} in {source.name} has an invalid braid word.")
    return word


def load_primitives():
    """Load the precise local words and the saved adjacent CX word."""
    sk = _load_json(SK_SEQUENCE_FILE)
    controlled = _load_json(CONTROLLED_SEQUENCE_FILE)
    return {
        gate: _validated_word(sk.get(gate), gate, SK_SEQUENCE_FILE)
        for gate in ("H", "T", "X")
    } | {
        "CX": _validated_word(
            controlled.get("CX"), "CX", CONTROLLED_SEQUENCE_FILE
        )
    }


def _inverse_word(sequence):
    """Return the chronological braid word for the inverse operation."""
    return tuple(-index for index in reversed(tuple(sequence)))


def _reduce_word(sequence):
    """Remove adjacent sigma_i, sigma_i^-1 pairs exactly."""
    reduced = []
    for index in sequence:
        if reduced and reduced[-1] == -index:
            reduced.pop()
        else:
            reduced.append(index)
    return tuple(reduced)


def _shift_word(sequence, offset):
    """Shift a positional braid word while retaining every crossing sign."""
    shifted = tuple(
        (1 if index > 0 else -1) * (abs(index) + offset)
        for index in sequence
    )
    if any(abs(index) > MAX_SIGMA for index in shifted):
        raise ValueError(
            f"Shifted word exceeds sigma_{MAX_SIGMA} for {ANYON_COUNT} anyons."
        )
    return shifted


def _local_word(sequence, qubit):
    if isinstance(qubit, bool) or not isinstance(qubit, int):
        raise TypeError("qubit must be an integer.")
    if not 0 <= qubit < QUBITS:
        raise ValueError("qubit must be 0, 1, or 2.")
    if any(abs(index) > 3 for index in sequence):
        raise ValueError("A four-anyon local word may use only sigma_1..sigma_3.")
    return _shift_word(sequence, ANYONS_PER_QUBIT * qubit)


def _adjacent_cx_word(cx_word, control, target):
    """Embed the saved left-to-right CX in adjacent logical blocks."""
    if (control, target) not in ((0, 1), (1, 2)):
        raise ValueError("Direct CX supports only (0,1) or (1,2).")
    if any(abs(index) > 7 for index in cx_word):
        raise ValueError("The saved CX is not an eight-anyon braid word.")
    return _shift_word(cx_word, ANYONS_PER_QUBIT * control)


def _remote_cx_02_word(cx01, cx12):
    """Implement CX(q[0],q[2]) while restoring the intermediate q[1]."""
    return cx01 + cx12 + cx01 + cx12


def _endpoint_order(sequence):
    """Return the final physical anyon order induced by a braid word."""
    order = list(range(1, ANYON_COUNT + 1))
    for index in sequence:
        left = abs(index) - 1
        if not 0 <= left < ANYON_COUNT - 1:
            raise ValueError(f"Invalid sigma index for {ANYON_COUNT} anyons: {index}.")
        order[left], order[left + 1] = order[left + 1], order[left]
    return tuple(order)


def _single_qubit_matrix(gate, qubit):
    factors = [np.eye(2, dtype=complex) for _ in range(QUBITS)]
    factors[qubit] = np.asarray(gate, dtype=complex)
    return np.kron(np.kron(factors[0], factors[1]), factors[2])


def _controlled_x_matrix(control, target):
    result = np.zeros((8, 8), dtype=complex)
    for column in range(8):
        bits = list(format(column, "03b"))
        if bits[control] == "1":
            bits[target] = "0" if bits[target] == "1" else "1"
        result[int("".join(bits), 2), column] = 1
    return result


def _ccx_matrix():
    result = np.zeros((8, 8), dtype=complex)
    for column in range(8):
        bits = list(format(column, "03b"))
        if bits[0] == bits[1] == "1":
            bits[2] = "0" if bits[2] == "1" else "1"
        result[int("".join(bits), 2), column] = 1
    return result


def _assert_ideal_decomposition():
    """Verify the chosen gate order and the nearest-neighbour CX identity."""
    identity = np.eye(8, dtype=complex)
    cx01 = _controlled_x_matrix(0, 1)
    cx12 = _controlled_x_matrix(1, 2)
    cx02 = _controlled_x_matrix(0, 2)

    remote = identity
    for operation in (cx01, cx12, cx01, cx12):
        remote = operation @ remote
    if not np.allclose(remote, cx02, atol=1e-12, rtol=0):
        raise RuntimeError("The nearest-neighbour CX(0,2) identity is incorrect.")

    h = math_constant.GATE_MATRICES["H"]
    t = math_constant.GATE_MATRICES["T"]
    x = math_constant.GATE_MATRICES["X"]
    operations = (
        _single_qubit_matrix(h, 2),
        cx12,
        _single_qubit_matrix(t.conj().T, 2),
        cx02,
        _single_qubit_matrix(t, 2),
        cx12,
        _single_qubit_matrix(t.conj().T, 2),
        cx02,
        _single_qubit_matrix(t, 1),
        _single_qubit_matrix(t, 2),
        _single_qubit_matrix(h, 2),
        cx01,
        _single_qubit_matrix(t, 0),
        # Logical identity used only to repair the SK endpoint permutation.
        _single_qubit_matrix(x, 0),
        _single_qubit_matrix(x, 0),
        _single_qubit_matrix(t.conj().T, 1),
        cx01,
    )
    compiled = identity
    for operation in operations:
        compiled = operation @ compiled
    target = _ccx_matrix()
    overlap = np.trace(target.conj().T @ compiled)
    phase = overlap / abs(overlap) if abs(overlap) else 1.0
    if not np.allclose(compiled, phase * target, atol=1e-12, rtol=0):
        raise RuntimeError("The selected single-qubit/CX decomposition is not CCX.")


def build_ccx_braid(primitives=None, reduce=True):
    """Return the physical 12-anyon braid word and component information."""
    _assert_ideal_decomposition()
    if primitives is None:
        primitives = load_primitives()

    h2 = _local_word(primitives["H"], 2)
    t0 = _local_word(primitives["T"], 0)
    t1 = _local_word(primitives["T"], 1)
    t2 = _local_word(primitives["T"], 2)
    tdg1 = _local_word(_inverse_word(primitives["T"]), 1)
    tdg2 = _local_word(_inverse_word(primitives["T"]), 2)
    x0 = _local_word(primitives["X"], 0)
    cx01 = _adjacent_cx_word(primitives["CX"], 0, 1)
    cx12 = _adjacent_cx_word(primitives["CX"], 1, 2)
    cx02 = _remote_cx_02_word(cx01, cx12)

    components = (
        ("H(q2)", h2),
        ("CX(q1,q2)", cx12),
        ("Tdg(q2)", tdg2),
        ("CX(q0,q2)", cx02),
        ("T(q2)", t2),
        ("CX(q1,q2)", cx12),
        ("Tdg(q2)", tdg2),
        ("CX(q0,q2)", cx02),
        ("T(q1)", t1),
        ("T(q2)", t2),
        ("H(q2)", h2),
        ("CX(q0,q1)", cx01),
        ("T(q0)", t0),
        ("X(q0)", x0),
        ("X(q0)", x0),
        ("Tdg(q1)", tdg1),
        ("CX(q0,q1)", cx01),
    )
    unreduced = tuple(index for _, word in components for index in word)
    sequence = _reduce_word(unreduced) if reduce else unreduced
    final_order = _endpoint_order(sequence)
    if final_order != tuple(range(1, ANYON_COUNT + 1)):
        raise RuntimeError(
            "The composed CCX braid does not restore all twelve anyon identities: "
            f"{final_order}."
        )
    return {
        "sequence": sequence,
        "unreduced_braid_count": len(unreduced),
        "braid_count": len(sequence),
        "components": tuple((name, len(word)) for name, word in components),
        "final_anyon_order": final_order,
        "order_restored": True,
        "anyon_count": ANYON_COUNT,
        "sigma_range": (1, MAX_SIGMA),
        "source_files": {
            "single_qubit": str(SK_SEQUENCE_FILE),
            "controlled_x": str(CONTROLLED_SEQUENCE_FILE),
        },
        "endpoint_correction": "X(q0)^2",
    }


def _validate_fidelity(fidelity):
    if isinstance(fidelity, (bool, np.bool_)) or not isinstance(
        fidelity, (int, float, np.integer, np.floating)
    ):
        raise TypeError("fidelity must be a percentage.")
    if not np.isfinite(fidelity) or not 0 < fidelity <= 100:
        raise ValueError("fidelity must be in (0, 100].")


def search_ccx(fidelity=99.0, max_leakage=None, verify=False):
    """Compose, score and optionally replay the saved-gate CCX braid.

    The returned ``braid_sequence`` is the signed sigma-index vector. The
    returned ``braid_matrix`` is its un-postselected 8x8 computational block
    in basis 000,001,...,111. Amplitude outside that block is represented by
    the leakage metrics and therefore lowers the reported fidelities.
    """
    _validate_fidelity(fidelity)
    if not isinstance(verify, bool):
        raise TypeError("verify must be a boolean.")
    if max_leakage is None:
        max_leakage = 1 - fidelity / 100
    if isinstance(max_leakage, (bool, np.bool_)) or not isinstance(
        max_leakage, (int, float, np.integer, np.floating)
    ):
        raise TypeError("max_leakage must be a probability.")
    if not np.isfinite(max_leakage) or not 0 <= max_leakage <= 1:
        raise ValueError("max_leakage must be in [0, 1].")

    candidate = build_ccx_braid()
    engine = braid_searching(
        qubits_num=3,
        gate="X",
        target=2,
        controllers=(0, 1),
    )
    result = engine.evaluate(candidate["sequence"])
    target = engine.target_matrix
    matrix = result["computational_matrix"]
    overlap = np.trace(target.conj().T @ matrix)
    global_phase = overlap / abs(overlap) if abs(overlap) else 1.0
    aligned_matrix = matrix / global_phase
    matrix_error = float(np.linalg.norm(aligned_matrix - target, ord=2))

    candidate.update({
        "target_kind": "CCX",
        "controls": (0, 1),
        "target": 2,
        "requested_fidelity": float(fidelity),
        "max_leakage": float(max_leakage),
        "braid_sequence": np.asarray(candidate["sequence"], dtype=int),
        "braid_matrix": matrix,
        "phase_aligned_braid_matrix": aligned_matrix,
        "ideal_matrix": target,
        "global_phase": complex(global_phase),
        "matrix_error": matrix_error,
        "result": result,
        "target_reached": (
            result["average_gate_fidelity"] >= fidelity
            and result["maximum_leakage"] <= max_leakage
            and result["order_restored"]
        ),
        "replay_error": None,
    })
    if verify:
        candidate["replay_error"] = engine.verify_with_qitker(candidate["sequence"])
    return candidate


def print_result(candidate, print_sequence=True):
    result = candidate["result"]
    print("CCX: controls=q[0],q[1], target=q[2]")
    print(f"Physical anyons: {candidate['anyon_count']}")
    print(
        "Available adjacent generators: "
        f"sigma_{candidate['sigma_range'][0]}..sigma_{candidate['sigma_range'][1]}"
    )
    print(f"Braid count: {candidate['braid_count']}")
    print(f"Average gate fidelity: {result['average_gate_fidelity']:.12f}%")
    print(f"Process fidelity: {result['process_fidelity']:.12f}%")
    print(f"Maximum leakage: {result['maximum_leakage']:.12e}")
    print(f"Matrix error: {candidate['matrix_error']:.12e}")
    print(f"Anyon order restored: {result['order_restored']}")
    print(f"Target reached: {candidate['target_reached']}")
    if candidate["replay_error"] is not None:
        print(f"F/R replay error: {candidate['replay_error']:.12e}")
    print("Braid computational matrix (000..111), global phase aligned:")
    with np.printoptions(precision=8, suppress=True, linewidth=200):
        print(candidate["phase_aligned_braid_matrix"])
    if print_sequence:
        print("Signed braid sequence on twelve anyons:")
        print(candidate["braid_sequence"].tolist())


def main():
    candidate = search_ccx(fidelity=99.0, max_leakage=None, verify=False)
    print_result(candidate)


if __name__ == "__main__":
    main()
