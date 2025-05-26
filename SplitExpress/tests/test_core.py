import pytest
from SplitExpress.core import ExpenseManager, Payment

# Helper to get name-id mapping from names
@pytest.fixture
def expense_manager():
    em = ExpenseManager()
    alice = em.add_person("Alice")
    bob = em.add_person("Bob")
    charlie = em.add_person("Charlie")
    return em, {"Alice": alice, "Bob": bob, "Charlie": charlie}


def test_split_scenario(expense_manager):
    em, ids = expense_manager

    # 1) Simple equal split: Alice pays 90 among all
    p1 = Payment({ids["Alice"]: 90}, {ids["Alice"]: 0, ids["Bob"]: 0, ids["Charlie"]: 0})
    em.add_payment(p1)

    # 2) Mixed contributions: Bob 60, Charlie 30 splitting equally among all
    p2 = Payment({ids["Bob"]: 60, ids["Charlie"]: 30}, {ids["Alice"]: 0, ids["Bob"]: 0, ids["Charlie"]: 0})
    em.add_payment(p2)

    # 3) Exact split: Alice pays 100, exact shares
    p3 = Payment({ids["Alice"]: 100}, {
        ids["Alice"]: 50, ids["Bob"]: 30, ids["Charlie"]: 20
    }, strategy='exact')
    em.add_payment(p3)

    # 4) Subset split: Bob pays 75 split only between Bob and Charlie
    p4 = Payment({ids["Bob"]: 75}, {ids["Bob"]: 0, ids["Charlie"]: 0})
    em.add_payment(p4)

    # 5) Complex multi-payer, multi-participant (ratio split)
    p5 = Payment(
        {ids["Alice"]: 40, ids["Bob"]: 20, ids["Charlie"]: 40},
        {ids["Alice"]: 0.25, ids["Bob"]: 0.25, ids["Charlie"]: 0.5},
        strategy="ratio"
    )
    em.add_payment(p5)

    # Run settlement
    net_balances, transactions = em.settle()

    # Check net balances are consistent (they should sum to 0.0)
    total_balance = round(sum(net_balances.values()), 2)
    assert total_balance == 0.0, f"Net balance does not sum to zero: {total_balance}"

    # Expected net balances
    expected_net = {
        "Alice": 95.0,
        "Bob": 2.5,
        "Charlie": -97.5
    }
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
    actual_named = [(
        next(k for k, v in ids.items() if v == debtor),
        next(k for k, v in ids.items() if v == creditor),
        amount
    ) for debtor, creditor, amount in transactions]

    for expected_tx in expected_transactions:
        assert expected_tx in actual_named, f"Expected transaction {expected_tx} not found in {actual_named}"
