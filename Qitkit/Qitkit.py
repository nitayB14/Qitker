from compiler.qubit import qubit
from compiler.circuit import circuit



def main():
    cirq = circuit()
    
    q1 = qubit(cirq, 0)
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    q1.T_gate()
    
    
    cirq.details()
    cirq.execute()

    comp, results = cirq.measure(1000)
    
    print(comp)
    print(results)





if __name__ == "__main__":
    main()