<script setup lang="ts">
import { computed } from 'vue'
import type { Question, QuestionProgress } from '../types/question'
import { questionTypeLabels, sectionLabels } from '../utils/normalize'

const props = defineProps<{
  question: Question
  progress?: QuestionProgress
  showAnswer?: boolean
}>()

const answerText = computed(() => props.question.answer.join('、'))
</script>

<template>
  <el-card class="question-card" shadow="hover">
    <template #header>
      <div class="question-card__header">
        <div>
          <el-tag>{{ sectionLabels[question.section] }}</el-tag>
          <el-tag type="info">{{ questionTypeLabels[question.type] }}</el-tag>
          <el-tag v-if="question.chapter" type="success">{{ question.chapter }}</el-tag>
          <el-tag v-if="question.year" type="warning">{{ question.year }}</el-tag>
        </div>
        <div class="question-card__actions">
          <el-tag v-if="progress?.favorite" type="danger">已收藏</el-tag>
          <el-tag v-if="progress?.wrongAttempts" type="danger">错 {{ progress.wrongAttempts }} 次</el-tag>
          <el-tag v-if="progress?.mastered" type="success">已掌握</el-tag>
        </div>
      </div>
    </template>

    <p class="stem">{{ question.stem }}</p>
    <div class="options">
      <div v-for="option in question.options" :key="option.key" class="option-row">
        <b>{{ option.key }}.</b>
        <span>{{ option.text }}</span>
      </div>
    </div>

    <el-alert v-if="showAnswer" type="success" :closable="false" class="answer-box">
      <template #title>答案：{{ answerText }}</template>
      <p v-if="question.explanation">{{ question.explanation }}</p>
      <small v-if="question.source">来源：{{ question.source }}</small>
    </el-alert>
  </el-card>
</template>
