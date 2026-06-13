<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import QuestionCard from '../components/QuestionCard.vue'
import QuestionFilters from '../components/QuestionFilters.vue'
import { markMastered } from '../services/questionService'
import { useQuestionsStore } from '../stores/questions'

const router = useRouter()
const store = useQuestionsStore()

async function refreshWrong() {
  store.filters.wrongOnly = true
  await store.refresh()
}

async function master(questionId: string) {
  await markMastered(questionId, true)
  await refreshWrong()
}

watch(
  () => ({ ...store.filters }),
  () => refreshWrong(),
  { deep: true },
)

onMounted(refreshWrong)
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>错题本</h1>
        <p>答错题目会自动进入这里，掌握后可隐藏但保留历史记录。</p>
      </div>
      <el-button type="danger" @click="router.push({ path: '/quiz', query: { mode: 'wrong' } })">错题复习</el-button>
    </div>

    <QuestionFilters v-model="store.filters" :chapters="store.chapters" />

    <el-empty v-if="!store.questions.length" description="暂无未掌握错题" />
    <div v-else class="question-list">
      <div v-for="question in store.questions" :key="question.id" class="question-actions-block">
        <QuestionCard :question="question" :progress="store.progressMap.get(question.id)" show-answer />
        <el-space class="inline-actions">
          <el-button size="small" type="success" @click="master(question.id)">标记已掌握</el-button>
          <el-button size="small" @click="store.toggleQuestionFavorite(question.id)">
            {{ store.progressMap.get(question.id)?.favorite ? '取消收藏' : '收藏' }}
          </el-button>
        </el-space>
      </div>
    </div>
  </div>
</template>
