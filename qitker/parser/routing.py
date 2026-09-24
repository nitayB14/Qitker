



ANYONS_PER_QUBIT = 4

def get_required_order(
    target: int,
    controllers: list[int] | tuple[int, ...] = (),
) -> tuple[int, ...]:
    """
    Return the participating logical qubits in the canonical order
    expected by the braid sequence.

    Controlled-gate braid sequences expect all controllers first,
    followed by the target.
    """

    if isinstance(target, bool) or not isinstance(target, int):
        raise TypeError(
            "target must be an integer."
        )

    if target < 0:
        raise ValueError(
            "target cannot be negative."
        )

    if not isinstance(controllers, (list, tuple)):
        raise TypeError(
            "controllers must be a list or tuple."
        )

    if len(controllers) > 2:
        raise ValueError(
            "At most two controller qubits are supported."
        )

    normalized_controllers = []

    for position, controller in enumerate(controllers):
        if isinstance(controller, bool) or not isinstance(controller, int):
            raise TypeError(
                f"controller at position {position} "
                "must be an integer."
            )

        if controller < 0:
            raise ValueError(
                f"controller at position {position} "
                "cannot be negative."
            )

        if controller == target:
            raise ValueError(
                "target cannot also be a controller."
            )

        if controller in normalized_controllers:
            raise ValueError(
                "controllers cannot contain duplicate qubits."
            )

        normalized_controllers.append(controller)

    return tuple(normalized_controllers) + (target,)



def get_block_swap_sequence(
    left_slot: int,
    qubits_num: int,
) -> tuple[int, ...]:
    """
    Return the sigma_global sequence that swaps two adjacent
    four-anyon logical-qubit blocks.

    left_slot is the zero-based physical slot of the left block.
    The right block is therefore left_slot + 1.
    """

    if isinstance(left_slot, bool) or not isinstance(left_slot, int):
        raise TypeError("left_slot must be an integer.")

    if isinstance(qubits_num, bool) or not isinstance(qubits_num, int):
        raise TypeError("qubits_num must be an integer.")

    if qubits_num < 2:
        raise ValueError(
            "At least two qubits are required for a block swap."
        )

    if left_slot < 0 or left_slot >= qubits_num - 1:
        raise ValueError(
            "left_slot must identify two adjacent qubit slots."
        )

    boundary = ANYONS_PER_QUBIT * (left_slot + 1)

    sequence = []

    for row in range(ANYONS_PER_QUBIT):
        start_index = boundary - row

        sequence.extend(
            range(
                start_index,
                start_index + ANYONS_PER_QUBIT,
            )
        )

    return tuple(sequence)




def get_routing_sequence(
    required_order: list[int] | tuple[int, ...],
    qubits_num: int,
) -> tuple[int, ...]:
    """
    Return a sigma_global sequence that moves the requested logical
    qubits into the leftmost physical slots in the requested order.

    The initial physical layout is assumed to be:
        (0, 1, 2, ..., qubits_num - 1)

    required_order describes the logical qubits that should occupy
    physical slots 0, 1, ... after routing.
    """

    if not isinstance(required_order, (list, tuple)):
        raise TypeError(
            "required_order must be a list or tuple."
        )

    if isinstance(qubits_num, bool) or not isinstance(qubits_num, int):
        raise TypeError(
            "qubits_num must be an integer."
        )

    if qubits_num < 1:
        raise ValueError(
            "qubits_num must be at least 1."
        )

    if not required_order:
        raise ValueError(
            "required_order must contain at least one qubit."
        )

    if len(required_order) > 3:
        raise ValueError(
            "Routing supports at most three participating qubits."
        )

    if len(required_order) > qubits_num:
        raise ValueError(
            "required_order cannot contain more qubits "
            "than the system."
        )

    for position, qubit_id in enumerate(required_order):
        if isinstance(qubit_id, bool) or not isinstance(qubit_id, int):
            raise TypeError(
                f"qubit ID at position {position} "
                "must be an integer."
            )

        if qubit_id < 0 or qubit_id >= qubits_num:
            raise ValueError(
                f"qubit ID at position {position} "
                f"must be between 0 and {qubits_num - 1}."
            )

    if len(set(required_order)) != len(required_order):
        raise ValueError(
            "required_order cannot contain duplicate qubits."
        )

    layout = list(range(qubits_num))
    routing_sequence = []

    for destination_slot, logical_qubit in enumerate(required_order):
        current_slot = layout.index(logical_qubit)

        while current_slot > destination_slot:
            left_slot = current_slot - 1

            routing_sequence.extend(
                get_block_swap_sequence(
                    left_slot=left_slot,
                    qubits_num=qubits_num,
                )
            )

            layout[left_slot], layout[current_slot] = (
                layout[current_slot],
                layout[left_slot],
            )

            current_slot -= 1

    return tuple(routing_sequence)


def invert_sequence(
    sequence: list[int] | tuple[int, ...],
) -> tuple[int, ...]:
    """
    Return the exact inverse of a chronological braid sequence.

    The inverse is obtained by reversing the operation order and
    replacing every sigma index with its negative.
    """

    if not isinstance(sequence, (list, tuple)):
        raise TypeError("sequence must be a list or tuple.")

    for position, index in enumerate(sequence):
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(
                f"sequence index at position {position} "
                "must be an integer."
            )

        if index == 0:
            raise ValueError(
                f"sequence index at position {position} "
                "cannot be zero."
            )

    return tuple(
        -index
        for index in reversed(sequence)
    )


def shift_sequence(
    sequence: list[int] | tuple[int, ...],
    start_slot: int,
    qubits_num: int,
) -> tuple[int, ...]:
    """
    Shift a canonical braid sequence to another physical qubit slot.

    Braid indices are signed and one-based. Physical qubit slots are
    zero-based. Each logical qubit occupies four anyon positions.
    """

    if not isinstance(sequence, (list, tuple)):
        raise TypeError(
            "sequence must be a list or tuple."
        )

    if isinstance(start_slot, bool) or not isinstance(start_slot, int):
        raise TypeError(
            "start_slot must be an integer."
        )

    if isinstance(qubits_num, bool) or not isinstance(qubits_num, int):
        raise TypeError(
            "qubits_num must be an integer."
        )

    if qubits_num < 1:
        raise ValueError(
            "qubits_num must be at least 1."
        )

    if start_slot < 0 or start_slot >= qubits_num:
        raise ValueError(
            f"start_slot must be between 0 and {qubits_num - 1}."
        )

    offset = ANYONS_PER_QUBIT * start_slot
    max_sigma_index = (
        ANYONS_PER_QUBIT * qubits_num
    ) - 1

    shifted_sequence = []

    for position, index in enumerate(sequence):
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(
                f"sequence index at position {position} "
                "must be an integer."
            )

        if index == 0:
            raise ValueError(
                f"sequence index at position {position} "
                "cannot be zero."
            )

        shifted_absolute_index = abs(index) + offset

        if shifted_absolute_index > max_sigma_index:
            raise ValueError(
                f"shifted sequence index at position {position} "
                f"exceeds sigma_{max_sigma_index}."
            )

        shifted_index = (
            shifted_absolute_index
            if index > 0
            else -shifted_absolute_index
        )

        shifted_sequence.append(shifted_index)

    return tuple(shifted_sequence)