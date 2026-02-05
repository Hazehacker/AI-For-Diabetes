<template>
  <view class="checkin-page">
    <view class="page-header">
      <view class="header-left">
        <text class="page-title">每日签到</text>
        <text class="page-subtitle">记录血糖/饮食/运动，积分换礼</text>
      </view>
      <view class="points-pill">
        <text class="pill-label">可用积分</text>
        <text class="pill-value">{{ dashboard.pointsBalance }}</text>
      </view>
    </view>

    <!-- 核心卡片 -->
    <view class="summary-card">
      <view class="summary-row">
        <view class="summary-item">
          <text class="summary-label">今日签到</text>
          <view class="summary-value">
            <text class="value-text">{{ dashboard.todaySigned ? '已签到' : '未签到' }}</text>
            <text class="value-badge" :class="dashboard.todaySigned ? 'badge-success' : 'badge-warning'">
              {{ dashboard.todaySigned ? '✓' : '!' }}
            </text>
          </view>
          <text class="summary-desc">奖励 {{ dashboard.todayPoints }} 积分</text>
        </view>

        <view class="summary-item">
          <text class="summary-label">连续签到</text>
          <text class="summary-value big">{{ dashboard.continuousDays }} 天</text>
          <text class="summary-desc">累计 {{ dashboard.totalDays }} 天</text>
        </view>

        <view class="summary-item">
          <text class="summary-label">会员特权</text>
          <text class="summary-value big">{{ dashboard.vipMultiplier }}x</text>
          <text class="summary-desc">积分加成</text>
        </view>
      </view>

      <button
        class="checkin-btn"
        :class="{ checked: dashboard.todaySigned }"
        :disabled="state.checking || dashboard.todaySigned"
        @tap="handleCheckin"
      >
        <text class="btn-icon">{{ dashboard.todaySigned ? '🎉' : '🚀' }}</text>
        <text>{{ dashboard.todaySigned ? '今天已签到' : '点击签到' }}</text>
      </button>
      <text v-if="dashboard.todaySigned" class="checkin-tip">已为你记录今日积分，继续保持！</text>
    </view>

    <!-- 月历 -->
    <view class="calendar-card">
      <view class="card-header">
        <view class="card-title">
          <text class="title-icon">📅</text>
          <text class="title-text">{{ calendarTitle }}</text>
        </view>
        <text class="hint">绿色=已签到 · 灰色=未签到</text>
      </view>

      <view class="calendar-grid">
        <view
          v-for="item in dashboard.monthlyCheckins"
          :key="item.date"
          class="calendar-cell"
          :class="{ checked: item.signed }"
        >
          <text class="calendar-day">{{ formatDay(item.date) }}</text>
          <text class="calendar-points" v-if="item.signed">+{{ item.points }}</text>
        </view>
      </view>
    </view>

    <!-- 积分商城 -->
    <view class="mall-card">
      <view class="card-header">
        <view class="card-title">
          <text class="title-icon">🎁</text>
          <text class="title-text">积分商城</text>
        </view>
        <text class="hint">选择商品，使用积分兑换</text>
      </view>

      <view class="mall-stats">
        <view class="stat-item">
          <text class="stat-label">总积分</text>
          <text class="stat-value">{{ dashboard.pointsBalance }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">历史已兑换</text>
          <text class="stat-value">0</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">可用积分</text>
          <text class="stat-value highlight">{{ dashboard.pointsBalance }}</text>
        </view>
      </view>

      <view class="goods-list">
        <view
          v-for="item in state.rewards"
          :key="item.id"
          class="goods-item"
        >
          <view class="goods-img">
            <image class="goods-img-inner" :src="item.cover" mode="aspectFill" />
          </view>
          <view class="goods-info">
            <text class="goods-name">{{ item.name }}</text>
            <text class="goods-desc">{{ item.desc }}</text>
            <view class="goods-bottom">
              <view class="price-block">
                <text class="points">{{ item.points }} 积分</text>
                <text class="tag" v-if="item.tag">{{ item.tag }}</text>
              </view>
              <view class="actions">
                <button
                  class="redeem-btn"
                  :class="{ disabled: dashboard.pointsBalance < item.points || state.redeeming }"
                  :disabled="dashboard.pointsBalance < item.points || state.redeeming"
                  @tap="() => handleRedeem(item)"
                >
                  {{ dashboard.pointsBalance < item.points ? '积分不足' : '积分兑换' }}
                </button>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { pointsApi } from '@/api'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const state = reactive({
  loading: false,
  checking: false,
  redeeming: false,
  rewards: []
})

const dashboard = reactive({
  pointsBalance: 0,
  todaySigned: false,
  todayPoints: 10,
  totalDays: 0,
  continuousDays: 0,
  vipMultiplier: 1,
  monthlyCheckins: []
})

const calendarTitle = `${new Date().getFullYear()}年${new Date().getMonth() + 1}月`

const formatDay = (dateStr) => {
  const d = new Date(dateStr)
  return d.getDate()
}

const normalizeDashboard = (data) => ({
  pointsBalance: data?.points_balance ?? data?.balance ?? 0,
  todaySigned: data?.today_signed ?? false,
  todayPoints: data?.today_points ?? 10,
  totalDays: data?.total_days ?? data?.totalDays ?? 0,
  continuousDays: data?.continuous_days ?? data?.continuousDays ?? 0,
  vipMultiplier: data?.vip_multiplier ?? 1,
  monthlyCheckins: data?.monthly_checkins ?? data?.monthlyCheckins ?? []
})

const mockRewards = [
  {
    id: 'vip-1m',
    name: '食卡卡会员·1个月',
    desc: '包含AI健康分析、饮食卡券，价值167元',
    points: 1180,
    tag: '限时特惠',
    cover: 'https://img.alicdn.com/imgextra/i2/2200706100162/O1CN01wSPvGv1jzoqjIyt63_!!2200706100162.png'
  },
  {
    id: 'vip-3m',
    name: '食卡卡会员·3个月',
    desc: '健康分析+会员权益，价值410元',
    points: 2998,
    tag: '限时优惠',
    cover: 'https://img.alicdn.com/imgextra/i3/2200706100162/O1CN01CAuQX31jzopSuA6AJ_!!2200706100162.png'
  },
  {
    id: 'brush',
    name: '亮可欣护齿软毛牙刷',
    desc: '医用级软毛，护龈舒适',
    points: 998,
    tag: '热兑',
    cover: 'https://img.alicdn.com/imgextra/i1/2200706100162/O1CN01jCOTBz1jzopSqQz7U_!!2200706100162.png'
  },
  {
    id: 'mouthwash',
    name: '亮可欣清新口气漱口水',
    desc: '抑菌清新，300ml',
    points: 2998,
    tag: '热兑',
    cover: 'https://img.alicdn.com/imgextra/i4/2200706100162/O1CN01EUYX8i1jzopSoj0tJ_!!2200706100162.png'
  },
  {
    id: 'toothpaste',
    name: '亮可欣温和金口腔护理牙膏',
    desc: '温和低刺激，呵护口腔',
    points: 4690,
    tag: '',
    cover: 'https://img.alicdn.com/imgextra/i2/2200706100162/O1CN01aJ6gl71jzopPUO4hZ_!!2200706100162.png'
  }
]

const mockDashboard = () => {
  const today = new Date()
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate()
  const monthly = []
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(today.getFullYear(), today.getMonth(), i)
    const isPast = date <= today
    monthly.push({
      date: date.toISOString().split('T')[0],
      signed: isPast && i % 2 === 0,
      points: 10
    })
  }
  return {
    pointsBalance: 0,
    todaySigned: false,
    todayPoints: 10,
    totalDays: 36,
    continuousDays: 5,
    vipMultiplier: 1.2,
    monthlyCheckins: monthly
  }
}

