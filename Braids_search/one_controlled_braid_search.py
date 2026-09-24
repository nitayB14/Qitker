"""Known-seed controlled braids and fidelity-driven weave generation.

Carnahan, Zeuch & Bonesteel, PRA 93, 052328 (2016), Secs. III--V,
Figs. 2/5/6: https://arxiv.org/abs/1511.00719

Qubit 0 controls qubit 1. In the original controlled-R^2 experiment the
three objects are the control pair (3, 4), target anyon 5, and target
anyon 6; anyons 1, 2, 7, 8 are spectators. The off-diagonal construction
below uses a different insertion. Composite crossings are expanded into
physical sigma crossings without twisting the control pair internally.

All words are chronological, with signed, one-based positional indices.
F tokens below are basis changes used to derive a weave, not physical gates.
generate_exchange_weave(fidelity=99.99) selects a diagonal exchange weave.
generate_offdiagonal_weave(fidelity=99.99) selects a returning phase weave
whose matrix approaches an off-diagonal unitary, using FR^2F and a custom
sign-modified recurrence.
generate_controlled_weave(fidelity=99.99) inserts the control pair into the
target using a four-anyon construction, applies that phase weave, then
extracts it. Its target is a controlled pi rotation,
locally equivalent to each controlled Pauli gate.

generate_controlled_pauli(gate, fidelity=99.99) compiles the required local
corrections and measures the complete physical sigma sequence against CX, CY,
or CZ itself. Its target_reached flag also requires the requested worst-case
leakage bound and restored order. generate_cnot remains as a compatibility
wrapper.

generate_controlled_phase(gate, fidelity=99.99) constructs CS or CT from two
verified CX braids and locally compiled half-angle phase rotations, then scores
the complete physical sequence against the requested controlled phase gate.

Fidelity arguments and reported average gate fidelities are percentages.
Leakage values are probabilities. The generation helpers return results in
memory; ``main`` saves verified controlled gates in braid_sequences_SK.json.
"""

import sys
from pathlib import Path
import time

import numpy as np

# The sibling search tools use script-style imports. Support both direct
# execution and `from Braids_search.controlled_braid_search import generate_cnot`.
SEARCH_DIRECTORY = str(Path(__file__).resolve().parent)
if SEARCH_DIRECTORY not in sys.path:
    sys.path.insert(0, SEARCH_DIRECTORY)
from search_engine import braid_searching
from qitker.QuantumMath.constant import math_constant


def _inverse_word(sequence):
    return tuple(-index for index in reversed(sequence))


def _validate_iterations(iterations):
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise TypeError("iterations must be an integer.")
    if iterations < 0:
        raise ValueError("iterations must be nonnegative.")


def _validate_fidelity(fidelity):
    if isinstance(fidelity, (bool, np.bool_)) or not isinstance(
        fidelity, (int, float, np.integer, np.floating)
    ):
        raise TypeError("fidelity must be a percentage, for example 99.99.")
    if not np.isfinite(fidelity) or not 0 < fidelity < 100:
        raise ValueError("fidelity must be strictly between 0 and 100 percent.")


def _average_gate_fidelity(matrix, target):
    """Unconditioned fidelity in percent; include any loss of amplitude."""
    d = target.shape[0]
    overlap = np.trace(target.conj().T @ matrix)
    return float(100 * (
        np.vdot(matrix, matrix).real + abs(overlap) ** 2
    ) / (d * (d + 1)))


def _exchange_tokens(iterations):
    """Apply Eq. (5) to FR^3F, retaining the unreduced F/R expression."""
    _validate_iterations(iterations)
    tokens = (("F", 0), ("R", 3), ("F", 0))
    for _ in range(iterations):
        inverse = tuple(
            (kind, -power) for kind, power in reversed(tokens)
        )
        tokens = (
            tokens + (("R", 1),) + inverse + (("R", 3),)
            + tokens + (("R", 3),) + inverse + (("R", 1),) + tokens
        )
    return tokens


def _tokens_to_weave(tokens):
    """Walk Fig. 2's hexagon and return a physical three-object word.

    Vertices 1/2 put the weft on the left, 3/4 in the middle, and 5/6
    on the right. F edges are 1--2, 3--4, 5--6. R edges are 2--3 and
    4--5. The 1--6 edge is R': move around BOTH warps in the opposite
    braid sense (Eq. (9)); replacing it with an ordinary R is incorrect.
    """
    vertex = 1
    word = []
    f_edges = {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5}
    for kind, power in tokens:
        if kind == "F":
            vertex = f_edges[vertex]
            continue
        if kind != "R":
            raise ValueError("Unknown F/R token.")
        sign = 1 if power > 0 else -1
        for _ in range(abs(power)):
            if vertex in (2, 3):
                word.append(sign)
                vertex = 5 - vertex
            elif vertex in (4, 5):
                word.append(2 * sign)
                vertex = 9 - vertex
            elif vertex == 1:
                word.extend((-sign, -2 * sign))
                vertex = 6
            else:
                word.extend((-2 * sign, -sign))
                vertex = 1
    return tuple(word), vertex


