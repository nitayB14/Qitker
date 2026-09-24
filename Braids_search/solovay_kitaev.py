"""Solovay--Kitaev refinement of the saved one-qubit Fibonacci braids.

The JSON braid for each gate is the starting approximation. Refinement uses
compiled physical sigma matrices from ``search_engine``; the selected answer
is then replayed through Qitker's F/R engine for physical verification.
"""

import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from scipy.spatial import cKDTree

from search_engine import braid_searching


BRAIDS_SEARCH_DIR = Path(__file__).resolve().parent

SEQUENCE_FILE = BRAIDS_SEARCH_DIR / "braid_sequences_primitive.json"
SK_SEQUENCE_FILE = BRAIDS_SEARCH_DIR / "braid_sequences_SK.json"


PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = (PAULI_X, PAULI_Y, PAULI_Z)


def _load_saved_sequences():
    """Load the existing one-qubit approximations used as search seeds."""
    with SEQUENCE_FILE.open(encoding="utf-8") as source:
        return json.load(source)


def _save_search_result(gate, seed_record, search_result):
    """Update one verified gate in the SK JSON, preserving the other gates.

    Fidelity/error are percentages; leakage values are probabilities (0--1).
    The source JSON remains the seed library. Only SK_SEQUENCE_FILE is updated.
    """
    if SK_SEQUENCE_FILE.exists():
        contents = SK_SEQUENCE_FILE.read_text(encoding="utf-8-sig")
        saved = json.loads(contents) if contents.strip() else {}
    else:
        saved = {}
    if not isinstance(saved, dict):
        raise ValueError("The SK sequence file must contain a JSON object.")

    result = search_result["result"]
    sequence = search_result["sequence"]
    # Keep descriptive/custom fields, but replace measured values from this run.
    record = dict(seed_record)
    record.update(saved.get(gate, {}))
    record.update({
        "sequence": list(sequence),
        "braid count": len(sequence),
        "gate fidelity": result["average_gate_fidelity"],
        "gate error": 100.0 - result["average_gate_fidelity"],
        "process fidelity": result["process_fidelity"],
        "average leakage": result["average_leakage"],
        "maximum leakage": result["maximum_leakage"],
        "leakage by input": result["leakage_by_input"],
        "final anyon order": list(result["final_anyon_order"]),
        "order restored": result["order_restored"],
        "F/R replay error": search_result["replay_error"],
        "target reached": search_result["target_reached"],
    })
    saved[gate] = record
    # Serialize before touching disk. NaN/Infinity must not enter the JSON.
    contents = json.dumps(saved, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    # Keep each integer braid sequence on one line; retain indentation elsewhere.
    contents = re.sub(
        r'(?m)^([ \t]*"sequence": )(\[[-0-9,\s]*\])',
        lambda match: match[1] + json.dumps(json.loads(match[2]), allow_nan=False),
        contents,
    )

    # Write beside the destination, then replace it only when the JSON is complete.
    # A failed write leaves the previously saved results intact.
    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=SK_SEQUENCE_FILE.parent,
            prefix=SK_SEQUENCE_FILE.name + ".", suffix=".tmp", delete=False,
        ) as destination:
            temporary_path = Path(destination.name)
            destination.write(contents)
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary_path, SK_SEQUENCE_FILE)  # The actual JSON replacement.
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _reduce_word(sequence):
    """Remove adjacent sigma_i sigma_i^-1 pairs without changing the braid."""
    reduced = []
    for index in sequence:
        if reduced and reduced[-1] == -index:
            reduced.pop()
        else:
            reduced.append(index)
    return tuple(reduced)


def _inverse_word(sequence):
    """Return the chronological word which applies the inverse operation."""
    return tuple(-index for index in reversed(sequence))


def _as_su2(matrix):
    """Remove global phase and choose the SU(2) representative near identity."""
    determinant = np.linalg.det(matrix)
    result = matrix * np.exp(-0.5j * np.angle(determinant))
    if np.real(np.trace(result)) < 0:
        result = -result
    return result


def _rotation(axis, angle):
    """Return exp(-i * angle * axis.sigma), where axis is a unit 3-vector."""
    pauli_axis = sum(component * matrix for component, matrix in zip(axis, PAULI))
    return np.cos(angle) * np.eye(2) - 1j * np.sin(angle) * pauli_axis


