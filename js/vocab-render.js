// 把 text 依 words 切成 token；比對忽略大小寫，只標第一次出現
export function markWords(text, words) {
  const tokens = [];
  let remaining = text;
  const lookup = words.map((w) => ({ lower: w.word.toLowerCase(), word: w }));
  while (remaining.length) {
    let hitIdx = -1, hit = null;
    for (const entry of lookup) {
      const idx = remaining.toLowerCase().indexOf(entry.lower);
      if (idx !== -1 && (hitIdx === -1 || idx < hitIdx)) {
        hitIdx = idx; hit = entry;
      }
    }
    if (hitIdx === -1) {
      tokens.push({ type: "text", value: remaining });
      break;
    }
    if (hitIdx > 0) tokens.push({ type: "text", value: remaining.slice(0, hitIdx) });
    const matched = remaining.slice(hitIdx, hitIdx + hit.lower.length);
    tokens.push({ type: "word", value: matched, word: hit.word });
    remaining = remaining.slice(hitIdx + hit.lower.length);
  }
  return tokens;
}
