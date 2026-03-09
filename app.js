/* ═══════════════════════════════════════════════════════════════
   QUIZFORGE  v3.0  —  app.js
   SSE scrape · Bookmarks · Chapter filter · Timer mode
   WhatsApp PDF gate · Dark mode · Confetti · Music player
═══════════════════════════════════════════════════════════════ */

/* ── JEE Numerical bank (built-in) ────────────────────────── */
const JEE_NUMERICALS = [
  { question:"A ball thrown vertically upward with speed 20 m/s. Maximum height? (g=10)", numericalAnswer:20, unit:"m", subject:"JEE — Physics · Mechanics", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"v²=u²−2gh → h=20 m", chapter:"Mechanics", marks:4, negative_marks:0 },
  { question:"KE (J) of 4 kg body at 5 m/s?", numericalAnswer:50, unit:"J", subject:"JEE — Physics · Mechanics", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"KE=½mv²=50 J", chapter:"Mechanics", marks:4, negative_marks:0 },
  { question:"Centripetal acceleration (m/s²): r=2 m, v=6 m/s?", numericalAnswer:18, unit:"m/s²", subject:"JEE — Physics · Circular Motion", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"a=v²/r=18", chapter:"Circular Motion", marks:4, negative_marks:0 },
  { question:"Wave speed (m/s): f=50 Hz, λ=4 m?", numericalAnswer:200, unit:"m/s", subject:"JEE — Physics · Waves", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"v=fλ=200", chapter:"Waves", marks:4, negative_marks:0 },
  { question:"Equivalent resistance (Ω): 6Ω ∥ 3Ω?", numericalAnswer:2, unit:"Ω", subject:"JEE — Physics · Electricity", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"R=2 Ω", chapter:"Electricity", marks:4, negative_marks:0 },
  { question:"Work done (J): F=10 N, d=5 m, θ=60°?", numericalAnswer:25, unit:"J", subject:"JEE — Physics · Work & Energy", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"W=Fd cosθ=25 J", chapter:"Work & Energy", marks:4, negative_marks:0 },
  { question:"Horizontal range (m): 45°, 10√2 m/s, g=10?", numericalAnswer:20, unit:"m", subject:"JEE — Physics · Projectile", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"R=20 m", chapter:"Projectile Motion", marks:4, negative_marks:0 },
  { question:"Current (A): V=24 V, R=8 Ω?", numericalAnswer:3, unit:"A", subject:"JEE — Physics · Electricity", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"I=V/R=3 A", chapter:"Electricity", marks:4, negative_marks:0 },
  { question:"Moles of water in 36 g?", numericalAnswer:2, unit:"mol", subject:"JEE — Chemistry · Mole Concept", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"n=36/18=2 mol", chapter:"Mole Concept", marks:4, negative_marks:0 },
  { question:"pH of 0.001 M HCl?", numericalAnswer:3, unit:"", subject:"JEE — Chemistry · Ionic Equilibrium", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"pH=3", chapter:"Ionic Equilibrium", marks:4, negative_marks:0 },
  { question:"Volume (L) of 2 mol ideal gas at STP?", numericalAnswer:44.8, unit:"L", subject:"JEE — Chemistry · Gases", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"2×22.4=44.8 L", chapter:"Gaseous State", marks:4, negative_marks:0 },
  { question:"f'(x) at x=2 for f(x)=3x²+2x?", numericalAnswer:14, unit:"", subject:"JEE — Mathematics · Calculus", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"f'(2)=14", chapter:"Calculus", marks:4, negative_marks:0 },
  { question:"∫₀² 2x dx = ?", numericalAnswer:4, unit:"", subject:"JEE — Mathematics · Integration", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"[x²]₀²=4", chapter:"Calculus", marks:4, negative_marks:0 },
  { question:"5th term of AP: a=3, d=4?", numericalAnswer:19, unit:"", subject:"JEE — Mathematics · Sequences", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"a₅=19", chapter:"Sequences & Series", marks:4, negative_marks:0 },
  { question:"Distance: (0,0) to (5,12)?", numericalAnswer:13, unit:"", subject:"JEE — Mathematics · Geometry", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"√(169)=13", chapter:"Coordinate Geometry", marks:4, negative_marks:0 },
  { question:"Sum of roots: x²−7x+12=0?", numericalAnswer:7, unit:"", subject:"JEE — Mathematics · Algebra", exam:"JEE", difficulty:"Easy", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"Sum=7", chapter:"Algebra", marks:4, negative_marks:0 },
  { question:"Coefficient of x³ in (1+x)⁵?", numericalAnswer:10, unit:"", subject:"JEE — Mathematics · Binomial", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"C(5,3)=10", chapter:"Binomial Theorem", marks:4, negative_marks:0 },
  { question:"det[[2,1],[1,2]] = ?", numericalAnswer:3, unit:"", subject:"JEE — Mathematics · Matrices", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"4−1=3", chapter:"Matrices", marks:4, negative_marks:0 },
  { question:"Sum: 1 + 1/3 + 1/9 + … = ?", numericalAnswer:1.5, unit:"", subject:"JEE — Mathematics · Series", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"S=3/2=1.5", chapter:"Sequences & Series", marks:4, negative_marks:0 },
  { question:"Escape velocity (km/s) from Earth? (g=9.8, R=6400 km)", numericalAnswer:11.2, unit:"km/s", subject:"JEE — Physics · Gravitation", exam:"JEE", difficulty:"Medium", year:"Practice", type:"numerical", source:"JEE Archive", explanation:"v=√(2gR)≈11.2 km/s", chapter:"Gravitation", marks:4, negative_marks:0 },
];

/* ═══════════════════════════════════════════════════════════════
   STATE
═══════════════════════════════════════════════════════════════ */
let allQ        = [];
let filteredQ   = [];
let currentIdx  = 0;
let selected    = null;
let answered    = false;
let score       = 0;
let streak      = 0;
let activeExam  = "ALL";
let activeChapter = "ALL";
let timerSec    = 30;
let timerInterval = null;
let sseSource   = null;

// Timer mode: 0 = off, otherwise seconds limit
let timerModeLimit   = 0;
let timerModeRemain  = 0;
let timerModeInterval = null;

