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

def test_fusion_space_dimensions():
    expected_vacuum_dimensions = {
        1: 2,
        2: 13,
        3: 89,
        4: 610,
        5: 4181,
        6: 28657,
    }

    for qubits_num, expected_vacuum in (
        expected_vacuum_dimensions.items()
    ):
        fs = FusionSystem(qubits_num)

        basis = FusionBasis(
            tree=fs.tree,
            qubits=fs.qubits,
            total_charge=Charge.VACUUM,
        )

        all_states = basis._enumerate_subtree(
            fs.tree.structure
        )

        vacuum_states = sum(
            state["total"] is Charge.VACUUM
            for state in all_states
        )

        tau_states = sum(
            state["total"] is Charge.TAU
            for state in all_states
        )

        total_fusion_states = len(all_states)

        physical_states = len(basis.states)
        computational_states = 2 ** qubits_num
        leakage_states = (
            physical_states - computational_states
        )

        assert vacuum_states == expected_vacuum

        assert physical_states == vacuum_states

        assert (
            vacuum_states + tau_states
            == total_fusion_states
        )

        assert (
            computational_states + leakage_states
            == physical_states
        )

        assert all(
            state["total"] is Charge.VACUUM
            for state in basis.states
        )

        print(f"{qubits_num} qubits:")
        print(
            f"  all fusion states:     "
            f"{total_fusion_states}"
        )
        print(
            f"  total VACUUM:          "
            f"{vacuum_states}"
        )
        print(
            f"    computational:       "
            f"{computational_states}"
        )
        print(
            f"    leakage:             "
            f"{leakage_states}"
        )
        print(
            f"  total TAU:             "
            f"{tau_states}"
        )
        print(
            "  fusion sectors match:  "
            f"{vacuum_states} + "
            f"{tau_states} = "
            f"{total_fusion_states}"
        )
        print(
            "  physical space matches:"
            f"  {computational_states} + "
            f"{leakage_states} = "
            f"{physical_states}"
        )
        print("  result:                PASS")
        print()



def main():
    test_fusion_outcomes()
    test_fusion_space_dimensions()
    


main()
