import sqlite3
import json

DB_NAME = "hackhub.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            organizer TEXT NOT NULL,
            date TEXT NOT NULL,
            mode TEXT NOT NULL,
            location TEXT NOT NULL,
            prize_pool TEXT NOT NULL,
            themes TEXT NOT NULL,          -- stored as JSON string, e.g. '["AI/ML","Web Dev"]'
            team_size_limit INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            registered_on TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS teammates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT,
            FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def seed_events():
    """Insert the original dummyData events, but only if the table is empty."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM events")
    if cur.fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    events = [
        (1, "CodeStorm 2026", "Zoho Corporation", "2026-08-15T09:00:00", "Offline",
         "Chennai", "₹1,00,000", ["AI/ML", "Web Development", "Open Innovation"], 4),
        (2, "HackNEC", "National Engineering College", "2026-08-02T10:00:00", "Offline",
         "Kovilpatti", "₹50,000", ["Sustainability", "EdTech"], 3),
        (3, "TCS CodeVita", "Tata Consultancy Services", "2026-09-05T00:00:00", "Online",
         "Virtual", "₹2,00,000", ["Competitive Programming"], 1),
        (4, "Smart India Hackathon", "Government of India", "2026-08-25T09:00:00", "Offline",
         "Bengaluru", "₹1,50,000", ["Smart Cities", "Healthcare", "Agriculture"], 6),
        (5, "HackVerse", "Amazon Web Services", "2026-09-20T09:00:00", "Online",
         "Virtual", "₹3,00,000", ["Cloud Computing", "Serverless", "DevOps"], 4),
        (6, "InnovateX", "Microsoft", "2026-08-30T09:00:00", "Offline",
         "Hyderabad", "₹1,75,000", ["AI/ML", "AR/VR", "Accessibility"], 5),
        (7, "FinTech Sprint", "HDFC Bank", "2026-09-10T09:30:00", "Offline",
         "Mumbai", "₹2,50,000", ["FinTech", "Blockchain", "Payments"], 4),
        (8, "GreenTech Hackathon", "Tamil Nadu Startup Mission", "2026-08-18T09:00:00", "Offline",
         "Coimbatore", "₹80,000", ["Climate Tech", "Renewable Energy", "Sustainability"], 3),
        (9, "Hack Synapse 2026", "MITS-DU, Gwalior", "2026-09-12T09:00:00", "Offline",
         "Gwalior, MP", "₹1,20,000", ["AI/ML", "Open Innovation"], 4),
        (10, "HackIndia Spark-12", "HackIndia", "2026-08-28T09:00:00", "Offline",
         "Jaipur, Rajasthan", "₹1,50,000", ["Web3", "AI", "FutureTech"], 4),
        (11, "AI, Web3 & FutureTech Hackathon", "HackIndia", "2026-09-18T09:30:00", "Offline",
         "Lucknow, UP", "₹2,00,000", ["AI", "Web3", "Blockchain"], 5),
        (12, "AI for Lawyers Hackathon", "HackIndia", "2026-09-25T10:00:00", "Online",
         "Virtual", "₹75,000", ["LegalTech", "AI"], 3),
    ]

    cur.executemany(
        """INSERT INTO events (id, name, organizer, date, mode, location, prize_pool, themes, team_size_limit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(e[0], e[1], e[2], e[3], e[4], e[5], e[6], json.dumps(e[7]), e[8]) for e in events]
    )

    conn.commit()
    conn.close()