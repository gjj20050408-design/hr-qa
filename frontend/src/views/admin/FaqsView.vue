<template>
  <div class="faqs-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchText" placeholder="搜索FAQ..." :prefix-icon="Search" size="default" class="search-input" @keyup.enter="loadFAQs" clearable />
        <el-select v-model="categoryFilter" placeholder="全部分类" size="default" class="tool-select" @change="loadFAQs">
          <el-option v-for="cat in categories" :key="cat.value" :label="cat.label" :value="cat.value" />
        </el-select>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>新增FAQ
      </el-button>
    </div>

    <div class="faq-list" v-loading="loading">
      <el-empty v-if="!filteredFaqs.length && !loading" description="暂无FAQ" />
      <div v-for="faq in filteredFaqs" :key="faq.faq_id" class="faq-card">
        <div class="faq-top">
          <h3>{{ faq.question }}</h3>
          <el-tag size="small">{{ faq.category_name || faq.category_label }}</el-tag>
        </div>
        <p class="faq-answer">{{ faq.answer }}</p>
        <div class="faq-bottom">
          <span>{{ faq.view_count || 0 }} 次匹配 · {{ faq.status === 'archived' ? '已归档' : '正常' }}</span>
          <div class="faq-actions">
            <el-button link type="primary" size="small" @click="openEditDialog(faq)">编辑</el-button>
            <el-popconfirm title="确认删除此FAQ？" @confirm="handleDelete(faq)">
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingFaq ? '编辑FAQ' : '新增FAQ'" width="600px" :close-on-click-modal="false" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="问题" prop="question">
          <el-input v-model="form.question" placeholder="请输入问题（如：年假有多少天？）" maxlength="500" />
        </el-form-item>
        <el-form-item label="答案" prop="answer">
          <el-input v-model="form.answer" type="textarea" :rows="5" placeholder="请输入答案" maxlength="2000" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="选择FAQ分类" style="width:100%">
            <el-option v-for="cat in categoryOptions" :key="cat.value" :label="cat.label" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" placeholder="搜索关键词（空格分隔，可不填）" maxlength="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSave">{{ editingFaq ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { getFAQs, getCategories, createFAQ, updateFAQ, deleteFAQ } from '@/api/admin'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const searchText = ref('')
const categoryFilter = ref('all')
const faqs = ref<any[]>([])
const loading = ref(false)
const categories = ref<{ label: string; value: string }[]>([{ label: '全部分类', value: 'all' }])
const categoryOptions = ref<{ label: string; value: string }[]>([])

// 弹窗
const dialogVisible = ref(false)
const editingFaq = ref<any>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = ref({ question: '', answer: '', category_id: '', keywords: '' })
const rules: FormRules = {
  question: [{ required: true, message: '请输入问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入答案', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

async function loadFAQs() {
  loading.value = true
  try {
    const params: any = {}
    if (categoryFilter.value !== 'all') params.category_id = categoryFilter.value
    if (searchText.value) params.keyword = searchText.value
    const res = await getFAQs(params)
    faqs.value = res.data?.data?.items || res.data?.items || []
  } catch {} finally { loading.value = false }
}

async function loadCategories() {
  try {
    const res = await getCategories({ type: 'faq' })
    const items = res.data?.data?.items || res.data?.items || []
    categories.value = [{ label: '全部分类', value: 'all' }]
    categoryOptions.value = []
    const flatten = (list: any[]) => {
      for (const c of list) {
        categories.value.push({ label: c.name, value: c.category_id })
        categoryOptions.value.push({ label: c.name, value: c.category_id })
        if (c.children) flatten(c.children)
      }
    }
    flatten(items)
  } catch {}
}

// 新增
function openCreateDialog() {
  editingFaq.value = null
  form.value = { question: '', answer: '', category_id: categoryOptions.value[0]?.value || '', keywords: '' }
  dialogVisible.value = true
}

// 编辑
function openEditDialog(faq: any) {
  editingFaq.value = faq
  form.value = {
    question: faq.question,
    answer: faq.answer,
    category_id: faq.category_id,
    keywords: faq.keywords || '',
  }
  dialogVisible.value = true
}

function resetForm() {
  editingFaq.value = null
  formRef.value?.resetFields()
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingFaq.value) {
      await updateFAQ(editingFaq.value.faq_id, form.value)
      ElMessage.success('FAQ已更新')
    } else {
      await createFAQ(form.value)
      ElMessage.success('FAQ创建成功')
    }
    dialogVisible.value = false
    loadFAQs()
  } catch {} finally { submitting.value = false }
}

// 删除
async function handleDelete(faq: any) {
  try {
    await deleteFAQ(faq.faq_id)
    ElMessage.success('FAQ已删除')
    loadFAQs()
  } catch {}
}

const filteredFaqs = computed(() => faqs.value)

onMounted(() => { loadCategories(); loadFAQs() })
</script>

<style scoped>
.faqs-view { max-width: 1000px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px; }
.toolbar-left { display:flex; gap:12px; align-items:center; }
.search-input { width:220px; }
.tool-select { width:130px; }
.faq-list { display:flex; flex-direction:column; gap:12px; min-height: 100px; }
.faq-card { background:white; border:1px solid var(--border); border-radius:12px; padding:20px; }
.faq-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }
.faq-top h3 { font-size:14px; font-weight:600; color:var(--primary); }
.faq-answer { font-size:13px; color:#64748b; line-height:1.6; }
.faq-bottom { display:flex; justify-content:space-between; align-items:center; margin-top:12px; padding-top:12px; border-top:1px solid var(--border-light); font-size:12px; color:#94a3b8; }
.faq-actions { display:flex; gap:4px; }
</style>
