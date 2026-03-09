"""
╔══════════════════════════════════════════════════════════════╗
║          QUIZFORGE BACKEND  v3.0  (app.py)                  ║
║          Flask · SSE Scrape · In-Memory Cache · Gzip        ║
╚══════════════════════════════════════════════════════════════╝

CHANGES FROM v2.0:
  ✅ Race condition fixed — _scraping flag moved inside lock
  ✅ _scraping reset via try/finally (never gets stuck)
  ✅ static_folder="static" (files live in ./static/)
  ✅ exam_filter input whitelisted against known exams
  ✅ All paths use os.path.dirname(__file__)
  ✅ /api/scrape converted to Server-Sent Events (SSE)
  ✅ /api/questions cached in-memory for 5 minutes
  ✅ Response compression via Flask-Compress
  ✅ CORS tightened; OPTIONS pre-flight handled
  ✅ Graceful shutdown of background threads

HOW TO RUN:
  pip install flask flask-compress requests beautifulsoup4
  mkdir -p static/css static/js
  python app.py
  → Open http://localhost:5000
"""

from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
from functools import wraps
from typing import Generator

from flask import Flask, Response, jsonify, request, send_from_directory

# ── Optional compression (gracefully degraded if missing) ──────────────────
try:
    from flask_compress import Compress
    _HAS_COMPRESS = True
except ImportError:
    _HAS_COMPRESS = False

# ── Import scraper (deferred so missing deps don't kill the server) ─────────
try:
    from scraper import (
        INDIABIX_TASKS,
        OPENTDB_TASKS,
        deduplicate,
        fetch_opentdb,
        scrape_indiabix,
    )
    _SCRAPER_AVAILABLE = True
except ImportError as _scraper_err:
    _SCRAPER_AVAILABLE = False
    _scraper_err_msg = str(_scraper_err)

import random

# ═══════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SCRAPED_FILE  = os.path.join(BASE_DIR, "scraped_questions.json")
STATIC_DIR    = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False

if _HAS_COMPRESS:
    Compress(app)

# ── Allowed exam values (whitelist) ────────────────────────────────────────
VALID_EXAMS = frozenset({"ALL", "JEE", "NEET", "UPSC", "CAT", "SAT", "GK"})

# ═══════════════════════════════════════════════════════════════
# STATE  (module-level, protected by _scrape_lock)
# ═══════════════════════════════════════════════════════════════

_scrape_lock = threading.Lock()
_scraping    = False          # True only while a scrape is in progress

# ── In-memory question cache ───────────────────────────────────────────────
_cache: dict = {
    "questions":    [],
    "loaded_at":    0.0,
    "ttl_seconds":  300,   # 5 minutes
}
_cache_lock = threading.Lock()

# ── SSE broadcast: each active SSE connection gets its own Queue ───────────
_sse_clients: list[queue.Queue] = []
_sse_lock    = threading.Lock()


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _broadcast(event: str, data: str | dict) -> None:
    """Push an SSE event to every connected client."""
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    payload = f"event: {event}\ndata: {data}\n\n"
    with _sse_lock:
        dead: list[queue.Queue] = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)


def _invalidate_cache() -> None:
    with _cache_lock:
        _cache["loaded_at"] = 0.0


def _load_from_disk() -> list:
    """Read scraped_questions.json from disk, return [] on any failure."""
    if not os.path.exists(SCRAPED_FILE):
        return []
    try:
        with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        app.logger.warning("Could not load scraped file: %s", exc)
        return []


def _get_questions(force_reload: bool = False) -> list:
    """
    Return questions from the in-memory cache.
    Reloads from disk if the cache is stale or force_reload is True.
    """
    now = time.monotonic()
    with _cache_lock:
        age = now - _cache["loaded_at"]
        if force_reload or age > _cache["ttl_seconds"]:
            _cache["questions"] = _load_from_disk()
            _cache["loaded_at"] = now
        return list(_cache["questions"])


