<template>
  <div class="categories-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <h3>分类权限管理</h3>
        <el-radio-group v-model="activeType" size="small" @change="loadCategories">
          <el-radio-button value="document">文档分类</el-radio-button>
          <el-radio-button value="faq">FAQ分类</el-radio-button>
        </el-radio-group>
      </div>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>添加分类
      </el-button>
    </div>

    <!-- 树形表格 -->
    <div class="table-card" v-loading="loading">
      <el-table
        :data="categoryTree"
        row-key="category_id"
        stripe
        default-expand-all
        style="width: 100%"
      >
        <el-table-column prop="name" label="分类名称" min-width="180">
          <template #default="{ row }">
            <span :style="{ paddingLeft: (row._depth || 0) * 24 + 'px' }">
              <el-icon v-if="row.children && row.children.length" style="margin-right: 4px">
                <Folder />
              </el-icon>
              {{ row.name }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'document' ? '' : 'success'" size="small">
              {{ row.type === 'document' ? '文档' : 'FAQ' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="权限" width="120">
          <template #default="{ row }">
            <el-tag :type="accessLevelTagType(row.access_level)" size="small">
              {{ accessLevelLabel(row.access_level) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="子分类" width="80" align="center">
          <template #default="{ row }">
            {{ row.children?.length || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="排序" width="80" prop="sort_order" />

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="warning" size="small" @click="openAccessDialog(row)">权限</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!categoryTree.length && !loading" description="暂无分类" />
    </div>

    <!-- 添加/编辑分类弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="editingCat ? '编辑分类' : '添加分类'"
      width="480px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="50" />
        </el-form-item>

        <el-form-item label="父级分类" prop="parent_id">
          <el-select
            v-model="form.parent_id"
            placeholder="无（顶级分类）"
            style="width: 100%"
            clearable
          >
            <el-option label="无（顶级分类）" value="" />
            <el-option
              v-for="cat in flatCategories"
              :key="cat.category_id"
              :label="cat.name"
              :value="cat.category_id"
              :disabled="cat.category_id === editingCat?.category_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type" :disabled="!!editingCat">
            <el-radio value="document">文档</el-radio>
            <el-radio value="faq">FAQ</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="访问权限" prop="access_level">
          <el-select v-model="form.access_level" placeholder="请选择访问权限" style="width: 100%">
            <el-option label="全员可见 (all_roles)" value="all_roles" />
            <el-option label="HR+管理员 (hr_admin_only)" value="hr_admin_only" />
            <el-option label="仅管理员 (admin_only)" value="admin_only" />
          </el-select>
        </el-form-item>

        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="formSubmitting" @click="handleFormSubmit">
          {{ editingCat ? '保存修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 权限设置弹窗（PRD FR-2.6） -->
    <el-dialog
      v-model="accessVisible"
      title="修改分类权限"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="access-info">
        <p>
          当前分类：<strong>{{ accessTarget?.name }}</strong>
        </p>
        <p>
          当前权限：
          <el-tag :type="accessLevelTagType(accessTarget?.access_level || '')" size="small">
            {{ accessLevelLabel(accessTarget?.access_level || '') }}
          </el-tag>
        </p>
      </div>

      <el-form label-width="100px" style="margin-top: 16px">
        <el-form-item label="新权限级别">
          <el-select
            v-model="newAccessLevel"
            placeholder="选择新权限级别"
            style="width: 100%"
          >
            <el-option label="全员可见 (all_roles)" value="all_roles" />
            <el-option label="HR+管理员 (hr_admin_only)" value="hr_admin_only" />
            <el-option label="仅管理员 (admin_only)" value="admin_only" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="accessVisible = false">取消</el-button>
        <el-button type="primary" :loading="accessSubmitting" @click="handleAccessSave">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Folder } from '@element-plus/icons-vue'
import { getCategories, createCategory, updateCategoryAccess } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// ── 状态 ──
const activeType = ref<'document' | 'faq'>('document')
const categoryTree = ref<any[]>([])
const flatCategories = ref<any[]>([])
const loading = ref(false)

// ── 表单弹窗 ──
const formVisible = ref(false)
const editingCat = ref<any>(null)
const formSubmitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  parent_id: '' as string,
  type: 'document' as 'document' | 'faq',
  access_level: 'all_roles',
  sort_order: 0,
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  access_level: [{ required: true, message: '请选择访问权限', trigger: 'change' }],
}

// ── 权限弹窗 ──
const accessVisible = ref(false)
const accessTarget = ref<any>(null)
const newAccessLevel = ref('')
const accessSubmitting = ref(false)

// ── 辅助方法 ──
function accessLevelTagType(level: string): 'info' | 'success' | 'warning' | 'danger' {
  if (level === 'inherit') return 'info'
  if (level === 'all_roles') return 'success'
  if (level === 'hr_admin_only') return 'warning'
  if (level === 'admin_only') return 'danger'
  return 'info'
}

function accessLevelLabel(level: string): string {
  const map: Record<string, string> = {
    all_roles: '全员可见',
    hr_admin_only: 'HR+管理',
    admin_only: '仅管理员',
  }
  return map[level] || level
}

// ── 构建树形数据 ──
function buildTree(list: any[], depth: number = 0): any[] {
  return list.map((item) => ({
    ...item,
    _depth: depth,
    children: item.children ? buildTree(item.children, depth + 1) : [],
  }))
}

function flattenTree(list: any[]): any[] {
  const result: any[] = []
  const walk = (nodes: any[]) => {
    for (const node of nodes) {
      result.push(node)
      if (node.children) walk(node.children)
    }
  }
  walk(list)
  return result
}

// ── 数据加载 ──
async function loadCategories() {
  loading.value = true
  try {
    const res = await getCategories({ type: activeType.value })
    const items = res.data?.items || res.data?.data?.items || []
    categoryTree.value = buildTree(items)
    flatCategories.value = flattenTree(items)
  } catch {
    /* error handled by interceptor */
  } finally {
    loading.value = false
  }
}

// ── 添加/编辑弹窗 ──
function openAddDialog() {
  editingCat.value = null
  resetForm()
  form.type = activeType.value
  formVisible.value = true
}

function openEditDialog(row: any) {
  editingCat.value = row
  form.name = row.name
  form.parent_id = row.parent_id || ''
  form.type = row.type
  form.access_level = row.access_level
  form.sort_order = row.sort_order || 0
  formVisible.value = true
}

function resetForm() {
  form.name = ''
  form.parent_id = ''
  form.type = activeType.value
  form.access_level = 'all_roles'
  form.sort_order = 0
  formRef.value?.resetFields()
}

async function handleFormSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  formSubmitting.value = true
  try {
    const payload: any = {
      name: form.name,
      parent_id: form.parent_id || null,
      type: form.type,
      access_level: form.access_level,
      sort_order: form.sort_order,
    }
    await createCategory(payload)
    ElMessage.success(editingCat.value ? '分类已更新' : '分类已添加')
    formVisible.value = false
    loadCategories()
  } catch {
    /* error handled by interceptor */
  } finally {
    formSubmitting.value = false
  }
}

// ── 权限弹窗 ──
function openAccessDialog(row: any) {
  accessTarget.value = row
  newAccessLevel.value = row.access_level
  accessVisible.value = true
}

async function handleAccessSave() {
  if (!accessTarget.value) return

  // 弹出确认对话框，询问是否级联更新
  try {
    await ElMessageBox.confirm(
      `是否将新权限「${accessLevelLabel(newAccessLevel.value)}」应用到该分类下所有继承权限的文档？`,
      '确认权限更新',
      {
        confirmButtonText: '是，全部应用',
        cancelButtonText: '否，仅影响新建文档',
        distinguishCancelAndClose: true,
        type: 'warning',
      },
    )
    // 用户点击"是，全部应用" -> cascade=true
    await doAccessSave(true)
  } catch (action: any) {
    if (action === 'cancel') {
      // 用户点击"否，仅影响新建文档" -> cascade=false
      await doAccessSave(false)
    }
    // 用户点击右上角关闭或按ESC -> 不做任何操作
  }
}

async function doAccessSave(cascade: boolean) {
  if (!accessTarget.value) return
  accessSubmitting.value = true
  try {
    await updateCategoryAccess(accessTarget.value.category_id, newAccessLevel.value, cascade)
    ElMessage.success(cascade ? '权限已更新，继承权限的文档已同步' : '权限已更新')
    accessVisible.value = false
    loadCategories()
  } catch {
    /* error handled by interceptor */
  } finally {
    accessSubmitting.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.categories-view {
  max-width: 1200px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.table-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.access-info {
  background: var(--surface-muted);
  border-radius: 8px;
  padding: 12px 16px;
}

.access-info p {
  margin-bottom: 8px;
  font-size: 14px;
  color: #334155;
}

.access-info p:last-child {
  margin-bottom: 0;
}
</style>
