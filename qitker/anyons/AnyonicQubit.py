from qitker.anyons.Anyon import Anyon


class AnyonicQubit:
    """Group the four anyons assigned to a logical qubit.

    The anyons remain in the order supplied to the constructor.
    Braiding may change their positions in the fusion tree without
    updating this stored grouping. The quantum state is held elsewhere.

    Attributes:
        qubit_id: Identifier of the logical qubit.
        anyons: The four assigned Anyon objects, in stored order.
    """

    def __init__(self, qubit_id: int, anyons: list[Anyon]):
        """Store a logical qubit ID and its four anyons.

        The supplied collection is stored directly, without copying it.

        Args:
            qubit_id: Integer identifier of the logical qubit.
            anyons: Four Anyon objects in their assigned order.

        Raises:
            TypeError: If qubit_id is not an integer or an element
                of anyons is not an Anyon.
            ValueError: If anyons does not contain exactly four elements.
        """

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if len(anyons) != 4:
            raise ValueError(
                f"An AnyonicQubit requires exactly 4 anyons, "
                f"received {len(anyons)}."
            )

        if not all(isinstance(anyon, Anyon) for anyon in anyons):
            raise TypeError(
                "All elements in anyons must be Anyon objects."
            )

        self.qubit_id = qubit_id
        self.anyons = anyons
#############################################################################
    def get_left_pair(self):
        """Return the first two anyons in the stored order."""
        return self.anyons[0], self.anyons[1]


    def get_middle_pair(self):
        """Return the second and third anyons in the stored order."""
        return self.anyons[1], self.anyons[2]


    def get_right_pair(self):
        """Return the last two anyons in the stored order."""
        return self.anyons[2], self.anyons[3]

    def get_id_list(self):
        """Return the anyon IDs as a new list in the stored order."""
        return [i.get_id() for i in self.anyons]


    def __repr__(self):
        """Return the anyon IDs as a new list in the stored order."""
        return (
            f"AnyonicQubit("
            f"qubit_id={self.qubit_id}, "
            f"anyons={self.anyons}"
            f")"
        )




   