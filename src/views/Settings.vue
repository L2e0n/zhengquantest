<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { clearAllData, clearProgressOnly, downloadJson, exportBackup, importBackup } from '../services/questionService'

async function exportData() {
  const backup = await exportBackup()
  downloadJson(backup, `zhengquantest-backup-${new Date().toISOString().slice(0, 10)}.json`)
}

async function handleBackup(file: File) {
  const backup = JSON.parse(await file.text())
  await importBackup(backup)
  ElMessage.success('备份已导入')
  return false
}

async function confirmClearAll() {
  await ElMessageBox.confirm('这会删除全部题库和答题记录，确认继续？', '清空全部数据', { type: 'warning' })
  await clearAllData()
  ElMessage.success('已清空全部数据')
}

async function confirmClearProgress() {
  await ElMessageBox.confirm('这会保留题库，但删除错题、收藏和答题记录，确认继续？', '清空进度', { type: 'warning' })
  await clearProgressOnly()
  ElMessage.success('已清空做题进度')
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>设置与备份</h1>
        <p>浏览器本地数据可能因清理缓存丢失，建议定期导出备份。</p>
      </div>
    </div>

    <el-card shadow="never">
      <template #header><strong>数据备份</strong></template>
      <el-space wrap>
        <el-button type="primary" @click="exportData">导出全部数据</el-button>
        <el-upload accept="application/json,.json" :auto-upload="false" :show-file-list="false" :before-upload="handleBackup">
          <el-button>导入备份</el-button>
        </el-upload>
      </el-space>
    </el-card>

    <el-card shadow="never" class="section-card">
      <template #header><strong>危险操作</strong></template>
      <el-space wrap>
        <el-button type="warning" @click="confirmClearProgress">仅清空做题记录</el-button>
        <el-button type="danger" @click="confirmClearAll">清空全部数据</el-button>
      </el-space>
    </el-card>
  </div>
</template>
