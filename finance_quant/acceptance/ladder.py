"""Python conformance for PromotionLadder.tla: no authority before review, no duplicates."""
from __future__ import annotations

from dataclasses import dataclass


STATES = {"IDLE", "SEALED", "RUNNING", "SCORED", "REVIEW", "PAPER", "TINY_LIVE", "REJECTED"}


class ProtocolError(RuntimeError):
    pass


@dataclass
class Ladder:
    state: str = "IDLE"
    current: str = ""
    authority: dict[str, int] | None = None

    def __post_init__(self) -> None:
        if self.authority is None:
            self.authority = {}

    def seal(self, candidate: str) -> None:
        if self.state != "IDLE":
            raise ProtocolError("seal only from IDLE")
        self.state = "SEALED"
        self.current = candidate

    def run(self) -> None:
        if self.state != "SEALED":
            raise ProtocolError("run only from SEALED")
        self.state = "RUNNING"

    def score(self) -> None:
        if self.state != "RUNNING":
            raise ProtocolError("score only from RUNNING")
        self.state = "SCORED"

    def review(self) -> None:
        if self.state != "SCORED":
            raise ProtocolError("review only from SCORED")
        self.state = "REVIEW"

    def paper_approve(self) -> None:
        if self.state != "REVIEW":
            raise ProtocolError("paper approval requires REVIEW")
        self.authority[self.current] = self.authority.get(self.current, 0) + 1
        if self.authority[self.current] > 1:
            raise ProtocolError("duplicate authority")
        self.state = "PAPER"

    def reject(self) -> None:
        if self.state not in {"REVIEW", "SCORED"}:
            raise ProtocolError("reject only from REVIEW or SCORED")
        self.state = "REJECTED"

    def tiny_live(self) -> None:
        if self.state != "PAPER":
            raise ProtocolError("tiny-live requires PAPER")
        self.state = "TINY_LIVE"

    def reset(self) -> None:
        if self.state not in {"PAPER", "TINY_LIVE", "REJECTED"}:
            raise ProtocolError("reset only from terminal promotion states")
        self.state = "IDLE"
        self.current = ""

    def no_authority_before_review(self) -> bool:
        if self.state in {"IDLE", "SEALED", "RUNNING", "SCORED", "REVIEW"}:
            return all(v == 0 for v in self.authority.values())
        return True
