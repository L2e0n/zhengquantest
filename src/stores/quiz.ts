import { nanoid } from 'nanoid'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { db } from '../db'
import type { ExamSection, Question, QuestionFilters, QuizMode, QuizSession } from '../types/question'
import { pickQuestions } from '../services/questionService'
import { recordAnswer } from '../services/progressService'
import { sameAnswer } from '../utils/normalize'

export const useQuizStore = defineStore('quiz', () => {
  const session = ref<QuizSession | null>(null)
  const questions = ref<Question[]>([])
  const selected = ref<string[]>([])
  const submitted = ref(false)
  const currentCorrect = ref<boolean | null>(null)
  const questionStartedAt = ref(Date.now())

  const currentIndex = computed(() => session.value?.currentIndex ?? 0)
  const currentQuestion = computed(() => questions.value[currentIndex.value])
  const finished = computed(() => Boolean(session.value?.finishedAt))

  async function startQuiz(params: { mode: QuizMode; section?: ExamSection; chapter?: string; year?: number; type?: string; limit?: number }) {
    const filters: QuestionFilters = {
      section: params.section,
      chapter: params.chapter,
      year: params.year,
      type: (params.type as any) || '',
      wrongOnly: params.mode === 'wrong',
      favoriteOnly: params.mode === 'favorite',
    }
    const picked = await pickQuestions(filters, params.limit ?? 20)
    const nextSession: QuizSession = {
      id: nanoid(),
      section: params.section,
      mode: params.mode,
      questionIds: picked.map((question) => question.id),
      currentIndex: 0,
      startedAt: Date.now(),
      correctCount: 0,
      wrongCount: 0,
    }

    questions.value = picked
    session.value = nextSession
    selected.value = []
    submitted.value = false
    currentCorrect.value = null
    questionStartedAt.value = Date.now()
    await db.quizSessions.put(JSON.parse(JSON.stringify(nextSession)))
  }

  function toggleOption(key: string) {
    const question = currentQuestion.value
    if (!question || submitted.value) return

    if (question.type === 'multiple') {
      selected.value = selected.value.includes(key)
        ? selected.value.filter((item) => item !== key)
        : [...selected.value, key]
      return
    }

    selected.value = [key]
  }

  async function submitCurrent() {
    const question = currentQuestion.value
    if (!question || !session.value || selected.value.length === 0 || submitted.value) return

    const correct = sameAnswer(selected.value, question.answer)
    const durationMs = Date.now() - questionStartedAt.value
    await recordAnswer({ questionId: question.id, selected: selected.value, correct, mode: session.value.mode, durationMs })

    const updatedSession = {
      ...session.value,
      correctCount: session.value.correctCount + (correct ? 1 : 0),
      wrongCount: session.value.wrongCount + (correct ? 0 : 1),
    }
    session.value = updatedSession
    await db.quizSessions.put(JSON.parse(JSON.stringify(updatedSession)))

    currentCorrect.value = correct
    submitted.value = true
  }

  async function nextQuestion() {
    if (!session.value) return
    if (session.value.currentIndex >= questions.value.length - 1) {
      const finishedSession = { ...session.value, finishedAt: Date.now() }
      session.value = finishedSession
      await db.quizSessions.put(JSON.parse(JSON.stringify(finishedSession)))
      return
    }

    const updatedSession = { ...session.value, currentIndex: session.value.currentIndex + 1 }
    session.value = updatedSession
    selected.value = []
    submitted.value = false
    currentCorrect.value = null
    questionStartedAt.value = Date.now()
    await db.quizSessions.put(JSON.parse(JSON.stringify(updatedSession)))
  }

  function reset() {
    session.value = null
    questions.value = []
    selected.value = []
    submitted.value = false
    currentCorrect.value = null
  }

  return {
    session,
    questions,
    selected,
    submitted,
    currentCorrect,
    currentIndex,
    currentQuestion,
    finished,
    startQuiz,
    toggleOption,
    submitCurrent,
    nextQuestion,
    reset,
  }
})
