<template>
  <div class="faqs-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchText" placeholder="搜索FAQ..." :prefix-icon="Search" size="default" class="search-input" />
        <el-select v-model="categoryFilter" placeholder="全部分类" size="default" class="tool-select">
          <el-option label="全部分类" value="all" />
          <el-option label="考勤FAQ" value="cat-faq-1" />
          <el-option label="薪酬FAQ" value="cat-faq-2" />
          <el-option label="休假FAQ" value="cat-faq-3" />
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
import { ref, computed } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'

const searchText = ref('')
const categoryFilter = ref('all')

const faqs = ref([
  { faq_id:'f1', question:'年假有多少天？', answer:'工龄1-10年享5天，10-20年享10天，20年以上享15天带薪年假。', category_id:'cat-faq-3', category_label:'休假FAQ', view_count:1234 },
  { faq_id:'f2', question:'加班费怎么计算？', answer:'工作日1.5倍，休息日2倍，法定节假日3倍。', category_id:'cat-faq-1', category_label:'考勤FAQ', view_count:987 },
])

const filteredFaqs = computed(() => faqs.value.filter(f => {
  const matchCat = categoryFilter.value === 'all' || f.category_id === categoryFilter.value
  const matchSearch = !searchText.value || f.question.includes(searchText.value)
  return matchCat && matchSearch
}))
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
