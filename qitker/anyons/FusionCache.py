"""Runtime cache infrastructure for the Fibonacci-anyon backend.

The cache contains derived, reproducible metadata only.  It must never own
physical simulation state such as a state vector, a fusion tree, operation
history, measurement results, or fidelity state.

Each ``FusionSystem`` is expected to own its own ``FusionCache`` instance.
Cache contents and statistics are deliberately not transactional: rolling
back a failed physical operation must restore the engine state, but it does
not need to remove valid metadata that was calculated while attempting that
operation.

This module currently provides the C0 cache container and instrumentation.
Lookup and storage operations for individual cache namespaces are introduced
in the later cache stages.
"""


class FusionCache:
    """Own derived cache namespaces and their runtime statistics.

    The namespace dictionaries are private so later stages can add validated
    lookup and storage operations without exposing mutable cache internals.
    Statistics can be inspected through :meth:`snapshot_stats`, which returns
    an independent dictionary safe for tests and performance reporting.

    Args:
        enabled: Whether callers should use cached values when cache lookup is
            implemented.  C0 records this setting but does not perform lookup.
    """

    _NAMESPACES = (
        "basis",
        "reindex",
        "r_plan",
        "cluster",
        "f_plan",
    )

    _COUNTER_NAMES = (
        "requests",
        "hits",
        "misses",
        "bypasses",
        "builds",
    )

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

        self._bases: dict[object, object] = {}
        self._reindex_maps: dict[object, object] = {}
        self._r_plans: dict[object, object] = {}
        self._cluster_labels: dict[object, object] = {}
        self._f_plans: dict[object, object] = {}

        self._stores = {
            "basis": self._bases,
            "reindex": self._reindex_maps,
            "r_plan": self._r_plans,
            "cluster": self._cluster_labels,
            "f_plan": self._f_plans,
        }

        self._stats = {
            f"{namespace}_{counter}": 0
            for namespace in self._NAMESPACES
            for counter in self._COUNTER_NAMES
        }

    @property
    def enabled(self) -> bool:
        """Return whether cache use is enabled."""

        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable cache use after validating the setting."""

        if not isinstance(value, bool):
            raise TypeError("enabled must be a boolean.")

        self._enabled = value

    @classmethod
    def _validate_namespace(cls, namespace: str) -> None:
        """Validate a statistics namespace used by the cache."""

        if not isinstance(namespace, str):
            raise TypeError("namespace must be a string.")

        if namespace not in cls._NAMESPACES:
            valid_namespaces = ", ".join(cls._NAMESPACES)
            raise ValueError(
                "Unsupported cache namespace. "
                f"Expected one of: {valid_namespaces}."
            )

    def _record(self, namespace: str, counter: str) -> None:
        """Increment one validated namespace counter."""

        self._validate_namespace(namespace)

        if counter not in self._COUNTER_NAMES:
            raise ValueError(f"Unsupported cache counter: {counter}.")

        self._stats[f"{namespace}_{counter}"] += 1

    def record_request(self, namespace: str) -> None:
        """Record one request for a cache namespace."""

        self._record(namespace, "requests")

    def record_hit(self, namespace: str) -> None:
        """Record one successful cache lookup."""

        self._record(namespace, "hits")

    def record_miss(self, namespace: str) -> None:
        """Record one enabled lookup whose key was not cached."""

        self._record(namespace, "misses")

    def record_bypass(self, namespace: str) -> None:
        """Record one request that intentionally bypassed cache lookup."""

        self._record(namespace, "bypasses")

    def record_build(self, namespace: str) -> None:
        """Record one successfully completed metadata construction."""

        self._record(namespace, "builds")

    def snapshot_stats(self) -> dict[str, int | bool]:
        """Return an independent snapshot for tests and benchmarks.

        Entry counts are calculated from the namespace dictionaries instead
        of maintained as counters, preventing them from becoming inconsistent
        with the actual stored data.
        """

        snapshot: dict[str, int | bool] = {
            "cache_enabled": self.enabled,
            **self._stats,
        }

        for namespace, store in self._stores.items():
            snapshot[f"{namespace}_entries"] = len(store)

        return snapshot

    def reset_stats(self) -> None:
        """Reset all counters while preserving cached entries and settings."""

        for key in self._stats:
            self._stats[key] = 0

    def clear(self) -> None:
        """Remove every cached entry and reset all runtime counters.

        The ``enabled`` setting is preserved so clearing a cache does not
        silently change which execution mode the owning system requested.
        """

        for store in self._stores.values():
            store.clear()

        self.reset_stats()


    def lookup(self, namespace: str, key: object,) -> tuple[bool, object | None]:
        self._validate_namespace(namespace)
        self.record_request(namespace)

        if not self.enabled:
            self.record_bypass(namespace)
            return False, None

        store = self._stores[namespace]

        if key not in store:
            self.record_miss(namespace)
            return False, None

        self.record_hit(namespace)
        return True, store[key]


    def store(self, namespace: str, key: object, value: object,) -> None:
        self._validate_namespace(namespace)

        if not self.enabled:
            raise RuntimeError(
                "Cannot store entries while cache use is disabled."
            )

        if value is None:
            raise ValueError(
                "A cached value cannot be None."
            )

        self._stores[namespace][key] = value

    def get_or_build(self, namespace: str, key: object, builder,) -> object:
        found, value = self.lookup(
            namespace,
            key,
        )

        if found:
            return value

        value = builder()
        self.record_build(namespace)

        if self.enabled:
            self.store(
                namespace,
                key,
                value,
            )

        return value

