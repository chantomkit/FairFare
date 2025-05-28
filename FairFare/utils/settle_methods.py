from typing import Dict, List, Union


def greedy_settlement(
    balances: Dict[str, float]
) -> List[Dict[str, Union[str, float]]]:
    """
    Compute minimum list of settlements transaction using greedy algorithm.
    Each settlement is a dict with keys "from", "to", and "amount".
    """
    total_balance = sum(bal for bal in balances.values())
    # Check if the total balance is zero
    if abs(total_balance) > 1e-9:
        raise ValueError(
            f"Invalid balances: total net balance is {total_balance}, \
                must be zero"
        )

    # prepare lists
    positives = [(id, bal) for id, bal in balances.items() if bal > 0]
    negatives = [(id, -bal) for id, bal in balances.items() if bal < 0]
    positives.sort(key=lambda x: x[1])
    negatives.sort(key=lambda x: x[1])

    i, j = 0, 0
    settlements: List[Dict[str, Union[str, float]]] = []
    while i < len(negatives) and j < len(positives):
        debtor_id, debt = negatives[i]
        creditor_id, credit = positives[j]
        amount = min(debt, credit)
        settlements.append(
            {"from": debtor_id, "to": creditor_id, "amount": round(amount, 2)}
        )
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
