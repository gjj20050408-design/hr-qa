<template>
  <div class="mermaid-chart">
    <div v-if="error" class="mermaid-fallback">
      <p class="mermaid-fallback-tip">流程图渲染失败，已显示源码：</p>
      <pre>{{ code }}</pre>
    </div>
    <div v-else class="mermaid-svg-host" v-html="svg"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()

const svg = ref('')
const error = ref(false)

let initialized = false
let renderSeq = 0

function ensureInit() {
  if (initialized) return
  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'default' })
  initialized = true
}

async function render() {
  const raw = (props.code || '').trim()
  if (!raw) {
    svg.value = ''
    error.value = false
    return
  }
  ensureInit()
  const seq = ++renderSeq
  try {
    // 每次用唯一 id，避免 mermaid 内部缓存冲突
    const { svg: out } = await mermaid.render(`mermaid-${Date.now()}-${seq}`, raw)
    if (seq === renderSeq) {
      svg.value = out
      error.value = false
    }
  } catch (e) {
    if (seq === renderSeq) {
      error.value = true
      svg.value = ''
    }
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<style scoped>
.mermaid-chart {
  width: 100%;
  overflow-x: auto;
}
.mermaid-svg-host {
  display: flex;
  justify-content: center;
}
.mermaid-svg-host :deep(svg) {
  max-width: 100%;
  height: auto;
}
.mermaid-fallback {
  background: var(--surface-muted, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  padding: 12px;
}
.mermaid-fallback-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}
.mermaid-fallback pre {
  font-size: 12px;
  color: #475569;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>
