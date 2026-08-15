"""Validation helpers for Qitker's frontend controlled gates."""


def validate_controlled_gate(
    target,
    control,
    where=None,
    allow_comparison=False,
):
    """Validate and normalize a frontend controlled-gate condition.

    Args:
        target: The qubit on which the gate will be applied.
        control: A single control qubit or a list of control qubits.
        where: ``None``, a condition string, a non-negative integer, or a
            qubit/list of qubits used as an equality reference.
        allow_comparison: Whether a qubit-based equality condition is allowed
            by the calling frontend operation.

    Returns:
        tuple: For a static condition, returns ``(controls, pattern)`` where
        ``pattern`` contains one normalized ``0``, ``1``, or ``x`` character
        per control.  For an enabled equality condition, returns
        ``(controls, references)`` as two equally sized lists of qubits.

    Raises:
        TypeError: If an argument has an unsupported type or the two sides of
            an equality comparison use different container types.
        ValueError: If a control, reference, or condition is invalid.
    """

    # Imported here to avoid a module-level circular import with qubit.py.
    from qitker.compiler.qubit import qubit

    control_is_qubit = isinstance(control, qubit)
    control_is_list = isinstance(control, list)

    if control_is_qubit:
        controls = [control]
    elif control_is_list:
        # Keep validation independent from later changes to the user's list.
        controls = list(control)
    else:
        raise TypeError("control must be a qubit or a list of qubits")

    if not controls:
        raise ValueError(
            "a controlled gate requires at least one control qubit"
        )

    validated_controls = []

    for index, current_control in enumerate(controls):
        if not isinstance(current_control, qubit):
            raise TypeError(f"control at index {index} must be a qubit")

        if current_control is target:
            raise ValueError(
                "target qubit cannot also be a control qubit"
            )

        if current_control._quantumCircuit is not target._quantumCircuit:
            raise ValueError(
                "all control qubits and the target qubit "
                "must belong to the same circuit"
            )

        if any(
            current_control is previous_control
            for previous_control in validated_controls
        ):
            raise ValueError(f"duplicate control qubit at index {index}")

        validated_controls.append(current_control)

    where_is_qubit = isinstance(where, qubit)
    where_is_list = isinstance(where, list)

    if where_is_qubit or where_is_list:
        if not allow_comparison:
            raise TypeError(
                "this controlled gate does not support qubit comparison"
            )

        if control_is_qubit != where_is_qubit:
            raise TypeError(
                "qubit comparison requires qubit with qubit, "
                "or list with list"
            )

        references = [where] if where_is_qubit else list(where)

        if not references:
            raise ValueError(
                "a comparison requires at least one reference qubit"
            )

        if len(validated_controls) != len(references):
            raise ValueError(
                "control and reference lists must have the same length"
            )

        validated_references = []

        for index, reference in enumerate(references):
            if not isinstance(reference, qubit):
                raise TypeError(
                    f"reference at index {index} must be a qubit"
                )

            if reference is target:
                raise ValueError(
                    "target qubit cannot also be a reference qubit"
                )

            if reference._quantumCircuit is not target._quantumCircuit:
                raise ValueError(
                    "all reference qubits and the target qubit "
                    "must belong to the same circuit"
                )

            if any(
                reference is previous_reference
                for previous_reference in validated_references
            ):
                raise ValueError(
                    f"duplicate reference qubit at index {index}"
                )

            validated_references.append(reference)

        same_operands = all(
            current_control is reference
            for current_control, reference in zip(
                validated_controls,
                validated_references,
            )
        )

        operands_overlap = any(
            current_control is reference
            for current_control in validated_controls
            for reference in validated_references
        )

        if operands_overlap and not same_operands:
            raise ValueError(
                "comparison operands cannot partially overlap"
            )

        return validated_controls, validated_references

    controls_number = len(validated_controls)

    if where is None:
        pattern = "1" * controls_number
    elif isinstance(where, bool):
        raise TypeError("where must not be a boolean")
    elif isinstance(where, int):
        if where < 0 or where >= 2 ** controls_number:
            raise ValueError(
                "integer where must be between 0 and "
                f"{(2 ** controls_number) - 1}"
            )

        pattern = format(where, f"0{controls_number}b")
    elif isinstance(where, str):
        pattern = where.lower()
    else:
        raise TypeError(
            "where must be None, a string, an integer, "
            "a qubit, or a list of qubits"
        )

    if len(pattern) != controls_number:
        raise ValueError(
            "where length must match the number of control qubits"
        )

    invalid_characters = {
        character
        for character in pattern
        if character not in "01x"
    }

    if invalid_characters:
        raise ValueError("where may contain only '0', '1', or 'x'")

    return validated_controls, pattern


