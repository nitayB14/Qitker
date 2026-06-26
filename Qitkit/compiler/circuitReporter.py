#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
class circuitReporter():


    def getHeadLine(): 
        return """==============================================\n        Fibonacci Anyons Quantum DSL     \n==============================================\nVersion: 1.0.0-alpha\nDate: 23/06/2026\nRule: Independent researcher"""
    
    def getNumberOfQubits(circuit): 
        return circuit.qubitsNumber
    
    
    def getCircuitDraw(circuit): 
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
        return len(circuit.operationVector)
        

    def getTotalBraids(exec): 
        return exec.braidsNumber

    #####################################################################################

    def getPercentage(results):
        total = sum(results.values())  # 1000
        s = ""
        for state, count in results.items():
            percent = count / total * 100
            s += (f"|{state}> : {count}  -->  ({percent:.2f}%)\n")

        return s

    def getFinalVector(execute): 
        return execute.getMatrix()


    ######################################################################################

    def getAproximationError(circuit): 
        pass