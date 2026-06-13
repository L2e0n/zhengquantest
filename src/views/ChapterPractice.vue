<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { db } from '../db'
import type { ExamSection, Question } from '../types/question'
import { sectionLabels } from '../utils/normalize'

const route = useRoute()
const router = useRouter()
const section = ref<ExamSection>((route.query.section as ExamSection) || 'finance_basic')

interface SectionDetail {
  name: string
  fullPath: string
  singleCount: number
  multipleCount: number
  trueFalseCount: number
  totalCount: number
}

interface ChapterGroup {
  name: string
  sections: SectionDetail[]
  totalCount: number
}

const chapterGroups = ref<ChapterGroup[]>([])
const loading = ref(true)

// 中文数字映射
const chineseNumbers: Record<string, number> = {
  '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
  '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
}

function parseChapterNumber(chapterName: string): number {
  const match = chapterName.match(/第([一二三四五六七八九十]+)章/)
  if (match) {
    return chineseNumbers[match[1]] || 0
  }
  return 0
}

onMounted(async () => {
  loading.value = true
  const questions = await db.questions
    .where('section')
    .equals(section.value)
    .toArray()

  // 过滤掉考前点题和真题
  const chapterQuestions = questions.filter(
    q => !q.chapter?.includes('考前点题') && !q.chapter?.includes('真题')
  )

  // 按章节分组
  const chapterMap = new Map<string, Map<string, Question[]>>()

  chapterQuestions.forEach(q => {
    if (!q.chapter) return

    const parts = q.chapter.split('/')
    const mainChapter = parts[0] // "第一章 金融市场体系"

    if (!chapterMap.has(mainChapter)) {
      chapterMap.set(mainChapter, new Map())
    }

    const sectionMap = chapterMap.get(mainChapter)!
    if (!sectionMap.has(q.chapter)) {
      sectionMap.set(q.chapter, [])
    }
    sectionMap.get(q.chapter)!.push(q)
  })

  // 转换为数组并统计
  chapterGroups.value = Array.from(chapterMap.entries())
    .map(([mainChapter, sectionMap]) => {
      const sections = Array.from(sectionMap.entries())
        .map(([fullPath, questions]) => {
          const singleCount = questions.filter(q => q.type === 'single').length
          const multipleCount = questions.filter(q => q.type === 'multiple').length
          const trueFalseCount = questions.filter(q => q.type === 'true_false').length

          return {
            name: fullPath.split('/')[1] || fullPath,
            fullPath,
            singleCount,
            multipleCount,
            trueFalseCount,
            totalCount: questions.length
          }
        })
        .sort((a, b) => {
          // 按节号排序
          const aMatch = a.name.match(/第([一二三四五六七八九十]+)节/)
          const bMatch = b.name.match(/第([一二三四五六七八九十]+)节/)
          if (aMatch && bMatch) {
            return chineseNumbers[aMatch[1]] - chineseNumbers[bMatch[1]]
          }
          return 0
        })

      const totalCount = sections.reduce((sum, s) => sum + s.totalCount, 0)

      return {
        name: mainChapter,
        sections,
        totalCount
      }
    })
    .sort((a, b) => parseChapterNumber(a.name) - parseChapterNumber(b.name))

  loading.value = false
})

function startSection(sec: SectionDetail, type?: 'single' | 'multiple' | 'true_false') {
  const query: any = {
    section: section.value,
    chapter: sec.fullPath,
    mode: 'chapter'
  }

  if (type) {
    query.type = type
    // 按题型练习时，使用该题型的总数作为 limit
    const count = type === 'single' ? sec.singleCount :
                  type === 'multiple' ? sec.multipleCount :
                  sec.trueFalseCount
    query.limit = count
  } else {
    // 全部练习时，使用该节的总题数
    query.limit = sec.totalCount
  }

  router.push({ path: '/quiz', query })
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>📚 章节练习</h1>
        <p>{{ sectionLabels[section] }} - 按章节系统学习</p>
      </div>
      <el-button @click="router.push({ path: '/practice-mode', query: { section } })">
        ← 返回
      </el-button>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated />

    <div v-else class="chapter-list">
      <el-card v-for="group in chapterGroups" :key="group.name" shadow="never" class="chapter-group">
        <template #header>
          <div class="group-header">
            <strong>{{ group.name }}</strong>
            <el-tag>{{ group.totalCount }}题</el-tag>
          </div>
        </template>

        <div class="section-list">
          <div
            v-for="sec in group.sections"
            :key="sec.fullPath"
            class="section-item"
          >
            <div class="section-header">
              <span class="section-name">{{ sec.name }}</span>
              <el-tag type="info" size="small">共{{ sec.totalCount }}题</el-tag>
            </div>

            <div class="section-types">
              <el-button
                size="small"
                @click="startSection(sec)"
              >
                全部练习
              </el-button>
              <el-button
                v-if="sec.singleCount > 0"
                type="primary"
                size="small"
                plain
                @click="startSection(sec, 'single')"
              >
                单选 {{ sec.singleCount }}题
              </el-button>
              <el-button
                v-if="sec.multipleCount > 0"
                type="success"
                size="small"
                plain
                @click="startSection(sec, 'multiple')"
              >
                多选 {{ sec.multipleCount }}题
              </el-button>
              <el-button
                v-if="sec.trueFalseCount > 0"
                type="warning"
                size="small"
                plain
                @click="startSection(sec, 'true_false')"
              >
                判断 {{ sec.trueFalseCount }}题
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chapter-group {
  border-left: 4px solid #409eff;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-item {
  padding: 15px;
  border-radius: 8px;
  background: #f9f9f9;
  transition: all 0.2s;
}

.section-item:hover {
  background: #ecf5ff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.section-types {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
