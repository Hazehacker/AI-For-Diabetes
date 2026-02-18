<template>
  <view class="match-page" :class="{ 'child-mode-page': isChildMode }">
    <!-- 儿童模式自定义导航栏 -->
    <view v-if="isChildMode" class="child-nav-bar">
      <image class="child-nav-back" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="child-nav-title">食物拼拼乐</text>
      <view class="child-nav-placeholder"></view>
    </view>
    
    <view class="top-bar">
      <view class="pill">
        <text class="pill-label">进度</text>
        <text class="pill-value">{{ step }}/{{ totalSteps }}</text>
      </view>
      <view class="pill">
        <text class="pill-label">得分</text>
        <text class="pill-value">{{ score }}</text>
      </view>
    </view>

    <view class="board">
      <text class="title">把食物送进正确的篮子</text>
      <text class="subtitle">拖动卡片到「低/中/高碳水」篮子</text>

      <view class="question">
        <view class="food-card">
          <text class="food-emoji">{{ current.emoji }}</text>
          <text class="food-name">{{ current.name }}</text>
        </view>
      </view>

      <movable-area
        id="drag-area"
        class="area"
        @touchend="onDrop"
        @touchcancel="onDrop"
      >
        <movable-view
          class="movable"
          direction="all"
          :x="pos.x"
          :y="pos.y"
          :disabled="locked"
          @change="onMove"
        >
          <view class="drag-card">
            <text class="drag-emoji">{{ current.emoji }}</text>
            <!-- <text class="drag-text">拖我进篮子！</text> -->
          </view>
        </movable-view>

        <view class="bins">
          <view id="bin-low" class="bin low" @tap="choose('low')">
            <text class="bin-title">低碳水</text>
            <text class="bin-sub">蔬菜/蛋白类</text>
          </view>
          <view id="bin-mid" class="bin mid" @tap="choose('mid')">
            <text class="bin-title">中碳水</text>
            <text class="bin-sub">水果/奶类</text>
          </view>
          <view id="bin-high" class="bin high" @tap="choose('high')">
            <text class="bin-title">高碳水</text>
            <text class="bin-sub">主食/甜食</text>
          </view>
        </view>
      </movable-area>

      <view class="feedback" v-if="feedback.text" :class="feedback.type">
        <text class="fb-text">{{ feedback.text }}</text>
      </view>
    </view>

    <view class="bottom-actions">
      <view class="btn secondary" @tap="goBack">返回</view>
      <view class="btn primary" @tap="restart">重新开始</view>
    </view>

    <view v-if="ended" class="overlay">
      <view class="result-card">
        <text class="result-title">本局结算</text>
        <view class="result-row">
          <text class="k">正确率</text>
          <text class="v">{{ Math.round(accuracy * 100) }}%</text>
        </view>
        <view class="result-row">
          <text class="k">得分</text>
          <text class="v">{{ score }}</text>
        </view>
        <view class="result-row">
          <text class="k">奖励积分</text>
          <text class="v highlight">+{{ reward.reward_points || 0 }}</text>
        </view>
        <text class="result-hint">{{ reward.hint || endHint }}</text>
        <view class="result-actions">
          <view class="btn secondary" @tap="goBack">返回列表</view>
          <view class="btn primary" @tap="restart">再来一局</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, getCurrentInstance, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useGamesStore } from '@/store/games'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const gamesStore = useGamesStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')
const instance = getCurrentInstance()

const totalSteps = 10
const step = ref(1)
const score = ref(0)
const correct = ref(0)
const ended = ref(false)
const locked = ref(false)
const endHint = ref('学得真快！记得把“碳水”放在心里～')
const reward = reactive({ reward_points: 0, hint: '', offline: false })

const cfg = ref(null)
const pool = ref([])
const current = reactive({ id: '', name: '', emoji: '', carb: 'mid' })

const accuracy = ref(1)
const sessionId = ref('')

// 拖拽位置（px）
const pos = reactive({ x: 0, y: 0 })
const lastPos = reactive({ x: 0, y: 0 })
const center = reactive({ x: 0, y: 0 })

const bins = reactive({
  low: null,
  mid: null,
  high: null
})
const areaRect = ref(null)

const feedback = reactive({ text: '', type: 'good' })
let fbTimer = null

function showFeedback(text, type = 'good') {
  feedback.text = text
  feedback.type = type
  if (fbTimer) clearTimeout(fbTimer)
  fbTimer = setTimeout(() => {
    feedback.text = ''
  }, 700)
}

function pickOne() {
  const list = pool.value
  const it = list[Math.floor(Math.random() * list.length)]
  current.id = it.id
  current.name = it.name
  current.emoji = it.emoji
  current.carb = it.carb
}

