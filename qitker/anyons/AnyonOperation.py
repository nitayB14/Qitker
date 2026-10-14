class AnyonOperation:
    """Store a description of an anyonic operation.

    The operation type identifies the kind of action, such as "F_MOVE",
    "R_MOVE", or "SIGMA". Additional details are kept in parameters.
    This class stores metadata; it does not execute the operation.

    Attributes:
        operation_type: Name of the operation.
        inverse: Whether the recorded operation is an inverse operation.
        parameters: Operation-specific details supplied as keyword arguments.
    """

    def __init__(self, operation_type, inverse=False, **parameters):
        """Create an operation record.

        Args:
            operation_type: Name of the operation. Any string is accepted.
            inverse: Whether to mark the operation as inverse.
                Defaults to False.
            **parameters: Additional operation-specific details to store.
                Their names and values are not validated here.

        Raises:
            TypeError: If operation_type is not a string or inverse
                is not a boolean.
        """

        if not isinstance(operation_type, str):
            raise TypeError("operation_type must be a string.")

        if not isinstance(inverse, bool):
            raise TypeError("inverse must be a boolean.")

        self.operation_type = operation_type
        self.inverse = inverse
        self.parameters = parameters

    def __str__(self):
        return (
            f"AnyonOperation("
            f"type={self.operation_type}, "
            f"inverse={self.inverse}, "
            f"parameters={self.parameters}"
            f")"
        )

    def __repr__(self):
        """Return the same description as __str__."""
        return self.__str__()

