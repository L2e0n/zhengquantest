import { db } from '../db'
import type { AppBackup, ExamSection, Question, QuestionFilters, QuestionProgress } from '../types/question'
import { normalizeText } from '../utils/normalize'

export async function getQuestionCounts() {
  const [total, finance, law, progress] = await Promise.all([
    db.questions.count(),
    db.questions.where('section').equals('finance_basic').count(),
    db.questions.where('section').equals('securities_law').count(),
    db.progress.toArray(),
  ])

  return {
    total,
    finance,
    law,
    wrong: progress.filter((item) => item.wrongAttempts > 0 && !item.mastered).length,
    favorite: progress.filter((item) => item.favorite).length,
  }
}

export async function searchQuestions(filters: QuestionFilters = {}) {
  let questions = await db.questions.toArray()

  if (filters.section) questions = questions.filter((question) => question.section === filters.section)
  if (filters.chapter) questions = questions.filter((question) => question.chapter?.includes(filters.chapter || ''))
  if (filters.type) questions = questions.filter((question) => question.type === filters.type)
  if (filters.year) questions = questions.filter((question) => question.chapter?.includes(`${filters.year}年`))

  const progress = await db.progress.toArray()
  const progressMap = new Map(progress.map((item) => [item.questionId, item]))

  if (filters.wrongOnly) {
    questions = questions.filter((question) => {
      const item = progressMap.get(question.id)
      return item && item.wrongAttempts > 0 && (filters.includeMastered || !item.mastered)
    })
  }

  if (filters.favoriteOnly) {
    questions = questions.filter((question) => progressMap.get(question.id)?.favorite)
  }

  const keyword = normalizeText(filters.keyword).toLowerCase()
  if (keyword) {
    questions = questions.filter((question) => {
      const content = [
        question.stem,
        question.explanation,
        question.chapter,
        question.topic,
        question.source,
        ...question.tags,
        ...question.options.map((option) => option.text),
      ]
        .join(' ')
        .toLowerCase()
      return content.includes(keyword)
    })
  }

  return questions
}

export async function listChapters(section?: ExamSection | '') {
  let questions = await db.questions.toArray()
  if (section) questions = questions.filter((question) => question.section === section)
  return Array.from(new Set(questions.map((question) => question.chapter).filter(Boolean))).sort() as string[]
}

export async function getProgressMap() {
  const progress = await db.progress.toArray()
  return new Map(progress.map((item) => [item.questionId, item]))
}

export async function ensureProgress(questionId: string): Promise<QuestionProgress> {
  const existing = await db.progress.get(questionId)
  if (existing) return existing
  const progress: QuestionProgress = {
    questionId,
    totalAttempts: 0,
    correctAttempts: 0,
    wrongAttempts: 0,
    mastered: false,
    favorite: false,
  }
  await db.progress.add(progress)
  return progress
}

export async function toggleFavorite(questionId: string) {
  const progress = await ensureProgress(questionId)
  await db.progress.put({ ...progress, favorite: !progress.favorite })
}

export async function markMastered(questionId: string, mastered = true) {
  const progress = await ensureProgress(questionId)
  await db.progress.put({ ...progress, mastered })
}

export async function exportBackup(): Promise<AppBackup> {
  const [questions, progress, answerRecords, quizSessions, importBatches] = await Promise.all([
    db.questions.toArray(),
    db.progress.toArray(),
    db.answerRecords.toArray(),
    db.quizSessions.toArray(),
    db.importBatches.toArray(),
  ])

  return {
    exportedAt: Date.now(),
    questions,
    progress,
    answerRecords,
    quizSessions,
    importBatches,
  }
}

export async function importBackup(backup: AppBackup) {
  await db.transaction('rw', [db.questions, db.progress, db.answerRecords, db.quizSessions, db.importBatches], async () => {
    await db.questions.clear()
    await db.progress.clear()
    await db.answerRecords.clear()
    await db.quizSessions.clear()
    await db.importBatches.clear()
    await db.questions.bulkPut(backup.questions ?? [])
    await db.progress.bulkPut(backup.progress ?? [])
    await db.answerRecords.bulkPut(backup.answerRecords ?? [])
    await db.quizSessions.bulkPut(backup.quizSessions ?? [])
    await db.importBatches.bulkPut(backup.importBatches ?? [])
  })
}

export async function clearAllData() {
  await db.transaction('rw', [db.questions, db.progress, db.answerRecords, db.quizSessions, db.importBatches], async () => {
    await db.questions.clear()
    await db.progress.clear()
    await db.answerRecords.clear()
    await db.quizSessions.clear()
    await db.importBatches.clear()
  })
}

export async function clearProgressOnly() {
  await db.transaction('rw', db.progress, db.answerRecords, db.quizSessions, async () => {
    await db.progress.clear()
    await db.answerRecords.clear()
    await db.quizSessions.clear()
  })
}

export async function pickQuestions(filters: QuestionFilters, limit = 20) {
  const questions = await searchQuestions(filters)
  return shuffle(questions).slice(0, limit)
}

function shuffle<T>(items: T[]) {
  return [...items].sort(() => Math.random() - 0.5)
}

export async function getRecentSessions() {
  return db.quizSessions.orderBy('startedAt').reverse().limit(5).toArray()
}

export function downloadJson(data: unknown, fileName: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  URL.revokeObjectURL(url)
}

export async function getQuestionById(id: string): Promise<Question | undefined> {
  return db.questions.get(id)
}
