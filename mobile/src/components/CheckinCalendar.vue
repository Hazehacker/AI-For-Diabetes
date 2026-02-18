<template>
  <view v-if="visible" class="modal-overlay" @tap="handleClose">
    <view class="modal-content" @tap.stop>
      <view class="modal-header">
        <view class="title-container">
          <image class="title-icon" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
          <text class="title">打卡日历</text>
        </view>
        <view class="actions">
          <view class="close-btn" @tap="handleClose">
            <text class="icon">✕</text>
          </view>
        </view>
      </view>

      <!-- 统计卡片 -->
      <view class="stats-section">
        <view class="stat-card">
          <text class="stat-value">{{ totalCheckins }}</text>
          <text class="stat-label">总打卡</text>
        </view>
        <view class="stat-card">
          <text class="stat-value success">{{ continuousDays }}</text>
          <text class="stat-label">连续天数</text>
        </view>
        <view class="stat-card">
          <text class="stat-value warning">{{ thisMonthCount }}</text>
          <text class="stat-label">本月打卡</text>
        </view>
      </view>

      <!-- 日历 -->
      <view class="calendar-section">
        <view class="calendar-header">
          <view class="nav-btn" @tap="prevMonth">
            <text class="icon">‹</text>
          </view>
          <text class="month-title">{{ currentMonthText }}</text>
          <view class="nav-btn" @tap="nextMonth">
            <text class="icon">›</text>
          </view>
        </view>

        <!-- 星期标题 -->
        <view class="weekdays">
          <text class="weekday">日</text>
          <text class="weekday">一</text>
          <text class="weekday">二</text>
          <text class="weekday">三</text>
          <text class="weekday">四</text>
          <text class="weekday">五</text>
          <text class="weekday">六</text>
        </view>

        <!-- 日期网格 -->
        <view class="calendar-grid">
          <view 
            v-for="(day, index) in calendarDays" 
            :key="index"
            class="day-cell"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday && !day.hasCheckin,
              'has-checkin': day.hasCheckin,
              'status-good': day.hasCheckin && (day.status === '好' || !day.status),
              'status-ok': day.hasCheckin && day.status === '良好',
              'status-normal': day.hasCheckin && day.status === '一般'
            }"
          >
            <!-- 仅显示当前月份的日期 -->
            <template v-if="day.isCurrentMonth">
              <text class="day-number">{{ day.day }}</text>
              <text v-if="day.hasCheckin" class="checkin-mark">{{ day.emoji }}</text>
            </template>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { CHECKIN_STATUS_META, pickBetterCheckinStatus, toDateKey } from '@/utils/common'

const props = defineProps({
  visible: Boolean,
  records: Array
})

const emit = defineEmits(['close', 'sync'])

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())

const currentMonthText = computed(() => {
  return `${currentYear.value}年${currentMonth.value + 1}月`
})

const totalCheckins = computed(() => {
  if (!props.records || props.records.length === 0) return 0
  const set = new Set()
  props.records.forEach(r => {
    const key = toDateKey(r.checkin_time)
    if (key) set.add(key)
  })
  return set.size
})

const continuousDays = computed(() => {
  if (!props.records || props.records.length === 0) return 0

  // 按“日期”去重，避免同一天多条记录导致连续天数膨胀
  const uniqueDates = Array.from(
    new Set(props.records.map(r => toDateKey(r.checkin_time)).filter(Boolean))
  )
    .map(key => new Date(key))
    .filter(d => !isNaN(d.getTime()))
    .sort((a, b) => b - a) // 从新到旧

  if (uniqueDates.length === 0) return 0

  let continuous = 0
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 对齐H5：diffDays === continuous 时算连续（0,1,2...）
  for (const d of uniqueDates) {
    const checkDate = new Date(d)
    checkDate.setHours(0, 0, 0, 0)

    const diffDays = Math.floor((today - checkDate) / (1000 * 60 * 60 * 24))
    if (diffDays === continuous) {
      continuous++
    } else {
      break
    }
  }

  return continuous
})

const thisMonthCount = computed(() => {
  if (!props.records || props.records.length === 0) return 0

  const now = new Date()
  const nowMonth = now.getMonth()
  const nowYear = now.getFullYear()

  const set = new Set()
  props.records.forEach(record => {
    const d = new Date(record.checkin_time)
    if (isNaN(d.getTime())) return
    if (d.getMonth() === nowMonth && d.getFullYear() === nowYear) {
      const key = toDateKey(d)
      if (key) set.add(key)
    }
  })
  return set.size
})

