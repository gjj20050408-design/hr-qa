<template>
  <div class="history-layout">
    <div class="history-header">
      <div>
        <h2>我的问答历史</h2>
        <p>共 <strong>{{ displayTotal }}</strong> 条记录</p>
      </div>
      <div class="header-actions">
        <el-select v-model="typeFilter" size="small" class="filter-select">
          <el-option label="全部类型" value="all" />
          <el-option label="FAQ匹配" value="faq" />
          <el-option label="全文搜索" value="search" />
          <el-option label="规则匹配" value="rule" />
        </el-select>
        <el-input
          v-model="searchText"
          placeholder="搜索历史..."
          :prefix-icon="Search"
          size="small"
          class="search-input"
        />
      </div>
    </div>

    <div class="history-list">
      <div
        v-for="record in paginatedRecords"
        :key="record.record_id"
        class="history-card"
        @click="expandRecord(record)"
      >
        <div class="record-header">
          <h3>{{ record.question }}</h3>
          <el-tag :type="typeTag(record.answer_type)" size="small">
            {{ typeLabel(record.answer_type) }}
          </el-tag>
        </div>
        <div v-if="expandedId === record.record_id" class="record-answer">
          {{ record.answer }}
        </div>
        <div v-else class="record-preview">
          {{ record.answer?.slice(0, 100) }}{{ record.answer?.length > 100 ? '...' : '' }}
        </div>
        <div class="record-footer">
          <span>{{ record.created_at?.slice(0, 16) }} · 响应 {{ (record.response_time_ms / 1000).toFixed(2) }}s</span>
          <el-button link :type="record.is_favorite ? 'warning' : 'info'" size="small" @click.stop="toggleFav(record)">
            <el-icon><StarFilled v-if="record.is_favorite" /></el-icon>
          </el-button>
        </div>
      </div>

      <el-empty v-if="!filteredRecords.length" description="暂无问答记录" :image-size="80" />

      <div class="pagination-row" v-if="displayTotal > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="displayTotal"
          layout="prev, pager, next"
          size="small"
          background
          @current-change="loadRecords"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search, StarFilled } from '@element-plus/icons-vue'
import type { QARecord } from '@/types'
import { useChatStore } from '@/stores/chat'
import { getQARecords } from '@/api/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()
const searchText = ref('')
const typeFilter = ref('all')
const expandedId = ref<string>('')
const currentPage = ref(1)
const pageSize = ref(10)
const records = ref<QARecord[]>([])
const total = ref(0)

async function loadRecords() {
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (typeFilter.value !== 'all') params.answer_type = typeFilter.value
    const res = await getQARecords(params)
    records.value = res.data?.data?.items || []
    total.value = res.data?.data?.pagination?.total || 0
  } catch {}
}

onMounted(loadRecords)

// 类型筛选变更时重新加载
watch(typeFilter, () => {
  currentPage.value = 1
  loadRecords()
})

const filteredRecords = computed(() => {
  if (!searchText.value) return records.value
  return records.value.filter(r => r.question.includes(searchText.value))
})

const paginatedRecords = computed(() => {
  // 有搜索文本时使用客户端分页，否则直接显示API已分页的数据
  if (searchText.value) {
    const start = (currentPage.value - 1) * pageSize.value
    return filteredRecords.value.slice(start, start + pageSize.value)
  }
  return filteredRecords.value
})

// 搜索时用客户端过滤后的总数，否则用API返回的总数
const displayTotal = computed(() => searchText.value ? filteredRecords.value.length : total.value)

function typeLabel(t: string) {
  const map: Record<string, string> = { faq: 'FAQ匹配', rule: '规则匹配', search: '全文搜索', rag: 'RAG问答', no_result: '未找到' }
  return map[t] || t
}

function typeTag(t: string) {
  const map: Record<string, string> = { faq: 'success', rule: 'primary', search: 'info', rag: '', no_result: 'danger' }
  return map[t] || ''
}

function expandRecord(record: QARecord) {
  expandedId.value = expandedId.value === record.record_id ? '' : record.record_id
}

async function toggleFav(record: QARecord) {
  try {
    const newState = !record.is_favorite
    const result = await chatStore.toggleFavorite(record.record_id, newState)
    record.is_favorite = result
    ElMessage.success(result ? '已收藏' : '已取消')
  } catch {
    // ignore
  }
}
</script>

<style scoped>
.history-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  padding: 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.history-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
.history-header p {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 4px;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.filter-select { width: 120px; }
.search-input { width: 200px; }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.history-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.history-card:hover {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.record-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  flex: 1;
  margin-right: 8px;
}

.record-preview {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.record-answer {
  font-size: 13px;
  color: #475569;
  margin-bottom: 12px;
  padding: 12px;
  background: var(--surface-muted);
  border-radius: 8px;
  line-height: 1.6;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

.pagination-row {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
