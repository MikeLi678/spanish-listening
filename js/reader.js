import { findArticle } from "./content.js";
import { markWords } from "./vocab-render.js";
import { scoreQuiz } from "./quiz.js";
import { saveProgress, saveVocab } from "./data-client.js";

const params = new URLSearchParams(location.search);
const date = params.get("date");
const id = params.get("id");
let article = null;
let rate = 1;

function speak(text) {
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "es-ES";
  u.rate = rate;
  const voice = window.speechSynthesis.getVoices().find((v) => v.lang.startsWith("es"));
  if (voice) u.voice = voice;
  else alert("此瀏覽器沒有西語語音，文字閱讀仍可使用。");
  window.speechSynthesis.speak(u);
}

function showPopup(word) {
  const el = document.getElementById("popup");
  el.className = "popup";
  el.innerHTML = `<b>${word.word}</b> <i>${word.pos}</i> — ${word.zh}<br>
    <small>${word.example}</small><br>
    <button class="primary" id="fav">★ 收藏</button>
    <button id="close">關閉</button>`;
  document.getElementById("fav").onclick = async () => {
    await saveVocab(word, article.id, article.level_label);
    el.innerHTML = "已收藏";
    setTimeout(() => { el.className = ""; el.innerHTML = ""; }, 800);
  };
  document.getElementById("close").onclick = () => { el.className = ""; el.innerHTML = ""; };
}

function renderText() {
  const container = document.createElement("p");
  for (const tok of markWords(article.text, article.words)) {
    if (tok.type === "word") {
      const span = document.createElement("span");
      span.className = "word";
      span.textContent = tok.value;
      span.onclick = () => showPopup(tok.word);
      container.appendChild(span);
    } else {
      container.appendChild(document.createTextNode(tok.value));
    }
  }
  return container;
}

function renderQuiz() {
  const wrap = document.createElement("div");
  const answers = new Array(article.quiz.length).fill(-1);
  article.quiz.forEach((q, qi) => {
    const block = document.createElement("div");
    block.innerHTML = `<p><b>${qi + 1}. ${q.q}</b></p>`;
    q.options.forEach((opt, oi) => {
      const b = document.createElement("button");
      b.className = "quiz-opt";
      b.textContent = opt;
      b.onclick = () => {
        answers[qi] = oi;
        [...block.querySelectorAll(".quiz-opt")].forEach((x, xi) => {
          x.className = "quiz-opt" + (xi === q.answer ? " correct" : (xi === oi ? " wrong" : ""));
        });
        block.querySelector(".explain")?.remove();
        const ex = document.createElement("div");
        ex.className = "explain"; ex.innerHTML = `<small>${q.explain}</small>`;
        block.appendChild(ex);
      };
      block.appendChild(b);
    });
    wrap.appendChild(block);
  });
  const submit = document.createElement("button");
  submit.className = "primary"; submit.textContent = "送出成績";
  submit.onclick = async () => {
    const r = scoreQuiz(article.quiz, answers);
    await saveProgress(article.id, r.score, r.total);
    submit.textContent = `已完成 ${r.score}/${r.total}`;
    submit.disabled = true;
  };
  wrap.appendChild(submit);
  return wrap;
}

async function init() {
  const resp = await fetch(`content/${date}.json`);
  const day = resp.ok ? await resp.json() : null;
  article = day ? findArticle(day, id) : null;
  const root = document.getElementById("article");
  if (!article) { root.textContent = "找不到這篇文章。"; return; }

  root.innerHTML = `<h2>${article.title}</h2>
    <div class="card-meta">${article.source === "real"
      ? `<a href="${article.origin_url}" target="_blank">${article.origin_name}</a> · ${article.level_label}`
      : `AI 生成 · ${article.level_label}`}</div>
    <div class="controls">
      <button class="primary" id="play">▶ 播放</button>
      語速 <input id="rate" type="range" min="0.7" max="1.2" step="0.1" value="1">
    </div>`;
  root.appendChild(renderText());
  root.appendChild(document.createElement("hr"));
  root.appendChild(renderQuiz());

  document.getElementById("rate").oninput = (e) => { rate = parseFloat(e.target.value); };
  document.getElementById("play").onclick = () => speak(article.text);
}

// 有些瀏覽器語音清單需等 voiceschanged
window.speechSynthesis.onvoiceschanged = () => {};
init();
