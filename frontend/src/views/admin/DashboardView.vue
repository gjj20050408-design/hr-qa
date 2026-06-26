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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ChatDotRound, UserFilled, Files, QuestionFilled } from '@element-plus/icons-vue'

const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const statCards = [
  {
    label: '今日问答', value: '1,247', change: '↑ 12.5% 较昨日', changeType: 'up',
    icon: ChatDotRound, iconBg: '#eff6ff', iconColor: '#3b82f6',
  },
  {
    label: '活跃用户', value: '328', change: '↑ 8.3% 较昨日', changeType: 'up',
    icon: UserFilled, iconBg: '#f0fdf4', iconColor: '#10b981',
  },
  {
    label: '制度文档', value: '86', change: '已发布 72 · 草稿 14', changeType: 'info',
    icon: Files, iconBg: '#faf5ff', iconColor: '#8b5cf6',
  },
  {
    label: 'FAQ条目', value: '145', change: '活跃 138 · 归档 7', changeType: 'info',
    icon: QuestionFilled, iconBg: '#fffbeb', iconColor: '#f59e0b',
  },
]

const hotQuestions = [
  { question: '年假有多少天？', count: 1234, percent: '85%' },
  { question: '加班费怎么算？', count: 987, percent: '68%' },
  { question: '婚假几天？', count: 756, percent: '52%' },
  { question: '体检什么时间？', count: 543, percent: '38%' },
  { question: '绩效考核标准？', count: 432, percent: '30%' },
]

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 10, bottom: 30 },
    xAxis: {
      type: 'category',
      data: ['06/18', '06/19', '06/20', '06/21', '06/22', '06/23', '06/24'],
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'line',
      smooth: true,
      data: [820, 932, 901, 1134, 1023, 1190, 1247],
      itemStyle: { color: '#0369a1' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(3,105,161,0.3)' },
          { offset: 1, color: 'rgba(3,105,161,0.02)' },
        ]),
      },
    }],
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
      center: ['50%', '45%'],
      label: { show: false },
      data: [
        { value: 45, name: 'FAQ匹配', itemStyle: { color: '#10b981' } },
        { value: 30, name: '全文搜索', itemStyle: { color: '#0369a1' } },
        { value: 15, name: '规则匹配', itemStyle: { color: '#f59e0b' } },
        { value: 10, name: '未找到', itemStyle: { color: '#ef4444' } },
      ],
    }],
  })
}

function initCategoryChart() {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  categoryChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 100, right: 20, top: 10, bottom: 20 },
    xAxis: { type: 'value' },
    yAxis: {
      type: 'category',
      data: ['考勤', '薪酬', '福利', '休假', '绩效'],
    },
    series: [{
      type: 'bar',
      data: [95, 78, 88, 92, 65],
      itemStyle: { color: '#0369a1', borderRadius: [0, 4, 4, 0] },
      barMaxWidth: 20,
    }],
  })
}

onMounted(async () => {
  await nextTick()
  initTrendChart()
  initPieChart()
  initCategoryChart()

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
