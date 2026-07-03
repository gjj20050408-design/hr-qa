<template>
  <div class="profile-page">
    <div class="profile-header">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回</span>
      </el-button>
      <h1>个人中心</h1>
    </div>

    <div class="profile-grid">
      <!-- 左侧：基本信息 -->
      <section class="card info-card">
        <div class="info-hero">
          <el-upload
            :show-file-list="false"
            :before-upload="handleAvatarUpload"
            accept="image/*"
            class="avatar-upload"
          >
            <div class="avatar-wrap" :class="{ uploading: avatarUploading }">
              <el-avatar :size="72" :src="user?.avatar_url || undefined" class="avatar-lg">
                {{ initial }}
              </el-avatar>
              <div class="avatar-mask">
                <el-icon v-if="avatarUploading" class="is-loading"><Loading /></el-icon>
                <template v-else>
                  <el-icon><Camera /></el-icon>
                  <span>更换头像</span>
                </template>
              </div>
            </div>
          </el-upload>
          <div class="hero-text">
            <h2>{{ user?.name || '未登录' }}</h2>
            <p>{{ user?.department_name || user?.department || '—' }} · {{ roleLabel }}</p>
            <div class="hero-actions">
              <el-tag v-if="user?.status === 'active'" type="success" size="small">在职</el-tag>
              <el-tag v-else-if="user?.status === 'disabled'" type="info" size="small">已停用</el-tag>
              <el-button
                v-if="user?.avatar_url"
                link
                type="danger"
                size="small"
                :disabled="avatarUploading"
                @click="handleAvatarDelete"
              >
                恢复默认头像
              </el-button>
            </div>
            <p class="avatar-tip">支持 jpg / png / webp / gif，2MB 以内</p>
          </div>
        </div>

        <ul class="info-list">
          <li>
            <span class="label">工号</span>
            <span class="value">{{ user?.employee_id || '—' }}</span>
          </li>
          <li>
            <span class="label">邮箱</span>
            <span class="value">{{ user?.email || '未填写' }}</span>
          </li>
          <li>
            <span class="label">手机号</span>
            <span class="value">{{ user?.phone || '未填写' }}</span>
          </li>
          <li>
            <span class="label">职级</span>
            <span class="value">{{ user?.job_level || '—' }}</span>
          </li>
          <li>
            <span class="label">入职日期</span>
            <span class="value">{{ user?.hire_date || '—' }}</span>
          </li>
          <li>
            <span class="label">工作地点</span>
            <span class="value">{{ user?.work_location || '—' }}</span>
          </li>
        </ul>

        <p class="info-hint">
          如需修改姓名、部门等基础信息，请联系 HR 或系统管理员。
        </p>
      </section>

      <!-- 右侧：修改密码 -->
      <section class="card password-card">
        <div class="card-title">
          <el-icon><Lock /></el-icon>
          <h2>修改密码</h2>
        </div>
        <p class="card-sub">密码需 8 位以上，且同时包含大小写字母与数字。</p>

        <el-form
          ref="pwdFormRef"
          :model="pwdForm"
          :rules="pwdRules"
          label-position="top"
          @submit.prevent="submitPassword"
        >
          <el-form-item label="旧密码" prop="old_password">
            <el-input
              v-model="pwdForm.old_password"
              type="password"
              show-password
              placeholder="请输入当前密码"
              size="large"
            />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="pwdForm.new_password"
              type="password"
              show-password
              placeholder="8 位以上，含大小写字母 + 数字"
              size="large"
            />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input
              v-model="pwdForm.confirm_password"
              type="password"
              show-password
              placeholder="再次输入新密码"
              size="large"
            />
          </el-form-item>
          <div class="form-actions">
            <el-button @click="resetPasswordForm">重置</el-button>
            <el-button type="primary" :loading="submitting" @click="submitPassword">
              保存修改
            </el-button>
          </div>
        </el-form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Lock, Camera, Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword, uploadAvatar, deleteAvatar } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const initial = computed(() => authStore.user?.name?.charAt(0) || '?')

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    admin: '系统管理员',
    hr_specialist: 'HR专员',
    employee: '普通员工',
  }
  return map[authStore.user?.role || ''] || '普通员工'
})

