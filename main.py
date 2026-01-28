from flask import Flask, render_template, request
import os
import json
import re
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "parcel_data.json"


def validate(form):
    errors = {}

    def required_min(field, name, min_len):
        value = form.get(field, "").strip()
        if len(value) < min_len:
            errors[field] = f"{name} musí mít alespoň {min_len} znaky."
        return value

    sender_name = required_min("sender_name", "Jméno odesílatele", 2)
    sender_address = required_min("sender_address", "Adresa odesílatele", 5)
    sender_zip = form.get("sender_zip", "")

    recipient_name = required_min("recipient_name", "Jméno příjemce", 2)
    recipient_address = required_min("recipient_address", "Adresa příjemce", 5)
    recipient_zip = form.get("recipient_zip", "")

    if not re.fullmatch(r"\d{5}", sender_zip):
        errors["sender_zip"] = "PSČ odesílatele musí mít přesně 5 číslic."

    if not re.fullmatch(r"\d{5}", recipient_zip):
        errors["recipient_zip"] = "PSČ příjemce musí mít přesně 5 číslic."

    try:
        weight = float(form.get("weight", 0))
        if weight <= 0:
            raise ValueError
    except ValueError:
        errors["weight"] = "Hmotnost musí být kladné číslo."

    shipment_type = form.get("shipment_type")
    if shipment_type not in ["balik", "dopis", "cenny"]:
        errors["shipment_type"] = "Neplatný typ zásilky."

    note = form.get("note", "")
    if len(note) > 200:
        errors["note"] = "Poznámka může mít maximálně 200 znaků."

    return errors


@app.route("/", methods=["GET", "POST"])
def index():
    errors = {}

    if request.method == "POST":
        errors = validate(request.form)

        if not errors:
            data = {
                "sender_name": request.form["sender_name"],
                "sender_address": request.form["sender_address"],
                "sender_zip": request.form["sender_zip"],
                "recipient_name": request.form["recipient_name"],
                "recipient_address": request.form["recipient_address"],
                "recipient_zip": request.form["recipient_zip"],
                "weight": float(request.form["weight"]),
                "shipment_type": request.form["shipment_type"],
                "insurance": "insurance" in request.form,
                "note": request.form.get("note", ""),
                "created_at": datetime.now().isoformat()
            }

            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    shipments = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                shipments = []

            shipments.append(data)

            with open("parcel_data".json, "w", encoding="utf-8") as f:
                json.dump(shipments, f, ensure_ascii=False, indent=2)

            return render_template("success.html")

    return render_template("form.html", errors=errors, form=request.form)


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)