function resetPos() {
  pos.x = center.x
  pos.y = center.y
  lastPos.x = pos.x
  lastPos.y = pos.y
}

function restart() {
  step.value = 1
  score.value = 0
  correct.value = 0
  ended.value = false
  locked.value = false
  reward.reward_points = 0
  reward.hint = ''
  reward.offline = false
  accuracy.value = 1
  sessionId.value = gamesStore.getNewSessionId()
  pickOne()
  resetPos()
}

function onMove(e) {
  if (e?.detail) {
    // 同步拖拽位置到实际坐标，便于后续 resetPos 生效
    pos.x = e.detail.x
    pos.y = e.detail.y
    lastPos.x = e.detail.x
    lastPos.y = e.detail.y
  }
}

function hitBin(key) {
  const rect = bins[key]
  const area = areaRect.value
  if (!rect || !area) return false

  // movable-view 的 x/y 是相对于 movable-area 左上角的，需要先转换到屏幕坐标
  const cardW = 140
  const cardH = 110
  const cx = area.left + lastPos.x + cardW / 2
  const cy = area.top + lastPos.y + cardH / 2

  return (
    cx >= rect.left &&
    cx <= rect.right &&
    cy >= rect.top &&
    cy <= rect.bottom
  )
}

function handleAnswer(ans) {
  if (locked.value || ended.value) return
  locked.value = true

  const ok = ans === current.carb
  if (ok) {
    correct.value += 1
    score.value += 100
    showFeedback('太棒了！✅', 'good')
  } else {
    score.value += 20
    showFeedback(`差一点～正确是「${labelMap[current.carb]}」`, 'bad')
  }

  setTimeout(() => {
    step.value += 1
    if (step.value > totalSteps) {
      finish()
      return
    }
    pickOne()
    resetPos()
    locked.value = false
  }, 650)
}

const labelMap = {
  low: '低碳水',
  mid: '中碳水',
  high: '高碳水'
}

function onDrop(e) {
  if (locked.value || ended.value) return

  // 优先使用触点的屏幕坐标来判断是否落在某个篮子上，
  // 避免受 draggable 区域高度和父容器限制的影响
  const touch = e?.changedTouches?.[0] || e?.touches?.[0]

  let key = null

  if (touch) {
    const x = touch.clientX
    const y = touch.clientY
    key = ['low', 'mid', 'high'].find((k) => {
      const rect = bins[k]
      if (!rect) return false
      return x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom
    })
  }

  // 兼容兜底：如果拿不到触点坐标，退回到原来的“根据卡片中心点”命中逻辑
  if (!key) {
    key = ['low', 'mid', 'high'].find((k) => hitBin(k))
  }

  if (key) {
    handleAnswer(key)
  } else {
    showFeedback('再靠近一点点篮子～', 'info')
    resetPos()
  }
}

function choose(key) {
  handleAnswer(key)
}

async function finish() {
  ended.value = true
  locked.value = true
  accuracy.value = totalSteps > 0 ? correct.value / totalSteps : 1

  const res = await gamesStore.submitResult('food_match', {
    session_id: sessionId.value,
    score: score.value,
    duration: totalSteps * 8,
    accuracy: accuracy.value,
    events: null
  })
  reward.reward_points = res?.reward_points ?? 0
  reward.hint = res?.hint || endHint.value
  reward.offline = !!res?.offline
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.navigateTo({ url: '/pages/interaction/games/index' })
  }
}

async function measureBins() {
  const q = uni.createSelectorQuery().in(instance?.proxy)
  const ids = [
    { key: 'low', id: '#bin-low' },
    { key: 'mid', id: '#bin-mid' },
    { key: 'high', id: '#bin-high' }
  ]
  await new Promise((resolve) => {
    q.select('#drag-area').boundingClientRect((rect) => {
      if (rect) areaRect.value = rect
    })
    ids.forEach((it) => {
      q.select(it.id).boundingClientRect((rect) => {
        if (rect) bins[it.key] = rect
      })
    })
    q.exec(() => resolve())
  })
}

onMounted(async () => {
  gamesStore.initFromCache()
  cfg.value = await gamesStore.fetchConfig('food_match')
  pool.value = cfg.value?.items || gamesStore.getDefaultConfig('food_match').items

  // 计算初始中心位置（大致居中）
  const sys = uni.getSystemInfoSync()
  center.x = Math.max(0, Math.floor(sys.windowWidth / 2 - 70))
  center.y = 150

  sessionId.value = gamesStore.getNewSessionId()
  pickOne()
  await nextTick()
  await measureBins()
  resetPos()
})

onBeforeUnmount(() => {
  if (fbTimer) clearTimeout(fbTimer)
})
</script>

