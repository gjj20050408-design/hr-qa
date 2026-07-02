<template>
  <div class="slider-captcha">
    <!-- 拼图画布区 -->
    <div class="captcha-canvas" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }">
      <canvas ref="bgCanvas" :width="canvasWidth" :height="canvasHeight" class="bg-canvas" />
      <canvas
        ref="pieceCanvas"
        :width="pieceSize"
        :height="canvasHeight"
        class="piece-canvas"
        :style="{ transform: `translateX(${pieceLeft}px)` }"
      />
      <!-- 刷新按钮 -->
      <div class="refresh-btn" @click="reset(false)" title="换一张">
        <el-icon><Refresh /></el-icon>
      </div>
      <!-- 结果提示 -->
      <transition name="fade">
        <div v-if="status !== 'idle'" class="result-tip" :class="status">
          {{ status === 'success' ? '验证通过' : '验证失败，请重试' }}
        </div>
      </transition>
    </div>

    <!-- 滑动轨道 -->
    <div class="slider-track" :class="status" ref="trackRef">
      <div class="slider-track-fill" :style="{ width: sliderLeft + trackHandle / 2 + 'px' }" />
      <div class="slider-track-text" v-show="status === 'idle' && sliderLeft === 0">
        向右拖动滑块完成拼图
      </div>
      <div
        class="slider-handle"
        :class="status"
        :style="{ transform: `translateX(${sliderLeft}px)` }"
        @mousedown="onStart"
        @touchstart.passive="onStart"
      >
        <el-icon v-if="status === 'idle'"><DArrowRight /></el-icon>
        <el-icon v-else-if="status === 'success'"><Check /></el-icon>
        <el-icon v-else><Close /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Refresh, DArrowRight, Check, Close } from '@element-plus/icons-vue'

const emit = defineEmits<{ (e: 'success'): void; (e: 'fail'): void }>()

// 画布尺寸
const canvasWidth = 320
const canvasHeight = 160
const pad = 10 // 拼图块画布左/上留白，容纳向外凸起的边
const pieceSize = 56 // 拼图块画布宽度（含留白与凸起）
const trackHandle = 40 // 滑块手柄宽度
const tolerance = 6 // 允许误差（px）

const bgCanvas = ref<HTMLCanvasElement>()
const pieceCanvas = ref<HTMLCanvasElement>()
const trackRef = ref<HTMLDivElement>()

const pieceLeft = ref(0) // 拼图块当前水平位置
const sliderLeft = ref(0) // 滑块手柄位移
const status = ref<'idle' | 'success' | 'fail'>('idle')

let targetX = 0 // 缺口目标 X
let pieceY = 0 // 拼图块 Y
let dragging = false
let startX = 0
let verified = false

// 离屏画布：保存未抠缺口的完整原图，验证通过时用于把缺口填充回去
let cleanCanvas: HTMLCanvasElement | null = null

// 当前拼图形状：主体边长 + 四条边的凸凹方向（1 凸出 / -1 凹入 / 0 平直）
let shape = { size: 30, tabs: { top: 0, right: 0, bottom: 0, left: 0 } as Record<'top' | 'right' | 'bottom' | 'left', number> }

// 随机生成一个拼图形状
function randomShape() {
  const pick = () => [-1, 0, 1][Math.floor(Math.random() * 3)]
  const tabs = { top: pick(), right: pick(), bottom: pick(), left: pick() }
  // 至少保留一条凸凹边，避免生成纯方块
  if (Object.values(tabs).every((v) => v === 0)) {
    tabs[(['top', 'right', 'bottom', 'left'] as const)[Math.floor(Math.random() * 4)]] = Math.random() < 0.5 ? 1 : -1
  }
  shape = { size: 28 + Math.floor(Math.random() * 8), tabs }
}

// 生成随机背景图（渐变 + 装饰形状，无需外部资源）
function drawBackground(ctx: CanvasRenderingContext2D) {
  const hue = Math.floor(Math.random() * 360)
  const g = ctx.createLinearGradient(0, 0, canvasWidth, canvasHeight)
  g.addColorStop(0, `hsl(${hue}, 55%, 55%)`)
  g.addColorStop(1, `hsl(${(hue + 60) % 360}, 55%, 42%)`)
  ctx.fillStyle = g
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  // 随机装饰圆，增加辨识难度
  for (let i = 0; i < 6; i++) {
    ctx.beginPath()
    const r = 20 + Math.random() * 40
    ctx.arc(Math.random() * canvasWidth, Math.random() * canvasHeight, r, 0, Math.PI * 2)
    ctx.fillStyle = `hsla(${Math.random() * 360}, 60%, 60%, 0.25)`
    ctx.fill()
  }
}

