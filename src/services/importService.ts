import { nanoid } from 'nanoid'
import { db } from '../db'
import type { ImportBatch, ImportPreview, ImportPreviewItem, Question, RawQuestion } from '../types/question'
import { createHash } from '../utils/hash'
import { isExamSection, isQuestionType, normalizeAnswer, normalizeText } from '../utils/normalize'

function parseTags(value: RawQuestion['tags']) {
  if (Array.isArray(value)) return value.map(normalizeText).filter(Boolean)
  return normalizeText(value)
    .split(/[，,、]/)
    .map(normalizeText)
    .filter(Boolean)
}

async function normalizeQuestion(raw: RawQuestion): Promise<Omit<ImportPreviewItem, 'duplicate'>> {
  const errors: string[] = []
  const section = normalizeText(raw.section)
  const type = normalizeText(raw.type)
  const stem = normalizeText(raw.stem)
  const options = Array.isArray(raw.options)
    ? raw.options.map((option) => ({ key: normalizeText(option.key).toUpperCase(), text: normalizeText(option.text) }))
    : []
  const answer = normalizeAnswer(raw.answer)

  if (!isExamSection(section)) errors.push('科目 section 必须是 finance_basic 或 securities_law')
  if (!isQuestionType(type)) errors.push('题型 type 必须是 single、multiple 或 true_false')
  if (!stem) errors.push('题干 stem 不能为空')
  if (type !== 'true_false' && options.length < 2) errors.push('单选/多选至少需要两个选项')
  if (!answer.length) errors.push('答案 answer 不能为空')

  const optionKeys = new Set(options.map((option) => option.key))
  if (options.length && answer.some((key) => !optionKeys.has(key))) {
    errors.push('答案中的选项 key 必须存在于 options')
  }

  if (type === 'single' && answer.length !== 1) errors.push('单选题只能有一个答案')
  if (type === 'true_false' && options.length === 0) {
    options.push({ key: 'A', text: '正确' }, { key: 'B', text: '错误' })
  }

  if (errors.length || !isExamSection(section) || !isQuestionType(type)) {
    return { raw, valid: false, errors }
  }

  const now = Date.now()
  const normalizedContent = JSON.stringify({ section, type, stem, options, answer })
  const contentHash = await createHash(normalizedContent)
  const year = raw.year === undefined || raw.year === '' ? undefined : Number(raw.year)

  const question: Question = {
    id: nanoid(),
    section,
    chapter: normalizeText(raw.chapter) || undefined,
    topic: normalizeText(raw.topic) || undefined,
    type,
    stem,
    options,
    answer,
    explanation: normalizeText(raw.explanation) || undefined,
    difficulty: raw.difficulty === 'easy' || raw.difficulty === 'medium' || raw.difficulty === 'hard' ? raw.difficulty : undefined,
    year: Number.isFinite(year) ? year : undefined,
    source: normalizeText(raw.source) || undefined,
    sourceUrl: normalizeText(raw.sourceUrl) || undefined,
    tags: parseTags(raw.tags),
    createdAt: now,
    updatedAt: now,
    contentHash,
  }

  return { raw, question, valid: true, errors: [] }
}

export async function buildImportPreview(rawItems: RawQuestion[]): Promise<ImportPreview> {
  const existingHashes = new Set((await db.questions.toArray()).map((question) => question.contentHash))
  const seenHashes = new Set<string>()
  const items: ImportPreviewItem[] = []

  for (const raw of rawItems) {
    const item = await normalizeQuestion(raw)
    const duplicate = Boolean(item.question && (existingHashes.has(item.question.contentHash) || seenHashes.has(item.question.contentHash)))
    if (item.question) seenHashes.add(item.question.contentHash)
    items.push({ ...item, duplicate })
  }

  return {
    items,
    addedCount: items.filter((item) => item.valid && !item.duplicate).length,
    duplicateCount: items.filter((item) => item.duplicate).length,
    invalidCount: items.filter((item) => !item.valid).length,
  }
}

export async function importQuestions(preview: ImportPreview, fileName: string) {
  const questions = preview.items
    .filter((item): item is ImportPreviewItem & { question: Question } => item.valid && !item.duplicate && Boolean(item.question))
    .map((item) => item.question)

  const batch: ImportBatch = {
    id: nanoid(),
    fileName,
    importedAt: Date.now(),
    addedCount: questions.length,
    updatedCount: 0,
    skippedCount: preview.duplicateCount,
    invalidCount: preview.invalidCount,
  }

  await db.transaction('rw', db.questions, db.importBatches, async () => {
    await db.questions.bulkAdd(questions)
    await db.importBatches.add(batch)
  })

  return batch
}

export async function parseQuestionJsonFile(file: File) {
  const text = await file.text()
  const parsed = JSON.parse(text)
  if (!Array.isArray(parsed)) throw new Error('JSON 顶层必须是题目数组')
  return parsed as RawQuestion[]
}