// History for chart (array of "correct"|"wrong"|"skipped")
let answerHistory = [];

// Bookmarks
let bookmarks = JSON.parse(localStorage.getItem("qf_bookmarks") || "[]");

/* ═══════════════════════════════════════════════════════════════
   DOM REFS
═══════════════════════════════════════════════════════════════ */
const $ = id => document.getElementById(id);
const $loader     = $("loadingScreen");
const $loaderRing = $("loaderRing");
const $loadLog    = $("loadLog");
const $fetchBtn   = $("fetchBtn");
const $quizArea   = $("quizArea");
const $tabsWrap   = $("tabsWrap");
const $progFill   = $("progFill");
const $progLabel  = $("progLabel");
const $progPct    = $("progPct");
const $qCard      = $("qCard");
const $qNumber    = $("qNumber");
const $qMeta      = $("qMeta");
const $qText      = $("qText");
const $answerArea = $("answerArea");
const $expBox     = $("expBox");
const $expText    = $("expText");
const $expCorrect = $("expCorrectVal");
const $btnSubmit  = $("btnSubmit");
const $btnNext    = $("btnNext");
const $btnSkip    = $("btnSkip");
const $qCounter   = $("qCounter");
const $results    = $("resultsBox");
const $scoreVal   = $("scoreVal");
const $streakVal  = $("streakVal");
const $totalQCount= $("totalQCount");
const $sseProgress= $("sseProgress");
const $sseBarFill = $("sseBarFill");
const $ssePct     = $("ssePct");
const $sseMsg     = $("sseMsg");
const $sseLogEl   = $("sseLog");
const $chapterSel = $("chapterSelect");
const $timerSel   = $("timerModeSelect");
const $tmBar      = $("timerModeBar");
const $tmCountdown= $("timerModeCountdown");
const $tmLabel    = $("timerModeLabel");
const $chartWrap  = $("progressChart");

/* ── Dark mode ─────────────────────────────────────────────── */
const _dm = localStorage.getItem("qf_darkmode");
if (_dm === "1" || (_dm === null && window.matchMedia("(prefers-color-scheme:dark)").matches)) {
  document.body.classList.add("dark-mode");
}
function toggleDark() {
  document.body.classList.toggle("dark-mode");
  localStorage.setItem("qf_darkmode", document.body.classList.contains("dark-mode") ? "1" : "0");
}

/* ═══════════════════════════════════════════════════════════════
   LOGGING
═══════════════════════════════════════════════════════════════ */
function log(msg, type = "") {
  const el = document.createElement("div");
  el.className = `log-line log-${type}`;
  el.textContent = msg;
  $loadLog.appendChild(el);
  $loadLog.scrollTop = $loadLog.scrollHeight;
}
function sseLog(msg, cls = "") {
  const el = document.createElement("div");
  el.textContent = msg;
  if (cls) el.className = cls;
  $sseLogEl.appendChild(el);
  $sseLogEl.scrollTop = $sseLogEl.scrollHeight;
}

/* ═══════════════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════════════ */
async function init() {
  log("> QuizForge v3.0 initialising…", "info");
  log("> Checking /api/questions…", "info");
  try {
    const res  = await fetch("/api/questions");
    const data = await res.json();
    if (data.questions && data.questions.length > 0) {
      log(`> Found ${data.questions.length} cached questions ✓`, "ok");
      log("> Merging JEE numerical bank…", "ok");
      setTimeout(() => launchQuiz(data.questions), 600);
    } else {
      log("> No cached questions found.", "");
      log("> Press the button below to fetch live PYQs.", "info");
      _stopLoaderRing();
      $fetchBtn.style.display = "flex";
    }
  } catch (e) {
    log(`> Server error: ${e.message}`, "err");
    log("> Ensure Flask (app.py) is running — python app.py", "err");
    _stopLoaderRing();
    $fetchBtn.style.display = "flex";
  }
}

function _stopLoaderRing() {
  $loaderRing.style.animation = "none";
  $loaderRing.style.opacity   = "0.3";
}

/* ═══════════════════════════════════════════════════════════════
   SSE SCRAPE
═══════════════════════════════════════════════════════════════ */
async function startScrape() {
  $fetchBtn.disabled = true;
  $loaderRing.style.animation = "";
  $loaderRing.style.opacity   = "1";

  // Kick off the scrape
  try {
    const r = await fetch("/api/scrape", { method: "POST" });
    if (!r.ok && r.status !== 202) {
      const d = await r.json();
      log(`> ❌ ${d.message || "Failed to start scrape"}`, "err");
      $fetchBtn.disabled = false;
      return;
    }
  } catch (e) {
    log(`> ❌ Network error: ${e.message}`, "err");
    $fetchBtn.disabled = false;
    return;
  }

  // Show SSE progress panel
  $sseProgress.classList.add("show");
  log("> Scrape started — streaming progress…", "info");

  // Open SSE stream
  sseSource = new EventSource("/api/scrape/stream");

  sseSource.addEventListener("progress", e => {
    const d = JSON.parse(e.data);
    $sseBarFill.style.width = d.pct + "%";
    $ssePct.textContent     = d.pct + "%";
    $sseMsg.textContent     = d.msg || "";
    sseLog(d.msg || "");
    if (d.fetched !== undefined) {
      log(`> +${d.fetched} questions`, "ok");
    }
  });

  sseSource.addEventListener("done", e => {
    const d = JSON.parse(e.data);
    sseSource.close();
    $sseBarFill.style.width = "100%";
    $ssePct.textContent     = "100%";
    sseLog(`✅ Done — ${d.count} questions`, "ok");
    log(`> ✅ Fetched ${d.count} questions!`, "ok");
    setTimeout(() => {
      $sseProgress.classList.remove("show");
      launchQuiz(d.questions || []);
    }, 800);
  });

  sseSource.addEventListener("error", e => {
    let msg = "Unknown error";
    try { msg = JSON.parse(e.data).msg; } catch {}
    sseSource.close();
    sseLog(`❌ ${msg}`, "err");
    log(`> ❌ Scrape error: ${msg}`, "err");
    $fetchBtn.disabled = false;
  });

  sseSource.onerror = () => {
    if (sseSource.readyState === EventSource.CLOSED) return;
    sseLog("Connection lost — retrying…");
  };
}

