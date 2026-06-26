<template>
  <div class="faq-layout">
    <!-- 左侧分类 -->
    <aside class="faq-categories">
      <div class="faq-search">
        <el-input
          v-model="searchText"
          placeholder="搜索常见问题..."
          :prefix-icon="Search"
          size="default"
        />
      </div>
      <div class="category-list">
        <div
          v-for="cat in categories"
          :key="cat.value"
          class="category-item"
          :class="{ active: activeCategory === cat.value }"
          @click="activeCategory = cat.value"
        >
          {{ cat.label }}
        </div>
      </div>
    </aside>

    <!-- 右侧FAQ列表 -->
    <section class="faq-content">
      <div class="faq-header">
        <h2>常见问题 (FAQ)</h2>
        <p>共 <strong>{{ filteredFaqs.length }}</strong> 条常见问题</p>
      </div>
      <div class="faq-list">
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item
            v-for="faq in filteredFaqs"
            :key="faq.faq_id"
            :name="faq.faq_id"
          >
            <template #title>
              <span class="faq-title">{{ faq.question }}</span>
            </template>
            <div class="faq-answer" v-html="formatAnswer(faq.answer)"></div>
            <div class="faq-footer">
              <span>来源：{{ faq.category_name }}</span>
              <span>被查看 {{ faq.view_count }} 次</span>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { FAQ } from '@/types'
import { getFAQs } from '@/api/faq'

const searchText = ref('')
const activeCategory = ref('all')
const activeNames = ref<string[]>([])

const categories = [
  { label: '全部FAQ', value: 'all' },
  { label: '考勤FAQ', value: 'cat-faq-1' },
  { label: '薪酬FAQ', value: 'cat-faq-2' },
  { label: '休假FAQ', value: 'cat-faq-3' },
  { label: '福利FAQ', value: 'cat-faq-4' },
  { label: '绩效FAQ', value: 'cat-faq-5' },
]

// Mock FAQ数据
const faqs: FAQ[] = [
  {
    faq_id: 'faq-001',
    question: '年假有多少天？工龄不同有什么区别？',
    answer: '根据《年假天数与工龄计算规定》第二条：<br><br>• 工龄 <strong>1-10年</strong>：每年 <strong>5天</strong> 带薪年假<br>• 工龄 <strong>10-20年</strong>：每年 <strong>10天</strong> 带薪年假<br>• 工龄 <strong>20年以上</strong>：每年 <strong>15天</strong> 带薪年假',
    category_id: 'cat-faq-3',
    category_name: '年假天数与工龄计算规定 V2.1',
    related_doc_id: '',
    keywords: '年假,工龄',
    view_count: 1234,
    status: 'active',
    created_by: '',
    created_at: '',
    updated_at: '',
  },
  {
    faq_id: 'faq-002',
    question: '加班费怎么计算？平时和周末有区别吗？',
    answer: '• <strong>工作日加班</strong>：按 <strong>1.5倍</strong> 工资计算<br>• <strong>休息日加班</strong>：按 <strong>2倍</strong> 工资计算<br>• <strong>法定节假日加班</strong>：按 <strong>3倍</strong> 工资计算<br><br>加班需提前申请并经主管审批通过。',
    category_id: 'cat-faq-1',
    category_name: '加班政策 V2.0',
    related_doc_id: '',
    keywords: '加班,加班费',
    view_count: 987,
    status: 'active',
    created_by: '',
    created_at: '',
    updated_at: '',
  },
  {
    faq_id: 'faq-003',
    question: '婚假能休多少天？需要什么材料？',
    answer: '• 符合法定结婚年龄（男22/女20周岁）：<strong>3天</strong>婚假<br>• 晚婚（男25/女23周岁以上）：额外 <strong>7天</strong>，共 <strong>10天</strong><br><br>需提供结婚证复印件，提前1个月申请。',
    category_id: 'cat-faq-3',
    category_name: '婚假/产假规定 V1.5',
    related_doc_id: '',
    keywords: '婚假,结婚',
    view_count: 756,
    status: 'active',
    created_by: '',
    created_at: '',
    updated_at: '',
  },
  {
    faq_id: 'faq-004',
    question: '公司每年安排体检吗？家属可以参加吗？',
    answer: '公司每年为入职满1年的员工安排 <strong>一次免费健康体检</strong>。家属可享受优惠价格参加。<br><br>体检时间一般在每年 <strong>5-6月</strong>，由HR统一邮件通知。',
    category_id: 'cat-faq-4',
    category_name: '健康体检政策 V1.0',
    related_doc_id: '',
    keywords: '体检,健康',
    view_count: 543,
    status: 'active',
    created_by: '',
    created_at: '',
    updated_at: '',
  },
  {
    faq_id: 'faq-005',
    question: '绩效考核的标准是什么？多久考核一次？',
    answer: '绩效考核按 <strong>季度</strong> 进行，每年 <strong>4次</strong>。评分标准包括工作业绩、能力素质、团队协作三个维度。<br><br>年度总分 = 各季度平均分 × 80% + 年度述职 × 20%。',
    category_id: 'cat-faq-5',
    category_name: '考核周期规定 V2.5',
    related_doc_id: '',
    keywords: '绩效,考核',
    view_count: 432,
    status: 'active',
    created_by: '',
    created_at: '',
    updated_at: '',
  },
]

const filteredFaqs = computed(() => {
  return faqs.filter(faq => {
    const matchCat = activeCategory.value === 'all' || faq.category_id === activeCategory.value
    const matchSearch = !searchText.value || faq.question.includes(searchText.value) || faq.answer.includes(searchText.value)
    return matchCat && matchSearch
  })
})

function formatAnswer(text: string) {
  return text.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.faq-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧分类 */
.faq-categories {
  width: 240px;
  border-right: 1px solid var(--border);
  background: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .faq-categories { width: 180px; }
}

.faq-search {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.category-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.category-item {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.category-item:hover {
  background: var(--surface-muted);
}
.category-item.active {
  background: rgba(3, 105, 161, 0.1);
  color: var(--accent);
  font-weight: 500;
}

/* 右侧FAQ */
.faq-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  overflow: hidden;
}
.faq-header {
  padding: 24px;
  background: white;
  border-bottom: 1px solid var(--border);
}
.faq-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
.faq-header p {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 4px;
}
.faq-header strong {
  font-weight: 600;
  color: #475569;
}

.faq-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.faq-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.faq-answer {
  font-size: 14px;
  color: #475569;
  line-height: 1.8;
  padding-bottom: 16px;
  border-top: 1px solid var(--border-light);
  padding-top: 16px;
}

.faq-footer {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

:deep(.el-collapse-item__header) {
  padding: 16px 20px;
  height: auto;
  line-height: 1.5;
}
:deep(.el-collapse-item__content) {
  padding: 0 20px 20px;
}
</style>
