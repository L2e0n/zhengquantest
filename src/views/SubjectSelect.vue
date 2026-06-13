<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionsStore } from '../stores/questions'
import type { ExamSection } from '../types/question'

const router = useRouter()
const store = useQuestionsStore()

const sections = [
  {
    key: 'finance_basic' as ExamSection,
    name: '金融市场基础知识',
    color: '#409eff',
    icon: '📈'
  },
  {
    key: 'securities_law' as ExamSection,
    name: '证券市场基本法律法规',
    color: '#f56c6c',
    icon: '⚖️'
  }
]

const stats = computed(() => ({
  finance_basic: store.counts.finance,
  securities_law: store.counts.law
}))

onMounted(async () => {
  await store.refresh()
})

function goToMode(section: ExamSection) {
  router.push({ path: '/practice-mode', query: { section } })
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <h1>💡 科目选择</h1>
      <p>选择你要练习的科目</p>
    </div>

    <div class="section-grid">
      <el-card
        v-for="section in sections"
        :key="section.key"
        shadow="hover"
        class="section-card-item"
        :body-style="{ padding: '40px' }"
        @click="goToMode(section.key)"
      >
        <div class="section-icon">{{ section.icon }}</div>
        <h2 class="section-name">{{ section.name }}</h2>
        <div class="section-stats">
          <el-statistic :value="stats[section.key]" suffix="题" />
        </div>
        <el-button type="primary" :style="{ background: section.color, borderColor: section.color }" size="large" style="width: 100%; margin-top: 20px">
          开始练习
        </el-button>
      </el-card>
    </div>

    <el-card shadow="never" style="margin-top: 30px">
      <template #header><strong>快速入口</strong></template>
      <el-space wrap>
        <el-button type="danger" @click="router.push('/wrong')">错题本</el-button>
        <el-button @click="router.push('/questions')">题库浏览</el-button>
        <el-button @click="router.push('/import')">导入题目</el-button>
      </el-space>
    </el-card>
  </div>
</template>

<style scoped>
.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.section-card-item {
  cursor: pointer;
  transition: transform 0.2s;
  text-align: center;
}

.section-card-item:hover {
  transform: translateY(-5px);
}

.section-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.section-name {
  font-size: 22px;
  margin: 15px 0;
  color: #333;
}

.section-stats {
  margin: 20px 0;
}
</style>
