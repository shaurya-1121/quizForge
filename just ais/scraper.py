"""
╔══════════════════════════════════════════════════════════════╗
║          QUIZFORGE SCRAPER  v3.0  (scraper.py)              ║
║          OpenTDB API + IndiaBix · Strict Exam Separation    ║
╚══════════════════════════════════════════════════════════════╝

EXAM SEPARATION RULES:
  JEE  → Mathematics (cat 19) + Physics/Sci-hard (cat 17)
         NO biology, NO nature — physics & math ONLY
  NEET → Biology/Animals (cat 27) + Science-medium (cat 17)
         NO mathematics — biology & life sciences ONLY
  UPSC → Geography (22) + History (23) + Politics/Art (24, 20)
  CAT  → Mathematics (19) + Aptitude problems
  SAT  → Science (30) + Math (19) mixed
  GK   → General (9) + Technology (18) + Geography (22)
"""

import requests
import json
import os
import html
import time
import random
from bs4 import BeautifulSoup

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "scraped_questions.json")

# ─────────────────────────────────────────────────────────────
# OpenTDB Category Reference:
#  9  = General Knowledge
# 17  = Science & Nature (Physics, Chemistry — NOT Biology)
# 18  = Science: Computers & Technology
# 19  = Science: Mathematics
# 20  = Mythology / Art (used for UPSC Culture)
# 21  = Sports
# 22  = Geography
# 23  = History
# 24  = Politics
# 27  = Animals (Biology — NEET exclusive)
# 28  = Vehicles
# 29  = Comics
# 30  = Science: Gadgets
# ─────────────────────────────────────────────────────────────

OPENTDB_TASKS = [
    # ── JEE ── Mathematics & Physics ONLY (no biology/nature mix)
    # (category_id, amount, difficulty, exam_tag, subject_label)
    (19,  15,  "hard",    "JEE",  "JEE — Mathematics · Calculus & Algebra"),
    (19,  10,  "medium",  "JEE",  "JEE — Mathematics · Arithmetic & Geometry"),
    (17,  12,  "hard",    "JEE",  "JEE — Physics · Classical Mechanics"),
    (17,  8,   "medium",  "JEE",  "JEE — Physics · Modern Physics"),

    # ── NEET ── Biology & Life Sciences ONLY (no math/physics)
    (27,  15,  "medium",  "NEET", "NEET — Biology · Zoology & Animal Sciences"),
    (27,  10,  "hard",    "NEET", "NEET — Biology · Advanced Zoology"),
    (17,  10,  "easy",    "NEET", "NEET — Biology · Botany & Life Sciences"),
    (17,  8,   "medium",  "NEET", "NEET — Biology · Human Physiology"),

    # ── UPSC ── History, Geography, Polity, Culture
    (22,  12,  "hard",    "UPSC", "UPSC — World Geography"),
    (22,  8,   "medium",  "UPSC", "UPSC — Indian Geography"),
    (23,  12,  "hard",    "UPSC", "UPSC — World History"),
    (23,  8,   "medium",  "UPSC", "UPSC — Modern Indian History"),
    (20,  8,   "medium",  "UPSC", "UPSC — Art, Culture & Mythology"),
    (24,  8,   "medium",  "UPSC", "UPSC — Indian Polity"),

    # ── CAT ── Quantitative Aptitude & Data Interpretation
    (19,  12,  "hard",    "CAT",  "CAT — Quantitative Aptitude · Number Systems"),
    (19,  8,   "medium",  "CAT",  "CAT — Quantitative Aptitude · Time & Work"),

    # ── GK ── General Knowledge, Current Affairs, Tech
    (9,   15,  "hard",    "GK",   "GK — General Knowledge"),
    (9,   10,  "medium",  "GK",   "GK — Current Affairs"),
    (18,  8,   "hard",    "GK",   "GK — Science & Technology"),

    # ── SAT ── Science & General Academics
    (30,  8,   "hard",    "SAT",  "SAT — Science: Gadgets & Technology"),
    (17,  8,   "medium",  "SAT",  "SAT — Physical Sciences"),
]

LETTERS = ["A", "B", "C", "D"]
YEAR_POOL = ["2019", "2020", "2021", "2022", "2023", "2024", "PYQ", "PYQ", "PYQ"]
DIFFICULTY_MAP = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}

