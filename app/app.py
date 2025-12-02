from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BOOKINGS = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        slot = request.form.get("slot")

        print("DEBUG:", name, phone, slot)  # <---- REQUIRED

        BOOKINGS.append({
            "name": name,
            "phone": phone,
            "slot": slot,
            "status": "Booked"
        })

        return redirect(url_for("list_bookings"))

    return render_template("book.html")

@app.route("/bookings")
def list_bookings():
    return render_template("bookings.html", bookings=BOOKINGS)

@app.route("/admin")
def admin():
    return render_template("admin.html", bookings=BOOKINGS)

@app.route("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
