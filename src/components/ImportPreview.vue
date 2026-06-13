<script setup lang="ts">
import type { ImportPreview } from '../types/question'

defineProps<{ preview: ImportPreview }>()
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <strong>导入预览</strong>
        <el-space>
          <el-tag type="success">可新增 {{ preview.addedCount }}</el-tag>
          <el-tag type="warning">重复 {{ preview.duplicateCount }}</el-tag>
          <el-tag type="danger">无效 {{ preview.invalidCount }}</el-tag>
        </el-space>
      </div>
    </template>

    <el-table :data="preview.items" max-height="360">
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="!row.valid" type="danger">无效</el-tag>
          <el-tag v-else-if="row.duplicate" type="warning">重复</el-tag>
          <el-tag v-else type="success">可导入</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="题干" min-width="280">
        <template #default="{ row }">{{ row.question?.stem || row.raw.stem }}</template>
      </el-table-column>
      <el-table-column label="问题" min-width="260">
        <template #default="{ row }">{{ row.errors.join('；') || '—' }}</template>
      </el-table-column>
    </el-table>
  </el-card>
</template>
