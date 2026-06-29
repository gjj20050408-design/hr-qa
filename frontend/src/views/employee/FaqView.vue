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
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { FAQ, Category } from '@/types'
import { getFAQs } from '@/api/faq'
import { getCategories } from '@/api/admin'

const searchText = ref('')
const activeCategory = ref('all')
const activeNames = ref<string[]>([])
const faqs = ref<FAQ[]>([])
const categories = ref<{ label: string; value: string }[]>([])

async function loadFAQs() {
  try {
    const params: any = { page_size: 100 }
    if (activeCategory.value !== 'all') params.category_id = activeCategory.value
    const res = await getFAQs(params)
    faqs.value = res.data?.items || []
  } catch {}
}

async function loadCategories() {
  try {
    const res = await getCategories({ type: 'faq' })
    const raw = res.data || []
    categories.value = [
      { label: '全部FAQ', value: 'all' },
      ...(Array.isArray(raw) ? raw : []).map((c: Category) => ({
        label: c.name + 'FAQ',
        value: c.category_id,
      })),
    ]
  } catch {}
}

onMounted(() => {
  loadCategories()
  loadFAQs()
})

const filteredFaqs = computed(() => {
  return faqs.value.filter(faq => {
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
