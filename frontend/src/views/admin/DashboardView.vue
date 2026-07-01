<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="12" :lg="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card">
          <div class="stat-top">
            <span class="stat-label">{{ card.label }}</span>
            <div class="stat-icon" :style="{ background: card.iconBg }">
              <component :is="card.icon" :style="{ color: card.iconColor }" :size="20" />
            </div>
          </div>
          <p class="stat-value">{{ card.value }}</p>
          <p class="stat-change" :class="card.changeType">
            {{ card.change }}
          </p>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="24" :lg="12">
        <div class="chart-card">
          <h3>问答趋势（近7天）</h3>
          <div ref="trendChartRef" class="chart-box"></div>
        </div>
      </el-col>
      <el-col :span="24" :lg="12">
        <div class="chart-card">
          <h3>问答类型分布</h3>
          <div ref="pieChartRef" class="chart-box"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 热门 + 分类 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="24" :lg="16">
        <div class="chart-card">
          <h3>热门问题 TOP 10</h3>
          <div class="hot-list">
            <div v-for="(item, idx) in hotQuestions" :key="idx" class="hot-item">
              <div class="hot-info">
                <span class="hot-rank">{{ idx + 1 }}</span>
                <span class="hot-question">{{ item.question }}</span>
                <span class="hot-count">{{ item.count }} 次</span>
              </div>
              <div class="hot-bar">
                <div class="hot-bar-inner" :style="{ width: item.percent }"></div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="24" :lg="8">
        <div class="chart-card">
          <h3>分类覆盖率</h3>
          <div ref="categoryChartRef" class="chart-box"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 待优化问题：答不出/被评无帮助的高频提问 → 一键生成 FAQ 草稿 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="24">
        <div class="chart-card">
          <div class="section-head">
            <h3>待优化问题（知识盲区）</h3>
            <span class="section-hint">来自答不出或被评"没帮助"的真实提问，可一键生成 FAQ 补齐</span>
          </div>
          <el-table :data="faqCandidates" stripe v-loading="candidatesLoading" empty-text="暂无待优化问题">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="question" label="问题" min-width="240" show-overflow-tooltip />
            <el-table-column label="出现次数" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.count }} 次</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="答不出" width="90" align="center">
              <template #default="{ row }">{{ row.no_result_count || 0 }}</template>
            </el-table-column>
            <el-table-column label="评为无用" width="90" align="center">
              <template #default="{ row }">{{ row.not_helpful_count || 0 }}</template>
            </el-table-column>
            <el-table-column label="最近提问" width="170">
              <template #default="{ row }">{{ row.last_asked?.slice(0, 19).replace('T', ' ') || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openDraftDialog(row)">
                  生成FAQ草稿
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- FAQ 草稿弹窗：LLM 生成后 HR 审核编辑再发布 -->
    <el-dialog v-model="draftVisible" title="生成 FAQ 草稿" width="640px" :close-on-click-modal="false">
      <div v-loading="draftGenerating" :element-loading-text="draftGenerating ? 'AI 正在依据制度文档生成草稿...' : ''">
        <el-form :model="draftForm" label-width="80px">
          <el-form-item label="问题">
            <el-input v-model="draftForm.question" maxlength="500" />
          </el-form-item>
          <el-form-item label="答案">
            <el-input v-model="draftForm.answer" type="textarea" :rows="6" />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="draftForm.keywords" placeholder="逗号分隔" />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="draftForm.category_id" placeholder="选择 FAQ 分类" style="width: 100%">
              <el-option
                v-for="c in categories"
                :key="c.category_id"
                :label="c.name"
                :value="c.category_id"
              />
            </el-select>
          </el-form-item>
          <p v-if="draftForm._model" class="draft-model-hint">
            本草稿由模型 {{ draftForm._model }} 依据现有制度文档生成，请人工核对后再发布。
          </p>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="draftVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="draftPublishing"
          :disabled="draftGenerating || !draftForm.answer || !draftForm.category_id"
          @click="handlePublishDraft"
        >
          发布为 FAQ
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, reactive } from 'vue'
import * as echarts from 'echarts'
import { ChatDotRound, UserFilled, Files, QuestionFilled } from '@element-plus/icons-vue'
import { getDashboard, getFaqCandidates, generateFaqDraft, getCategories, createFAQ } from '@/api/admin'
import { ElMessage } from 'element-plus'

