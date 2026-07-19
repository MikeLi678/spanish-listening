import { LEVELS } from "./config.js";
import { articlesForLevel } from "./content.js";
import { getUser, signInWithGoogle, signOut } from "./data-client.js";

let currentLevel = LEVELS[0];
let index = { dates: [] };

async function loadDay(date) {
  const resp = await fetch(`content/${date}.json`);
  if (!resp.ok) return null;
  return resp.json();
}

function renderTabs() {
  const el = document.getElementById("tabs");
  el.innerHTML = "";
  for (const lvl of LEVELS) {
    const b = document.createElement("button");
    b.textContent = lvl;
    b.className = lvl === currentLevel ? "tab active" : "tab";
    b.onclick = () => { currentLevel = lvl; renderTabs(); renderList(); };
    el.appendChild(b);
  }
}

async function renderList() {
  const main = document.getElementById("list");
  main.innerHTML = "載入中…";
  const cards = [];
  for (const date of index.dates) {
    const day = await loadDay(date);
    if (!day) continue;
    for (const art of articlesForLevel(day, currentLevel)) {
      const src = art.source === "real"
        ? `${art.origin_name} · ${art.level_label}` : `AI 生成 · ${art.level_label}`;
      cards.push(`<a class="card" href="reader.html?date=${date}&id=${encodeURIComponent(art.id)}">
        <div class="card-title">${art.title}</div>
        <div class="card-meta">${date} · ${src}</div></a>`);
    }
  }
  main.innerHTML = cards.length ? cards.join("") : "今天這個等級沒有新內容";
}

async function renderAuth() {
  const el = document.getElementById("auth");
  const user = await getUser();
  if (user) {
    el.innerHTML = `<span>${user.email}</span> <button id="out">登出</button>`;
    document.getElementById("out").onclick = () => signOut().then(() => location.reload());
  } else {
    el.innerHTML = `<button id="in">登入以同步</button>`;
    document.getElementById("in").onclick = () => signInWithGoogle();
  }
}

async function init() {
  const resp = await fetch("content/index.json");
  index = resp.ok ? await resp.json() : { dates: [] };
  renderTabs();
  await renderAuth();
  await renderList();
}

init();
