import uuid
from dataclasses import dataclass, field
from numbers import Number
from typing import Dict

from FairFare.utils.mappings import SPLIT_METHODS_MAPPING


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
    description: str = ""
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

        if self.split_method not in SPLIT_METHODS_MAPPING:
            raise ValueError(
                f"Unknown split method '{self.split_method}'. "
                f"Available methods: {list(SPLIT_METHODS_MAPPING.keys())}"
            )
