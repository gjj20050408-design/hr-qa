<template>
  <div class="interpretation-layout">
    <!-- 左：可解读文档列表 -->
    <aside class="doc-aside">
      <div class="aside-header">
        <h3>制度文档</h3>
        <el-input
          v-model="keyword"
          placeholder="搜索制度..."
          :prefix-icon="Search"
          size="small"
          clearable
          @keyup.enter="loadDocs"
          @clear="loadDocs"
        />
      </div>
      <div class="doc-list">
        <div
          v-for="doc in docs"
          :key="doc.document_id"
          class="doc-item"
          :class="{ active: selectedId === doc.document_id }"
          @click="selectDoc(doc)"
        >
          <h4>{{ doc.title }}</h4>
          <p>{{ doc.category_name || '未分类' }} · v{{ doc.version }}</p>
        </div>
        <el-empty v-if="!docs.length" description="暂无制度文档" :image-size="60" />
      </div>
    </aside>

    <!-- 右：解读详情 -->
    <section class="detail-section">
      <el-empty v-if="!selectedId" description="请选择左侧制度文档查看 AI 解读" :image-size="100" />

      <div v-else class="detail-inner" v-loading="loading">
        <div class="detail-toolbar">
          <h2>{{ current?.title }}</h2>
          <div class="toolbar-actions">
            <el-tag v-if="current?.cached" type="info" size="small">缓存</el-tag>
            <el-tag v-if="current?.degraded" type="warning" size="small">AI 暂不可用</el-tag>
            <el-button
              v-if="authStore.isHR"
              size="small"
              :icon="Refresh"
              :loading="refreshing"
              @click="refresh"
            >
              重新生成
            </el-button>
          </div>
        </div>

        <template v-if="current && !loading">
          <div v-if="current.degraded" class="degrade-tip">
            {{ current.message || 'AI 解读服务暂不可用，已展示制度原文摘要。' }}
          </div>

          <!-- 通俗摘要 -->
          <div v-if="current.summary" class="block">
            <h3 class="block-title">通俗解读</h3>
            <div class="md-body" v-html="renderMarkdown(current.summary)"></div>
          </div>

          <!-- 流程图 -->
          <div v-if="current.flowchart" class="block">
            <h3 class="block-title">办理流程</h3>
            <MermaidChart :code="current.flowchart" />
          </div>

          <!-- 对比表格 -->
          <div v-if="current.comparison_table" class="block">
            <h3 class="block-title">分档对比</h3>
            <div class="md-body" v-html="renderMarkdown(current.comparison_table)"></div>
          </div>

          <!-- 要点 -->
          <div v-if="current.key_points?.length" class="block">
            <h3 class="block-title">关键要点</h3>
            <ul class="key-points">
              <li v-for="(kp, i) in current.key_points" :key="i">{{ kp }}</li>
            </ul>
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Document as DocType, PolicyInterpretation } from '@/types'
import { useAuthStore } from '@/stores/auth'
import { searchDocuments } from '@/api/search'
import { getInterpretation, refreshInterpretation } from '@/api/insights'
import { renderMarkdown } from '@/utils/markdown'
import MermaidChart from '@/components/MermaidChart.vue'

const authStore = useAuthStore()
const keyword = ref('')
const docs = ref<DocType[]>([])
const selectedId = ref('')
const current = ref<PolicyInterpretation | null>(null)
const loading = ref(false)
const refreshing = ref(false)

async function loadDocs() {
  try {
    const res: any = await searchDocuments({ keyword: keyword.value, page: 1, page_size: 50 } as any)
    const data = res.data?.data || res.data || {}
    docs.value = data.items || []
  } catch {
    docs.value = []
  }
}

async function selectDoc(doc: DocType) {
  selectedId.value = doc.document_id
  current.value = null
  loading.value = true
  try {
    const res = await getInterpretation(doc.document_id)
    current.value = res.data?.data || null
  } catch {
    // 拦截器已提示错误（如 403 无权限）
    selectedId.value = ''
  } finally {
    loading.value = false
  }
}

async function refresh() {
  if (!selectedId.value) return
  refreshing.value = true
  try {
    const res = await refreshInterpretation(selectedId.value)
    current.value = res.data?.data || null
    ElMessage.success('已重新生成解读')
  } catch {
    // ignore
  } finally {
    refreshing.value = false
  }
}

onMounted(loadDocs)
</script>

<style scoped>
.interpretation-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧文档列表 */
.doc-aside {
  width: 320px;
  flex-shrink: 0;
  background: white;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}
.aside-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.aside-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 12px;
}
.doc-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.doc-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 4px;
}
.doc-item:hover {
  background: var(--surface-muted);
}
.doc-item.active {
  background: var(--accent);
}
.doc-item.active h4,
.doc-item.active p {
  color: white;
}
.doc-item h4 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}
.doc-item p {
  font-size: 12px;
  color: #94a3b8;
}

/* 右侧详情 */
.detail-section {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
.detail-inner {
  max-width: 860px;
  margin: 0 auto;
}
.detail-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}
.detail-toolbar h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.degrade-tip {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #b45309;
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
  margin-bottom: 16px;
}

.block {
  margin-bottom: 24px;
}
.block-title {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid var(--accent);
}
.key-points {
  margin: 0;
  padding-left: 20px;
}
.key-points li {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
}

/* markdown 正文样式 */
.md-body {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
}
.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3) {
  font-weight: 700;
  margin: 12px 0 8px;
  color: #1e293b;
}
.md-body :deep(p) {
  margin: 8px 0;
}
.md-body :deep(ul),
.md-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}
.md-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 13px;
}
.md-body :deep(th),
.md-body :deep(td) {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}
.md-body :deep(th) {
  background: var(--surface-muted);
  font-weight: 600;
}
.md-body :deep(code) {
  background: var(--surface-muted);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
</style>
