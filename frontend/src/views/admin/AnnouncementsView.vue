<template>
  <div class="announcements-view">
    <div class="toolbar">
      <h3>通知公告管理</h3>
      <el-button type="primary"><el-icon><Plus /></el-icon>发布公告</el-button>
    </div>
    <div class="ann-list">
      <div v-for="item in announcements" :key="item.announcement_id" class="ann-card">
        <div class="ann-title-row">
          <h4>{{ item.title }}</h4>
          <div class="ann-tags">
            <el-tag :type="item.priority==='urgent'?'danger':item.priority==='important'?'warning':'info'" size="small">
              {{ item.priority==='urgent'?'紧急':item.priority==='important'?'重要':'公告' }}
            </el-tag>
            <el-tag size="small">{{ item.target_type==='all'?'全员':item.target_type }}</el-tag>
          </div>
        </div>
        <p class="ann-meta">已发布 · {{ item.published_at }}</p>
      </div>
      <el-empty v-if="!announcements.length" description="暂无公告" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const announcements = ref([
  { announcement_id:'a1',title:'关于2026年度体检安排',priority:'important',target_type:'all',published_at:'2026-06-20' },
])
</script>

<style scoped>
.announcements-view { max-width:1000px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.toolbar h3 { font-size:18px; font-weight:700; color:var(--primary); }
.ann-list { display:flex; flex-direction:column; gap:12px; }
.ann-card { background:white; border:1px solid var(--border); border-radius:12px; padding:20px; }
.ann-title-row { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.ann-title-row h4 { font-size:14px; font-weight:600; color:var(--primary); }
.ann-tags { display:flex; gap:8px; }
.ann-meta { font-size:12px; color:#94a3b8; }
</style>
