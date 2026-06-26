import numpy as np
import random

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

R23 = F_inv @ R @ F
R23_inv = F_inv @ R_inv @ F

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
#####################################################


#R on 1,2
def apply_R12(state):
    return R @ state

def apply_reverseR12(state):
    return R_inv @ state

def apply_R34(state):
    return R @ state

def apply_reverseR34(state):
    return R_inv @ state

#FRF^-1 ON 2,3
def apply_R23(state):
    return F_inv @ R @ F @ state

def apply_reverseR23(state):
    return F_inv @ R_inv @ F @ state


def probs(state):
    return np.abs(state) ** 2


#########################################################


def sigma(num, state):
    if num == 1:
        state = apply_R12(state)
    elif num == 2:
        state = apply_R23(state)
    elif num == 3:
        state = apply_R34(state)
    elif num == -1:
        state = apply_reverseR12(state)
    elif num == -2:
        state = apply_reverseR23(state)
    elif num == -3:
        state = apply_reverseR34(state)
    else:
        raise ValueError("bad input")
    return state
##############################################################

def sigma_matrix(num):
    if num == 1:
        return R12
    elif num == 2:
        return R23
    elif num == 3:
        return R34
    elif num == -1:
        return R12_inv
    elif num == -2:
        return R23_inv
    elif num == -3:
        return R34_inv
    else:
        raise ValueError("bad input")


def sequence_to_matrix(sequence):
    U = np.eye(2, dtype=complex)

    for s in sequence:
        U = sigma_matrix(s) @ U

    return U


def gate_fidelity(U_target, U):
    d = U.shape[0]
    return abs(np.trace(U_target.conj().T @ U)) / d


def gate_error_percent(U_target, U):
    fidelity = gate_fidelity(U_target, U)
    return (1 - fidelity) * 100


##############################################################

def random_sequence(length):
    return [random.choice([1, -1, 2, -2]) for _ in range(length)]


def search_gate_random(target_gate, length=60, attempts=10000):
    best_seq = None
    best_fidelity = -1
    best_U = None

    for _ in range(attempts):
        seq = random_sequence(length)
        U = sequence_to_matrix(seq)
        fidelity = gate_fidelity(target_gate, U)

        if fidelity > best_fidelity:
            best_fidelity = fidelity
            best_seq = seq
            best_U = U
            

    return best_seq, best_fidelity, best_U
##############################################################        

def measure_once(state):
    p = probs(state)
    return np.random.choice([0, 1], p=p)


def run_measurements(state, shots=1000):
    results = {0: 0, 1: 0}

    for _ in range(shots):
        outcome = measure_once(state)
        results[outcome] += 1

    return results
##############################################################
H_SEQ_BETTER = [-1, -2,  1,  1, -2,  1,  1,  2, -1,  2,1,  2,  1,  1,  2,  2,  1, -2,  1,  1,-2, -2, -1, -1, -1, -2, -1,  2,  1,  2,-1, -2,  1,  2,  2,  2,  2,  2,  1,  2,2, -1,  2,  2,  1,  2, -1, -2, -2, -2,1, -2, -2,  1,  1, -2, -2,  1,  1,  2, -1,  2,  2, -1,  2] 

X_SEQ_BETTER = [-1, -1, -2, 1, 1, 1, -2, -1,1, -1, -1, 2, -1, 2, -2, -1,-1, -2, -2, -1, 1, 2, 2, -2,-1, 2, -2, -2, -2, 1, -2, -2,-1, 2, 2, -1, -2, -1, 2, 1, 2,2, -1, -2, 2, -1, -2, -2, -2,-2, 1, 2, -2, -1, -2, -2, -1,1, 1, 1]

Y_SEQ_BETTER = [-1, -2, -1, -1, 2, -2, -1, 2, -2, -1, 2, -1, -1, -2, -1, -1, 2, 2, -2, 1, 2, 2, 2, -1, -1, -2, 1, 1, 2, -1, 1, 1, -1, -1, -2, 2, -1, 2, -1, 2, 2, 2, -1, 2, -1, -1, -1, -2, -1, -1, 2, -1, 2, -2, 2, 1, -1, 2, -2, -2]

