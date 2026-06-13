<script setup lang="ts">
import { ref } from 'vue'
import ImportPreview from '../components/ImportPreview.vue'
import { useQuestionsStore } from '../stores/questions'

const store = useQuestionsStore()
const selectedFileName = ref('')
const loading = ref(false)

async function handleFile(file: File) {
  loading.value = true
  selectedFileName.value = file.name
  try {
    await store.previewFile(file)
  } finally {
    loading.value = false
  }
  return false
}

async function importSample() {
  loading.value = true
  try {
    const response = await fetch('/sample-questions.json')
    const blob = new Blob([await response.text()], { type: 'application/json' })
    const file = new File([blob], 'sample-questions.json', { type: 'application/json' })
    await handleFile(file)
  } finally {
    loading.value = false
  }
}

async function confirm() {
  if (!selectedFileName.value) return
  await store.confirmImport(selectedFileName.value)
}
</script>

<template>
  <div class="page">
    <div class="page-title">
      <div>
        <h1>导入题库</h1>
        <p>支持 JSON 数组格式，导入前会校验字段并按内容去重。</p>
      </div>
      <el-button @click="importSample">加载示例题</el-button>
    </div>

    <el-card shadow="never">
      <el-upload drag accept="application/json,.json" :auto-upload="false" :show-file-list="false" :before-upload="handleFile">
        <div class="upload-text">拖拽 JSON 文件到此处，或点击选择文件</div>
        <template #tip>
          <div class="el-upload__tip">顶层必须是题目数组。每题建议包含 section、type、stem、options、answer、explanation、source。</div>
        </template>
      </el-upload>
    </el-card>

    <ImportPreview v-if="store.preview" :preview="store.preview" class="section-card" />

    <div v-if="store.preview" class="toolbar">
      <el-button type="primary" :disabled="store.preview.addedCount === 0" :loading="loading" @click="confirm">确认导入 {{ store.preview.addedCount }} 题</el-button>
      <el-button @click="store.preview = null">取消</el-button>
    </div>
  </div>
</template>
