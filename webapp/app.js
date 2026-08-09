const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();
tg?.setHeaderColor?.('#0D1117');
tg?.setBackgroundColor?.('#0D1117');

const initData = tg?.initData || "";
const userId = tg?.initDataUnsafe?.user?.id || demoUserId();

function demoUserId() {
  let id = sessionStorage.getItem("demo_uid");
  if (!id) {
    id = String(900000000 + Math.floor(Math.random() * 99999999));
    sessionStorage.setItem("demo_uid", id);
  }
  return Number(id);
}

const state = {
  screenIndex: 0,
  screens: ["welcome", "level", "language", "dashboard"],
  level: null,
  language: null,
  hp: 5,
  xp: 0,
  premium: false,
  priceStars: 150,
};

const LANG_ICONS = {
  "Python": "🐍", "JavaScript": "🟨", "HTML/CSS": "🌐", "C++": "➕",
  "Java": "☕", "C#": "🎯", "Kotlin": "🟣", "Swift": "🕊️",
  "Go": "🐹", "Rust": "⚙️", "PHP": "🐘", "SQL": "🗄️",
};

async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  if (initData) headers["X-Init-Data"] = initData;
  const res = await fetch(path, { ...opts, headers });
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return res.json();
}

function goToScreen(name) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.querySelector(`.screen[data-screen="${name}"]`).classList.add("active");

  const idx = state.screens.indexOf(name);
  document.querySelectorAll(".onboard-steps .step").forEach((el, i) => {
    el.classList.toggle("active", i === idx);
    el.classList.toggle("done", i < idx);
  });
  document.getElementById("onboardSteps").style.display = (name === "dashboard") ? "none" : "flex";
}

function haptic(type = "light") {
  tg?.HapticFeedback?.impactOccurred?.(type);
}

document.getElementById("levelList").addEventListener("click", (e) => {
  const card = e.target.closest(".option-card");
  if (!card) return;
  document.querySelectorAll("#levelList .option-card").forEach(c => c.classList.remove("selected"));
  card.classList.add("selected");
  state.level = card.dataset.value;
  document.querySelector('.screen[data-screen="level"] [data-next]').disabled = false;
  haptic();
});

function renderLangGrid() {
  const grid = document.getElementById("langGrid");
  grid.innerHTML = "";
  META.languages.forEach(lang => {
    const card = document.createElement("button");
    card.className = "lang-card";
    card.dataset.value = lang;
    card.innerHTML = `<span class="lang-chip">${LANG_ICONS[lang] || "💻"}</span>${lang}`;
    grid.appendChild(card);
  });
}
document.getElementById("langGrid").addEventListener("click", (e) => {
  const card = e.target.closest(".lang-card");
  if (!card) return;
  document.querySelectorAll("#langGrid .lang-card").forEach(c => c.classList.remove("selected"));
  card.classList.add("selected");
  state.language = card.dataset.value;
  document.querySelector('.screen[data-screen="language"] [data-next]').disabled = false;
  haptic();
});

document.getElementById("btnStart").addEventListener("click", () => {
  state.screenIndex = 1;
  goToScreen("level");
});

document.querySelectorAll("[data-next]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const current = state.screens[state.screenIndex];
    if (current === "level") {
      await api(`/api/user/${userId}/level`, { method: "POST", body: JSON.stringify({ level: state.level }) });
      state.screenIndex = 2;
      goToScreen("language");
    } else if (current === "language") {
      await api(`/api/user/${userId}/language`, { method: "POST", body: JSON.stringify({ language: state.language }) });
      state.screenIndex = 3;
      goToScreen("dashboard");
      await enterDashboard();
    }
  });
});

document.querySelectorAll("[data-back]").forEach(btn => {
  btn.addEventListener("click", () => {
    state.screenIndex = Math.max(0, state.screenIndex - 1);
    goToScreen(state.screens[state.screenIndex]);
  });
});