/* ═══════════════════════════════════════════════════════════════
   REFRESH
═══════════════════════════════════════════════════════════════ */
function confirmRefresh() {
  if (!confirm("Re-fetch questions from the internet? This takes ~30–60 seconds.")) return;
  allQ = []; filteredQ = [];
  $quizArea.classList.remove("show");
  $results.classList.remove("show");
  $loader.classList.add("show");
  $loadLog.innerHTML = "";
  $fetchBtn.disabled = false;
  $loaderRing.style.animation = ""; $loaderRing.style.opacity = "1";
  $fetchBtn.style.display = "flex";
  log("> Ready to re-fetch…", "info");
}

/* ═══════════════════════════════════════════════════════════════
   LAUNCH QUIZ
═══════════════════════════════════════════════════════════════ */
function launchQuiz(questions) {
  allQ = [...questions, ...JEE_NUMERICALS];
  $loader.classList.remove("show");
  buildTabs();
  buildChapterDropdown();
  applyFilter("ALL", "ALL");
  $quizArea.classList.add("show");
  $totalQCount.textContent = allQ.length;
  $("downloadHdrBtn").style.display = "flex";
  const sources = [...new Set(allQ.map(q => q.source).filter(Boolean))];
  const srcTxt  = `LIVE — ${sources.join(" + ") || "OpenTDB + JEE Archive"}`;
  $("sourceLabel").textContent     = srcTxt;
  $("sourceLabelQuiz").textContent = srcTxt;
}

/* ═══════════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════════ */
const EXAM_ICONS  = { ALL:"🎯", JEE:"⚛️", NEET:"🧬", UPSC:"🏛️", CAT:"📐", SAT:"🌍", GK:"💡" };
const EXAM_COLORS = { JEE:"#1E3A8A", NEET:"#15803D", UPSC:"#B91C1C", CAT:"#B45309", SAT:"#6D28D9", GK:"#EA580C" };

function buildTabs() {
  const order = ["ALL","JEE","NEET","UPSC","CAT","SAT","GK"];
  const exams  = [...new Set(["ALL", ...allQ.map(q => q.exam).filter(Boolean)])];
  exams.sort((a,b) => (order.indexOf(a)+1||99) - (order.indexOf(b)+1||99));
  $tabsWrap.innerHTML = "";
  exams.forEach(exam => {
    const btn = document.createElement("button");
    btn.className = "tab" + (exam === "ALL" ? " active" : "");
    btn.dataset.exam = exam;
    const count = exam === "ALL" ? allQ.length : allQ.filter(q=>q.exam===exam).length;
    btn.textContent = `${EXAM_ICONS[exam]||"📚"} ${exam} (${count})`;
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
      btn.classList.add("active");
      activeExam = exam;
      buildChapterDropdown();
      applyFilter(exam, "ALL");
    });
    $tabsWrap.appendChild(btn);
  });
}

/* ═══════════════════════════════════════════════════════════════
   CHAPTER DROPDOWN
═══════════════════════════════════════════════════════════════ */
function buildChapterDropdown() {
  if (!$chapterSel) return;
  const pool = activeExam === "ALL" ? allQ : allQ.filter(q=>q.exam===activeExam);
  const chapters = ["ALL", ...new Set(pool.map(q=>q.chapter||"General").filter(Boolean))].sort((a,b)=>a==="ALL"?-1:a.localeCompare(b));
  $chapterSel.innerHTML = chapters.map(c=>`<option value="${c}">${c}</option>`).join("");
  $chapterSel.value = "ALL";
  activeChapter = "ALL";
}

function onChapterChange() {
  activeChapter = $chapterSel.value || "ALL";
  applyFilter(activeExam, activeChapter);
}

/* ═══════════════════════════════════════════════════════════════
   FILTER
═══════════════════════════════════════════════════════════════ */
function applyFilter(exam, chapter) {
  activeExam    = exam;
  activeChapter = chapter;

  let pool = exam === "ALL" ? [...allQ] : allQ.filter(q=>q.exam===exam);
  if (chapter && chapter !== "ALL") {
    pool = pool.filter(q=>(q.chapter||"General")===chapter);
  }

  // Shuffle
  for (let i=pool.length-1; i>0; i--) {
    const j = Math.floor(Math.random()*(i+1));
    [pool[i],pool[j]] = [pool[j],pool[i]];
  }
  filteredQ = pool;
  score = 0; streak = 0; currentIdx = 0;
  answerHistory = [];
  $scoreVal.textContent  = 0;
  $streakVal.textContent = 0;
  $results.classList.remove("show");

  // Timer mode
  startTimerMode();
  renderQuestion();
}

/* ═══════════════════════════════════════════════════════════════
   TIMER MODE
═══════════════════════════════════════════════════════════════ */
function onTimerModeChange() {
  const val = parseInt($timerSel.value) || 0;
  timerModeLimit = val * 60;
  applyFilter(activeExam, activeChapter);
}

function startTimerMode() {
  clearInterval(timerModeInterval);
  if (!timerModeLimit) { $tmBar.classList.remove("show"); return; }
  timerModeRemain = timerModeLimit;
  $tmBar.classList.add("show");
  _updateTimerModeDisplay();
  timerModeInterval = setInterval(() => {
    timerModeRemain--;
    _updateTimerModeDisplay();
    if (timerModeRemain <= 0) {
      clearInterval(timerModeInterval);
      toast("⏰ Time's up!");
      showResults();
    }
  }, 1000);
}

function _updateTimerModeDisplay() {
  const mins = Math.floor(timerModeRemain/60).toString().padStart(2,"0");
  const secs = (timerModeRemain%60).toString().padStart(2,"0");
  $tmCountdown.textContent = `${mins}:${secs}`;
  $tmCountdown.classList.toggle("urgent", timerModeRemain <= 60);
  $tmLabel.textContent = `/${Math.floor(timerModeLimit/60)} min mode`;
}