def _axis_angle(matrix):
    """Read U = cos(angle) I - i sin(angle) axis.sigma from an SU(2) matrix."""
    matrix = _as_su2(matrix)
    scalar = float(np.clip(np.real(np.trace(matrix)) / 2, -1.0, 1.0))
    vector = np.array(
        [np.real(0.5j * np.trace(pauli @ matrix)) for pauli in PAULI]
    )
    magnitude = float(np.linalg.norm(vector))
    if magnitude < 1e-14:
        return np.array((0.0, 0.0, 1.0)), 0.0
    return vector / magnitude, float(np.arctan2(magnitude, scalar))


def _rotate_axis(source_axis, target_axis):
    """Return R satisfying R(source.sigma)R^dagger = target.sigma."""
    dot = float(np.clip(np.dot(source_axis, target_axis), -1.0, 1.0))
    if dot > 1 - 1e-12:
        return np.eye(2, dtype=complex)
    if dot < -1 + 1e-12:
        trial = np.array((1.0, 0.0, 0.0))
        if abs(source_axis[0]) > 0.9:
            trial = np.array((0.0, 1.0, 0.0))
        perpendicular = np.cross(source_axis, trial)
        return _rotation(perpendicular / np.linalg.norm(perpendicular), np.pi / 2)
    source_pauli = sum(value * pauli for value, pauli in zip(source_axis, PAULI))
    target_pauli = sum(value * pauli for value, pauli in zip(target_axis, PAULI))
    return (np.eye(2) + target_pauli @ source_pauli) / np.sqrt(2 * (1 + dot))


def _group_commutator_decomposition(delta):
    """Find V,W with V W V^-1 W^-1 equal to near-identity ``delta``."""
    target_axis, target_angle = _axis_angle(delta)
    if target_angle < 1e-14:
        identity = np.eye(2, dtype=complex)
        return identity, identity

    # For V0=Rx(phi), W0=Ry(phi): cos(angle) = 1 - 2 sin(phi)^4.
    phi = np.arcsin(np.sqrt(np.sin(target_angle / 2)))
    v0 = _rotation(np.array((1.0, 0.0, 0.0)), phi)
    w0 = _rotation(np.array((0.0, 1.0, 0.0)), phi)
    commutator = v0 @ w0 @ v0.conj().T @ w0.conj().T
    commutator_axis, _ = _axis_angle(commutator)
    conjugator = _rotate_axis(commutator_axis, target_axis)
    return conjugator @ v0 @ conjugator.conj().T, conjugator @ w0 @ conjugator.conj().T


def _build_epsilon_net(engine, max_depth, saved_sequences):
    """Build the SK base net from the saved physical one-qubit braids.

    Each JSON gate and its inverse is an alphabet symbol.  This is far denser
    than enumerating individual sigma operations at the same depth, while all
    net points still remain real Fibonacci braid words.
    """
    if max_depth < 0:
        raise ValueError("net_depth must be non-negative.")
    units = []
    for gate, record in saved_sequences.items():
        word = _reduce_word(record["sequence"])
        matrix = _as_su2(engine.run_sequence(word)[0])
        forward = (gate, 1)
        backward = (gate, -1)
        units.append((forward, backward, word, matrix))
        units.append((backward, forward, _inverse_word(word), matrix.conj().T))

    words = [()]
    matrices = [np.eye(2, dtype=complex)]
    frontier = [((), np.eye(2, dtype=complex), None)]
    for _ in range(max_depth):
        next_frontier = []
        for word, matrix, forbidden in frontier:
            for label, inverse_label, unit_word, unit_matrix in units:
                if label == forbidden:
                    continue
                next_word = word + unit_word
                next_matrix = unit_matrix @ matrix
                words.append(next_word)
                matrices.append(_as_su2(next_matrix))
                next_frontier.append((next_word, next_matrix, inverse_label))
        frontier = next_frontier
    return tuple(words), np.asarray(matrices)


def _nearest_net_word(target, words, matrices):
    """Find the net matrix with maximum global-phase-invariant overlap."""
    overlaps = np.abs(np.einsum("nij,ji->n", matrices.conj(), target))
    best = int(np.argmax(overlaps))
    return words[best], matrices[best]