function renderHp() {
  const bar = document.getElementById("hpBar");
  if (state.premium) {
    bar.innerHTML = `<span class="hp-infinite">∞</span>`;
  } else {
    let html = "";
    for (let i = 0; i < 5; i++) {
      html += `<span class="hp-block ${i < state.hp ? "" : "empty"}">▮</span>`;
    }
    bar.innerHTML = html;
  }
  document.getElementById("xpBadge").textContent = `${state.xp} XP`;
  document.getElementById("premiumPill").hidden = !state.premium;
  document.getElementById("outOfHp").hidden = state.premium || state.hp > 0;
  document.getElementById("lessonCard").style.opacity = (!state.premium && state.hp <= 0) ? 0.35 : 1;
}

async function enterDashboard() {
  document.getElementById("dashLang").textContent = state.language || "—";
  const user = await api(`/api/user/${userId}`);
  state.hp = user.hp;
  state.xp = user.xp;
  state.premium = user.premium;
  renderHp();
  renderLesson();
}

const LESSON_BANK = {
  "Python": [
    { q: "Что выведет:\nprint(2 ** 3)", options: ["6", "8", "9", "ошибка"], correct: 1 },
    { q: "Как объявить список в Python?", options: ["list = ()", "list = []", "list = {}", "list = <>"], correct: 1 },
  ],
  "JavaScript": [
    { q: "Что выведет:\nconsole.log(typeof [])", options: ["'array'", "'object'", "'list'", "'undefined'"], correct: 1 },
    { q: "Как объявить константу?", options: ["var x = 1", "let x = 1", "const x = 1", "int x = 1"], correct: 2 },
  ],
  "HTML/CSS": [
    { q: "Тег для самой важной ссылки на странице?", options: ["<link>", "<a>", "<href>", "<url>"], correct: 1 },
  ],
  "C++": [
    { q: "Какой оператор выводит текст в консоль?", options: ["print()", "echo", "cout <<", "console.log"], correct: 2 },
  ],
};

function pickLesson(lang) {
  const bank = LESSON_BANK[lang] || LESSON_BANK["Python"];
  return bank[Math.floor(Math.random() * bank.length)];
}

function renderLesson() {
  const lesson = pickLesson(state.language);
  document.getElementById("lessonQ").textContent = lesson.q;
  const wrap = document.getElementById("lessonAnswers");
  wrap.innerHTML = "";
  lesson.options.forEach((opt, i) => {
    const b = document.createElement("button");
    b.className = "answer-btn";
    b.textContent = opt;
    b.addEventListener("click", () => handleAnswer(i === lesson.correct, b, wrap));
    wrap.appendChild(b);
  });
}

async function handleAnswer(correct, btnEl, wrap) {
  if (!state.premium && state.hp <= 0) return;
  wrap.querySelectorAll(".answer-btn").forEach(b => b.disabled = true);
  btnEl.classList.add(correct ? "correct" : "wrong");
  haptic(correct ? "light" : "heavy");

  const res = await api(`/api/user/${userId}/answer`, { method: "POST", body: JSON.stringify({ correct }) });
  state.hp = res.hp;
  state.xp = res.xp;
  renderHp();

  setTimeout(() => {
    if (!state.premium && state.hp <= 0) return;
    renderLesson();
  }, 700);
}

document.getElementById("btnGoPremium").addEventListener("click", async () => {
  const { link } = await api("/api/create_invoice", { method: "POST", body: JSON.stringify({ user_id: userId }) });
  if (tg?.openInvoice) {
    tg.openInvoice(link, async (status) => {
      if (status === "paid") {
        const user = await api(`/api/user/${userId}`);
        state.hp = user.hp;
        state.premium = user.premium;
        renderHp();
        renderLesson();
      }
    });
  } else {
    window.open(link, "_blank");
  }
});

let META = { languages: [], levels: [], premium_price_stars: 150 };

(async function init() {
  META = await api("/api/meta");
  document.getElementById("priceStars").textContent = META.premium_price_stars;
  renderLangGrid();
  goToScreen("welcome");
})();
