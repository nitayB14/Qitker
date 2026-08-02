class AnyonOperation:

    def __init__(self, operation_type, inverse=False, **parameters):
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
        return self.__str__()

"""
# יצירת פעולת R
    r_operation = AnyonOperation(
        operation_type="R",
        first_id=1,
        second_id=2
    )

    # יצירת פעולת F הפוכה
    f_operation = AnyonOperation(
        operation_type="F",
        inverse=True,
        path=(0,),
        direction="left"
    )
"""