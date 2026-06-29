<template>
  <div class="announcements-view">
    <div class="toolbar">
      <h3>通知公告管理</h3>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>发布公告
      </el-button>
    </div>

    <!-- 公告卡片列表 -->
    <div class="ann-list" v-loading="loading">
      <div v-for="item in announcements" :key="item.announcement_id" class="ann-card">
        <div class="ann-title-row">
          <div class="ann-title-left">
            <h4>{{ item.title }}</h4>
            <div class="ann-tags">
              <el-tag
                :type="priorityTagType(item.priority)"
                size="small"
              >
                {{ priorityLabel(item.priority) }}
              </el-tag>
              <el-tag size="small">{{ targetTypeLabel(item.target_type) }}</el-tag>
            </div>
          </div>
          <div class="ann-actions">
            <el-button link type="primary" size="small" @click="toggleReadStatus(item)">
              <el-icon><View /></el-icon>查看阅读状态
            </el-button>
          </div>
        </div>

        <p class="ann-content-preview">{{ item.content?.slice(0, 100) }}{{ item.content?.length > 100 ? '...' : '' }}</p>

        <div class="ann-meta">
          <span>发布人：{{ item.publisher_name || '系统管理员' }}</span>
          <span>{{ item.published_at }}</span>
        </div>

        <!-- 阅读状态展开区 -->
        <div v-if="item._showReads" class="ann-reads-section" v-loading="item._loadingReads">
          <h5>阅读状态</h5>
          <el-table :data="item._reads || []" size="small" stripe>
            <el-table-column prop="employee_id" label="工号" width="100" />
            <el-table-column prop="name" label="用户名" min-width="120" />
            <el-table-column prop="department_name" label="部门" width="140" />
            <el-table-column label="是否已读" width="90">
              <template #default="{ row }">
                <el-tag :type="row.is_read ? 'success' : 'info'" size="small">
                  {{ row.is_read ? '已读' : '未读' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="阅读时间" width="160">
              <template #default="{ row }">
                {{ row.read_at || '-' }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!item._reads?.length" description="暂无阅读数据" :image-size="60" />
        </div>
      </div>

      <el-empty v-if="!announcements.length && !loading" description="暂无公告" />
    </div>

    <!-- 发布公告弹窗 -->
    <el-dialog
      v-model="createVisible"
      title="发布公告"
      width="600px"
      :close-on-click-modal="false"
      @closed="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="90px"
      >
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="createForm.title"
            placeholder="请输入公告标题（最多100字）"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="5"
            placeholder="请输入公告内容"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="createForm.priority">
            <el-radio value="normal">
              <el-tag type="info" size="small">普通</el-tag>
            </el-radio>
            <el-radio value="important">
              <el-tag type="warning" size="small">重要</el-tag>
            </el-radio>
            <el-radio value="urgent">
              <el-tag type="danger" size="small">紧急</el-tag>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="目标类型" prop="target_type">
          <el-radio-group v-model="createForm.target_type" @change="onTargetTypeChange">
            <el-radio value="all">全员</el-radio>
            <el-radio value="department">按部门</el-radio>
            <el-radio value="role">按角色</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            action="/api/v1/upload"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
          >
            <el-button type="primary" plain>上传附件</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item
          v-if="createForm.target_type !== 'all'"
          label="目标选择"
          prop="target_ids"
        >
          <el-select
            v-model="createForm.target_ids"
            multiple
            :placeholder="createForm.target_type === 'department' ? '选择部门' : '选择角色'"
            style="width: 100%"
          >
            <template v-if="createForm.target_type === 'department'">
              <el-option
                v-for="dept in departmentOptions"
                :key="dept.value"
                :label="dept.label"
                :value="dept.value"
              />
            </template>
            <template v-else>
              <el-option label="普通员工" value="employee" />
              <el-option label="HR专员" value="hr_specialist" />
              <el-option label="管理员" value="admin" />
            </template>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="handleCreate">
          确认发布
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, View } from '@element-plus/icons-vue'
import { getAnnouncements, createAnnouncement, getAnnouncementReads } from '@/api/admin'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// ── 公告列表 ──
const announcements = ref<any[]>([])
const loading = ref(false)

// ── 创建弹窗 ──
const createVisible = ref(false)
const createSubmitting = ref(false)
const createFormRef = ref<FormInstance>()
const attachmentUrl = ref('')

const createForm = reactive({
  title: '',
  content: '',
  priority: 'normal' as 'normal' | 'important' | 'urgent',
  target_type: 'all' as 'all' | 'department' | 'role',
  target_ids: [] as string[],
})

const createFormRules: FormRules = {
  title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' },
    { max: 100, message: '标题不能超过100字', trigger: 'blur' },
  ],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  target_type: [{ required: true, message: '请选择目标类型', trigger: 'change' }],
}

// ── 部门选项（可扩展为从API获取） ──
const departmentOptions = ref<{ label: string; value: string }[]>([])

// ── 辅助方法 ──
function priorityTagType(priority: string): 'info' | 'warning' | 'danger' {
  if (priority === 'urgent') return 'danger'
  if (priority === 'important') return 'warning'
  return 'info'
}

function priorityLabel(priority: string): string {
  const map: Record<string, string> = {
    normal: '普通',
    important: '重要',
    urgent: '紧急',
  }
  return map[priority] || priority
}

function targetTypeLabel(type: string): string {
  const map: Record<string, string> = {
    all: '全员',
    department: '按部门',
    role: '按角色',
  }
  return map[type] || type
}

function onTargetTypeChange() {
  createForm.target_ids = []
}

// ── 数据加载 ──
async function loadAnnouncements() {
  loading.value = true
  try {
    const res = await getAnnouncements()
    const items = res.data?.items || res.data?.data?.items || []
    announcements.value = items.map((item: any) => ({
      ...item,
      _showReads: false,
      _reads: [],
      _loadingReads: false,
    }))
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

// ── 创建弹窗 ──
function openCreateDialog() {
  resetCreateForm()
  createVisible.value = true
}

function resetCreateForm() {
  createForm.title = ''
  createForm.content = ''
  createForm.priority = 'normal'
  createForm.target_type = 'all'
  createForm.target_ids = []
  attachmentUrl.value = ''
  createFormRef.value?.resetFields()
}

async function handleCreate() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return

  createSubmitting.value = true
  try {
    const payload: any = {
      title: createForm.title,
      content: createForm.content,
      priority: createForm.priority,
      target_type: createForm.target_type,
    }
    if (createForm.target_type !== 'all') {
      payload.target_ids = createForm.target_ids
    }
    if (attachmentUrl.value) {
      payload.attachment = attachmentUrl.value
    }
    await createAnnouncement(payload)
    ElMessage.success('公告已发布')
    createVisible.value = false
    loadAnnouncements()
  } catch {
    /* error handled by interceptor */
  } finally {
    createSubmitting.value = false
  }
}

// ── 附件上传 ──
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
}))

function handleUploadSuccess(response: any) {
  attachmentUrl.value = response.data?.url || response.url || ''
  ElMessage.success('附件上传成功')
}

function handleUploadError() {
  ElMessage.error('附件上传失败')
}

// ── 阅读状态 ──
async function toggleReadStatus(item: any) {
  if (item._showReads) {
    item._showReads = false
    return
  }

  item._showReads = true
  if (item._reads && item._reads.length > 0) return

  item._loadingReads = true
  try {
    const res = await getAnnouncementReads(item.announcement_id)
    item._reads = res.data?.items || res.data?.data?.items || res.data || []
  } catch {
    item._reads = []
  } finally {
    item._loadingReads = false
  }
}

onMounted(loadAnnouncements)
</script>

<style scoped>
.announcements-view {
  max-width: 1000px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.ann-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ann-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}

.ann-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.ann-title-left h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 8px;
}

.ann-tags {
  display: flex;
  gap: 8px;
}

.ann-actions {
  flex-shrink: 0;
}

.ann-content-preview {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 10px;
}

.ann-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

/* 阅读状态区域 */
.ann-reads-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.ann-reads-section h5 {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 10px;
}
</style>
