<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '../db'
import type { ExamSection } from '../types/question'
import { sectionLabels } from '../utils/normalize'

const route = useRoute()
const router = useRouter()
const section = ref<ExamSection>((route.query.section as ExamSection) || 'finance_basic')

interface ExamPaper {
  name: string
  count: number
}

const papers = ref<ExamPaper[]>([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  const questions = await db.questions
    .where('section')
    .equals(section.value)
    .toArray()

  // 筛选考前点题
  const examQuestions = questions.filter(q => q.chapter?.includes('考前点题'))

  // 统计题数（假设每套试卷大约100题）
  const totalCount = examQuestions.length
  papers.value = [
    { name: '考前点题卷一', count: Math.floor(totalCount / 3) },
    { name: '考前点题卷二', count: Math.floor(totalCount / 3) },
    { name: '考前点题卷三', count: totalCount - Math.floor(totalCount / 3) * 2 },
  ].filter(p => p.count > 0)

  loading.value = false
})

function startPaper(paperName: string) {
  router.push({
    path: '/quiz',
    query: {
      section: section.value,
      chapter: '考前点题',
      mode: 'exam'
    }
  })
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>🎯 考前点题</h1>
        <p>{{ sectionLabels[section] }} - 考前冲刺必做题</p>
      </div>
      <el-button @click="router.push({ path: '/practice-mode', query: { section } })">
        ← 返回
      </el-button>
    </div>

    <el-alert type="info" :closable="false" style="margin-bottom: 20px">
      <template #title>
        考前点题是根据考试大纲和历年真题精心编制的冲刺题库，帮助你在短时间内掌握考试重点。
      </template>
    </el-alert>

    <el-skeleton v-if="loading" :rows="3" animated />

    <div v-else class="paper-list">
      <el-card
        v-for="paper in papers"
        :key="paper.name"
        shadow="hover"
        class="paper-card"
        @click="startPaper(paper.name)"
      >
        <div class="paper-icon">📄</div>
        <h3 class="paper-name">{{ paper.name }}</h3>
        <div class="paper-count">
          <el-statistic :value="paper.count" suffix="题" />
        </div>
        <el-button type="warning" size="large" style="width: 100%; margin-top: 15px">
          开始练习
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.paper-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.paper-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s;
}

.paper-card:hover {
  transform: translateY(-5px);
}

.paper-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.paper-name {
  font-size: 18px;
  margin: 10px 0;
  color: #333;
}

.paper-count {
  margin: 15px 0;
}
</style>
