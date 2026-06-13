import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import './styles/index.scss'
import App from './App.vue'
import { router } from './router'
import { initializeQuestions } from './services/initQuestions'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 应用启动时自动初始化题库
initializeQuestions().then(result => {
  if (result.success) {
    console.log(`📚 题库就绪：${result.count} 道题目`)
  } else {
    console.warn('⚠️ 题库加载失败:', result.message)
  }
})

app.mount('#app')
