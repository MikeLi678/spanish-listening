import { test } from "node:test";
import assert from "node:assert";
import { scoreQuiz } from "../../js/quiz.js";

test("scoreQuiz counts correct answers", () => {
  const quiz = [
    { answer: 0 }, { answer: 2 }, { answer: 1 },
  ];
  const r = scoreQuiz(quiz, [0, 1, 1]);
  assert.equal(r.total, 3);
  assert.equal(r.score, 2);
  assert.deepEqual(r.results, [true, false, true]);
});
