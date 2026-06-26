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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { StarFilled } from '@element-plus/icons-vue'
import type { QARecord } from '@/types'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()

// Mock收藏数据
const favorites = ref<QARecord[]>([
  {
    record_id: 'rec-001',
    user_id: '',
    session_id: '',
    question: '加班费如何计算？',
    answer: '工作日加班1.5倍，休息日2倍，法定节假日3倍工资。',
    answer_type: 'faq',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 85,
    is_favorite: true,
    created_at: '昨天 15:30',
  },
  {
    record_id: 'rec-002',
    user_id: '',
    session_id: '',
    question: '年假如果今年没休完可以延到明年吗？',
    answer: '当年未休完的年假可延期至次年3月31日，过期作废。',
    answer_type: 'rule',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 120,
    is_favorite: true,
    created_at: '今天 10:35',
  },
  {
    record_id: 'rec-003',
    user_id: '',
    session_id: '',
    question: '婚假需要什么材料？',
    answer: '需提供结婚证复印件，提前1个月申请。',
    answer_type: 'faq',
    confidence: 0,
    reference_docs: [],
    response_time_ms: 95,
    is_favorite: true,
    created_at: '6月20日',
  },
])

function viewDetail(item: QARecord) {
  ElMessage.info('详情查看（功能待接入）')
}

async function removeFav(item: QARecord) {
  try {
    await chatStore.toggleFavorite(item.record_id)
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
</style>
