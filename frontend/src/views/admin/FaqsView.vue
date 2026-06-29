<template>
  <div class="faqs-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchText" placeholder="搜索FAQ..." :prefix-icon="Search" size="default" class="search-input" />
        <el-select v-model="categoryFilter" placeholder="全部分类" size="default" class="tool-select" @change="loadFAQs">
          <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
        </el-select>
      </div>
      <el-button type="primary"><el-icon><Plus /></el-icon>新增FAQ</el-button>
    </div>

    <div class="faq-list">
      <div v-for="faq in filteredFaqs" :key="faq.faq_id" class="faq-card">
        <div class="faq-top">
          <h3>{{ faq.question }}</h3>
          <el-tag size="small">{{ faq.category_label }}</el-tag>
        </div>
        <p class="faq-answer">{{ faq.answer }}</p>
        <div class="faq-bottom">
          <span>{{ faq.view_count }} 次匹配</span>
          <el-button link type="primary" size="small">编辑</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { getFAQs, getCategories } from '@/api/admin'

const searchText = ref('')
const categoryFilter = ref('all')
const faqs = ref<any[]>([])
const categories = ref<{ label: string; value: string }[]>([{ label: '全部分类', value: 'all' }])

async function loadFAQs() {
  try {
    const params: any = {}
    if (categoryFilter.value !== 'all') params.category_id = categoryFilter.value
    if (searchText.value) params.keyword = searchText.value
    const res = await getFAQs(params)
    faqs.value = res.data?.items || []
  } catch {}
}

async function loadCategories() {
  try {
    const res = await getCategories({ type: 'faq' })
    const items = res.data?.items || []
    categories.value = [{ label: '全部分类', value: 'all' }]
    const flatten = (list: any[]) => {
      for (const c of list) {
        categories.value.push({ label: c.name, value: c.category_id })
        if (c.children) flatten(c.children)
      }
    }
    flatten(items)
  } catch {}
}

onMounted(() => { loadCategories(); loadFAQs() })

const filteredFaqs = computed(() => faqs.value)
</script>

<style scoped>
.faqs-view { max-width: 1000px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px; }
.toolbar-left { display:flex; gap:12px; align-items:center; }
.search-input { width:220px; }
.tool-select { width:130px; }
.faq-list { display:flex; flex-direction:column; gap:12px; }
.faq-card { background:white; border:1px solid var(--border); border-radius:12px; padding:20px; }
.faq-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.faq-top h3 { font-size:14px; font-weight:600; color:var(--primary); }
.faq-answer { font-size:13px; color:#64748b; line-height:1.6; }
.faq-bottom { display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding-top:12px; border-top:1px solid var(--border-light); font-size:12px; color:#94a3b8; }
</style>