def _checked_weave_matrix(word, tokens):
    """Compare the physical word with the abstract F/R expression."""
    # Right-associated basis: right-pair exchange is R, left-pair is FRF.
    f, r = math_constant.F, math_constant.R
    generators = {1: f @ r @ f, 2: r}
    matrix = np.eye(2, dtype=complex)
    for index in word:
        generator = generators[abs(index)]
        matrix = (generator if index > 0 else generator.conj().T) @ matrix
    reference = np.eye(2, dtype=complex)
    for kind, power in tokens:
        operation = f if kind == "F" else np.linalg.matrix_power(r, power)
        reference = operation @ reference
    # R' differs from R by a phase; compare the complete weave up to that phase.
    overlap = np.vdot(reference, matrix)
    phase = overlap / abs(overlap) if abs(overlap) else 1.0
    if not np.allclose(matrix, phase * reference, atol=1e-11, rtol=0):
        raise RuntimeError("Physical weave disagrees with its F/R expression.")
    if not np.allclose(matrix.conj().T @ matrix, np.eye(2), atol=1e-11, rtol=0):
        raise RuntimeError("Three-object weave lost numerical unitarity.")
    return matrix


def build_exchange_weave(iterations=2):
    """Return FR^3F's exchange weave in the right-associated two-channel basis.

    Supplement the raw expression with diagonal R factors when needed
    to start at vertex 1 and end at vertex 4, as prescribed in Sec. III.
    Its ideal target keeps the measured diagonal phases, which this
    construction does not prescribe. This fidelity is not CNOT fidelity.
    """
    tokens = _exchange_tokens(iterations)
    _, vertex = _tokens_to_weave(tokens)
    if vertex in (2, 3):
        tokens = (("R", 1),) + tokens
    _, vertex = _tokens_to_weave(tokens)
    if vertex == 5:
        tokens = tokens + (("R", 1),)
    word, vertex = _tokens_to_weave(tokens)
    if vertex != 4:
        raise RuntimeError("Exchange weave did not end at hexagon vertex 4.")
    matrix = _checked_weave_matrix(word, tokens)
    f, r = math_constant.F, math_constant.R
    x0 = float(abs((f @ np.linalg.matrix_power(r, 3) @ f)[0, 1]))
    expected_error = x0 ** (5 ** iterations)
    exchange_error = float(abs(matrix[0, 1]))
    if not np.isclose(exchange_error, expected_error, atol=1e-11, rtol=1e-8):
        raise RuntimeError("Exchange weave does not satisfy x_(k+1) = x_k^5.")
    target = np.diag(np.exp(1j * np.angle(np.diag(matrix))))
    return {
        "iterations": iterations,
        "seed": "FR^3F",
        "word": word,
        "matrix": matrix,
        "target_matrix": target,
        "target_kind": "diagonal exchange weave",
        "average_gate_fidelity": _average_gate_fidelity(matrix, target),
        "exchange_error": exchange_error,
        "expected_exchange_error": expected_error,
    }


def build_offdiagonal_weave(iterations=1):
    """Use the phase seed FR^2F and a custom recurrence to approach a pi rotation.

    Eq. (22), in CHRONOLOGICAL order, is
    U, R, U^-1, R^-3, U, R^3, U^-1, R^-1, U.
    Here the diagonal magnitude y obeys y_(k+1) = y_k^5. The ideal
    off-diagonal target retains both phases of the physical word; no
    independent control-branch phase is removed when embedding it later.
    """
    _validate_iterations(iterations)
    tokens = (("F", 0), ("R", 2), ("F", 0))
    for _ in range(iterations):
        inverse = tuple((kind, -power) for kind, power in reversed(tokens))
        tokens = (
            tokens + (("R", 1),) + inverse + (("R", -3),)
            + tokens + (("R", 3),) + inverse + (("R", -1),) + tokens
        )
    word, vertex = _tokens_to_weave(tokens)
    if vertex != 1:
        raise RuntimeError("Off-diagonal weave did not return to hexagon vertex 1.")
    matrix = _checked_weave_matrix(word, tokens)
    f, r = math_constant.F, math_constant.R
    y0 = float(abs((f @ np.linalg.matrix_power(r, 2) @ f)[0, 0]))
    expected_error = y0 ** (5 ** iterations)
    diagonal_error = float(np.max(np.abs(np.diag(matrix))))
    if not np.isclose(diagonal_error, expected_error, atol=1e-11, rtol=1e-8):
        raise RuntimeError("Off-diagonal weave does not satisfy y_(k+1) = y_k^5.")
    target = np.array([
        [0, np.exp(1j * np.angle(matrix[0, 1]))],
        [np.exp(1j * np.angle(matrix[1, 0])), 0],
    ], dtype=complex)
    return {
        "iterations": iterations,
        "seed": "FR^2F",
        "word": word,
        "matrix": matrix,
        "target_matrix": target,
        "target_kind": "off-diagonal pi rotation",
        "average_gate_fidelity": _average_gate_fidelity(matrix, target),
        "diagonal_error": diagonal_error,
        "expected_diagonal_error": expected_error,
    }


