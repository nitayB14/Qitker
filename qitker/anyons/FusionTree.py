
class FusionTree:
    """
    Represents the binary fusion-tree structure of Fibonacci anyons.

    Internal nodes are nested (left, right) tuples, and leaves are
    Anyon objects. The tree stores the grouping and order of the anyons.

    Tree operations modify only the structure; they do not transform
    the quantum state.
    """

    def __init__(self, structure, total_charge=None):
        """
        Initializes a fusion tree with the given structure and optional total charge.

        Args:
            structure:
                An Anyon leaf or nested (left, right) tuples of Anyon leaves.
                Stored directly without copying.
            total_charge:
                Optional total charge associated with the tree.
                Stored without validating fusion compatibility.

        Raises:
            ValueError: If structure is None.
        """

        if structure is None:
            raise ValueError("Fusion-tree structure cannot be None.")

        self.structure = structure
        self.total_charge = total_charge
    

    def flatten(self, node=None):
        """
        Returns the anyon objects in left-to-right leaf order.

        Args:
            node:
                The subtree or leaf to traverse. If None, uses the entire tree.

        Returns:
            list: A new list containing the existing Anyon objects.
        """

        if node is None:
            node = self.structure

        if not isinstance(node, tuple):
            return [node]

        result = []

        for child in node:
            result.extend(self.flatten(child))

        return result



    #############################################################


    def find_path(self, anyon_id):
        """
        Returns the path from the root to the anyon with the given ID.
        Each path value is 0 for left or 1 for right.

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
        Searches a subtree recursively, visiting the left branch before the right.

        Args:
            node:
                The current subtree or Anyon leaf.
            anyon_id:
                The ID of the anyon to find.
            current_path:
                The path from the tree root to the current node.

        Returns:
            tuple: The path to the first matching anyon.
            None: If the anyon was not found in this subtree.
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
        Returns the node at the given path from the root.

        Each path value should be 0 for left or 1 for right.
        An empty path returns the entire tree structure.

        Args:
            path (tuple):
                The sequence of directions from the root.

        Returns:
            Anyon or tuple: The leaf or subtree at the given path.
            None: If the path continues beyond an Anyon leaf.
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


    def _swap_siblings(self, first_id, second_id):
        """
        Swaps two direct sibling anyons in the tree structure.

        Updates self.structure without applying R-move phases
        to the quantum state.

        Args:
            first_id:
                The ID of the first anyon.
            second_id:
                The ID of the second anyon.

        Raises:
            ValueError: If the IDs do not identify two distinct direct siblings.
        """

        if not self.is_siblings(first_id, second_id):
            
            raise ValueError(
                f"Anyons {first_id} and {second_id} "
                "are not direct siblings."
            )

        first_path = self.find_path(first_id)
        parent_path = first_path[:-1]

        parent = self.get_node_at_path(parent_path)
        left, right = parent

        self.structure = self._replace_node_at_path(
            parent_path,
            (right, left)
        )


    def _replace_node_at_path(self, path, replacement):
        """
        Returns a tree structure with the node at the given path replaced.

        Rebuilds the tuples along the path without modifying self.structure.
        Unchanged subtrees and Anyon objects are reused.

        Args:
            path (tuple):
                Directions from the root: 0 for left and 1 for right.
                An empty path replaces the root.
            replacement:
                The leaf or subtree to insert.

        Returns:
            The resulting tree structure.

        Raises:
            ValueError: If the path continues beyond a leaf or contains
                a value other than 0 or 1.
        """

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
        Applies the structural part of an F-move at the given path.

        Updates self.structure while preserving the left-to-right leaf order.
        Does not transform the fusion basis or quantum state.

        Args:
            path (tuple):
                Directions from the root: 0 for left and 1 for right.
                An empty path selects the root.
            direction (str):
                "right": ((a, b), c) -> (a, (b, c)).
                "left": (a, (b, c)) -> ((a, b), c).
                Each component may be a leaf or subtree.

        Raises:
            ValueError: If the target is not a subtree, its structure is
                incompatible with the move, or the direction is invalid.
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
        Returns a subtree regrouped from ((a, b), c) to (a, (b, c)).

        The components a, b, and c may be leaves or subtrees.
        Does not modify self.structure.

        Args:
            subtree (tuple):
                The subtree to regroup.

        Returns:
            tuple: The regrouped subtree.

        Raises:
            ValueError: If the subtree does not have the required structure.
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
        Returns a subtree regrouped from (a, (b, c)) to ((a, b), c).

        The components a, b, and c may be leaves or subtrees.
        Does not modify self.structure.

        Args:
            subtree (tuple):
                The subtree to regroup.

        Returns:
            tuple: The regrouped subtree.

        Raises:
            ValueError: If the subtree does not have the required structure.
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




#return basic information about the fution tree

    def to_ids(self):
        """
        Returns the tree structure with each Anyon leaf replaced by its ID.

        Preserves the nested tuple structure without modifying the tree.
        """

        return self._to_ids_recursive(self.structure)


    def _to_ids_recursive(self, node):
        """
        Recursively converts Anyon leaves to IDs while preserving tuple structure.

        Args:
            node:
                The subtree or Anyon leaf to convert.

        Returns:
            tuple or int: The converted subtree or the leaf's ID.
        """
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



