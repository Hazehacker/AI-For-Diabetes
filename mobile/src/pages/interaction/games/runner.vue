<template>
  <view class="runner-page" :class="{ 'child-mode-page': isChildMode }">
    <!-- 儿童模式自定义导航栏 -->
    <view v-if="isChildMode" class="child-nav-bar">
      <image class="child-nav-back" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="child-nav-title">糖值守护跑酷</text>
      <view class="child-nav-placeholder"></view>
    </view>
    
    <view class="top-bar">
      <view class="pill">
        <text class="pill-label">得分</text>
        <text class="pill-value">{{ score }}</text>
      </view>
      <view class="pill">
        <text class="pill-label">时间</text>
        <text class="pill-value">{{ timeLeft }}s</text>
      </view>
    </view>

    <view class="gauge-wrap">
      <image class="gauge-mascot" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
      <view class="gauge-info">
        <text class="gauge-title">糖值稳定条</text>
        <view class="gauge">
          <view class="gauge-safe"></view>
          <view class="gauge-fill" :style="{ width: gauge + '%' }"></view>
        </view>
        <text class="gauge-tip">{{ gaugeTip }}</text>
      </view>
    </view>

    <view class="game-area" @touchstart.stop.prevent="onTap">
      <view class="sky-hint" v-if="!running && !ended">
        <text class="hint-title">点击开始</text>
        <text class="hint-sub">跳起来躲开陷阱，收集健康食物！</text>
      </view>

      <view class="countdown" v-if="countdown > 0">{{ countdown }}</view>

      <view class="ground"></view>

      <view class="player" :style="{ transform: `translateY(-${playerY}px)` }">
        <image class="player-img" src="/static/ch/ch_play_avatar.png" mode="aspectFit"></image>
      </view>

      <view
        v-for="it in items"
        :key="it.id"
        class="item"
        :class="it.kind"
        :style="{ transform: `translate(${it.x}px, -${it.y}px)` }"
      >
        <text class="item-emoji">{{ it.emoji }}</text>
      </view>

      <view class="toast" v-if="toast.text" :class="toast.type">
        <text class="toast-text">{{ toast.text }}</text>
      </view>
    </view>

    <view class="bottom-actions">
      <view class="btn secondary" @tap="goBack">返回</view>
      <view class="btn primary" @tap="startOrRestart">{{ running ? '重新开始' : '开始挑战' }}</view>
    </view>

    <view v-if="ended" class="overlay">
      <view class="result-card">
        <text class="result-title">本局结算</text>
        <view class="result-row">
          <text class="k">得分</text>
          <text class="v">{{ score }}</text>
        </view>
        <view class="result-row">
          <text class="k">稳定度</text>
          <text class="v">{{ Math.round(stability * 100) }}%</text>
        </view>
        <view class="result-row">
          <text class="k">奖励积分</text>
          <text class="v highlight">+{{ reward.reward_points || 0 }}</text>
        </view>
        <text class="result-hint">{{ reward.hint || endHint }}</text>
        <view class="result-actions">
          <view class="btn secondary" @tap="goBack">返回列表</view>
          <view class="btn primary" @tap="startOrRestart">再来一局</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useGamesStore } from '@/store/games'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const gamesStore = useGamesStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')

// 基础状态
const running = ref(false)
const ended = ref(false)
const countdown = ref(0)
const timeLeft = ref(90)
const score = ref(0)
const gauge = ref(50) // 0-100，越靠近50越稳定
const stability = ref(1)
const endHint = ref('做得不错！选择更健康的食物，糖值更稳～')
const reward = reactive({ reward_points: 0, hint: '', offline: false })

// 玩家物理
const playerY = ref(0)
const vy = ref(0)
const onGround = ref(true)
const jumpCount = ref(0) // 支持二段跳：0/1/2

// 道具
const items = ref([])
const toast = reactive({ text: '', type: 'good' })
let toastTimer = null

// 运行时
let loopTimer = null
let spawnTimer = null
let secTimer = null
let width = 360
let height = 520
let sessionId = ''
let stableAccumulator = 0
let stableTicks = 0

const cfg = ref(null)

const gaugeTip = computed(() => {
  if (gauge.value < 30) return '有点偏低啦，注意补充能量～'
  if (gauge.value > 70) return '有点偏高啦，试试更健康的选择～'
  return '很棒！保持在安全区～'
})

const showToast = (text, type = 'good') => {
  toast.text = text
  toast.type = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.text = ''
  }, 800)
}

function resetGame() {
  running.value = false
  ended.value = false
  countdown.value = 0
  timeLeft.value = 90
  score.value = 0
  gauge.value = 50
  playerY.value = 0
  vy.value = 0
  onGround.value = true
  jumpCount.value = 0
  items.value = []
  reward.reward_points = 0
  reward.hint = ''
  reward.offline = false
  sessionId = gamesStore.getNewSessionId()
  stableAccumulator = 0
  stableTicks = 0
  stability.value = 1
}

