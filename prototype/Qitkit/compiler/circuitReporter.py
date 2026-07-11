#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
import subprocess



class circuitReporter():
    """
    Responsible on Anyon DSL output

    Responsibilities:
        - Outputs
    """


    def getHeadLine(): 
        """
        Information about project

        Args:
            - None

        Returns:
            - None
        """
        
        return """==============================================\n        Fibonacci Anyons Quantum DSL     \n==============================================\nVersion: 1.0.0-alpha\nDate: 23/06/2026\nRule: Independent researcher"""
    

    def getNumberOfQubits(circuit): 
        """
        Returning number of qubits

        Args:
            - circuit (circuit):

        Returns:
            - (int) number of qubits
        """

        return circuit.qubitsNumber
    
    
    def getCircuitDraw(circuit): 
        """
        Returning draw of circuit

        Args:
            - circuit (circuit):

        Returns:
            - (string) draw of circuit
        """

        s = ""
        for i in range(circuit.qubitsNumber):
            s += (f"q[{i}]:  ")
            
            for j in circuit.operationVector:
                s += f"--"                  
                if j.getTarget() == i:
                    s += j.getName()
                else:
                    s += "-"


            s += f"--"              
            s += "\n"
        
        return s


    def getTotalGates(circuit):
        """
        Returning number of total gates

        Args:
            - circuit (circuit):

        Returns:
            - (int) number of gates
        """
        
        return f"Total gates:        : {len(circuit.operationVector)}\n"
        

    def getTotalBraids(exec): 
        """
        Returning number of braids

        Args:
            - exec (execution):

        Returns:
            - (int) number of braids
        """

        return f"Total braids:       : {exec.braidsNumber}\n"
        

    
    def getPercentage(results):
        """
        Returning statistics of results

        Args:
            - results (dict):

        Returns:
            - (string) how many times each result appear
        """

        total = sum(results.values())  # 1000
        s = ""
        for state, count in results.items():
            percent = count / total * 100
            s += (f"|{state}> : {count}  -->  ({percent:.2f}%)\n")

        return str(s)


    def getFidelity(ex): 
        """
        returning fidelity of circuit

        Args:
            - ex (execution):

        Returns:
            - (float) : fidelity
        """
        
        return f"Fidelity:           : {ex.getFidelity()}"


    def printFinalMatrix(ex):
        """
        Printing final matrix

        Args:
            - ex (execution):

        Returns:
            - None
        """

        print(f"\nFinal matrix:\n{ex.getMatrix()}")
        
    
    

    def printAnyonMove(anyonMoveList):
        """
        Printing how anyons move 

        Args:
            - anyonMoveList (List):
                list of anyon places

        Returns:
            - None
        """

        for i in anyonMoveList:
            for vecId, operation in enumerate(i):
                print(f"[{vecId:05d}]:    {operation}")
        
        