def _quaternion(matrix):
    """Map an SU(2) matrix to its canonical unit quaternion coordinates."""
    axis, angle = _axis_angle(matrix)
    return np.concatenate(([np.cos(angle)], np.sin(angle) * axis))


def _build_macro_mitm_net(engine, max_depth, saved_sequences):
    """Build a dense MITM net whose symbols are the saved JSON gate braids."""
    units = {}
    for gate, record in saved_sequences.items():
        word = _reduce_word(record["sequence"])
        matrix = _as_su2(engine.run_sequence(word)[0])
        units[(gate, 1)] = (word, matrix, (gate, -1))
        units[(gate, -1)] = (_inverse_word(word), matrix.conj().T, (gate, 1))

    token_words = [()]
    matrices = [np.eye(2, dtype=complex)]
    frontier = [((), np.eye(2, dtype=complex), None)]
    for _ in range(max_depth):
        next_frontier = []
        for tokens, matrix, forbidden in frontier:
            for token, (_, unit_matrix, inverse_token) in units.items():
                if token == forbidden:
                    continue
                next_tokens = tokens + (token,)
                next_matrix = unit_matrix @ matrix
                token_words.append(next_tokens)
                matrices.append(_as_su2(next_matrix))
                next_frontier.append((next_tokens, next_matrix, inverse_token))
        frontier = next_frontier
    matrices = np.asarray(matrices)
    quaternions = np.asarray([_quaternion(matrix) for matrix in matrices])
    return tuple(token_words), matrices, cKDTree(quaternions), units


def _macro_mitm_approximate(target, token_words, matrices, tree, units):
    """Compile a target from two short sequences of saved JSON braid blocks."""
    desired_suffixes = target @ matrices.conj().transpose(0, 2, 1)
    desired_quaternions = np.asarray(
        [_quaternion(matrix) for matrix in desired_suffixes]
    )
    distances, suffix_indices = tree.query(desired_quaternions)
    prefix_index = int(np.argmin(distances))
    suffix_index = int(suffix_indices[prefix_index])
    tokens = token_words[prefix_index] + token_words[suffix_index]
    word = _reduce_word(
        index for token in tokens for index in units[token][0]
    )
    matrix = _as_su2(matrices[suffix_index] @ matrices[prefix_index])
    return word, matrix


def _solovay_kitaev(target, level, words, matrices):
    """Recursively approximate a one-qubit SU(2) target by a braid word."""
    target = _as_su2(target)
    if level == 0:
        return _nearest_net_word(target, words, matrices)

    coarse_word, coarse_matrix = _solovay_kitaev(target, level - 1, words, matrices)
    residual = _as_su2(target @ coarse_matrix.conj().T)
    exact_v, exact_w = _group_commutator_decomposition(residual)
    v_word, v_matrix = _solovay_kitaev(exact_v, level - 1, words, matrices)
    w_word, w_matrix = _solovay_kitaev(exact_w, level - 1, words, matrices)

    # Chronological [W^-1, V^-1, W, V] has matrix V W V^-1 W^-1.
    correction_word = (
        _inverse_word(w_word)
        + _inverse_word(v_word)
        + w_word
        + v_word
    )
    correction_matrix = v_matrix @ w_matrix @ v_matrix.conj().T @ w_matrix.conj().T
    return (
        _reduce_word(coarse_word + correction_word),
        _as_su2(correction_matrix @ coarse_matrix),
    )


def print_result(result, sequence):
    """Print the metrics needed to judge a candidate braid."""
    print(f"  length: {len(sequence)}")
    print(f"  average gate fidelity: {result['average_gate_fidelity']:.12f}%")
    print(f"  process fidelity: {result['process_fidelity']:.12f}%")
    print(f"  average leakage: {result['average_leakage']:.12e}")
    print(f"  maximum leakage: {result['maximum_leakage']:.12e}")
    print(f"  anyon order restored: {result['order_restored']}")


