<template>
  <div class="search-layout">
    <!-- 左侧搜索面板 -->
    <aside class="search-panel">
      <div class="search-header">
        <h2>制度搜索</h2>
        <div class="search-input-wrapper">
          <el-input
            v-model="keyword"
            placeholder="输入关键词搜索制度..."
            :prefix-icon="Search"
            size="large"
            @keyup.enter="doSearch"
          />
        </div>
        <div class="category-tags">
          <el-tag
            v-for="cat in allCategories"
            :key="cat.value"
            :type="selectedCategory === cat.value ? 'primary' : 'info'"
            class="cat-tag"
            @click="selectedCategory = selectedCategory === cat.value ? '' : cat.value"
          >
            {{ cat.label }}
          </el-tag>
        </div>
      </div>

      <div class="search-results">
        <p class="result-count" v-if="results.length">
          找到 <strong>{{ total }}</strong> 条相关制度
        </p>

        <div
          v-for="doc in results"
          :key="doc.document_id"
          class="result-card"
          :class="{ active: selectedDoc?.document_id === doc.document_id }"
          @click="selectDoc(doc)"
        >
          <div class="card-header">
            <h3>{{ doc.title }}</h3>
            <el-tag
              :type="doc.has_access !== false ? 'success' : 'warning'"
              size="small"
            >
              {{ doc.has_access !== false ? '可查看' : '需HR权限' }}
            </el-tag>
          </div>
          <p class="card-summary" v-html="getHighlight(doc.content || doc.summary || '')"></p>
          <div class="card-meta">
            <span>{{ doc.category_name }}</span>
            <span>V{{ doc.version }}</span>
            <span>{{ doc.updated_at?.slice(0, 10) }}</span>
          </div>
        </div>

        <el-empty v-if="!results.length && keyword" description="未找到相关制度" />
        <el-pagination
          v-if="total > pageSize"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          size="small"
          class="search-pagination"
          @change="doSearch"
        />
      </div>
    </aside>

    <!-- 右侧文档详情 -->
    <section class="doc-detail" v-if="selectedDoc">
      <div class="detail-header">
        <div class="detail-title-row">
          <div>
            <h2>{{ selectedDoc.title }}</h2>
            <div class="detail-meta">
              <span>{{ selectedDoc.category_name }}</span>
              <span class="dot"></span>
              <span>版本 V{{ selectedDoc.version }}</span>
              <span class="dot"></span>
              <span>{{ selectedDoc.updated_at?.slice(0, 10) }} 更新</span>
            </div>
          </div>
          <el-button size="small" class="correction-btn">纠错反馈</el-button>
        </div>
      </div>
      <div class="detail-content" v-html="formattedContent"></div>
    </section>
    <section class="doc-detail empty-detail" v-else>
      <el-empty description="请从左侧选择文档查看详情" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { searchDocuments, getDocumentDetail } from '@/api/search'
import type { Document as DocType } from '@/types'

const keyword = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const results = ref<DocType[]>([])
const selectedDoc = ref<DocType | null>(null)

const allCategories = [
  { label: '全部', value: '' },
  { label: '考勤制度', value: 'cat-doc-1' },
  { label: '休假制度', value: 'cat-doc-4' },
  { label: '薪酬制度', value: 'cat-doc-2' },
  { label: '福利制度', value: 'cat-doc-3' },
  { label: '绩效制度', value: 'cat-doc-5' },
]

// 模拟数据用于原型展示
const mockResults: DocType[] = [
  {
    document_id: 'doc-001',
    title: '年假天数与工龄计算规定',
    content: '员工累计工作已满1年不满10年的，年假5天；已满10年不满20年的，年假10天；已满20年的，年假15天。',
    summary: '...员工累计工作已满1年不满10年的，年假5天；已满10年不满20年的，年假10天...',
    category_id: 'cat-doc-4-1',
    category_name: '休假制度 · 年假规定',
    format: 'word',
    version: '2.1',
    version_note: '',
    status: 'published',
    access_level: 'all_roles',
    uploaded_by: '',
    word_count: 1500,
    published_at: '2026-06-15',
    created_at: '2026-06-15',
    updated_at: '2026-06-15',
    has_access: true,
  },
  {
    document_id: 'doc-002',
    title: '年假申请流程与审批规范',
    content: '员工申请年假需提前3个工作日通过OA系统提交，由直属主管审批。',
    summary: '...员工申请年假需提前3个工作日通过OA系统提交...',
    category_id: 'cat-doc-4-1',
    category_name: '休假制度 · 年假规定',
    format: 'word',
    version: '1.3',
    version_note: '',
    status: 'published',
    access_level: 'all_roles',
    uploaded_by: '',
    word_count: 800,
    published_at: '2026-05-20',
    created_at: '2026-05-20',
    updated_at: '2026-05-20',
    has_access: true,
  },
  {
    document_id: 'doc-003',
    title: '病假与年假转换政策说明',
    content: '该文档需要HR专员及以上权限才能查看完整内容',
    summary: '该文档需要HR专员及以上权限才能查看完整内容',
    category_id: 'cat-doc-4-2',
    category_name: '休假制度 · 病假规定',
    format: 'word',
    version: '1.0',
    version_note: '',
    status: 'published',
    access_level: 'hr_admin_only',
    uploaded_by: '',
    word_count: 500,
    published_at: '2026-04-01',
    created_at: '2026-04-01',
    updated_at: '2026-04-01',
    has_access: false,
  },
]

