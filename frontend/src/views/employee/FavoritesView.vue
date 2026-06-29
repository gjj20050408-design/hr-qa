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
import { ref, onMounted } from 'vue'
import { StarFilled } from '@element-plus/icons-vue'
import type { QARecord } from '@/types'
import { useChatStore } from '@/stores/chat'
import { getQARecords } from '@/api/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()
const favorites = ref<QARecord[]>([])

async function loadFavorites() {
  try {
    // 加载所有收藏的问答记录
    const res = await getQARecords({ page_size: 100 })
    favorites.value = (res.data?.items || []).filter((r: any) => r.is_favorite)
  } catch {}
}

onMounted(loadFavorites)

function viewDetail(item: QARecord) {
  ElMessage.info('详情查看（功能待接入）')
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
</style>
