"""Section 20: validate the cache infrastructure."""

import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker.anyons.FusionSystem import FusionSystem


TEST_QUBITS = 2

def create_test_systems() -> dict[str, FusionSystem]:
    """Create the systems used by the infrastructure tests."""

    return {
        "enabled": FusionSystem(
            TEST_QUBITS,
            cache_enabled=True,
        ),
        "disabled": FusionSystem(
            TEST_QUBITS,
            cache_enabled=False,
        ),
    }


def run_test(name, test_function, *args) -> None:
    """Run one test and report success."""

    test_function(*args)
    print(f"{name}: PASS")


def assert_namespace_cache_behavior(
    namespace: str,
    enabled_stats: dict,
    disabled_stats: dict,
) -> None:
    """Check enabled and disabled behavior for one cache namespace."""

    assert enabled_stats[f"{namespace}_requests"] > 0
    assert enabled_stats[f"{namespace}_hits"] > 0
    assert enabled_stats[f"{namespace}_misses"] > 0
    assert enabled_stats[f"{namespace}_bypasses"] == 0

    assert (
        enabled_stats[f"{namespace}_requests"]
        == enabled_stats[f"{namespace}_hits"]
        + enabled_stats[f"{namespace}_misses"]
    )

    assert (
        enabled_stats[f"{namespace}_builds"]
        == enabled_stats[f"{namespace}_misses"]
    )

    assert (
        enabled_stats[f"{namespace}_entries"]
        == enabled_stats[f"{namespace}_misses"]
    )

    assert disabled_stats[f"{namespace}_requests"] > 0
    assert disabled_stats[f"{namespace}_hits"] == 0
    assert disabled_stats[f"{namespace}_misses"] == 0

    assert (
        disabled_stats[f"{namespace}_bypasses"]
        == disabled_stats[f"{namespace}_requests"]
    )

    assert (
        disabled_stats[f"{namespace}_builds"]
        == disabled_stats[f"{namespace}_bypasses"]
    )

    assert disabled_stats[f"{namespace}_entries"] == 0


def test_cache_connection(
    systems: dict[str, FusionSystem],
) -> None:
    """Check cache ownership, configuration, and isolation."""

    enabled = systems["enabled"]
    disabled = systems["disabled"]

    assert enabled.cache is not None
    assert disabled.cache is not None

    assert enabled.cache.enabled is True
    assert disabled.cache.enabled is False

    assert enabled.cache is not disabled.cache


def test_cache_statistics(
    systems: dict[str, FusionSystem],
) -> None:
    """Check cache counters, reset, and clear behavior."""

    system = systems["enabled"]
    system.clear_cache()

    initial_stats = system.get_cache_stats()

    assert initial_stats["cache_enabled"] is True
    assert initial_stats["basis_requests"] == 0
    assert initial_stats["basis_hits"] == 0
    assert initial_stats["basis_builds"] == 0
    assert initial_stats["basis_entries"] == 0

    system.cache.record_request("basis")
    system.cache.record_hit("basis")
    system.cache.record_build("basis")

    recorded_stats = system.get_cache_stats()

    assert recorded_stats["basis_requests"] == 1
    assert recorded_stats["basis_hits"] == 1
    assert recorded_stats["basis_builds"] == 1

    system.reset_cache_stats()

    reset_stats = system.get_cache_stats()

    assert reset_stats["basis_requests"] == 0
    assert reset_stats["basis_hits"] == 0
    assert reset_stats["basis_builds"] == 0

    system.clear_cache()

    cleared_stats = system.get_cache_stats()

    assert cleared_stats["cache_enabled"] is True
    assert cleared_stats["basis_entries"] == 0


def test_cache_not_in_physical_snapshot(
    systems: dict[str, FusionSystem],
) -> None:
    """Check that cache state is not part of physical rollback."""

    system = systems["enabled"]
    snapshot = system._capture_state_snapshot()

    assert "cache" not in snapshot
    assert "cache_stats" not in snapshot


def test_cache_flag_does_not_change_physics() -> None:
    """Check identical physics with cache enabled and disabled."""

    enabled = FusionSystem(
        TEST_QUBITS,
        cache_enabled=True,
    )

    disabled = FusionSystem(
        TEST_QUBITS,
        cache_enabled=False,
    )

    # The first sigma 4 builds the required bases. Its inverse revisits those
    # topologies and must produce cache hits. The final sigma leaves both
    # systems in the same non-initial physical state.
    sequence = (4, -4, 4)

    for sigma_index in sequence:
        enabled.sigma_global(sigma_index)
        disabled.sigma_global(sigma_index)

    assert enabled.tree.to_ids() == disabled.tree.to_ids()

    assert (
        enabled.get_current_anyon_order()
        == disabled.get_current_anyon_order()
    )

    assert enabled.basis.tree_signature == disabled.basis.tree_signature

    # Cache reuse must preserve both the exact physical-basis ordering and
    # every mapping used to interpret computational and leakage states.
    assert enabled.basis.states == disabled.basis.states
    assert enabled.basis.state_to_index == disabled.basis.state_to_index
    assert (
        enabled.basis.computational_indices
        == disabled.basis.computational_indices
    )
    assert enabled.basis.leakage_indices == disabled.basis.leakage_indices
    assert (
        enabled.basis.logical_to_physical
        == disabled.basis.logical_to_physical
    )
    assert (
        enabled.basis.physical_to_logical
        == disabled.basis.physical_to_logical
    )

    assert np.array_equal(
        enabled.hilbertSpace.get_state_vector(),
        disabled.hilbertSpace.get_state_vector(),
    )

    enabled_stats = enabled.get_cache_stats()
    disabled_stats = disabled.get_cache_stats()

    for namespace in (
        "basis",
        "reindex",
        "r_plan",
        "cluster",
        "f_plan",
    ):
        assert_namespace_cache_behavior(
            namespace,
            enabled_stats,
            disabled_stats,
        )

        print(f"  {namespace} cache behavior: PASS")

def test_foreign_basis_is_rejected() -> None:
    """Reject a cached basis owned by another FusionSystem."""

    owner = FusionSystem(TEST_QUBITS)
    target = FusionSystem(TEST_QUBITS)

    target.clear_cache()

    key = target._get_basis_cache_key(
        classify_logical=True,
    )

    target.cache.store(
        "basis",
        key,
        owner.basis,
    )

    try:
        target._get_or_build_basis(
            classify_logical=True,
        )
    except RuntimeError:
        return

    raise AssertionError(
        "FusionSystem accepted a basis owned by another system."
    )

def main() -> None:
    """Run the selected cache infrastructure tests."""

    print("Creating T20 test systems...")
    systems = create_test_systems()

    run_test(
        "Cache connection",
        test_cache_connection,
        systems,
    )

    run_test(
        "Cache statistics",
        test_cache_statistics,
        systems,
    )

    run_test(
        "Cache outside physical snapshot",
        test_cache_not_in_physical_snapshot,
        systems,
    )

    run_test(
        "Cache flag physical equivalence",
        test_cache_flag_does_not_change_physics,
    )

    run_test(
        "Foreign basis rejection",
        test_foreign_basis_is_rejected,
    )

    print("All selected section 20 cache tests passed.")


if __name__ == "__main__":
    main()