const loadDashboard = async () => {
  state.loading = true
  try {
    const res = await pointsApi.getCheckinDashboard()
    Object.assign(dashboard, normalizeDashboard(res?.data || {}))
  } catch (error) {
    console.warn('使用本地mock的签到数据，原因：', error?.message || error)
    Object.assign(dashboard, mockDashboard())
  } finally {
    state.loading = false
  }
}

const loadRewards = async () => {
  try {
    const res = await pointsApi.getRewards()
    state.rewards = Array.isArray(res?.data?.rewards)
      ? res.data.rewards
      : Array.isArray(res?.data)
        ? res.data
        : mockRewards
  } catch (error) {
    console.warn('使用本地mock的奖励数据，原因：', error?.message || error)
    state.rewards = mockRewards
  }
}

const handleCheckin = async () => {
  if (dashboard.todaySigned || state.checking) return
  state.checking = true
  try {
    await pointsApi.submitCheckin()
    dashboard.todaySigned = true
    dashboard.continuousDays += 1
    dashboard.totalDays += 1
    dashboard.pointsBalance += dashboard.todayPoints
    dashboard.monthlyCheckins = dashboard.monthlyCheckins.map((item) => {
      const todayStr = new Date().toISOString().split('T')[0]
      if (item.date === todayStr) {
        return { ...item, signed: true, points: dashboard.todayPoints }
      }
      return item
    })

    uni.showToast({ title: `签到成功 +${dashboard.todayPoints}积分`, icon: 'success' })
  } catch (error) {
    uni.showToast({ title: error?.message || '签到失败，请稍后重试', icon: 'none' })
  } finally {
    state.checking = false
  }
}

