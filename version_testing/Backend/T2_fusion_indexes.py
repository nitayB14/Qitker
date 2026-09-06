"""Compare two quantum registers with Grover-style phase amplification."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))



from qitker import circuit, qubit, qRegister
from qitker.anyons.Anyon import Charge, fusion_outcomes
from qitker.anyons.FusionSystem import FusionSystem
from qitker.anyons.FusionBasis import FusionBasis



def test_fusion_outcomes():
    assert fusion_outcomes(
        Charge.VACUUM,
        Charge.VACUUM,
    ) == (Charge.VACUUM,)

    assert fusion_outcomes(
        Charge.VACUUM,
        Charge.TAU,
    ) == (Charge.TAU,)

    assert fusion_outcomes(
        Charge.TAU,
        Charge.VACUUM,
    ) == (Charge.TAU,)

    assert fusion_outcomes(
        Charge.TAU,
        Charge.TAU,
    ) == (
        Charge.VACUUM,
        Charge.TAU,
    )

def test_state_index_mapping():
    for qubits_num in (1, 2, 3, 4):
        fs = FusionSystem(qubits_num)

        basis = FusionBasis(
            tree=fs.tree,
            qubits=fs.qubits,
            total_charge=Charge.VACUUM,
        )

        assert (
            len(basis.state_to_index)
            == len(basis.states)
        )

        for expected_index, expected_state in enumerate(
            basis.states
        ):
            actual_state = basis.get_state(
                expected_index
            )

            actual_index = basis.get_index(
                expected_state
            )

            assert actual_state == expected_state
            assert actual_index == expected_index

        print(f"{qubits_num} qubits:")
        print(
            f"  states:      {len(basis.states)}"
        )
        print(
            f"  unique keys: "
            f"{len(basis.state_to_index)}"
        )
        print(
            f"  round trips: "
            f"{len(basis.states)}/"
            f"{len(basis.states)}"
        )
        print("  result:      PASS")
        print()


def main():
    test_fusion_outcomes()
    test_state_index_mapping()
    


main()
