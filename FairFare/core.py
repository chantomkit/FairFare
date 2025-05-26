from typing import List, Dict, Tuple
from FairFare.strategies.mapping import SPLIT_METHODS_MAPPING
import uuid
from numbers import Number

class Person:
    def __init__(self, name: str):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.net_balance: float = 0.0  # Positive: should receive; Negative: should pay

    def __repr__(self):
        balance = round(self.net_balance, 2)
        return f"Person(id={self.id}, name='{self.name}', net_balance={balance})"

class Payment:
    def __init__(
        self,
        participant_contributions: Dict[str, float],
        participant_shares: Dict[str, float],
        strategy: str = 'even' # Default to even split
    ):
        """
        participant_contributions: mapping from person id to amount they paid
        participants: list of person ids among whom to split the cost
        strategy: 'equal' (default) or 'exact' (shares set via set_exact_shares)
        """
        self.contributions = participant_contributions
        self.participant_shares = participant_shares
        # always compute total from contributions
        self.total = sum(participant_contributions.values())
        self.strategy = strategy

        self.validate()
        self.shares = SPLIT_METHODS_MAPPING[self.strategy](self.total, self.participant_shares)

    def validate(self):
        if self.total <= 0:
            raise ValueError("Total amount must be larger than 0.")
        
        if not any(isinstance(paid, Number) for paid in self.contributions.values()):
            raise ValueError("Paid values should be numeric.")

        if not any(isinstance(share, Number) for share in self.participant_shares.values()):
            raise ValueError("Shares should be numeric.")
        
        if self.strategy not in SPLIT_METHODS_MAPPING:
            raise ValueError(f"Unknown strategy '{self.strategy}'. Available strategies: {list(SPLIT_METHODS_MAPPING.keys())}")

    def apply(self, people: Dict[str, Person]):
        # add contributions
        for pid, paid in self.contributions.items():
            people[pid].net_balance += paid
        # subtract owed shares
        for pid, share in self.shares.items():
            people[pid].net_balance -= share

    def __repr__(self):
        return (f"Payment(total={self.total}, contributions={self.contributions}, "
                f"shares={self.shares}, strategy='{self.strategy}')")

class Settlement:
    @staticmethod
    def compute(people: Dict[str, Person]) -> List[Tuple[str, str, float]]:
        """
        Computes the net balances and returns a list of settlements.
        Each settlement is a tuple (debtor_id, creditor_id, amount).
        """
        total_balance = sum(p.net_balance for p in people.values())
        # Check if the total balance is zero
        if abs(total_balance) > 1e-9:
            raise ValueError(f"Invalid balances: total net balance is {total_balance}, must be zero")

        # prepare lists
        positives = [(p.id, p.net_balance) for p in people.values() if p.net_balance > 0]
        negatives = [(p.id, -p.net_balance) for p in people.values() if p.net_balance < 0]
        positives.sort(key=lambda x: x[1])
        negatives.sort(key=lambda x: x[1])

        i, j = 0, 0
        settlements: List[Tuple[str, str, float]] = []
        while i < len(negatives) and j < len(positives):
            debtor_id, debt = negatives[i]
            creditor_id, credit = positives[j]
            amount = min(debt, credit)
            settlements.append((debtor_id, creditor_id, round(amount, 2)))
            debt -= amount
            credit -= amount
            if debt == 0:
                i += 1
            else:
                negatives[i] = (debtor_id, debt)
            if credit == 0:
                j += 1
            else:
                positives[j] = (creditor_id, credit)
        return settlements

class ExpenseManager:
    def __init__(self):
        self.people: Dict[str, Person] = {}
        self.payments: List[Payment] = []

    def add_person(self, name: str) -> str:
        new_person = Person(name)
        self.people[new_person.id] = new_person
        return new_person.id

    def add_payment(self, payment: Payment):
        self.payments.append(payment)

    def settle(self) -> Tuple[Dict[str, float], List[Tuple[str, str, float]]]:
        # reset
        for p in self.people.values():
            p.net_balance = 0.0
        # apply payments
        for pay in self.payments:
            pay.apply(self.people)
        net = {pid: round(p.net_balance, 2) for pid, p in self.people.items()}
        flows = Settlement.compute(self.people)
        return net, flows
