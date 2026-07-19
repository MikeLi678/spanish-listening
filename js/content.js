export function articlesForLevel(day, level) {
  return (day && day.levels && day.levels[level]) || [];
}

export function findArticle(day, id) {
  if (!day || !day.levels) return null;
  for (const level of Object.keys(day.levels)) {
    for (const art of day.levels[level]) {
      if (art.id === id) return art;
    }
  }
  return null;
}
