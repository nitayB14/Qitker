import circuit
import operation


op = operation.operation()


"""
class qubit - responsible on the qubit itself, calls to operation and manage the qubit
              locate the qubit to a circuit, initialize with |0> or |1> or with H gate

"""
class qubit:

    def __init__(self, quantumCircuit, initialize = None):

        if(type(quantumCircuit) == circuit.circuit):
            self.quantumCircuit = quantumCircuit
            self.quantumCircuit.addQubit(self)
            self.initialize = initialize
            if initialize == None: #if user have not choose to initialize we apply H gate
                op.applyHadamard(self, self.quantumCircuit)
            elif initialize == 0:
                pass #already initialize to 0s
            elif initialize == 1:
                self.flip() #apply not gate to initialize as 1
            else:
                print("number too big throw exception")

        else:
            print("throw error")
    #####################################################################################

    
    def H(self):
        op.applyHadamard(self, self.quantumCircuit)
    #####################################################################################


    def swap(self, control):
        op.applyCNOT(control, self, self.quantumCircuit)
        op.applyCNOT(self, control, self.quantumCircuit)
        op.applyCNOT(control, self, self.quantumCircuit)
    #####################################################################################

    #X gate
    def flip(self):
        op.applyNOT(self, self.quantumCircuit)

    def flipIf(self, *args):
        #add cnot for 3 or more controls
        if len(args) == 1:
            control = args[0]
            op.applyCNOT(control, self, self.quantumCircuit)
        elif len(args) == 2:
            control1, control2 = args
            op.applyCCNOT(control1, control2, self, self.quantumCircuit)
        else:
            print("error")
    #####################################################################################

    #Y gate
    def flipY(self):
        op.applyY(self, self.quantumCircuit)

    def flipYIf(self, *args):
        #add cnot for 3 or more controls
        if len(args) == 1:
            control = args[0]
            op.applyCY(control, self, self.quantumCircuit)
        elif len(args) == 2:
            control1, control2 = args
            op.applyCCY(control1, control2, self, self.quantumCircuit)
        else:
            print("error")
    #####################################################################################

    #Z gate
    def flipZ(self):
        op.applyZ(self, self.quantumCircuit)

    def flipZIf(self, *args):
        #add cnot for 3 or more controls
        if len(args) == 1:
            control = args[0]
            op.applyCZ(control, self, self.quantumCircuit)
        elif len(args) == 2:
            control1, control2 = args
            op.applyCCZ(control1, control2, self, self.quantumCircuit)
        else:
            print("error")

    #####################################################################################

    #S gate
    def flipS(self):
        op.applyS(self, self.quantumCircuit)

    def flipSIf(self, *args):
        #add cnot for 3 or more controls
        if len(args) == 1:
            control = args[0]
            op.applyCS(control, self, self.quantumCircuit)
        elif len(args) == 2:
            control1, control2 = args
            op.applyCCS(control1, control2, self, self.quantumCircuit)
        else:
            print("error")

    #####################################################################################

    #T gate
    def flipT(self):
        op.applyT(self, self.quantumCircuit)

    def flipTIf(self, *args):
        #add cnot for 3 or more controls
        if len(args) == 1:
            control = args[0]
            op.applyCT(control, self, self.quantumCircuit)
        elif len(args) == 2:
            control1, control2 = args
            op.applyCCT(control1, control2, self, self.quantumCircuit)
        else:
            print("error")


    def __invert__(self):
        self.flip()


    def __str__(self):
        return f"index: {self.quantumCircuit.getIndex(self)}, initialize: {self.initialize}"