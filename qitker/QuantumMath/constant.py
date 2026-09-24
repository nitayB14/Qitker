import numpy as np

class math_constant():
    
    phi = (1 + np.sqrt(5)) / 2

    R_VACUUM = np.exp(-4j * np.pi / 5)
    R_TAU = np.exp(3j * np.pi / 5)

    R = np.array([
        [R_VACUUM, 0],
        [0, R_TAU]

    ], dtype=complex)


    F = np.array([
        [1/phi, 1/np.sqrt(phi)],
        [1/np.sqrt(phi), -1/phi]
    ], dtype=complex)


    F_inv = F.conj().T
    R_inv = R.conj().T

 

    
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


    SIGMA_MATRICES = {
    1: R12,
    -1: R12_inv,
    2: R23,
    -2: R23_inv,
    3: R34,
    -3: R34_inv,
    }


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

    # I gate.
    # Type: np.ndarray (2x2, complex)
    # Represents: Applies identity gate.
    I = np.array([
        [1, 0],
        [0, 1]
    ], dtype=complex)


    GATE_MATRICES = {
    "I": I,
    "H": H,
    "X": X,
    "Y": Y,
    "Z": Z,
    "S": S,
    "T": T,
}
