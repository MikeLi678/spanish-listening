import { test } from "node:test";
import assert from "node:assert";
import { articlesForLevel, findArticle } from "../../js/content.js";

const day = { date: "2026-07-18", levels: { A1: [{ id: "x", title: "t" }], B2: [] } };

test("articlesForLevel returns level array", () => {
  assert.equal(articlesForLevel(day, "A1").length, 1);
  assert.deepEqual(articlesForLevel(day, "C2"), []);
});

test("findArticle searches all levels", () => {
  assert.equal(findArticle(day, "x").title, "t");
  assert.equal(findArticle(day, "none"), null);
});
