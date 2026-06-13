import Dexie, { type EntityTable } from 'dexie'
import type { AnswerRecord, ImportBatch, Question, QuestionProgress, QuizSession } from '../types/question'

class ZhengQuanDatabase extends Dexie {
  questions!: EntityTable<Question, 'id'>
  progress!: EntityTable<QuestionProgress, 'questionId'>
  answerRecords!: EntityTable<AnswerRecord, 'id'>
  quizSessions!: EntityTable<QuizSession, 'id'>
  importBatches!: EntityTable<ImportBatch, 'id'>

  constructor() {
    super('zhengquantest')
    this.version(1).stores({
      questions: 'id, section, chapter, topic, type, year, contentHash, *tags',
      progress: 'questionId, favorite, mastered, wrongAttempts, lastWrongAt, lastAnsweredAt',
      answerRecords: 'id, questionId, correct, mode, answeredAt',
      quizSessions: 'id, mode, section, startedAt, finishedAt',
      importBatches: 'id, importedAt',
    })
  }
}

export const db = new ZhengQuanDatabase()
