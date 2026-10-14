"""Coordinate Fibonacci fusion trees, bases, state evolution, and braiding."""

import numpy as np

from qitker.anyons.Anyon import Anyon, Charge
from qitker.anyons.AnyonicQubit import AnyonicQubit
from qitker.anyons.FusionTree import FusionTree
from qitker.anyons.AnyonOperation import AnyonOperation
from qitker.QuantumMath.HilbertSpace import HilbertSpace
from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.FusionCache import FusionCache


class FusionSystem:
    """Manage a shared fusion tree, basis, and HilbertSpace for logical qubits.

    Anyon IDs are permanent identities. Braids act on current leaf positions;
    each logical block occupies four consecutive positions. Original qubit
    ownership remains available through the ID-based lookup helpers.

    F-moves regroup the tree and transform amplitudes into the new basis.
    R-moves apply channel phases and exchange sibling leaves. Public physical
    operations record history and restore their entry state on failure.
    Derived cache entries and counters are not rolled back.
    """

    BRAID_CONVENTION = "MOVING_ANYON_IDENTITIES"

    def __init__(self, qubits_num: int, cache_enabled: bool = True,):
        """Create four TAU anyons per qubit and initialize logical |00...0>.

        Builds paired qubit subtrees, a global VACUUM-charge basis, and the
        corresponding HilbertSpace. History starts empty; the cache is private
        to this system.

        Args:
            qubits_num: Number of logical qubits, from 1 to 10.
            cache_enabled: Whether to reuse derived bases and operation plans.

        Raises:
            TypeError: If an argument has an invalid type.
            ValueError: If qubits_num is outside the supported range.
        """

        if not isinstance(qubits_num, int):
            raise TypeError("qubits_num must be an integer.")

        if qubits_num < 1:
            raise ValueError("qubits_num must be at least 1.")

        if qubits_num > 10:
            raise ValueError("Number too big for simulation")

        self.cache = FusionCache(enabled=cache_enabled,)

        self.qubits_num = qubits_num
        self.anyons = []
        self.qubits = []

        self._create_anyons()
        self._create_qubits()
        self.operation_history = []

        structure = self._build_global_structure()

        self.tree = FusionTree(
            structure=structure,
            total_charge=Charge.VACUUM
        )

        self.basis = self._get_or_build_basis(classify_logical=True,)

        self.hilbertSpace = HilbertSpace(self.basis)

    def get_qubit(self, qubit_id):
        """
        Return the original AnyonicQubit object for a zero-based qubit ID.
        """

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= len(self.qubits):
            raise ValueError(f"Qubit {qubit_id} does not exist.")

        return self.qubits[qubit_id]


    def get_current_anyon_order(self) -> tuple[int, ...]:
        """
        Return anyon IDs in their current physical tree order.
        """

        return tuple(anyon.get_id()for anyon in self.tree.flatten())

    def get_anyon(self, anyon_id):
        """
        Return an Anyon by its permanent ID, regardless of current position.
        """

        if (isinstance(anyon_id, bool) or not isinstance(anyon_id, int)):
            raise TypeError("anyon_id must be an integer.")

        if anyon_id < 1 or anyon_id > len(self.anyons):
            raise ValueError(f"Anyon {anyon_id} does not exist.")

        return self.anyons[anyon_id - 1]

    def get_anyon_at_position(self, position: int) -> Anyon:
        """
        Return the anyon currently located at a one-based position.
        """

        if isinstance(position, bool) or not isinstance(position, int):
            raise TypeError(
                "position must be an integer."
            )

        anyons = self.tree.flatten()

        if position < 1 or position > len(anyons):
            raise ValueError(
                f"position must be between 1 and {len(anyons)}."
            )

        return anyons[position - 1]

    def get_current_qubit_block(self,qubit_id: int,) -> tuple[Anyon, ...]:
        """
        Return the four anyons currently occupying a zero-based qubit block.

        Selects consecutive leaves in current tree order, which may differ
        from the anyons originally assigned to that qubit.
        """

        if isinstance(qubit_id, bool) or not isinstance(qubit_id, int):
            raise TypeError(
                "qubit_id must be an integer."
            )

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(
                f"Qubit {qubit_id} does not exist."
            )

        anyons = self.tree.flatten()

        start = 4 * qubit_id
        end = start + 4

        return tuple(anyons[start:end])

    def _capture_state_snapshot(self) -> dict:
        """
        Capture the physical state needed to roll back a braid or F/R move.

        Copies the statevector and local braid matrices, shallow-copies
        history, and retains tree-structure and basis references. Cache data
        and the separate ideal reference state are not part of the snapshot.
        """

        return {
            "tree_structure": self.tree.structure,
            "basis": self.basis,
            "hilbert_basis": self.hilbertSpace.basis,
            "state_vector": (self.hilbertSpace.state_vector.copy()),
            "dimension": self.hilbertSpace.dimension,
            "operation_history": (self.operation_history.copy()),
            "local_braid_operators": [operator.copy() for operator in self.hilbertSpace.local_braid_operators],
        }

    def _restore_state_snapshot(self, snapshot: dict,) -> None:
        """
        Restore physical state, history, and local braids from a snapshot.

        Cache contents and the ideal reference state are left unchanged.
        """

        self.tree.structure = snapshot["tree_structure"]
        self.basis = snapshot["basis"]
        self.hilbertSpace.basis = snapshot["hilbert_basis"]
        self.hilbertSpace.state_vector = snapshot["state_vector"]
        self.hilbertSpace.dimension = snapshot["dimension"]
        self.operation_history = snapshot["operation_history"]
        self.hilbertSpace.local_braid_operators = [operator.copy() for operator in snapshot["local_braid_operators"]]


    def get_qubit_of_anyon(self, anyon_id):
        """
        Return the qubit originally assigned to the given permanent anyon ID.

        Uses the initial four-ID grouping, not the anyon's current position.
        """

        anyon = self.get_anyon(anyon_id)

        qubit_id = (anyon.get_id() - 1) // 4

        return self.get_qubit(qubit_id)

    def are_same_qubit(self, first_id, second_id):
        """
        Return whether the anyon IDs share the same original qubit owner.
        """

        first_qubit = self.get_qubit_of_anyon(first_id)
        second_qubit = self.get_qubit_of_anyon(second_id)

        return first_qubit.qubit_id == second_qubit.qubit_id

    def are_neighbor_qubits(self, first_id, second_id):
        """
        Return whether the original qubit owners have consecutive IDs.
        """

        first_qubit = self.get_qubit_of_anyon(first_id)
        second_qubit = self.get_qubit_of_anyon(second_id)

        return abs(first_qubit.qubit_id - second_qubit.qubit_id) == 1

    def get_local_pair_type(self, first_id, second_id):
        """
        Return 'left', 'middle', or 'right' for an original local anyon pair.

        Uses permanent IDs within their initial four-anyon group, ignoring
        argument order. Returns None if they are not consecutive within the
        same original group. Does not inspect current tree positions.
        """

        if not self.are_same_qubit(first_id, second_id):
            return None

        first_local_id = (first_id - 1) % 4
        second_local_id = (second_id - 1) % 4

        pair = tuple(sorted((first_local_id, second_local_id)))

        if pair == (0, 1):
            return "left"

        if pair == (1, 2):
            return "middle"

        if pair == (2, 3):
            return "right"

        return None


    def _create_anyons(self):
        """
        Append four TAU anyons per qubit, with consecutive IDs starting at 1.
        """

        anyons_num = self.qubits_num * 4

        for anyon_id in range(1, anyons_num + 1):
            charge = (Charge.TAU)

            self.anyons.append(
                Anyon(
                    anyon_id=anyon_id,
                    charge=charge
                )
            )


    def _create_qubits(self):
        """
        Append qubits with IDs starting at 0, grouping consecutive anyons.
        """

        for qubit_id in range(self.qubits_num):
            start = qubit_id * 4
            end = start + 4

            qubit_anyons = self.anyons[start:end]

            self.qubits.append(
                AnyonicQubit(
                    qubit_id=qubit_id,
                    anyons=qubit_anyons
                )
            )


    def _build_global_structure(self):
        """
        Return the global tree built from each qubit's ((a, b), (c, d)) block.
        """

        qubit_subtrees = []

        for qubit in self.qubits:
            a1, a2, a3, a4 = qubit.anyons

            qubit_subtrees.append(
                (
                    (a1, a2),
                    (a3, a4)
                )
            )

        return self._combine_subtrees(qubit_subtrees)


    def _combine_subtrees(self, subtrees):
        """
        Pair neighboring subtrees recursively, preserving their leaf order.

        An unpaired subtree advances to the next level unchanged.
        Assumes subtrees is nonempty.
        """

        if len(subtrees) == 1:
            return subtrees[0]

        next_level = []

        for index in range(0, len(subtrees), 2):

            if index + 1 < len(subtrees):
                next_level.append(
                    (
                        subtrees[index],
                        subtrees[index + 1]
                    )
                )
            else:
                next_level.append(subtrees[index])

        return self._combine_subtrees(next_level)

    def record_operation(self, operation):
        """Append an AnyonOperation to history without executing it.

        Raises TypeError for any other object type.
        """
        if not isinstance(operation, AnyonOperation):
            raise TypeError("operation must be an AnyonOperation object.")

        self.operation_history.append(operation)


    def get_operation_history(self):
        """Return numbered descriptions joined by newlines, or an empty string."""
        lines = []

        for number, operation in enumerate(
            self.operation_history,
            start=1,
        ):
            params = operation.parameters

            if operation.operation_type == "SIGMA":
                sigma = f"σ{params['sigma_index']}"

                if operation.inverse:
                    sigma += "⁻¹"

                description = (
                    f"q[{params['qubit_id']}]"
                    f" | Sigma: {sigma}"
                )

            elif operation.operation_type == "R_MOVE":
                suffix = "⁻¹" if operation.inverse else ""
                description = (
                    f"R{suffix}"
                    f" | anyons: "
                    f"{params['first_id']}, "
                    f"{params['second_id']}"
                )

            elif operation.operation_type == "F_MOVE":
                description = (
                    f"F"
                    f" | path: {params['path']}"
                    f" | direction: {params['direction']}"
                )
            elif operation.operation_type == "SIGMA_GLOBAL":
                sigma = f"σ{params['global_index']}"

                if operation.inverse:
                    sigma += "⁻¹"

                description = (
                    f"Global Sigma: {sigma}"
                    f" | anyons: "
                    f"{params['first_id']}, "
                    f"{params['second_id']}"
                )
            else:
                description = operation.operation_type

            lines.append(
                f"[{number:05d}]  {description}"
            )

        return "\n".join(lines)


    def clear_operation_history(self):
        """Clear recorded operations without changing the simulated state."""
        self.operation_history.clear()

    def addOperationToIdealMatrix(
        self,
        operation,
    ):
        """Apply an operation to the ideal reference through HilbertSpace.

        Reads getName(), getTarget(), and optionally getControllers() from
        operation. Updates ideal amplitudes and history, not physical braids.
        """

        controllers = (
            tuple(
                operation.getControllers()
            )
            if hasattr(
                operation,
                "getControllers",
            )
            else ()
        )

        self.hilbertSpace.add_ideal_operation(
            gate_name=operation.getName(),
            target=operation.getTarget(),
            controllers=controllers,
        )

    def _commit_basis_state(self, new_basis: FusionBasis, new_state_vector,) -> None:
        """
        Validate and install a basis and a copy of its physical statevector.

        Requires the basis to describe the current tree and the vector shape
        to match its dimension. Synchronizes HilbertSpace and checks coherence.
        The calling operation is responsible for rollback if an error occurs.
        """

        if not isinstance(new_basis, FusionBasis):
            raise TypeError("new_basis must be a FusionBasis object.")

        if not isinstance(new_state_vector, np.ndarray):
            raise TypeError("new_state_vector must be a NumPy array.")

        expected_shape = (len(new_basis.states),)

        if new_state_vector.shape != expected_shape:
            raise ValueError(
                "Statevector shape does not match "
                "the new fusion basis."
            )

        if new_basis.tree_signature != self.tree.to_ids():
            raise ValueError(
                "New FusionBasis does not describe "
                "the current FusionTree."
            )

        self.basis = new_basis

        self.hilbertSpace.basis = new_basis
        self.hilbertSpace.dimension = len(
            new_basis.states
        )
        self.hilbertSpace.state_vector = (
            new_state_vector.copy()
        )

        self._validate_system_coherence()

    def _validate_system_coherence(self) -> None:
        """Raise RuntimeError if tree, shared basis, or vector dimensions differ."""
        if self.basis.tree_signature != self.tree.to_ids():
            raise RuntimeError("FusionBasis does not match FusionTree.")

        if self.hilbertSpace.basis is not self.basis:
            raise RuntimeError("HilbertSpace does not use the system basis.")

        if self.hilbertSpace.dimension != len(self.basis.states):
            raise RuntimeError("HilbertSpace dimension does not match basis.")

        if self.hilbertSpace.state_vector.shape != (self.hilbertSpace.dimension,):
            raise RuntimeError("Statevector shape does not match dimension.")




    def _apply_r_move(self, first_id: int, second_id: int, inverse: bool = False,) -> dict:
        """
        Apply R phases and swap two sibling anyons identified by permanent IDs.

        inverse selects conjugate phases. Rebuilds or reuses the resulting
        basis, reindexes amplitudes, and commits after checking norm preservation.
        Works in temporary physical bases as well as logically classified ones.

        Returns move metadata: type, inverse, IDs, parent path, and the before
        and after ID trees. Does not record history; restores the physical
        snapshot on failure.
        """

        if not isinstance(inverse, bool):
            raise TypeError(
                "inverse must be a boolean."
            )

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()
        old_basis = self.basis
        norm_before = np.linalg.norm(
            self.hilbertSpace.state_vector
        )

        try:
            if not self.tree.is_siblings(
                first_id,
                second_id,
            ):
                raise ValueError(
                    f"Anyons {first_id} and {second_id} "
                    "are not direct siblings."
                )

            first_path = self.tree.find_path(first_id)
            second_path = self.tree.find_path(second_id)

            parent_path = first_path[:-1]

            if second_path[:-1] != parent_path:
                raise ValueError(
                    "The anyons do not share the same parent."
                )

            r_plan = self._get_or_build_r_plan(
            parent_path=parent_path,
            inverse=inverse,)

            phased_state_vector = (
            self.hilbertSpace.state_vector_after_r(
                parent_path=parent_path,
                inverse=inverse,
                r_plan=r_plan,
            )
        )
            
            # Phases use the old basis; the exchanged leaves define the new one.
            self.tree._swap_siblings(first_id, second_id,)
            
            classify_logical = (self._tree_supports_logical_classification())

            new_basis = self._get_or_build_basis(classify_logical=classify_logical,)

            reindex_map = self._get_or_build_reindex_map(
                old_basis=old_basis,
                new_basis=new_basis,
            )

            new_state_vector = (
                self.hilbertSpace.state_vector_in_basis(
                    new_basis,
                    state_vector=phased_state_vector,
                    reindex_map=reindex_map,
                )
            )

            norm_after = np.linalg.norm(
                new_state_vector
            )

            if not np.isclose(norm_before, norm_after):
                raise RuntimeError(
                    "R-move did not preserve statevector norm."
                )

            self._commit_basis_state(
                new_basis,
                new_state_vector,
            )

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

        return {
            "type": "R",
            "inverse": inverse,
            "first_id": first_id,
            "second_id": second_id,
            "parent_path": parent_path,
            "tree_before": tree_before,
            "tree_after": self.tree.to_ids(),
        }

    @staticmethod
    def _leaf_id_cluster(node) -> frozenset:
        """Return all anyon IDs contained in a tree node."""

        if not isinstance(node, tuple):
            return frozenset((node.get_id(),))

        return (
            FusionSystem._leaf_id_cluster(node[0])
            | FusionSystem._leaf_id_cluster(node[1])
        )

    def _tree_supports_logical_classification(self) -> bool:
        """Check that each current four-leaf block and both pairs form subtrees.

        This tests tree structure only, not the state's leakage probability.
        """

        current_anyons = self.tree.flatten()

        for qubit_id in range(self.qubits_num):
            start = 4 * qubit_id
            block = current_anyons[start:start + 4]
            expected_groups = (
                block,
                block[:2],
                block[2:],
            )

            for group in expected_groups:
                paths = [
                    self.tree.find_path(anyon.get_id())
                    for anyon in group
                ]
                common_path = FusionBasis._common_path(paths)
                subtree = self.tree.get_node_at_path(common_path)

                # A common ancestor is sufficient only if it has no extra leaves.
                if self.tree.flatten(subtree) != list(group):
                    return False

        return True

    def _apply_f_move(self, path: tuple, direction: str,) -> dict:
        """Regroup a subtree and transform amplitudes into the resulting basis.

        path uses 0/1 steps from the root; () selects the root. direction is
        "right" for ((a, b), c) -> (a, (b, c)), or "left" for the inverse.
        Leaf order is preserved. Logical classification may become unavailable
        until a compatible tree shape is restored.

        Returns type, path, direction, and before/after ID trees without
        recording history. Checks norm preservation and restores the physical
        snapshot on failure.
        """

        if not isinstance(path, tuple):
            raise TypeError("path must be a tuple.")

        if direction not in {"left", "right"}:
            raise ValueError(
                "direction must be 'left' or 'right'."
            )

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()
        old_basis = self.basis
        norm_before = np.linalg.norm(
            self.hilbertSpace.state_vector
        )

        try:
            old_subtree = self.tree.get_node_at_path(path)

            if not isinstance(old_subtree, tuple):
                raise ValueError(
                    "F-move target must be a subtree."
                )

            if direction == "right":
                if not isinstance(old_subtree[0], tuple):
                    raise ValueError(
                        "Right F-move requires ((a, b), c)."
                    )
                old_intermediate = old_subtree[0]
            else:
                if not isinstance(old_subtree[1], tuple):
                    raise ValueError(
                        "Left F-move requires (a, (b, c))."
                    )
                old_intermediate = old_subtree[1]

            # Identify the changing channel by its leaves across both trees.
            old_intermediate_cluster = (
                self._leaf_id_cluster(old_intermediate)
            )

            self.tree.FMove(path, direction)

            # The tree has changed; HilbertSpace still holds the old basis and
            # amplitudes until the transformed vector is ready to commit.
            new_subtree = self.tree.get_node_at_path(path)
            new_intermediate = (
                new_subtree[1]
                if direction == "right"
                else new_subtree[0]
            )
            new_intermediate_cluster = (
                self._leaf_id_cluster(new_intermediate)
            )

            classify_logical = (
                self._tree_supports_logical_classification()
            )

            new_basis = self._get_or_build_basis(classify_logical=classify_logical,)
            # The old/new clusters identify the channel replaced by this F-move.
            f_plan = self._get_or_build_f_plan(
                old_basis=old_basis,
                new_basis=new_basis,
                old_intermediate_cluster=old_intermediate_cluster,
                new_intermediate_cluster=new_intermediate_cluster,
                direction=direction,
            )

            new_state_vector = (
                self.hilbertSpace.state_vector_after_f(
                    new_basis=new_basis,
                    old_intermediate_cluster=(
                        old_intermediate_cluster
                    ),
                    new_intermediate_cluster=(
                        new_intermediate_cluster
                    ),
                    direction=direction,
                    f_plan=f_plan,
                )
            )

            norm_after = np.linalg.norm(new_state_vector)

            if not np.isclose(norm_before, norm_after):
                raise RuntimeError(
                    "F-move did not preserve statevector norm."
                )

            self._commit_basis_state(
                new_basis,
                new_state_vector,
            )

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

        return {
            "type": "F",
            "direction": direction,
            "path": path,
            "tree_before": tree_before,
            "tree_after": self.tree.to_ids(),
        }


    def apply_f_move(self,path: tuple,direction: str,) -> None:
        """Apply an F-move and record one F_MOVE entry.

        path and direction follow _apply_f_move. Updates the tree, basis, and
        amplitudes; a temporary basis may have no logical classification.
        Rolls back the physical state and history if any step fails.
        """
        snapshot = self._capture_state_snapshot()

        try:
            step = self._apply_f_move(
                path=path,
                direction=direction,
            )

            self.record_operation(
                AnyonOperation(
                    operation_type="F_MOVE",
                    path=path,
                    direction=direction,
                    tree_before=step["tree_before"],
                    tree_after=step["tree_after"],
                )
            )

            self._validate_system_coherence()

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise


    def apply_r_move(self,first_id: int,second_id: int,inverse: bool = False,) -> None:
        """Braid sibling anyon IDs and record one R_MOVE entry.

        Applies channel phases, swaps leaves, and updates the basis and vector.
        inverse selects the inverse braid. Rolls back physical state and
        history if any step fails, including history recording.
        """
        snapshot = self._capture_state_snapshot()

        try:
            step = self._apply_r_move(
                first_id=first_id,
                second_id=second_id,
                inverse=inverse,
            )

            self.record_operation(
                AnyonOperation(
                    operation_type="R_MOVE",
                    inverse=inverse,
                    first_id=first_id,
                    second_id=second_id,
                    parent_path=step["parent_path"],
                    tree_before=step["tree_before"],
                    tree_after=step["tree_after"],
                )
            )

            self._validate_system_coherence()

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

    def _validate_adjacent_anyons(self, first_id: int, second_id: int,) -> None:
        """Require two existing, distinct IDs adjacent in current left-to-right order."""
        self.get_anyon(first_id)
        self.get_anyon(second_id)


        if first_id == second_id:
            raise ValueError(
                "Recoupling requires two different anyons."
            )

        order = self.get_current_anyon_order()

        first_position = order.index(first_id)
        second_position = order.index(second_id)

        if second_position != first_position + 1:
            raise ValueError(
                "Anyons must be adjacent and provided "
                "in left-to-right order."
            )

    def _find_lca_path(self, first_id: int, second_id: int, ) -> tuple:
        """Return the deepest common ancestor path of an ordered adjacent pair."""
        self._validate_adjacent_anyons(
            first_id,
            second_id,
        )

        first_path = self.tree.find_path(first_id)
        second_path = self.tree.find_path(second_id)

        return FusionBasis._common_path([
            first_path,
            second_path,
        ])

    def _recouple_adjacent_anyons(self, first_id: int, second_id: int,) -> tuple:
        """Apply F-moves until an ordered adjacent pair of anyon IDs are siblings.

        Starts at their common ancestor and rotates inward, preserving leaf
        order while updating the basis and amplitudes at each step. Returns
        a tuple of (path, direction) steps for _undo_recoupling.
        Does not record history; restores the entry snapshot on failure.
        """
        self._validate_adjacent_anyons(
            first_id,
            second_id,
        )

        snapshot = self._capture_state_snapshot()
        steps = []

        try:
            current_path = self._find_lca_path(
                first_id,
                second_id,
            )

            while not self.tree.is_siblings(
                first_id,
                second_id,
            ):
                subtree = self.tree.get_node_at_path(
                    current_path
                )

                if not isinstance(subtree, tuple):
                    raise RuntimeError(
                        "Recoupling reached an invalid subtree."
                    )

                left, right = subtree

                # Adjacency puts first_id at the right edge of left, and
                # second_id at the left edge of right.
                left_ids = self._leaf_id_cluster(left)
                right_ids = self._leaf_id_cluster(right)

                if (
                    first_id not in left_ids
                    or second_id not in right_ids
                ):
                    raise RuntimeError(
                        "Adjacent anyons are not separated "
                        "across the expected subtree."
                    )

                # Expose the boundary leaves by rotating into the pair's branch.
                if isinstance(left, tuple):
                    self._apply_f_move(
                        current_path,
                        "right",
                    )

                    steps.append((
                        current_path,
                        "right",
                    ))

                    # After the right rotation, both target leaves lie on the right.
                    current_path = current_path + (1,)
                    continue

                if isinstance(right, tuple):
                    self._apply_f_move(
                        current_path,
                        "left",
                    )

                    steps.append((
                        current_path,
                        "left",
                    ))

                    # After the left rotation, both target leaves lie on the left.
                    current_path = current_path + (0,)
                    continue

                raise RuntimeError(
                    "The anyons did not become siblings."
                )

            self._validate_system_coherence()

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

        return tuple(steps)

    def _undo_recoupling(self, steps: tuple,) -> None:
        """Apply inverse F-moves in reverse order for recorded recoupling steps.

        Each step is (path, direction). Restores the grouping while retaining
        any leaf exchanges made since recoupling; it does not undo an intervening
        R-move. Does not record history. On failure, restores its entry snapshot.
        """
        if not isinstance(steps, tuple):
            raise TypeError(
                "steps must be a tuple."
            )

        snapshot = self._capture_state_snapshot()

        try:
            for step in reversed(steps):
                if (
                    not isinstance(step, tuple)
                    or len(step) != 2
                ):
                    raise ValueError(
                        "Every recoupling step must contain "
                        "a path and direction."
                    )

                path, direction = step

                if not isinstance(path, tuple):
                    raise TypeError(
                        "Recoupling path must be a tuple."
                    )

                if direction == "right":
                    inverse_direction = "left"
                elif direction == "left":
                    inverse_direction = "right"
                else:
                    raise ValueError(
                        "Recoupling direction must be "
                        "'left' or 'right'."
                    )

                self._apply_f_move(
                    path,
                    inverse_direction,
                )

            self._validate_system_coherence()

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise


    def _validate_local_sigma_inputs(self, qubit_id: int, index: int, ) -> None:
        """Validate a qubit ID, signed local generator, and classified basis.

        Requires a zero-based qubit ID and index in +/-1, +/-2, +/-3.
        Raises TypeError for non-integer or boolean inputs, ValueError for
        invalid ranges, or RuntimeError if logical classification is absent.
        """
        if (
            isinstance(qubit_id, bool)
            or not isinstance(qubit_id, int)
        ):
            raise TypeError(
                "qubit_id must be an integer."
            )

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(
                f"Qubit {qubit_id} does not exist."
            )

        if (
            isinstance(index, bool)
            or not isinstance(index, int)
        ):
            raise TypeError(
                "index must be an integer."
            )

        if index not in {-3, -2, -1, 1, 2, 3}:
            raise ValueError(
                "index must be ±1, ±2, or ±3."
            )

        if not self.basis.classify_logical:
            raise RuntimeError(
                "sigma requires a stable logical-qubit topology."
            )
    
    def _validate_global_sigma_input(self, index: int,) -> None:
        """Validate a signed generator between adjacent global positions.

        Requires 1 <= abs(index) < len(anyons) and a classified logical basis.
        Raises TypeError for non-integer or boolean input, ValueError for an
        invalid range, or RuntimeError if logical classification is absent.
        """
        if (
            isinstance(index, bool)
            or not isinstance(index, int)
        ):
            raise TypeError(
                "index must be an integer."
            )

        max_index = len(self.anyons) - 1

        if index == 0 or abs(index) > max_index:
            raise ValueError(
                f"index must be between "
                f"-{max_index} and {max_index}, excluding 0."
            )

        if not self.basis.classify_logical:
            raise RuntimeError(
                "sigma_global requires a stable "
                "logical-qubit topology."
            )
    
    
    def _global_to_local_sigma(self, index: int,) -> tuple[int, int]:
        """Return (qubit_id, signed_local_index) for a non-boundary generator.

        Uses current positional blocks. Rejects multiples of four, which
        exchange anyons across block boundaries, and preserves the sign.
        """
        self._validate_global_sigma_input(index)

        global_index = abs(index)

        if global_index % 4 == 0:
            raise ValueError(
                "Cross-qubit sigma cannot be converted "
                "to a local sigma."
            )

        qubit_id = (global_index - 1) // 4
        local_index = ((global_index - 1) % 4) + 1

        if index < 0:
            local_index = -local_index

        return qubit_id, local_index



    def sigma(self, qubit_id: int, index: int) -> None:
        """Braid neighboring positions within a current four-anyon qubit block.

        Args:
            qubit_id: Zero-based positional block index.
            index: Signed local generator: +/-1, +/-2, or +/-3. The magnitude
                selects positions i and i+1; negative selects the inverse braid.

        Generators 1 and 3 apply R directly; generator 2 uses two F-moves,
        R, then inverse regrouping. Requires and restores logical topology,
        updates the local braid operator, and records one SIGMA entry.
        Restores physical state and history on failure.
        """
        self._validate_local_sigma_inputs(qubit_id, index,)

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()

        try:
            sigma_index = abs(index)
            inverse = index < 0

            block = self.get_current_qubit_block(
                qubit_id
            )
            current_ids = [
                anyon.get_id()
                for anyon in block
            ]

            first_id = current_ids[sigma_index - 1]
            second_id = current_ids[sigma_index]

            qubit_path = self.basis.qubit_paths[
                qubit_id
            ]["root"]

            if sigma_index in {1, 3}:
                self._apply_r_move(
                    first_id,
                    second_id,
                    inverse=inverse,
                )

            else:
                # Make the middle leaves siblings, braid, then restore grouping.
                inner_path = qubit_path + (1,)

                self._apply_f_move(
                    qubit_path,
                    "right",
                )
                self._apply_f_move(
                    inner_path,
                    "left",
                )
                self._apply_r_move(
                    first_id,
                    second_id,
                    inverse=inverse,
                )
                self._apply_f_move(
                    inner_path,
                    "right",
                )
                self._apply_f_move(
                    qubit_path,
                    "left",
                )

            self._validate_system_coherence()

            if not self.basis.classify_logical:
                raise RuntimeError(
                    "sigma did not restore logical topology."
                )

            self.hilbertSpace.record_local_braid(
                qubit_id,
                index,
            )

            self.record_operation(
                AnyonOperation(
                    operation_type="SIGMA",
                    inverse=inverse,
                    qubit_id=qubit_id,
                    sigma_index=sigma_index,
                    first_id=first_id,
                    second_id=second_id,
                    tree_before=tree_before,
                    tree_after=self.tree.to_ids(),
                )
            )

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

    

    def _apply_cross_qubit_sigma(self, global_index: int, inverse: bool = False,) -> dict:
        """Braid the current leaves on either side of a qubit-block boundary.

        global_index is the positive, one-based left position and must be a
        multiple of four; the right position is global_index + 1. Recouples
        the leaves with F-moves, applies R, then undoes the regrouping.

        Returns IDs, recoupling steps, and before/after tree and order metadata.
        Restores logical topology but may create leakage. Checks norm and leaf
        order, and restores the entry snapshot on failure. Does not record
        history or update local braid matrices.
        """
        if not isinstance(inverse, bool):
            raise TypeError(
                "inverse must be a boolean."
            )

        if global_index % 4 != 0:
            raise ValueError(
                "Cross-qubit sigma index must be "
                "a multiple of four."
            )

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()
        order_before = self.get_current_anyon_order()
        norm_before = np.linalg.norm(
            self.hilbertSpace.state_vector
        )

        try:
            first_id = (
                self.get_anyon_at_position(
                    global_index
                )
                .get_id()
            )

            second_id = (
                self.get_anyon_at_position(
                    global_index + 1
                )
                .get_id()
            )

            steps = self._recouple_adjacent_anyons(
                first_id,
                second_id,
            )

            if not self.tree.is_siblings(
                first_id,
                second_id,
            ):
                raise RuntimeError(
                    "Recoupling did not make the "
                    "boundary anyons siblings."
                )

            self._apply_r_move(
                first_id,
                second_id,
                inverse=inverse,
            )

            self._undo_recoupling(steps)

            self._validate_system_coherence()

            if not self.basis.classify_logical:
                raise RuntimeError(
                    "Cross-qubit sigma did not restore "
                    "logical topology."
                )

            norm_after = np.linalg.norm(
                self.hilbertSpace.state_vector
            )

            if not np.isclose(norm_before, norm_after):
                raise RuntimeError(
                    "Cross-qubit sigma did not preserve "
                    "statevector norm."
                )

            # F-moves preserve leaf order, so only the R pair should be exchanged.
            expected_order = list(order_before)
            left = global_index - 1
            right = global_index

            expected_order[left], expected_order[right] = (
                expected_order[right],
                expected_order[left],
            )

            if (
                self.get_current_anyon_order()
                != tuple(expected_order)
            ):
                raise RuntimeError(
                    "Cross-qubit sigma changed an "
                    "unexpected anyon position."
                )

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise

        return {
            "type": "SIGMA_GLOBAL",
            "global_index": global_index,
            "inverse": inverse,
            "first_id": first_id,
            "second_id": second_id,
            "recoupling_steps": steps,
            "tree_before": tree_before,
            "tree_after": self.tree.to_ids(),
            "order_before": order_before,
            "order_after": (
                self.get_current_anyon_order()
            ),
        }

    def sigma_global(self, index: int,) -> None:
        """Braid current global positions abs(index) and abs(index) + 1.

        Positions are one-based; a negative index selects the inverse braid.
        Requires a logically classified basis. Within a qubit block, delegates
        to sigma and records SIGMA. At a block boundary, recouples across blocks
        and records one SIGMA_GLOBAL entry, hiding the internal F/R steps.
        Failed operations restore physical state and history.
        """
        self._validate_global_sigma_input(index)

        global_index = abs(index)
        inverse = index < 0

        if global_index % 4 != 0:
            qubit_id, local_index = (
                self._global_to_local_sigma(index)
            )

            self.sigma(
                qubit_id=qubit_id,
                index=local_index,
            )
            return

        snapshot = self._capture_state_snapshot()

        try:
            result = self._apply_cross_qubit_sigma(
                global_index=global_index,
                inverse=inverse,
            )

            self.record_operation(
                AnyonOperation(
                    operation_type="SIGMA_GLOBAL",
                    inverse=inverse,
                    global_index=global_index,
                    first_id=result["first_id"],
                    second_id=result["second_id"],
                    recoupling_steps=(
                        result["recoupling_steps"]
                    ),
                    tree_before=result["tree_before"],
                    tree_after=result["tree_after"],
                    order_before=result["order_before"],
                    order_after=result["order_after"],
                )
            )

            self._validate_system_coherence()

        except Exception:
            self._restore_state_snapshot(snapshot)
            raise


    def get_cache_stats(self) -> dict:
        """Return a snapshot of the current cache statistics."""
        return self.cache.snapshot_stats()


    def reset_cache_stats(self) -> None:
        """Reset cache counters without removing cached entries."""
        self.cache.reset_stats()


    def clear_cache(self) -> None:
        """Remove cached entries and reset their counters."""
        self.cache.clear()

    def set_cache_enabled(self, enabled: bool) -> None:
        """Enable or disable future cache use, preserving entries and counters."""
        self.cache.enabled = enabled

    def _get_basis_cache_key(self, classify_logical: bool,) -> tuple:
        """Key the ID tree, original qubit groups, VACUUM total, and classification."""

        tree_signature = self.tree.to_ids()

        qubit_signature = tuple(
            tuple(qubit.get_id_list())
            for qubit in self.qubits
        )

        return (
            tree_signature,
            qubit_signature,
            Charge.VACUUM,
            classify_logical,
        )

    def _get_or_build_basis(self, classify_logical: bool,) -> FusionBasis:
        """Return a validated cached basis or build one for the current tree.

        Uses total VACUUM charge. classify_logical controls positional qubit
        paths and logical/leakage mappings; False still builds the full physical
        basis. Stores new bases only when caching is enabled. Does not install
        the returned basis into the system or HilbertSpace.
        """
        key = self._get_basis_cache_key(
            classify_logical,
        )

        found, cached_basis = self.cache.lookup(
            "basis",
            key,
        )

        if found:
            self._validate_cached_basis(
                cached_basis,
                classify_logical,
            )
            return cached_basis

        new_basis = FusionBasis(
            tree=self.tree,
            qubits=self.qubits,
            total_charge=Charge.VACUUM,
            classify_logical=classify_logical,
        )

        self.cache.record_build("basis")

        if self.cache.enabled:
            self.cache.store(
                "basis",
                key,
                new_basis,
            )

        return new_basis


    def _validate_cached_basis(self, basis: FusionBasis, classify_logical: bool,) -> None:
        """Check cached basis type, ID tree, qubit count, classification, and owners.

        Requires the same tree and qubit-list objects as this system.
        Raises TypeError for a non-basis or RuntimeError for a mismatch.
        """
        if not isinstance(basis, FusionBasis):
            raise TypeError(
                "Cached basis must be a FusionBasis."
            )

        if basis.tree_signature != self.tree.to_ids():
            raise RuntimeError(
                "Cached FusionBasis does not match the current tree."
            )

        if basis.qubits_num != self.qubits_num:
            raise RuntimeError(
                "Cached FusionBasis has the wrong qubit count."
            )

        if basis.classify_logical is not classify_logical:
            raise RuntimeError(
                "Cached FusionBasis has the wrong classification mode."
            )

        if basis._tree is not self.tree:
            raise RuntimeError(
                "Cached FusionBasis belongs to another FusionSystem tree."
            )

        if basis._qubits is not self.qubits:
            raise RuntimeError(
                "Cached FusionBasis belongs to another FusionSystem qubit set."
            )



    def _get_or_build_reindex_map(self, old_basis: FusionBasis, new_basis: FusionBasis,) -> tuple[int, ...]:
        """Return a cached or computed old-index to new-index mapping.

        The bases must contain matching fusion-label states. Cached by the
        two basis objects; this does not transform amplitudes.
        """
        return self.cache.get_or_build(
            namespace="reindex",
            key=(old_basis, new_basis),
            builder=lambda: old_basis.get_reindex_map(
                new_basis
            ),
        )

    def _get_or_build_r_plan(
        self,
        parent_path: tuple,
        inverse: bool,
    ) -> np.ndarray:
        """Return R phases cached by current basis, parent path, and inverse flag."""
        return self.cache.get_or_build(
            namespace="r_plan",
            key=(
                self.basis,
                parent_path,
                inverse,
            ),
            builder=lambda: self.hilbertSpace.build_r_plan(
                parent_path=parent_path,
                inverse=inverse,
            ),
        )

    def _get_or_build_cluster_maps(
        self,
        basis: FusionBasis,
    ) -> tuple[dict, ...]:
        """Return cached or computed cluster-charge maps in the given basis order."""
        return self.cache.get_or_build(
            namespace="cluster",
            key=basis,
            builder=lambda: tuple(
                basis.get_cluster_labels(state)
                for state in basis.states
            ),
        )


    def _get_or_build_f_plan(
        self,
        old_basis: FusionBasis,
        new_basis: FusionBasis,
        old_intermediate_cluster: frozenset,
        new_intermediate_cluster: frozenset,
        direction: str,
    ) -> tuple:
        """Return cached or computed F-move index groups for two bases.

        Intermediate clusters are frozensets of anyon IDs; direction is
        "left" or "right". Reuses per-basis cluster maps during construction.
        Assumes HilbertSpace still holds old_basis while the tree has already
        been regrouped. The returned plan does not change amplitudes.
        """
        # Each entry is (old_indices, new_indices): one channel to copy, or
        # two channels to mix in (VACUUM, TAU) order on both sides.
        return self.cache.get_or_build(
            namespace="f_plan",
            key=(
                old_basis,
                new_basis,
                old_intermediate_cluster,
                new_intermediate_cluster,
                direction,
            ),
            builder=lambda: self.hilbertSpace.build_f_plan(
                new_basis=new_basis,
                old_intermediate_cluster=old_intermediate_cluster,
                new_intermediate_cluster=new_intermediate_cluster,
                direction=direction,
                old_cluster_maps=(
                    self._get_or_build_cluster_maps(old_basis)
                ),
                new_cluster_maps=(
                    self._get_or_build_cluster_maps(new_basis)
                ),
            ),
        )

    def __str__(self):
        """Return qubit and anyon counts with the current anyon-ID tree."""
        return (
            f"FusionSystem(\n"
            f"    qubits = {self.qubits_num},\n"
            f"    anyons = {len(self.anyons)},\n"
            f"    tree = {self.tree.to_ids()}\n"
            f")"
        )


    def __repr__(self):
        """Return the same diagnostic summary as str(self)."""
        return self.__str__()
