import uuid
from numbers import Number
from typing import Dict


class Person:
    def __init__(self, name: str):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.net_balance: float = (
            0.0  # Positive: should receive; Negative: should pay
        )


class Payment:
    def __init__(
        self,
        participant_contributions: Dict[str, float],
        participant_shares: Dict[str, float],
        split_method: str = "even",  # Default to even split
    ):
        """
        participant_contributions: mapping from person id to amount they paid
        participants: list of person ids among whom to split the cost
        split_method: 'equal' (default) or 'exact' (shares set via set_exact_shares)
        """
        self.participant_contributions = participant_contributions
        self.participant_shares = participant_shares
        # always compute total from contributions
        self.total = sum(participant_contributions.values())
        self.split_method = split_method

        self.validate()

    def validate(self):
        if self.total <= 0:
            raise ValueError("Total amount must be larger than 0.")

        if not any(
            isinstance(paid, Number)
            for paid in self.participant_contributions.values()
        ):
            raise ValueError("Paid values should be numeric.")

        if not any(
            isinstance(share, Number)
            for share in self.participant_shares.values()
        ):
            raise ValueError("Shares should be numeric.")
