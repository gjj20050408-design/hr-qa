<template>
  <div class="categories-view">
    <el-row :gutter="16">
      <el-col :span="24" :lg="12" v-for="cat in categories" :key="cat.category_id">
        <div class="cat-card">
          <div class="cat-header">
            <h3>{{ cat.name }}</h3>
            <el-tag :type="cat.access_level==='all_roles'?'success':'warning'" size="small">
              {{ cat.access_level==='all_roles'?'全员可见':'HR可见' }}
            </el-tag>
          </div>
          <div class="cat-items">
            <div v-for="child in cat.children" :key="child.category_id" class="cat-item" :class="{active: child.category_id===cat.children?.[0]?.category_id}">
              {{ child.name }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
const categories = [
  { category_id:'cat-doc-1',name:'考勤制度',access_level:'all_roles',children:[
    {category_id:'s1',name:'打卡管理'},{category_id:'s2',name:'加班政策'},{category_id:'s3',name:'调休规定'}
  ]},
  { category_id:'cat-doc-2',name:'薪酬制度',access_level:'hr_admin_only',children:[
    {category_id:'s4',name:'薪资结构'},{category_id:'s5',name:'奖金发放'},{category_id:'s6',name:'个税说明'}
  ]},
]
</script>

<style scoped>
.categories-view { max-width: 1000px; }
.cat-card { background:white; border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:16px; }
.cat-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.cat-header h3 { font-size:14px; font-weight:600; color:var(--primary); }
.cat-items { display:flex; flex-direction:column; gap:4px; }
.cat-item { padding:8px 12px; border-radius:6px; font-size:14px; color:#475569; cursor:pointer; transition:background 0.15s; }
.cat-item:hover { background:var(--surface-muted); }
.cat-item.active { background:var(--surface-muted); color:var(--accent); font-weight:500; }
</style>
