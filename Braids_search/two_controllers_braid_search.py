"""Compose and evaluate three-qubit doubly controlled braids.

The single-qubit H, T, X and S words and the controlled gates come from the
final ``braid_sequences_SK.json`` gate library. This module currently treats
that library as read-only and keeps all newly composed results in memory.

CCS is composed in memory from the saved T and CT braids. CCT additionally
synthesizes sqrt(T) and controlled-sqrt(T) in memory with the existing SK
helpers. Neither result is written to the JSON library.

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


BRAIDS_SEARCH_DIR = Path(__file__).resolve().parent
SK_SEQUENCE_FILE = BRAIDS_SEARCH_DIR / "braid_sequences_SK.json"

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


def load_primitives(include_ccs=False):
    """Load required components from the final SK gate library."""
    if not isinstance(include_ccs, bool):
        raise TypeError("include_ccs must be a boolean.")

    library = _load_json(SK_SEQUENCE_FILE)
    gates = ("H", "T", "X", "S", "CX")
    if include_ccs:
        gates += ("CT",)

    return {
        gate: _validated_word(
            library.get(gate),
            gate,
            SK_SEQUENCE_FILE,
        )
        for gate in gates
    }

def build_cc_pauli_braid(gate="X", primitives=None, reduce=True):
    gate = gate.upper()
    if gate not in {"X", "Y", "Z"}:
        raise ValueError("gate must be X, Y, or Z.")

    if primitives is None:
        primitives = load_primitives()

    if gate == "X":
        return build_ccx_braid(primitives, reduce=reduce)

    # Build the unreduced CCX first so reduction happens over the
    # complete CCY/CCZ braid, including component boundaries.
    ccx = build_ccx_braid(primitives, reduce=False)

    local_gate = {
        "Y": "S",
        "Z": "H",
    }[gate]

    target_after = _local_word(primitives[local_gate], 2)
    target_before = _inverse_word(target_after)

    unreduced = (
        target_before
        + tuple(ccx["sequence"])
        + target_after
    )
    sequence = _reduce_word(unreduced) if reduce else unreduced

    final_order = _endpoint_order(sequence)
    if final_order != tuple(range(1, ANYON_COUNT + 1)):
        raise RuntimeError(
            f"The composed CC{gate} braid does not restore all anyon identities: "
            f"{final_order}."
        )

    ccx.update({
        "sequence": sequence,
        "unreduced_braid_count": len(unreduced),
        "braid_count": len(sequence),
        "final_anyon_order": final_order,
        "order_restored": True,
        "basis_change": local_gate,
    })
    return ccx

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


def _adjacent_controlled_word(word, gate, control, target):
    """Embed a saved left-to-right controlled gate in adjacent blocks."""
    if (control, target) not in ((0, 1), (1, 2)):
        raise ValueError(f"Direct {gate} supports only (0,1) or (1,2).")
    if any(abs(index) > 7 for index in word):
        raise ValueError(f"The saved {gate} is not an eight-anyon braid word.")
    return _shift_word(word, ANYONS_PER_QUBIT * control)


def _adjacent_cx_word(cx_word, control, target):
    """Compatibility wrapper for embedding the saved adjacent CX word."""
    return _adjacent_controlled_word(cx_word, "CX", control, target)


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


def _controlled_phase_matrix(angle, first, second):
    """Return a three-qubit phase on states where both selected bits are one."""
    result = np.eye(8, dtype=complex)
    phase = np.exp(1j * angle)
    for index in range(8):
        bits = format(index, "03b")
        if bits[first] == bits[second] == "1":
            result[index, index] = phase
    return result


def _cc_phase_matrix(angle):
    """Return diag(1,...,1,exp(i*angle)) in the 000..111 basis."""
    result = np.eye(8, dtype=complex)
    result[-1, -1] = np.exp(1j * angle)
    return result


def _phase_matrix(angle):
    """Return the one-qubit phase gate diag(1, exp(i*angle))."""
    return np.diag((1.0, np.exp(1j * angle))).astype(complex)


def _controlled_phase_target(angle):
    """Return diag(I, P(angle)) in the 00,01,10,11 basis."""
    result = np.eye(4, dtype=complex)
    result[2:, 2:] = _phase_matrix(angle)
    return result


def _assert_ideal_ccs_decomposition():
    """Verify the T/CCX/CT decomposition of CCS before using physical words."""
    t2 = _single_qubit_matrix(math_constant.GATE_MATRICES["T"], 2)
    ccx = _ccx_matrix()
    ct01 = _controlled_phase_matrix(np.pi / 4, 0, 1)
    operations = (t2, ccx, t2.conj().T, ccx, ct01)

    compiled = np.eye(8, dtype=complex)
    for operation in operations:
        compiled = operation @ compiled

    target = _cc_phase_matrix(np.pi / 2)
    overlap = np.trace(target.conj().T @ compiled)
    phase = overlap / abs(overlap) if abs(overlap) else 1.0
    if not np.allclose(compiled, phase * target, atol=1e-12, rtol=0):
        raise RuntimeError("The selected T/CCX/CT decomposition is not CCS.")


def _assert_ideal_cct_decomposition():
    """Verify the sqrt(T)/CCX/Csqrt(T) decomposition of CCT."""
    sqrt_t2 = _single_qubit_matrix(_phase_matrix(np.pi / 8), 2)
    ccx = _ccx_matrix()
    controlled_sqrt_t01 = _controlled_phase_matrix(np.pi / 8, 0, 1)
    operations = (
        sqrt_t2,
        ccx,
        sqrt_t2.conj().T,
        ccx,
        controlled_sqrt_t01,
    )

    compiled = np.eye(8, dtype=complex)
    for operation in operations:
        compiled = operation @ compiled

    target = _cc_phase_matrix(np.pi / 4)
    overlap = np.trace(target.conj().T @ compiled)
    phase = overlap / abs(overlap) if abs(overlap) else 1.0
    if not np.allclose(compiled, phase * target, atol=1e-12, rtol=0):
        raise RuntimeError(
            "The selected sqrt(T)/CCX/Csqrt(T) decomposition is not CCT."
        )


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
            "controlled_x": str(SK_SEQUENCE_FILE),
        },
        "endpoint_correction": "X(q0)^2",
    }


def build_ccs_braid(primitives=None, reduce=True):
    """Compose CCS from saved T and CT words and the existing CCX braid."""
    _assert_ideal_ccs_decomposition()
    if primitives is None:
        primitives = load_primitives(include_ccs=True)

    t2 = _local_word(primitives["T"], 2)
    tdg2 = _inverse_word(t2)
    ccx = tuple(build_ccx_braid(primitives, reduce=False)["sequence"])
    ccx_inverse = _inverse_word(ccx)
    ct01 = _adjacent_controlled_word(primitives["CT"], "CT", 0, 1)

    components = (
        ("T(q2)", t2),
        ("CCX(q0,q1,q2)", ccx),
        ("Tdg(q2)", tdg2),
        ("CCXdg(q0,q1,q2)", ccx_inverse),
        ("CT(q0,q1)", ct01),
    )
    unreduced = tuple(index for _, word in components for index in word)
    sequence = _reduce_word(unreduced) if reduce else unreduced
    final_order = _endpoint_order(sequence)
    if final_order != tuple(range(1, ANYON_COUNT + 1)):
        raise RuntimeError(
            "The composed CCS braid does not restore all twelve anyon identities: "
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
            "single_qubit_t": str(SK_SEQUENCE_FILE),
            "controlled_t": str(SK_SEQUENCE_FILE),
            "controlled_controlled_x": "composed in this module",
        },
        "phase_decomposition": "T(q2), CCX, Tdg(q2), CCXdg, CT(q0,q1)",
    }


def build_cct_braid(
    sqrt_t_word,
    controlled_sqrt_t_word,
    primitives=None,
    reduce=True,
):
    """Compose CCT from in-memory sqrt(T), controlled-sqrt(T), and CCX."""
    _assert_ideal_cct_decomposition()
    if primitives is None:
        primitives = load_primitives()

    sqrt_t2 = _local_word(sqrt_t_word, 2)
    sqrt_t_dg2 = _inverse_word(sqrt_t2)
    ccx = tuple(build_ccx_braid(primitives, reduce=False)["sequence"])
    ccx_inverse = _inverse_word(ccx)
    controlled_sqrt_t01 = _adjacent_controlled_word(
        controlled_sqrt_t_word,
        "Csqrt(T)",
        0,
        1,
    )

    components = (
        ("sqrt(T)(q2)", sqrt_t2),
        ("CCX(q0,q1,q2)", ccx),
        ("sqrt(T)dg(q2)", sqrt_t_dg2),
        ("CCXdg(q0,q1,q2)", ccx_inverse),
        ("Csqrt(T)(q0,q1)", controlled_sqrt_t01),
    )
    unreduced = tuple(index for _, word in components for index in word)
    sequence = _reduce_word(unreduced) if reduce else unreduced
    final_order = _endpoint_order(sequence)
    if final_order != tuple(range(1, ANYON_COUNT + 1)):
        raise RuntimeError(
            "The composed CCT braid does not restore all twelve anyon identities: "
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
            "controlled_x": str(SK_SEQUENCE_FILE),
            "controlled_controlled_x": "composed in this module",
        },
        "local_phase_synthesis": "in-memory Solovay-Kitaev pure-braid net",
        "phase_decomposition": (
            "sqrt(T)(q2), CCX, sqrt(T)dg(q2), CCXdg, "
            "Csqrt(T)(q0,q1)"
        ),
    }


def _validate_fidelity(fidelity):
    if isinstance(fidelity, (bool, np.bool_)) or not isinstance(
        fidelity, (int, float, np.integer, np.floating)
    ):
        raise TypeError("fidelity must be a percentage.")
    if not np.isfinite(fidelity) or not 0 < fidelity <= 100:
        raise ValueError("fidelity must be in (0, 100].")


def _validate_search_depth(value, name):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer.")
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")


def _compile_pure_phase_candidates(
    angle,
    max_refinements,
    local_engine,
    net,
    sk,
    one_controlled,
):
    """Compile an in-memory phase while preserving local endpoint order."""
    target = _phase_matrix(angle)
    candidates = []
    for level in range(max_refinements + 1):
        word, _ = one_controlled._compile_local_correction(
            target,
            level,
            net,
            sk,
        )
        matrix, order = local_engine.run_sequence(word)
        if order != local_engine.initial_order:
            raise RuntimeError(
                "The pure local phase compiler changed the endpoint permutation."
            )
        candidates.append({
            "sequence": tuple(word),
            "matrix": matrix,
            "refinement": level,
            "fidelity": one_controlled._average_gate_fidelity(matrix, target),
        })
    return candidates


def _build_controlled_sqrt_t_candidates(
    cx_word,
    half_phase_candidates,
    one_controlled,
):
    """Build controlled-sqrt(T) from saved CX and synthesized pi/16 phases."""
    engine = braid_searching(2, "I", target=1, controllers=(0,))
    target = _controlled_phase_target(np.pi / 8)
    cx_word = tuple(cx_word)
    cx_inverse = _inverse_word(cx_word)
    candidates = []

    for half_phase in half_phase_candidates:
        control_phase = half_phase["sequence"]
        target_phase = _shift_word(control_phase, ANYONS_PER_QUBIT)
        target_inverse_phase = _inverse_word(target_phase)
        sequence = _reduce_word(
            cx_word
            + target_inverse_phase
            + cx_inverse
            + control_phase
            + target_phase
        )
        result = one_controlled._evaluate_controlled(engine, sequence, target)
        if not result["order_restored"]:
            raise RuntimeError(
                "The synthesized controlled-sqrt(T) changed endpoint order."
            )
        candidates.append({
            "sequence": sequence,
            "result": result,
            "half_phase_refinement": half_phase["refinement"],
            "half_phase_fidelity": half_phase["fidelity"],
        })
    return candidates


def search_cc_pauli(gate="X", fidelity=99.0, max_leakage=None, verify=False):
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
    gate = gate.upper()
    if gate not in {"X", "Y", "Z"}:
        raise ValueError("gate must be X, Y, or Z.")

    candidate = build_cc_pauli_braid(gate)
    engine = braid_searching(
        qubits_num=3,
        gate=gate,
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
        "target_kind": f"CC{gate}",
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


def search_ccs(fidelity=99.0, max_leakage=None, verify=False):
    """Compose and score CCS without saving it to the SK JSON library."""
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

    candidate = build_ccs_braid()
    engine = braid_searching(
        qubits_num=3,
        gate="S",
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
        "target_kind": "CCS",
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


def search_cct(
    fidelity=99.0,
    max_leakage=None,
    verify=False,
    local_net_depth=7,
    max_local_refinements=2,
):
    """Synthesize and score CCT entirely in memory without changing JSON."""
    _validate_fidelity(fidelity)
    if not isinstance(verify, bool):
        raise TypeError("verify must be a boolean.")
    _validate_search_depth(local_net_depth, "local_net_depth")
    _validate_search_depth(max_local_refinements, "max_local_refinements")
    if max_leakage is None:
        max_leakage = 1 - fidelity / 100
    if isinstance(max_leakage, (bool, np.bool_)) or not isinstance(
        max_leakage, (int, float, np.integer, np.floating)
    ):
        raise TypeError("max_leakage must be a probability.")
    if not np.isfinite(max_leakage) or not 0 <= max_leakage <= 1:
        raise ValueError("max_leakage must be in [0, 1].")

    import solovay_kitaev as sk
    import one_controlled_braid_search as one_controlled

    primitives = load_primitives()
    local_engine = braid_searching(1, "I", target=0)
    net = sk._build_macro_mitm_net(
        local_engine,
        local_net_depth,
        {
            "sigma1_squared": {"sequence": (1, 1)},
            "sigma2_squared": {"sequence": (2, 2)},
        },
    )
    sqrt_t_candidates = _compile_pure_phase_candidates(
        np.pi / 8,
        max_local_refinements,
        local_engine,
        net,
        sk,
        one_controlled,
    )
    pi_over_16_candidates = _compile_pure_phase_candidates(
        np.pi / 16,
        max_local_refinements,
        local_engine,
        net,
        sk,
        one_controlled,
    )
    controlled_sqrt_t_candidates = _build_controlled_sqrt_t_candidates(
        primitives["CX"],
        pi_over_16_candidates,
        one_controlled,
    )

    engine = braid_searching(
        qubits_num=3,
        gate="T",
        target=2,
        controllers=(0, 1),
    )
    best = None
    history = []
    for sqrt_t in sqrt_t_candidates:
        for controlled_sqrt_t in controlled_sqrt_t_candidates:
            candidate = build_cct_braid(
                sqrt_t["sequence"],
                controlled_sqrt_t["sequence"],
                primitives=primitives,
            )
            result = engine.evaluate(candidate["sequence"])
            target = engine.target_matrix
            matrix = result["computational_matrix"]
            overlap = np.trace(target.conj().T @ matrix)
            global_phase = overlap / abs(overlap) if abs(overlap) else 1.0
            aligned_matrix = matrix / global_phase
            matrix_error = float(np.linalg.norm(aligned_matrix - target, ord=2))
            candidate.update({
                "target_kind": "CCT",
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
                "sqrt_t_refinement": sqrt_t["refinement"],
                "sqrt_t_fidelity": sqrt_t["fidelity"],
                "controlled_sqrt_t_refinement": (
                    controlled_sqrt_t["half_phase_refinement"]
                ),
                "controlled_sqrt_t_fidelity": controlled_sqrt_t[
                    "result"
                ]["average_gate_fidelity"],
                "target_reached": (
                    result["average_gate_fidelity"] >= fidelity
                    and result["maximum_leakage"] <= max_leakage
                    and result["order_restored"]
                ),
                "replay_error": None,
            })
            history.append({
                "sqrt_t_refinement": sqrt_t["refinement"],
                "controlled_sqrt_t_refinement": controlled_sqrt_t[
                    "half_phase_refinement"
                ],
                "braid_count": candidate["braid_count"],
                "average_gate_fidelity": result["average_gate_fidelity"],
                "maximum_leakage": result["maximum_leakage"],
            })
            if best is None or (
                result["average_gate_fidelity"]
                > best["result"]["average_gate_fidelity"]
            ):
                best = candidate

    best["history"] = history
    if verify:
        best["replay_error"] = engine.verify_with_qitker(best["sequence"])
    return best


def print_result(candidate, print_sequence=True):
    result = candidate["result"]
    print(f"{candidate['target_kind']}: controls=q[0],q[1], target=q[2]")   
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

def search_ccx(**kwargs):
    return search_cc_pauli("X", **kwargs)


def search_ccy(**kwargs):
    return search_cc_pauli("Y", **kwargs)


def search_ccz(**kwargs):
    return search_cc_pauli("Z", **kwargs)

def _save_two_controlled_gate(candidate):
    """Save one verified three-qubit gate in braid_sequences_SK.json."""
    if not candidate["target_reached"]:
        raise RuntimeError(
            f"{candidate['target_kind']} did not reach the requested target; "
            "result was not saved."
        )

    if candidate["replay_error"] is None:
        raise RuntimeError(
            f"{candidate['target_kind']} was not verified through F/R; "
            "result was not saved."
        )


    import solovay_kitaev as sk

    seed_record = {
        "type": "controlled_qubit",
        "basis": "fibonacci_12_anyons",
    }

    sk._save_search_result(
        candidate["target_kind"],
        seed_record,
        candidate,
    )

def main():
    for search in (
        search_ccs,
        search_cct,
    ):
        candidate = search(
            fidelity=99.0,
            max_leakage=None,
            verify=True,
        )

        _save_two_controlled_gate(candidate)


        print_result(candidate, print_sequence=False)
        print()


if __name__ == "__main__":
    main()
