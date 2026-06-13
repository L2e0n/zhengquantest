<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '../db'
import type { ExamSection } from '../types/question'
import { sectionLabels } from '../utils/normalize'

const route = useRoute()
const router = useRouter()
const section = ref<ExamSection>((route.query.section as ExamSection) || 'finance_basic')

const sectionName = computed(() => sectionLabels[section.value])

// 统计数据
const chapterCount = ref(0)
const examCount = ref(0)
const mockCount = ref(0)

const modes = computed(() => [
  {
    key: 'chapter',
    name: '章节练习',
    icon: '📚',
    description: '按章节系统学习，逐个击破知识点',
    count: chapterCount.value,
    color: '#409eff',
    route: '/chapter-practice'
  },
  {
    key: 'exam',
    name: '考前点题',
    icon: '🎯',
    description: '考前冲刺必做题，掌握考试重点',
    count: examCount.value,
    color: '#e6a23c',
    route: '/exam-practice'
  },
  {
    key: 'mock',
    name: '真题模拟',
    icon: '📝',
    description: '真实考试题型，100题限时模拟',
    count: mockCount.value,
    color: '#f56c6c',
    route: '/mock-exam'
  }
])

onMounted(async () => {
  // 统计各模式题目数量
  const questions = await db.questions.where('section').equals(section.value).toArray()

  // 章节练习：排除考前点题和真题
  chapterCount.value = questions.filter(q =>
    !q.chapter?.includes('考前点题') &&
    !q.chapter?.includes('真题')
  ).length

  // 考前点题
  examCount.value = questions.filter(q => q.chapter?.includes('考前点题')).length

  // 真题模拟
  mockCount.value = questions.filter(q => q.chapter?.includes('真题')).length
})

function goToMode(mode: typeof modes.value[0]) {
  router.push({ path: mode.route, query: { section: section.value } })
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>{{ sectionName }}</h1>
        <p>选择练习模式</p>
      </div>
      <el-button @click="router.push('/subject')">← 返回科目选择</el-button>
    </div>

    <div class="mode-grid">
      <el-card
        v-for="mode in modes"
        :key="mode.key"
        shadow="hover"
        class="mode-card"
        :body-style="{ padding: '35px' }"
        @click="goToMode(mode)"
      >
        <div class="mode-icon">{{ mode.icon }}</div>
        <h2 class="mode-name">{{ mode.name }}</h2>
        <p class="mode-desc">{{ mode.description }}</p>
        <div class="mode-count">
          <el-statistic :value="mode.count" suffix="题" />
        </div>
        <el-button
          type="primary"
          :style="{ background: mode.color, borderColor: mode.color }"
          size="large"
          style="width: 100%; margin-top: 20px"
        >
          进入练习
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.mode-card {
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.mode-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.mode-icon {
  font-size: 56px;
  margin-bottom: 15px;
}

.mode-name {
  font-size: 20px;
  margin: 10px 0;
  color: #333;
}

.mode-desc {
  color: #666;
  font-size: 14px;
  margin: 10px 0;
  min-height: 40px;
}

.mode-count {
  margin: 15px 0;
}
</style>
