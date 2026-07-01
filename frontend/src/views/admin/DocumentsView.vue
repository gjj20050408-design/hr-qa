<template>
  <div class="documents-view">
    <!-- 搜索工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchText"
          placeholder="搜索文档标题..."
          :prefix-icon="Search"
          size="default"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        />
        <el-select
          v-model="categoryFilter"
          placeholder="全部分类"
          size="default"
          class="tool-select"
          @change="handleSearch"
        >
          <el-option
            v-for="cat in categories"
            :key="cat.value"
            :label="cat.label"
            :value="cat.value"
          />
        </el-select>
        <el-select
          v-model="statusFilter"
          placeholder="全部状态"
          size="default"
          class="tool-select"
          @change="handleSearch"
        >
          <el-option label="全部状态" value="all" />
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已归档" value="archived" />
        </el-select>
      </div>
      <el-button type="primary" @click="openUploadDialog">
        <el-icon><Upload /></el-icon>上传文档
      </el-button>
    </div>

    <!-- 文档表格 -->
    <div class="table-card" v-loading="loading">
      <el-table :data="docs" stripe style="width: 100%">
        <el-table-column prop="title" label="文档标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="130" />
        <el-table-column label="版本" width="80">
          <template #default="{ row }">V{{ row.version }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag
              :type="statusTagType(row.status)"
              size="small"
            >
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限" width="150">
          <template #default="{ row }">
            <el-tag
              :type="accessLevelTagType(row.access_level)"
              size="small"
            >
              {{ accessLevelLabel(row.access_level) }}
            </el-tag>
            <el-tooltip content="分类默认权限已被覆盖" placement="top">
              <el-tag v-if="row.access_level !== 'inherit'" type="warning" size="small" effect="plain" style="margin-left: 4px">
                ⚠ 已覆盖
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="字数" width="70">
          <template #default="{ row }">{{ row.word_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">{{ row.updated_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="warning" size="small" @click="openAccessDialog(row)">权限</el-button>
            <el-button
              link
              :type="row.status === 'archived' ? 'success' : 'danger'"
              size="small"
              @click="handleArchive(row)"
            >
              {{ row.status === 'archived' ? '恢复' : '归档' }}
            </el-button>
            <el-button
              v-if="authStore.isAdmin"
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
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
          @current-change="loadDocs"
          @size-change="loadDocs"
        />
      </div>
    </div>

    <!-- 上传/编辑弹窗 -->
    <el-dialog
      v-model="uploadVisible"
      :title="editingDoc ? '编辑文档' : '上传文档'"
      width="560px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="90px"
      >
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文档标题" maxlength="200" />
        </el-form-item>

        <el-form-item v-if="!editingDoc" label="上传文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".pdf,.doc,.docx,.md,.html"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .pdf / .doc / .docx / .md / .html 格式
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="cat in categoryOptions"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="版本说明" prop="version_note">
          <el-input
            v-model="form.version_note"
            placeholder="版本说明（如：初始版本、V2修订）"
            maxlength="200"
          />
        </el-form-item>

        <el-form-item label="访问权限" prop="access_level">
          <el-select v-model="form.access_level" placeholder="请选择访问权限" style="width: 100%">
            <el-option label="继承分类 (inherit)" value="inherit" />
            <el-option label="全员可见 (all_roles)" value="all_roles" />
            <el-option label="HR+管理员 (hr_admin_only)" value="hr_admin_only" />
            <el-option label="仅管理员 (admin_only)" value="admin_only" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingDoc ? '保存修改' : '确认上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 权限设置弹窗 -->
    <el-dialog
      v-model="accessVisible"
      title="权限设置"
      width="480px"
      :close-on-click-modal="false"
    >
      <div class="access-info">
        <p class="access-current">
          当前文档：<strong>{{ accessTarget?.title }}</strong>
        </p>
        <p class="access-current">
          当前生效级别：
          <el-tag :type="accessLevelTagType(accessTarget?.access_level || '')" size="small">
            {{ accessLevelLabel(accessTarget?.access_level || '') }}
          </el-tag>
        </p>
      </div>
      <el-form label-width="100px" style="margin-top: 16px">
        <el-form-item label="设置新权限">
          <el-select
            v-model="newAccessLevel"
            placeholder="选择新权限级别"
            style="width: 100%"
          >
            <el-option label="继承分类 (inherit)" value="inherit" />
            <el-option label="全员可见 (all_roles)" value="all_roles" />
            <el-option label="HR+管理员 (hr_admin_only)" value="hr_admin_only" />
            <el-option label="仅管理员 (admin_only)" value="admin_only" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="accessVisible = false">取消</el-button>
        <el-button type="primary" :loading="accessSubmitting" @click="handleAccessSave">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Upload, UploadFilled } from '@element-plus/icons-vue'
import {
  getDocuments,
  getCategories,
  createDocument,
  updateDocument,
  archiveDocument,
  restoreDocument,
  deleteDocument,
  updateDocumentAccess,
} from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// ── 搜索与筛选 ──
const searchText = ref('')
const statusFilter = ref('all')
const categoryFilter = ref('all')

// ── 表格数据 ──
const docs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// ── 分类数据 ──
const categories = ref<{ label: string; value: string }[]>([{ label: '全部分类', value: 'all' }])
const categoryOptions = ref<{ label: string; value: string }[]>([])

// ── 上传/编辑弹窗 ──
const uploadVisible = ref(false)
const editingDoc = ref<any>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const selectedFile = ref<File | null>(null)

const form = reactive({
  title: '',
  category_id: '',
  version_note: '',
  access_level: 'inherit',
})

