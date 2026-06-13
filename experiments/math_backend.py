import numpy as np

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

#####################################################


#R on 1,2
def apply_R12(state):
    return R @ state

def apply_reverseR12(state):
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
    elif num == -1:
        state = apply_reverseR12(state)
    elif num == -2:
        state = apply_reverseR23(state)
    else:
        raise ValueError("bad input")
    return state
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
def main():
    state = np.array([1,0], dtype=complex)

    print(f"initial: {state}")
    print(f"probs: {probs(state)}")
    print("####################################################")
    
    H_SEQ_BETTER = [
    -1, -2,  1,  1, -2,  1,  1,  2, -1,  2,
     1,  2,  1,  1,  2,  2,  1, -2,  1,  1,
    -2, -2, -1, -1, -1, -2, -1,  2,  1,  2,
    -1, -2,  1,  2,  2,  2,  2,  2,  1,  2,
     2, -1,  2,  2,  1,  2, -1, -2, -2, -2,
     1, -2, -2,  1,  1, -2, -2,  1,  1,  2,
    -1,  2,  2, -1,  2
]

    for i in H_SEQ_BETTER:
        state = sigma(i, state)


    """
    state = sigma(1, state)
    state = sigma(2, state)
    state = sigma(1, state)
    state = sigma(-2, state)
    state = sigma(-1, state)
    state = sigma(2, state)
    """

    print(f"state: {state}")
    print(f"probs: {probs(state)}")
    print("####################################################")
    results = run_measurements(state, shots=1000)
    print("measurement results:", results)

main()


