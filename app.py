"""
╔══════════════════════════════════════════════════════════════╗
║          QUIZFORGE BACKEND  v2.0  (app.py)                  ║
║          Flask | Dynamic PYQ Questions | Live Scraper       ║
╚══════════════════════════════════════════════════════════════╝

HOW TO RUN:
  pip install flask requests beautifulsoup4
  python app.py
  → Open http://localhost:5000
  → Questions are fetched live via /api/scrape on first load
"""

from flask import Flask, jsonify, send_from_directory, request
from flask import Response
import os
import json
import threading
import time

# Import scraper functions directly
from scraper import fetch_opentdb, scrape_indiabix, deduplicate, OPENTDB_TASKS, INDIABIX_TASKS
import random

app = Flask(__name__, static_folder=".")

SCRAPED_FILE = os.path.join(os.path.dirname(__file__), "scraped_questions.json")

# Thread lock to prevent concurrent scrapes
_scrape_lock = threading.Lock()
_scraping    = False


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def load_scraped():
    """Load previously scraped questions from disk."""
    if os.path.exists(SCRAPED_FILE):
        try:
            with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️  Could not load scraped file: {e}")
    return []


def run_scrape():
    """Run the full scrape pipeline synchronously. Returns list of questions."""
    global _scraping
    questions = []

    print("\n🔄 Starting live scrape pipeline...")

    # Phase 1: OpenTDB
    for (cat_id, amount, difficulty, exam, subject) in OPENTDB_TASKS:
        qs = fetch_opentdb(cat_id, amount, difficulty, exam, subject)
        questions.extend(qs)
        time.sleep(0.6)

    # Phase 2: IndiaBix (best effort)
    for (url, subject, exam) in INDIABIX_TASKS:
        qs = scrape_indiabix(url, subject, exam, max_q=6)
        questions.extend(qs)
        time.sleep(1.0)

    # Dedup + shuffle + assign IDs
    questions = deduplicate(questions)
    random.shuffle(questions)
    for i, q in enumerate(questions):
        q["id"] = i + 1

    # Save to disk
    if questions:
        with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Scraped & saved {len(questions)} questions.")

    _scraping = False
    return questions


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """
    Returns all available questions.
    - If scraped_questions.json exists → return those
    - Otherwise → return empty (frontend will call /api/scrape)
    """
    questions = load_scraped()

    # Support optional exam filter
    exam_filter = request.args.get("exam", "ALL").upper()
    if exam_filter and exam_filter != "ALL":
        questions = [q for q in questions if q.get("exam", "").upper() == exam_filter]

    return jsonify({
        "status":   "success",
        "count":    len(questions),
        "questions": questions,
        "scraped":  len(questions) > 0
    })


@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    """
    Triggers a fresh scrape. Called by the frontend on first load
    or when the user clicks 'Refresh Questions'.
    Returns the scraped questions directly (synchronous for simplicity).
    """
    global _scraping

    if _scraping:
        return jsonify({"status": "pending", "message": "Scrape already in progress..."}), 202

    with _scrape_lock:
        _scraping = True

    try:
        questions = run_scrape()
        return jsonify({
            "status":    "success",
            "count":     len(questions),
            "questions": questions
        })
    except Exception as e:
        _scraping = False
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/exams", methods=["GET"])
def get_exams():
    """Returns distinct exam categories from scraped questions."""
    questions = load_scraped()
    exams = sorted(set(q.get("exam", "GK") for q in questions))
    return jsonify({"exams": ["ALL"] + exams})


@app.route("/api/status", methods=["GET"])
def status():
    """Returns current scrape status and question count."""
    questions = load_scraped()
    return jsonify({
        "scraping":       _scraping,
        "question_count": len(questions),
        "has_questions":  len(questions) > 0
    })


# ──────────────────────────────────────────────────────────────
# CORS (helpful for dev)
# ──────────────────────────────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 QuizForge v2.0 is live!")
    print("   → Frontend  : http://localhost:5000")
    print("   → API       : http://localhost:5000/api/questions")
    print("   → Scrape    : POST http://localhost:5000/api/scrape")
    print("   → Questions are fetched live — no preloaded data!\n")
    app.run(debug=True, port=5000)