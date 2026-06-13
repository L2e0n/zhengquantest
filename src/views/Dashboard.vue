<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getRecentSessions } from '../services/questionService'
import { useQuestionsStore } from '../stores/questions'
import type { ExamSection, QuizSession } from '../types/question'
import { formatDateTime, sectionLabels } from '../utils/normalize'

const router = useRouter()
const store = useQuestionsStore()
const sessions = ref<QuizSession[]>([])

onMounted(async () => {
  await store.refresh()
  sessions.value = await getRecentSessions()
})
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>证券从业资格本地题库</h1>
        <p>导入题库后可按科目刷题，答错会自动进入错题本。</p>
      </div>
      <el-button type="primary" @click="router.push('/import')">导入题库</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :md="6"><el-card><el-statistic title="总题数" :value="store.counts.total" /></el-card></el-col>
      <el-col :xs="24" :md="6"><el-card><el-statistic title="金融基础知识" :value="store.counts.finance" /></el-card></el-col>
      <el-col :xs="24" :md="6"><el-card><el-statistic title="法律法规" :value="store.counts.law" /></el-card></el-col>
      <el-col :xs="24" :md="6"><el-card><el-statistic title="未掌握错题" :value="store.counts.wrong" /></el-card></el-col>
    </el-row>

    <el-card class="section-card" shadow="never">
      <template #header><strong>快速开始</strong></template>
      <el-space wrap>
        <el-button type="primary" size="large" @click="router.push('/subject')">📚 开始刷题</el-button>
        <el-button type="danger" @click="router.push('/wrong')">错题本</el-button>
        <el-button @click="router.push('/questions')">题库浏览</el-button>
      </el-space>
    </el-card>

    <el-card class="section-card" shadow="never">
      <template #header><strong>最近练习</strong></template>
      <el-empty v-if="!sessions.length" description="还没有练习记录" />
      <el-table v-else :data="sessions">
        <el-table-column label="开始时间">
          <template #default="{ row }">{{ formatDateTime(row.startedAt) }}</template>
        </el-table-column>
        <el-table-column label="科目">
          <template #default="{ row }">{{ row.section ? sectionLabels[row.section as ExamSection] : '综合' }}</template>
        </el-table-column>
        <el-table-column prop="correctCount" label="正确" />
        <el-table-column prop="wrongCount" label="错误" />
      </el-table>
    </el-card>
  </div>
</template>
