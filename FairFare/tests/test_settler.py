import pytest

from FairFare.core import Payment
from FairFare.settler import ExpenseManager


# Helper to get name-id mapping from names
@pytest.fixture
def expense_manager():
    names = ["Alice", "Bob", "Charlie"]
    em = ExpenseManager(names)
    return em, {p.name: p.id for p in em.people.values()}


def test_settlement_scenario(expense_manager: tuple[ExpenseManager, dict]):
    em, ids = expense_manager

    # 1) Simple equal split: Alice pays 90 among all
    p1 = Payment(
        {ids["Alice"]: 90}, {ids["Alice"]: 0, ids["Bob"]: 0, ids["Charlie"]: 0}
    )
    em.add_payment(p1)

    # 2) Mixed contributions: Bob 60, Charlie 30 splitting equally among all
    p2 = Payment(
        {ids["Bob"]: 60, ids["Charlie"]: 30},
        {ids["Alice"]: 0, ids["Bob"]: 0, ids["Charlie"]: 0},
    )
    em.add_payment(p2)

    # 3) Exact split: Alice pays 100, exact shares
    p3 = Payment(
        {ids["Alice"]: 100},
        {ids["Alice"]: 50, ids["Bob"]: 30, ids["Charlie"]: 20},
        split_method="exact",
    )
    em.add_payment(p3)

    # 4) Subset split: Bob pays 75 split only between Bob and Charlie
    p4 = Payment({ids["Bob"]: 75}, {ids["Bob"]: 0, ids["Charlie"]: 0})
    em.add_payment(p4)

    # 5) Complex multi-payer, multi-participant (ratio split)
    p5 = Payment(
        {ids["Alice"]: 40, ids["Bob"]: 20, ids["Charlie"]: 40},
        {ids["Alice"]: 0.25, ids["Bob"]: 0.25, ids["Charlie"]: 0.5},
        split_method="ratio",
    )
    em.add_payment(p5)

    # Run settlement
    em.balance_expenses()
    net_balances = em.get_net_balances()
    transactions = em.settle()
    print("Net Balances:", net_balances)
    print("Transactions:", transactions)

    # Check net balances are consistent (they should sum to 0.0)
    total_balance = round(sum(net_balances.values()), 2)
    assert (
        total_balance == 0.0
    ), f"Net balance does not sum to zero: {total_balance}"

    # Expected net balances
    expected_net = {"Alice": 95.0, "Bob": 2.5, "Charlie": -97.5}
    for name, expected in expected_net.items():
        actual = round(net_balances[ids[name]], 2)
        assert actual == expected, f"{name}: expected {expected}, got {actual}"

    # Expected settlement transactions
    expected_transactions = [
        ("Charlie", "Bob", 2.5),
        ("Charlie", "Alice", 95.0),
    ]
    assert len(transactions) == len(expected_transactions)

    # Match transactions using name mapping
    actual_named = [
        (
            next(k for k, v in ids.items() if v == debtor),
            next(k for k, v in ids.items() if v == creditor),
            amount,
        )
        for debtor, creditor, amount in transactions
    ]

    for expected_tx in expected_transactions:
        assert (
            expected_tx in actual_named
        ), f"Expected transaction {expected_tx} not found in {actual_named}"
