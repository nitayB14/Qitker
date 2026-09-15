import numpy as np

from qitker.anyons.Anyon import Anyon, Charge
from qitker.anyons.AnyonicQubit import AnyonicQubit
from qitker.anyons.FusionTree import FusionTree
from qitker.anyons.AnyonOperation import AnyonOperation
from qitker.QuantumMath.HilbertSpace import HilbertSpace
from qitker.anyons.FusionBasis import FusionBasis


class FusionSystem:
    """
    Represents a global system of Fibonacci anyonic qubits.

    Braiding convention:
        An anyon ID represents a permanent physical identity.

        The position of an anyon is determined by its current
        position in the flattened FusionTree.

        An R-move exchanges the positions of two sibling anyons
        while preserving their IDs.
    """

    BRAID_CONVENTION = "MOVING_ANYON_IDENTITIES"

    def __init__(self, qubits_num: int):

        if not isinstance(qubits_num, int):
            raise TypeError("qubits_num must be an integer.")

        if qubits_num < 1:
            raise ValueError("qubits_num must be at least 1.")

        if qubits_num > 20:
            raise ValueError("Number too big for simulation")

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

        self.basis = FusionBasis(tree=self.tree, qubits=self.qubits, total_charge=Charge.VACUUM)

        self.hilbertSpace = HilbertSpace(self.basis)

    def get_qubit(self, qubit_id):
        """
        Returns the AnyonicQubit with the given ID.
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
        Returns the Anyon with the given ID.
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
        Return the four anyons currently occupying a logical-qubit block.
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
        Capture the state required to roll back an atomic operation.
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
        Restore tree, basis, and HilbertSpace after a failed operation.
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
        Returns the AnyonicQubit that owns the given anyon.
        """

        anyon = self.get_anyon(anyon_id)

        qubit_id = (anyon.get_id() - 1) // 4

        return self.get_qubit(qubit_id)

    def are_same_qubit(self, first_id, second_id):
        """
        Returns True if both anyons belong to the same logical qubit.
        """

        first_qubit = self.get_qubit_of_anyon(first_id)
        second_qubit = self.get_qubit_of_anyon(second_id)

        return first_qubit.qubit_id == second_qubit.qubit_id

    def are_neighbor_qubits(self, first_id, second_id):
        """
        Returns True if the two anyons belong to neighboring logical qubits.
        """

        first_qubit = self.get_qubit_of_anyon(first_id)
        second_qubit = self.get_qubit_of_anyon(second_id)

        return abs(first_qubit.qubit_id - second_qubit.qubit_id) == 1

    def get_local_pair_type(self, first_id, second_id):
        """
        Returns the local pair type inside a logical qubit:
        'left', 'middle', or 'right'.

        Returns None if the anyons do not form a valid local pair.
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
        Creates four anyons for every anyonic qubit.
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
        Groups every four anyons into one AnyonicQubit.
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
        Builds the initial global fusion-tree structure.
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
        Combines a list of subtrees into one binary tree.
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
        if not isinstance(operation, AnyonOperation):
            raise TypeError("operation must be an AnyonOperation object.")

        self.operation_history.append(operation)


    def get_operation_history(self):
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
        self.operation_history.clear()

    def addOperationToIdealMatrix(self, operation):
        self.hilbertSpace.add_ideal_operation(operation.getName(), operation.getTarget())

    def _commit_basis_state(self, new_basis: FusionBasis, new_state_vector,) -> None:
        """
        Atomically install a validated basis and statevector.
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
        Atomically apply a quantum R-move to sibling anyons.
        """

        if not isinstance(inverse, bool):
            raise TypeError(
                "inverse must be a boolean."
            )

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()
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

            phased_state_vector = (
                self.hilbertSpace.state_vector_after_r(
                    parent_path=parent_path,
                    inverse=inverse,
                )
            )

            
            self.tree._swap_siblings(first_id, second_id,)
            
            classify_logical = (self._tree_supports_logical_classification())

            new_basis = FusionBasis(
                tree=self.tree,
                qubits=self.qubits,
                total_charge=Charge.VACUUM,
                classify_logical=classify_logical,
            )

            new_state_vector = (
                self.hilbertSpace.state_vector_in_basis(
                    new_basis,
                    state_vector=phased_state_vector,
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
        """Return whether every positional qubit has its expected nodes."""

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

                if self.tree.flatten(subtree) != list(group):
                    return False

        return True

    def _apply_f_move(self, path: tuple, direction: str,) -> dict:
        """Atomically apply a quantum F-move and change basis."""

        if not isinstance(path, tuple):
            raise TypeError("path must be a tuple.")

        if direction not in {"left", "right"}:
            raise ValueError(
                "direction must be 'left' or 'right'."
            )

        snapshot = self._capture_state_snapshot()
        tree_before = self.tree.to_ids()
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

            old_intermediate_cluster = (
                self._leaf_id_cluster(old_intermediate)
            )

            self.tree.FMove(path, direction)

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
            new_basis = FusionBasis(
                tree=self.tree,
                qubits=self.qubits,
                total_charge=Charge.VACUUM,
                classify_logical=classify_logical,
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

                if isinstance(left, tuple):
                    self._apply_f_move(
                        current_path,
                        "right",
                    )

                    steps.append((
                        current_path,
                        "right",
                    ))

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

    def __str__(self):
        return (
            f"FusionSystem(\n"
            f"    qubits = {self.qubits_num},\n"
            f"    anyons = {len(self.anyons)},\n"
            f"    tree = {self.tree.to_ids()}\n"
            f")"
        )


    def __repr__(self):
        return self.__str__()
