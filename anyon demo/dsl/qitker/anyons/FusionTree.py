
class FusionTree:
    """
    Represents the fusion tree structure of four Fibonacci anyons.              
    """

    # Initializes a fusion tree with four anyons and an optional total charge.
    def __init__(self, structure, total_charge=None):
        if structure is None:
            raise ValueError("Fusion-tree structure cannot be None.")

        self.structure = structure
        self.total_charge = total_charge
    

    def flatten(self, node=None):
        """
        Returns all anyons in the fusion tree as a flat list.
        """

        if node is None:
            node = self.structure

        if not isinstance(node, tuple):
            return [node]

        result = []

        for child in node:
            result.extend(self.flatten(child))

        return result



    def get_anyon(self, anyon_id):
        """
        Returns the anyon object matching the given ID
        """
        stractureFlat = self.flatten()

        for anyon in stractureFlat:
            if anyon_id == anyon.get_id():
                return anyon
        return None
    #############################################################


    def find_path(self, anyon_id):
        """
        Returns the path from the root to the anyon with the given ID.

        Path values:
            0 -> left
            1 -> right

        Returns:
            tuple: path to the anyon
            None: if the anyon was not found
        """

        return self._find_path_recursive(
            self.structure,
            anyon_id,
            ()
        )
    
    def _find_path_recursive(self, node, anyon_id, current_path):
        """
        Recursively searches for an anyon and builds its path.
        """

        # Reached an anyon leaf.
        if not isinstance(node, tuple):
            if node.get_id() == anyon_id:
                return current_path

            return None

        left, right = node

        # Search the left subtree.
        path = self._find_path_recursive(
            left,
            anyon_id,
            current_path + (0,)
        )

        if path is not None:
            return path

        # Search the right subtree.
        return self._find_path_recursive(
            right,
            anyon_id,
            current_path + (1,)
        )


    def get_node_at_path(self, path):
        """
        Returns the node located at the given path.

        Path values:
            0 -> left
            1 -> right

        Args:
            path (tuple): Path from the root.

        Returns:
            Anyon or subtree.
        """

        node = self.structure

        for direction in path:

            if not isinstance(node, tuple):
                return None

            node = node[direction]

        return node
    #############################################################

    def is_siblings(self, first_id, second_id):
        """
        Checks whether two anyons are direct siblings
        in the fusion tree.

        Args:
            first_id:
                ID of the first anyon.

            second_id:
                ID of the second anyon.

        Returns:
            True if both anyons have the same direct parent,
            otherwise False.
        """

        if first_id == second_id:
            return False

        first_parent = self.find_parent(first_id)
        second_parent = self.find_parent(second_id)

        if first_parent is None or second_parent is None:
            return False

        return first_parent == second_parent

    def find_parent(self, anyon_id):
        """
        Returns the direct parent of the anyon with the given ID.

        Args:
            anyon_id:
                The ID of the target anyon.

        Returns:
            The direct parent subtree, or None if the anyon
            has no parent.
        """

        path = self.find_path(anyon_id)

        if path is None:
            return None

        if len(path) == 0:
            return None

        parent_path = path[:-1]

        return self.get_node_at_path(parent_path)




    def RMove(self, first_id, second_id):
        self._swap_siblings(first_id, second_id)


    def undoRMove(self, first_id, second_id):
        self._swap_siblings(first_id, second_id)


    def _swap_siblings(self, first_id, second_id):
        if not self.is_siblings(first_id, second_id):
            """
            raise ValueError(
                f"Anyons {first_id} and {second_id} "
                "are not direct siblings."
            )"""

        first_path = self.find_path(first_id)
        parent_path = first_path[:-1]

        parent = self.get_node_at_path(parent_path)
        left, right = parent

        self.structure = self._replace_node_at_path(
            parent_path,
            (right, left)
        )


    def _replace_node_at_path(self, path, replacement):
        def replace_recursive(node, remaining_path):
            if len(remaining_path) == 0:
                return replacement

            if not isinstance(node, tuple):
                raise ValueError(
                    "Path continues beyond an anyon leaf."
                )

            direction = remaining_path[0]
            rest = remaining_path[1:]

            left, right = node

            if direction == 0:
                return (
                    replace_recursive(left, rest),
                    right
                )

            if direction == 1:
                return (
                    left,
                    replace_recursive(right, rest)
                )

            raise ValueError(
                "Path values must be either 0 or 1."
            )

        return replace_recursive(self.structure, path)





    ##########################################################################################

    def FMove(self, path, direction):


        """
        Applies a local F-move at the given subtree.

        direction:
            "right":
                ((a, b), c) -> (a, (b, c))

            "left":
                (a, (b, c)) -> ((a, b), c)
        """

        subtree = self.get_node_at_path(path)
        if not isinstance(subtree, tuple):
            raise ValueError("F-move target must be a subtree.")

        if direction == "right":
            new_subtree = self._rotate_right(subtree)

        elif direction == "left":
            new_subtree = self._rotate_left(subtree)

        else:
            raise ValueError(
                "direction must be 'left' or 'right'."
            )

        self.structure = self._replace_node_at_path(
            path,
            new_subtree
        )


    def _rotate_right(self, subtree):
        """
        Converts:

            ((a, b), c) -> (a, (b, c))
        """

        left, c = subtree

        if not isinstance(left, tuple):
            raise ValueError(
                "Right F-move requires structure ((a, b), c)."
            )

        a, b = left

        return (
            a,
            (b, c)
        )

    def _rotate_left(self, subtree):
        """
        Converts:

            (a, (b, c)) -> ((a, b), c)
        """

        a, right = subtree

        if not isinstance(right, tuple):
            raise ValueError(
                "Left F-move requires structure (a, (b, c))."
            )

        b, c = right

        return (
            (a, b),
            c
        )

    def undoFMove(self, path, direction):
        """
        Reverses an F-move previously applied in the given direction.
        """

        inverse_direction = (
            "left"
            if direction == "right"
            else "right"
        )

        self.FMove(path, inverse_direction)



#return basic information about the fution tree

    def to_ids(self):
        return self._to_ids_recursive(self.structure)


    def _to_ids_recursive(self, node):

        if isinstance(node, tuple):
            return tuple(
                self._to_ids_recursive(child)
                for child in node
            )

        return node.get_id()
    


    def __str__(self):
        return f"{self.structure}"

    def __repr__(self):
        return f"FusionTree(structure={self.structure!r})"



    """
        def flatten(self, obj):
        
        Converts a nested fusion tree into a flat list of anyons.
        
        result = []

        if isinstance(obj, tuple):
            for item in obj:
                result.extend(self.flatten(item))
        else:
            result.append(obj)

        return result
    """

    
    """
    def fibonacci_are_siblings(self, my_tuple, anyon1, anyon2):
        
        Recursively searches the fusion tree to determine if two anyons are siblings.
        

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
    """
   
