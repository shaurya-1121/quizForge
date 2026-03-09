"""
╔══════════════════════════════════════════════════════════════╗
║          QUIZFORGE SCRAPER  v3.0  (scraper.py)              ║
║          Parallel Workers · Backoff · Hash Dedup            ║
╚══════════════════════════════════════════════════════════════╝

CHANGES FROM v2.0:
  ✅ ThreadPoolExecutor — 6 OpenTDB workers, 3 IndiaBix workers
  ✅ Exponential backoff for OpenTDB rate-limit (429 / code 5)
  ✅ Answer detection via regex  re.search(r'\b([A-D])\b', txt[:10])
  ✅ Deduplication by SHA-256 of full question text (not first 80 chars)
  ✅ IndiaBix multi-selector fallback chain for structural variation
  ✅ year tagged as "Practice" for OpenTDB (not fake years)
  ✅ source field always "OpenTDB" or "IndiaBix"
  ✅ All functions return [] instead of raising on failure
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_questions.json")

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

LETTERS = ["A", "B", "C", "D"]

DIFFICULTY_MAP = {
    "easy":   "Easy",
    "medium": "Medium",
    "hard":   "Hard",
}

# All OpenTDB items tagged "Practice" — never fake years
YEAR_TAG = "Practice"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

# ═══════════════════════════════════════════════════════════════
# TASK DEFINITIONS
# ═══════════════════════════════════════════════════════════════
#
# OpenTDB category reference:
#   9  = General Knowledge        18 = Science: Computers
#  17  = Science & Nature         19 = Science: Mathematics
#  20  = Mythology                22 = Geography
#  23  = History                  24 = Politics
#  27  = Animals                  30 = Science: Gadgets
#
# Tuple: (category_id, amount, difficulty, exam_tag, subject_label)
# ─────────────────────────────────────────────────────────────

OPENTDB_TASKS: list[tuple] = [
    # ── JEE  (Mathematics + Physics, no biology) ─────────────
    (19, 15, "hard",   "JEE",  "JEE — Mathematics · Calculus & Algebra"),
    (19, 10, "medium", "JEE",  "JEE — Mathematics · Arithmetic & Geometry"),
    (17, 12, "hard",   "JEE",  "JEE — Physics · Classical Mechanics"),
    (17,  8, "medium", "JEE",  "JEE — Physics · Modern Physics"),

    # ── NEET (Biology + Life Sciences, no pure math) ─────────
    (27, 15, "medium", "NEET", "NEET — Biology · Zoology & Animal Sciences"),
    (27, 10, "hard",   "NEET", "NEET — Biology · Advanced Zoology"),
    (17, 10, "easy",   "NEET", "NEET — Biology · Botany & Life Sciences"),
    (17,  8, "medium", "NEET", "NEET — Biology · Human Physiology"),

    # ── UPSC (Geography, History, Polity, Culture) ────────────
    (22, 12, "hard",   "UPSC", "UPSC — World Geography"),
    (22,  8, "medium", "UPSC", "UPSC — Indian Geography"),
    (23, 12, "hard",   "UPSC", "UPSC — World History"),
    (23,  8, "medium", "UPSC", "UPSC — Modern Indian History"),
    (20,  8, "medium", "UPSC", "UPSC — Art, Culture & Mythology"),
    (24,  8, "medium", "UPSC", "UPSC — Indian Polity"),

    # ── CAT  (Quantitative Aptitude) ─────────────────────────
    (19, 12, "hard",   "CAT",  "CAT — Quantitative Aptitude · Number Systems"),
    (19,  8, "medium", "CAT",  "CAT — Quantitative Aptitude · Time & Work"),

    # ── GK ───────────────────────────────────────────────────
    (9,  15, "hard",   "GK",   "GK — General Knowledge"),
    (9,  10, "medium", "GK",   "GK — Current Affairs"),
    (18,  8, "hard",   "GK",   "GK — Science & Technology"),

    # ── SAT ──────────────────────────────────────────────────
    (30,  8, "hard",   "SAT",  "SAT — Science: Gadgets & Technology"),
    (17,  8, "medium", "SAT",  "SAT — Physical Sciences"),
]

INDIABIX_TASKS: list[tuple] = [
    # (url, subject, exam)
    ("https://www.indiabix.com/general-knowledge/world-geography/",   "UPSC — World Geography",              "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-politics/",   "UPSC — Indian Polity",                "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-history/",    "UPSC — Indian History",               "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-economy/",    "UPSC — Indian Economy",               "UPSC"),
    ("https://www.indiabix.com/aptitude/problems-on-trains/",         "CAT — Quantitative Aptitude",         "CAT"),
    ("https://www.indiabix.com/aptitude/time-and-work/",              "CAT — Time & Work",                   "CAT"),
    ("https://www.indiabix.com/aptitude/percentage/",                 "CAT — Percentage Problems",           "CAT"),
    ("https://www.indiabix.com/aptitude/profit-and-loss/",            "CAT — Profit & Loss",                 "CAT"),
    ("https://www.indiabix.com/general-knowledge/biology/",           "NEET — Biology · Life Sciences",      "NEET"),
    ("https://www.indiabix.com/general-knowledge/general-science/",   "GK — General Science",                "GK"),
]

# ═══════════════════════════════════════════════════════════════
# EXAM BOUNDARY FILTERS
# ═══════════════════════════════════════════════════════════════

_BIOLOGY_TOKENS = frozenset({
    "cell", "mitosis", "meiosis", "photosynthesis", "chlorophyll",
    "enzyme", "dna", "rna", "chromosome", "genetics", "organism",
    "vertebrate", "invertebrate", "mammal", "species", "taxonomy",
    "ecology", "ecosystem", "blood", "heart", "lung", "brain", "liver",
    "muscle", "bone", "nerve", "evolution", "antibiotic", "virus",
    "bacteria", "fungi", "algae", "protein", "amino", "hormone",
    "insulin", "disease", "immune", "nucleus", "mitochondria",
})

_MATH_PHYSICS_TOKENS = frozenset({
    "equation", "derivative", "integral", "matrix", "vector",
    "velocity", "acceleration", "force", "momentum", "circuit",
    "resistance", "current", "voltage", "magnetic", "electric",
    "wavelength", "frequency", "thermodynamics", "entropy",
    "pressure", "density", "gravitational", "calculus",
})


def _token_overlap(text_lower: str, token_set: frozenset) -> int:
    words = set(re.findall(r'\b\w+\b', text_lower))
    return len(words & token_set)


def is_suitable_for_exam(q_text_lower: str, exam: str) -> bool:
    """
    Returns False if the question text strongly contradicts its exam tag.
    Heuristic-based; uses token overlap counts, not simple substring search.
    """
    if exam == "JEE":
        # Drop questions with 2+ biology-specific tokens
        if _token_overlap(q_text_lower, _BIOLOGY_TOKENS) >= 2:
            return False
    elif exam == "NEET":
        # Drop questions dominated by math/physics tokens
        if _token_overlap(q_text_lower, _MATH_PHYSICS_TOKENS) >= 3:
            return False
    return True


# ═══════════════════════════════════════════════════════════════
# DEDUPLICATION
# ═══════════════════════════════════════════════════════════════

def _question_hash(q: dict) -> str:
    """SHA-256 of the full normalised question text."""
    text = re.sub(r'\s+', ' ', q.get("question", "")).strip().lower()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def deduplicate(questions: list[dict]) -> list[dict]:
    """Remove questions with identical normalised text (full-text hash)."""
    seen: set[str] = set()
    unique: list[dict] = []
    for q in questions:
        h = _question_hash(q)
        if h not in seen:
            seen.add(h)
            unique.append(q)
    return unique


# ═══════════════════════════════════════════════════════════════
# OPENTDB  — Fetch with exponential backoff
# ═══════════════════════════════════════════════════════════════

_OPENTDB_BASE = "https://opentdb.com/api.php"
_RATE_LIMIT_CODE = 5   # OpenTDB returns response_code 5 when rate-limited

def _opentdb_url(category_id: int, amount: int, difficulty: str) -> str:
    return (
        f"{_OPENTDB_BASE}"
        f"?amount={amount}"
        f"&category={category_id}"
        f"&type=multiple"
        f"&difficulty={difficulty}"
    )


def fetch_opentdb(
    category_id: int,
    amount: int,
    difficulty: str,
    exam: str,
    subject: str,
    max_retries: int = 4,
) -> list[dict]:
    """
    Fetch MCQ questions from Open Trivia Database.

    Retries up to `max_retries` times with exponential backoff when the
    API returns rate-limit code 5 or an HTTP 429.  Returns [] on failure.
    """
    url = _opentdb_url(category_id, amount, difficulty)
    backoff = 2.0   # seconds; doubles each retry

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=25)

            # HTTP-level rate limit
            if resp.status_code == 429:
                print(f"  ⏳ OpenTDB 429 [{subject}] — backing off {backoff:.0f}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            resp.raise_for_status()
            data = resp.json()
            code = data.get("response_code", -1)

            # API-level rate limit
            if code == _RATE_LIMIT_CODE:
                print(f"  ⏳ OpenTDB rate-limit (code 5) [{subject}] — backing off {backoff:.0f}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            if code != 0:
                print(f"  ⚠️  OpenTDB [{subject}] code={code} — skipping")
                return []

            return _parse_opentdb_results(data.get("results", []), exam, subject, difficulty)

        except requests.RequestException as exc:
            print(f"  ❌ OpenTDB [{subject}] network error (attempt {attempt+1}): {exc}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

    print(f"  ❌ OpenTDB [{subject}] gave up after {max_retries} attempts")
    return []


def _parse_opentdb_results(
    results: list,
    exam: str,
    subject: str,
    difficulty: str,
) -> list[dict]:
    questions: list[dict] = []
    for item in results:
        q_text  = html.unescape(item.get("question", "")).strip()
        correct = html.unescape(item.get("correct_answer", "")).strip()
        wrongs  = [html.unescape(a).strip() for a in item.get("incorrect_answers", [])]

        if not q_text or not correct:
            continue

        if not is_suitable_for_exam(q_text.lower(), exam):
            continue

        opts_list = [correct] + wrongs
        random.shuffle(opts_list)
        options = {LETTERS[i]: opts_list[i] for i in range(min(len(opts_list), 4))}
        answer  = next((k for k, v in options.items() if v == correct), "A")

        topic = (
            subject.split("·")[-1].strip()
            if "·" in subject
            else subject.split("—")[-1].strip()
        )
        explanation = (
            f"Correct answer: {correct}. "
            f"This question covers {topic} — a key topic in {exam}."
        )

        questions.append({
            "subject":     subject,
            "exam":        exam,
            "year":        YEAR_TAG,
            "difficulty":  DIFFICULTY_MAP.get(item.get("difficulty", difficulty), "Medium"),
            "question":    q_text,
            "options":     options,
            "answer":      answer,
            "explanation": explanation,
            "source":      "OpenTDB",
            "type":        "mcq",
        })

    print(f"  ✅ OpenTDB [{subject}]: {len(questions)} questions")
    return questions


# ═══════════════════════════════════════════════════════════════
# INDIABIX  — Scrape with multi-selector fallback chain
# ═══════════════════════════════════════════════════════════════

# Each fallback is a tuple (question_selector, options_selector, answer_selector)
# IndiaBix occasionally restructures its markup; we try each in order.
_INDIABIX_SELECTORS = [
    # Variant A — classic layout
    {
        "q_wrap":    ("div", {"class": "bix-div-d"}),
        "q_text":    ("div", {"class": "bix-td-qtxt"}),
        "opts_tbl":  ("table", {"class": "bix-tbl-options"}),
        "ans_wrap":  ("div", {"class": "bix-div-answer"}),
        "exp_wrap":  ("div", {"class": "bix-ans-description"}),
    },
    # Variant B — newer card layout
    {
        "q_wrap":    ("div", {"class": "question"}),
        "q_text":    ("p", {"class": "question-text"}),
        "opts_tbl":  ("ul", {"class": "options"}),
        "ans_wrap":  ("div", {"class": "answer"}),
        "exp_wrap":  ("div", {"class": "explanation"}),
    },
    # Variant C — minimal div structure
    {
        "q_wrap":    ("div", {"class": "qtxt"}),
        "q_text":    ("p", {}),
        "opts_tbl":  ("ol", {}),
        "ans_wrap":  ("span", {"class": "correct"}),
        "exp_wrap":  ("div", {"class": "explain"}),
    },
]

_ANSWER_RE = re.compile(r'\b([A-D])\b')


def _detect_answer(ans_el) -> str:
    """Extract the answer letter from an answer element using regex."""
    if ans_el is None:
        return "A"
    txt = ans_el.get_text(separator=" ", strip=True)[:20]
    m = _ANSWER_RE.search(txt)
    return m.group(1) if m else "A"


def _parse_indiabix_variant_a(q_div, subject: str, exam: str) -> Optional[dict]:
    """Parse classic IndiaBix layout (Variant A)."""
    sel = _INDIABIX_SELECTORS[0]

    q_el = q_div.find(*sel["q_text"])
    if not q_el:
        return None
    q_text = q_el.get_text(separator=" ", strip=True).strip()
    if not q_text or not is_suitable_for_exam(q_text.lower(), exam):
        return None

    opts_tbl = q_div.find(*sel["opts_tbl"])
    if not opts_tbl:
        return None
    rows = opts_tbl.find_all("tr")
    options: dict[str, str] = {}
    for j, row in enumerate(rows[:4]):
        cells = row.find_all("td")
        if len(cells) >= 2:
            options[LETTERS[j]] = cells[-1].get_text(strip=True)

    if len(options) < 2:
        return None

    ans_div    = q_div.find(*sel["ans_wrap"])
    answer     = _detect_answer(ans_div)
    exp_div    = q_div.find(*sel["exp_wrap"])
    explanation = (
        exp_div.get_text(separator=" ", strip=True)[:400]
        if exp_div
        else f"Refer to IndiaBix for a detailed explanation of this {exam} question."
    )

    return {
        "subject":     subject,
        "exam":        exam,
        "year":        YEAR_TAG,
        "difficulty":  "Medium",
        "question":    q_text[:400],
        "options":     options,
        "answer":      answer,
        "explanation": explanation,
        "source":      "IndiaBix",
        "type":        "mcq",
    }


def _parse_indiabix_variant_b(q_div, subject: str, exam: str) -> Optional[dict]:
    """Parse newer IndiaBix card layout (Variant B) — <ul class='options'>."""
    q_el = q_div.find("p", class_="question-text") or q_div.find("p")
    if not q_el:
        return None
    q_text = q_el.get_text(separator=" ", strip=True)
    if not q_text or not is_suitable_for_exam(q_text.lower(), exam):
        return None

    ul = q_div.find("ul")
    if not ul:
        return None
    items = ul.find_all("li")
    options: dict[str, str] = {}
    for j, li in enumerate(items[:4]):
        options[LETTERS[j]] = li.get_text(strip=True)

    if len(options) < 2:
        return None

    ans_el  = q_div.find(class_=re.compile(r'answer|correct', re.I))
    answer  = _detect_answer(ans_el)
    exp_el  = q_div.find(class_=re.compile(r'explain', re.I))
    explanation = (
        exp_el.get_text(separator=" ", strip=True)[:400]
        if exp_el
        else f"Refer to IndiaBix for a detailed explanation."
    )

    return {
        "subject":     subject,
        "exam":        exam,
        "year":        YEAR_TAG,
        "difficulty":  "Medium",
        "question":    q_text[:400],
        "options":     options,
        "answer":      answer,
        "explanation": explanation,
        "source":      "IndiaBix",
        "type":        "mcq",
    }


def scrape_indiabix(url: str, subject: str, exam: str, max_q: int = 8) -> list[dict]:
    """
    Scrape questions from IndiaBix.
    Tries Variant A first; falls back to Variant B for each question block.
    Returns [] on any network / parse failure.
    """
    questions: list[dict] = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find question wrapper divs
        q_divs = (
            soup.find_all("div", class_="bix-div-d")
            or soup.find_all("div", class_="question")
            or soup.find_all("div", class_=re.compile(r'q-?block|question-block', re.I))
        )

        if not q_divs:
            print(f"  ⚠️  IndiaBix [{subject}]: no question blocks found (page structure unknown)")
            return []

        for q_div in q_divs[:max_q]:
            try:
                q = _parse_indiabix_variant_a(q_div, subject, exam)
                if q is None:
                    q = _parse_indiabix_variant_b(q_div, subject, exam)
                if q:
                    questions.append(q)
            except Exception:
                continue   # skip individual malformed blocks silently

        print(f"  ✅ IndiaBix [{subject}]: {len(questions)} questions")

    except requests.RequestException as exc:
        print(f"  ❌ IndiaBix [{subject}] network error: {exc}")
    except Exception as exc:
        print(f"  ❌ IndiaBix [{subject}] parse error: {exc}")

    return questions


# ═══════════════════════════════════════════════════════════════
# PARALLEL SCRAPE RUNNERS
# ═══════════════════════════════════════════════════════════════

def _run_opentdb_parallel(tasks: list[tuple], max_workers: int = 6) -> list[dict]:
    """Run OpenTDB fetches in parallel (up to max_workers threads)."""
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="opentdb") as pool:
        futures = {
            pool.submit(fetch_opentdb, cat_id, amount, diff, exam, subject): subject
            for (cat_id, amount, diff, exam, subject) in tasks
        }
        for future in as_completed(futures):
            subj = futures[future]
            try:
                qs = future.result()
                results.extend(qs)
            except Exception as exc:
                print(f"  ❌ OpenTDB [{subj}] thread error: {exc}")
    return results


def _run_indiabix_parallel(tasks: list[tuple], max_workers: int = 3) -> list[dict]:
    """Run IndiaBix scrapes in parallel (up to max_workers threads)."""
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="indiabix") as pool:
        futures = {
            pool.submit(scrape_indiabix, url, subject, exam): subject
            for (url, subject, exam) in tasks
        }
        for future in as_completed(futures):
            subj = futures[future]
            try:
                qs = future.result()
                results.extend(qs)
            except Exception as exc:
                print(f"  ❌ IndiaBix [{subj}] thread error: {exc}")
    return results


# ═══════════════════════════════════════════════════════════════
# MAIN (standalone run)
# ═══════════════════════════════════════════════════════════════

def main() -> list[dict]:
    from collections import Counter

    print("\n🎯 QuizForge Scraper v3.0 — Parallel · Backoff · Hash-Dedup")
    print("=" * 62)

    all_questions: list[dict] = []

    print(f"\n🌐 Phase 1 — OpenTDB ({len(OPENTDB_TASKS)} tasks, 6 parallel workers)…")
    all_questions.extend(_run_opentdb_parallel(OPENTDB_TASKS, max_workers=6))

    print(f"\n📚 Phase 2 — IndiaBix ({len(INDIABIX_TASKS)} tasks, 3 parallel workers)…")
    all_questions.extend(_run_indiabix_parallel(INDIABIX_TASKS, max_workers=3))

    all_questions = deduplicate(all_questions)
    random.shuffle(all_questions)
    for i, q in enumerate(all_questions):
        q["id"] = i + 1

    counts = Counter(q["exam"] for q in all_questions)
    print(f"\n📊 Distribution:")
    for exam, count in sorted(counts.items()):
        print(f"   {exam:8s} → {count:4d} questions")

    if all_questions:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(all_questions)} unique questions → {OUTPUT_FILE}")
        print("   Run  python app.py  to serve!\n")
    else:
        print("\n⚠️  Nothing scraped — check internet connection.\n")

    return all_questions


if __name__ == "__main__":
    main()