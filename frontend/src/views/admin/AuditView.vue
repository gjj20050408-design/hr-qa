<template>
  <div class="audit-view">
    <div class="toolbar">
      <h3>审计日志</h3>
      <div class="toolbar-right">
        <el-select v-model="actionFilter" size="default" class="tool-select">
          <el-option label="全部操作" value="all" />
          <el-option label="登录" value="login" />
          <el-option label="文档操作" value="document" />
          <el-option label="问答记录" value="qa" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索..." :prefix-icon="Search" size="default" class="search-input" />
      </div>
    </div>
    <div class="table-card">
      <el-table :data="filteredLogs" stripe>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="action" label="操作类型" width="150">
          <template #default="{row}">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="detail" label="操作详情" min-width="200" />
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="170" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getAuditLogs } from '@/api/admin'

const searchText = ref('')
const actionFilter = ref('all')
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)

async function loadLogs() {
  try {
    const params: any = { page: page.value, page_size: 50 }
    if (actionFilter.value !== 'all') params.action = actionFilter.value
    if (searchText.value) params.resource_id = searchText.value
    const res = await getAuditLogs(params)
    logs.value = res.data?.items || []
    total.value = res.data?.pagination?.total || 0
  } catch {}
}

onMounted(loadLogs)

const filteredLogs = computed(() => logs.value)
</script>

<style scoped>
.audit-view { max-width:1400px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px; }
.toolbar h3 { font-size:18px; font-weight:700; color:var(--primary); }
.toolbar-right { display:flex; gap:12px; align-items:center; }
.tool-select { width:130px; }
.search-input { width:200px; }
.table-card { background:white; border:1px solid var(--border); border-radius:12px; overflow:hidden; }
</style>
