<template>
  <div class="history-layout">
    <div class="history-header">
      <div>
        <h2>我的问答历史</h2>
        <p>共 <strong>{{ filteredRecords.length }}</strong> 条记录</p>
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
          <span>{{ record.created_at?.slice(0, 16) }} · 响应 {{ record.response_time_ms }}ms</span>
          <el-button link :type="record.is_favorite ? 'warning' : 'info'" size="small" @click.stop="toggleFav(record)">
            <el-icon><StarFilled v-if="record.is_favorite" /></el-icon>
          </el-button>
        </div>
      </div>

      <el-empty v-if="!filteredRecords.length" description="暂无问答记录" :image-size="80" />

      <div class="pagination-row" v-if="totalPages > 1">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredRecords.length"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, StarFilled } from '@element-plus/icons-vue'
import type { QARecord } from '@/types'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()
const searchText = ref('')
const typeFilter = ref('all')
const expandedId = ref<string>('')
const currentPage = ref(1)
const pageSize = ref(10)

// Mock数据
const records = ref<QARecord[]>([
  {
    record_id: 'rec-001',
    user_id: '',
    session_id: '',
    question: '我的工龄是3年，请问我有多少天年假？',
    answer: '根据规定，您的工龄3年属于"满1年不满10年"，每年享有5天带薪年假。',
    answer_type: 'rule',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 120,
    is_favorite: true,
    created_at: '2026-06-24 10:30',
  },
  {
    record_id: 'rec-002',
    user_id: '',
    session_id: '',
    question: '加班费如何计算？',
    answer: '工作日加班1.5倍，休息日2倍，法定节假日3倍工资。加班需提前申请并经主管审批通过。',
    answer_type: 'faq',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 85,
    is_favorite: false,
    created_at: '2026-06-23 15:22',
  },
  {
    record_id: 'rec-003',
    user_id: '',
    session_id: '',
    question: '婚假需要满足什么条件？',
    answer: '符合法定年龄可享受3天婚假，晚婚额外7天共10天。需提供结婚证复印件，提前1个月申请。',
    answer_type: 'faq',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 95,
    is_favorite: false,
    created_at: '2026-06-20',
  },
  {
    record_id: 'rec-004',
    user_id: '',
    session_id: '',
    question: '绩效考核的标准是什么？',
    answer: '绩效考核按季度进行，每年4次。评分标准包括工作业绩、能力素质、团队协作三个维度。',
    answer_type: 'search',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 250,
    is_favorite: false,
    created_at: '2026-06-18',
  },
])

const filteredRecords = computed(() => {
  return records.value.filter(r => {
    const typeMatch = typeFilter.value === 'all' || r.answer_type === typeFilter.value
    const searchMatch = !searchText.value || r.question.includes(searchText.value)
    return typeMatch && searchMatch
  })
})

const totalPages = computed(() => Math.ceil(filteredRecords.value.length / pageSize.value))

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRecords.value.slice(start, start + pageSize.value)
})

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
    const result = await chatStore.toggleFavorite(record.record_id)
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
