from qitker.anyons.Anyon import Anyon


class AnyonicQubit:
    """
    Represents one logical qubit encoded by four Fibonacci anyons.
    """

    def __init__(self, qubit_id: int, anyons: list[Anyon]):

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
        return self.anyons[0], self.anyons[1]


    def get_middle_pair(self):
        return self.anyons[1], self.anyons[2]


    def get_right_pair(self):
        return self.anyons[2], self.anyons[3]

    def get_id_list(self):
        return [i.get_id() for i in self.anyons]

    #return information about the logical anyon qubit
    def __repr__(self):
        return (
            f"AnyonicQubit("
            f"qubit_id={self.qubit_id}, "
            f"anyons={self.anyons}"
            f")"
        )




   