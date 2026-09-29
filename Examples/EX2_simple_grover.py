#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 29/09/2026
#Rule: Independent researcher
#
#

"""Demonstrate a two-qubit Grover search and result selection with Qitker."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from qitker import circuit, qubit, qRegister


def oracle(search, marker):
    """Phase-mark the all-ones search state using a marker prepared in |->."""
    marker.flipIf(search)



def diffuser(search):
    """Apply Grover's diffusion operator to the search qubits."""
    
    for current_qubit in search:
        current_qubit.mix()
        current_qubit.flip()

    # Apply a phase when all transformed qubits are 1.
    search[-1].phaseIf(search[:-1])

    for current_qubit in search:
        current_qubit.flip()
        current_qubit.mix()



def main():
    """Run one Grover iteration on two search qubits using Qitker.

    Print the measurement report, select the most frequent non-leakage
    outcome, and read the selected values of both search qubits.
    """
    
    #creating circuit
    network = circuit()

    first_network = qubit(network)
    second_network = qubit(network)
    
    marker = qubit(network,initialize=1, measured=False)

    #prepering qubits for circuit   
    first_network.mix()
    second_network.mix()

    #prepering marker qubit for circuit
    marker.mix()

    oracle([first_network, second_network], marker)

    diffuser([first_network, second_network])


    network.draw()

    result = network.measure(shots=1024)
    print(result)

    best = result.selectResult(rank=1)
    print(f"Most frequent result: {best}")
    print(f"First bit: {first_network.getValue()}")
    print(f"Second bit: {second_network.getValue()}")



main()
