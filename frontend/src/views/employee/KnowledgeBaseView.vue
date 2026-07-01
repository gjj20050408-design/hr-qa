<template>
  <div class="knowledge-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📚 知识库管理</h2>
      <p class="page-desc">管理制度文档的添加、更新和发布，所有已发布的文档将自动进行向量化处理供 AI 检索</p>
    </div>

    <!-- 上传区域 - 参考 bigProject 拖拽设计 -->
    <div
      class="upload-zone"
      :class="{ 'drag-over': isDragOver, 'uploading': isUploading }"
      @dragover.prevent="isDragOver = true"
      @dragleave="isDragOver = false"
      @drop.prevent="handleDrop"
      @click="fileInputRef?.click()"
    >
      <div v-if="!isUploading" class="upload-content">
        <div class="upload-icon">
          <el-icon :size="40"><UploadFilled /></el-icon>
        </div>
        <p class="upload-title">拖拽文件到此处上传</p>
        <p class="upload-hint">支持 PDF、DOCX、DOC、Markdown、HTML、TXT 格式（最大 50MB）</p>
        <el-button type="primary" size="default" class="upload-btn" @click.stop="fileInputRef?.click()">
          <el-icon><FolderAdd /></el-icon>选择文件
        </el-button>
        <input
          ref="fileInputRef"
          type="file"
          class="hidden-input"
          accept=".pdf,.doc,.docx,.md,.html,.txt"
          multiple
          @change="handleFileSelect"
        />
      </div>

      <!-- 上传进度 -->
      <div v-else class="upload-progress">
        <div class="progress-icon">
          <el-icon :size="36" class="is-loading"><Loading /></el-icon>
        </div>
        <p class="progress-title">正在上传...</p>
        <p class="progress-file">{{ uploadingFileName }}</p>
        <div class="progress-bar-wrapper">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ uploadProgress }}%</span>
        </div>
      </div>
    </div>

    <!-- 待上传文件列表 -->
    <div v-if="pendingFiles.length > 0 && !isUploading" class="pending-files">
      <div class="section-title">
        <span>待上传文件 ({{ pendingFiles.length }})</span>
        <el-button link type="danger" size="small" @click="pendingFiles = []">清空全部</el-button>
      </div>
      <div v-for="(f, idx) in pendingFiles" :key="idx" class="pending-file-item">
        <el-icon class="file-icon"><Document /></el-icon>
        <span class="file-name">{{ f.name }}</span>
        <span class="file-size">{{ formatSize(f.size) }}</span>
        <div class="file-form">
          <el-input v-model="f.title" placeholder="文档标题（必填）" size="small" class="file-title-input" />
          <el-select v-model="f.category_id" placeholder="分类" size="small" style="width:140px">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
          <el-input v-model="f.version_note" placeholder="版本说明" size="small" style="width:150px" />
        </div>
        <div class="file-actions">
          <el-button type="primary" size="small" :loading="f._uploading" @click="uploadSingleFile(idx)">
            <el-icon><Upload /></el-icon>上传
          </el-button>
          <el-button size="small" @click="pendingFiles.splice(idx, 1)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="batch-actions">
        <el-button type="primary" :loading="batchUploading" @click="uploadAllFiles">
          <el-icon><Upload /></el-icon>一键上传全部
        </el-button>
      </div>
    </div>

    <!-- 文档列表工具栏 -->
    <div class="list-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档标题..."
          :prefix-icon="Search"
          size="default"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        />
        <el-select v-model="statusFilter" size="default" class="filter-select" @change="handleSearch">
          <el-option label="全部状态" value="all" />
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-select v-model="categoryFilter" size="default" class="filter-select" @change="handleSearch">
          <el-option label="全部分类" value="all" />
          <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <span class="doc-count">共 {{ total }} 份文档</span>
      </div>
    </div>

    <!-- 文档卡片列表 -->
    <div class="doc-list" v-loading="loading">
      <!-- 空状态 -->
      <div v-if="docs.length === 0 && !loading" class="empty-state">
        <el-icon :size="48"><Folder /></el-icon>
        <p>暂无文档，请上传第一份制度文档</p>
      </div>

      <!-- 文档卡片 -->
      <div v-for="doc in docs" :key="doc.document_id" class="doc-card" :class="{ archived: doc.status === 'archived' }">
        <div class="card-main">
          <div class="card-icon">
            <el-icon :size="22">
              <Document v-if="doc.format === 'word' || doc.format === 'pdf'" />
              <Reading v-else-if="doc.format === 'markdown' || doc.format === 'html'" />
              <Tickets v-else />
            </el-icon>
          </div>
          <div class="card-info">
            <div class="card-header">
              <span class="card-title">{{ doc.title }}</span>
              <el-tag
                :type="statusTagType(doc.status)"
                size="small"
                effect="dark"
              >
                {{ statusLabel(doc.status) }}
              </el-tag>
              <el-tag
                v-if="doc.embedding_status === 'completed' && doc.status === 'published'"
                type="success"
                size="small"
                effect="plain"
              >
                🤖 已向量化
              </el-tag>
              <el-tag
                v-else-if="doc.embedding_status === 'processing'"
                type="warning"
                size="small"
                effect="plain"
              >
                🔄 向量化中
              </el-tag>
            </div>
            <div class="card-meta">
              <span><el-icon><FolderOpened /></el-icon>{{ doc.category_name || '未分类' }}</span>
              <span><el-icon><Histogram /></el-icon>V{{ doc.version }}</span>
              <span><el-icon><Document /></el-icon>{{ doc.word_count || 0 }} 字 · {{ doc.chunk_count || 0 }} 分块</span>
              <span><el-icon><Clock /></el-icon>{{ doc.updated_at?.slice(0, 10) || '-' }}</span>
              <el-tag
                v-if="doc.access_level !== 'inherit'"
                type="warning"
                size="small"
                effect="plain"
              >
                {{ accessLevelLabel(doc.access_level) }}
              </el-tag>
            </div>
          </div>
        </div>
        <div class="card-actions">
          <!-- 发布按钮（仅草稿状态） -->
          <el-button
            v-if="doc.status === 'draft'"
            type="success"
            size="small"
            plain
            :loading="doc._publishing"
            @click="handlePublish(doc)"
          >
            <el-icon><Finished /></el-icon>发布
          </el-button>
          <!-- 替换文件按钮 -->
          <el-button
            size="small"
            plain
            @click="openReplaceDialog(doc)"
          >
            <el-icon><Refresh /></el-icon>替换文件
          </el-button>
          <!-- 编辑按钮 -->
          <el-button
            size="small"
            plain
            @click="openEditDialog(doc)"
          >
            <el-icon><Edit /></el-icon>编辑
          </el-button>
          <!-- 归档/恢复按钮 -->
          <el-button
            v-if="doc.status !== 'draft'"
            size="small"
            :type="doc.status === 'archived' ? 'success' : 'danger'"
            plain
            @click="handleArchive(doc)"
          >
            <el-icon><component :is="doc.status === 'archived' ? 'CircleCheck' : 'Box'" /></el-icon>
            {{ doc.status === 'archived' ? '恢复' : '归档' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadDocs"
        @size-change="loadDocs"
        background
      />
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editVisible"
      title="编辑文档"
      width="520px"
      :close-on-click-modal="false"
      @closed="resetEditForm"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="90px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入文档标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="editForm.category_id" placeholder="请选择分类" style="width:100%">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本说明">
          <el-input v-model="editForm.version_note" placeholder="版本说明" maxlength="200" />
        </el-form-item>
        <el-form-item label="访问权限">
          <el-select v-model="editForm.access_level" style="width:100%">
            <el-option label="继承分类" value="inherit" />
            <el-option label="全员可见" value="all_roles" />
            <el-option label="HR+管理员" value="hr_admin_only" />
            <el-option label="仅管理员" value="admin_only" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 替换文件弹窗 -->
    <el-dialog
      v-model="replaceVisible"
      title="替换文档文件"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="replace-info">
        <p>当前文档：<strong>{{ replaceTarget?.title }}</strong></p>
        <p>当前版本：V{{ replaceTarget?.version }}</p>
      </div>
      <el-upload
        ref="replaceUploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleReplaceFileChange"
        :on-remove="handleReplaceFileRemove"
        accept=".pdf,.doc,.docx,.md,.html,.txt"
        drag
        style="margin-top: 16px"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件或<em>点击上传</em>以替换当前文档</div>
        <template #tip>
          <div class="el-upload__tip">新文件将替换原文档内容，版本号自动递增</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="replaceVisible = false">取消</el-button>
        <el-button type="primary" :loading="replaceSubmitting" @click="handleReplaceSave">
          确认替换
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  Search, Upload, UploadFilled, FolderAdd, Document, Reading, Tickets,
  Folder, FolderOpened, Histogram, Clock, Delete, Loading, Edit,
  Refresh, Finished, CircleCheck, Box,
} from '@element-plus/icons-vue'
import {
  getDocuments, getCategories, createDocument, updateDocument,
  archiveDocument, restoreDocument, publishDocument, updateDocumentFile,
} from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'

// ── 文件上传 ──
const fileInputRef = ref<HTMLInputElement>()
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadingFileName = ref('')
const uploadProgress = ref(0)
const pendingFiles = ref<Array<{
  name: string
  size: number
  file: File
  ext: string
  format: string
  title: string
  category_id: string
  version_note: string
  _uploading: boolean
}>>([])
const batchUploading = ref(false)

// ── 搜索筛选 ──
const searchKeyword = ref('')
const statusFilter = ref('all')
const categoryFilter = ref('all')

// ── 文档列表 ──
const docs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

// ── 分类数据 ──
const categoryOptions = ref<Array<{ label: string; value: string }>>([])

// ── 编辑弹窗 ──
const editVisible = ref(false)
const editSubmitting = ref(false)
const editTarget = ref<any>(null)
const editFormRef = ref<FormInstance>()
const editForm = reactive({ title: '', category_id: '', version_note: '', access_level: 'inherit' })
const editRules: FormRules = {
  title: [{ required: true, message: '请输入文档标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

// ── 替换文件弹窗 ──
const replaceVisible = ref(false)
const replaceTarget = ref<any>(null)
const replaceSubmitting = ref(false)
const replaceFile = ref<File | null>(null)

// ── 辅助方法 ──
function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusTagType(s: string) {
  if (s === 'published') return 'success' as const
  if (s === 'draft') return 'info' as const
  return 'warning' as const
}

function statusLabel(s: string) {
  if (s === 'published') return '已发布'
  if (s === 'draft') return '草稿'
  if (s === 'archived') return '已归档'
  return s
}

function accessLevelLabel(level: string) {
  const map: Record<string, string> = {
    inherit: '继承分类',
    all_roles: '全员可见',
    hr_admin_only: 'HR+管理',
    admin_only: '仅管理员',
  }
  return map[level] || level
}

function getExt(filename: string) {
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop()!.toLowerCase() : ''
}

function getFormat(ext: string) {
  const map: Record<string, string> = {
    pdf: 'pdf', doc: 'word', docx: 'word',
    md: 'markdown', html: 'html', txt: 'txt',
  }
  return map[ext] || 'markdown'
}

// ── 文件处理 ──
function handleDrop(e: DragEvent) {
  isDragOver.value = false
  if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files))
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
    input.value = ''
  }
}

function addFiles(files: File[]) {
  const validExts = ['pdf', 'doc', 'docx', 'md', 'html', 'txt']
  for (const file of files) {
    const ext = getExt(file.name)
    if (!validExts.includes(ext)) {
      ElMessage.warning(`不支持的文件格式: ${file.name}`)
      continue
    }
    if (file.size > 50 * 1024 * 1024) {
      ElMessage.warning(`文件过大，最大支持 50MB: ${file.name}`)
      continue
    }
    const nameWithoutExt = file.name.replace(/\.[^.]+$/, '')
    pendingFiles.value.push({
      name: file.name,
      size: file.size,
      file,
      ext,
      format: getFormat(ext),
      title: nameWithoutExt,
      category_id: categoryOptions.value[0]?.value || '',
      version_note: '',
      _uploading: false,
    })
  }
}

async function uploadSingleFile(idx: number) {
  const f = pendingFiles.value[idx]
  if (!f.title.trim()) {
    ElMessage.warning('请填写文档标题')
    return
  }
  if (!f.category_id) {
    ElMessage.warning('请选择分类')
    return
  }

  f._uploading = true
  isUploading.value = true
  uploadingFileName.value = f.name
  uploadProgress.value = 0

  try {
    const fd = new FormData()
    fd.append('file', f.file)
    fd.append('title', f.title)
    fd.append('category_id', f.category_id)
    fd.append('format', f.format)
    fd.append('version_note', f.version_note)
    fd.append('access_level', 'inherit')

    // 使用原生 fetch 以支持上传进度（axios 的 onUploadProgress 也可用，这里用简单方式）
    await createDocument(fd)
    ElMessage.success(`「${f.title}」上传成功`)
    pendingFiles.value.splice(idx, 1)
    loadDocs()
  } catch {
    /* error handled by interceptor */
  } finally {
    f._uploading = false
    isUploading.value = false
    uploadProgress.value = 0
    uploadingFileName.value = ''
  }
}

async function uploadAllFiles() {
  if (pendingFiles.value.length === 0) return

  const hasTitle = pendingFiles.value.every(f => f.title.trim())
  if (!hasTitle) {
    ElMessage.warning('请为所有文件填写标题')
    return
  }
  const hasCategory = pendingFiles.value.every(f => f.category_id)
  if (!hasCategory) {
    ElMessage.warning('请为所有文件选择分类')
    return
  }

  batchUploading.value = true
  isUploading.value = true
  let successCount = 0

  for (let i = 0; i < pendingFiles.value.length; i++) {
    const f = pendingFiles.value[i]
    uploadingFileName.value = f.name
    uploadProgress.value = Math.round((i / pendingFiles.value.length) * 100)

    try {
      const fd = new FormData()
      fd.append('file', f.file)
      fd.append('title', f.title)
      fd.append('category_id', f.category_id)
      fd.append('format', f.format)
      fd.append('version_note', f.version_note)
      fd.append('access_level', 'inherit')
      await createDocument(fd)
      successCount++
    } catch {
      ElMessage.error(`「${f.title}」上传失败`)
    }
  }

  uploadProgress.value = 100
  batchUploading.value = false
  isUploading.value = false

  if (successCount > 0) {
    ElMessage.success(`成功上传 ${successCount} 份文档`)
    pendingFiles.value = []
    loadDocs()
  }
}

// ── 文档操作 ──
async function loadDocs() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (statusFilter.value !== 'all') params.status = statusFilter.value
    if (categoryFilter.value !== 'all') params.category_id = categoryFilter.value
    if (searchKeyword.value) params.keyword = searchKeyword.value

    const res = await getDocuments(params)
    const data = res.data?.data || res.data || {}
    docs.value = (data.items || []).map((d: any) => ({
      ...d,
      _publishing: false,
    }))
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
    categoryOptions.value = []
    const flatten = (list: any[]) => {
      for (const c of list) {
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

async function handlePublish(doc: any) {
  try {
    await ElMessageBox.confirm(
      `确认发布「${doc.title}」？发布后将自动进行分块和向量化处理，供 AI 智能问答使用。`,
      '确认发布',
      { confirmButtonText: '确认发布', type: 'success' }
    )
    doc._publishing = true
    await publishDocument(doc.document_id)
    ElMessage.success(`「${doc.title}」发布成功，向量化已完成`)
    loadDocs()
  } catch {
    /* cancelled or error */
  } finally {
    doc._publishing = false
  }
}

async function handleArchive(doc: any) {
  const isArchived = doc.status === 'archived'
  const action = isArchived ? '恢复' : '归档'
  try {
    await ElMessageBox.confirm(
      isArchived
        ? `确认恢复「${doc.title}」？恢复后将回到草稿状态，需重新发布以更新检索数据。`
        : `确认归档「${doc.title}」？归档后不再对外可见。`,
      `确认${action}`,
    )
    if (isArchived) {
      await restoreDocument(doc.document_id)
    } else {
      await archiveDocument(doc.document_id)
    }
    ElMessage.success(`已${action}`)
    loadDocs()
  } catch {
    /* cancelled */
  }
}

// ── 编辑弹窗 ──
function openEditDialog(doc: any) {
  editTarget.value = doc
  editForm.title = doc.title
  editForm.category_id = doc.category_id
  editForm.version_note = doc.version_note || ''
  editForm.access_level = doc.access_level || 'inherit'
  editVisible.value = true
}

function resetEditForm() {
  editTarget.value = null
  editForm.title = ''
  editForm.category_id = ''
  editForm.version_note = ''
  editForm.access_level = 'inherit'
  editFormRef.value?.resetFields()
}

async function handleEditSave() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid || !editTarget.value) return

  editSubmitting.value = true
  try {
    await updateDocument(editTarget.value.document_id, {
      title: editForm.title,
      category_id: editForm.category_id,
      version_note: editForm.version_note,
      access_level: editForm.access_level,
    })
    ElMessage.success('文档已更新')
    editVisible.value = false
    loadDocs()
  } catch {
    /* error handled by interceptor */
  } finally {
    editSubmitting.value = false
  }
}

// ── 替换文件弹窗 ──
function openReplaceDialog(doc: any) {
  replaceTarget.value = doc
  replaceFile.value = null
  replaceVisible.value = true
}

function handleReplaceFileChange(file: UploadFile) {
  replaceFile.value = file.raw || null
}

function handleReplaceFileRemove() {
  replaceFile.value = null
}

async function handleReplaceSave() {
  if (!replaceTarget.value || !replaceFile.value) {
    ElMessage.warning('请选择要替换的文件')
    return
  }

  replaceSubmitting.value = true
  try {
    const fd = new FormData()
    fd.append('file', replaceFile.value)
    fd.append('title', replaceTarget.value.title)
    fd.append('version_note', `文件替换: ${replaceFile.value.name}`)
    await updateDocumentFile(replaceTarget.value.document_id, fd)
    ElMessage.success('文件已替换，版本号已更新，请重新发布以更新向量化数据')
    replaceVisible.value = false
    loadDocs()
  } catch {
    /* error handled by interceptor */
  } finally {
    replaceSubmitting.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadDocs()
})
</script>

<style scoped>
.knowledge-view {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}

.page-header {
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}
.page-desc {
  font-size: 13px;
  color: #94a3b8;
}

/* ── 上传区域 ── */
.upload-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s;
  background: #f8fafc;
  margin-bottom: 16px;
}
.upload-zone:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}
.upload-zone.drag-over {
  border-color: #3b82f6;
  background: #dbeafe;
  transform: scale(1.01);
}
.upload-zone.uploading {
  border-color: #8b5cf6;
  background: #f5f3ff;
  cursor: default;
}
.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.upload-icon {
  color: #94a3b8;
  margin-bottom: 4px;
}
.drag-over .upload-icon {
  color: #3b82f6;
}
.upload-title {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  margin: 0;
}
.upload-hint {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}
.upload-btn {
  margin-top: 8px;
}
.hidden-input {
  display: none;
}

