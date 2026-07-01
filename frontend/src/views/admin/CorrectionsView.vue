<template>
  <div class="corrections-view">
    <!-- 状态筛选 Tabs -->
    <div class="toolbar">
      <h3>纠错审核</h3>
      <el-radio-group v-model="statusFilter" size="default" @change="handleFilterChange">
        <el-radio-button value="pending">
          <el-badge :value="pendingCount" :max="99" :hidden="pendingCount === 0" class="tab-badge">
            待审核
          </el-badge>
        </el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已驳回</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 纠错卡片列表 -->
    <div class="corr-list" v-loading="loading">
      <div v-for="item in corrections" :key="item.request_id" class="corr-card">
        <div class="corr-header">
          <el-tag
            :type="statusTagType(item.status)"
            size="small"
          >
            {{ statusLabel(item.status) }}
          </el-tag>
          <span class="corr-meta">
            {{ item.submitter_name || '匿名' }} · {{ item.created_at }}
          </span>
        </div>

        <div class="corr-body">
          <p class="corr-doc">
            <strong>文档：</strong>{{ item.document_title || '未知文档' }}
          </p>
          <p class="corr-section" v-if="item.section">
            <strong>章节：</strong>{{ item.section }}
          </p>
          <div class="corr-desc">
            <p>{{ item.description }}</p>
          </div>
        </div>

        <!-- 审核备注（已审核项） -->
        <div v-if="item.review_comment" class="corr-comment">
          <strong>审核备注：</strong>{{ item.review_comment }}
        </div>
        <div v-if="item.reviewer_name" class="corr-reviewer">
          审核人：{{ item.reviewer_name }} · {{ item.reviewed_at }}
        </div>

        <!-- pending 操作按钮 -->
        <div v-if="item.status === 'pending'" class="corr-actions">
          <el-button type="success" size="small" @click="openReviewDialog(item, 'approved')">
            <el-icon><Select /></el-icon>通过
          </el-button>
          <el-button type="danger" size="small" @click="openReviewDialog(item, 'rejected')">
            <el-icon><CloseBold /></el-icon>驳回
          </el-button>
        </div>
      </div>

      <el-empty v-if="!corrections.length && !loading" description="暂无纠错申请" />
    </div>

    <!-- 审核弹窗 -->
    <el-dialog
      v-model="reviewVisible"
      :title="reviewAction === 'approved' ? '通过纠错申请' : '驳回纠错申请'"
      width="480px"
      :close-on-click-modal="false"
    >
      <div class="review-info">
        <p>
          <strong>文档：</strong>{{ reviewTarget?.document_title }}
        </p>
        <p v-if="reviewTarget?.section">
          <strong>章节：</strong>{{ reviewTarget?.section }}
        </p>
        <div class="review-desc">
          <p>{{ reviewTarget?.description }}</p>
        </div>
      </div>

      <el-form label-width="90px" style="margin-top: 16px">
        <el-form-item
          :label="reviewAction === 'approved' ? '备注(可选)' : '驳回原因'"
          :required="reviewAction === 'rejected'"
        >
          <el-input
            v-model="reviewComment"
            type="textarea"
            :rows="3"
            :placeholder="
              reviewAction === 'approved'
                ? '可选，填写审核备注...'
                : '请填写驳回原因（必填）'
            "
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button
          :type="reviewAction === 'approved' ? 'success' : 'danger'"
          :loading="reviewSubmitting"
          @click="handleReviewSubmit"
        >
          {{ reviewAction === 'approved' ? '确认通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Select, CloseBold } from '@element-plus/icons-vue'
import { getCorrections, reviewCorrection } from '@/api/admin'
import { ElMessage } from 'element-plus'

// ── 筛选 ──
const statusFilter = ref<'pending' | 'approved' | 'rejected'>('pending')

// ── 列表 ──
const corrections = ref<any[]>([])
const loading = ref(false)
const pendingCount = ref(0)

// ── 审核弹窗 ──
const reviewVisible = ref(false)
const reviewTarget = ref<any>(null)
const reviewAction = ref<'approved' | 'rejected'>('approved')
const reviewComment = ref('')
const reviewSubmitting = ref(false)

// ── 辅助 ──
function statusTagType(status: string): 'warning' | 'success' | 'danger' {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function statusLabel(status: string): string {
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已驳回'
  return '待审核'
}

// ── 加载 ──
async function loadCorrections() {
  loading.value = true
  try {
    const res = await getCorrections({ status: statusFilter.value })
    const data = res.data?.data || res.data || {}
    corrections.value = data.items || []

    // 同时加载待审核计数
    if (statusFilter.value === 'pending') {
      pendingCount.value = corrections.value.length
    }
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

async function loadPendingCount() {
  try {
    const res = await getCorrections({ status: 'pending', page_size: 1 })
    const data = res.data?.data || res.data || {}
    pendingCount.value = data.pagination?.total || data.items?.length || 0
  } catch {
    /* ignore */
  }
}

function handleFilterChange() {
  loadCorrections()
}

// ── 审核弹窗 ──
function openReviewDialog(item: any, action: 'approved' | 'rejected') {
  reviewTarget.value = item
  reviewAction.value = action
  reviewComment.value = ''
  reviewVisible.value = true
}

async function handleReviewSubmit() {
  if (reviewAction.value === 'rejected' && !reviewComment.value.trim()) {
    ElMessage.warning('驳回时必须填写原因')
    return
  }
  if (!reviewTarget.value) return

  reviewSubmitting.value = true
  try {
    const payload: { action: string; comment?: string } = { action: reviewAction.value }
    if (reviewComment.value.trim()) {
      payload.comment = reviewComment.value.trim()
    }
    await reviewCorrection(reviewTarget.value.request_id, payload)
    ElMessage.success(reviewAction.value === 'approved' ? '已通过该纠错申请' : '已驳回该纠错申请')
    reviewVisible.value = false
    loadCorrections()
    loadPendingCount()
  } catch {
    /* error handled by interceptor */
  } finally {
    reviewSubmitting.value = false
  }
}

onMounted(() => {
  loadCorrections()
  loadPendingCount()
})
</script>

<style scoped>
.corrections-view {
  max-width: 1000px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.tab-badge {
  /* override badge styles */
}

.corr-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.corr-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}

.corr-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.corr-meta {
  font-size: 12px;
  color: #94a3b8;
}

.corr-body {
  margin-bottom: 4px;
}

.corr-doc {
  font-size: 14px;
  color: #334155;
  margin-bottom: 4px;
}

.corr-section {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.corr-desc {
  background: var(--surface-muted);
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

.corr-desc p {
  margin: 0;
}

.corr-comment {
  margin-top: 10px;
  padding: 10px 12px;
  background: #fffbeb;
  border-radius: 8px;
  font-size: 13px;
  color: #92400e;
}

.corr-reviewer {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.corr-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

/* 审核弹窗 */
.review-info {
  background: var(--surface-muted);
  border-radius: 8px;
  padding: 12px 16px;
}

.review-info p {
  margin-bottom: 6px;
  font-size: 14px;
  color: #334155;
}

.review-desc {
  margin-top: 4px;
  font-size: 13px;
  color: #475569;
}

.review-desc p {
  margin: 0;
}
</style>
