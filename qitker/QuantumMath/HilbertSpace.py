from qitker.QuantumMath.constant import math_constant
import numpy as np

from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.Anyon import Charge

fibonacciConst = math_constant()

class HilbertSpace:

    def __init__(self, basis: FusionBasis):

        self.basis = basis
        self.qubits_num = basis.qubits_num
        self.dimension = len(basis.states)

        initial_label = "0" * self.qubits_num
        initial_index = (self.basis.logical_to_physical[initial_label])

        self.state_vector = np.zeros(self.dimension, dtype=complex,)
        self.state_vector[initial_index] = 1



        self.local_braid_operators = [fibonacciConst.I.copy() for _ in range(self.qubits_num)]
        self.local_ideal_operators = [fibonacciConst.I.copy() for _ in range(self.qubits_num)]

        self.ideal_operations = []


        self.logical_dimension = 2 ** self.qubits_num

        self.logical_labels = tuple(
            format(index, f"0{self.qubits_num}b")
            for index in range(self.logical_dimension)
        )

        self.ideal_state_vector = np.zeros(
            self.logical_dimension,
            dtype=complex,
        )

        self.ideal_state_vector[0] = 1.0



    def state_vector_in_basis(
        self,
        new_basis: FusionBasis,
        state_vector: np.ndarray | None = None,
        reindex_map: tuple[int, ...] | None = None,
    ) -> np.ndarray:
        """
        Return the current statevector reindexed into new_basis.

        This method does not modify the HilbertSpace.
        """

        source_state_vector = (self.state_vector if state_vector is None else state_vector)

        if not isinstance(source_state_vector, np.ndarray):
            raise TypeError("state_vector must be a NumPy array.")

        if source_state_vector.shape != (self.dimension,):
            raise ValueError(
                "state_vector shape does not match "
                "the current fusion basis."
            )

        if reindex_map is None:
            reindex_map = self.basis.get_reindex_map(new_basis)

        new_state_vector = np.zeros(
            len(new_basis.states),
            dtype=complex,
        )

        for old_index, new_index in enumerate(reindex_map):
            new_state_vector[new_index] = (
                source_state_vector[old_index]
            )

        return new_state_vector



    def probs(self):
        """
        Computes the measurement probabilities
        of the current quantum state.
        """

        probabilities = np.abs(self.state_vector) ** 2

        return probabilities / probabilities.sum()
    
    def computational_probability(self) -> float:
        if not self.basis.classify_logical:
            raise RuntimeError(
                "Computational probability is unavailable "
                "in a temporary physical fusion basis."
            )

        probabilities = self.probs()
        return float(probabilities[self.basis.computational_indices].sum())
    
    def leakage_probability(self) -> float:
        if not self.basis.classify_logical:
            raise RuntimeError(
                "Leakage probability is unavailable in a "
                "temporary physical fusion basis."
            )

        probabilities = self.probs()
        return float(probabilities[self.basis.leakage_indices].sum())
    
    def measure_once(self):
        """
        Measures the current quantum state once.

        Returns:
            int: Measured basis-state index.
        """

        probabilities = self.probs()

        return np.random.choice(
            self.dimension,
            p=probabilities
        )


    def run_measurements(self, shots):
        if not isinstance(shots, int):
            raise TypeError(
                "shots must be an integer."
            )

        if shots < 1:
            raise ValueError(
                "shots must be at least 1."
            )

        results = {}

        for _ in range(shots):
            physical_index = self.measure_once()

            result = self._decode_measurement(
                physical_index
            )

            results[result] = (
                results.get(result, 0) + 1
            )

        return results

    
    def add_ideal_operation(
        self,
        gate_name: str,
        target: int,
        controllers=(),
    ) -> None:

        if not isinstance(gate_name, str):
            raise TypeError(
                "gate_name must be a string."
            )

        gate_name = gate_name.upper()

        local_gate = self._get_gate_matrix(
            gate_name
        )

        if (
            isinstance(target, bool)
            or not isinstance(target, int)
        ):
            raise TypeError(
                "target must be an integer."
            )

        if target < 0 or target >= self.qubits_num:
            raise ValueError(
                f"Qubit {target} does not exist."
            )

        if not isinstance(controllers, (tuple, list)):
            raise TypeError(
                "controllers must be a tuple or list."
            )

        controllers = tuple(controllers)

        for controller in controllers:
            if (
                isinstance(controller, bool)
                or not isinstance(controller, int)
            ):
                raise TypeError(
                    "Controller indices must be integers."
                )

            if (
                controller < 0
                or controller >= self.qubits_num
            ):
                raise ValueError(
                    f"Qubit {controller} does not exist."
                )

        if len(set(controllers)) != len(controllers):
            raise ValueError(
                "Controllers must be unique."
            )

        if target in controllers:
            raise ValueError(
                "The target cannot also be a controller."
            )

        self.ideal_state_vector = (
            self._apply_ideal_gate_to_state(
                state=self.ideal_state_vector,
                gate=local_gate,
                target=target,
                controllers=controllers,
            )
        )

        self.ideal_operations.append({
            "gate": gate_name,
            "target": target,
            "controllers": controllers,
        })

        if not controllers:
            self.local_ideal_operators[target] = (
                local_gate
                @ self.local_ideal_operators[target]
            )

    
    def _apply_ideal_gate_to_state(
        self,
        state: np.ndarray,
        gate: np.ndarray,
        target: int,
        controllers: tuple,
    ) -> np.ndarray:

        state = np.asarray(
            state,
            dtype=complex,
        )

        if state.shape != (
            self.logical_dimension,
        ):
            raise ValueError(
                "Logical state shape does not match "
                "the logical Hilbert-space dimension."
            )

        if gate.shape != (2, 2):
            raise ValueError(
                "A logical base gate must be a 2x2 matrix."
            )

        target_mask = (
            1 << (self.qubits_num - 1 - target)
        )

        controller_masks = tuple(
            1 << (
                self.qubits_num
                - 1
                - controller
            )
            for controller in controllers
        )

        result = state.copy()

        for zero_index in range(
            self.logical_dimension
        ):
            if zero_index & target_mask:
                continue

            if any(
                (
                    zero_index
                    & controller_mask
                ) == 0
                for controller_mask
                in controller_masks
            ):
                continue

            one_index = (
                zero_index | target_mask
            )

            zero_amplitude = state[zero_index]
            one_amplitude = state[one_index]

            result[zero_index] = (
                gate[0, 0] * zero_amplitude
                + gate[0, 1] * one_amplitude
            )

            result[one_index] = (
                gate[1, 0] * zero_amplitude
                + gate[1, 1] * one_amplitude
            )

        return result



    def _get_gate_matrix(self, gate_name: str) -> np.ndarray:
        if not isinstance(gate_name, str):
            raise TypeError("gate_name must be a string.")



        gate_name = gate_name.upper()

        if gate_name not in fibonacciConst.GATE_MATRICES:
            raise ValueError(
                f"{gate_name} is not supported by the Qitker V1 backend. "
                "Export the circuit to use another backend."
            )

        return fibonacciConst.GATE_MATRICES[gate_name]


    def state_fidelity(self) -> float:

        if not self.basis.classify_logical:
            raise RuntimeError(
                "State fidelity requires a stable "
                "logical fusion basis."
            )

        logical_physical_indices = tuple(
            self.basis.logical_to_physical[
                label
            ]
            for label in self.logical_labels
        )

        ideal_physical_state = np.zeros(
            self.dimension,
            dtype=complex,
        )

        ideal_physical_state[
            list(logical_physical_indices)
        ] = self.ideal_state_vector

        fidelity = abs(
            np.vdot(
                ideal_physical_state,
                self.state_vector,
            )
        ) ** 2

        tolerance = 1e-10

        if fidelity > 1.0 + tolerance:
            raise RuntimeError(
                "Calculated state fidelity is greater "
                "than one."
            )

        return float(
            np.clip(
                fidelity,
                0.0,
                1.0,
            )
        )
    
    def _decode_measurement(self,physical_index: int,) -> str:
        if physical_index in (self.basis.physical_to_logical):
            return self.basis.physical_to_logical[physical_index]

        return "LEAKAGE"
    def get_state_vector(self):
        #Returns the current quantum state.
        return self.state_vector

    def record_local_braid(self, qubit_id: int, index: int,) -> None:
        if isinstance(qubit_id, bool) or not isinstance(qubit_id, int,):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(f"Qubit {qubit_id} does not exist.")
        
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("index must be an integer.")

        if index not in fibonacciConst.SIGMA_MATRICES:
            raise ValueError("Unsupported local sigma index.")

        operator = fibonacciConst.SIGMA_MATRICES[index]

        self.local_braid_operators[qubit_id] = (
            operator
            @ self.local_braid_operators[qubit_id]
        )


    def build_r_plan(
        self,
        parent_path: tuple,
        inverse: bool = False,
    ) -> np.ndarray:
        if not isinstance(parent_path, tuple):
            raise TypeError(
                "parent_path must be a tuple."
            )

        if not isinstance(inverse, bool):
            raise TypeError(
                "inverse must be a boolean."
            )

        r_plan = np.empty(
            self.dimension,
            dtype=complex,
        )

        for index, state in enumerate(self.basis.states):
            if parent_path not in state["labels"]:
                raise ValueError(
                    "parent_path is not an internal fusion node "
                    "in the current basis."
                )

            parent_charge = state["labels"][parent_path]

            if parent_charge is Charge.VACUUM:
                phase = fibonacciConst.R_VACUUM
            elif parent_charge is Charge.TAU:
                phase = fibonacciConst.R_TAU
            else:
                raise ValueError(
                    "Unsupported fusion channel for R-move."
                )

            if inverse:
                phase = np.conjugate(phase)

            r_plan[index] = phase

        r_plan.setflags(write=False)
        return r_plan

    def state_vector_after_r(
        self,
        parent_path: tuple,
        inverse: bool = False,
        r_plan: np.ndarray | None = None,
    ) -> np.ndarray:
        """Return the statevector after applying an R-symbol."""

        if r_plan is None:
            r_plan = self.build_r_plan(
                parent_path=parent_path,
                inverse=inverse,
            )

        return r_plan * self.state_vector


    def build_f_plan(
        self,
        new_basis: FusionBasis,
        old_intermediate_cluster: frozenset,
        new_intermediate_cluster: frozenset,
        direction: str,
        old_cluster_maps: tuple[dict, ...] | None = None,
        new_cluster_maps: tuple[dict, ...] | None = None,
    ) -> tuple:
        """Build the index transitions required by an F-move."""

        if not isinstance(new_basis, FusionBasis):
            raise TypeError(
                "new_basis must be a FusionBasis object."
            )

        if direction not in {"left", "right"}:
            raise ValueError(
                "direction must be 'left' or 'right'."
            )

        if not isinstance(old_intermediate_cluster, frozenset):
            raise TypeError(
                "old_intermediate_cluster must be a frozenset."
            )

        if not isinstance(new_intermediate_cluster, frozenset):
            raise TypeError(
                "new_intermediate_cluster must be a frozenset."
            )

        if old_cluster_maps is None:
            old_cluster_maps = tuple(
                self.basis.get_cluster_labels(state)
                for state in self.basis.states
            )

        if new_cluster_maps is None:
            new_cluster_maps = tuple(
                new_basis.get_cluster_labels(state)
                for state in new_basis.states
            )

        def spectator_key(cluster_labels, excluded_cluster):
            items = [
                (tuple(sorted(cluster)), charge)
                for cluster, charge in cluster_labels.items()
                if cluster != excluded_cluster
            ]
            return tuple(sorted(items, key=lambda item: item[0]))

        def build_groups(cluster_maps, excluded_cluster):
            groups = {}

            for index, cluster_labels in enumerate(cluster_maps):
                if excluded_cluster not in cluster_labels:
                    raise ValueError(
                        "Intermediate fusion channel is missing."
                    )

                channel = cluster_labels[excluded_cluster]
                key = spectator_key(
                    cluster_labels,
                    excluded_cluster,
                )
                channel_map = groups.setdefault(key, {})

                if channel in channel_map:
                    raise ValueError(
                        "Duplicate fusion channel in an F-move group."
                    )

                channel_map[channel] = index

            return groups

        old_groups = build_groups(
            old_cluster_maps,
            old_intermediate_cluster,
        )
        new_groups = build_groups(
            new_cluster_maps,
            new_intermediate_cluster,
        )

        if set(old_groups) != set(new_groups):
            raise ValueError(
                "Old and new F-move spectator sectors do not match."
            )

        channel_order = (
            Charge.VACUUM,
            Charge.TAU,
        )
        f_plan = []

        for key, old_channels in old_groups.items():
            new_channels = new_groups[key]

            if len(old_channels) != len(new_channels):
                raise ValueError(
                    "F-move sector dimensions do not match."
                )

            if len(old_channels) == 1:
                old_index = next(iter(old_channels.values()))
                new_index = next(iter(new_channels.values()))
                f_plan.append((
                    (old_index,),
                    (new_index,),
                ))
                continue

            if (
                set(old_channels) != set(channel_order)
                or set(new_channels) != set(channel_order)
            ):
                raise ValueError(
                    "Unsupported multi-channel F-move sector."
                )

            f_plan.append((
                tuple(
                    old_channels[channel]
                    for channel in channel_order
                ),
                tuple(
                    new_channels[channel]
                    for channel in channel_order
                ),
            ))

        return tuple(f_plan)

    def state_vector_after_f(
        self,
        new_basis: FusionBasis,
        old_intermediate_cluster: frozenset,
        new_intermediate_cluster: frozenset,
        direction: str,
        old_cluster_maps: tuple[dict, ...] | None = None,
        new_cluster_maps: tuple[dict, ...] | None = None,
        f_plan: tuple | None = None,
    ) -> np.ndarray:
        """Return the statevector transformed into an F-related basis."""

        if f_plan is None:
            f_plan = self.build_f_plan(
                new_basis=new_basis,
                old_intermediate_cluster=old_intermediate_cluster,
                new_intermediate_cluster=new_intermediate_cluster,
                direction=direction,
                old_cluster_maps=old_cluster_maps,
                new_cluster_maps=new_cluster_maps,
            )

        new_state_vector = np.zeros(
            len(new_basis.states),
            dtype=complex,
        )
        matrix = (
            fibonacciConst.F
            if direction == "right"
            else fibonacciConst.F_inv
        )

        for old_indices, new_indices in f_plan:
            if len(old_indices) == 1:
                new_state_vector[new_indices[0]] = (
                    self.state_vector[old_indices[0]]
                )
                continue

            old_local_vector = np.array([
                self.state_vector[index]
                for index in old_indices
            ], dtype=complex)
            new_local_vector = matrix @ old_local_vector

            for row, new_index in enumerate(new_indices):
                new_state_vector[new_index] = new_local_vector[row]

        return new_state_vector

    def __str__(self):
        return (
            f"HilbertSpace(\n"
            f"    qubits = {self.qubits_num},\n"
            f"    dimension = {self.dimension},\n"
            f"    state_vector_shape = {self.state_vector.shape},\n"
            f")"
        )


    def __repr__(self):
        return self.__str__()
