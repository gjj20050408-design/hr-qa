<template>
  <div class="users-view">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h3>用户管理</h3>
        <el-input
          v-model="searchText"
          placeholder="搜索工号或姓名..."
          :prefix-icon="Search"
          size="default"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        />
      </div>
      <el-button type="primary" @click="openImportDialog">
        <el-icon><Upload /></el-icon>导入员工
      </el-button>
    </div>

    <!-- 用户表格 -->
    <div class="table-card" v-loading="loading">
      <el-table :data="users" stripe style="width: 100%">
        <el-table-column prop="employee_id" label="工号" width="110" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="department_name" label="部门" width="140" show-overflow-tooltip />
        <el-table-column label="角色" width="110">
          <template #default="{ row }">
            <el-tag
              :type="roleTagType(row.role)"
              size="small"
            >
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="job_level" label="职级" width="90" />
        <el-table-column label="入职日期" width="110">
          <template #default="{ row }">{{ row.hire_date?.slice(0, 10) || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadUsers"
          @size-change="loadUsers"
        />
      </div>
    </div>

    <!-- 导入员工弹窗 -->
    <el-dialog
      v-model="importVisible"
      title="导入员工"
      width="560px"
      :close-on-click-modal="false"
      @closed="resetImport"
    >
      <div class="import-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleImportFileChange"
          :on-remove="handleImportFileRemove"
          accept=".xlsx,.xls"
          drag
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx / .xls 格式，文件需包含工号、姓名、部门、职级等字段
            </div>
          </template>
        </el-upload>
      </div>

      <div style="margin-top: 12px">
        <el-button
          type="primary"
          :loading="importSubmitting"
          :disabled="!importFile"
          @click="handleImport"
        >
          开始导入
        </el-button>
      </div>

      <!-- 导入结果 -->
      <div v-if="importResult" class="import-result">
        <el-alert
          :type="importResult.fail > 0 ? 'warning' : 'success'"
          :closable="false"
          show-icon
        >
          <template #title>
            导入完成：成功 <strong>{{ importResult.success }}</strong> 人，
            失败 <strong>{{ importResult.fail }}</strong> 人
          </template>
        </el-alert>

        <!-- 失败详情 -->
        <div v-if="importResult.errors && importResult.errors.length" class="import-errors">
          <h5>失败详情：</h5>
          <el-table :data="importResult.errors" size="small" stripe max-height="200">
            <el-table-column prop="row" label="行号" width="60" />
            <el-table-column prop="employee_id" label="工号" width="100" />
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="reason" label="失败原因" min-width="150" show-overflow-tooltip />
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button @click="importVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Upload, UploadFilled } from '@element-plus/icons-vue'
import { getUsers, importEmployees } from '@/api/admin'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'

// ── 搜索 ──
const searchText = ref('')

// ── 表格 ──
const users = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// ── 导入弹窗 ──
const importVisible = ref(false)
const importFile = ref<File | null>(null)
const importSubmitting = ref(false)
const importResult = ref<{
  success: number
  fail: number
  errors: { row: number; employee_id: string; name: string; reason: string }[]
} | null>(null)

// ── 辅助方法 ──
function roleTagType(role: string): 'danger' | 'warning' | 'info' {
  if (role === 'admin') return 'danger'
  if (role === 'hr_specialist') return 'warning'
  return 'info'
}

function roleLabel(role: string): string {
  const map: Record<string, string> = {
    admin: '管理员',
    hr_specialist: 'HR专员',
    employee: '普通员工',
  }
  return map[role] || role
}

// ── 数据加载 ──
async function loadUsers() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchText.value) params.keyword = searchText.value
    const res = await getUsers(params)
    const data = res.data?.data || res.data || {}
    users.value = data.items || []
    total.value = data.pagination?.total || 0
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadUsers()
}

// ── 导入弹窗 ──
function openImportDialog() {
  resetImport()
  importVisible.value = true
}

function resetImport() {
  importFile.value = null
  importResult.value = null
}

function handleImportFileChange(file: UploadFile) {
  importFile.value = file.raw || null
}

function handleImportFileRemove() {
  importFile.value = null
}

async function handleImport() {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importSubmitting.value = true
  importResult.value = null
  try {
    const res = await importEmployees(importFile.value)
    const d = res.data?.data || res.data || {}
    importResult.value = {
      success: d.success || d.success_count || 0,
      fail: d.fail || d.fail_count || 0,
      errors: d.errors || d.failures || [],
    }
    ElMessage.success(`导入完成：成功 ${importResult.value.success} 人，失败 ${importResult.value.fail} 人`)
    loadUsers()
  } catch {
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    importSubmitting.value = false
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.users-view {
  max-width: 1200px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.search-input {
  width: 240px;
}

.table-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-top: 1px solid var(--border-light);
}

/* 导入区域 */
.import-section {
  margin-bottom: 8px;
}

.import-result {
  margin-top: 20px;
  padding: 16px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
}

.import-errors {
  margin-top: 12px;
}

.import-errors h5 {
  font-size: 13px;
  font-weight: 600;
  color: #b91c1c;
  margin-bottom: 8px;
}
</style>