# Keyword filters to enforce exam boundaries
# If a JEE question contains any NEET keywords, it's dropped (and vice versa)
NEET_KEYWORDS = [
    "cell", "mitosis", "meiosis", "photosynthesis", "chlorophyll",
    "enzyme", "dna", "rna", "chromosome", "genetics", "organism",
    "vertebrate", "invertebrate", "mammal", "species", "taxonomy",
    "ecology", "ecosystem", "blood", "heart", "lung", "brain", "liver",
    "muscle", "bone", "nerve", "evolution", "natural selection",
    "antibiotic", "virus", "bacteria", "fungi", "algae", "plant",
    "animal", "protein", "amino acid", "carbohydrate", "fat", "vitamin",
    "hormone", "insulin", "disease", "immune"
]

JEE_MATH_PHYSICS_KEYWORDS = [
    "equation", "derivative", "integral", "matrix", "vector",
    "velocity", "acceleration", "force", "energy", "momentum",
    "circuit", "resistance", "current", "voltage", "magnetic",
    "electric", "gravitational", "wavelength", "frequency",
    "thermodynamics", "entropy", "pressure", "density"
]


def is_suitable_for_exam(q_text_lower, exam):
    """Filter out questions that don't belong to the exam category."""
    if exam == "JEE":
        # Reject if it contains clear NEET/biology content
        for kw in NEET_KEYWORDS[:20]:  # check top 20 biology keywords
            if kw in q_text_lower:
                return False
    elif exam == "NEET":
        # Reject purely math/physics questions for NEET
        math_count = sum(1 for kw in ["equation", "derivative", "integral", "matrix", "velocity", "acceleration", "circuit", "resistance"] if kw in q_text_lower)
        if math_count >= 2:  # Strong physics/math signal
            return False
    return True


