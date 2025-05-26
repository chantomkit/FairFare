import uuid
from dataclasses import dataclass, field
from numbers import Number
from typing import Dict


@dataclass
class Person:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    net_balance: float = 0.0  # Positive: should receive; Negative: should pay


@dataclass
class Payment:
    participant_contributions: Dict[str, float]
    participant_shares: Dict[str, float]
    split_method: str = "even"
    total: float = field(init=False)

    def __post_init__(self):
        # compute total after initialization
        self.total = sum(self.participant_contributions.values())
        self.validate()

    def validate(self):
        if self.total <= 0:
            raise ValueError("Total amount must be larger than 0.")

        if not all(
            isinstance(paid, Number)
            for paid in self.participant_contributions.values()
        ):
            raise ValueError("Paid values should be numeric.")

        if not all(
            isinstance(share, Number)
            for share in self.participant_shares.values()
        ):
            raise ValueError("Shares should be numeric.")
