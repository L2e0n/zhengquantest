<script setup lang="ts">
import type { QuestionFilters } from '../types/question'
import { questionTypeLabels, sectionLabels } from '../utils/normalize'

const props = defineProps<{
  modelValue: QuestionFilters
  chapters: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: QuestionFilters]
}>()

function patch(value: Partial<QuestionFilters>) {
  emit('update:modelValue', { ...props.modelValue, ...value })
}
</script>

<template>
  <el-card shadow="never" class="filters-card">
    <el-form label-position="top">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="关键词">
            <el-input :model-value="modelValue.keyword" clearable placeholder="题干/解析/标签" @input="patch({ keyword: String($event) })" />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="科目">
            <el-select :model-value="modelValue.section" clearable placeholder="全部" @change="patch({ section: $event, chapter: undefined })">
              <el-option v-for="(label, value) in sectionLabels" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="章节">
            <el-select :model-value="modelValue.chapter" clearable filterable placeholder="全部" @change="patch({ chapter: $event })">
              <el-option v-for="chapter in chapters" :key="chapter" :label="chapter" :value="chapter" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-form-item label="题型">
            <el-select :model-value="modelValue.type" clearable placeholder="全部" @change="patch({ type: $event })">
              <el-option v-for="(label, value) in questionTypeLabels" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-space wrap>
        <el-checkbox :model-value="modelValue.wrongOnly" @change="patch({ wrongOnly: Boolean($event) })">只看错题</el-checkbox>
        <el-checkbox :model-value="modelValue.favoriteOnly" @change="patch({ favoriteOnly: Boolean($event) })">只看收藏</el-checkbox>
        <el-checkbox :model-value="modelValue.includeMastered" @change="patch({ includeMastered: Boolean($event) })">包含已掌握错题</el-checkbox>
      </el-space>
    </el-form>
  </el-card>
</template>