const handleRedeem = async (item) => {
  if (dashboard.pointsBalance < item.points || state.redeeming) return
  state.redeeming = true
  try {
    await pointsApi.redeemReward({ reward_id: item.id })
    dashboard.pointsBalance -= item.points
    uni.showToast({ title: '兑换成功', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: error?.message || '兑换失败，请稍后再试', icon: 'none' })
  } finally {
    state.redeeming = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  loadDashboard()
  loadRewards()
})
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 24rpx;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1f2937;
}

.page-subtitle {
  font-size: 26rpx;
  color: #6b7280;
}

.points-pill {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  padding: 16rpx 24rpx;
  border-radius: 24rpx;
  color: #fff;
  display: flex;
  flex-direction: column;
  min-width: 200rpx;
}

.pill-label {
  font-size: 22rpx;
  opacity: 0.9;
}

.pill-value {
  font-size: 40rpx;
  font-weight: 700;
}

.summary-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 50rpx rgba(79, 70, 229, 0.08);
  margin-bottom: 20rpx;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.summary-item {
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 20rpx;
}

.summary-label {
  font-size: 24rpx;
  color: #6b7280;
}

.summary-value {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: #111827;
  margin: 12rpx 0;
}

.summary-value.big {
  font-size: 38rpx;
}

.summary-desc {
  font-size: 22rpx;
  color: #9ca3af;
}

.value-badge {
  width: 40rpx;
  height: 40rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
}

.badge-success {
  background: #10b981;
}

.badge-warning {
  background: #f59e0b;
}

.checkin-btn {
  width: 100%;
  margin-top: 30rpx;
  padding: 0rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #969FFF, #5147FF);
  color: #fff;
  border: none;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 14rpx 40rpx #c4caed;
}

.checkin-btn.checked {
  background: #e5e7eb;
  color: #6b7280;
  box-shadow: none;
}

.checkin-btn:disabled {
  opacity: 0.9;
}

.btn-icon {
  font-size: 36rpx;
}

.checkin-tip {
  display: block;
  margin-top: 12rpx;
  text-align: center;
  color: #10b981;
  font-size: 24rpx;
}

.calendar-card,
.mall-card {
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 50rpx rgba(55, 65, 81, 0.06);
  margin-bottom: 20rpx;
}

.mall-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 16rpx;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  align-items: flex-start;
}

.stat-label {
  font-size: 22rpx;
  color: #94a3b8;
}

.stat-value {
  font-size: 30rpx;
  font-weight: 700;
  color: #0f172a;
}

.stat-value.highlight {
  color: #16a34a;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.title-icon {
  font-size: 30rpx;
}

.title-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #111827;
}

.hint {
  font-size: 24rpx;
  color: #9ca3af;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12rpx;
  margin-top: 12rpx;
}

.calendar-cell {
  background: #f3f4f6;
  border-radius: 12rpx;
  padding: 14rpx 10rpx;
  text-align: center;
  color: #6b7280;
}

.calendar-cell.checked {
  background: #dcfce7;
  color: #15803d;
  border: 1rpx solid #22c55e;
}

.calendar-day {
  font-size: 28rpx;
  font-weight: 600;
}

.calendar-points {
  font-size: 22rpx;
  color: #16a34a;
}

.goods-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.goods-item {
  display: flex;
  gap: 16rpx;
  background: #ffffff;
  border-radius: 18rpx;
  padding: 16rpx;
  border: 1rpx solid #eef2ff;
  box-shadow: 0 10rpx 30rpx rgba(79, 70, 229, 0.05);
}

.goods-img {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.goods-img-inner {
  width: 100%;
  height: 100%;
}

.goods-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.goods-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #111827;
}

.goods-desc {
  font-size: 24rpx;
  color: #6b7280;
}

.goods-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
}

.price-block {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.points {
  color: #dc2626;
  font-size: 30rpx;
  font-weight: 700;
}

.tag {
  background: #f97316;
  color: #fff;
  border-radius: 12rpx;
  padding: 4rpx 8rpx;
  font-size: 22rpx;
}

.actions {
  display: flex;
  height: 30px;
  align-items: center;
}

.redeem-btn {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #fff;
  padding: 0rpx 28rpx;
  border-radius: 12rpx;
  border: none;
  font-size: 26rpx;
  box-shadow: 0 8rpx 24rpx rgba(79, 70, 229, 0.25);
}

.redeem-btn.disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
}

@media (max-width: 768px) {
  .summary-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