function stopTimers() {
  if (loopTimer) clearInterval(loopTimer)
  if (spawnTimer) clearInterval(spawnTimer)
  if (secTimer) clearInterval(secTimer)
  loopTimer = null
  spawnTimer = null
  secTimer = null
}

function endGame(reasonHint) {
  if (ended.value) return
  running.value = false
  ended.value = true
  stopTimers()

  endHint.value = reasonHint || endHint.value
  stability.value = stableTicks > 0 ? stableAccumulator / stableTicks : 1

  const totalCollected = Math.max(1, itemsCollected.good + itemsCollected.bad)
  const accuracy = itemsCollected.good / totalCollected

  gamesStore
    .submitResult('runner', {
      session_id: sessionId,
      score: score.value,
      duration: 90 - timeLeft.value,
      accuracy,
      events: null
    })
    .then((res) => {
      reward.reward_points = res?.reward_points ?? 0
      reward.hint = res?.hint || endHint.value
      reward.offline = !!res?.offline
    })
    .catch(() => {})
}

const itemsCollected = reactive({ good: 0, bad: 0 })

function spawnItem() {
  const foods = cfg.value?.foods || []
  if (foods.length === 0) return

  // 降低陷阱出现概率
  const pool = foods.filter((f) => (f.type === 'trap' ? Math.random() < 0.25 : true))
  const pick = pool[Math.floor(Math.random() * pool.length)] || foods[0]

  const isFlying = pick.type !== 'trap' && Math.random() < 0.25
  const item = {
    id: `${Date.now()}_${Math.random()}`,
    kind: pick.type,
    emoji: pick.emoji,
    score: pick.score,
    delta: pick.delta,
    x: width + 40,
    y: isFlying ? 140 : 40,
    w: 42,
    h: 42
  }
  items.value.push(item)
}

function collide(a, b) {
  return (
    a.x < b.x + b.w &&
    a.x + a.w > b.x &&
    a.y < b.y + b.h &&
    a.y + a.h > b.y
  )
}

function gameLoop() {
  // 玩家物理（跳跃）
  // 调整重力与跳跃参数：减小重力，让滞空更久，便于躲避低空道具
  const gravity = 0.6
  if (!onGround.value) {
    vy.value -= gravity
    playerY.value += vy.value
    if (playerY.value <= 0) {
      playerY.value = 0
      vy.value = 0
      onGround.value = true
      jumpCount.value = 0
    }
  }

  // 道具移动与碰撞
  const speedBase = 5 * (cfg.value?.difficulty?.speed || 1.0)
  const playerBox = {
    x: 42,
    y: 40 + playerY.value,
    w: 46,
    h: 54
  }

  const next = []
  for (const it of items.value) {
    it.x -= speedBase
    if (it.x < -80) continue

    const itBox = { x: it.x, y: it.y, w: it.w, h: it.h }
    if (collide(playerBox, itBox)) {
      if (it.kind === 'trap') {
        showToast('哎呀！踩到陷阱啦', 'bad')
        endGame('踩到陷阱啦～下次记得跳起来躲开哦！')
        return
      }
      score.value += it.score
      gauge.value = Math.max(0, Math.min(100, gauge.value + it.delta))
      if (it.kind === 'good') {
        itemsCollected.good++
        showToast(`+${Math.max(0, it.score)}`, 'good')
      } else if (it.kind === 'bad') {
        itemsCollected.bad++
        showToast(`${it.score}`, 'bad')
      }
      continue
    }

    next.push(it)
  }
  items.value = next

  // 稳定度统计：越靠近 50 越稳定
  const dist = Math.abs(gauge.value - 50)
  const tickStability = Math.max(0, 1 - dist / 50)
  stableAccumulator += tickStability
  stableTicks++

  // 出界判定
  if (gauge.value < 18) {
    endGame('有点偏低啦～下一局多收集健康食物，别忘了关注身体感受！')
  } else if (gauge.value > 82) {
    endGame('有点偏高啦～试试多收集健康食物，躲开高糖捣蛋鬼！')
  }
}

function startTimers() {
  stopTimers()
  loopTimer = setInterval(gameLoop, 16)
  const spawnRate = cfg.value?.difficulty?.spawn_rate || 1.0
  spawnTimer = setInterval(spawnItem, Math.max(520, 900 / spawnRate))
  secTimer = setInterval(() => {
    if (!running.value) return
    timeLeft.value -= 1
    if (timeLeft.value <= 0) {
      endGame('时间到！你已经很棒啦～')
    }
  }, 1000)
}