def _generate_weave(builder, fidelity, max_iterations):
    _validate_fidelity(fidelity)
    _validate_iterations(max_iterations)
    best = None
    for iteration in range(max_iterations + 1):
        candidate = builder(iteration)
        candidate["requested_fidelity"] = float(fidelity)
        candidate["target_reached"] = candidate["average_gate_fidelity"] >= fidelity
        if best is None or candidate["average_gate_fidelity"] > best["average_gate_fidelity"]:
            best = candidate
        if candidate["target_reached"]:
            return candidate
    return best


def generate_exchange_weave(fidelity=99.99, max_iterations=3):
    """Select a weave by measured two-channel fidelity to a diagonal unitary.

    word uses THREE-OBJECT sigma indices; it needs cabling for eight anyons.
    If the iteration budget is exhausted, return the best candidate with
    target_reached=False. Subproblem fidelity does not guarantee gate fidelity.
    """
    return _generate_weave(build_exchange_weave, fidelity, max_iterations)


def generate_offdiagonal_weave(fidelity=99.99, max_iterations=3):
    """Select a returning three-object weave by fidelity to a pi rotation.

    The axis and phase are measured, not chosen. Check target_reached;
    exhausting the iteration budget does not count as success.
    """
    return _generate_weave(build_offdiagonal_weave, fidelity, max_iterations)


def _cable_weave(word, objects=((3, 4), (5,), (6,)), prefix=(1, 2), suffix=(7, 8)):
    """Expand crossings of three adjacent objects; only pair (3,4) may weave."""
    objects = list(objects)
    physical_word = []
    for index in word:
        if index not in (-2, -1, 1, 2):
            raise ValueError("A three-object weave uses only +/-1 and +/-2.")
        left = abs(index) - 1
        first, second = objects[left:left + 2]
        if (3, 4) not in (first, second):
            raise ValueError("A weave must not braid the two fixed warps together.")
        start = len(prefix) + sum(len(obj) for obj in objects[:left])
        sign = 1 if index > 0 else -1
        # Exchange adjacent blocks preserving the internal order of each block.
        for offset in range(len(second)):
            for step in range(len(first)):
                physical_word.append(sign * (start + len(first) + offset - step))
        objects[left:left + 2] = [second, first]
    final_order = prefix + tuple(a for obj in objects for a in obj) + suffix
    return tuple(physical_word), final_order


def build_controlled_r2(iterations=2):
    """Build W, the middle R^2 on objects 2/3, then W inverse (Fig. 5)."""
    exchange = build_exchange_weave(iterations)
    word = exchange["word"]
    # After W the object order is [5, (3,4), 6]. The middle full winding
    # therefore braids the control pair around anyon 6, conserving its charge.
    abstract_word = word + (2, 2) + _inverse_word(word)
    sequence, order = _cable_weave(abstract_word)
    if order != tuple(range(1, 9)):
        raise RuntimeError("Controlled braid did not restore the anyon order.")
    return {
        "iterations": iterations,
        "seed": "FR^3F",
        "exchange_word": word,
        "object_word": abstract_word,
        "sequence": sequence,
        "exchange_error": exchange["exchange_error"],
        "expected_exchange_error": exchange["expected_exchange_error"],
    }


def build_controlled_offdiagonal(exchange_iterations=1, offdiagonal_iterations=1):
    """Use four-anyon insertion, a middle weave, and extraction.

    Reflect the paper's layout so q[0] remains the control. The insertion
    moves (3,4) through objects [(1,2), (3,4), 5], yielding the order
    [1,2,5,3,4,6,7,8]. The effective target is then [(3,4),6,7,8].
    This is NOT the Fig. 5 insertion used by build_controlled_r2: that
    insertion has target-dependent phases and only permits diagonal gates.
    """
    exchange = build_exchange_weave(exchange_iterations)
    middle = build_offdiagonal_weave(offdiagonal_iterations)
    # Mirror the object indices of the inverse exchange, keeping braid signs.
    insertion_word = tuple(
        (1 if i > 0 else -1) * (3 - abs(i))
        for i in _inverse_word(exchange["word"])
    )
    insertion, inserted_order = _cable_weave(
        insertion_word, objects=((1, 2), (3, 4), (5,)),
        prefix=(), suffix=(6, 7, 8),
    )
    if inserted_order != (1, 2, 5, 3, 4, 6, 7, 8):
        raise RuntimeError("Control pair was not inserted at the target boundary.")
    middle_sequence, middle_order = _cable_weave(
        middle["word"], objects=((3, 4), (6,), (7,)),
        prefix=(1, 2, 5), suffix=(8,),
    )
    if middle_order != inserted_order:
        raise RuntimeError("Middle weave did not restore the inserted pair.")
    sequence = insertion + middle_sequence + _inverse_word(insertion)
    # Qitker labels the LEFT pair of [A,6,7], while the three-object
    # construction uses the right-associated basis: V_logical = F V F.
    # V is a traceless unitary, with opposite eigenvalues, so controlled-V
    # is locally equivalent to CX. Its complete phase is retained here.
    f = math_constant.F
    target = np.eye(4, dtype=complex)
    target[2:, 2:] = f @ middle["target_matrix"] @ f
    return {
        "sequence": sequence,
        "control": 0,
        "target": 1,
        "target_kind": "controlled pi rotation; local CNOT corrections pending",
        "target_matrix": target,
        "exchange_iterations": exchange_iterations,
        "offdiagonal_iterations": offdiagonal_iterations,
        "exchange_error": exchange["exchange_error"],
        "diagonal_error": middle["diagonal_error"],
        "insertion_sequence": insertion,
        "middle_sequence": middle_sequence,
    }


