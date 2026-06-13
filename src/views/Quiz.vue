<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useQuizStore } from '../stores/quiz'
import { useQuestionsStore } from '../stores/questions'
import type { ExamSection, QuizMode } from '../types/question'
import { questionTypeLabels, sectionLabels } from '../utils/normalize'

const route = useRoute()
const quiz = useQuizStore()
const questions = useQuestionsStore()

// 将自定义的 mode 映射到标准 QuizMode
const routeMode = route.query.mode as string
let standardMode: QuizMode = 'section'
if (routeMode === 'wrong') standardMode = 'wrong'
else if (routeMode === 'favorite') standardMode = 'favorite'
else if (routeMode === 'random') standardMode = 'random'

const mode = ref<QuizMode>(standardMode)
const section = ref<ExamSection | undefined>((route.query.section as ExamSection) || 'finance_basic')
const chapter = ref<string | undefined>(route.query.chapter as string)
const year = ref<string | undefined>(route.query.year as string)
const questionType = ref<string | undefined>(route.query.type as string)
const limit = ref(parseInt(route.query.limit as string) || 20)

const progressText = computed(() => {
  if (!quiz.session) return '未开始'
  return `${quiz.currentIndex + 1} / ${quiz.questions.length}`
})

async function start() {
  const filters: any = {
    mode: mode.value,
    section: mode.value === 'wrong' || mode.value === 'favorite' ? undefined : section.value,
    limit: limit.value
  }

  // 章节练习
  if (chapter.value) {
    filters.chapter = chapter.value
  }

  // 真题模拟（按年份）
  if (year.value) {
    filters.year = parseInt(year.value)
  }

  // 题型筛选
  if (questionType.value) {
    filters.type = questionType.value
  }

  await quiz.startQuiz(filters)
}

onMounted(async () => {
  await questions.refresh()
  // 如果有 chapter 或 year 参数，直接开始
  if (route.query.chapter || route.query.year || route.query.section || route.query.mode) {
    await start()
  }
})
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>刷题练习</h1>
        <p>提交后立刻显示答案和解析，答错自动进入错题本。</p>
      </div>
      <el-tag size="large">{{ progressText }}</el-tag>
    </div>

    <el-card v-if="!quiz.session" shadow="never">
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :xs="24" :md="8">
            <el-form-item label="练习模式">
              <el-select v-model="mode">
                <el-option label="按科目练习" value="section" />
                <el-option label="随机练习" value="random" />
                <el-option label="错题复习" value="wrong" />
                <el-option label="收藏复习" value="favorite" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="科目">
              <el-select v-model="section" :disabled="mode === 'wrong' || mode === 'favorite'">
                <el-option v-for="(label, value) in sectionLabels" :key="value" :label="label" :value="value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="题数">
              <el-input-number v-model="limit" :min="1" :max="500" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-button type="primary" @click="start">开始练习</el-button>
      </el-form>
    </el-card>

    <el-empty v-else-if="!quiz.questions.length" description="没有匹配题目，请先导入题库或调整模式">
      <el-button @click="quiz.reset">返回</el-button>
    </el-empty>

    <el-result v-else-if="quiz.finished" icon="success" title="练习完成">
      <template #sub-title>
        正确 {{ quiz.session?.correctCount }} 题，错误 {{ quiz.session?.wrongCount }} 题
      </template>
      <template #extra>
        <el-button type="primary" @click="quiz.reset">再来一组</el-button>
      </template>
    </el-result>

    <el-card v-else-if="quiz.currentQuestion" shadow="never" class="quiz-card">
      <template #header>
        <div class="card-header">
          <strong>{{ questionTypeLabels[quiz.currentQuestion.type] }} · {{ sectionLabels[quiz.currentQuestion.section] }}</strong>
          <el-tag>{{ progressText }}</el-tag>
        </div>
      </template>

      <h2>{{ quiz.currentQuestion.stem }}</h2>
      <div class="quiz-options">
        <button
          v-for="option in quiz.currentQuestion.options"
          :key="option.key"
          class="quiz-option"
          :class="{
            selected: quiz.selected.includes(option.key),
            correct: quiz.submitted && quiz.currentQuestion.answer.includes(option.key),
            wrong: quiz.submitted && quiz.selected.includes(option.key) && !quiz.currentQuestion.answer.includes(option.key),
          }"
          @click="quiz.toggleOption(option.key)"
        >
          <b>{{ option.key }}.</b>
          <span>{{ option.text }}</span>
        </button>
      </div>

      <el-alert v-if="quiz.submitted" :type="quiz.currentCorrect ? 'success' : 'error'" :closable="false" class="section-card">
        <template #title>
          {{ quiz.currentCorrect ? '回答正确' : `回答错误，正确答案：${quiz.currentQuestion.answer.join('、')}` }}
        </template>
        <p v-if="quiz.currentQuestion.explanation">{{ quiz.currentQuestion.explanation }}</p>
      </el-alert>

      <div class="toolbar">
        <el-button :disabled="!quiz.selected.length || quiz.submitted" type="primary" @click="quiz.submitCurrent">提交答案</el-button>
        <el-button :disabled="!quiz.submitted" @click="quiz.nextQuestion">下一题</el-button>
      </div>
    </el-card>
  </div>
</template>