// 日期Key -> 最佳控糖状态（好 > 良好 > 一般）
const statusByDateKey = computed(() => {
  const map = {}
  if (!props.records) return map

  for (const r of props.records) {
    const key = toDateKey(r.checkin_time)
    if (!key) continue
    const status = r.glucose_status || '好'
    map[key] = map[key] ? pickBetterCheckinStatus(map[key], status) : status
  }

  return map
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const prevLastDay = new Date(currentYear.value, currentMonth.value, 0)
  
  const firstDayOfWeek = firstDay.getDay()
  const daysInMonth = lastDay.getDate()
  const daysInPrevMonth = prevLastDay.getDate()
  
  // 上个月的日期
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    days.push({
      day: daysInPrevMonth - i,
      isCurrentMonth: false,
      isToday: false,
      hasCheckin: false
    })
  }
  
  // 当前月的日期
  const today = new Date()
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    const isToday = date.toDateString() === today.toDateString()
    const dateKey = toDateKey(date)
    const status = statusByDateKey.value[dateKey]
    const hasCheckin = !!status
    const emoji = hasCheckin
      ? (CHECKIN_STATUS_META[status]?.emoji || CHECKIN_STATUS_META['好'].emoji)
      : ''
    
    days.push({
      day: i,
      isCurrentMonth: true,
      isToday,
      hasCheckin,
      status: status || '',
      emoji
    })
  }
  
  // 下个月的日期
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      day: i,
      isCurrentMonth: false,
      isToday: false,
      hasCheckin: false
    })
  }
  
  return days
})

const handleClose = () => {
  emit('close')
}

const handleSync = () => {
  emit('sync')
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    const now = new Date()
    currentYear.value = now.getFullYear()
    currentMonth.value = now.getMonth()
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 40rpx;
}

.modal-content {
  width: 100%;
  max-width: 680rpx;
  max-height: 85vh;
  background: linear-gradient(180deg, #FFFEF7 0%, #FFF8E1 100%);
  border-radius: 32rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 8rpx 24rpx rgba(203, 142, 84, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 2rpx solid #E3C7A4;
  background: #FFFEF7;
  flex-shrink: 0;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.title-icon {
  width: 48rpx;
  height: 48rpx;
  animation: bounce 2s infinite;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #8B4513;
  text-shadow: 1rpx 1rpx 3rpx rgba(203, 142, 84, 0.3);
}

.actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}


.close-btn {
  width: 60rpx;
  height: 60rpx;
  background: #FFC0CB;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #FF9AAA;
  transition: transform 0.2s;
}

.close-btn:active {
  transform: scale(0.95);
}

.close-btn .icon {
  font-size: 32rpx;
  color: white;
  font-weight: bold;
}

.stats-section {
  display: flex;
  gap: 16rpx;
  padding: 32rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F5E6D3 100%);
  flex-shrink: 0;
}

.stat-card {
  flex: 1;
  background: #FFFEF7;
  border-radius: 20rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(203, 142, 84, 0.15);
  border: 1rpx solid #E3C7A4;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8rpx;
}

.stat-value.success {
  background: linear-gradient(135deg, #30BF78 0%, #22A366 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-value.warning {
  background: linear-gradient(135deg, #F6D387 0%, #D2691E 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  display: block;
  font-size: 22rpx;
  color: #8B4513;
}

.calendar-section {
  padding: 32rpx;
  flex: 1;
  overflow-y: auto;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.nav-btn {
  width: 60rpx;
  height: 60rpx;
  background: #AED581;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #8BC34A;
  transition: transform 0.2s;
}

.nav-btn:active {
  transform: scale(0.95);
}

.nav-btn .icon {
  font-size: 32rpx;
  color: #FFFFFF;
  font-weight: bold;
}

.month-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #8B4513;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.weekday {
  text-align: center;
  font-size: 24rpx;
  color: #8B4513;
  padding: 12rpx 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8rpx;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  /* 数字与表情横向排列（数字在左，表情在右），居中显示 */
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  position: relative;
}

.day-cell.other-month {
  opacity: 0.3;
}

.day-cell.today {
  background: #FFF8E7;
  border: 3rpx solid #FF9AAA;
  box-shadow: 0 2rpx 8rpx rgba(255, 154, 170, 0.3);
}

.day-cell.has-checkin {
  border: 2rpx solid transparent;
}

/* 与H5保持一致的状态配色：好=绿、良好=黄、一般=灰 */
.day-cell.status-good {
  background: #d1fae5; /* green-100 */
  border: 2rpx solid #a7f3d0; /* green-200 */
  position: relative;
}

.day-cell.status-good::after {
  content: '';
  position: absolute;
  top: -6rpx;
  right: -6rpx;
  width: 20rpx;
  height: 20rpx;
  background: url('/static/ch/ch_index_star.png') no-repeat center/cover;
  animation: rotate 3s linear infinite;
}

.day-cell.status-ok {
  background: #fef3c7; /* yellow-100 */
  border-color: #fde68a; /* yellow-200 */
}

.day-cell.status-normal {
  background: #f3f4f6; /* gray-100 */
  border-color: #e5e7eb; /* gray-200 */
}

.day-number {
  font-size: 26rpx;
  color: #602F27;
}

.checkin-mark {
  font-size: 20rpx;
  /* 放在日期数字右侧，略微留一点间距 */
  margin-left: 6rpx;
}
</style>
