<script setup lang="ts">
const menus = [
  { path: '/', label: '首页' },
  { path: '/subject', label: '刷题' },
  { path: '/questions', label: '题库' },
  { path: '/wrong', label: '错题本' },
  { path: '/import', label: '导入' },
  { path: '/settings', label: '设置' },
]
</script>

<template>
  <el-container class="app-shell">
    <el-aside width="236px" class="sidebar">
      <div class="brand">
        <strong>证券从业题库</strong>
        <span>本地练习站</span>
      </div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          {{ item.label }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div>
          <strong>金融基础知识 / 证券市场基本法律法规</strong>
          <p>题库和答题记录仅保存在当前浏览器本地 IndexedDB。</p>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