function startOrRestart() {
  resetGame()
  countdown.value = 3
  itemsCollected.good = 0
  itemsCollected.bad = 0
  ended.value = false

  const cd = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(cd)
      running.value = true
      startTimers()
    }
  }, 900)
}

function onTap() {
  if (!running.value || ended.value) return

  // 一段跳和二段跳使用不同的起跳速度，二段跳高度更低
  if (jumpCount.value === 0) {
    onGround.value = false
    jumpCount.value = 1
    vy.value = 13 // 一段跳高度
  } else if (jumpCount.value === 1) {
    onGround.value = false
    jumpCount.value = 2
    vy.value = 10 // 二段跳高度（可按需继续调小/调大）
    showToast('二段跳！', 'good')
  }
}

function goBack() {
  stopTimers()
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.navigateTo({ url: '/pages/interaction/games/index' })
  }
}

onMounted(async () => {
  const sys = uni.getSystemInfoSync()
  width = sys.windowWidth
  height = sys.windowHeight

  gamesStore.initFromCache()
  cfg.value = await gamesStore.fetchConfig('runner')
  resetGame()
})

onBeforeUnmount(() => {
  stopTimers()
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<style scoped>
.runner-page {
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
  font-weight: 800;
  color: #602F27;
}

.gauge-wrap {
  margin-top: 18rpx;
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.1);
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.gauge-mascot {
  width: 100rpx;
  height: 100rpx;
  flex-shrink: 0;
}

.gauge-info {
  flex: 1;
  min-width: 0;
}

.gauge-title {
  display: block;
  font-size: 26rpx;
  font-weight: 800;
  color: #602F27;
  margin-bottom: 12rpx;
}

.gauge {
  position: relative;
  height: 28rpx;
  border-radius: 999rpx;
  background: #D0D5DD;
  overflow: hidden;
  border: 2rpx solid #B8C0CC;
}

.gauge-safe {
  position: absolute;
  left: 30%;
  width: 40%;
  height: 100%;
  background: rgba(76, 175, 80, 0.2);
}

.gauge-fill {
  position: absolute;
  left: 0;
  height: 100%;
  background: #5BB5E0;
  background-image: repeating-linear-gradient(
    -45deg,
    transparent,
    transparent 6px,
    rgba(255, 255, 255, 0.3) 6px,
    rgba(255, 255, 255, 0.3) 12px
  );
  border-radius: 999rpx;
  animation: stripe-move 1s linear infinite;
}

@keyframes stripe-move {
  0% { background-position: 0 0; }
  100% { background-position: 24px 0; }
}

.gauge-tip {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #A85835;
  font-weight: 600;
}

.game-area {
  margin-top: 18rpx;
  background: white;
  border-radius: 28rpx;
  height: 720rpx;
  position: relative;
  overflow: hidden;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.1);
}

.ground {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 120rpx;
  background: #90EE90;
  border-top: 4rpx solid #228B22;
}

.ground::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 20rpx;
  background: repeating-linear-gradient(
    90deg,
    #228B22 0px,
    #228B22 8px,
    transparent 8px,
    transparent 16px
  );
  opacity: 0.6;
}

.player {
  position: absolute;
  left: 32rpx;
  bottom: 120rpx;
  width: 80rpx;
  height: 90rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-emoji {
  font-size: 64rpx;
}

.player-img {
  width: 80rpx;
  height: 80rpx;
}

.item {
  position: absolute;
  left: 0;
  bottom: 120rpx;
  width: 70rpx;
  height: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-emoji {
  font-size: 56rpx;
}

.toast {
  position: absolute;
  top: 20rpx;
  left: 50%;
  transform: translateX(-50%);
  padding: 12rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(17, 24, 39, 0.85);
}

.toast.good {
  background: rgba(16, 185, 129, 0.85);
}
.toast.bad {
  background: rgba(239, 68, 68, 0.85);
}

.toast-text {
  color: #fff;
  font-size: 24rpx;
  font-weight: 700;
}

.countdown {
  position: absolute;
  top: 46%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 92rpx;
  font-weight: 900;
  color: rgba(17, 24, 39, 0.8);
}

.sky-hint {
  position: absolute;
  top: 36rpx;
  left: 36rpx;
  right: 36rpx;
  padding: 24rpx 28rpx;
  border-radius: 24rpx;
  background: white;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874, 0 8rpx 20rpx rgba(96, 47, 39, 0.15);
  text-align: center;
}

.hint-title {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
  font-weight: 800;
  color: #602F27;
  margin-bottom: 8rpx;
}

.hint-title::before {
  content: '🎮';
  margin-right: 10rpx;
}

.hint-sub {
  display: block;
  font-size: 26rpx;
  color: #A85835;
  line-height: 1.5;
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


