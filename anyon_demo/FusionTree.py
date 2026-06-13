





class FusionTree:

    def __init__(self, anyons, total_charge=None):
        if (len(anyons) != 4):
            raise ValueError(f"Invalid size {len(anyons)}")
        
        self.structure = ((anyons[0],anyons[1]),(anyons[2], anyons[3]))
        self.total_charge = total_charge
###########################################################################################################

    def is_siblings(self, first_id, second_id):   
        return self.fibonnaci_are_siblings(self.structure, first_id, second_id)

    def fibonnaci_are_siblings(self, my_tuple, anyon1, anyon2):

        validate = False
        count = 0

        if(anyon1 == anyon2):
            return False

        for item in my_tuple:
            if isinstance(item, tuple):
                validate = self.fibonnaci_are_siblings(item, anyon1, anyon2)
            else:
                if item.get_id() == anyon1 or item.get_id() == anyon2:
                    count += 1
            
            if count == 2 or validate:
                return True

        return validate
    

 ###########################################################################################################      
    def get_anyon(self, anyon_id):
        for i in self.structure:
            for j in i:
                if anyon_id == j.get_id():
                    return j

    def flatten(self, obj):
        result = []

        if isinstance(obj, tuple):
            for item in obj:
                result.extend(self.flatten(item))
        else:
            result.append(obj)

        return result

###########################################################################################################
    def RMove(self, id1, id2):
        self.structure = self.swap_siblings(self.structure, id1, id2)
    
    def swap_siblings(self, tree, id1, id2):
        if not self.is_siblings(id1, id2):
            print("Not siblings — need F move before R")
            return tree

        def swap_recursive(node):
            if not isinstance(node, tuple):
                return node

            left, right = node

            if not isinstance(left, tuple) and not isinstance(right, tuple):
                if {left.get_id(), right.get_id()} == {id1, id2}:
                    return (right, left)

            return tuple(swap_recursive(x) for x in node)

        return swap_recursive(tree)
    
###########################################################################################################
    def getMiddleId(self):        
        return self.structure[0][1].get_id(),self.structure[1][0].get_id()
    def getLeftId(self):
        return self.structure[0][0].get_id(),self.structure[0][1].get_id()
    def getRightId(self):
        return self.structure[1][0].get_id(),self.structure[1][1].get_id()
###########################################################################################################
    def FMove(self):
        obj = self.flatten(self.structure)
        self.to_left_chain(obj)
        self.make_middle_pair(obj)

    def undoFmove(self):
        obj = self.flatten(self.structure)
        self.to_left_chain(obj)
        self.to_pair_basis(obj)

    def to_left_chain(self, obj):
        self.structure = (((obj[0], obj[1]), obj[2]), obj[3])

    def make_middle_pair(self, obj):
        self.structure = ((obj[0], (obj[1], obj[2])), obj[3])

    def to_pair_basis(self, obj):
        self.structure = ((obj[0], obj[1]), (obj[2], obj[3]))



###########################################################################################################
    def __str__(self):
        return f"{self.structure}"
###########################################################################################################






