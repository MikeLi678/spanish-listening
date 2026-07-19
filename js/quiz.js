export function scoreQuiz(quiz, answers) {
  const results = quiz.map((q, i) => answers[i] === q.answer);
  return {
    score: results.filter(Boolean).length,
    total: quiz.length,
    results,
  };
}
