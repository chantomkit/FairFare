from typing import Dict, List, Tuple

from FairFare.core import Person


def greedy_settlement(
    people: Dict[str, Person]
) -> List[Tuple[str, str, float]]:
    """
    Computes the net balances and returns a minimum list of settlements transaction required.
    Each settlement is a tuple (debtor_id, creditor_id, amount).
    """
    total_balance = sum(p.net_balance for p in people.values())
    # Check if the total balance is zero
    if abs(total_balance) > 1e-9:
        raise ValueError(
            f"Invalid balances: total net balance is {total_balance}, must be zero"
        )

    # prepare lists
    positives = [
        (p.id, p.net_balance) for p in people.values() if p.net_balance > 0
    ]
    negatives = [
        (p.id, -p.net_balance) for p in people.values() if p.net_balance < 0
    ]
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
