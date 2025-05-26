from typing import Dict, List, Tuple

from FairFare.core import Payment, Person
from FairFare.utils.mappings import (
    SETTLEMENT_METHODS_MAPPING,
    SPLIT_METHODS_MAPPING,
)


class ExpenseManager:
    def __init__(self, names: List[str], settlement_method: str = "greedy"):
        self.names = names
        self.payments: List[Payment] = []
        self.settlement_method = settlement_method
        self.validate()
        self.initalise_participant_list()

    def validate(self):
        if not self.names:
            raise ValueError("At least one participant is required.")

        if any(name is None or name.strip() == "" for name in self.names):
            raise ValueError("Participant names must be non-empty strings.")

        if self.settlement_method not in SETTLEMENT_METHODS_MAPPING:
            raise ValueError(
                f"Unknown settlement_method '{self.settlement_method}'. "
                f"Available methods: {list(SETTLEMENT_METHODS_MAPPING.keys())}"
            )

    def initalise_participant_list(self):
        self.people: Dict[str, Person] = {}
        for name in self.names:
            person = Person(name)
            self.people[person.id] = person

    def add_payment(self, payment: Payment):
        self.payments.append(payment)

    def balance_expenses(self):
        # reset
        for p in self.people.values():
            p.net_balance = 0.0
        # apply payments
        for pay in self.payments:
            split_shares = SPLIT_METHODS_MAPPING[pay.split_method](
                pay.total, pay.participant_shares
            )

            for pid, paid in pay.participant_contributions.items():
                self.people[pid].net_balance += paid
            # subtract owed shares
            for pid, share in split_shares.items():
                self.people[pid].net_balance -= share

    def get_net_balances(self) -> Dict[str, float]:
        return {p.id: p.net_balance for p in self.people.values()}

    def settle(self) -> List[Tuple[str, str, float]]:
        flows = SETTLEMENT_METHODS_MAPPING[self.settlement_method](
            self.get_net_balances()
        )
        return flows
