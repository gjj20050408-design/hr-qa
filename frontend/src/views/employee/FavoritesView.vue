<template>
  <div class="favorites-layout">
    <div class="favorites-header">
      <h2>我的收藏</h2>
      <p>共 <strong>{{ favorites.length }}</strong> 条收藏</p>
    </div>

    <div class="favorites-list">
      <div
        v-for="item in favorites"
        :key="item.record_id"
        class="favorite-card"
        @click="viewDetail(item)"
      >
        <el-icon class="fav-star" color="#f59e0b" :size="20"><StarFilled /></el-icon>
        <div class="fav-content">
          <h3>{{ item.question }}</h3>
          <p class="fav-meta">收藏于 {{ item.created_at }}</p>
        </div>
        <el-button
          link
          type="danger"
          size="small"
          @click.stop="removeFav(item)"
        >
          取消收藏
        </el-button>
      </div>

      <el-empty v-if="!favorites.length" description="暂无收藏" :image-size="80" />
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="收藏详情"
      width="640px"
      append-to-body
    >
      <div v-if="detail" class="detail-body">
        <div class="detail-block">
          <div class="detail-label">问题</div>
          <div class="detail-question">{{ detail.question }}</div>
        </div>
        <div class="detail-block">
          <div class="detail-label">回答</div>
          <div class="detail-answer" v-html="formatAnswer(detail.answer)"></div>
        </div>
        <div class="detail-block" v-if="detail.reference_docs?.length">
          <div class="detail-label">参考来源</div>
          <ul class="detail-refs">
            <li v-for="(ref, i) in detail.reference_docs" :key="i">
              {{ ref.title }}<span v-if="ref.section"> · {{ ref.section }}</span>
            </li>
          </ul>
        </div>
        <div class="detail-meta">收藏于 {{ detail.created_at }}</div>
      </div>
      <template #footer>
        <el-button v-if="detail" type="danger" plain @click="removeFromDetail">取消收藏</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { StarFilled } from '@element-plus/icons-vue'
import type { QARecord } from '@/types'
import { useChatStore } from '@/stores/chat'
import { getQARecords } from '@/api/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()
const favorites = ref<QARecord[]>([])
const detailVisible = ref(false)
const detail = ref<QARecord | null>(null)

async function loadFavorites() {
  try {
    // 加载所有收藏的问答记录
    const res = await getQARecords({ page_size: 100 })
    favorites.value = (res.data?.data?.items || []).filter((r: any) => r.is_favorite)
  } catch {}
}

onMounted(loadFavorites)

// 将答案中的换行转为 <br>，并转义 HTML 防止注入
function formatAnswer(text: string): string {
  const escaped = (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped.replace(/\n/g, '<br>')
}

function viewDetail(item: QARecord) {
  detail.value = item
  detailVisible.value = true
}

async function removeFromDetail() {
  if (!detail.value) return
  await removeFav(detail.value)
  detailVisible.value = false
}

async function removeFav(item: QARecord) {
  try {
    await chatStore.toggleFavorite(item.record_id, false)
    favorites.value = favorites.value.filter(f => f.record_id !== item.record_id)
    ElMessage.success('已取消收藏')
  } catch {
    // ignore
  }
}
</script>

<style scoped>
.favorites-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.favorites-header {
  padding: 24px;
  background: white;
  border-bottom: 1px solid var(--border);
}
.favorites-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
.favorites-header p {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 4px;
}

.favorites-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.favorite-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.favorite-card:hover {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.fav-star {
  flex-shrink: 0;
}

.fav-content {
  flex: 1;
}
.fav-content h3 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
.fav-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

/* 详情对话框 */
.detail-block {
  margin-bottom: 18px;
}
.detail-label {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 6px;
}
.detail-question {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.6;
}
.detail-answer {
  font-size: 14px;
  color: #334155;
  line-height: 1.7;
  white-space: normal;
}
.detail-refs {
  margin: 0;
  padding-left: 18px;
}
.detail-refs li {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}
.detail-meta {
  font-size: 12px;
  color: #94a3b8;
  text-align: right;
}
</style>
