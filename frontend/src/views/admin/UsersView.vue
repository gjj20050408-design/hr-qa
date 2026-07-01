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
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'active' ? 'success' : 'danger'"
              size="small"
            >
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
            <el-tag v-if="row.locked" type="warning" size="small" style="margin-left: 4px">
              已锁定
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button
              v-if="row.locked"
              link
              type="warning"
              size="small"
              @click="handleUnlock(row)"
            >
              解锁
            </el-button>
            <el-button link type="info" size="small" @click="handleResetPassword(row)">
              重置密码
            </el-button>
            <el-button
              v-if="row.status === 'active'"
              link
              type="danger"
              size="small"
              @click="handleDisable(row)"
            >
              禁用
            </el-button>
            <el-button
              v-else
              link
              type="success"
              size="small"
              @click="handleEnable(row)"
            >
              启用
            </el-button>
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

    <!-- 编辑用户弹窗 -->
    <el-dialog
      v-model="editVisible"
      title="编辑用户"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="工号">
          <el-input :model-value="editForm.employee_id" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" maxlength="50" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" :placeholder="editForm.emailMasked || '未设置，留空则不修改'" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" :placeholder="editForm.phoneMasked || '未设置，留空则不修改'" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="editForm.department_id" placeholder="选择部门" style="width: 100%">
            <el-option
              v-for="d in departments"
              :key="d.department_id"
              :label="d.name"
              :value="d.department_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职级">
          <el-input v-model="editForm.job_level" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" :disabled="editForm.isSelf" style="width: 100%">
            <el-option label="普通员工" value="employee" />
            <el-option label="HR专员" value="hr_specialist" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" :disabled="editForm.isSelf" style="width: 100%">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="handleUpdate">保存</el-button>
      </template>
    </el-dialog>

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
import { getUsers, importEmployees, updateUser, deleteUser, getDepartments, unlockUser, resetUserPassword } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

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

// ── 编辑弹窗 ──
const editVisible = ref(false)
const editSubmitting = ref(false)
const departments = ref<{ department_id: string; name: string }[]>([])
const editForm = ref<any>({
  user_id: '',
  employee_id: '',
  name: '',
  email: '',
  phone: '',
  department_id: '',
  job_level: '',
  role: 'employee',
  status: 'active',
  isSelf: false,
})

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

// ── 编辑用户 ──
async function loadDepartments() {
  try {
    const res = await getDepartments()
    const data = res.data?.data || res.data || {}
    departments.value = data.items || []
  } catch {
    /* error handled by interceptor */
  }
}

function openEditDialog(row: any) {
  editForm.value = {
    user_id: row.user_id,
    employee_id: row.employee_id,
    name: row.name || '',
    email: '',
    phone: '',
    emailMasked: row.email || '',
    phoneMasked: row.phone || '',
    department_id: row.department_id || '',
    job_level: row.job_level || '',
    role: row.role || 'employee',
    status: row.status || 'active',
    isSelf: row.user_id === authStore.user?.user_id,
  }
  editVisible.value = true
}

async function handleUpdate() {
  const f = editForm.value
  // 仅提交有变更的字段；邮箱/手机号留空表示不修改（列表返回的是脱敏值）
  const payload: any = {}
  if (f.name) payload.name = f.name
  if (f.email) payload.email = f.email
  if (f.phone) payload.phone = f.phone
  if (f.department_id) payload.department_id = f.department_id
  if (f.job_level !== undefined) payload.job_level = f.job_level
  if (!f.isSelf) {
    payload.role = f.role
    payload.status = f.status
  }

  editSubmitting.value = true
  try {
    await updateUser(f.user_id, payload)
    ElMessage.success('用户信息已更新')
    editVisible.value = false
    loadUsers()
  } catch {
    /* error handled by interceptor */
  } finally {
    editSubmitting.value = false
  }
}

async function handleDisable(row: any) {
  if (row.user_id === authStore.user?.user_id) {
    ElMessage.warning('不能禁用自己的账号')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要禁用用户「${row.name}（${row.employee_id}）」吗？禁用后该用户将无法登录。`,
      '禁用用户',
      { type: 'warning', confirmButtonText: '确定禁用', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await deleteUser(row.user_id)
    ElMessage.success('用户已禁用')
    loadUsers()
  } catch {
    /* error handled by interceptor */
  }
}

async function handleEnable(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定要重新启用用户「${row.name}（${row.employee_id}）」吗？启用后该用户可正常登录。`,
      '启用用户',
      { type: 'info', confirmButtonText: '确定启用', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await updateUser(row.user_id, { status: 'active' })
    ElMessage.success('用户已启用')
    loadUsers()
  } catch {
    /* error handled by interceptor */
  }
}

async function handleUnlock(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定要解锁用户「${row.name}（${row.employee_id}）」吗？解锁后该用户可重新尝试登录。`,
      '解锁用户',
      { type: 'warning', confirmButtonText: '确定解锁', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await unlockUser(row.user_id)
    ElMessage.success('用户已解锁')
    loadUsers()
  } catch {
    /* error handled by interceptor */
  }
}

async function handleResetPassword(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户「${row.name}（${row.employee_id}）」的密码吗？密码将重置为默认密码并解除锁定。`,
      '重置密码',
      { type: 'warning', confirmButtonText: '确定重置', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    const res = await resetUserPassword(row.user_id)
    const pwd = res.data?.data?.default_password || res.data?.default_password
    ElMessageBox.alert(
      `密码已重置为：${pwd}\n请将该密码告知用户，并提醒其登录后尽快修改。`,
      '重置成功',
      { confirmButtonText: '我知道了' },
    )
    loadUsers()
  } catch {
    /* error handled by interceptor */
  }
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

onMounted(() => {
  loadUsers()
  loadDepartments()
})
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
