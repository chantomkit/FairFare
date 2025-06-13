from typing import Dict, List, Union

from FairFare.core import Payment, Person
from FairFare.utils.mappings import SETTLEMENT_METHODS_MAPPING


class ExpenseManager:
    def __init__(
        self,
        participant_list: List[Person],
        payment_list: List[Payment],
        settlement_method: str = "greedy",
    ):
        self.participant_list = participant_list
        self.payment_list = payment_list
        self.settlement_method = settlement_method
        self.validate()
        self.id_to_participant = {p.id: p for p in self.participant_list}

    def validate(self):
        if not self.participant_list:
            raise ValueError("At least one participant is required.")

        if self.settlement_method not in SETTLEMENT_METHODS_MAPPING:
            raise ValueError(
                f"Unknown settlement_method '{self.settlement_method}'. "
                f"Available methods: {list(SETTLEMENT_METHODS_MAPPING.keys())}"
            )

    def _reset_net_balances(self):
        for p in self.id_to_participant.values():
            p.net_balance = 0.0

    def balance_expenses(self):
        # reset
        self._reset_net_balances()
        # apply payments
        for pay in self.payment_list:
            for pid, paid in pay.participant_contributions.items():
                self.id_to_participant[pid].net_balance += paid
            # subtract owed shares
            for pid, share in pay.split_participant_shares.items():
                self.id_to_participant[pid].net_balance -= share

    def get_net_balances(self) -> Dict[str, float]:
        self.balance_expenses()
        return {p.id: p.net_balance for p in self.id_to_participant.values()}

    def settle(self) -> List[Dict[str, Union[str, float]]]:
        flows = SETTLEMENT_METHODS_MAPPING[self.settlement_method](
            self.get_net_balances()
        )
        return flows
