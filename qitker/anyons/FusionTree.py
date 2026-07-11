
class FusionTree:
    """
    Represents the fusion tree structure of four Fibonacci anyons.
    
    Attributes:
        - structure: tuple of anyons
            4 anyons that represent the qubit
        - total_charge : charge
            can be VACUUM or TAU                
    """

    # Initializes a fusion tree with four anyons and an optional total charge.
    def __init__(self, anyons, total_charge=None):
        if (len(anyons) != 4):
            raise ValueError(f"Invalid size {len(anyons)}")
        
        self.structure = ((anyons[0],anyons[1]),(anyons[2], anyons[3]))
        self.total_charge = total_charge
    

    def is_siblings(self, first_id, second_id):   
        """
        Checks whether two anyons belong to the same fusion subtree.

        Args:
            - first_id (int):
                id of the first anyon
            - second_id (int):
                id of the second anyon            
        Returns:
            - (bool) : if the anyons in the same sub group
        """

        return self.fibonacci_are_siblings(self.structure, first_id, second_id)


    def fibonacci_are_siblings(self, my_tuple, anyon1, anyon2):
        """
        Recursively searches the fusion tree to determine if two anyons are siblings.

        Args:
            - my_tuple (self.structure):
                the structure of the qubit
            - first_id (int):
                id of the first anyon
            - second_id (int):
                id of the second anyon            
        Returns:
            - (bool) : if the anyons in the same sub group
        """

        validate = False
        count = 0

        if(anyon1 == anyon2):
            return False

        for item in my_tuple:
            if isinstance(item, tuple):
                validate = self.fibonacci_are_siblings(item, anyon1, anyon2)
            else:
                if item.get_id() == anyon1 or item.get_id() == anyon2:
                    count += 1
            
            if count == 2 or validate:
                return True

        return validate
    
   
    def get_anyon(self, anyon_id):
        """
        Returns the anyon object matching the given ID

        Args:
            - anyon_id (int):
                id of anyon

        Returns:
            - (anyon) : anyon with the same id
        """

        for i in self.structure:
            for j in i:
                if anyon_id == j.get_id():
                    return j
    

    def flatten(self, obj):
        """
        Converts a nested fusion tree into a flat list of anyons.

        Args:
            - obj (self.structure):
                tuple of anyons

        Returns:
            - (array) : tuple converted to array
        """

        result = []

        if isinstance(obj, tuple):
            for item in obj:
                result.extend(self.flatten(item))
        else:
            result.append(obj)

        return result


    def RMove(self, id1, id2):
        """
        Applies an R braid by swapping two sibling anyons.

        Args:
            - id1 (int):
                id of anyons
            - id2 (int):
                id of anyons

        Returns:
            - None
        """
        self.structure = self.swap_siblings(self.structure, id1, id2)
    
        
    def undoRMove(self, id1, id2):
        """
        Applies an R^-1 braid by swapping two sibling anyons.

        Args:
            - id1 (int):
                id of anyons
            - id2 (int):
                id of anyons

        Returns:
            - None
        """
        
        self.structure = self.swap_siblings(self.structure, id2, id1)

  
    def swap_siblings(self, tree, id1, id2):
        """
        Recursively swaps two sibling anyons inside the fusion tree.

        Args:
            -tree (self.structure):
                structure of qubit
            - id1 (int):
                id of anyons
            - id2 (int):
                id of anyons

        Returns:
            - (tree) : after swap
        """
        
        if not self.is_siblings(id1, id2):
            print("Not siblings — need F move before R")
            return tree
        
        # Traverses the fusion tree and performs the requested sibling swap.
        def swap_recursive(node):
            if not isinstance(node, tuple):
                return node

            left, right = node

            if not isinstance(left, tuple) and not isinstance(right, tuple):
                if {left.get_id(), right.get_id()} == {id1, id2}:
                    return (right, left)

            return tuple(swap_recursive(x) for x in node)

        return swap_recursive(tree)
    

    def getMiddleId(self):      # Returns the IDs of the middle anyon pair.        
        return self.structure[0][1].get_id(),self.structure[1][0].get_id()
    def getLeftId(self):        # Returns the IDs of the left anyon pair.
        return self.structure[0][0].get_id(),self.structure[0][1].get_id()
    def getRightId(self):       # Returns the IDs of the right anyon pair.
        return self.structure[1][0].get_id(),self.structure[1][1].get_id()


    def FMove(self):      
        """
        Applies an F-move transformation to the fusion tree.

        Args:
            - None
        Returns:
            - None
        """

        obj = self.flatten(self.structure)
        self.to_left_chain(obj)
        self.make_middle_pair(obj)


    def undoFmove(self):  
        """
        Reverses the previously applied F-move.

        Args:
            - None
        Returns:
            - None
        """

        obj = self.flatten(self.structure)
        self.to_left_chain(obj)
        self.to_pair_basis(obj)


    def to_left_chain(self, obj):      # Converts the fusion tree into a left-chain basis.
        self.structure = (((obj[0], obj[1]), obj[2]), obj[3])

    def make_middle_pair(self, obj):   # Reorganizes the fusion tree to form a middle anyon pair.
        self.structure = ((obj[0], (obj[1], obj[2])), obj[3])

    def to_pair_basis(self, obj):      # Converts the fusion tree back to the pair basis representation.
        self.structure = ((obj[0], obj[1]), (obj[2], obj[3]))


#return basic information about the fution tree
    def __str__(self):
        return f"{self.structure}"



