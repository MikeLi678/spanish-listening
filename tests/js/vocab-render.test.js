import { test } from "node:test";
import assert from "node:assert";
import { markWords } from "../../js/vocab-render.js";

test("markWords tokenizes matched words", () => {
  const tokens = markWords("Como pan hoy", [{ word: "pan", zh: "麵包" }]);
  const wordTok = tokens.find((t) => t.type === "word");
  assert.equal(wordTok.value, "pan");
  assert.equal(wordTok.word.zh, "麵包");
});
