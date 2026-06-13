export type ExamSection = 'finance_basic' | 'securities_law'

export type QuestionType = 'single' | 'multiple' | 'true_false'

export type QuizMode = 'section' | 'random' | 'chapter' | 'wrong' | 'favorite'

export interface QuestionOption {
  key: string
  text: string
}

export interface Question {
  id: string
  section: ExamSection
  chapter?: string
  topic?: string
  type: QuestionType
  stem: string
  options: QuestionOption[]
  answer: string[]
  explanation?: string
  difficulty?: 'easy' | 'medium' | 'hard'
  year?: number
  source?: string
  sourceUrl?: string
  tags: string[]
  createdAt: number
  updatedAt: number
  contentHash: string
}

export interface RawQuestion {
  section?: string
  chapter?: string
  topic?: string
  type?: string
  stem?: string
  options?: QuestionOption[]
  answer?: string[] | string
  explanation?: string
  difficulty?: string
  year?: number | string
  source?: string
  sourceUrl?: string
  tags?: string[] | string
}

export interface QuestionProgress {
  questionId: string
  totalAttempts: number
  correctAttempts: number
  wrongAttempts: number
  lastSelected?: string[]
  lastCorrect?: boolean
  lastAnsweredAt?: number
  firstWrongAt?: number
  lastWrongAt?: number
  mastered: boolean
  favorite: boolean
}

export interface AnswerRecord {
  id: string
  questionId: string
  selected: string[]
  correct: boolean
  mode: 'practice' | 'exam' | 'wrong_review'
  durationMs: number
  answeredAt: number
}

export interface QuizSession {
  id: string
  section?: ExamSection
  mode: QuizMode
  questionIds: string[]
  currentIndex: number
  startedAt: number
  finishedAt?: number
  correctCount: number
  wrongCount: number
}

export interface ImportBatch {
  id: string
  fileName: string
  source?: string
  importedAt: number
  addedCount: number
  updatedCount: number
  skippedCount: number
  invalidCount: number
}

export interface QuestionFilters {
  keyword?: string
  section?: ExamSection | ''
  chapter?: string
  type?: QuestionType | ''
  year?: number | ''
  wrongOnly?: boolean
  favoriteOnly?: boolean
  includeMastered?: boolean
}

export interface ImportPreviewItem {
  raw: RawQuestion
  question?: Question
  valid: boolean
  duplicate: boolean
  errors: string[]
}

export interface ImportPreview {
  items: ImportPreviewItem[]
  addedCount: number
  duplicateCount: number
  invalidCount: number
}

export interface AppBackup {
  exportedAt: number
  questions: Question[]
  progress: QuestionProgress[]
  answerRecords: AnswerRecord[]
  quizSessions: QuizSession[]
  importBatches: ImportBatch[]
}