const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const statCards = reactive([
  { label: '今日问答', value: 0, change: '加载中...', changeType: 'info', icon: ChatDotRound, iconBg: '#eff6ff', iconColor: '#3b82f6' },
  { label: '活跃用户', value: 0, change: '加载中...', changeType: 'info', icon: UserFilled, iconBg: '#f0fdf4', iconColor: '#10b981' },
  { label: '制度文档', value: 0, change: '加载中...', changeType: 'info', icon: Files, iconBg: '#faf5ff', iconColor: '#8b5cf6' },
  { label: 'FAQ条目', value: 0, change: '加载中...', changeType: 'info', icon: QuestionFilled, iconBg: '#fffbeb', iconColor: '#f59e0b' },
])

const hotQuestions = ref<any[]>([])
const dashboardData = ref<any>(null)

async function loadDashboard() {
  try {
    const res = await getDashboard('7d')
    const d = res.data?.data || res.data || {}
    dashboardData.value = d
    statCards[0].value = d.total_questions || 0
    statCards[1].value = d.total_users || 0
    statCards[2].value = d.total_documents || 0
    statCards[3].value = d.total_faqs || 0
    statCards[0].change = d.today_questions != null ? `今日 ${d.today_questions} 次` : '—'
    statCards[1].change = `共 ${d.total_users || 0} 名用户`
    statCards[2].change = `已发布 ${d.total_documents || 0} 篇`
    statCards[3].change = d.faq_match_rate != null ? `匹配率 ${d.faq_match_rate}%` : `共 ${d.total_faqs || 0} 条`
    // 热门问题 TOP10：取自用户在 AI 问答中真实提出的问题（按出现次数）
    if (d.hot_search_terms) {
      const maxCount = Math.max(...d.hot_search_terms.map((h: any) => h.count || 0), 1)
      hotQuestions.value = d.hot_search_terms.map((h: any) => ({
        question: h.term || '',
        count: h.count || 0,
        percent: Math.round((h.count || 0) / maxCount * 100) + '%',
      }))
    }
    await nextTick()
    refreshCharts()
  } catch {
    // 使用默认数据
    statCards[0].value = 0; statCards[1].value = 0
    statCards[2].value = 0; statCards[3].value = 0
  }
}

function refreshCharts() {
  if (trendChart) trendChart.dispose()
  if (pieChart) pieChart.dispose()
  if (categoryChart) categoryChart.dispose()
  initTrendChart()
  initPieChart()
  initCategoryChart()
}

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const d = dashboardData.value
  const dates = d?.daily_trend?.map((t: any) => t.date) || []
  const values = d?.daily_trend?.map((t: any) => t.count) || []
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: dates.length ? dates : ['暂无数据'] },
    yAxis: { type: 'value' },
    series: [{
      type: 'line', smooth: true,
      data: values.length ? values : [0],
      itemStyle: { color: '#0369a1' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(3,105,161,0.3)' },
        { offset: 1, color: 'rgba(3,105,161,0.02)' },
      ])},
    }],
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const d = dashboardData.value
  const typeDist = d?.answer_type_distribution || {}
  const pieData = Object.entries(typeDist).map(([name, value]) => ({
    name: { faq: 'FAQ匹配', search: '全文搜索', rule: '规则匹配', rag: 'RAG', no_result: '未找到' }[name] || name,
    value,
    itemStyle: { color: { faq: '#10b981', search: '#0369a1', rule: '#f59e0b', rag: '#8b5cf6', no_result: '#ef4444' }[name] || '#94a3b8' },
  }))
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie', radius: ['50%', '75%'], center: ['50%', '45%'],
      label: { show: false },
      data: pieData.length ? pieData : [{ value: 1, name: '暂无数据', itemStyle: { color: '#e2e8f0' } }],
    }],
  })
}

function initCategoryChart() {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  const d = dashboardData.value
  const catDist = d?.category_distribution || []
  const catData = (Array.isArray(catDist) ? catDist : []).map((c: any) => [c.category_name || c.category_id || '未分类', c.count || 0])
  categoryChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 100, right: 20, top: 10, bottom: 20 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: catData.map(c => c[0]) },
    series: [{
      type: 'bar',
      data: catData.map(c => c[1]),
      itemStyle: { color: '#0369a1', borderRadius: [0, 4, 4, 0] },
      barMaxWidth: 20,
    }],
  })
}

