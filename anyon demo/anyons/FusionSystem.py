from anyons.Anyon import Anyon, Charge
from anyons.AnyonicQubit import AnyonicQubit
from anyons.FusionTree import FusionTree
from anyons.AnyonOperation import AnyonOperation

class FusionSystem:
    """
    Represents a global system of Fibonacci anyonic qubits.
    """

    def __init__(self, qubits_num: int):

        if not isinstance(qubits_num, int):
            raise TypeError("qubits_num must be an integer.")

        if qubits_num < 1:
            raise ValueError("qubits_num must be at least 1.")

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

    def get_qubit(self, qubit_id):
        """
        Returns the AnyonicQubit with the given ID.
        """

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= len(self.qubits):
            raise ValueError(f"Qubit {qubit_id} does not exist.")

        return self.qubits[qubit_id]

    def get_anyon(self, anyon_id):
        """
        Returns the Anyon with the given ID.
        """

        if not isinstance(anyon_id, int):
            raise TypeError("anyon_id must be an integer.")

        if anyon_id < 1 or anyon_id > len(self.anyons):
            raise ValueError(f"Anyon {anyon_id} does not exist.")

        return self.anyons[anyon_id - 1]

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
            charge = (
                Charge.VACUUM
                if anyon_id % 4 == 1
                else Charge.TAU
            )

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
        return self.operation_history.copy()


    def clear_operation_history(self):
        self.operation_history.clear()


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