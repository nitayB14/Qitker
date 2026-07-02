import numpy as np

class math_constant():
    """




    """

    phi = (1 + np.sqrt(5)) / 2
    #####################################################
    #R matrix
    R = np.array([
        [np.exp(-4j*np.pi/5), 0],
        [0, np.exp(3j*np.pi/5)]
    ], dtype=complex)

    #F matrix
    F = np.array([
        [1/phi, 1/np.sqrt(phi)],
        [1/np.sqrt(phi), -1/phi]
    ], dtype=complex)
    #####################################################
    F_inv = F
    R_inv = np.linalg.inv(R)

    R12 = R
    R12_inv = R_inv

    R23 = F @ R @ F_inv
    R23_inv = F @ R_inv @ F_inv

    R34 = R
    R34_inv = R_inv

    #####################################################
    H = (1/np.sqrt(2)) * np.array([
        [1, 1],
        [1, -1]
    ], dtype=complex)

    X = np.array([
        [0, 1],
        [1, 0]
    ], dtype=complex)

    Y = np.array([
        [0, -1j],
        [1j, 0]
    ], dtype=complex)

    Z = np.array([
        [1, 0],
        [0, -1]
    ], dtype=complex)

    S = np.array([
        [1, 0],
        [0, 1j]
    ], dtype=complex)

    T = np.array([
        [1, 0],
        [0, np.exp(1j*np.pi/4)]
    ], dtype=complex)