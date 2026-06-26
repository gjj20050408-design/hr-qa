<template>
  <div class="corrections-view">
    <el-select v-model="statusFilter" size="default" class="mb-filter">
      <el-option label="待审核" value="pending" />
      <el-option label="已通过" value="approved" />
      <el-option label="已驳回" value="rejected" />
    </el-select>

    <div class="corr-list">
      <div v-for="item in filteredCorrections" :key="item.request_id" class="corr-card">
        <div class="corr-header">
          <el-tag :type="item.status==='pending'?'warning':item.status==='approved'?'success':'danger'" size="small">
            {{ item.status==='pending'?'待审核':item.status==='approved'?'已通过':'已驳回' }}
          </el-tag>
          <span class="corr-meta">{{ item.submitter_name }} · {{ item.created_at }}</span>
        </div>
        <p class="corr-doc">文档：{{ item.document_title }} · {{ item.section }}</p>
        <p class="corr-desc">{{ item.description }}</p>
        <div class="corr-actions" v-if="item.status === 'pending'">
          <el-button type="success" size="small">通过</el-button>
          <el-button type="danger" size="small">驳回</el-button>
        </div>
      </div>
      <el-empty v-if="!filteredCorrections.length" description="暂无纠错申请" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const statusFilter = ref('pending')

const corrections = ref([
  { request_id:'c1',document_id:'doc-001',document_title:'年假天数与工龄计算规定',section:'第二条',description:'"工龄1-10年享5天" 应注明包含试用期。',submitted_by:'',submitter_name:'张三',status:'pending',created_at:'2026-06-23' },
])

const filteredCorrections = computed(() =>
  corrections.value.filter(c => statusFilter.value === c.status)
)
</script>

<style scoped>
.corrections-view { max-width: 1000px; }
.mb-filter { margin-bottom:16px; }
.corr-list { display:flex; flex-direction:column; gap:12px; }
.corr-card { background:white; border:1px solid var(--border); border-radius:12px; padding:20px; }
.corr-header { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
.corr-meta { font-size:12px; color:#94a3b8; }
.corr-doc { font-size:14px; color:#334155; margin-bottom:4px; }
.corr-desc { font-size:13px; color:#475569; background:var(--surface-muted); padding:12px; border-radius:8px; margin-top:8px; }
.corr-actions { display:flex; gap:8px; margin-top:12px; padding-top:12px; border-top:1px solid var(--border-light); }
</style>