onMounted(async () => {
  await loadDashboard()
  loadCandidates()
  loadCategories()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
  categoryChart?.dispose()
})

function handleResize() {
  trendChart?.resize()
  pieChart?.resize()
  categoryChart?.resize()
}

// ── 待优化问题 → FAQ 草稿 ──
const faqCandidates = ref<any[]>([])
const candidatesLoading = ref(false)
const categories = ref<any[]>([])

const draftVisible = ref(false)
const draftGenerating = ref(false)
const draftPublishing = ref(false)
const draftForm = reactive<any>({
  question: '',
  answer: '',
  keywords: '',
  category_id: '',
  related_doc_id: null,
  _model: '',
})

async function loadCandidates() {
  candidatesLoading.value = true
  try {
    const res = await getFaqCandidates(10)
    const d = res.data?.data || res.data || {}
    faqCandidates.value = d.items || []
  } catch {
    /* error handled by interceptor */
  } finally {
    candidatesLoading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await getCategories({ type: 'faq' })
    const d = res.data?.data || res.data || {}
    const items = d.items || []
    // 分类接口返回的是树，拍平成下拉可用的扁平列表（与 FAQ 管理页一致）
    const flat: any[] = []
    const flatten = (list: any[]) => {
      list.forEach((c) => {
        flat.push({ category_id: c.category_id, name: c.name })
        if (c.children) flatten(c.children)
      })
    }
    flatten(items)
    categories.value = flat
  } catch {
    /* error handled by interceptor */
  }
}

async function openDraftDialog(row: any) {
  // 先带上原问题打开弹窗，再异步向 LLM 请求草稿
  draftForm.question = row.question
  draftForm.answer = ''
  draftForm.keywords = ''
  draftForm.category_id = categories.value[0]?.category_id || ''
  draftForm.related_doc_id = null
  draftForm._model = ''
  draftVisible.value = true

  draftGenerating.value = true
  try {
    const res = await generateFaqDraft(row.question)
    const d = res.data?.data || res.data || {}
    draftForm.question = d.question || row.question
    draftForm.answer = d.answer || ''
    draftForm.keywords = d.keywords || ''
    draftForm.related_doc_id = d.related_doc_id || null
    draftForm._model = d._model || ''
  } catch {
    // LLM 不可用时保留问题，允许 HR 手动填写答案
  } finally {
    draftGenerating.value = false
  }
}

async function handlePublishDraft() {
  if (!draftForm.answer || !draftForm.category_id) {
    ElMessage.warning('答案和分类不能为空')
    return
  }
  draftPublishing.value = true
  try {
    await createFAQ({
      question: draftForm.question,
      answer: draftForm.answer,
      category_id: draftForm.category_id,
      related_doc_id: draftForm.related_doc_id || undefined,
      keywords: draftForm.keywords || undefined,
    })
    ElMessage.success('FAQ 已发布')
    draftVisible.value = false
    loadCandidates()
  } catch {
    /* error handled by interceptor */
  } finally {
    draftPublishing.value = false
  }
}

// ── 待优化问题 → FAQ 草稿 结束 ──
</script>

<style scoped>
.dashboard { max-width: 1400px; }

.section-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.section-hint {
  font-size: 12px;
  color: var(--text-secondary, #909399);
}
.draft-model-hint {
  font-size: 12px;
  color: var(--text-secondary, #909399);
  margin: 0;
}

.stat-row { margin-bottom: 24px; }

.stat-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.2s;
  margin-bottom: 16px;
}
.stat-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); }

.stat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.stat-label { font-size: 14px; color: #64748b; }
.stat-icon {
  width: 36px; height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-value { font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-change { font-size: 12px; margin-top: 4px; }
.stat-change.up { color: #10b981; }
.stat-change.info { color: #94a3b8; }

.chart-row { margin-bottom: 24px; }
.chart-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}
.chart-card h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 16px;
}
.chart-box { height: 280px; }

/* 热门列表 */
.hot-list { padding: 0 8px; }
.hot-item { margin-bottom: 16px; }
.hot-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
}
.hot-rank {
  width: 24px; text-align: center;
  color: #94a3b8; font-weight: 600;
}
.hot-question { flex: 1; color: #334155; }
.hot-count { color: #94a3b8; font-size: 13px; }
.hot-bar {
  height: 6px;
  background: var(--surface);
  border-radius: 3px;
  overflow: hidden;
}
.hot-bar-inner {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>