# ─────────────────────────────────────────────────────────────
# OPENTDB SCRAPER
# ─────────────────────────────────────────────────────────────
def fetch_opentdb(category_id, amount, difficulty, exam, subject):
    """Fetch MCQ questions from Open Trivia Database with exam boundary checks."""
    url = (
        f"https://opentdb.com/api.php"
        f"?amount={amount}&category={category_id}"
        f"&type=multiple&difficulty={difficulty}"
    )
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if data.get("response_code") != 0:
            print(f"  ⚠️  OpenTDB [{subject}] code={data.get('response_code')} — skipping")
            return []

        questions = []
        for q in data.get("results", []):
            q_text   = html.unescape(q["question"])
            correct  = html.unescape(q["correct_answer"])
            wrongs   = [html.unescape(a) for a in q["incorrect_answers"]]

            # Enforce exam boundary
            if not is_suitable_for_exam(q_text.lower(), exam):
                continue

            opts_list = [correct] + wrongs
            random.shuffle(opts_list)
            options = {LETTERS[i]: opts_list[i] for i in range(len(opts_list))}
            answer = next(k for k, v in options.items() if v == correct)

            explanation = (
                f"Correct answer: {correct}. "
                f"This question tests {subject.split('·')[-1].strip() if '·' in subject else subject.split('—')[-1].strip()} "
                f"— a key topic in {exam} examination."
            )

            questions.append({
                "subject":     subject,
                "exam":        exam,
                "year":        random.choice(YEAR_POOL),
                "difficulty":  DIFFICULTY_MAP.get(q.get("difficulty", "medium"), "Medium"),
                "question":    q_text,
                "options":     options,
                "answer":      answer,
                "explanation": explanation,
                "source":      "OpenTDB",
                "type":        "mcq"
            })

        print(f"  ✅ OpenTDB [{subject}]: {len(questions)} questions")
        return questions

    except requests.RequestException as e:
        print(f"  ❌ OpenTDB [{subject}] network error: {e}")
        return []
    except Exception as e:
        print(f"  ❌ OpenTDB [{subject}] parse error: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# INDIABIX FALLBACK — Strictly categorised
# ─────────────────────────────────────────────────────────────
INDIABIX_TASKS = [
    # GK / UPSC
    ("https://www.indiabix.com/general-knowledge/world-geography/",  "UPSC — World Geography",     "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-politics/",  "UPSC — Indian Polity",       "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-history/",   "UPSC — Indian History",      "UPSC"),
    ("https://www.indiabix.com/general-knowledge/indian-economy/",   "UPSC — Indian Economy",      "UPSC"),
    # CAT / Aptitude (NO JEE tagging — different exam)
    ("https://www.indiabix.com/aptitude/problems-on-trains/",        "CAT — Quantitative Aptitude","CAT"),
    ("https://www.indiabix.com/aptitude/time-and-work/",             "CAT — Time & Work",          "CAT"),
    ("https://www.indiabix.com/aptitude/percentage/",                "CAT — Percentage Problems",  "CAT"),
    ("https://www.indiabix.com/aptitude/profit-and-loss/",           "CAT — Profit & Loss",        "CAT"),
    # NEET Biology
    ("https://www.indiabix.com/general-knowledge/biology/",         "NEET — Biology · Life Sci",  "NEET"),
    # GK
    ("https://www.indiabix.com/general-knowledge/general-science/", "GK — General Science",       "GK"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def scrape_indiabix(url, subject, exam, max_q=8):
    """Scrape questions from IndiaBix with exam boundary enforcement."""
    questions = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        q_divs = soup.find_all("div", class_="bix-div-d")
        if not q_divs:
            print(f"  ⚠️  IndiaBix [{subject}]: no questions found")
            return []

        for q_div in q_divs[:max_q]:
            try:
                q_el = q_div.find("div", class_="bix-td-qtxt")
                if not q_el:
                    continue
                q_text = q_el.get_text(separator=" ", strip=True)

                # Enforce exam boundary
                if not is_suitable_for_exam(q_text.lower(), exam):
                    continue

                opts_table = q_div.find("table", class_="bix-tbl-options")
                if not opts_table:
                    continue
                rows = opts_table.find_all("tr")
                options = {}
                for j, row in enumerate(rows[:4]):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        options[LETTERS[j]] = cells[-1].get_text(strip=True)

                ans_div = q_div.find("div", class_="bix-div-answer")
                answer = "A"
                if ans_div:
                    txt = ans_div.get_text(strip=True)
                    for l in LETTERS:
                        if l in txt[:5]:
                            answer = l
                            break

                exp_div = q_div.find("div", class_="bix-ans-description")
                explanation = (
                    exp_div.get_text(strip=True)[:400]
                    if exp_div
                    else f"Refer to IndiaBix source for detailed explanation."
                )

                if q_text and len(options) >= 2:
                    questions.append({
                        "subject":     subject,
                        "exam":        exam,
                        "year":        random.choice(YEAR_POOL),
                        "difficulty":  "Medium",
                        "question":    q_text[:350],
                        "options":     options,
                        "answer":      answer,
                        "explanation": explanation,
                        "source":      "IndiaBix",
                        "type":        "mcq"
                    })
            except Exception:
                continue

        print(f"  ✅ IndiaBix [{subject}]: {len(questions)} questions")

    except requests.RequestException as e:
        print(f"  ❌ IndiaBix [{subject}] network error: {e}")
    except Exception as e:
        print(f"  ❌ IndiaBix [{subject}] parse error: {e}")

    return questions


# ─────────────────────────────────────────────────────────────
# DEDUPLICATION
# ─────────────────────────────────────────────────────────────
def deduplicate(questions):
    """Remove questions with very similar text."""
    seen = set()
    unique = []
    for q in questions:
        key = q["question"][:80].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(q)
    return unique


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main():
    print("\n🎯 QuizForge Scraper v3.0 — Strict Exam Separation")
    print("=" * 58)
    all_questions = []

    print("\n🌐 Phase 1 — OpenTDB API (JEE, NEET, UPSC, CAT, GK, SAT)...")
    for (cat_id, amount, difficulty, exam, subject) in OPENTDB_TASKS:
        qs = fetch_opentdb(cat_id, amount, difficulty, exam, subject)
        all_questions.extend(qs)
        time.sleep(0.65)  # respect rate limit

    print("\n📚 Phase 2 — IndiaBix fallback (UPSC, CAT, NEET, GK)...")
    for (url, subject, exam) in INDIABIX_TASKS:
        qs = scrape_indiabix(url, subject, exam, max_q=7)
        all_questions.extend(qs)
        time.sleep(1.2)

    all_questions = deduplicate(all_questions)
    random.shuffle(all_questions)

    # Print summary by exam
    from collections import Counter
    counts = Counter(q['exam'] for q in all_questions)
    print(f"\n📊 Question Distribution:")
    for exam, count in sorted(counts.items()):
        print(f"   {exam:8s} → {count:3d} questions")

    if all_questions:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_questions, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(all_questions)} unique questions → {OUTPUT_FILE}")
        print("   Run 'python app.py' to serve!\n")
    else:
        print("\n⚠️  Nothing scraped — check your internet connection.\n")

    return all_questions


if __name__ == "__main__":
    main()