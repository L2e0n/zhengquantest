<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '../db'
import type { ExamSection, Question } from '../types/question'
import { sectionLabels } from '../utils/normalize'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const section = ref<ExamSection>((route.query.section as ExamSection) || 'finance_basic')

interface MockExam {
  name: string
  year: string
  count: number
  singleCount: number
  multipleCount: number
}

const exams = ref<MockExam[]>([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  const questions = await db.questions
    .where('section')
    .equals(section.value)
    .toArray()

  // 筛选真题
  const mockQuestions = questions.filter(q => q.chapter?.includes('真题'))

  // 按年份分组
  const yearMap = new Map<string, Question[]>()
  mockQuestions.forEach(q => {
    const match = q.chapter?.match(/(\d{4})年/)
    if (match) {
      const year = match[1]
      if (!yearMap.has(year)) {
        yearMap.set(year, [])
      }
      yearMap.get(year)!.push(q)
    }
  })

  // 转换为数组
  exams.value = Array.from(yearMap.entries())
    .map(([year, questions]) => ({
      name: `${year}年真题`,
      year,
      count: questions.length,
      singleCount: questions.filter(q => q.type === 'single').length,
      multipleCount: questions.filter(q => q.type === 'multiple').length,
    }))
    .sort((a, b) => parseInt(b.year) - parseInt(a.year)) // 按年份降序

  loading.value = false
})

async function startMockExam(exam: MockExam) {
  // 真题模拟需要确认，因为会限时
  await ElMessageBox.confirm(
    `本次模拟考试共 ${exam.count} 题（单选 ${exam.singleCount} 题，多选 ${exam.multipleCount} 题），建议用时 120 分钟。确定开始？`,
    '真题模拟',
    {
      confirmButtonText: '开始考试',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )

  router.push({
    path: '/quiz',
    query: {
      section: section.value,
      year: exam.year,
      mode: 'mock',
      limit: exam.count
    }
  })
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>📝 真题模拟</h1>
        <p>{{ sectionLabels[section] }} - 历年真题模拟考试</p>
      </div>
      <el-button @click="router.push({ path: '/practice-mode', query: { section } })">
        ← 返回
      </el-button>
    </div>

    <el-alert type="warning" :closable="false" style="margin-bottom: 20px">
      <template #title>
        真题模拟按照真实考试标准组卷，建议在安静环境下完成。每套试卷约100题，建议用时120分钟。
      </template>
    </el-alert>

    <el-skeleton v-if="loading" :rows="4" animated />

    <div v-else class="exam-list">
      <el-card
        v-for="exam in exams"
        :key="exam.year"
        shadow="hover"
        class="exam-card"
        @click="startMockExam(exam)"
      >
        <div class="exam-header">
          <div class="exam-icon">🏆</div>
          <div class="exam-year">{{ exam.year }}</div>
        </div>
        <h3 class="exam-name">{{ exam.name }}</h3>
        <div class="exam-stats">
          <div class="stat-item">
            <div class="stat-value">{{ exam.count }}</div>
            <div class="stat-label">总题数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ exam.singleCount }}</div>
            <div class="stat-label">单选题</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ exam.multipleCount }}</div>
            <div class="stat-label">多选题</div>
          </div>
        </div>
        <el-button type="danger" size="large" style="width: 100%; margin-top: 15px">
          开始模拟考试
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.exam-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.exam-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s;
}

.exam-card:hover {
  transform: translateY(-5px);
}

.exam-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 15px;
}

.exam-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.exam-year {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.exam-name {
  font-size: 18px;
  margin: 10px 0 20px;
  color: #333;
}

.exam-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}
</style>
