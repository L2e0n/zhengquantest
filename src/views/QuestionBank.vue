<script setup lang="ts">
import { onMounted, watch } from 'vue'
import QuestionCard from '../components/QuestionCard.vue'
import QuestionFilters from '../components/QuestionFilters.vue'
import { useQuestionsStore } from '../stores/questions'

const store = useQuestionsStore()

watch(
  () => ({ ...store.filters }),
  () => store.refresh(),
  { deep: true },
)

onMounted(store.refresh)
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>题库</h1>
        <p>搜索、筛选、收藏本地题目。</p>
      </div>
      <el-tag size="large">{{ store.questions.length }} 题</el-tag>
    </div>

    <QuestionFilters v-model="store.filters" :chapters="store.chapters" />

    <el-empty v-if="!store.questions.length" description="暂无题目，请先导入题库" />
    <div v-else class="question-list">
      <div v-for="question in store.questions" :key="question.id" class="question-actions-block">
        <QuestionCard :question="question" :progress="store.progressMap.get(question.id)" show-answer />
        <el-space class="inline-actions">
          <el-button size="small" @click="store.toggleQuestionFavorite(question.id)">
            {{ store.progressMap.get(question.id)?.favorite ? '取消收藏' : '收藏' }}
          </el-button>
        </el-space>
      </div>
    </div>
  </div>
</template>
