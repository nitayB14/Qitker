import numpy as np

class math_constant():
    """
    Stores mathematical constants used throughout the quantum compiler.

    This class contains:
    - Fibonacci anyon braiding matrices (R, F and their inverses).
    - Precomputed braid operators (R12, R23, R34).
    - Standard single-qubit quantum gate matrices (H, X, Y, Z, S, T).

    All matrices are immutable and shared across the project to avoid
    recalculating them during execution.
    """


    # Golden ratio related constant used in Fibonacci anyon calculations.
    # Type: float
    # Represents: φ⁻¹ = (√5 - 1) / 2
    phi = (1 + np.sqrt(5)) / 2


    # Fibonacci anyon R-move matrix.
    # Type: np.ndarray (2x2, complex)
    # Represents: Braiding transformation for two neighboring anyons.
    R = np.array([
        [np.exp(-4j*np.pi/5), 0],
        [0, np.exp(3j*np.pi/5)]
    ], dtype=complex)


    # Fibonacci anyon F-move matrix.
    # Type: np.ndarray (2x2, complex)
    # Represents: Basis transformation between fusion trees.
    F = np.array([
        [1/phi, 1/np.sqrt(phi)],
        [1/np.sqrt(phi), -1/phi]
    ], dtype=complex)


    # Inverse F-move matrix.
    F_inv = F

    # Inverse R-move matrix.
    R_inv = np.linalg.inv(R)

    # Braiding matrix for σ₁.
    R12 = R

    # Inverse braiding matrix for σ₁⁻¹.
    R12_inv = R_inv

    # Braiding matrix for σ₂.
    R23 = F @ R @ F_inv

    # Inverse braiding matrix for σ₂⁻¹.
    R23_inv = F @ R_inv @ F_inv

    # Braiding matrix for σ₃.
    R34 = R

    # Inverse braiding matrix for σ₃⁻¹.
    R34_inv = R_inv


    # Hadamard gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Creates superposition.
    H = (1/np.sqrt(2)) * np.array([
        [1, 1],
        [1, -1]
    ], dtype=complex)

    # Pauli-X gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Bit-flip operation.
    X = np.array([
        [0, 1],
        [1, 0]
    ], dtype=complex)

    # Pauli-Y gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Bit-flip combined with phase flip.
    Y = np.array([
        [0, -1j],
        [1j, 0]
    ], dtype=complex)

    # Pauli-Z gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Phase-flip operation.
    Z = np.array([
        [1, 0],
        [0, -1]
    ], dtype=complex)

    # Phase (S) gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Applies a π/2 phase to |1⟩.
    S = np.array([
        [1, 0],
        [0, 1j]
    ], dtype=complex)

    # T gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Applies a π/4 phase to |1⟩.
    T = np.array([
        [1, 0],
        [0, np.exp(1j*np.pi/4)]
    ], dtype=complex)