// 绘制拼图缺口路径（形状由 shape 决定，四条边可凸/凹/平）
function drawPuzzlePath(ctx: CanvasRenderingContext2D, x: number, y: number) {
  const s = shape.size // 主体边长
  const bump = 8 // 凸起半径
  const t = shape.tabs
  ctx.beginPath()
  ctx.moveTo(x, y)
  // 上边（凸起圆心在外侧上方 dir=-1 逆时针为凸出画面上方）
  drawEdge(ctx, x, y, x + s, y, t.top)
  // 右边
  drawEdge(ctx, x + s, y, x + s, y + s, t.right)
  // 下边
  drawEdge(ctx, x + s, y + s, x, y + s, t.bottom)
  // 左边
  drawEdge(ctx, x, y + s, x, y, t.left)
  ctx.closePath()

  function drawEdge(c: CanvasRenderingContext2D, x1: number, y1: number, x2: number, y2: number, dir: number) {
    if (dir === 0) {
      c.lineTo(x2, y2)
      return
    }
    const mx = (x1 + x2) / 2
    const my = (y1 + y2) / 2
    // 边方向的单位向量与其法向量
    const dx = x2 - x1
    const dy = y2 - y1
    const len = Math.hypot(dx, dy)
    const ux = dx / len
    const uy = dy / len
    // 法向量（指向多边形外侧，配合 dir 决定凸出/凹入）
    const nx = -uy * dir
    const ny = ux * dir
    // 圆心在中点沿法向偏移，画半圆形成凸/凹的“耳朵”
    const cx = mx + nx * bump * 0.6
    const cy = my + ny * bump * 0.6
    c.lineTo(mx - ux * bump, my - uy * bump)
    const a0 = Math.atan2((my - uy * bump) - cy, (mx - ux * bump) - cx)
    const a1 = Math.atan2((my + uy * bump) - cy, (mx + ux * bump) - cx)
    c.arc(cx, cy, bump, a0, a1, dir < 0)
    c.lineTo(x2, y2)
  }
}

// 初始化 / 重置
function reset(silent = true) {
  if (!bgCanvas.value || !pieceCanvas.value) return
  const bgCtx = bgCanvas.value.getContext('2d')!
  const pieceCtx = pieceCanvas.value.getContext('2d')!

  status.value = 'idle'
  verified = false
  sliderLeft.value = 0
  pieceLeft.value = 0

  // 每次随机一个拼图形状
  randomShape()

  // 随机缺口位置（预留滑动空间与画布边距，保证形状不被裁切且可对齐）
  targetX = Math.floor(Math.random() * 190) + 70 // [70, 260]
  pieceY = Math.floor(Math.random() * (canvasHeight - 60)) + 15

  // 背景
  drawBackground(bgCtx)

  // 保存未抠缺口的完整原图（离屏），供拼图块取像素 & 验证通过后填充
  if (!cleanCanvas) {
    cleanCanvas = document.createElement('canvas')
    cleanCanvas.width = canvasWidth
    cleanCanvas.height = canvasHeight
  }
  const cleanCtx = cleanCanvas.getContext('2d')!
  cleanCtx.clearRect(0, 0, canvasWidth, canvasHeight)
  cleanCtx.drawImage(bgCanvas.value, 0, 0)

  // 在背景上抠出缺口（描边 + 变暗）
  drawPuzzlePath(bgCtx, targetX, pieceY)
  bgCtx.save()
  bgCtx.clip()
  bgCtx.fillStyle = 'rgba(0, 0, 0, 0.45)'
  bgCtx.fillRect(0, 0, canvasWidth, canvasHeight)
  bgCtx.restore()
  drawPuzzlePath(bgCtx, targetX, pieceY)
  bgCtx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
  bgCtx.lineWidth = 1.5
  bgCtx.stroke()

  // 拼图块：形状画在留白位置 pad，从干净原图对应偏移取像素
  pieceCtx.clearRect(0, 0, pieceSize, canvasHeight)
  drawPuzzlePath(pieceCtx, pad, pieceY)
  pieceCtx.save()
  pieceCtx.clip()
  pieceCtx.drawImage(cleanCanvas, targetX - pad, 0, pieceSize, canvasHeight, 0, 0, pieceSize, canvasHeight)
  pieceCtx.restore()
  drawPuzzlePath(pieceCtx, pad, pieceY)
  pieceCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)'
  pieceCtx.lineWidth = 1.5
  pieceCtx.stroke()

  if (!silent) emit('fail') // 通知父级重置（如清除已通过状态）
}