def _evaluate_controlled(engine, sequence, target):
    """Score physical evolution against the given full 4x4 target."""
    if engine.qubits_num != 2 or engine.logical_labels != ("00", "01", "10", "11"):
        raise ValueError("This reconstruction requires two qubits in Qitker bit order.")
    physical, final_order = engine.run_sequence(sequence)
    logical = physical[list(engine.computational_indices), :]
    leaked = physical[list(engine.leakage_indices), :]
    loss = leaked.conj().T @ leaked
    overlap = np.trace(target.conj().T @ logical)
    global_phase = overlap / abs(overlap) if abs(overlap) else 1.0
    # Remove only ONE phase shared by the entire gate, never a phase per control.
    matrix_error = float(np.linalg.norm(logical - global_phase * target, ord=2))
    return {
        "target_matrix": target,
        "computational_matrix": logical,
        "matrix_error": matrix_error,
        "global_phase": complex(global_phase),
        "control_zero_error": float(np.linalg.norm(
            physical[:, :2] - engine.initial_columns[:, :2], ord=2
        )),
        "process_fidelity": float(100 * abs(overlap) ** 2 / 16),
        "average_gate_fidelity": _average_gate_fidelity(logical, target),
        "leakage_by_input": dict(zip(engine.logical_labels, map(float, np.diag(loss).real))),
        "average_leakage": max(
            0.0,
            float(np.trace(loss).real / len(engine.logical_labels)),
        ),
        "maximum_leakage": max(0.0, float(np.linalg.eigvalsh(loss)[-1])),
        "final_anyon_order": final_order,
        "order_restored": final_order == engine.initial_order,
    }


def evaluate_controlled_r2(engine, sequence):
    """Score the full 13D evolution against diag(I, R^2), without postselection."""
    target = np.eye(4, dtype=complex)
    target[2:, 2:] = np.linalg.matrix_power(math_constant.R, 2)
    return _evaluate_controlled(engine, sequence, target)


def generate_controlled_weave(fidelity=99.99, max_leakage=None, max_iterations=3):
    """Return physical eight-anyon sigmas approaching a controlled pi rotation.

    Fidelity is the measured, unconditioned average gate fidelity against
    the returned target_matrix, NOT against CX. The ideal target is in
    the local-equivalence class of CX; its local corrections are not applied.
    max_leakage bounds the worst-case leakage probability over all logical
    superpositions; it defaults to 1 - fidelity/100. Intermediate weaves
    may leak more. Iteration budgets apply separately to both weaves.

    A result includes sequence, result (metrics/matrix), replay_error,
    target_reached, and a compact history. On budget exhaustion the best
    verified attempt is returned with target_reached=False. Nothing is saved.
    """
    _validate_fidelity(fidelity)
    _validate_iterations(max_iterations)
    if max_leakage is None:
        max_leakage = 1 - fidelity / 100
    if isinstance(max_leakage, (bool, np.bool_)) or not isinstance(
        max_leakage, (int, float, np.integer, np.floating)
    ):
        raise TypeError("max_leakage must be a probability.")
    if not np.isfinite(max_leakage) or not 0 <= max_leakage <= 1:
        raise ValueError("max_leakage must be a probability in [0, 1].")
    exchange = generate_exchange_weave(fidelity, max_iterations)
    middle = generate_offdiagonal_weave(fidelity, max_iterations)
    e, m = exchange["iterations"], middle["iterations"]
    engine = braid_searching(2, "I", target=1, controllers=(0,))
    best = None
    history = []
    while True:
        candidate = build_controlled_offdiagonal(e, m)
        result = _evaluate_controlled(engine, candidate["sequence"], candidate["target_matrix"])
        if not result["order_restored"] or result["control_zero_error"] > 1e-9:
            raise RuntimeError("Four-anyon controlled weave failed structural verification.")
        candidate.update({
            "result": result,
            "requested_fidelity": float(fidelity),
            "max_leakage": float(max_leakage),
            "target_reached": (
                result["average_gate_fidelity"] >= fidelity
                and result["maximum_leakage"] <= max_leakage
            ),
        })
        history.append({
            "exchange_iterations": e,
            "offdiagonal_iterations": m,
            "braid_count": len(candidate["sequence"]),
            "average_gate_fidelity": result["average_gate_fidelity"],
            "maximum_leakage": result["maximum_leakage"],
        })
        if best is None or result["average_gate_fidelity"] > best["result"]["average_gate_fidelity"]:
            best = candidate
        if candidate["target_reached"]:
            best = candidate
            break
        if e == max_iterations and m == max_iterations:
            break
        # Insertion error controls leakage. Otherwise refine the larger
        # amplitude error, measuring the COMPLETE gate again after each step.
        if e < max_iterations and (
            m == max_iterations or result["maximum_leakage"] > max_leakage
            or candidate["exchange_error"] >= candidate["diagonal_error"]
        ):
            e += 1
        else:
            m += 1
    best["replay_error"] = engine.verify_with_qitker(best["sequence"])
    best["history"] = history
    return best


