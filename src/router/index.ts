import { createRouter, createWebHashHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import ImportQuestions from '../views/ImportQuestions.vue'
import QuestionBank from '../views/QuestionBank.vue'
import Quiz from '../views/Quiz.vue'
import Settings from '../views/Settings.vue'
import WrongBook from '../views/WrongBook.vue'
import SubjectSelect from '../views/SubjectSelect.vue'
import PracticeMode from '../views/PracticeMode.vue'
import ChapterPractice from '../views/ChapterPractice.vue'
import ExamPractice from '../views/ExamPractice.vue'
import MockExam from '../views/MockExam.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: Dashboard },
        { path: 'subject', name: 'subject', component: SubjectSelect },
        { path: 'practice-mode', name: 'practice-mode', component: PracticeMode },
        { path: 'chapter-practice', name: 'chapter-practice', component: ChapterPractice },
        { path: 'exam-practice', name: 'exam-practice', component: ExamPractice },
        { path: 'mock-exam', name: 'mock-exam', component: MockExam },
        { path: 'questions', name: 'questions', component: QuestionBank },
        { path: 'quiz', name: 'quiz', component: Quiz },
        { path: 'wrong', name: 'wrong', component: WrongBook },
        { path: 'import', name: 'import', component: ImportQuestions },
        { path: 'settings', name: 'settings', component: Settings },
      ],
    },
  ],
})
