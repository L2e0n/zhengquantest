import { nanoid } from 'nanoid'
import { db } from '../db'
import type { AnswerRecord, QuestionProgress, QuizMode } from '../types/question'
import { ensureProgress } from './questionService'

export async function recordAnswer(params: {
  questionId: string
  selected: string[]
  correct: boolean
  mode: QuizMode
  durationMs: number
}) {
  const now = Date.now()
  const record: AnswerRecord = {
    id: nanoid(),
    questionId: params.questionId,
    selected: [...params.selected].sort(),
    correct: params.correct,
    mode: params.mode === 'wrong' ? 'wrong_review' : 'practice',
    durationMs: params.durationMs,
    answeredAt: now,
  }

  const current = await ensureProgress(params.questionId)
  const next: QuestionProgress = {
    ...current,
    totalAttempts: current.totalAttempts + 1,
    correctAttempts: current.correctAttempts + (params.correct ? 1 : 0),
    wrongAttempts: current.wrongAttempts + (params.correct ? 0 : 1),
    lastSelected: record.selected,
    lastCorrect: params.correct,
    lastAnsweredAt: now,
    firstWrongAt: params.correct ? current.firstWrongAt : current.firstWrongAt ?? now,
    lastWrongAt: params.correct ? current.lastWrongAt : now,
    mastered: params.correct ? current.mastered : false,
  }

  await db.transaction('rw', db.answerRecords, db.progress, async () => {
    await db.answerRecords.add(record)
    await db.progress.put(next)
  })

  return { record, progress: next }
}