const formRules: FormRules = {
  title: [{ required: true, message: '请输入文档标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

// ── 权限弹窗 ──
const accessVisible = ref(false)
const accessTarget = ref<any>(null)
const newAccessLevel = ref('')
const accessSubmitting = ref(false)

// ── 辅助方法 ──
function statusTagType(status: string): 'success' | 'info' | 'warning' {
  if (status === 'published') return 'success'
  if (status === 'draft') return 'info'
  return 'warning'
}

function statusLabel(status: string): string {
  if (status === 'published') return '已发布'
  if (status === 'draft') return '草稿'
  if (status === 'archived') return '已归档'
  return status
}

function accessLevelTagType(level: string): 'info' | 'success' | 'warning' | 'danger' {
  if (level === 'inherit') return 'info'
  if (level === 'all_roles') return 'success'
  if (level === 'hr_admin_only') return 'warning'
  if (level === 'admin_only') return 'danger'
  return 'info'
}

function accessLevelLabel(level: string): string {
  const map: Record<string, string> = {
    inherit: '继承分类',
    all_roles: '全员可见',
    hr_admin_only: 'HR+管理',
    admin_only: '仅管理员',
  }
  return map[level] || level
}

// ── 数据加载 ──
async function loadDocs() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (statusFilter.value !== 'all') params.status = statusFilter.value
    if (categoryFilter.value !== 'all') params.category_id = categoryFilter.value
    if (searchText.value) params.keyword = searchText.value
    const res = await getDocuments(params)
    const data = res.data?.data || res.data || {}
    docs.value = data.items || []
    total.value = data.pagination?.total || 0
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await getCategories({ type: 'document' })
    const items = res.data?.data?.items || res.data?.items || []
    categories.value = [{ label: '全部分类', value: 'all' }]
    categoryOptions.value = []
    const flatten = (list: any[]) => {
      for (const c of list) {
        categories.value.push({ label: c.name, value: c.category_id })
        categoryOptions.value.push({ label: c.name, value: c.category_id })
        if (c.children) flatten(c.children)
      }
    }
    flatten(items)
  } catch {
    /* error handled by interceptor */
  }
}

function handleSearch() {
  page.value = 1
  loadDocs()
}

// ── 上传弹窗 ──
function openUploadDialog() {
  editingDoc.value = null
  resetForm()
  uploadVisible.value = true
}

function openEditDialog(row: any) {
  editingDoc.value = row
  form.title = row.title
  form.category_id = row.category_id
  form.version_note = row.version_note || ''
  form.access_level = row.access_level || 'inherit'
  uploadVisible.value = true
}

function handleFileChange(file: UploadFile) {
  selectedFile.value = file.raw || null
}

function handleFileRemove() {
  selectedFile.value = null
}

function resetForm() {
  form.title = ''
  form.category_id = ''
  form.version_note = ''
  form.access_level = 'inherit'
  selectedFile.value = null
  formRef.value?.resetFields()
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingDoc.value) {
      await updateDocument(editingDoc.value.document_id, {
        title: form.title,
        category_id: form.category_id,
        version_note: form.version_note,
        access_level: form.access_level,
      })
      ElMessage.success('文档已更新')
    } else {
      if (!selectedFile.value) {
        ElMessage.warning('请选择文件')
        submitting.value = false
        return
      }
      const fd = new FormData()
      fd.append('file', selectedFile.value)
      fd.append('title', form.title)
      fd.append('category_id', form.category_id)
      fd.append('version_note', form.version_note)
      fd.append('access_level', form.access_level)
      await createDocument(fd)
      ElMessage.success('文档上传成功')
    }
    uploadVisible.value = false
    loadDocs()
  } catch {
    /* error handled by interceptor */
  } finally {
    submitting.value = false
  }
}

// ── 归档/恢复 ──
async function handleArchive(row: any) {
  const isArchived = row.status === 'archived'
  const action = isArchived ? '恢复' : '归档'
  try {
    await ElMessageBox.confirm(
      isArchived
        ? `确认恢复「${row.title}」？恢复后将回到草稿状态，需重新发布以更新检索数据。`
        : `确认归档「${row.title}」？归档后不再对外可见。`,
      `确认${action}`,
    )
    if (isArchived) {
      await restoreDocument(row.document_id)
    } else {
      await archiveDocument(row.document_id)
    }
    ElMessage.success(`已${action}`)
    loadDocs()
  } catch {
    /* cancelled or error */
  }
}

// ── 彻底删除（仅管理员）──
async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确认彻底删除「${row.title}」？此操作将一并删除其历史版本、分块与检索索引，且无法恢复！`,
      '危险操作',
      { type: 'warning', confirmButtonText: '彻底删除', confirmButtonClass: 'el-button--danger' },
    )
    await deleteDocument(row.document_id)
    ElMessage.success('已彻底删除')
    loadDocs()
  } catch {
    /* cancelled or error */
  }
}

// ── 权限弹窗 ──
function openAccessDialog(row: any) {
  accessTarget.value = row
  newAccessLevel.value = row.access_level || 'inherit'
  accessVisible.value = true
}

async function handleAccessSave() {
  if (!accessTarget.value) return
  accessSubmitting.value = true
  try {
    await updateDocumentAccess(accessTarget.value.document_id, newAccessLevel.value)
    ElMessage.success('权限已更新')
    accessVisible.value = false
    loadDocs()
  } catch {
    /* error handled by interceptor */
  } finally {
    accessSubmitting.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadDocs()
})
</script>

<style scoped>
.documents-view {
  max-width: 1400px;
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
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  width: 240px;
}

.tool-select {
  width: 140px;
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

.access-info {
  background: var(--surface-muted);
  border-radius: 8px;
  padding: 12px 16px;
}

.access-info p {
  margin-bottom: 8px;
  font-size: 14px;
  color: #334155;
}

.access-info p:last-child {
  margin-bottom: 0;
}
</style>
