from flask import Flask, jsonify, render_template, request

from FairFare.core import Payment, Person
from FairFare.settler import ExpenseManager

app = Flask(__name__)

# Store session data (in a real app, use a proper database)
sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/initialize", methods=["POST"])
def initialize():
    data = request.json
    names = data.get("names", [])

    if not names:
        return jsonify({"error": "At least one participant is required"}), 400

    # Create participants
    participants = [Person(name) for name in names]
    id_map = {p.name: p.id for p in participants}
    name_map = {p.id: p.name for p in participants}

    # Store in session
    session_id = request.cookies.get("session_id", "default")
    sessions[session_id] = {
        "participants": participants,
        "id_map": id_map,
        "name_map": name_map,
        "payments": [],
    }

    return jsonify(
        {"participants": [{"name": p.name, "id": p.id} for p in participants]}
    )


@app.route("/api/add_payment", methods=["POST"])
def add_payment():
    try:
        session_id = request.cookies.get("session_id", "default")
        if session_id not in sessions:
            return jsonify({"error": "No active session"}), 400

        session = sessions[session_id]
        data = request.get_json()

        id_map = session["id_map"]
        name_map = session["name_map"]

        contributions = {
            id_map[payer]: float(data["amounts"][i])
            for i, payer in enumerate(data["payers"])
        }

        shares = {
            id_map[sharee]: float(data["share_amounts"][i])
            for i, sharee in enumerate(data["shares"])
        }

        payment = Payment(
            participant_contributions=contributions,
            input_participant_shares=shares,
            split_method=data["split_method"],
            description=data["description"],
        )

        # If editing existing payment, remove it first
        if "id" in data and data["id"]:
            session["payments"] = [
                p for p in session["payments"] if p.id != data["id"]
            ]

        # Add new payment
        session["payments"].append(payment)

        # Return the payment with names instead of IDs
        formatted_payment = {
            "id": payment.id,
            "description": payment.description,
            "participant_contributions": {
                name_map[pid]: float(amount)
                for pid, amount in payment.participant_contributions.items()
            },
            "input_participant_shares": {
                name_map[pid]: float(amount)
                for pid, amount in payment.input_participant_shares.items()
            },
            "split_participant_shares": {
                name_map[pid]: float(amount)
                for pid, amount in payment.split_participant_shares.items()
            },
            "split_method": payment.split_method,
        }

        return jsonify(
            {
                "message": "Payment added successfully",
                "payment": formatted_payment,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/settle", methods=["GET"])
def settle():
    session_id = request.cookies.get("session_id", "default")
    if session_id not in sessions:
        return jsonify({"error": "Session not initialized"}), 400

    session = sessions[session_id]

    try:
        # Create expense manager and get settlements
        em = ExpenseManager(session["participants"], session["payments"])
        net_balances = em.get_net_balances()
        transactions = em.settle()

        # Convert to name-based format for frontend
        named_balances = {
            session["name_map"][pid]: round(balance, 2)
            for pid, balance in net_balances.items()
        }

        named_transactions = [
            {
                "from": session["name_map"][tx["from"]],
                "to": session["name_map"][tx["to"]],
                "amount": round(tx["amount"], 2),
            }
            for tx in transactions
        ]

        return jsonify(
            {
                "net_balances": named_balances,
                "transactions": named_transactions,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/payments", methods=["GET"])
def get_payments():
    try:
        session_id = request.cookies.get("session_id", "default")
        if session_id not in sessions:
            return jsonify({"error": "No active session"}), 400

        session = sessions[session_id]
        name_map = session["name_map"]
        payments = session["payments"]

        # Convert payments to a frontend-friendly format
        formatted_payments = []
        for payment in payments:
            contributions = {
                name_map[pid]: float(amount)
                for pid, amount in payment.participant_contributions.items()
            }
            shares = {
                name_map[pid]: float(amount)
                for pid, amount in payment.input_participant_shares.items()
            }
            split_shares = {
                name_map[pid]: float(amount)
                for pid, amount in payment.split_participant_shares.items()
            }

            formatted_payments.append(
                {
                    "id": payment.id,
                    "description": payment.description,
                    "participant_contributions": contributions,
                    "input_participant_shares": shares,
                    "split_participant_shares": split_shares,
                    "split_method": payment.split_method,
                }
            )

        return jsonify(formatted_payments)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/payments/<payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    try:
        session_id = request.cookies.get("session_id", "default")
        if session_id not in sessions:
            return jsonify({"error": "No active session"}), 400

        session = sessions[session_id]

        # Remove the payment with the given ID
        session["payments"] = [
            p for p in session["payments"] if p.id != payment_id
        ]

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
