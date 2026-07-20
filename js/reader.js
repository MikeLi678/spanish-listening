import { findArticle } from "./content.js";
import { markWords } from "./vocab-render.js";
import { scoreQuiz } from "./quiz.js";
import { saveProgress, saveVocab } from "./data-client.js";

const params = new URLSearchParams(location.search);
const date = params.get("date");
const id = params.get("id");
let article = null;
let rate = 1;

// 播放控制：Web Speech API 無法改變進行中語音的語速，
// 所以改語速時從目前唸到的位置用新語速重啟；暫停/繼續用 pause()/resume()
let utter = null;      // 目前的 utterance（用來忽略被 cancel 的舊事件）
let currentChar = 0;   // 目前唸到的字元位置（相對 article.text）
let playing = false;   // 是否正在播放（含暫停中）
let paused = false;
let warnedNoVoice = false;
let keepAlive = null;

// Chrome 長語音約 15 秒會被自動中斷：播放中（非使用者暫停）週期性 resume 保活
function startKeepAlive() {
  stopKeepAlive();
  keepAlive = setInterval(() => {
    if (playing && !paused) window.speechSynthesis.resume();
  }, 10000);
}
function stopKeepAlive() {
  if (keepAlive) { clearInterval(keepAlive); keepAlive = null; }
}

function speakFrom(fromChar) {
  const synth = window.speechSynthesis;
  const u = new SpeechSynthesisUtterance(article.text.slice(fromChar));
  u.lang = "es-ES";
  u.rate = rate;
  const voice = synth.getVoices().find((v) => v.lang.startsWith("es"));
  if (voice) u.voice = voice;
  else if (!warnedNoVoice) {
    warnedNoVoice = true;
    alert("此瀏覽器沒有西語語音，文字閱讀仍可使用。");
  }
  u.onboundary = (e) => { if (utter === u) currentChar = fromChar + e.charIndex; };
  u.onend = () => {
    if (utter !== u) return;   // 忽略被 cancel 掉的舊 utterance
    playing = false; paused = false; currentChar = 0;
    stopKeepAlive();
    updateButtons();
  };
  utter = u;
  const doSpeak = () => { if (utter === u) synth.speak(u); };
  if (synth.speaking || synth.pending) {
    synth.cancel();
    setTimeout(doSpeak, 120);   // 避開 Chrome 的 cancel→speak 競態
  } else {
    doSpeak();
  }
  playing = true; paused = false;
  startKeepAlive();
  updateButtons();
}

function play() {
  const synth = window.speechSynthesis;
  if (playing && paused) { synth.resume(); paused = false; updateButtons(); }
  else { speakFrom(0); }   // 停止中或播放中：從頭播；暫停中：繼續
}

function pause() {
  if (playing && !paused) { window.speechSynthesis.pause(); paused = true; updateButtons(); }
}

function setRate(value) {
  rate = value;
  if (playing) speakFrom(currentChar);   // 播放中改語速：從目前位置用新語速無縫重啟
}

function updateButtons() {
  const playBtn = document.getElementById("play");
  const pauseBtn = document.getElementById("pause");
  if (playBtn) playBtn.textContent = (playing && paused) ? "▶ 繼續" : "▶ 播放";
  if (pauseBtn) pauseBtn.disabled = !(playing && !paused);
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
      <button id="pause" disabled>⏸ 暫停</button>
      語速
      <select id="rate">
        <option value="0.25">0.25x</option>
        <option value="0.5">0.5x</option>
        <option value="0.75">0.75x</option>
        <option value="1" selected>1x</option>
        <option value="1.25">1.25x</option>
        <option value="1.5">1.5x</option>
        <option value="2">2x</option>
      </select>
      ${article.translation ? '<button id="translate">翻譯成中文</button>' : ""}
    </div>`;
  root.appendChild(renderText());

  let translationEl = null;
  if (article.translation) {
    translationEl = document.createElement("div");
    translationEl.className = "translation";
    translationEl.hidden = true;
    translationEl.textContent = article.translation;
    root.appendChild(translationEl);
  }

  root.appendChild(document.createElement("hr"));
  root.appendChild(renderQuiz());

  document.getElementById("rate").onchange = (e) => setRate(parseFloat(e.target.value));
  document.getElementById("play").onclick = play;
  document.getElementById("pause").onclick = pause;
  if (translationEl) {
    const tbtn = document.getElementById("translate");
    tbtn.onclick = () => {
      translationEl.hidden = !translationEl.hidden;
      tbtn.textContent = translationEl.hidden ? "翻譯成中文" : "隱藏翻譯";
    };
  }
}

// 有些瀏覽器語音清單需等 voiceschanged
window.speechSynthesis.onvoiceschanged = () => {};
init();