const formattedContent = computed(() => {
  if (!selectedDoc.value) return ''
  const doc = selectedDoc.value
  return `
    <h3>第一条 年假享受条件</h3>
    <p>员工连续工作满1年以上的，享受带薪年休假（以下简称年假）。员工在年假期间享受与正常工作期间相同的工资收入。</p>
    <h3>第二条 年假天数标准</h3>
    <p>员工累计工作年限满1年不满10年的，年假<span class="search-highlight">5天</span>；满10年不满20年的，年假<span class="search-highlight">10天</span>；满20年的，年假<span class="search-highlight">15天</span>。</p>
    <h3>第三条 年假申请流程</h3>
    <p>员工申请年假需提前3个工作日通过OA系统提交，由直属主管审批。连续申请5天以上需提前7个工作日申请。年假最小申请单位为半天。</p>
    <div class="tips-box">
      <p class="tips-title">提示</p>
      <p>当年未休完的年假可延期至次年3月31日，过期作废。</p>
    </div>
  `
})

function getHighlight(text: string) {
  if (!keyword.value) return text
  const reg = new RegExp(`(${keyword.value})`, 'g')
  return text.replace(reg, '<span class="search-highlight">$1</span>')
}

function selectDoc(doc: DocType) {
  selectedDoc.value = doc
}

async function doSearch() {
  if (!keyword.value.trim()) return
  try {
    const res = await searchDocuments({
      keyword: keyword.value,
      category_id: selectedCategory.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    results.value = res.data.items
    total.value = res.data.pagination.total
  } catch {
    // 使用mock数据
    results.value = mockResults.filter(
      d => d.title.includes(keyword.value) || d.content.includes(keyword.value)
    )
    total.value = results.value.length
  }
}

onMounted(() => {
  keyword.value = '年假'
  // 预加载mock数据
  results.value = mockResults
  total.value = mockResults.length
  selectedDoc.value = mockResults[0]
})
</script>

<style scoped>
.search-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧搜索面板 */
.search-panel {
  width: 100%;
  max-width: 400px;
  border-right: 1px solid var(--border);
  background: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .search-panel { max-width: 100%; }
}

.search-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.search-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 16px;
}
.search-input-wrapper {
  margin-bottom: 12px;
}
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.cat-tag {
  cursor: pointer;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.result-count {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 12px;
}
.result-count strong {
  font-weight: 600;
  color: #475569;
}

.result-card {
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.result-card:hover {
  border-color: rgba(3, 105, 161, 0.5);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.result-card.active {
  border-color: var(--accent);
  background: rgba(3, 105, 161, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.card-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  flex: 1;
  margin-right: 8px;
}
.result-card:hover .card-header h3,
.result-card.active .card-header h3 {
  color: var(--accent);
}

.card-summary {
  font-size: 12px;
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
}

.search-pagination {
  margin-top: 12px;
  justify-content: center;
}

/* 右侧文档详情 */
.doc-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  overflow: hidden;
}
@media (max-width: 1023px) {
  .doc-detail { display: none; }
}
.empty-detail {
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-header {
  padding: 24px;
  border-bottom: 1px solid var(--border);
  background: white;
}
.detail-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.detail-title-row h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
  font-size: 12px;
  color: #94a3b8;
}
.dot {
  width: 4px;
  height: 4px;
  background: #cbd5e1;
  border-radius: 50%;
}
.correction-btn {
  color: var(--accent);
  border-color: var(--accent);
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  max-width: 800px;
  line-height: 1.8;
  font-size: 14px;
  color: #475569;
}
.detail-content :deep(h3) {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 12px;
  margin-top: 24px;
}
.detail-content :deep(p) {
  margin-bottom: 12px;
}
.detail-content :deep(.tips-box) {
  background: rgba(3, 105, 161, 0.05);
  border: 1px solid rgba(3, 105, 161, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}
.detail-content :deep(.tips-title) {
  font-size: 14px;
  font-weight: 500;
  color: var(--accent);
  margin-bottom: 4px;
}
</style>
