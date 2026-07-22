import { LEVELS } from "./config.js";
import { listVocab } from "./data-client.js";
import { pronounce } from "./speak.js";

let all = [];
let filter = "全部";

function render() {
  const main = document.getElementById("vocab-list");
  const rows = all.filter((w) => filter === "全部" || (w.level && w.level.includes(filter)));
  if (!rows.length) { main.innerHTML = "還沒有收藏單字。"; return; }
  main.innerHTML = rows.map((w) => `<div class="card">
    <div class="card-title">${w.word} <button class="say" title="發音">🔊</button> <i>${w.pos || ""}</i> — ${w.zh || ""}</div>
    <div class="card-meta">${w.example || ""}${w.example_zh ? "<br>" + w.example_zh : ""}${w.level ? " · " + w.level : ""}</div>
  </div>`).join("");
  const buttons = main.querySelectorAll(".say");
  rows.forEach((w, i) => { if (buttons[i]) buttons[i].onclick = () => pronounce(w.word); });
}

function renderFilter() {
  const el = document.getElementById("filter");
  const opts = ["全部", ...LEVELS];
  el.innerHTML = "";
  for (const o of opts) {
    const b = document.createElement("button");
    b.textContent = o;
    b.className = o === filter ? "tab active" : "tab";
    b.onclick = () => { filter = o; renderFilter(); render(); };
    el.appendChild(b);
  }
}

async function init() {
  all = await listVocab();
  renderFilter();
  render();
}

init();