def _normalize_controlled_gate(gate):
    """Return a base-gate name; accept either G or CG spelling."""
    if not isinstance(gate, str):
        raise TypeError("gate must be X, Y, Z, S, T or its controlled spelling.")
    gate = gate.strip().upper()
    if gate in {"CX", "CY", "CZ", "CS", "CT"}:
        gate = gate[1:]
    if gate not in {"X", "Y", "Z", "S", "T"}:
        raise ValueError("gate must be X, Y, Z, S, T, CX, CY, CZ, CS, or CT.")
    return gate


def _normalize_controlled_pauli(gate):
    """Return X, Y, or Z for the locally equivalent controlled-pi path."""
    gate = _normalize_controlled_gate(gate)
    if gate not in {"X", "Y", "Z"}:
        raise ValueError("controlled-pi synthesis supports only X, Y, or Z.")
    return gate


def controlled_pauli_local_corrections(target_matrix, gate="X"):
    """Find local corrections that turn controlled-V into CX, CY, or CZ.

    V = exp(i*chi) N with N Hermitian, traceless, and N^2=I. Its eigenbasis
    sends N to Z, followed by H to send Z to X. A final basis change maps X
    to the requested Pauli. P cancels exp(i*chi) only on the control=1 branch;
    this phase must not be discarded as global.
    """
    gate = _normalize_controlled_pauli(gate)
    target = np.asarray(target_matrix, dtype=complex)
    if target.shape != (4, 4) or not np.all(np.isfinite(target)):
        raise ValueError("Expected a finite 4x4 controlled-pi target.")
    v = target[2:, 2:]
    expected = np.eye(4, dtype=complex)
    expected[2:, 2:] = v
    if not np.allclose(target, expected, atol=1e-10, rtol=0):
        raise ValueError("Target must have the form diag(I,V).")
    if not np.allclose(v.conj().T @ v, np.eye(2), atol=1e-10, rtol=0) or abs(np.trace(v)) > 1e-10:
        raise ValueError("V must be a traceless unitary pi rotation.")
    chi = float(np.angle(-np.linalg.det(v)) / 2)
    n = np.exp(-1j * chi) * v
    if not np.allclose(n, n.conj().T, atol=1e-10, rtol=0):
        raise RuntimeError("Failed to extract the Hermitian rotation axis.")
    _, eigenvectors = np.linalg.eigh(n)
    cnot_basis = math_constant.H @ eigenvectors[:, ::-1].conj().T
    output_basis = {
        "X": math_constant.I,
        "Y": math_constant.S,
        "Z": math_constant.H,
    }[gate]
    basis_change = output_basis @ cnot_basis
    p = np.diag([1, np.exp(-1j * chi)])
    controlled_gate = np.eye(4, dtype=complex)
    controlled_gate[2:, 2:] = math_constant.GATE_MATRICES[gate]
    corrected = (
        np.kron(p, basis_change)
        @ target
        @ np.kron(np.eye(2), basis_change.conj().T)
    )
    if not np.allclose(corrected, controlled_gate, atol=1e-10, rtol=0):
        raise RuntimeError(f"Analytic local corrections do not produce C{gate}.")
    return {
        "gate": gate,
        "target_before": basis_change.conj().T,
        "target_after": basis_change,
        "control_after": p,
        "control_phase": chi,
        "controlled_matrix": controlled_gate,
    }


def cnot_local_corrections(target_matrix):
    """Compatibility wrapper for the original CX correction helper."""
    corrections = controlled_pauli_local_corrections(target_matrix, "X")
    corrections["cnot_matrix"] = corrections["controlled_matrix"]
    return corrections


def _compile_local_correction(target, level, net, sk):
    """Use the existing MITM net and SK commutator decomposition.

    Every alphabet symbol is sigma_1^+/-2 or sigma_2^+/-2, so every
    candidate restores the four local anyon identities. Matrices in this
    compiler are SU(2) representatives only; final scores use physical words.
    """
    target = sk._as_su2(target)
    if level == 0:
        return sk._macro_mitm_approximate(target, *net)
    word, matrix = _compile_local_correction(target, level - 1, net, sk)
    delta = sk._as_su2(target @ matrix.conj().T)
    exact_v, exact_w = sk._group_commutator_decomposition(delta)
    v_word, v = _compile_local_correction(exact_v, level - 1, net, sk)
    w_word, w = _compile_local_correction(exact_w, level - 1, net, sk)
    correction = _inverse_word(w_word) + _inverse_word(v_word) + w_word + v_word
    return (sk._reduce_word(word + correction),
            sk._as_su2(v @ w @ v.conj().T @ w.conj().T @ matrix))


