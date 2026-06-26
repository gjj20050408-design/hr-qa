<template>
  <div class="users-view">
    <div class="toolbar">
      <h3>用户管理</h3>
      <el-button type="primary"><el-icon><Plus /></el-icon>添加用户</el-button>
    </div>
    <div class="table-card">
      <el-table :data="users" stripe>
        <el-table-column prop="employee_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="140" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{row}">
            <el-tag :type="row.role==='admin'?'danger':row.role==='hr_specialist'?'warning':'info'" size="small">
              {{ row.role==='admin'?'管理员':row.role==='hr_specialist'?'HR专员':'普通员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{row}">
            <el-tag :type="row.status==='active'?'success':'danger'" size="small">
              {{ row.status==='active'?'正常':'禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default>
            <el-button link type="primary" size="small">编辑</el-button>
            <el-button link type="danger" size="small">禁用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const users = ref([
  { employee_id:'admin001',name:'系统管理员',department:'人力资源部',role:'admin',status:'active' },
  { employee_id:'hr001',name:'李HR',department:'人力资源部',role:'hr_specialist',status:'active' },
  { employee_id:'emp001',name:'张三',department:'技术部',role:'employee',status:'active' },
])
</script>

<style scoped>
.users-view { max-width:1200px; }
.toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.toolbar h3 { font-size:18px; font-weight:700; color:var(--primary); }
.table-card { background:white; border:1px solid var(--border); border-radius:12px; overflow:hidden; }
</style>