def check_from_json(gate="X"):
    """Evaluate, but do not improve, a saved one-qubit braid."""
    saved_sequences = _load_saved_sequences()
    gate = gate.upper()
    sequence = tuple(saved_sequences[gate]["sequence"])
    engine = braid_searching(qubits_num=1, gate=gate, target=0)
    result = engine.evaluate(sequence)
    print(f"Saved {gate} braid")
    print_result(result, sequence)
    return result


def search_better_sequence(
    gates=None,
    target_fidelity=99.99999,
    recursion_depth=3,
    net_depth=4,
    mitm_depth=5,
    max_rounds=2,
):
    """Refine saved one-qubit braids toward ``target_fidelity`` percent.

    ``gates`` may be one name or an iterable of JSON gate names. The returned
    mapping contains the selected word, metrics, and final independent F/R
    replay error. A candidate is kept only if it improves its JSON seed.
    Each gate's final verified result is saved to SK_SEQUENCE_FILE, even if
    the requested fidelity was not reached (recorded as "target reached").
    """
    if not 0 < target_fidelity <= 100:
        raise ValueError("target_fidelity must be in the interval (0, 100].")
    if recursion_depth < 0 or net_depth < 0 or mitm_depth < 0 or max_rounds < 0:
        raise ValueError("Search depths and max_rounds must be non-negative.")

    saved_sequences = _load_saved_sequences()
    single_qubit_sequences = {
        gate: record
        for gate, record in saved_sequences.items()
        if isinstance(record, dict) and record.get("type") == "single_qubit"
    }
    if gates is None:
        gates = tuple(single_qubit_sequences)
    elif isinstance(gates, str):
        gates = (gates.upper(),)
    else:
        gates = tuple(gate.upper() for gate in gates)

    results = {}
    for gate in gates:
        if gate not in single_qubit_sequences:
            raise ValueError(f"No saved braid is available for gate {gate!r}.")
        engine = braid_searching(qubits_num=1, gate=gate, target=0)
        net_words, net_matrices = _build_epsilon_net(
            engine, net_depth, single_qubit_sequences
        )
        mitm_words, mitm_matrices, mitm_tree, mitm_units = _build_macro_mitm_net(
            engine, mitm_depth, single_qubit_sequences
        )
        sequence = _reduce_word(single_qubit_sequences[gate]["sequence"])
        best = engine.evaluate(sequence)
        target_matrix = _as_su2(engine.target_matrix)

        print(f"\n{gate}: JSON seed")
        print_result(best, sequence)
        for round_number in range(1, max_rounds + 1):
            if best["average_gate_fidelity"] >= target_fidelity:
                break
            current_matrix = engine.run_sequence(sequence)[0]
            residual = _as_su2(target_matrix @ current_matrix.conj().T)
            # The dense MITM net is the level-zero SK compiler. The ordinary
            # recursive correction is also considered; only the best physical
            # candidate is kept.
            mitm_correction, _ = _macro_mitm_approximate(
                residual, mitm_words, mitm_matrices, mitm_tree, mitm_units
            )
            sk_correction, _ = _solovay_kitaev(
                residual, recursion_depth, net_words, net_matrices
            )
            candidates = (
                _reduce_word(sequence + mitm_correction),
                _reduce_word(sequence + sk_correction),
            )
            candidate = max(
                candidates,
                key=lambda word: engine.evaluate(word)["average_gate_fidelity"],
            )
            candidate_result = engine.evaluate(candidate)
            if candidate_result["average_gate_fidelity"] <= best["average_gate_fidelity"]:
                print(f"  round {round_number}: no improvement; keeping current sequence.")
                break
            sequence, best = candidate, candidate_result
            print(f"  round {round_number}: improved")
            print_result(best, sequence)

        replay_error = engine.verify_with_qitker(sequence)
        results[gate] = {
            "sequence": sequence,
            "result": best,
            "replay_error": replay_error,
            "target_reached": best["average_gate_fidelity"] >= target_fidelity,
        }
        # Save only after physical verification succeeds; checkpoint every gate.
        
        
        _save_search_result(gate, saved_sequences[gate], results[gate])
        print(f"  F/R replay error: {replay_error:.3e}")
        print(f"  saved to: {SK_SEQUENCE_FILE}")
        print(f"  final sequence: {sequence}")
    return results


def main():
    print("start searching for braid...")
    search_better_sequence()


if __name__ == "__main__":
    main()