/* ═══════════════════════════════════════════════════════════════
   RENDER QUESTION
═══════════════════════════════════════════════════════════════ */
function getExamColor(exam) { return EXAM_COLORS[exam] || "#1E3A8A"; }

function renderQuestion() {
  clearInterval(timerInterval);
  if (currentIdx >= filteredQ.length) { showResults(); return; }
  const q = filteredQ[currentIdx];
  selected = null; answered = false;

  // Card accent
  const accent = getExamColor(q.exam);
  $qCard.style.setProperty("--card-accent", accent);

  // Progress
  const pct = Math.round((currentIdx / filteredQ.length) * 100);
  $progFill.style.width  = pct + "%";
  $progLabel.textContent = `Q ${currentIdx+1} / ${filteredQ.length}`;
  $progPct.textContent   = pct + "%";

  $qNumber.textContent = `Question ${currentIdx+1} of ${filteredQ.length}`;

  const isNumerical = q.type === "numerical";
  const isBookmarked = bookmarks.includes(String(q.id || q.question.slice(0,40)));
  $qMeta.innerHTML = `
    <span class="badge badge-exam" style="background:${accent}18;border-color:${accent}30;color:${accent}">${q.exam||"GK"}</span>
    ${isNumerical ? '<span class="badge badge-numerical">🔢 Numerical</span>' : ""}
    <span class="badge badge-subj">${(q.subject||"").split("—").pop().trim()}</span>
    <span class="badge badge-year">${q.year||"Practice"}</span>
    <span class="badge badge-diff ${q.difficulty||"Medium"}">${q.difficulty||"Medium"}</span>
    <button class="btn-bookmark${isBookmarked?" bookmarked":""}" onclick="toggleBookmark('${encodeURIComponent(q.question.slice(0,40))}',this)" title="Bookmark">🔖</button>
    <span class="timer-badge" id="timerBadge">⏱ <span id="timerNum">30</span>s</span>
  `;

  $qText.textContent = q.question;
  $expBox.classList.remove("show");
  $expCorrect.style.display = "none";
  $btnSubmit.disabled = true;
  $btnSubmit.style.display = "";
  $btnNext.style.display   = "none";
  $qCounter.textContent    = `${currentIdx+1} of ${filteredQ.length} · ${filteredQ.length-currentIdx-1} remaining`;

  isNumerical ? renderNumerical(q) : renderMCQ(q);
  injectResourceAd(q.subject || q.exam || "");

  // Animate card in
  $qCard.style.display = "";
  $qCard.style.animation = "none";
  void $qCard.offsetWidth;
  $qCard.style.animation = "";

  // Per-question timer
  timerSec = isNumerical ? 45 : 30;
  updateTimer(timerSec);
  timerInterval = setInterval(() => {
    timerSec--;
    updateTimer(timerSec);
    if (timerSec <= 0) {
      clearInterval(timerInterval);
      if (!answered) { streak=0; $streakVal.textContent=0; revealAndAdvance(); }
    }
  }, 1000);
}

/* ── MCQ ──────────────────────────────────────────────────── */
function renderMCQ(q) {
  $answerArea.innerHTML = '<div class="options" id="optList"></div>';
  const $optList = $("optList");
  Object.keys(q.options||{}).forEach(letter => {
    const div = document.createElement("div");
    div.className = "option";
    div.dataset.letter = letter;
    div.innerHTML = `<div class="opt-key">${letter}</div><div class="opt-text">${q.options[letter]}</div>`;
    div.addEventListener("click", () => selectMCQ(letter));
    $optList.appendChild(div);
  });
}

/* ── Numerical ────────────────────────────────────────────── */
function renderNumerical(q) {
  const unit = q.unit ? `<span style="color:var(--purple-700);font-weight:700">${q.unit}</span>` : "";
  $answerArea.innerHTML = `
    <div class="numerical-wrap">
      <div class="num-label">🔢 Enter your numerical answer ${unit}</div>
      <div class="num-input-row">
        <input type="number" id="numInput" class="numerical-input" placeholder="Type your answer…" step="any" autocomplete="off" />
      </div>
      <div style="font-size:0.78rem;color:var(--text-400)">JEE numericals accept ±0.01 tolerance. Press <strong>Enter</strong> to submit.</div>
    </div>
  `;
  const $ni = $("numInput");
  $ni.addEventListener("input", () => { $btnSubmit.disabled = $ni.value.trim() === ""; });
  $ni.addEventListener("keydown", e => { if (e.key==="Enter" && !$btnSubmit.disabled && !answered) submitAnswer(); });
  $ni.focus();
}

function updateTimer(sec) {
  const el    = $("timerNum");
  const badge = $("timerBadge");
  if (el)    el.textContent = sec;
  if (badge) badge.className = "timer-badge" + (sec<=8 ? " urgent" : "");
}

/* ═══════════════════════════════════════════════════════════════
   SELECT / SUBMIT
═══════════════════════════════════════════════════════════════ */
function selectMCQ(letter) {
  if (answered) return;
  selected = letter;
  document.querySelectorAll(".option").forEach(o => {
    o.classList.toggle("selected", o.dataset.letter === letter);
  });
  $btnSubmit.disabled = false;
}

document.addEventListener("keydown", e => {
  if (answered) return;
  if (["1","2","3","4"].includes(e.key)) {
    const q = filteredQ[currentIdx];
    if (!q || q.type==="numerical") return;
    selectMCQ(["A","B","C","D"][parseInt(e.key)-1]);
  }
  if (e.key==="Enter" && selected && !answered) submitAnswer();
  if (e.key==="ArrowRight" && answered) nextQuestion();
});

