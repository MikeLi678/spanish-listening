import { FIREBASE_CONFIG } from "./config.js";
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut as fbSignOut, onAuthStateChanged }
  from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore, doc, setDoc, collection, getDocs, query, orderBy }
  from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

// FIREBASE_CONFIG.apiKey 留空時不啟用雲端同步，全程走 localStorage
const enabled = Boolean(FIREBASE_CONFIG && FIREBASE_CONFIG.apiKey);
const app = enabled ? initializeApp(FIREBASE_CONFIG) : null;
const auth = app ? getAuth(app) : null;
const db = app ? getFirestore(app) : null;

const LS_PROGRESS = "sl_progress";
const LS_VOCAB = "sl_vocab";
function lsGet(key) { try { return JSON.parse(localStorage.getItem(key)) || []; } catch { return []; } }
function lsSet(key, v) { localStorage.setItem(key, JSON.stringify(v)); }

// Firebase 在載入後才非同步還原登入狀態，等第一次 onAuthStateChanged 再回答 getUser
let currentUser = null;
let resolveReady;
const authReady = new Promise((res) => { resolveReady = res; });
if (auth) {
  onAuthStateChanged(auth, (user) => { currentUser = user; resolveReady(); });
} else {
  resolveReady();
}

// Firestore 文件 id 不可含 "/"，用 encodeURIComponent 保險（真正的值另存欄位）
function docId(s) { return encodeURIComponent(s); }

export async function getUser() {
  if (!auth) return null;
  await authReady;
  return currentUser;
}

export async function signInWithGoogle() {
  if (!auth) return;
  try {
    await signInWithPopup(auth, new GoogleAuthProvider());
    location.reload();
  } catch (e) {
    // 使用者關閉彈窗或取消登入，忽略
  }
}

export async function signOut() {
  if (auth) await fbSignOut(auth);
}

export async function saveProgress(articleId, score, total) {
  const user = await getUser();
  if (user) {
    try {
      await setDoc(doc(db, "users", user.uid, "progress", docId(articleId)),
        { article_id: articleId, score, total, completed_at: Date.now() });
      return;
    } catch (e) { /* 落回 localStorage */ }
  }
  const rows = lsGet(LS_PROGRESS).filter((r) => r.article_id !== articleId);
  rows.push({ article_id: articleId, score, total });
  lsSet(LS_PROGRESS, rows);
}

export async function saveVocab(wordObj, articleId, level) {
  const user = await getUser();
  const row = { word: wordObj.word, pos: wordObj.pos, zh: wordObj.zh,
                example: wordObj.example, source_article_id: articleId, level };
  if (user) {
    try {
      await setDoc(doc(db, "users", user.uid, "vocabulary", docId(wordObj.word)),
        { ...row, created_at: Date.now() });
      return;
    } catch (e) { /* 落回 localStorage */ }
  }
  const rows = lsGet(LS_VOCAB).filter((r) => r.word !== row.word);
  rows.push(row);
  lsSet(LS_VOCAB, rows);
}

export async function listVocab() {
  const user = await getUser();
  if (user) {
    try {
      const q = query(collection(db, "users", user.uid, "vocabulary"), orderBy("created_at", "desc"));
      const snap = await getDocs(q);
      return snap.docs.map((d) => d.data());
    } catch (e) { /* 落回 localStorage */ }
  }
  return lsGet(LS_VOCAB);
}
