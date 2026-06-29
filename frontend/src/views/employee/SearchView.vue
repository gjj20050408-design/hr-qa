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
          <span v-if="filteredCount > 0" class="filtered-count">
            （已过滤 {{ filteredCount }} 条受限文档）
          </span>
        </p>

        <!-- 权限过滤提示 -->
        <div v-if="notice" class="filter-notice">
          🔒 {{ notice }}
        </div>

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
          <p class="card-summary" v-html="getHighlight(doc.snippet || '')"></p>
          <div class="card-meta">
            <span>{{ doc.category || doc.category_name }}</span>
            <span>V{{ doc.version }}</span>
            <span>{{ doc.published_at?.slice(0, 10) || doc.updated_at?.slice(0, 10) }}</span>
          </div>
        </div>

        <el-empty v-if="!results.length && keyword && !notice" description="未找到相关制度" />
        <div v-if="!results.length && notice" class="filter-notice-full">
          🔒 {{ notice }}
        </div>
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
          <el-button size="small" class="correction-btn" @click="openCorrectionDialog">纠错反馈</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Document as DocType } from '@/types'

const keyword = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const results = ref<DocType[]>([])
const selectedDoc = ref<DocType | null>(null)

const allCategories = ref<{ label: string; value: string }[]>([])
const notice = ref('')
const filteredCount = ref(0)
const searching = ref(false)

const formattedContent = computed(() => {
  if (!selectedDoc.value) return ''
  return selectedDoc.value.content || '文档内容加载中...'
})

function getHighlight(text: string) {
  if (!keyword.value) return text
  const reg = new RegExp(`(${keyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(reg, '<span class="search-highlight">$1</span>')
}

async function selectDoc(doc: DocType) {
  try {
    const res = await getDocumentDetail(doc.document_id)
    const resData = res.data || res
    const data = resData.data || resData
    selectedDoc.value = { ...doc, ...data }
  } catch {
    selectedDoc.value = doc
  }
}

async function loadCategories() {
  try {
    const { getCategories } = await import('@/api/admin')
    const res = await getCategories({ type: 'document' })
    const roots = res.data.data?.items || []
    // 递归展开树形分类，只取非根节点的叶子分类
    const flat: { label: string; value: string }[] = []
    function walk(nodes: any[]) {
      for (const n of nodes) {
        if (n.children && n.children.length > 0) {
          walk(n.children)
        } else {
          flat.push({ label: n.name, value: n.category_id })
        }
      }
    }
    walk(roots)
    allCategories.value = [
      { label: '全部', value: '' },
      ...flat,
    ]
  } catch { /* 使用默认分类 */ }
}

async function doSearch() {
  if (!keyword.value.trim()) return
  searching.value = true
  try {
    const res = await searchDocuments({
      keyword: keyword.value,
      category_id: selectedCategory.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    // res 是 AxiosResponse，res.data 是响应体 {code, data:{items, pagination}}
    const resData = res.data || res
    const data = resData.data || {}
    results.value = data.items || []
    total.value = data.pagination?.total || 0
    notice.value = data.notice || ''
    filteredCount.value = data.pagination?.filtered_count || 0
  } catch (e) {
    console.error('搜索失败:', e)
    results.value = []
    total.value = 0
  } finally {
    searching.value = false
  }
}

function openCorrectionDialog() {
  if (!selectedDoc.value) return
  // 打开纠错提交弹窗
  ElMessageBox.prompt('请输入您发现的错误或建议', '纠错反馈', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '请描述文档中的错误或您的改进建议...',
  }).then(async ({ value }) => {
    if (!value?.trim()) return
    try {
      const { createCorrection } = await import('@/api/admin')
      await createCorrection({
        document_id: selectedDoc.value!.document_id,
        section: selectedDoc.value!.title,
        description: value.trim(),
      })
      ElMessage.success('纠错反馈已提交，感谢您的贡献')
    } catch {
      ElMessage.error('提交失败，请稍后重试')
    }
  }).catch(() => {
    // 用户取消
  })
}

onMounted(() => {
  loadCategories()
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

.filter-notice {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.filter-notice-full {
  text-align: center;
  padding: 32px 16px;
  color: #94a3b8;
  font-size: 14px;
}

.filtered-count {
  color: #f59e0b;
  font-size: 12px;
  margin-left: 4px;
}
</style>