def generate_controlled_pauli(gate="X", fidelity=99.99, max_leakage=None,
                              max_iterations=3, local_net_depth=7,
                              max_local_refinements=2):
    """Return a verified physical CX, CY, or CZ braid for q[0] -> q[1].

    gate accepts X/Y/Z and CX/CY/CZ. fidelity is average gate fidelity in
    PERCENT against the requested controlled gate itself, without postselection.
    max_leakage is a worst-case probability (default 1-F/100). Reserve an
    eighth of the infidelity budget for the controlled weave; the FINAL complete
    gate score, not that allocation, decides success.

    Local synthesis is bounded by max_local_refinements. If a budget runs
    out, return the best evaluated sequence with target_reached=False.
    No gate library, backend, or saved braid file is changed.
    """
    gate = _normalize_controlled_pauli(gate)
    _validate_fidelity(fidelity)
    _validate_iterations(max_iterations)
    _validate_iterations(local_net_depth)
    _validate_iterations(max_local_refinements)
    if max_leakage is None:
        max_leakage = 1 - fidelity / 100
    weave_fidelity = 100 - (100 - float(fidelity)) / 8
    # Avoid rounding a very tight but finite request up to the forbidden 100%.
    weave_fidelity = min(weave_fidelity, float(np.nextafter(100.0, 0.0)))
    weave = generate_controlled_weave(weave_fidelity, max_leakage, max_iterations)
    corrections = controlled_pauli_local_corrections(weave["target_matrix"], gate)

    # Import only for local synthesis; reuse helpers without their saving path.
    import solovay_kitaev as sk
    local_engine = braid_searching(1, "I", target=0)
    net = sk._build_macro_mitm_net(local_engine, local_net_depth, {
        "sigma1_squared": {"sequence": (1, 1)},
        "sigma2_squared": {"sequence": (2, 2)},
    })
    engine = braid_searching(2, gate, target=1, controllers=(0,))
    best = None
    history = []
    for level in range(max_local_refinements + 1):
        s_word, _ = _compile_local_correction(corrections["target_after"], level, net, sk)
        p_word, _ = _compile_local_correction(corrections["control_after"], level, net, sk)
        s_matrix, s_order = local_engine.run_sequence(s_word)
        p_matrix, p_order = local_engine.run_sequence(p_word)
        if s_order != local_engine.initial_order or p_order != local_engine.initial_order:
            raise RuntimeError("Local correction changed the endpoint permutation.")
        target_after = tuple((1 if i > 0 else -1) * (abs(i) + 4) for i in s_word)
        target_before = _inverse_word(target_after)
        # Use the EXACT inverse braid for the pre-rotation: its physical
        # global phase cancels that of the post-rotation even at finite accuracy.
        sequence = sk._reduce_word(target_before + weave["sequence"] + target_after + p_word)
        result = _evaluate_controlled(engine, sequence, engine.target_matrix)
        physical, _ = engine.run_sequence(sequence)
        result["control_zero_error"] = float(np.linalg.norm(
            physical[:, :2] - result["global_phase"] * engine.initial_columns[:, :2], ord=2
        ))
        candidate = {
            "sequence": sequence, "control": 0, "target": 1,
            "target_kind": f"C{gate}", "target_matrix": engine.target_matrix,
            "requested_fidelity": float(fidelity), "max_leakage": float(max_leakage),
            "result": result, "local_refinement": level,
            "weave": weave, "local_corrections": corrections,
            "target_before_sequence": target_before,
            "target_after_sequence": target_after, "control_after_sequence": p_word,
            "local_fidelities": {
                "target_rotation": _average_gate_fidelity(s_matrix, corrections["target_after"]),
                "control_phase": _average_gate_fidelity(p_matrix, corrections["control_after"]),
            },
            "target_reached": (
                result["average_gate_fidelity"] >= fidelity
                and result["maximum_leakage"] <= max_leakage
                and result["order_restored"]
            ),
        }
        history.append({"local_refinement": level, "braid_count": len(sequence),
                        "average_gate_fidelity": result["average_gate_fidelity"],
                        "maximum_leakage": result["maximum_leakage"]})
        if best is None or result["average_gate_fidelity"] > best["result"]["average_gate_fidelity"]:
            best = candidate
        if candidate["target_reached"]:
            best = candidate
            break
    best["replay_error"] = engine.verify_with_qitker(best["sequence"])
    best["history"] = history
    return best


def generate_cnot(fidelity=99.99, max_leakage=None, max_iterations=3,
                  local_net_depth=7, max_local_refinements=2):
    """Compatibility wrapper returning a verified physical CX braid."""
    return generate_controlled_pauli(
        "X", fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )


def generate_cy(fidelity=99.99, max_leakage=None, max_iterations=3,
                local_net_depth=7, max_local_refinements=2):
    """Return a verified physical CY braid for control=0, target=1."""
    return generate_controlled_pauli(
        "Y", fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )


def generate_cz(fidelity=99.99, max_leakage=None, max_iterations=3,
                local_net_depth=7, max_local_refinements=2):
    """Return a verified physical CZ braid for control=0, target=1."""
    return generate_controlled_pauli(
        "Z", fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )


