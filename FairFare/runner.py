from typing import Dict, List

from FairFare.core import Payment, Person
from FairFare.settler import ExpenseManager


def get_participants() -> List[Person]:
    print(
        "\nEnter participant names separated by spaces \n"
        "(e.g. 'Alice Bob Charlie'):"
    )
    names = input().strip().split()
    if not names:
        raise ValueError("At least one participant is required")
    return [Person(name) for name in names]


def get_payment(
    participants: List[Person], id_map: Dict[str, str]
) -> Payment | None:
    print("\nEnter payment details (or type 'STOP' to finish):")
    print(
        "Who paid? (Enter names separated by spaces, \n"
        "followed by their contributions)"
    )
    print("Example: 'Alice 50 Bob 30' means Alice paid 50 and Bob paid 30")
    payer_input = input().strip()

    if payer_input.upper() == "STOP":
        return None

    # Parse payers and amounts
    payer_tokens = payer_input.split()
    if len(payer_tokens) % 2 != 0:
        raise ValueError("Each payer must have an amount")

    contributions: Dict[str, float] = {}
    for i in range(0, len(payer_tokens), 2):
        name, amount = payer_tokens[i], float(payer_tokens[i + 1])
        if name not in id_map:
            raise ValueError(f"Unknown participant: {name}")
        contributions[id_map[name]] = amount

    print("\nHow should it be split?")
    print("1. Even split among all")
    print("2. Even split among specific people")
    print("3. Exact amounts")
    print("4. Ratio split")
    split_choice = input().strip()

    shares: Dict[str, float] = {}
    split_method = "even"

    if split_choice == "1":
        # Even split among all - initialize with 0
        shares = {p.id: 0 for p in participants}

    elif split_choice == "2":
        print("Enter names of people to split between (space-separated):")
        split_names = input().strip().split()
        shares = {p.id: 0 for p in participants if p.name in split_names}

    elif split_choice == "3":
        split_method = "exact"
        print("Enter name and exact amount for each person:")
        print("Example: 'Alice 25 Bob 15 Charlie 10'")
        share_input = input().strip().split()
        for i in range(0, len(share_input), 2):
            name, amount = share_input[i], float(share_input[i + 1])
            if name not in id_map:
                raise ValueError(f"Unknown participant: {name}")
            shares[id_map[name]] = amount

    elif split_choice == "4":
        split_method = "ratio"
        print("Enter name and ratio for each person (ratios should sum to 1):")
        print("Example: 'Alice 0.5 Bob 0.3 Charlie 0.2'")
        ratio_input = input().strip().split()
        for i in range(0, len(ratio_input), 2):
            name, ratio = ratio_input[i], float(ratio_input[i + 1])
            if name not in id_map:
                raise ValueError(f"Unknown participant: {name}")
            shares[id_map[name]] = ratio

    else:
        raise ValueError("Invalid split choice")

    return Payment(
        participant_contributions=contributions,
        participant_shares=shares,
        split_method=split_method,
    )


def main():
    try:
        # Get participants
        participants = get_participants()
        id_map = {p.name: p.id for p in participants}
        name_map = {p.id: p.name for p in participants}

        # Get payments
        payments: List[Payment] = []
        while True:
            try:
                payment = get_payment(participants, id_map)
                if payment is None:
                    break
                payments.append(payment)
            except (ValueError, KeyError) as e:
                print(f"Error: {e}")
                print("Please try this payment entry again.")
                continue

        if not payments:
            print("\nNo payments recorded.")
            return

        # Process settlements
        em = ExpenseManager(participants, payments)
        net_balances = em.get_net_balances()
        transactions = em.settle()

        # Print results
        print("\n=== Participants ===")
        for p in participants:
            print(f"{p.name}: {p.id}")

        print("\n=== Payments Inputted ===")
        for pay in payments:
            print(pay)

        print("\n=== Net Balances ===")
        for pid, balance in net_balances.items():
            name = name_map[pid]
            print(f"{name}: {'%.2f' % balance}")

        print("\n=== Settlement Transactions ===")
        if not transactions:
            print("No settlements needed!")
        for tx in transactions:
            from_name = name_map[tx["from"]]
            to_name = name_map[tx["to"]]
            amount = tx["amount"]
            print(f"{from_name} pays {to_name}: {'%.2f' % amount}")

    except (ValueError, KeyError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
