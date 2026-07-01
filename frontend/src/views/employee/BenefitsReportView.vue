<template>
  <div class="benefits-layout">
    <div class="benefits-inner" v-loading="loading">
      <!-- 报告头 -->
      <div class="report-header">
        <div class="report-title">
          <h2>您的 {{ report?.year || currentYear }} 年专属权益清单</h2>
          <p v-if="report">
            {{ report.user_name }}
            <span v-if="report.department_name"> · {{ report.department_name }}</span>
            · 工龄 {{ report.tenure_years ?? 0 }} 年
          </p>
        </div>
        <div class="header-actions">
          <el-select v-model="selectedYear" size="small" class="year-select" @change="load">
            <el-option v-for="y in yearOptions" :key="y" :label="`${y} 年`" :value="y" />
          </el-select>
          <el-button size="small" :icon="Refresh" :loading="refreshing" @click="refresh">
            刷新报告
          </el-button>
        </div>
      </div>

      <!-- 整体寄语 -->
      <div v-if="report?.summary" class="report-summary">
        {{ report.summary }}
      </div>

      <!-- 权益条目卡片 -->
      <div class="benefit-grid">
        <div v-for="(item, idx) in report?.items || []" :key="idx" class="benefit-card">
          <div class="card-top">
            <span class="card-title">{{ item.title }}</span>
            <el-tag size="small" effect="plain">{{ item.category || '权益' }}</el-tag>
          </div>
          <div class="card-value">{{ item.value }}</div>
          <p class="card-desc">{{ item.description }}</p>
        </div>
      </div>

      <el-empty v-if="!loading && !report?.items?.length" description="暂无权益数据" :image-size="80" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { BenefitReport } from '@/types'
import { getBenefitReport, refreshBenefitReport } from '@/api/insights'

const currentYear = new Date().getFullYear()
const yearOptions = [currentYear, currentYear - 1, currentYear - 2]
const selectedYear = ref(currentYear)
const report = ref<BenefitReport | null>(null)
const loading = ref(false)
const refreshing = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await getBenefitReport(selectedYear.value)
    report.value = res.data?.data || null
  } catch {
    report.value = null
  } finally {
    loading.value = false
  }
}

async function refresh() {
  refreshing.value = true
  try {
    const res = await refreshBenefitReport(selectedYear.value)
    report.value = res.data?.data || null
    ElMessage.success('已刷新权益报告')
  } catch {
    // ignore
  } finally {
    refreshing.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.benefits-layout {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
.benefits-inner {
  max-width: 960px;
  margin: 0 auto;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}
.report-title h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--primary);
}
.report-title p {
  font-size: 14px;
  color: #64748b;
  margin-top: 6px;
}
.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.year-select {
  width: 110px;
}

.report-summary {
  background: linear-gradient(135deg, #eff6ff, #f0fdfa);
  border: 1px solid #dbeafe;
  border-radius: 12px;
  padding: 16px 20px;
  font-size: 14px;
  color: #334155;
  line-height: 1.7;
  margin-bottom: 24px;
}

.benefit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.benefit-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  transition: all 0.15s;
}
.benefit-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}
.card-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 8px;
}
.card-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}
</style>