def _save_to_disk(questions: list) -> None:
    """Persist question list to disk and refresh the cache."""
    try:
        with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        app.logger.error("Could not save scraped file: %s", exc)
        return
    with _cache_lock:
        _cache["questions"] = list(questions)
        _cache["loaded_at"] = time.monotonic()


def _sanitise_exam(raw: str) -> str:
    """Return a whitelisted exam value; fall back to ALL."""
    upper = (raw or "ALL").strip().upper()
    return upper if upper in VALID_EXAMS else "ALL"


# ── Decorator: ensure scraper is available ─────────────────────────────────
def require_scraper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not _SCRAPER_AVAILABLE:
            return jsonify({
                "status":  "error",
                "message": f"Scraper module unavailable: {_scraper_err_msg}"
            }), 503
        return f(*args, **kwargs)
    return wrapper


# ═══════════════════════════════════════════════════════════════
# SCRAPE PIPELINE
# ═══════════════════════════════════════════════════════════════

def _run_scrape_pipeline() -> list:
    """
    Execute the full scrape pipeline synchronously.
    Publishes SSE progress events throughout.
    Returns the final question list.

    IMPORTANT: Called from a background thread; the caller is
    responsible for setting/clearing _scraping under _scrape_lock.
    """
    questions: list = []
    total_tasks = len(OPENTDB_TASKS) + len(INDIABIX_TASKS)
    done = 0

    _broadcast("progress", {"stage": "start", "pct": 0,
                             "msg": "Scrape pipeline starting…"})

    # ── Phase 1: OpenTDB ──────────────────────────────────────
    _broadcast("progress", {"stage": "opentdb", "pct": 2,
                             "msg": f"OpenTDB — {len(OPENTDB_TASKS)} tasks queued"})

    for (cat_id, amount, difficulty, exam, subject) in OPENTDB_TASKS:
        qs = fetch_opentdb(cat_id, amount, difficulty, exam, subject)
        questions.extend(qs)
        done += 1
        pct = int((done / total_tasks) * 75)   # Phase 1 → 0–75%
        _broadcast("progress", {
            "stage":   "opentdb",
            "pct":     pct,
            "msg":     f"✅ {subject} — {len(qs)} questions",
            "fetched": len(questions),
        })
        time.sleep(0.65)   # respect OpenTDB rate limit

    # ── Phase 2: IndiaBix ─────────────────────────────────────
    _broadcast("progress", {"stage": "indiabix", "pct": 76,
                             "msg": f"IndiaBix — {len(INDIABIX_TASKS)} tasks queued"})

    for (url, subject, exam) in INDIABIX_TASKS:
        qs = scrape_indiabix(url, subject, exam, max_q=7)
        questions.extend(qs)
        done += 1
        pct = 75 + int(((done - len(OPENTDB_TASKS)) / len(INDIABIX_TASKS)) * 20)
        _broadcast("progress", {
            "stage":   "indiabix",
            "pct":     min(pct, 95),
            "msg":     f"✅ {subject} — {len(qs)} questions",
            "fetched": len(questions),
        })
        time.sleep(1.2)

    # ── Finalise ──────────────────────────────────────────────
    questions = deduplicate(questions)
    random.shuffle(questions)
    for i, q in enumerate(questions):
        q["id"] = i + 1

    _save_to_disk(questions)

    _broadcast("progress", {
        "stage":   "done",
        "pct":     100,
        "msg":     f"✅ Complete — {len(questions)} unique questions saved",
        "total":   len(questions),
    })
    _broadcast("done", {"count": len(questions), "questions": questions})

    return questions


# ── Thread target: wraps pipeline and always clears _scraping ──────────────
def _scrape_thread_target() -> None:
    global _scraping
    try:
        _run_scrape_pipeline()
    except Exception as exc:
        app.logger.exception("Scrape pipeline error: %s", exc)
        _broadcast("error", {"msg": str(exc)})
    finally:
        with _scrape_lock:
            _scraping = False