function submitAnswer() {
  if (answered) return;
  clearInterval(timerInterval);
  answered = true;
  const q = filteredQ[currentIdx];
  const isNumerical = q.type === "numerical";
  let isCorrect = false;

  if (isNumerical) {
    const $ni = $("numInput");
    const userVal = parseFloat($ni.value);
    const tol     = q.tolerance !== undefined ? q.tolerance : 0.01;
    isCorrect = !isNaN(userVal) && Math.abs(userVal - q.numericalAnswer) <= Math.max(tol, Math.abs(q.numericalAnswer)*0.001+0.01);
    $ni.disabled = true;
    $ni.classList.add(isCorrect ? "correct-input" : "wrong-input");
    $expCorrect.textContent = `✓ Correct answer: ${q.numericalAnswer}${q.unit?" "+q.unit:""}`;
    $expCorrect.style.display = "block";
  } else {
    if (!selected) return;
    isCorrect = selected === q.answer;
    document.querySelectorAll(".option").forEach(o => {
      o.classList.add("locked");
      o.classList.remove("selected");
      if (o.dataset.letter === q.answer) o.classList.add("correct");
      else if (o.dataset.letter === selected && !isCorrect) o.classList.add("wrong");
    });
  }

  answerHistory.push(isCorrect ? "correct" : "wrong");

  if (isCorrect) {
    score++; streak++;
    $scoreVal.textContent  = score;
    $streakVal.textContent = streak;
    if (streak >= 3) spawnConfetti($qCard);
  } else {
    streak = 0; $streakVal.textContent = 0;
  }

  $expText.textContent = q.explanation || "No explanation available.";
  $expBox.classList.add("show");
  $btnSubmit.style.display = "none";
  $btnNext.style.display   = "";
  updateChart();
}

function revealAndAdvance() {
  answered = true;
  const q = filteredQ[currentIdx];
  answerHistory.push("skipped");
  if (q.type !== "numerical") {
    document.querySelectorAll(".option").forEach(o => {
      o.classList.add("locked");
      if (o.dataset.letter === q.answer) o.classList.add("reveal");
    });
  } else {
    const $ni = $("numInput");
    if ($ni) $ni.disabled = true;
    $expCorrect.textContent = `✓ Correct answer: ${q.numericalAnswer}${q.unit?" "+q.unit:""}`;
    $expCorrect.style.display = "block";
  }
  $expText.textContent = q.explanation || "";
  $expBox.classList.add("show");
  $btnSubmit.style.display = "none";
  $btnNext.style.display   = "";
  streak=0; $streakVal.textContent=0;
  updateChart();
}

function nextQuestion() { currentIdx++; renderQuestion(); }
function skipQuestion()  {
  clearInterval(timerInterval);
  answerHistory.push("skipped");
  streak=0; $streakVal.textContent=0;
  currentIdx++; renderQuestion();
}

/* ═══════════════════════════════════════════════════════════════
   BOOKMARKS
═══════════════════════════════════════════════════════════════ */
function toggleBookmark(encodedKey, btn) {
  const key = decodeURIComponent(encodedKey);
  const idx = bookmarks.indexOf(key);
  if (idx === -1) {
    bookmarks.push(key);
    btn.classList.add("bookmarked");
    toast("🔖 Bookmarked!");
  } else {
    bookmarks.splice(idx,1);
    btn.classList.remove("bookmarked");
    toast("Bookmark removed.");
  }
  localStorage.setItem("qf_bookmarks", JSON.stringify(bookmarks));
}

function showBookmarks() {
  const panel = $("bookmarksPanel");
  const list  = $("bookmarksList");
  panel.classList.toggle("show");
  if (!panel.classList.contains("show")) return;

  const bqList = allQ.filter(q => bookmarks.includes(String(q.id||q.question.slice(0,40))));
  if (!bqList.length) {
    list.innerHTML = '<div class="bookmark-empty">No bookmarks yet — click 🔖 on any question!</div>';
    return;
  }
  list.innerHTML = bqList.map((q,i)=>`
    <div class="bookmark-item" onclick="jumpToQuestion('${encodeURIComponent(q.question.slice(0,40))}')">
      <strong>Q${i+1}.</strong> ${q.question.slice(0,80)}…
    </div>
  `).join("");
}

function jumpToQuestion(encodedQ) {
  const qText = decodeURIComponent(encodedQ);
  const idx   = filteredQ.findIndex(q => q.question.slice(0,40) === qText);
  if (idx >= 0) { currentIdx = idx; renderQuestion(); }
  $("bookmarksPanel").classList.remove("show");
}

/* ═══════════════════════════════════════════════════════════════
   PROGRESS CHART  (pure CSS bars)
═══════════════════════════════════════════════════════════════ */
function updateChart() {
  if (!$chartWrap) return;
  const last10 = answerHistory.slice(-10);
  if (!last10.length) return;
  $chartWrap.classList.add("show");
  const bars = $("chartBars");
  if (!bars) return;

  const maxH = 68;
  const total = last10.length;
  bars.innerHTML = last10.map((r,i)=>`
    <div class="chart-bar-wrap">
      <div class="chart-bar ${r}" style="height:${maxH*(i+1)/total}px" title="${r}"></div>
      <div class="chart-bar-label">${i+1}</div>
    </div>
  `).join("");
}

/* ═══════════════════════════════════════════════════════════════
   RESULTS
═══════════════════════════════════════════════════════════════ */
function showResults() {
  clearInterval(timerInterval);
  clearInterval(timerModeInterval);
  $qCard.style.display = "none";
  $results.classList.add("show");
  $progFill.style.width = "100%";

  const pct   = filteredQ.length ? Math.round((score/filteredQ.length)*100) : 0;
  const emoji = pct===100?"🏆":pct>=80?"🎉":pct>=60?"💪":pct>=40?"📚":"😤";
  const title = pct===100?"Flawless!":pct>=80?"Outstanding!":pct>=60?"Well Done!":pct>=40?"Keep Going!":"Back to Books!";

  $("resEmoji").textContent = emoji;
  $("resTitle").textContent = title;
  $("resSub").textContent   = `${score} of ${filteredQ.length} correct — ${pct}% accuracy`;
  $("ringArc").style.setProperty("--pct", pct);
  $("ringNum").textContent  = `${score}/${filteredQ.length}`;

  const numQ = filteredQ.filter(q=>q.type==="numerical").length;
  $("resStatsRow").innerHTML = `
    <div class="res-stat"><span class="res-stat-val">${pct}%</span><div class="res-stat-lbl">Accuracy</div></div>
    <div class="res-stat"><span class="res-stat-val">${score}</span><div class="res-stat-lbl">Correct</div></div>
    <div class="res-stat"><span class="res-stat-val">${filteredQ.length-score}</span><div class="res-stat-lbl">Incorrect</div></div>
    <div class="res-stat"><span class="res-stat-val">${filteredQ.length-numQ}</span><div class="res-stat-lbl">MCQ</div></div>
    ${numQ>0?`<div class="res-stat"><span class="res-stat-val">${numQ}</span><div class="res-stat-lbl">Numerical</div></div>`:""}
  `;
  if (pct===100) setTimeout(()=>spawnConfetti(null),300);
}

