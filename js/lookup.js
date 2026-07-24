// 線上查任意西語單字/片語的繁中翻譯（免金鑰、瀏覽器直接呼叫、純靜態站可用）
// 主要用 Google translate 的公開端點（品質好、支援繁中、CORS *），失敗時退到 MyMemory。
export async function lookup(text) {
  const q = (text || "").trim();
  if (!q) return null;

  try {
    const url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=es&tl=zh-TW&dt=t&q="
      + encodeURIComponent(q);
    const r = await fetch(url);
    if (r.ok) {
      const d = await r.json();
      const zh = (d[0] || []).map((seg) => seg[0]).join("").trim();
      if (zh) return zh;
    }
  } catch (e) { /* 落到備援 */ }

  try {
    const url = "https://api.mymemory.translated.net/get?langpair=es|zh-TW&q=" + encodeURIComponent(q);
    const r = await fetch(url);
    if (r.ok) {
      const d = await r.json();
      const zh = d.responseData && d.responseData.translatedText;
      if (zh) return zh.trim();
    }
  } catch (e) { /* 無 */ }

  return null;
}