/* ── 上传进度 ── */
.upload-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.progress-icon {
  color: #8b5cf6;
}
.progress-title {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  margin: 0;
}
.progress-file {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 400px;
}
.progress-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.3s ease;
}
.progress-text {
  font-size: 13px;
  font-weight: 600;
  color: #8b5cf6;
  min-width: 40px;
}

/* ── 待上传文件列表 ── */
.pending-files {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}
.pending-file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.file-icon {
  color: #3b82f6;
  flex-shrink: 0;
}
.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-size {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}
.file-form {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 300px;
}
.file-title-input {
  width: 180px;
}
.file-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.batch-actions {
  margin-top: 12px;
  text-align: center;
}

/* ── 工具栏 ── */
.list-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.toolbar-left {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.search-input {
  width: 240px;
}
.filter-select {
  width: 130px;
}
.toolbar-right {
  display: flex;
  align-items: center;
}
.doc-count {
  font-size: 13px;
  color: #94a3b8;
}

/* ── 文档卡片列表 ── */
.doc-list {
  min-height: 200px;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #cbd5e1;
}
.empty-state p {
  margin-top: 12px;
  font-size: 14px;
  color: #94a3b8;
}

.doc-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  transition: all 0.15s;
}
.doc-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.doc-card.archived {
  opacity: 0.6;
  background: #f8fafc;
}

.card-main {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 0;
}
.card-icon {
  width: 40px;
  height: 40px;
  background: #eff6ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  flex-shrink: 0;
}
.card-info {
  flex: 1;
  min-width: 0;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.card-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

/* ── 分页 ── */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* ── 替换文件信息 ── */
.replace-info {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px 16px;
}
.replace-info p {
  margin-bottom: 4px;
  font-size: 14px;
  color: #475569;
}
.replace-info p:last-child {
  margin-bottom: 0;
}
</style>
