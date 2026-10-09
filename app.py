from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from database import get_connection, init_db, seed_events
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
CORS(app)  # allows the Vite dev server (different port) to call this API

init_db()
seed_events()


def event_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "organizer": row["organizer"],
        "date": row["date"],
        "mode": row["mode"],
        "location": row["location"],
        "prizePool": row["prize_pool"],
        "themes": json.loads(row["themes"]),
        "teamSizeLimit": row["team_size_limit"],
    }


@app.route("/api/events", methods=["GET"])
def get_events():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM events ORDER BY date").fetchall()
    conn.close()
    return jsonify([event_to_dict(r) for r in rows])


@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(event_to_dict(row))


@app.route("/api/registrations", methods=["GET"])
def get_registrations():
    conn = get_connection()
    regs = conn.execute("""
        SELECT r.id, r.event_id, r.team_name, r.registered_on, e.name AS event_name
        FROM registrations r
        JOIN events e ON e.id = r.event_id
        ORDER BY r.id DESC
    """).fetchall()

    result = []
    for r in regs:
        teammates = conn.execute(
            "SELECT name, email, role FROM teammates WHERE registration_id = ?",
            (r["id"],)
        ).fetchall()
        result.append({
            "id": r["id"],
            "eventId": r["event_id"],
            "eventName": r["event_name"],
            "teamName": r["team_name"],
            "registeredOn": r["registered_on"],
            "teammates": [dict(t) for t in teammates],
        })

    conn.close()
    return jsonify(result)


@app.route("/api/registrations", methods=["POST"])
def create_registration():
    data = request.get_json()
    event_id = data.get("eventId")
    team_name = data.get("teamName", "").strip()
    teammates = data.get("teammates", [])

    if not event_id or not team_name:
        return jsonify({"error": "eventId and teamName are required"}), 400

    conn = get_connection()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    registered_on = datetime.now().strftime("%d/%m/%Y")

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO registrations (event_id, team_name, registered_on) VALUES (?, ?, ?)",
        (event_id, team_name, registered_on)
    )
    registration_id = cur.lastrowid

    for mate in teammates:
        if mate.get("name", "").strip():
            cur.execute(
                "INSERT INTO teammates (registration_id, name, email, role) VALUES (?, ?, ?, ?)",
                (registration_id, mate["name"].strip(), mate.get("email", ""), mate.get("role", ""))
            )

    conn.commit()
    conn.close()

    return jsonify({
        "id": registration_id,
        "eventId": event_id,
        "eventName": event["name"],
        "teamName": team_name,
        "registeredOn": registered_on,
        "teammates": teammates,
    }), 201


@app.route("/api/registrations/<int:registration_id>", methods=["DELETE"])
def delete_registration(registration_id):
    conn = get_connection()
    conn.execute("DELETE FROM teammates WHERE registration_id = ?", (registration_id,))
    cur = conn.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Registration not found"}), 404
    return jsonify({"message": "Cancelled"}), 200

@app.route("/")
def home():
    return jsonify({"message": "HackHub API is running", "try": ["/api/events", "/api/registrations", "/admin"]})


ADMIN_HTML = """
<!doctype html>
<html><head><title>HackHub Database</title>
<style>
  body{font-family:Arial;margin:30px;background:#fffdf7}
  h1{color:#0f766e}
  table{border-collapse:collapse;width:100%;margin-bottom:10px}
  th,td{border:1px solid #ccc;padding:8px;text-align:left;font-size:14px}
  th{background:#0f766e;color:#fff}
</style></head><body>
<h1>HackHub Database (hackhub.db)</h1>
{% for title, rows in tables %}
  <h2>{{ title }} ({{ rows|length }} rows)</h2>
  {% if rows %}
  <table>
    <tr>{% for k in rows[0].keys() %}<th>{{ k }}</th>{% endfor %}</tr>
    {% for r in rows %}
    <tr>{% for k in r.keys() %}<td>{{ r[k] }}</td>{% endfor %}</tr>
    {% endfor %}
  </table>
  {% else %}<p>No rows yet.</p>{% endif %}
{% endfor %}
</body></html>
"""


@app.route("/admin")
def admin():
    conn = get_connection()
    events = conn.execute(
        "SELECT id, name, organizer, date, mode, location, prize_pool, team_size_limit FROM events"
    ).fetchall()
    regs = conn.execute("""
        SELECT r.id, e.name AS event, r.team_name, r.registered_on
        FROM registrations r JOIN events e ON e.id = r.event_id
        ORDER BY r.id DESC
    """).fetchall()
    mates = conn.execute("""
        SELECT t.id, t.registration_id, r.team_name, t.name, t.email, t.role
        FROM teammates t JOIN registrations r ON r.id = t.registration_id
        ORDER BY t.id DESC
    """).fetchall()
    conn.close()
    return render_template_string(
        ADMIN_HTML,
        tables=[("events", events), ("registrations", regs), ("teammates", mates)],
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)