import json
from pathlib import Path

import pytest

from FairFare.core import Payment, Person
from FairFare.settler import ExpenseManager

TEST_CASES = ["test_case_1", "test_case_2"]


def load_test_data(path: str):
    # Get the absolute path to test_case_1 directory
    base_dir = Path(__file__).parent.parent
    test_case_dir = base_dir / "data" / path

    # Read names from names.txt
    names_file = test_case_dir / "names.txt"
    participant_list = []
    with open(names_file, "r") as f:
        for line in f:
            name, uuid = line.strip().split(", ")
            participant_list.append(Person(name, uuid))

    # Read payments from payments.json
    payments_file = test_case_dir / "payments.json"
    with open(payments_file, "r") as f:
        payments_data = json.load(f)
    payment_list = [Payment(**payment_data) for payment_data in payments_data]

    # Read expected net balances
    expected_net_file = test_case_dir / "expected_net.json"
    with open(expected_net_file, "r") as f:
        expected_net = json.load(f)

    # Read expected transactions
    expected_transactions_file = test_case_dir / "expected_transactions.json"
    with open(expected_transactions_file, "r") as f:
        expected_transactions = json.load(f)

    return participant_list, payment_list, expected_net, expected_transactions


@pytest.mark.parametrize("path", TEST_CASES)
def test_settlement_scenario(path: str):
    (
        participant_list,
        payment_list,
        expected_net,
        expected_transactions,
    ) = load_test_data(path)

    # Initialize ExpenseManager with names from file
    em = ExpenseManager(participant_list, payment_list)

    # Run settlement
    net_balances = em.get_net_balances()
    transactions = em.settle()
    print("Net Balances:", net_balances)
    print("Transactions:", transactions)

    # Check net balances are consistent (they should sum to 0.0)
    total_balance = round(sum(net_balances.values()), 2)
    assert (
        total_balance == 0.0
    ), f"Net balance does not sum to zero: {total_balance}"

    # Check net balances match expected values
    for uuid, expected in expected_net.items():
        actual = round(net_balances[uuid], 2)
        assert actual == expected, f"{uuid}: expected {expected}, got {actual}"

    # Check settlement transactions match expected
    assert len(transactions) == len(expected_transactions)

    # Sort both lists to ensure consistent comparison
    sorted_transactions = sorted(
        transactions, key=lambda x: (x["from"], x["to"], x["amount"])
    )
    sorted_expected = sorted(
        expected_transactions, key=lambda x: (x["from"], x["to"], x["amount"])
    )

    for actual, expected in zip(sorted_transactions, sorted_expected):
        assert (
            actual == expected
        ), f"Transaction mismatch: expected {expected}, got {actual}"