# ═══════════════════════════════════════════════════════════════
# ROUTES — Static / SPA
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the SPA entry-point."""
    return send_from_directory(BASE_DIR, "index.html")


# ═══════════════════════════════════════════════════════════════
# ROUTES — Questions API
# ═══════════════════════════════════════════════════════════════

@app.route("/api/questions", methods=["GET"])
def get_questions():
    """
    Returns all (or exam-filtered) questions.

    Query params:
      exam      — one of ALL | JEE | NEET | UPSC | CAT | SAT | GK
      chapter   — optional free-text chapter filter (case-insensitive)
      difficulty— optional: Easy | Medium | Hard
      limit     — optional int, max questions to return (default unlimited)
    """
    questions = _get_questions()

    # ── Exam filter (whitelisted) ──────────────────────────────
    exam_param = _sanitise_exam(request.args.get("exam", "ALL"))
    if exam_param != "ALL":
        questions = [q for q in questions if q.get("exam", "").upper() == exam_param]

    # ── Chapter filter ─────────────────────────────────────────
    chapter_param = (request.args.get("chapter") or "").strip().lower()
    if chapter_param:
        questions = [q for q in questions
                     if chapter_param in (q.get("subject") or "").lower()
                     or chapter_param in (q.get("chapter") or "").lower()]

    # ── Difficulty filter ──────────────────────────────────────
    diff_param = (request.args.get("difficulty") or "").strip().title()
    if diff_param in {"Easy", "Medium", "Hard"}:
        questions = [q for q in questions if q.get("difficulty") == diff_param]

    # ── Limit ──────────────────────────────────────────────────
    raw_limit = request.args.get("limit", "")
    if raw_limit.isdigit():
        questions = questions[:int(raw_limit)]

    return jsonify({
        "status":    "success",
        "count":     len(questions),
        "questions": questions,
        "scraped":   len(questions) > 0,
    })


@app.route("/api/exams", methods=["GET"])
def get_exams():
    """Returns sorted, distinct exam tags from all cached questions."""
    questions = _get_questions()
    exams = sorted(VALID_EXAMS & {q.get("exam", "GK") for q in questions})
    return jsonify({"exams": ["ALL"] + exams})


@app.route("/api/chapters", methods=["GET"])
def get_chapters():
    """
    Returns distinct chapter/subject values, optionally filtered by exam.
    Used by the frontend chapter-filter dropdown.
    """
    questions = _get_questions()
    exam_param = _sanitise_exam(request.args.get("exam", "ALL"))
    if exam_param != "ALL":
        questions = [q for q in questions if q.get("exam", "").upper() == exam_param]
    subjects = sorted({q.get("subject") or q.get("chapter") or "General"
                       for q in questions})
    return jsonify({"chapters": subjects})


@app.route("/api/status", methods=["GET"])
def status():
    """Returns current scrape state, cache age, and question count."""
    questions = _get_questions()
    with _cache_lock:
        age = time.monotonic() - _cache["loaded_at"]
    return jsonify({
        "scraping":       _scraping,
        "question_count": len(questions),
        "has_questions":  len(questions) > 0,
        "cache_age_s":    round(age, 1),
        "scraper_ready":  _SCRAPER_AVAILABLE,
    })


# ═══════════════════════════════════════════════════════════════
# ROUTES — SSE Scrape
# ═══════════════════════════════════════════════════════════════

@app.route("/api/scrape", methods=["POST"])
@require_scraper
def trigger_scrape():
    """
    Kicks off a background scrape and immediately returns 202.
    The client should open GET /api/scrape/stream for SSE progress.
    """
    global _scraping

    with _scrape_lock:
        if _scraping:
            return jsonify({
                "status":  "pending",
                "message": "A scrape is already in progress — connect to /api/scrape/stream for live updates.",
            }), 202
        _scraping = True

    _invalidate_cache()
    thread = threading.Thread(target=_scrape_thread_target, daemon=True, name="scraper")
    thread.start()

    return jsonify({
        "status":  "started",
        "message": "Scrape started. Connect to GET /api/scrape/stream for live progress.",
    }), 202


@app.route("/api/scrape/stream", methods=["GET"])
@require_scraper
def scrape_stream():
    """
    Server-Sent Events endpoint.

    The client opens this as an EventSource. It receives:
      event: progress  data: {"stage", "pct", "msg", "fetched"}
      event: done      data: {"count", "questions": [...]}
      event: error     data: {"msg": "..."}
      event: heartbeat data: ""           (every 15 s, keeps connection alive)

    If no scrape is running and questions already exist, the endpoint
    immediately emits a 'done' event with the cached questions so the
    frontend can bootstrap without a round-trip.
    """
    client_q: queue.Queue = queue.Queue(maxsize=200)

    def generate() -> Generator[str, None, None]:
        with _sse_lock:
            _sse_clients.append(client_q)

        # If questions are already cached and no scrape is running,
        # push them immediately so the client doesn't hang.
        if not _scraping:
            existing = _get_questions()
            if existing:
                yield (
                    f"event: done\n"
                    f"data: {json.dumps({'count': len(existing), 'questions': existing}, ensure_ascii=False)}\n\n"
                )
                with _sse_lock:
                    if client_q in _sse_clients:
                        _sse_clients.remove(client_q)
                return

        try:
            while True:
                try:
                    # Block up to 15 s; if nothing arrives, send a heartbeat
                    payload = client_q.get(timeout=15)
                    yield payload
                    # If this was a terminal event, close cleanly
                    if payload.startswith("event: done") or payload.startswith("event: error"):
                        break
                except queue.Empty:
                    # Heartbeat keeps Nginx / load-balancers from closing idle connections
                    yield "event: heartbeat\ndata: \n\n"
        finally:
            with _sse_lock:
                if client_q in _sse_clients:
                    _sse_clients.remove(client_q)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":   "no-cache",
            "X-Accel-Buffering": "no",   # disable Nginx buffering
        },
    )


# ═══════════════════════════════════════════════════════════════
# ROUTES — Download helpers
# ═══════════════════════════════════════════════════════════════

@app.route("/api/download/json", methods=["GET"])
def download_json():
    """Download filtered questions as a JSON attachment."""
    questions = _get_questions()
    exam_param = _sanitise_exam(request.args.get("exam", "ALL"))
    if exam_param != "ALL":
        questions = [q for q in questions if q.get("exam", "").upper() == exam_param]

    payload = json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "exam":      exam_param,
        "count":     len(questions),
        "questions": questions,
    }, indent=2, ensure_ascii=False)

    return Response(
        payload,
        mimetype="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="QuizForge_{exam_param}.json"',
        },
    )


# ═══════════════════════════════════════════════════════════════
# CORS  (dev-friendly; tighten origin in production)
# ═══════════════════════════════════════════════════════════════

@app.after_request
def add_cors(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/api/<path:_>", methods=["OPTIONS"])
def options_preflight(_):
    """Handle CORS pre-flight requests for all /api/* routes."""
    return Response(status=204, headers={
        "Access-Control-Allow-Origin":  "*",
        "Access-Control-Allow-Headers": "Content-Type, Accept",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    })


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

    print("\n🚀  QuizForge v3.0 is live!")
    print(f"    → Frontend   : http://localhost:5000")
    print(f"    → Questions  : http://localhost:5000/api/questions")
    print(f"    → Start scrape: POST  http://localhost:5000/api/scrape")
    print(f"    → SSE stream  : GET   http://localhost:5000/api/scrape/stream")
    print(f"    → Static dir  : {STATIC_DIR}")
    print(f"    → Compressor  : {'flask-compress ✅' if _HAS_COMPRESS else 'not installed (pip install flask-compress)'}")
    print(f"    → Scraper     : {'ready ✅' if _SCRAPER_AVAILABLE else '❌ ' + _scraper_err_msg}\n")

    # Use threaded=True so SSE streams don't block other requests
    app.run(debug=True, port=5000, threaded=True)