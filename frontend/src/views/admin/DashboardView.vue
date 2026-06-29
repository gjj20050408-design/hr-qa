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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, reactive } from 'vue'
import * as echarts from 'echarts'
import { ChatDotRound, UserFilled, Files, QuestionFilled } from '@element-plus/icons-vue'
import { getDashboard } from '@/api/admin'

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
    const d = res.data || {}
    dashboardData.value = d
    statCards[0].value = d.total_questions || 0
    statCards[1].value = d.active_users || 0
    statCards[2].value = d.total_documents || 0
    statCards[3].value = d.total_faqs || 0
    if (d.daily_trend) {
      statCards[0].change = d.today_questions ? `今日 ${d.today_questions} 次` : '加载中...'
    }
    if (d.hot_topics) {
      const maxCount = Math.max(...d.hot_topics.map((h: any) => h.count || 0), 1)
      hotQuestions.value = d.hot_topics.map((h: any) => ({
        question: h.topic || h.keyword || '',
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
  const typeDist = d?.type_distribution || {}
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
  const catDist = d?.category_distribution || {}
  const catData = Object.entries(catDist).map(([name, value]) => [name, value])
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
</script>

<style scoped>
.dashboard { max-width: 1400px; }

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
