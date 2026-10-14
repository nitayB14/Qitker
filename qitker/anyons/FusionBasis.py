from qitker.anyons.Anyon import Anyon, Charge, fusion_outcomes
from qitker.anyons.FusionTree import FusionTree
from qitker.anyons.AnyonicQubit import AnyonicQubit


class FusionBasis:
    """
    Describes a fusion basis for one FusionTree topology.

    The basis stores metadata and index mappings only. Quantum amplitudes
    belong to HilbertSpace and are not stored here.

    Attributes:
        qubits_num:
            Number of logical four-anyon qubits represented by the basis.
        tree_signature:
            Snapshot of the anyon-ID tree topology used to build the basis.
        qubit_paths:
            Paths to each qubit root and its left and right fusion pairs.
        states:
            Valid fusion-charge labelings with the requested total charge.
        state_to_index:
            Reverse mapping from an immutable state key to its basis index.
        computational_indices:
            Indices whose logical-qubit block totals are all vacuum.
        leakage_indices:
            Valid physical indices outside the computational subspace.
        logical_to_physical:
            Maps a logical bitstring to its physical fusion-basis index.
        physical_to_logical:
            Maps a computational physical index back to its bitstring.
    """

    def __init__(
        self,
        tree: FusionTree,
        qubits: list[AnyonicQubit],
        total_charge: Charge = Charge.VACUUM,
        classify_logical: bool = True,
    ):
        """Build the fusion basis for the given tree and logical qubits.

        Enumerates valid fusion-charge labelings and keeps those with the
        requested total charge. Optionally classifies the resulting states
        as computational or leakage states and builds logical index mappings.

        Args:
            tree: The fusion tree whose current structure defines the basis.
            qubits: Logical qubits ordered by ID from 0 to n-1.
            total_charge: Required charge at the root; defaults to VACUUM.
            classify_logical: Whether to build qubit paths and classify the
                physical states. The physical basis is built either way.

        Raises:
            TypeError: If an argument has an invalid type.
            ValueError: If the tree, qubits, or charge are incompatible, or
                the resulting basis contains duplicate physical or
                logical states.
        """
        self._validate_inputs(tree, qubits, total_charge)

        if not isinstance(classify_logical, bool):
            raise TypeError(
                "classify_logical must be a boolean."
            )

        # Objects that define which physical fusion space this basis describes.
        self._tree = tree
        self._qubits = qubits
        self.qubits_num = len(self._qubits)
        self._total_charge = total_charge
        self.classify_logical = classify_logical

        # Snapshot and path metadata for the current tree topology.
        self.tree_signature = tree.to_ids()
        self.qubit_paths = {}

        # Ordered physical basis and its reverse index lookup.
        self.states = []
        self.state_to_index = {}

        # Partition of the physical basis into logical and leakage subspaces.
        self.computational_indices = []
        self.leakage_indices = []

        # Translation between logical bitstrings and physical basis indices.
        self.logical_to_physical = {}
        self.physical_to_logical = {}

        if self.classify_logical:
            self._build_qubit_paths()

        # Enumerate valid fusion channels, then keep states with the
        # requested charge at the root.
        all_states = self._enumerate_subtree(
            self._tree.structure
        )

        self.states = [state for state in all_states if state["total"] is self._total_charge]

        # Index each state by its internal-node labels for fast lookup.
        self.state_to_index = {
            self._state_key(state["labels"]): index
            for index, state in enumerate(self.states)
        }

        if len(self.state_to_index) != len(self.states):
            raise ValueError(
                "Fusion basis contains duplicate states."
            )

        # Map computational states to logical bits; keep the remaining
        # physical states classified as leakage.
        if self.classify_logical:
            self._classify_states()



    @staticmethod
    def _validate_inputs(
        tree: FusionTree,
        qubits: list[AnyonicQubit],
        total_charge: Charge,
    ) -> None:
        """
        Validate that the tree, qubits, and total charge describe one system.

        Checks that qubits have consecutive IDs, their anyons are distinct TAU
        anyons, and the tree contains exactly the same anyon IDs. If the tree
        specifies a total charge, it must match total_charge.

        Args:
            tree: The fusion tree to validate.
            qubits: Logical qubits ordered by ID from 0 to n-1.
            total_charge: The required total charge.

        Raises:
            TypeError: If an argument or tree leaf has an invalid type.
            ValueError: If the qubits are empty, IDs are duplicated or out of
                order, charges are incompatible, or tree and qubit IDs differ.
        """

        if not isinstance(tree, FusionTree):
            raise TypeError("tree must be a FusionTree object.")

        if not isinstance(qubits, list):
            raise TypeError("qubits must be a list.")

        if not qubits:
            raise ValueError("qubits must contain at least one logical qubit.")

        if not all(isinstance(qubit, AnyonicQubit) for qubit in qubits):
            raise TypeError(
                "Every element in qubits must be an AnyonicQubit object."
            )

        if not isinstance(total_charge, Charge):
            raise TypeError("total_charge must be a Charge value.")

        if (
            tree.total_charge is not None
            and tree.total_charge is not total_charge
        ):
            raise ValueError(
                "total_charge must match the FusionTree total charge."
            )

        qubit_ids = [qubit.qubit_id for qubit in qubits]

        if len(qubit_ids) != len(set(qubit_ids)):
            raise ValueError("Logical qubit IDs must be unique.")

        if qubit_ids != list(range(len(qubits))):
            raise ValueError(
                "Logical qubits must be ordered with IDs from 0 to n-1."
            )

        qubit_anyons = [
            anyon
            for qubit in qubits
            for anyon in qubit.anyons
        ]
        qubit_anyon_ids = [anyon.get_id() for anyon in qubit_anyons]

        if len(qubit_anyon_ids) != len(set(qubit_anyon_ids)):
            raise ValueError("An anyon cannot belong to multiple qubits.")

        if not all(anyon.get_charge() is Charge.TAU for anyon in qubit_anyons):
            raise ValueError(
                "Every physical anyon in the four-anyon encoding must be TAU."
            )

        tree_anyons = tree.flatten()

        if not all(isinstance(anyon, Anyon) for anyon in tree_anyons):
            raise TypeError("Every FusionTree leaf must be an Anyon object.")

        tree_anyon_ids = [anyon.get_id() for anyon in tree_anyons]

        if len(tree_anyon_ids) != len(set(tree_anyon_ids)):
            raise ValueError("FusionTree anyon IDs must be unique.")

        if set(tree_anyon_ids) != set(qubit_anyon_ids):
            raise ValueError(
                "FusionTree leaves must match the anyons owned by qubits."
            )


    @staticmethod
    def _common_path(paths: list[tuple]) -> tuple:
        """
        Return the longest prefix shared by all paths.

        The result is the path to the deepest common ancestor of the
        corresponding nodes. Returns an empty tuple if the paths have
        no shared first step.

        Args:
            paths: A non-empty list of paths from the tree root.

        Returns:
            tuple: The longest common path prefix.

        Raises:
            ValueError: If paths is empty.
        """

        if not paths:
            raise ValueError(
                "paths must contain at least one path."
            )

        common = []

        for directions in zip(*paths):
            if len(set(directions)) != 1:
                break

            common.append(directions[0])

        return tuple(common)


    def _build_qubit_paths(self) -> None:
        """
        Build the tree paths used to classify each logical qubit.

        Divides the current left-to-right leaf order into blocks of four anyons.
        For each block, stores the common path of all four leaves ("root"),
        the first two ("left_pair"), and the last two ("right_pair") in
        self.qubit_paths.

        The blocks are determined by current leaf positions, not by the
        anyons originally assigned to each qubit.

        Raises:
            ValueError: If a block does not contain four anyons or one of
                its leaves cannot be found in the tree.
        """
        current_anyons = self._tree.flatten()
        qubit_paths = {}

        for qubit_id in range(self.qubits_num):
            start = 4 * qubit_id
            end = start + 4
            block_anyons = current_anyons[start:end]

            if len(block_anyons) != 4:
                raise ValueError(
                    f"Qubit block {qubit_id} does not contain "
                    "exactly four anyons."
                )

            leaf_paths = [
                self._tree.find_path(anyon.get_id())
                for anyon in block_anyons
            ]

            if any(path is None for path in leaf_paths):
                raise ValueError(
                    f"Qubit block {qubit_id} was not found "
                    "completely in the fusion tree."
                )

            qubit_paths[qubit_id] = {
                "root": self._common_path(leaf_paths),
                "left_pair": self._common_path(leaf_paths[:2]),
                "right_pair": self._common_path(leaf_paths[2:]),
            }

        self.qubit_paths = qubit_paths

    def _enumerate_subtree(
        self,
        node,
        path: tuple = (),
    ) -> list[dict]:
        """
        Enumerate all valid fusion-charge labelings of a subtree.

        For each combination of left and right child states, applies the
        Fibonacci fusion rules and creates a state for every allowed outcome
        at the current node. Leaf charges come from the Anyon objects.

        Args:
            node:
                The subtree or Anyon leaf to enumerate.
            path:
                Path from the tree root to node. Used as the key for its
                fusion charge when node is internal.

        Returns:
            list[dict]: Possible states of the subtree. Each state contains
                "total", its resulting charge, and "labels", a mapping from
                internal-node paths to charges.
        """
        if not isinstance(node, tuple):
            return [
                {
                    "total": node.get_charge(),
                    "labels": {},
                }
            ]

        left_states = self._enumerate_subtree(
            node[0],
            path + (0,),
        )

        right_states = self._enumerate_subtree(
            node[1],
            path + (1,),
        )

        states = []

        # Combine every pair of child states, creating one state for
        # each charge allowed by the fusion rules.
        for left_state in left_states:
            for right_state in right_states:
                outcomes = fusion_outcomes(
                    left_state["total"],
                    right_state["total"],
                )

                for total_charge in outcomes:
                    states.append({
                        "total": total_charge,
                        "labels": {
                            **left_state["labels"],
                            **right_state["labels"],
                            path: total_charge,
                        },
                    })

        return states



    def get_reindex_map(self, new_basis: "FusionBasis",) -> tuple[int, ...]:
        """
        Map this basis's physical indices to matching indices in another basis.

        States are matched by their internal-node charge labels. This
        reorders amplitudes when both bases contain the same labeled states;
        it does not apply an F-move transformation.

        Args:
            new_basis:
                The basis to map into.

        Returns:
            tuple[int, ...]: A mapping where result[old_index] is the
                corresponding index in new_basis.

        Raises:
            TypeError: If new_basis is not a FusionBasis.
            ValueError: If the dimensions differ, a state is missing from
                new_basis, or the mapping is not one-to-one.
        """

        if not isinstance(new_basis, FusionBasis):
            raise TypeError(
                "new_basis must be a FusionBasis object."
            )

        if len(self.states) != len(new_basis.states):
            raise ValueError(
                "Fusion bases have different dimensions."
            )

        reindex_map = []

        for state in self.states:
            try:
                new_index = new_basis.get_index(state)
            except ValueError as error:
                raise ValueError(
                    "Fusion bases do not contain the same "
                    "fusion-label states."
                ) from error

            reindex_map.append(new_index)

        if len(set(reindex_map)) != len(reindex_map):
            raise ValueError(
                "Fusion-basis mapping is not one-to-one."
            )

        return tuple(reindex_map)


    def get_charge_at_path(
        self,
        state: dict,
        path: tuple,
    ) -> Charge:
        """
        Return the fusion charge at a path in the current tree.

        For an Anyon leaf, reads its fixed charge from the Anyon object.
        For an internal node, reads the charge assigned to that path in
        the given basis state.

        Args:
            state:
                A basis state containing internal-node charges in "labels".
            path:
                Path from the tree root to the requested node.

        Returns:
            Charge: The charge of the leaf or internal node.

        Raises:
            TypeError: If state is not a dictionary or path is not a tuple.
            ValueError: If the path does not exist or an internal-node
                charge is missing from the state.
        """

        if not isinstance(state, dict):
            raise TypeError("state must be a dictionary.")

        if not isinstance(path, tuple):
            raise TypeError("path must be a tuple.")

        node = self._tree.get_node_at_path(path)

        if node is None:
            raise ValueError("path does not exist in the fusion tree.")

        if isinstance(node, tuple):
            if path not in state["labels"]:
                raise ValueError(
                    "state does not contain the internal-node label."
                )

            return state["labels"][path]

        return node.get_charge()


    def get_cluster_labels(self, state: dict) -> dict:
        """
        Map each internal anyon cluster to its fusion charge in a state.

        Traverses the tree structure saved when this basis was built.
        Each key is a frozenset of the anyon IDs below an internal node;
        its value is that node's charge from state["labels"].

        Args:
            state:
                A basis state containing charges for the internal nodes.

        Returns:
            dict: A new mapping from anyon-ID clusters to their charges.

        Raises:
            TypeError: If state is not a dictionary.
            ValueError: If state has no "labels" entry or a charge is
                missing for an internal node.
        """

        if not isinstance(state, dict):
            raise TypeError("state must be a dictionary.")

        if "labels" not in state:
            raise ValueError("state must contain labels.")

        cluster_labels = {}

        def visit(node, path):
            if not isinstance(node, tuple):
                return frozenset((node,))

            left_ids = visit(node[0], path + (0,))
            right_ids = visit(node[1], path + (1,))
            cluster = left_ids | right_ids

            if path not in state["labels"]:
                raise ValueError(
                    "state does not contain all tree labels."
                )

            cluster_labels[cluster] = state["labels"][path]
            return cluster

        visit(self.tree_signature, ())
        return cluster_labels


    @staticmethod
    def _state_key(labels: dict) -> tuple:
        """
        Convert internal-node labels into a consistent lookup key.

        Sorts the (path, charge) pairs by path, so dictionaries with the
        same labels produce the same key regardless of insertion order.

        Args:
            labels:
                A mapping from internal-node paths to their charges.

        Returns:
            tuple: The sorted (path, charge) pairs.

        Raises:
            TypeError: If labels is not a dictionary.
        """
        if not isinstance(labels, dict):
            raise TypeError(
                "labels must be a dictionary."
            )

        return tuple(
            sorted(
                labels.items(),
                key=lambda item: item[0],
            )
        )


    def get_state(self, index: int) -> dict:
        """
        Return the basis state at a physical index.

        Returns the stored dictionary itself, without copying it.
        Changing the returned dictionary would change the basis data.

        Args:
            index:
                A physical basis index.

        Returns:
            dict: The state and its internal-node charge labels.

        Raises:
            TypeError: If index is not an integer or is a boolean.
            IndexError: If index is outside the basis.
        """

        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(
                "index must be an integer."
            )

        if index < 0 or index >= len(self.states):
            raise IndexError(
                "basis state index is out of range."
            )

        return self.states[index]


    def get_index(self, state: dict) -> int:
        """
        Return the physical basis index of a state.

        Looks up the state by its internal-node charge labels. The state's
        "total" field is not used for this lookup.

        Args:
            state:
                A state containing a "labels" dictionary.

        Returns:
            int: The state's index in this basis.

        Raises:
            TypeError: If state is not a dictionary.
            ValueError: If "labels" is missing or its labels do not match
                a state in this basis.
        """
        if not isinstance(state, dict):
            raise TypeError(
                "state must be a dictionary."
            )

        if "labels" not in state:
            raise ValueError(
                "state must contain labels."
            )

        key = self._state_key(state["labels"])

        if key not in self.state_to_index:
            raise ValueError(
                "state does not belong to this fusion basis."
            )

        return self.state_to_index[key]


    def _is_computational(self, state: dict) -> bool:
        """
        Return whether a physical state belongs to the computational subspace.

        A state is computational when the fusion charge at the root of
        every four-anyon qubit block is VACUUM. Assumes qubit_paths has
        already been built for the current tree structure.

        Args:
            state:
                A basis state containing internal-node charges in "labels".

        Returns:
            bool: True if every qubit block has VACUUM total charge.
        """
        return all(
            state["labels"][paths["root"]]
            is Charge.VACUUM
            for paths in self.qubit_paths.values()
        )


    def _get_logical_label(self, state: dict) -> str:
        """
        Decode the bitstring represented by a computational basis state.

        For each qubit block, the left pair's fusion charge encodes one
        bit: VACUUM is "0" and TAU is "1". Bits are returned in qubit-ID
        order, from 0 to n-1.

        Args:
            state:
                A basis state containing internal-node charges in "labels".

        Returns:
            str: The logical bitstring represented by the state.

        Raises:
            ValueError: If the state is outside the computational subspace.
        """

        if not self._is_computational(state):
            raise ValueError(
                "Cannot decode a leakage state."
            )

        bits = []

        for paths in self.qubit_paths.values():
            left_pair_charge = state["labels"][
                paths["left_pair"]
            ]

            bit = (
                "0"
                if left_pair_charge is Charge.VACUUM
                else "1"
            )

            bits.append(bit)

        return "".join(bits)


    def _classify_states(self) -> None:
        """
        Classify physical basis states and build logical index mappings.

        Adds each state's index to computational_indices or leakage_indices.
        For computational states, maps the decoded bitstring to its physical
        index and builds the reverse mapping. Leakage states remain in states.

        Assumes qubit_paths has been built and the classification containers
        are empty.

        Raises:
            ValueError: If two computational states decode to the same
                logical bitstring.
        """

        for index, state in enumerate(self.states):
            if not self._is_computational(state):
                self.leakage_indices.append(index)
                continue

            logical_label = self._get_logical_label(state)

            if logical_label in self.logical_to_physical:
                raise ValueError(
                    f"Duplicate logical state: {logical_label}."
                )

            self.computational_indices.append(index)
            self.logical_to_physical[logical_label] = index
            self.physical_to_logical[index] = logical_label