def generate_controlled_phase(gate="S", fidelity=99.99, max_leakage=None,
                              max_iterations=3, local_net_depth=7,
                              max_local_refinements=2):
    """Return a verified physical CS or CT braid for q[0] -> q[1].

    For P(theta) equal to S or T, use the exact circuit identity

        CP(theta) = (P(theta/2) tensor P(theta/2))
                    CX (I tensor P(-theta/2)) CX.

    The two CX occurrences reuse one generated physical braid. The half-angle
    phase is compiled as a pure local braid, and its exact inverse word supplies
    the negative phase. The complete sequence is evaluated without postselection.
    """
    gate = _normalize_controlled_gate(gate)
    if gate not in {"S", "T"}:
        raise ValueError("controlled-phase synthesis supports only S or T.")
    _validate_fidelity(fidelity)
    _validate_iterations(max_iterations)
    _validate_iterations(local_net_depth)
    _validate_iterations(max_local_refinements)
    if max_leakage is None:
        max_leakage = 1 - fidelity / 100
    if isinstance(max_leakage, (bool, np.bool_)) or not isinstance(
        max_leakage, (int, float, np.integer, np.floating)
    ):
        raise TypeError("max_leakage must be a probability.")
    if not np.isfinite(max_leakage) or not 0 <= max_leakage <= 1:
        raise ValueError("max_leakage must be a probability in [0, 1].")

    # Two entangling gates and three local phase occurrences share the final
    # error budget. Final full-gate evaluation remains the acceptance test.
    component_fidelity = 100 - (100 - float(fidelity)) / 4
    component_fidelity = min(
        component_fidelity, float(np.nextafter(100.0, 0.0))
    )
    cnot = generate_cnot(
        fidelity=component_fidelity,
        max_leakage=float(max_leakage) / 2,
        max_iterations=max_iterations,
        local_net_depth=local_net_depth,
        max_local_refinements=max_local_refinements,
    )
    cnot_word = tuple(cnot["sequence"])

    import solovay_kitaev as sk
    local_engine = braid_searching(1, "I", target=0)
    net = sk._build_macro_mitm_net(local_engine, local_net_depth, {
        "sigma1_squared": {"sequence": (1, 1)},
        "sigma2_squared": {"sequence": (2, 2)},
    })
    theta = {"S": np.pi / 2, "T": np.pi / 4}[gate]
    half_phase = np.diag([1, np.exp(1j * theta / 2)])
    engine = braid_searching(2, gate, target=1, controllers=(0,))
    best = None
    history = []
    for level in range(max_local_refinements + 1):
        phase_word, _ = _compile_local_correction(
            half_phase, level, net, sk
        )
        phase_matrix, phase_order = local_engine.run_sequence(phase_word)
        if phase_order != local_engine.initial_order:
            raise RuntimeError("Local half-phase changed the endpoint permutation.")
        control_phase = tuple(phase_word)
        target_phase = tuple(
            (1 if index > 0 else -1) * (abs(index) + 4)
            for index in phase_word
        )
        target_inverse_phase = _inverse_word(target_phase)
        sequence = sk._reduce_word(
            cnot_word
            + target_inverse_phase
            + cnot_word
            + control_phase
            + target_phase
        )
        result = _evaluate_controlled(engine, sequence, engine.target_matrix)
        physical, _ = engine.run_sequence(sequence)
        result["control_zero_error"] = float(np.linalg.norm(
            physical[:, :2]
            - result["global_phase"] * engine.initial_columns[:, :2],
            ord=2,
        ))
        candidate = {
            "sequence": sequence,
            "control": 0,
            "target": 1,
            "target_kind": f"C{gate}",
            "target_matrix": engine.target_matrix,
            "requested_fidelity": float(fidelity),
            "max_leakage": float(max_leakage),
            "result": result,
            "local_refinement": level,
            "phase_angle": theta,
            "half_phase_matrix": half_phase,
            "half_phase_sequence": control_phase,
            "target_inverse_phase_sequence": target_inverse_phase,
            "cnot_component": cnot,
            "component_fidelity": component_fidelity,
            "local_fidelities": {
                "half_phase": _average_gate_fidelity(
                    phase_matrix, half_phase
                ),
            },
            "target_reached": (
                result["average_gate_fidelity"] >= fidelity
                and result["maximum_leakage"] <= max_leakage
                and result["order_restored"]
            ),
        }
        history.append({
            "local_refinement": level,
            "braid_count": len(sequence),
            "average_gate_fidelity": result["average_gate_fidelity"],
            "maximum_leakage": result["maximum_leakage"],
        })
        if best is None or (
            result["average_gate_fidelity"]
            > best["result"]["average_gate_fidelity"]
        ):
            best = candidate
        if candidate["target_reached"]:
            best = candidate
            break
    best["replay_error"] = engine.verify_with_qitker(best["sequence"])
    best["history"] = history
    return best


def generate_cs(fidelity=99.99, max_leakage=None, max_iterations=3,
                local_net_depth=7, max_local_refinements=2):
    """Return a verified physical CS braid for control=0, target=1."""
    return generate_controlled_phase(
        "S", fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )


def generate_ct(fidelity=99.99, max_leakage=None, max_iterations=3,
                local_net_depth=7, max_local_refinements=2):
    """Return a verified physical CT braid for control=0, target=1."""
    return generate_controlled_phase(
        "T", fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )


def print_result(candidate):
    result = candidate["result"]
    print(f"\nFR^3F, iteration {candidate['iterations']}")
    print(f"  physical braid count: {len(candidate['sequence'])}")
    print(f"  exchange error: {candidate['exchange_error']:.6e}")
    print(f"  expected exchange error: {candidate['expected_exchange_error']:.6e}")
    print(f"  controlled-R^2 matrix error: {result['matrix_error']:.6e}")
    print(f"  average gate fidelity: {result['average_gate_fidelity']:.12f}%")
    print(f"  maximum leakage: {result['maximum_leakage']:.6e}")
    print(f"  control=0 identity error: {result['control_zero_error']:.6e}")
    print(f"  anyon order restored: {result['order_restored']}")