function restartQuiz() {
  $results.classList.remove("show");
  applyFilter(activeExam, activeChapter);
}

/* ═══════════════════════════════════════════════════════════════
   DOWNLOAD  — WhatsApp gate for PDF
═══════════════════════════════════════════════════════════════ */
function openDownload() {
  if (!filteredQ.length) { toast("⚠️ No questions loaded yet."); return; }
  $("downloadModal").classList.add("open");
}
function closeDownload() { $("downloadModal").classList.remove("open"); }
$("downloadModal").addEventListener("click", e => { if (e.target === $("downloadModal")) closeDownload(); });

function downloadJSON() {
  const exam = activeExam==="ALL" ? "All_Exams" : activeExam;
  const blob = new Blob([JSON.stringify({
    generated: new Date().toISOString(), exam: activeExam,
    count: filteredQ.length,
    questions: filteredQ.map((q,i)=>({
      number:i+1, exam:q.exam, subject:q.subject, chapter:q.chapter||"",
      year:q.year, difficulty:q.difficulty, type:q.type||"mcq",
      marks:q.marks||1, negative_marks:q.negative_marks||0,
      question:q.question,
      ...(q.type==="numerical"?{answer:q.numericalAnswer,unit:q.unit}:{options:q.options,answer:q.answer}),
      explanation:q.explanation
    }))
  }, null, 2)], {type:"application/json"});
  _triggerDownload(blob, `QuizForge_${exam}.json`);
  closeDownload(); toast("✅ JSON downloaded!");
}

function downloadCSV() {
  const exam = activeExam==="ALL" ? "All_Exams" : activeExam;
  const rows = [["#","Exam","Subject","Chapter","Year","Difficulty","Type","Question","Answer/Options","Explanation"]];
  filteredQ.forEach((q,i)=>{
    const ansStr = q.type==="numerical"
      ? `${q.numericalAnswer}${q.unit?" "+q.unit:""}`
      : `A:${q.options?.A||""} B:${q.options?.B||""} C:${q.options?.C||""} D:${q.options?.D||""} Correct:${q.answer}`;
    rows.push([i+1,q.exam,q.subject,q.chapter||"",q.year,q.difficulty,q.type||"mcq",
      `"${(q.question||"").replace(/"/g,'""')}"`,
      `"${ansStr.replace(/"/g,'""')}"`,
      `"${(q.explanation||"").replace(/"/g,'""')}"`]);
  });
  const blob = new Blob([rows.map(r=>r.join(",")).join("\n")], {type:"text/csv"});
  _triggerDownload(blob, `QuizForge_${exam}.csv`);
  closeDownload(); toast("✅ CSV downloaded!");
}

/* WhatsApp gate for PDF */
function downloadPDF() {
  closeDownload();
  const waKey = "qf_wa_shared";
  const lastShare = parseInt(localStorage.getItem(waKey)||"0");
  const now = Date.now();

  // Re-check every 24 h
  if (now - lastShare < 86400000) {
    _doPrintPDF(); return;
  }

  // Show WhatsApp share gate
  const overlay = $("waModal");
  overlay.classList.add("open");
  const fill = $("waProgressFill");
  const btn  = $("waContinueBtn");
  btn.disabled = true;
  fill.style.width = "0";

  // Open WhatsApp
  const shareText = encodeURIComponent("📚 I'm using QuizForge to practice PYQs! Try it at localhost:5000");
  window.open(`https://wa.me/?text=${shareText}`, "_blank");

  // 4s countdown
  setTimeout(() => { fill.style.width = "100%"; }, 50);
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = "✅ Download PDF Now";
  }, 4000);
}

function onWaContinue() {
  localStorage.setItem("qf_wa_shared", String(Date.now()));
  $("waModal").classList.remove("open");
  _doPrintPDF();
}

function closeWaModal() { $("waModal").classList.remove("open"); }

