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
      <el-table :data="filteredLogs" stripe v-loading="loading">
        <el-table-column label="用户" width="140">
          <template #default="{row}">
            {{ row.user_name || '-' }}
            <span v-if="row.employee_id" class="emp-id">({{ row.employee_id }})</span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="150">
          <template #default="{row}">
            <el-tag size="small">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column label="操作详情" min-width="200">
          <template #default="{row}">
            <span class="detail-text">{{ formatDetail(row.detail) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="170">
          <template #default="{row}">{{ row.created_at?.slice(0, 19).replace('T', ' ') || '-' }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          :current-page="page"
          :page-size="50"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="(p: number) => { page = p; loadLogs() }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getAuditLogs } from '@/api/admin'

const searchText = ref('')
const actionFilter = ref('all')
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

// 下拉分类 → 后端精确 action 值（后端按 action 精确匹配）
const ACTION_GROUPS: Record<string, string[]> = {
  login: ['login_success', 'login_failed'],
  document: ['document_create', 'document_update', 'document_archive', 'document_restore', 'document_delete'],
  user: ['user_register', 'user_import', 'user_update', 'user_disable'],
}

// action 值 → 中文标签
const ACTION_LABELS: Record<string, string> = {
  login_success: '登录成功',
  login_failed: '登录失败',
  change_password: '修改密码',
  user_register: '用户注册',
  user_import: '导入用户',
  user_update: '修改用户',
  user_disable: '禁用用户',
  document_create: '创建文档',
  document_update: '更新文档',
  document_archive: '归档文档',
  document_restore: '恢复文档',
  document_delete: '删除文档',
  faq_create: '创建FAQ',
  faq_update: '更新FAQ',
  faq_archive: '归档FAQ',
  permission_filtered: '权限过滤',
  personal_data_denied: '越权访问被拒',
}

function actionLabel(action: string): string {
  return ACTION_LABELS[action] || action
}

function formatDetail(detail: any): string {
  if (!detail) return '-'
  if (typeof detail === 'string') return detail
  try {
    const parts = Object.entries(detail).map(([k, v]) => {
      const val = typeof v === 'object' ? JSON.stringify(v) : v
      return `${k}: ${val}`
    })
    return parts.join('，') || '-'
  } catch {
    return '-'
  }
}

async function loadLogs() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: 50 }
    // 分类下拉：单个 action 直接传；一类多个 action 时后端不支持批量，取第一个仍不够——改为前端过滤
    if (actionFilter.value !== 'all' && ACTION_GROUPS[actionFilter.value]?.length === 1) {
      params.action = ACTION_GROUPS[actionFilter.value][0]
    }
    if (searchText.value) params.resource_id = searchText.value
    const res = await getAuditLogs(params)
    const data = res.data?.data || res.data || {}
    logs.value = data.items || []
    total.value = data.pagination?.total || 0
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

// 切换分类/搜索时回到第一页重新加载
watch([actionFilter, searchText], () => {
  page.value = 1
  loadLogs()
})

onMounted(loadLogs)

// 分类含多个 action 时，后端无法一次过滤，这里做前端二次过滤
const filteredLogs = computed(() => {
  if (actionFilter.value === 'all') return logs.value
  const group = ACTION_GROUPS[actionFilter.value]
  if (!group || group.length <= 1) return logs.value
  return logs.value.filter((l) => group.includes(l.action))
})
</script>

<style scoped>
.audit-view { max-width:1400px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px; }
.toolbar h3 { font-size:18px; font-weight:700; color:var(--primary); }
.toolbar-right { display:flex; gap:12px; align-items:center; }
.tool-select { width:130px; }
.search-input { width:200px; }
.table-card { background:white; border:1px solid var(--border); border-radius:12px; overflow:hidden; }
.emp-id { color:var(--text-secondary,#909399); font-size:12px; }
.detail-text { color:var(--text-secondary,#606266); font-size:13px; word-break:break-all; }
.pagination-wrapper { display:flex; justify-content:flex-end; padding:16px; }
</style>
