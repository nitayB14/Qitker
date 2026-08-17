"""Verify register-size inference when ``size`` is not supplied.

Integers use their minimum binary width, while strings preserve their full
length so that leading zeroes remain meaningful to the frontend.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker import circuit, qRegister


def test_register_inferred_size():
    """Check the inferred width for integer and binary-string inputs."""
    cases = (
        (0, 1),
        (1, 1),
        (4, 3),
        ("0001", 4),
        ("1010", 4),
    )

    for initial_value, expected_size in cases:
        circ = circuit()
        register = qRegister(circ, initialize=initial_value)

        assert len(register[::]) == expected_size
        assert circ.getQubitsNumber() == expected_size


if __name__ == "__main__":
    test_register_inferred_size()
    print("T5_register_inferred_size: PASS")
