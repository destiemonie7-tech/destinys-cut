from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Change this before putting the site online.
app.secret_key = os.environ.get("SECRET_KEY", "destinys-cut-local-secret")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "DESTINY2026")

BOOKINGS_FILE = "bookings.json"


# ================= BOOKING STORAGE =================

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []

    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(bookings, file, indent=4)


# ================= ADMIN PROTECTION =================

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return function(*args, **kwargs)

    return wrapper


# ================= HOME =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= ADMIN LOGIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Incorrect password."
        )

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# ================= ADMIN DASHBOARD =================

@app.route("/admin")
@admin_required
def admin():

    bookings = load_bookings()

    bookings = list(reversed(bookings))

    total = len(bookings)

    confirmed = sum(
        1 for booking in bookings
        if booking.get("status") == "Confirmed"
    )

    pending = sum(
        1 for booking in bookings
        if booking.get("status") == "Pending"
    )

    cancelled = sum(
        1 for booking in bookings
        if booking.get("status") == "Cancelled"
    )

    return render_template(
        "admin.html",
        bookings=bookings,
        total=total,
        confirmed=confirmed,
        pending=pending,
        cancelled=cancelled
    )


# ================= CREATE BOOKING =================

@app.route("/book", methods=["POST"])
def book():

    data = request.get_json() or {}

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    service = data.get("service", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    request_note = data.get("request", "").strip()

    if not name or not phone or not service or not date or not time:

        return jsonify({
            "success": False,
            "message": "Please complete all required fields."
        }), 400

    booking = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "name": name,
        "phone": phone,
        "service": service,
        "date": date,
        "time": time,
        "request": request_note,
        "status": "Pending",
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    bookings = load_bookings()

    bookings.append(booking)

    save_bookings(bookings)

    print("\n" + "=" * 50)
    print("DESTINY'S CUT - NEW APPOINTMENT")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Phone: {phone}")
    print(f"Service: {service}")
    print(f"Date: {date}")
    print(f"Time: {time}")
    print(f"Special Request: {request_note}")
    print("Status: Pending")
    print("=" * 50 + "\n")

    return jsonify({
        "success": True,
        "message": "Appointment request received!",
        "name": name,
        "service": service,
        "date": date,
        "time": time
    })


# ================= UPDATE BOOKING STATUS =================

@app.route("/admin/booking/<booking_id>/status", methods=["POST"])
@admin_required
def update_status(booking_id):

    data = request.get_json() or {}

    new_status = data.get("status", "")

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message": "Invalid booking status."
        }), 400

    bookings = load_bookings()

    found = False

    for booking in bookings:

        if booking.get("id") == booking_id:

            booking["status"] = new_status
            found = True
            break

    if not found:

        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    save_bookings(bookings)

    return jsonify({
        "success": True,
        "status": new_status
    })


# ================= DELETE BOOKING =================

@app.route("/admin/booking/<booking_id>/delete", methods=["POST"])
@admin_required
def delete_booking(booking_id):

    bookings = load_bookings()

    updated_bookings = [
        booking
        for booking in bookings
        if booking.get("id") != booking_id
    ]

    if len(updated_bookings) == len(bookings):

        return jsonify({
            "success": False,
            "message": "Booking not found."
        }), 404

    save_bookings(updated_bookings)

    return jsonify({
        "success": True
    })


# ================= START SERVER =================

if __name__ == "__main__":

    print("-" * 50)
    print("DESTINY'S CUT")
    print("Premium Barbing Salon")
    print("Booking system is running")
    print("-" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )