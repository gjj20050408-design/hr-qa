<template>
  <div class="documents-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchText" placeholder="搜索文档..." :prefix-icon="Search" size="default" class="search-input" />
        <el-select v-model="statusFilter" placeholder="全部状态" size="default" class="tool-select">
          <el-option label="全部状态" value="all" />
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-select v-model="categoryFilter" placeholder="全部分类" size="default" class="tool-select">
          <el-option label="全部分类" value="all" />
          <el-option label="考勤制度" value="cat-doc-1" />
          <el-option label="休假制度" value="cat-doc-4" />
          <el-option label="薪酬制度" value="cat-doc-2" />
          <el-option label="福利制度" value="cat-doc-3" />
        </el-select>
      </div>
      <el-button type="primary"><el-icon><Plus /></el-icon>上传文档</el-button>
    </div>

    <div class="table-card">
      <el-table :data="filteredDocs" stripe>
        <el-table-column prop="title" label="文档标题" min-width="200" />
        <el-table-column prop="category_name" label="分类" width="130" />
        <el-table-column label="版本" width="80"><template #default="{row}">V{{row.version}}</template></el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="row.status==='published'?'success':row.status==='draft'?'info':'info'" size="small">
              {{ row.status==='published'?'已发布':row.status==='draft'?'草稿':'已归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="access_level" label="权限" width="90">
          <template #default="{row}">
            <el-tag :type="row.access_level==='all_roles'?'success':'warning'" size="small">
              {{ row.access_level==='all_roles'?'全员':'HR可见' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="120"><template #default="{row}">{{row.updated_at?.slice(0,10)}}</template></el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default>
            <el-button link type="primary" size="small">编辑</el-button>
            <el-button link type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'

const searchText = ref('')
const statusFilter = ref('all')
const categoryFilter = ref('all')

const docs = ref([
  { document_id:'doc-001',title:'年假天数与工龄计算规定',category_name:'休假制度',version:'2.1',status:'published',access_level:'all_roles',updated_at:'2026-06-15' },
  { document_id:'doc-002',title:'薪资结构与发放标准',category_name:'薪酬制度',version:'3.0',status:'published',access_level:'hr_admin_only',updated_at:'2026-06-10' },
  { document_id:'doc-003',title:'健康体检福利政策',category_name:'福利制度',version:'1.0',status:'archived',access_level:'all_roles',updated_at:'2026-03-01' },
])

const filteredDocs = computed(() => docs.value.filter(d => {
  const matchTitle = !searchText.value || d.title.includes(searchText.value)
  const matchStatus = statusFilter.value === 'all' || d.status === statusFilter.value
  const matchCat = categoryFilter.value === 'all' || d.category_name.includes(
    categoryFilter.value === 'cat-doc-1' ? '考勤' : categoryFilter.value === 'cat-doc-4' ? '休假' : categoryFilter.value === 'cat-doc-2' ? '薪酬' : categoryFilter.value === 'cat-doc-3' ? '福利' : ''
  )
  return matchTitle && matchStatus && matchCat
}))
</script>

<style scoped>
.documents-view { max-width: 1400px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px; }
.toolbar-left { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
.search-input { width:220px; }
.tool-select { width:130px; }
.table-card { background:white; border:1px solid var(--border); border-radius:12px; overflow:hidden; }
</style>
