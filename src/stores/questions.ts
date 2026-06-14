import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { ImportPreview, Question, QuestionFilters } from '../types/question'
import { buildImportPreview, importQuestions, parseQuestionJsonFile } from '../services/importService'
import { getProgressMap, getQuestionCounts, listChapters, searchQuestions, toggleFavorite } from '../services/questionService'

export const useQuestionsStore = defineStore('questions', () => {
  const filters = ref<QuestionFilters>({})
  const questions = ref<Question[]>([])
  const progressMap = ref(new Map())
  const counts = ref({ total: 0, finance: 0, law: 0, wrong: 0, favorite: 0 })
  const chapters = ref<string[]>([])
  const loading = ref(false)
  const preview = ref<ImportPreview | null>(null)

  const hasQuestions = computed(() => counts.value.total > 0)

  async function refresh() {
    loading.value = true
    try {
      counts.value = await getQuestionCounts()
      progressMap.value = await getProgressMap()
      questions.value = await searchQuestions(filters.value)
      chapters.value = await listChapters(filters.value.section)
    } finally {
      loading.value = false
    }
  }

  async function setFilters(next: QuestionFilters) {
    filters.value = { ...filters.value, ...next }
    await refresh()
  }

  async function previewFile(file: File) {
    const raw = await parseQuestionJsonFile(file)
    preview.value = await buildImportPreview(raw)
  }

  async function confirmImport(fileName: string) {
    if (!preview.value) return null
    const batch = await importQuestions(preview.value, fileName)
    preview.value = null
    await refresh()
    return batch
  }

  async function toggleQuestionFavorite(questionId: string) {
    await toggleFavorite(questionId)
    await refresh()
  }

  async function forceRefresh() {
    // 清空题库，重新从服务器下载
    const { db } = await import('../db')
    await db.questions.clear()

    // 重新导入
    const { initializeQuestions } = await import('../services/initQuestions')
    await initializeQuestions()

    // 刷新
    await refresh()
  }

  return {
    filters,
    questions,
    progressMap,
    counts,
    chapters,
    loading,
    preview,
    hasQuestions,
    refresh,
    setFilters,
    previewFile,
    confirmImport,
    toggleQuestionFavorite,
    forceRefresh,
  }
})
