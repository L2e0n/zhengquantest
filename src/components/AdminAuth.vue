<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  onSuccess: () => void
}>()

const password = ref('')
const loading = ref(false)

const ADMIN_PASSWORD = '123!Wheelsup*'

function handleSubmit() {
  if (!password.value) {
    ElMessage.warning('请输入管理员密码')
    return
  }

  loading.value = true

  setTimeout(() => {
    if (password.value === ADMIN_PASSWORD) {
      sessionStorage.setItem('admin_auth', 'true')
      ElMessage.success('验证成功')
      props.onSuccess()
    } else {
      ElMessage.error('密码错误')
      password.value = ''
    }
    loading.value = false
  }, 300)
}
</script>

<template>
  <div class="admin-auth-overlay">
    <el-card class="auth-card">
      <template #header>
        <div class="card-header">
          <span>管理员验证</span>
        </div>
      </template>
      <el-form @submit.prevent="handleSubmit">
        <el-form-item label="密码">
          <el-input
            v-model="password"
            type="password"
            placeholder="请输入管理员密码"
            show-password
            @keyup.enter="handleSubmit"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit" style="width: 100%">
            验证
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.admin-auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.auth-card {
  width: 400px;
  max-width: 90%;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}
</style>
