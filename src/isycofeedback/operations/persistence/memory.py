"""In-memory persistence backend for tests and ephemeral runs."""
from __future__ import annotations

import threading
from typing import Any, Mapping

from .errors import ConflictError

# Legal state transitions
LEGAL_LEASE_TRANSITIONS: dict[str, set[str]] = {
    "OPEN": {"SATISFIED", "EXPIRED", "CANCELLED"},
    "SATISFIED": set(),
    "EXPIRED": set(),
    "CANCELLED": set(),
    "UNKNOWN": set(),
}

LEGAL_EXECUTION_TRANSITIONS: dict[str, set[str]] = {
    "RUN_STARTED": {"LEASE_OPEN", "RECOVERY_REQUIRED"},
    "LEASE_OPEN": {"FINDING_CREATED", "RECOVERY_REQUIRED"},
    "FINDING_CREATED": {"ACTION_REQUESTED", "LEASE_EVALUATED", "RECOVERY_REQUIRED"},
    "ACTION_REQUESTED": {"ACTION_RESULT_RECORDED", "RECOVERY_REQUIRED"},
    "ACTION_RESULT_RECORDED": {"LEASE_EVALUATED", "RECOVERY_REQUIRED"},
    "LEASE_EVALUATED": {"RUN_COMPLETED", "RECOVERY_REQUIRED"},
    "RUN_COMPLETED": set(),
    "RECOVERY_REQUIRED": set(),
}


class MemoryBackend:
    """Dict-backed persistence. Thread-safe. Stdlib only."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}
        self._lock = threading.Lock()
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def close(self) -> None:
        pass

    def get(self, namespace: str, key: str) -> Mapping[str, Any] | None:
        with self._lock:
            return self._data.get(namespace, {}).get(key)

    def put(self, namespace: str, key: str, value: Mapping[str, Any]) -> None:
        with self._lock:
            self._data.setdefault(namespace, {})[key] = dict(value)

    def put_immutable(self, namespace: str, key: str, data_json: str) -> None:
        with self._lock:
            ns = self._data.setdefault(namespace, {})
            existing = ns.get(key)
            if existing is None:
                ns[key] = {"data": data_json}
            elif existing["data"] == data_json:
                pass  # idempotent
            else:
                raise ConflictError(f"{namespace}/{key}: content mismatch")

    def upsert_stateful(self, namespace: str, key: str, data_json: str,
                         state: str) -> None:
        with self._lock:
            ns = self._data.setdefault(namespace, {})
            existing = ns.get(key)
            if existing is None:
                ns[key] = {"data": data_json, "state": state}
                return

            current_state = existing["state"]
            if current_state == state and existing["data"] == data_json:
                return  # idempotent

            legal = (LEGAL_LEASE_TRANSITIONS if namespace == "leases"
                     else LEGAL_EXECUTION_TRANSITIONS)
            allowed = legal.get(current_state, set())
            if state not in allowed:
                raise ConflictError(
                    f"Illegal transition: {namespace}/{key} {current_state} → {state}"
                )
            existing["data"] = data_json
            existing["state"] = state

    def delete(self, namespace: str, key: str) -> None:
        with self._lock:
            ns = self._data.get(namespace, {})
            ns.pop(key, None)

    def list_all(self, namespace: str) -> list[Mapping[str, Any]]:
        with self._lock:
            ns = self._data.get(namespace, {})
            primary = {'operational_events': 'event_id', 'findings': 'finding_id',
                       'action_requests': 'action_id', 'action_results': 'result_id',
                       'leases': 'lease_id', 'executions': 'execution_id'}.get(namespace, 'key')
            return [{**v, primary: k} for k, v in ns.items()]

    def list_where(self, namespace: str, field: str, value: Any) -> list[Mapping[str, Any]]:
        with self._lock:
            ns = self._data.get(namespace, {})
            return [{**v, "key": k} for k, v in ns.items() if v.get(field) == value]

    def count(self, namespace: str) -> int:
        with self._lock:
            return len(self._data.get(namespace, {}))

    def execute_raw(self, sql: str, params: tuple = ()) -> list[tuple]:
        raise NotImplementedError("MemoryBackend does not support raw SQL")

    def update_fields(self, namespace: str, key: str, updates: Mapping[str, Any]) -> None:
        with self._lock:
            ns = self._data.get(namespace, {})
            record = ns.get(key)
            if record is not None:
                record.update(updates)
