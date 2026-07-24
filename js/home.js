import { LEVELS } from "./config.js";
import { getUser, signInWithGoogle, signOut, listProgress } from "./data-client.js";

let currentLevel = LEVELS[0];
let manifest = { days: [] };   // 來自 index.json 的輕量清單（含各篇摘要，無全文）
let progress = new Map();      // article_id -> {score, total}（已完成的測驗）

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

// 只讀清單即可渲染，切分頁是純前端運算、不再逐日抓內容
function renderList() {
  const main = document.getElementById("list");
  const cards = [];
  for (const day of manifest.days) {
    for (const art of day.articles) {
      if (art.level !== currentLevel) continue;
      const src = art.source === "real"
        ? `${art.origin_name} · ${art.level_label}` : `AI 生成 · ${art.level_label}`;
      const done = progress.get(art.id);
      const badge = done ? `<span class="badge-done">✓ ${done.score}/${done.total}</span>` : "";
      cards.push(`<a class="card${done ? " done" : ""}" href="reader.html?date=${day.date}&id=${encodeURIComponent(art.id)}">
        <div class="card-title">${art.title}${badge}</div>
        <div class="card-meta">${day.date} · ${src}</div></a>`);
    }
  }
  main.innerHTML = cards.length ? cards.join("") : "這個等級目前沒有內容";
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
  const main = document.getElementById("list");
  main.innerHTML = "載入中…";
  try {
    const resp = await fetch("content/index.json");
    manifest = resp.ok ? await resp.json() : { days: [] };
  } catch {
    manifest = { days: [] };
  }
  if (!Array.isArray(manifest.days)) manifest = { days: [] };
  renderTabs();
  await renderAuth();
  try {
    const prog = await listProgress();
    progress = new Map(prog.map((p) => [p.article_id, p]));
  } catch { progress = new Map(); }
  renderList();
  if (!manifest.days.length) main.innerHTML = "目前無法載入內容，請稍後再試。";
}

init();
