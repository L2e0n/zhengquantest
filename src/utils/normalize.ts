import type { ExamSection, QuestionType } from '../types/question'

export const sectionLabels: Record<ExamSection, string> = {
  finance_basic: '金融基础知识',
  securities_law: '证券市场基本法律法规',
}

export const questionTypeLabels: Record<QuestionType, string> = {
  single: '单选题',
  multiple: '多选题',
  true_false: '判断题',
}

export function normalizeText(value: unknown) {
  return String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim()
}

export function normalizeAnswer(value: string[] | string | undefined) {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeText(item).toUpperCase()).filter(Boolean).sort()
  }

  return normalizeText(value)
    .split(/[，,、\s]+/)
    .map((item) => item.toUpperCase())
    .filter(Boolean)
    .sort()
}

export function isExamSection(value: unknown): value is ExamSection {
  return value === 'finance_basic' || value === 'securities_law'
}

export function isQuestionType(value: unknown): value is QuestionType {
  return value === 'single' || value === 'multiple' || value === 'true_false'
}

export function sameAnswer(left: string[], right: string[]) {
  if (left.length !== right.length) return false
  const sortedLeft = [...left].sort()
  const sortedRight = [...right].sort()
  return sortedLeft.every((item, index) => item === sortedRight[index])
}

export function formatDateTime(value?: number) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(value)
}