// 首次进入若 store 没有 user，主动拉一次（例如刷新页面后）
onMounted(async () => {
  if (!authStore.user) await authStore.fetchUserInfo()
})

// 头像上传
const avatarUploading = ref(false)

async function handleAvatarUpload(file: File) {
  const isImage = /^image\/(jpeg|png|gif|webp)$/i.test(file.type)
  if (!isImage) {
    ElMessage.error('仅支持 jpg / png / gif / webp 格式')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }

  avatarUploading.value = true
  try {
    const res = await uploadAvatar(file)
    authStore.setAvatar(res.data.avatar_url)
    ElMessage.success('头像更新成功')
  } catch {
    // 拦截器已提示
  } finally {
    avatarUploading.value = false
  }
  return false // 阻止 el-upload 默认上传行为
}

async function handleAvatarDelete() {
  try {
    await ElMessageBox.confirm('确认恢复为默认字母头像？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  avatarUploading.value = true
  try {
    await deleteAvatar()
    authStore.setAvatar(null)
    ElMessage.success('已恢复默认头像')
  } catch {
    // 拦截器已提示
  } finally {
    avatarUploading.value = false
  }
}

// 修改密码表单
const pwdFormRef = ref<FormInstance>()
const submitting = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 位', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, message: '需含大小写字母和数字', trigger: 'blur' },
    {
      validator: (_r, value: string, cb) => {
        if (value && value === pwdForm.old_password) cb(new Error('新密码不能与旧密码相同'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_r, value: string, cb) => {
        if (value !== pwdForm.new_password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

async function submitPassword() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await changePassword({
        old_password: pwdForm.old_password,
        new_password: pwdForm.new_password,
      })
      ElMessage.success('密码修改成功，请重新登录')
      // 密码变更后立即失效登录态，回到登录页
      await authStore.logout()
      router.replace('/login')
    } catch {
      // 拦截器已提示，具体错误无需重复
    } finally {
      submitting.value = false
    }
  })
}

function resetPasswordForm() {
  pwdFormRef.value?.resetFields()
}

function goBack() {
  // 优先回上一页，没有历史则按角色回到默认落地页
  if (window.history.length > 1) {
    router.back()
  } else if (authStore.isAdmin || authStore.isHR) {
    router.replace('/admin')
  } else {
    router.replace('/employee')
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.profile-header h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary, #0f172a);
  margin: 0;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}
@media (min-width: 960px) {
  .profile-grid { grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); }
}

.card {
  background: white;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

/* 基本信息 */
.avatar-upload {
  flex-shrink: 0;
}
.avatar-wrap {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}
.avatar-wrap.uploading {
  cursor: not-allowed;
  opacity: 0.7;
}
.avatar-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
  gap: 4px;
}
.avatar-wrap:hover .avatar-mask {
  opacity: 1;
}
.avatar-wrap.uploading .avatar-mask {
  opacity: 1;
}
.is-loading {
  animation: rotating 1s linear infinite;
}
@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.info-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border, #e2e8f0);
}
.avatar-lg {
  background: var(--primary, #0f172a) !important;
  color: white !important;
  font-size: 26px;
  font-weight: 600;
}
.hero-text h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary, #0f172a);
  margin: 0 0 4px;
}
.hero-text p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px;
}
.hero-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.avatar-tip {
  font-size: 11px;
  color: #94a3b8;
  margin: 0;
}

.info-list {
  list-style: none;
  padding: 20px 0 4px;
  margin: 0;
  display: grid;
  gap: 12px;
}
.info-list li {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 14px;
}
.info-list .label {
  color: #94a3b8;
  flex-shrink: 0;
}
.info-list .value {
  color: #334155;
  font-weight: 500;
  text-align: right;
  word-break: break-all;
}
.info-hint {
  margin-top: 16px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 12px;
  color: #64748b;
}

/* 修改密码 */
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary, #0f172a);
}
.card-title h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}
.card-sub {
  font-size: 12px;
  color: #94a3b8;
  margin: 4px 0 20px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