// 拖动逻辑
function onStart(e: MouseEvent | TouchEvent) {
  if (verified) return
  dragging = true
  startX = getClientX(e)
  status.value = 'idle'
  window.addEventListener('mousemove', onMove)
  window.addEventListener('touchmove', onMove, { passive: false })
  window.addEventListener('mouseup', onEnd)
  window.addEventListener('touchend', onEnd)
}

function onMove(e: MouseEvent | TouchEvent) {
  if (!dragging) return
  if (e instanceof TouchEvent) e.preventDefault()
  const maxSlide = canvasWidth - trackHandle
  let delta = getClientX(e) - startX
  delta = Math.max(0, Math.min(delta, maxSlide))
  sliderLeft.value = delta
  // 拼图块随滑块移动（比例映射到画布宽度）
  pieceLeft.value = (delta / maxSlide) * (canvasWidth - pieceSize)
}

function onEnd() {
  if (!dragging) return
  dragging = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('touchmove', onMove)
  window.removeEventListener('mouseup', onEnd)
  window.removeEventListener('touchend', onEnd)

  // 拼图块形状绘制在留白 pad 处，故对齐条件为 pieceLeft + pad ≈ targetX
  if (Math.abs(pieceLeft.value + pad - targetX) <= tolerance) {
    status.value = 'success'
    verified = true
    fillComplete()
    emit('success')
  } else {
    status.value = 'fail'
    emit('fail')
    setTimeout(() => reset(true), 800)
  }
}

// 验证通过：把拼图块吸附到精确位置，并将缺口填充回完整原图
function fillComplete() {
  if (!bgCanvas.value || !cleanCanvas) return
  // 吸附：拼图块对齐到缺口，滑块同步到对应位置
  const maxSlide = canvasWidth - trackHandle
  pieceLeft.value = targetX - pad
  sliderLeft.value = ((targetX - pad) / (canvasWidth - pieceSize)) * maxSlide
  // 用干净原图覆盖背景，缺口消失，画面恢复完整
  const bgCtx = bgCanvas.value.getContext('2d')!
  bgCtx.clearRect(0, 0, canvasWidth, canvasHeight)
  bgCtx.drawImage(cleanCanvas, 0, 0)
}

function getClientX(e: MouseEvent | TouchEvent): number {
  return e instanceof TouchEvent ? e.touches[0]?.clientX ?? e.changedTouches[0].clientX : e.clientX
}

// 供父组件调用：重置验证状态
defineExpose({ reset: () => reset(true) })

onMounted(() => reset(true))
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('touchmove', onMove)
  window.removeEventListener('mouseup', onEnd)
  window.removeEventListener('touchend', onEnd)
})
</script>

<style scoped>
.slider-captcha {
  user-select: none;
}

.captcha-canvas {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 auto;
}
.bg-canvas {
  display: block;
  border-radius: 8px;
}
.piece-canvas {
  position: absolute;
  top: 0;
  left: 0;
  will-change: transform;
}

.refresh-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.35);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}
.refresh-btn:hover {
  background: rgba(0, 0, 0, 0.55);
}

.result-tip {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  padding: 4px 0;
  text-align: center;
  font-size: 13px;
  color: white;
}
.result-tip.success {
  background: rgba(16, 185, 129, 0.85);
}
.result-tip.fail {
  background: rgba(239, 68, 68, 0.85);
}

.slider-track {
  position: relative;
  height: 40px;
  margin-top: 14px;
  background: #f1f5f9;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
}
.slider-track.success {
  background: #ecfdf5;
  border-color: #10b981;
}
.slider-track.fail {
  background: #fef2f2;
  border-color: #ef4444;
}

.slider-track-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 8px 0 0 8px;
}
.slider-track.success .slider-track-fill {
  background: rgba(16, 185, 129, 0.2);
}

.slider-track-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #94a3b8;
  pointer-events: none;
}

.slider-handle {
  position: absolute;
  top: -1px;
  left: 0;
  width: 40px;
  height: 40px;
  background: white;
  border: 1px solid var(--border, #e2e8f0);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  color: var(--accent, #3b82f6);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  will-change: transform;
}
.slider-handle:active {
  cursor: grabbing;
}
.slider-handle.success {
  color: white;
  background: #10b981;
  border-color: #10b981;
}
.slider-handle.fail {
  color: white;
  background: #ef4444;
  border-color: #ef4444;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