Z_SEQ_BETTER = [-2, 2, -2, -1, 2, -1, 2, -1, 2, -1, -1, -1, 1, 2, -2, 1, -1, -2, -2, -1, -2, -2, -1, 1, -2, 2, -2, -2, -2, 1, -2, -1, -1, 2, 2, -1, 1, 2, 1, 1, 1, -1, 2, 2, 2, -1, 1, -2, -1, -2, -1, 1, -2, -2, -1, 1, -1, -2, 2, 2]

S_SEQ_BETTER = [-2, 1, -1, 1, -2, 1, -2, 1, 2, 1, -1, 2, 2, 1, -1, -1, -1, 1, -2, 1, 1, 2, -1, -1, 2, -2, -2, 1, 1, -1, -2, -2, 2, 2, -1, 2, -1, 1, 2, 1, 1, 2, 1, 2, -2, -2, -2, -1, 1, -2, 1, -1, -2, -2, -2, 1, 1, -2, 2, -1]

T_SEQ_BETTER = [1, 1, 1, -1, 2, 2, -1, -1, 1, 2, 2, 2, 1, 1, 1, -1, 2, 2, 2, -2, 2, -2, 1, 1, 2, 1, -2, -1, 1, 2, 2, 2, 1, -1, 2, -1, 2, 1, -2, 1, -1, 1, 1, -2, 1, -1, -2, 2, -2, 1, -1, -2, 1, 2, 2, 2, -1, 1, 1, 1]


################################################################################################

def checkUT():
    Ut = sequence_to_matrix(T_SEQ_BETTER)

    U2 = Ut @ Ut
    U4 = U2 @ U2
    U8 = U4 @ U4

    print(f"T^2 -> S fidelity: {gate_fidelity(S, U2)*100:.4f}%")
    print(f"T^4 -> Z fidelity: {gate_fidelity(Z, U4)*100:.4f}%")
    print(f"T^8 -> I fidelity: {gate_fidelity(np.eye(2), U8)*100:.4f}%")

def main():
    state = np.array([1,0], dtype=complex)
    print("check T")
    print(f"initial: {state}")
    print(f"probs: {probs(state)}")
    print("####################################################")
    check(state, T_SEQ_BETTER, T)


    #checkUT()

    #matrix = H
    #matrix = X



    #seq, fidelity, U = search_gate_random(matrix, length=60, attempts=50000)
    #print("SEQ =", seq)
    #print(f"fidelity: {fidelity*100:.4f}%")
    #print(f"error: {(1-fidelity)*100:.4f}%")
    #print(U)

    

    
################################################################################################
def check(state, sequence, matrix):
    for i in sequence:
        state = sigma(i, state)

    U = sequence_to_matrix(sequence)

    fidelity = gate_fidelity(matrix, U)
    error_percent = gate_error_percent(matrix, U)

    print("apply gate")
    print("####################################################")

    print(f"state: {state}")
    print(f"probs: {probs(state)}")
    print("####################################################")
    results = run_measurements(state, shots=1000)
    print("measurement results:", results)
    print("####################################################")
    print("braid count:", len(sequence))

    print(f"gate fidelity: {fidelity*100:.4f}%")
    print(f"gate error: {error_percent:.4f}%")
    print("####################################################")
    print("approximated matrix:")
    print(U)
################################################################################################

main()
"""
comp = [Z,S,T]
num = 0
for i in comp:
    num = num + 1
    for j in range(30):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        if num == 1:
            print(f"check number: {j} <-> Z")
        elif num == 2:
            print(f"check number: {j} <-> S")
        elif num == 3:
            print(f"check number: {j} <-> T")
        else: 
            pass

        main(i)


"""
#"""