function _doPrintPDF() {
  const exam = activeExam==="ALL" ? "All Exams" : activeExam;
  const win  = window.open("", "_blank");
  if (!win) { toast("⚠️ Pop-up blocked — allow pop-ups and retry."); return; }
  let html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>QuizForge — ${exam}</title>
  <style>
    body{font-family:Georgia,serif;max-width:760px;margin:40px auto;padding:0 24px;color:#1C1917;line-height:1.7}
    h1{font-size:2rem;color:#1E3A8A;border-bottom:3px solid #1E3A8A;padding-bottom:12px;margin-bottom:6px}
    .meta{font-size:0.8rem;color:#78716C;margin-bottom:32px;font-family:monospace}
    .q-block{margin-bottom:28px;padding-bottom:22px;border-bottom:1px solid #E8DCC8;break-inside:avoid}
    .q-num{font-size:0.7rem;font-family:monospace;color:#A8A29E;text-transform:uppercase;letter-spacing:0.1em}
    .q-text{font-size:1.05rem;font-weight:600;color:#1C1917;margin:6px 0 10px}
    .opt{margin:3px 0 3px 16px;font-size:0.9rem}
    .opt .key{font-family:monospace;font-weight:700;color:#44403C;min-width:22px;display:inline-block}
    .answer{margin-top:6px;font-size:0.8rem;color:#15803D;font-weight:700;font-family:monospace}
    .exp{margin-top:7px;font-size:0.8rem;color:#44403C;font-style:italic;background:#EFF6FF;padding:7px 12px;border-radius:6px;border-left:3px solid #3B82F6}
    @media print{body{margin:20px}}
  </style></head><body>
  <h1>🎯 QuizForge — ${exam}</h1>
  <div class="meta">Generated: ${new Date().toLocaleString()} · ${filteredQ.length} Questions · QuizForge v3.0</div>`;

  filteredQ.forEach((q,i)=>{
    html += `<div class="q-block"><div class="q-num">Question ${i+1} · ${q.exam||""} · ${q.difficulty||""} · ${q.year||""}</div>
    <div class="q-text">${q.question}</div>`;
    if (q.type==="numerical") {
      html += `<div class="opt">Numerical answer — enter value${q.unit?" ("+q.unit+")":""}</div>
      <div class="answer">Answer: ${q.numericalAnswer}${q.unit?" "+q.unit:""}</div>`;
    } else if (q.options) {
      html += Object.entries(q.options).map(([k,v])=>`<div class="opt"><span class="key">${k}.</span> ${v}${k===q.answer?" ✓":""}</div>`).join("");
      html += `<div class="answer">Correct: ${q.answer}</div>`;
    }
    if (q.explanation) html += `<div class="exp">${q.explanation}</div>`;
    html += "</div>";
  });
  html += "</body></html>";
  win.document.open(); win.document.write(html); win.document.close();
  setTimeout(()=>win.print(), 600);
  toast("🖨️ Opening print dialog…");
}

function _triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a   = Object.assign(document.createElement("a"), { href:url, download:filename });
  a.click();
  URL.revokeObjectURL(url);
}

/* ═══════════════════════════════════════════════════════════════
   RESOURCE AD
═══════════════════════════════════════════════════════════════ */
const AD_BOOKS = {
  jee:  { emoji:"⚛️", title:"Concepts of Physics", author:"H.C. Verma", why:"Gold-standard JEE Physics — every concept from first principles.", amazon:"https://www.amazon.in/s?k=hc+verma+concepts+of+physics", bg:"linear-gradient(135deg,#1E3A8A,#3B82F6)" },
  neet: { emoji:"🧬", title:"NCERT at your Fingertips — Biology", author:"MTG Editorial", why:"Chapter-wise MCQs mapped to NCERT — the NEET Bible.", amazon:"https://www.amazon.in/s?k=ncert+fingertips+biology+mtg", bg:"linear-gradient(135deg,#15803D,#22C55E)" },
  upsc: { emoji:"🏛️", title:"Indian Polity", author:"M. Laxmikanth", why:"The single most important UPSC Polity book — on every aspirant's list.", amazon:"https://www.amazon.in/s?k=laxmikanth+indian+polity", bg:"linear-gradient(135deg,#B91C1C,#EF4444)" },
  cat:  { emoji:"📐", title:"Quantitative Aptitude", author:"Arun Sharma", why:"Definitive CAT Quant resource — shortcuts + graded practice.", amazon:"https://www.amazon.in/s?k=arun+sharma+quantitative+aptitude+cat", bg:"linear-gradient(135deg,#B45309,#D97706)" },
  gk:   { emoji:"🌐", title:"Manorama Yearbook 2026", author:"Mammen Mathew", why:"India's best-selling almanac — GK for all competitive exams.", amazon:"https://www.amazon.in/s?k=manorama+yearbook+2026", bg:"linear-gradient(135deg,#EA580C,#FB923C)" },
};

function injectResourceAd(subject) {
  const $ad = $("adContainer");
  if (!$ad) return;
  const s = (subject||"").toUpperCase();
  let book;
  if (s.includes("JEE")||s.includes("PHYSICS")||s.includes("MATH")||s.includes("CHEM")) book=AD_BOOKS.jee;
  else if (s.includes("NEET")||s.includes("BIOL")||s.includes("ZOO")) book=AD_BOOKS.neet;
  else if (s.includes("UPSC")||s.includes("POLITY")||s.includes("HIST")||s.includes("GEO")) book=AD_BOOKS.upsc;
  else if (s.includes("CAT")||s.includes("APTITUDE")||s.includes("QUANT")) book=AD_BOOKS.cat;
  else book=AD_BOOKS.gk;

  $ad.innerHTML = `
    <div class="resource-ad-card" role="complementary">
      <button class="ad-dismiss" onclick="this.closest('.resource-ad-card').remove()">✕</button>
      <div class="ad-cover" style="background:${book.bg}"><span>${book.emoji}</span></div>
      <div class="ad-body">
        <div class="ad-label">✦ Curated for this topic</div>
        <div class="ad-title">${book.title}</div>
        <div class="ad-author">${book.author}</div>
        <div class="ad-why">${book.why}</div>
      </div>
      <a class="ad-cta" href="${book.amazon}" target="_blank" rel="noopener noreferrer">View on Amazon 🛒</a>
    </div>`;
}

/* ═══════════════════════════════════════════════════════════════
   CONFETTI  (fixed DOM leak — elements self-remove)
═══════════════════════════════════════════════════════════════ */
const CONFETTI_COLORS = ["#1E3A8A","#EA580C","#6D28D9","#D97706","#15803D","#F97316","#3B82F6"];
function spawnConfetti(anchor) {
  const count = anchor ? 28 : 90;
  const frag  = document.createDocumentFragment();
  for (let i=0; i<count; i++) {
    const p = document.createElement("div");
    p.className = "confetti-piece";
    const rect = anchor
      ? anchor.getBoundingClientRect()
      : { left:window.innerWidth/2-100, top:window.innerHeight/4, width:200 };
    const dur  = (1.8 + Math.random()*1.4).toFixed(2);
    const del  = (Math.random()*0.5).toFixed(2);
    p.style.cssText = `
      left:${rect.left + Math.random()*Math.max(rect.width,200)}px;
      top:${rect.top}px;
      background:${CONFETTI_COLORS[Math.floor(Math.random()*CONFETTI_COLORS.length)]};
      animation-duration:${dur}s;
      animation-delay:${del}s;
      transform:rotate(${Math.random()*360}deg);
      border-radius:${Math.random()>0.5?"50%":"2px"};
      width:${6+Math.random()*6}px;
      height:${6+Math.random()*6}px;
    `;
    // Self-remove after animation ends (no leak)
    p.addEventListener("animationend", () => p.remove(), { once: true });
    frag.appendChild(p);
  }
  document.body.appendChild(frag);
}

/* ═══════════════════════════════════════════════════════════════
   MUSIC PLAYER
═══════════════════════════════════════════════════════════════ */
const TRACKS = [
  { name:"Lo-Fi Study Beats",  src:"iloveradio",    emoji:"🎵", url:"https://streams.ilovemusic.de/iloveradio17.mp3",  type:"radio" },
  { name:"Chill Jazz Café",    src:"JazzGroove",    emoji:"🎷", url:"https://jzgroove.streamguys1.com/jazzgroove-dash",type:"radio" },
  { name:"Classical Focus",    src:"Klassik Radio", emoji:"🎻", url:"https://stream.klassikradio.de/klassikradio/mp3-128/stream.klassikradio.de/", type:"radio" },
  { name:"Synthwave Night",    src:"iloveradio",    emoji:"🌃", url:"https://streams.ilovemusic.de/iloveradio2.mp3",   type:"radio" },
  { name:"Lo-Fi Ambient Synth",src:"Built-in",      emoji:"🌊", url:"SYNTH", type:"synth" },
];

let trackIdx=0, isPlaying=false, audioCtx=null, synthGain=null, synthInterval=null;
const $audio    = $("audioEl");
const $btnPlay  = $("btnPlay");
const $disc     = $("disc");
const $tName    = $("trackName");
const $tSrc     = $("trackSrc");
const $eq       = $("eqBars");
const $vol      = $("volSlider");
const $mStatus  = $("musicStatus");

$audio.volume = 0.5;

function _initAudio() {
  if (audioCtx) return;
  audioCtx   = new (window.AudioContext||window.webkitAudioContext)();
  synthGain  = audioCtx.createGain(); synthGain.gain.value = 0.18;
  const f    = audioCtx.createBiquadFilter(); f.type="lowpass"; f.frequency.value=900;
  synthGain.connect(f); f.connect(audioCtx.destination);
}
function _playNote(freq,start,dur,vol=0.11) {
  if (!audioCtx) return;
  const o=audioCtx.createOscillator(), g=audioCtx.createGain();
  o.type="sine"; o.frequency.setValueAtTime(freq,start);
  g.gain.setValueAtTime(0,start);
  g.gain.linearRampToValueAtTime(vol,start+0.18);
  g.gain.setValueAtTime(vol,start+dur-0.3);
  g.gain.linearRampToValueAtTime(0,start+dur);
  o.connect(g); g.connect(synthGain); o.start(start); o.stop(start+dur);
}
const CHORDS=[[261.63,329.63,392],[220,261.63,329.63],[174.61,220,261.63],[196,246.94,293.66]];
let _chordIdx=0;
function _startSynth() {
  _initAudio();
  if (audioCtx.state==="suspended") audioCtx.resume();
  function chord() {
    if (!isPlaying) return;
    const now=audioCtx.currentTime, c=CHORDS[_chordIdx%CHORDS.length];
    c.forEach((f,i)=>_playNote(f*0.5,now+i*0.07,3.5,0.09));
    _playNote(c[2]*2,now+0.5,1.2,0.055); _playNote(c[0]*2,now+2,0.9,0.05);
    _chordIdx++;
  }
  chord(); synthInterval=setInterval(chord,4200);
}
function _stopSynth() { clearInterval(synthInterval); synthInterval=null; }

function loadTrack(idx, autoplay=false) {
  const t=$tName; const ts=$tSrc; const de=$disc.querySelector(".disc-emoji");
  const tr = TRACKS[idx];
  t.textContent  = tr.name;
  ts.textContent = tr.src;
  de.textContent = tr.emoji;
  if (tr.type==="synth") {
    $audio.pause(); $audio.src="";
    $mStatus.textContent="SYNTH"; $mStatus.className="music-status synth";
    if (autoplay) { isPlaying=true; _startSynth(); _setPlayUI(true); }
  } else {
    $mStatus.textContent="RADIO"; $mStatus.className="music-status";
    _stopSynth(); $audio.src=tr.url;
    if (autoplay) { $audio.play().then(()=>_setPlayUI(true)).catch(()=>{trackIdx=TRACKS.length-1;loadTrack(trackIdx,true);}); }
  }
}
function _setPlayUI(p) {
  isPlaying=p; $btnPlay.textContent=p?"⏸":"▶";
  $disc.classList.toggle("playing",p); $eq.classList.toggle("active",p);
}
function togglePlay() {
  const tr=TRACKS[trackIdx];
  if (tr.type==="synth") { isPlaying?_stopSynth():_startSynth(); _setPlayUI(!isPlaying); return; }
  if ($audio.paused) {
    if (!$audio.src) loadTrack(trackIdx);
    $audio.play().then(()=>_setPlayUI(true)).catch(()=>{trackIdx=TRACKS.length-1;loadTrack(trackIdx,true);});
  } else { $audio.pause(); _setPlayUI(false); }
}
function prevTrack() { _stopSynth(); trackIdx=(trackIdx-1+TRACKS.length)%TRACKS.length; loadTrack(trackIdx,isPlaying); }
function nextTrack() { _stopSynth(); trackIdx=(trackIdx+1)%TRACKS.length; loadTrack(trackIdx,isPlaying); }
function setVol(v)   { $audio.volume=v/100; if(synthGain) synthGain.gain.value=(v/100)*0.22; }
$audio.addEventListener("ended", nextTrack);
$audio.addEventListener("error", ()=>{if(trackIdx<TRACKS.length-1){trackIdx++;loadTrack(trackIdx,true);}else{trackIdx=TRACKS.length-1;loadTrack(trackIdx,true);}});
loadTrack(trackIdx, false);

/* ═══════════════════════════════════════════════════════════════
   TOAST
═══════════════════════════════════════════════════════════════ */
function toast(msg, ms=4200) {
  document.querySelectorAll(".toast").forEach(t=>t.remove());
  const el = document.createElement("div");
  el.className="toast"; el.textContent=msg;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(), ms);
}

/* ═══════════════════════════════════════════════════════════════
   BOOT
═══════════════════════════════════════════════════════════════ */
init();
setTimeout(()=>toast("⚡ Keys 1–4 select · Enter confirm · → next"),2500);