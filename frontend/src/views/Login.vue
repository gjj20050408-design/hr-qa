<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="brand-panel">
        <div class="brand-bg-1"></div>
        <div class="brand-bg-2"></div>
        <div class="brand-content">
          <div class="brand-icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <h1>HR制度智能问答系统</h1>
          <p>7×24小时自助HR制度查询与智能问答服务，秒级获取准确答案</p>
        </div>
        <div class="brand-features">
          <div class="feature-item">
            <el-icon color="#10b981"><Check /></el-icon>
            <span>基于AI的智能RAG问答引擎</span>
          </div>
          <div class="feature-item">
            <el-icon color="#10b981"><Check /></el-icon>
            <span>全文搜索 + FAQ快速匹配</span>
          </div>
          <div class="feature-item">
            <el-icon color="#10b981"><Check /></el-icon>
            <span>制度文档分类管理与权限控制</span>
          </div>
        </div>
      </div>

      <!-- 右侧表单 -->
      <div class="form-panel">
        <!-- 移动端logo -->
        <div class="mobile-logo">
          <div class="brand-icon-sm">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <h1>HR制度智能问答系统</h1>
        </div>

        <div class="form-header">
          <h2>欢迎回来</h2>
          <p>请登录您的账号</p>
        </div>

        <!-- Tab切换 -->
        <div class="tab-switch">
          <span :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">账号登录</span>
          <span :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">员工注册</span>
        </div>

        <!-- 登录表单 -->
        <el-form
          v-if="activeTab === 'login'"
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="account">
            <el-input
              v-model="loginForm.account"
              placeholder="工号 / 邮箱"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <div class="form-extra">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>

        <!-- 注册表单 -->
        <el-form
          v-else
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
        >
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item prop="employee_id">
                <el-input v-model="registerForm.employee_id" placeholder="工号（字母数字4-20位）" size="large" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="name">
                <el-input v-model="registerForm.name" placeholder="真实姓名" size="large" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item prop="department_id">
            <el-select v-model="registerForm.department_id" placeholder="请选择部门" size="large" class="w-full">
              <el-option label="技术部" value="dept-002" />
              <el-option label="产品部" value="dept-003" />
              <el-option label="人力资源部" value="dept-004" />
              <el-option label="财务部" value="dept-005" />
            </el-select>
          </el-form-item>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item prop="email">
                <el-input v-model="registerForm.email" placeholder="邮箱（选填）" size="large" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="phone">
                <el-input v-model="registerForm.phone" placeholder="手机号（选填）" size="large" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="8位以上，含大小写字母+数字"
              size="large"
              show-password
            />
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form>


      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Document, Check } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref<'login' | 'register'>('login')
const loading = ref(false)
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

// 登录表单
const loginForm = reactive({
  account: '',
  password: '',
  remember: false,
})

const loginRules: FormRules = {
  account: [{ required: true, message: '请输入工号或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 注册表单
const registerForm = reactive({
  employee_id: '',
  name: '',
  department_id: '',
  email: '',
  phone: '',
  password: '',
})

const registerRules: FormRules = {
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]{4,20}$/, message: '工号为4-20位字母数字', trigger: 'blur' },
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department_id: [{ required: true, message: '请选择部门', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
    { pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, message: '含大小写字母+数字', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login({
        account: loginForm.account,
        password: loginForm.password,
      })
      ElMessage.success('登录成功')
      router.push(authStore.isAdmin ? '/admin' : '/employee')
    } catch {
      // error handled by interceptor
    } finally {
      loading.value = false
    }
  })
}

async function handleRegister() {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.register({
        employee_id: registerForm.employee_id,
        name: registerForm.name,
        department_id: registerForm.department_id,
        email: registerForm.email || undefined,
        phone: registerForm.phone || undefined,
        password: registerForm.password,
      })
      ElMessage.success('注册成功，请登录')
      activeTab.value = 'login'
    } catch {
      // error handled by interceptor
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
}

.login-card {
  width: 100%;
  max-width: 1024px;
  display: flex;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 左侧品牌区 */
.brand-panel {
  display: none;
  width: 50%;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  padding: 48px;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

@media (min-width: 1024px) {
  .brand-panel { display: flex; }
}

.brand-bg-1 {
  position: absolute;
  top: 0;
  right: 0;
  width: 256px;
  height: 256px;
  background: rgba(3, 105, 161, 0.2);
  border-radius: 50%;
  transform: translate(50%, -50%);
}
.brand-bg-2 {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 384px;
  height: 384px;
  background: rgba(3, 105, 161, 0.1);
  border-radius: 50%;
  transform: translate(-50%, 50%);
}

.brand-content {
  position: relative;
  z-index: 1;
}
.brand-icon {
  width: 48px;
  height: 48px;
  background: var(--accent);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 32px;
}
.brand-content h1 {
  font-size: 30px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
}
.brand-content p {
  color: #93c5fd;
  line-height: 1.6;
}

.brand-features {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #93c5fd;
  font-size: 14px;
}

/* 右侧表单 */
.form-panel {
  width: 100%;
  background: white;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
@media (min-width: 1024px) {
  .form-panel { width: 50%; padding: 48px; }
}

.mobile-logo {
  text-align: center;
  margin-bottom: 32px;
}
.mobile-logo .brand-icon-sm {
  width: 40px;
  height: 40px;
  background: var(--accent);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 12px;
}
.mobile-logo h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}
@media (min-width: 1024px) {
  .mobile-logo { display: none; }
}

.form-header {
  margin-bottom: 32px;
}
.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}
.form-header p {
  color: #64748b;
  margin-top: 4px;
}

.tab-switch {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}
.tab-switch span {
  padding-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.15s;
}
.tab-switch span.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.tab-switch span:hover:not(.active) {
  color: #475569;
}

.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.forgot-link {
  font-size: 14px;
  color: var(--accent);
}
.forgot-link:hover {
  color: var(--accent-hover);
}

.submit-btn {
  width: 100%;
}

.footer-text {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 32px;
}

.w-full { width: 100%; }
</style>