def search_better_sequence(max_iterations=2, target_error=1e-10, max_leakage=1e-12):
    """Try successive known-seed iterations; return the best verified candidate.

    This is a bounded reconstruction experiment. Word length grows roughly
    fivefold per iteration. The target is controlled-R^2, not CX.
    """
    _validate_iterations(max_iterations)
    if not np.isfinite(target_error) or target_error <= 0:
        raise ValueError("target_error must be positive and finite.")
    if not np.isfinite(max_leakage) or not 0 <= max_leakage <= 1:
        raise ValueError("max_leakage must be a probability in [0, 1].")
    # Reuse the physical evaluator. Its built-in I target is unused; the scorer
    # above supplies the full controlled-R^2 target, which its gate API lacks.
    engine = braid_searching(2, "I", target=1, controllers=(0,))
    best = None
    history = []
    for iteration in range(max_iterations + 1):
        candidate = build_controlled_r2(iteration)
        result = evaluate_controlled_r2(engine, candidate["sequence"])
        candidate["result"] = result
        if not result["order_restored"] or result["control_zero_error"] > 1e-9:
            raise RuntimeError("Controlled-weave structural verification failed.")
        candidate["target_reached"] = (
            result["matrix_error"] <= target_error
            and result["maximum_leakage"] <= max_leakage
        )
        print_result(candidate)
        history.append(candidate)
        if best is None or result["matrix_error"] < best["result"]["matrix_error"]:
            best = candidate
        if candidate["target_reached"]:
            best = candidate
            break
    best = dict(best)
    best["replay_error"] = engine.verify_with_qitker(best["sequence"])
    best["history"] = history
    print(f"\nTarget reached: {best['target_reached']}")
    print(f"F/R replay error: {best['replay_error']:.6e}")
    return best


def searchControlledGate(gate="X", controls=(0,), target=1, fidelity=99.999,
                         max_leakage=None, max_iterations=3,
                         local_net_depth=7, max_local_refinements=2):
    gate = _normalize_controlled_gate(gate)
    if tuple(controls) != (0,) or target != 1:
        raise NotImplementedError(
            "Physical synthesis currently supports control=q[0], target=q[1]."
        )
    print(f"C{gate}: control=q[0], target=q[1] (including physical local corrections)")
    generator = (
        generate_controlled_pauli
        if gate in {"X", "Y", "Z"}
        else generate_controlled_phase
    )
    result = generator(
        gate, fidelity, max_leakage, max_iterations,
        local_net_depth, max_local_refinements,
    )
    metrics = result["result"]
    print(f"Requested average gate fidelity: {result['requested_fidelity']}%")
    print(f"Measured average gate fidelity: {metrics['average_gate_fidelity']:.12f}%")
    if "weave" in result:
        weave = result["weave"]
        print(
            "Exchange/off-diagonal iterations: "
            f"{weave['exchange_iterations']}/{weave['offdiagonal_iterations']}"
        )
        print(f"Local synthesis refinement: {result['local_refinement']}")
    else:
        cnot = result["cnot_component"]
        print(
            "CX component fidelity: "
            f"{cnot['result']['average_gate_fidelity']:.12f}%"
        )
        print(f"CX component braid count: {len(cnot['sequence'])}")
        print(f"Half-phase synthesis refinement: {result['local_refinement']}")
    print(f"Physical braid count: {len(result['sequence'])}")
    print(f"Maximum leakage: {metrics['maximum_leakage']:.6e}")
    print(f"Control=0 identity error: {metrics['control_zero_error']:.6e}")
    print(f"Anyon order restored: {metrics['order_restored']}")
    print(f"Target reached: {result['target_reached']}")
    print(f"F/R replay error: {result['replay_error']:.6e}")
    print("Computational matrix (00, 01, 10, 11), global phase aligned:")
    with np.printoptions(precision=8, suppress=True):
        print(metrics["computational_matrix"] / metrics["global_phase"])
    print(f"Final sequence: {result['sequence']}")
    return result


def _save_controlled_gate(gate, candidate):
    """Save one verified controlled gate beside the single-qubit SK gates."""
    import solovay_kitaev as sk

    gate_key = f"C{_normalize_controlled_gate(gate)}"
    seed_record = {
        "type": "controlled_qubit",
        "basis": "fibonacci_8_anyons",
    }
    sk._save_search_result(gate_key, seed_record, candidate)


def main():
    for gate in ("X", "Y", "Z", "S", "T"):
        print(f"start searching C{gate} braiding")
        start = time.perf_counter()
        candidate = searchControlledGate(
            gate=gate,
            controls=(0,),
            target=1,
            fidelity=99.99,
            max_leakage=None,
        )
        _save_controlled_gate(gate, candidate)
        end = time.perf_counter()
        print(f"Runtime: {end - start:.6f} seconds")

if __name__ == "__main__":
    main()