<style scoped>
.match-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.top-bar {
  display: flex;
  gap: 16rpx;
  margin-top: 6rpx;
}

.pill {
  flex: 1;
  background: white;
  border-radius: 20rpx;
  padding: 18rpx 22rpx;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5A874;
}

.pill-label {
  font-size: 24rpx;
  color: #A85835;
}

.pill-value {
  font-size: 34rpx;
  font-weight: 900;
  color: #602F27;
}

.board {
  margin-top: 18rpx;
  background: white;
  border-radius: 28rpx;
  padding: 26rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.title {
  display: block;
  font-size: 32rpx;
  font-weight: 900;
  color: #602F27;
}
.subtitle {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #A85835;
}

.question {
  margin-top: 14rpx;
  display: flex;
  justify-content: center;
}

.food-card {
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  border-radius: 22rpx;
  padding: 18rpx 22rpx;
  display: flex;
  align-items: center;
  gap: 14rpx;
  border: 2rpx solid #E3C7A4;
}

.food-emoji {
  font-size: 56rpx;
}
.food-name {
  font-size: 28rpx;
  font-weight: 900;
  color: #602F27;
}

.area {
  margin-top: 18rpx;
  height: 460rpx;
  width: 100%;
  background: linear-gradient(180deg, #FFFBF0 0%, #FFF8E7 100%);
  border-radius: 22rpx;
  position: relative;
  overflow: hidden;
  border: 2rpx solid #E3C7A4;
}

.movable {
  width: 114rpx;
  height: 180rpx;
}

.drag-card {
  width: 110rpx;
  height: 110rpx;
  border-radius: 22rpx;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874;
}

.drag-emoji {
  font-size: 60rpx;
}
.drag-text {
  margin-top: 8rpx;
  font-size: 12rpx;
  color: #A85835;
  font-weight: 700;
}

.bins {
  margin-top: 18rpx;
  display: flex;
  gap: 14rpx;
}

.bin {
  flex: 1;
  border-radius: 20rpx;
  padding: 16rpx 12rpx;
  text-align: center;
  border: 2rpx solid;
}

.bin-title {
  display: block;
  font-size: 26rpx;
  font-weight: 900;
  color: #602F27;
}
.bin-sub {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #A85835;
}

.bin.low {
  background: #E8F5E9;
  border-color: #A5D6A7;
}
.bin.mid {
  background: #E3F2FD;
  border-color: #90CAF9;
}
.bin.high {
  background: #FFEBEE;
  border-color: #EF9A9A;
}

.feedback {
  margin-top: 14rpx;
  padding: 14rpx 16rpx;
  border-radius: 18rpx;
  text-align: center;
}
.feedback.good {
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  border: 2rpx solid #E3C7A4;
}
.feedback.bad {
  background: #FFEBEE;
  border: 2rpx solid #EF9A9A;
}
.feedback.info {
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  border: 2rpx solid #E3C7A4;
}
.fb-text {
  font-size: 24rpx;
  color: #602F27;
  font-weight: 800;
}

.bottom-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 18rpx;
}

.btn {
  flex: 1;
  text-align: center;
  padding: 22rpx 0;
  border-radius: 44rpx;
  font-weight: 800;
  font-size: 28rpx;
}

.btn.primary {
  background: #F6D387;
  color: #602F27;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874;
}

.btn.primary:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.btn.secondary {
  background: white;
  color: #602F27;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5A874;
}

.btn.secondary:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.overlay {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
}

.result-card {
  width: 100%;
  background: white;
  border-radius: 28rpx;
  padding: 28rpx;
  border: 3rpx solid #E3C7A4;
}

.result-title {
  display: block;
  font-size: 34rpx;
  font-weight: 900;
  color: #602F27;
  margin-bottom: 16rpx;
}

.result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
}

.k {
  font-size: 26rpx;
  color: #A85835;
}
.v {
  font-size: 28rpx;
  font-weight: 900;
  color: #602F27;
}
.v.highlight {
  color: #CB8E54;
}

.result-hint {
  display: block;
  margin-top: 14rpx;
  font-size: 24rpx;
  color: #A85835;
  line-height: 1.6;
}

.result-actions {
  margin-top: 18rpx;
  display: flex;
  gap: 16rpx;
}

/* 儿童模式导航栏样式 */
.child-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
  margin: -20rpx -20rpx 20rpx -20rpx;
}

.child-nav-back {
  width: 64rpx;
  height: 64rpx;
  display: block;
  padding: 10rpx;
  cursor: pointer;
  z-index: 100;
  position: relative;
}

.child-nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.child-nav-placeholder {
  width: 64rpx;
}
</style>


