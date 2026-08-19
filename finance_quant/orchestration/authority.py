"""Capability classes and capability-by-absence enforcement (issue #10, invariants 8-10).

A worker subprocess runs with an environment that *does not contain* handles to the
experiment ledger, promotion API, or sealed storage. Enforcement is therefore
structural: this module both (a) constructs sanitized worker environments and
(b) provides the assertion a worker main calls before doing anything.
"""
from __future__ import annotations

import os
from enum import Enum
from typing import Mapping


class CapabilityClass(str, Enum):
    RESEARCH_WORKER = "research_worker"
    SEALED_SCORING_WORKER = "sealed_scoring_worker"
    SCHEDULER_CORE = "scheduler_core"
    PROMOTION_SERVICE = "promotion_service"


class AuthorityViolation(PermissionError):
    pass


# Handles that MUST NOT be present in an ordinary research worker's environment.
FORBIDDEN_WORKER_VARS = (
    "FQ_ATTEMPT_LEDGER_PATH",
    "FQ_EXPERIMENT_LEDGER_URI",
    "FQ_PROMOTION_API",
    "FQ_SEALED_STORE",
    "MLFLOW_TRACKING_URI",
)

# Sealed scoring additionally loses all network egress (memo #9).
SEALED_FORBIDDEN_EXTRA = ("FQ_LITELLM_BASE", "OPENAI_API_BASE", "HTTP_PROXY", "HTTPS_PROXY")

_OS_MINIMAL = ("PATH", "SystemRoot", "SYSTEMROOT", "WINDIR", "PYTHONPATH")


def worker_environment(capability: CapabilityClass,
                       base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build a sanitized env for a worker subprocess (capability by absence)."""
    base = base if base is not None else os.environ
    forbidden = set(FORBIDDEN_WORKER_VARS)
    if capability is CapabilityClass.SEALED_SCORING_WORKER:
        forbidden |= set(SEALED_FORBIDDEN_EXTRA)
    env = {k: v for k, v in base.items()
           if k in _OS_MINIMAL or k.startswith("FQ_TASK_")}
    env = {k: v for k, v in env.items() if k not in forbidden}
    env["FQ_CAPABILITY"] = capability.value
    return env


def assert_worker_capability(env: Mapping[str, str] | None = None) -> CapabilityClass:
    """Called by worker_main BEFORE any task code runs."""
    env = env if env is not None else os.environ
    present = [v for v in FORBIDDEN_WORKER_VARS if v in env]
    cap_raw = env.get("FQ_CAPABILITY", CapabilityClass.RESEARCH_WORKER.value)
    capability = CapabilityClass(cap_raw)
    if capability is CapabilityClass.SEALED_SCORING_WORKER:
        present += [v for v in SEALED_FORBIDDEN_EXTRA if v in env]
    if present:
        raise AuthorityViolation(
            f"worker environment contains forbidden handles: {sorted(present)}"
        )
    return capability
