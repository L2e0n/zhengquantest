import { db } from '../db'
import type { Question, QuestionProgress } from '../types/question'
import { nanoid } from 'nanoid'

/**
 * 初始化题库数据
 * 从预置的 JSON 文件加载题目到 IndexedDB
 */
export async function initializeQuestions() {
  try {
    // 检查是否已经初始化过
    const count = await db.questions.count()
    if (count > 0) {
      console.log('题库已存在，跳过初始化')
      return { success: true, message: '题库已存在', count }
    }

    console.log('开始加载预置题库...')

    // 从服务器加载题库 JSON
    const response = await fetch('/questions.json')
    if (!response.ok) {
      throw new Error('题库文件加载失败')
    }

    const rawQuestions = await response.json()
    console.log(`加载了 ${rawQuestions.length} 道题目`)

    const now = Date.now()
    const questions: Question[] = []
    const progressRecords: QuestionProgress[] = []

    // 转换题目数据
    for (const raw of rawQuestions) {
      const questionId = nanoid()

      questions.push({
        id: questionId,
        section: raw.section,
        chapter: raw.chapter || '',
        topic: raw.topic || '',
        type: raw.type,
        stem: raw.stem,
        options: raw.options,
        answer: raw.answer,
        explanation: raw.explanation || '',
        difficulty: raw.difficulty,
        year: raw.year,
        source: raw.source || '',
        sourceUrl: raw.sourceUrl || '',
        tags: raw.tags || [],
        contentHash: raw.contentHash,
        createdAt: now,
        updatedAt: now
      })

      // 初始化进度记录
      progressRecords.push({
        questionId,
        totalAttempts: 0,
        correctAttempts: 0,
        wrongAttempts: 0,
        mastered: false,
        favorite: false
      })
    }

    // 批量导入数据库
    await db.transaction('rw', db.questions, db.progress, async () => {
      await db.questions.bulkAdd(questions)
      await db.progress.bulkAdd(progressRecords)
    })

    console.log('✅ 题库初始化完成！')

    return {
      success: true,
      message: '题库加载成功',
      count: questions.length
    }
  } catch (error) {
    console.error('题库初始化失败:', error)
    return {
      success: false,
      message: error instanceof Error ? error.message : '未知错误',
      count: 0
    }
  }
}

/**
 * 检查题库状态
 */
export async function checkQuestionsStatus() {
  const count = await db.questions.count()
  return {
    initialized: count > 0,
    count
  }
}
