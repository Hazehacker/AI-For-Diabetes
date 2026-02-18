<template>
  <!-- 儿童模式：奶酪仓鼠风格 -->
  <view v-if="userRole === 'child_under_12'" class="child-dashboard">
    <!-- 顶部导航栏 -->
    <view class="child-nav-bar">
      <view class="child-nav-left">
        <image class="child-nav-back" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      </view>
      <text class="child-nav-title">我的历史数据</text>
      <view class="child-nav-right">
      </view>
    </view>
    
    <!-- 历史数据折线图 -->    
    <view class="child-history-chart-card">
      <view class="child-chart-header">
        <view class="child-chart-title-container">
          <image class="child-chart-icon" src="/static/ch/ch_home_reg.png" mode="aspectFit"></image>
          <text class="child-chart-title">我的历史数据</text>
        </view>
        <view class="child-chart-period-selector">
          <text 
            v-for="(period, index) in chartPeriods" 
            :key="index"
            class="child-period-option"
            :class="{ 'child-period-active': selectedPeriod === period.value }"
            @tap="selectPeriod(period.value)"
          >{{ period.label }}</text>
        </view>
      </view>
      <view class="child-chart-container">
        <view class="child-pie-chart">
          <view v-if="!pieChartData.hasData" class="no-data-message">
            <text class="no-data-text">暂无数据</text>
          </view>
          <view v-else class="simple-pie-chart">
            <view class="pie-slice" :style="pieChartStyle"></view>
            <view class="pie-center">
              <text class="pie-text">{{ selectedPeriod === 'today' ? '本日' : '本周' }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="child-chart-legend">
        <view class="child-legend-item">
          <view class="child-legend-color child-legend-good"></view>
          <text class="child-legend-text">能量刚好</text>
        </view>
        <view class="child-legend-item">
          <view class="child-legend-color child-legend-low"></view>
          <text class="child-legend-text">能量低</text>
        </view>
        <view class="child-legend-item">
          <view class="child-legend-color child-legend-high"></view>
          <text class="child-legend-text">能量高</text>
        </view>
      </view>
    </view>

    <!-- 折线图卡片 -->
    <view class="child-line-chart-card">
      <view class="child-chart-header">
        <text class="child-chart-title">📈 血糖趋势</text>
        <view class="child-chart-period-selector">
          <text 
            v-for="(period, index) in chartPeriods" 
            :key="index"
            class="child-period-option"
            :class="{ 'child-period-active': selectedPeriod === period.value }"
            @tap="selectPeriod(period.value)"
          >{{ period.label }}</text>
        </view>
      </view>
      <view class="child-chart-container">
        <view class="child-line-chart">
          <view class="child-line-chart-svg">
            <svg viewBox="0 0 320 180" class="line-chart-svg">
              <!-- 背景 -->
              <rect width="100%" height="100%" fill="#FFFEF7" rx="8"/>
              
              <!-- 网格线 -->
              <defs>
                <pattern id="lineGrid" width="40" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#E3C7A4" stroke-width="0.5" opacity="0.2"/>
                </pattern>
              </defs>
              <rect x="40" y="20" width="260" height="120" fill="url(#lineGrid)" />
              
              <!-- Y轴 -->
              <line x1="40" y1="20" x2="40" y2="140" stroke="#8B4513" stroke-width="2"/>
              <!-- X轴 -->
              <line x1="40" y1="140" x2="300" y2="140" stroke="#8B4513" stroke-width="2"/>
              
              <!-- Y轴刻度 -->
              <g font-family="Arial" font-size="10" fill="#8B4513">
                <text x="35" y="25" text-anchor="end">10</text>
                <text x="35" y="50" text-anchor="end">8</text>
                <text x="35" y="75" text-anchor="end">6</text>
                <text x="35" y="100" text-anchor="end">4</text>
                <text x="35" y="125" text-anchor="end">2</text>
                <text x="35" y="145" text-anchor="end">0</text>
              </g>
              
              <!-- X轴刻度 -->
              <g font-family="Arial" font-size="9" fill="#8B4513">
                <text v-if="selectedPeriod === 'today'" x="70" y="155" text-anchor="middle">6:00</text>
                <text v-if="selectedPeriod === 'today'" x="110" y="155" text-anchor="middle">9:00</text>
                <text v-if="selectedPeriod === 'today'" x="150" y="155" text-anchor="middle">12:00</text>
                <text v-if="selectedPeriod === 'today'" x="190" y="155" text-anchor="middle">15:00</text>
                <text v-if="selectedPeriod === 'today'" x="230" y="155" text-anchor="middle">18:00</text>
                <text v-if="selectedPeriod === 'today'" x="270" y="155" text-anchor="middle">21:00</text>
                
                <text v-if="selectedPeriod === 'week'" x="70" y="155" text-anchor="middle">周一</text>
                <text v-if="selectedPeriod === 'week'" x="110" y="155" text-anchor="middle">周二</text>
                <text v-if="selectedPeriod === 'week'" x="150" y="155" text-anchor="middle">周三</text>
                <text v-if="selectedPeriod === 'week'" x="190" y="155" text-anchor="middle">周四</text>
                <text v-if="selectedPeriod === 'week'" x="230" y="155" text-anchor="middle">周五</text>
                <text v-if="selectedPeriod === 'week'" x="270" y="155" text-anchor="middle">周六</text>
              </g>
              
              <!-- 目标区间 -->
              <rect x="40" y="65" width="260" height="35" fill="#8CC152" fill-opacity="0.1" stroke="#8CC152" stroke-width="1" stroke-dasharray="3,3"/>
              <text x="305" y="80" font-family="Arial" font-size="8" fill="#8CC152">目标区间</text>
              
              <!-- 折线数据（根据时间段变化） -->
              <polyline v-if="selectedPeriod === 'today'"
                points="70,110 110,85 150,95 190,70 230,90 270,75"
                fill="none" 
                stroke="#8CC152" 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <polyline v-if="selectedPeriod === 'week'"
                points="70,100 110,80 150,105 190,85 230,95 270,80"
                fill="none" 
                stroke="#8CC152" 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              
              <!-- 数据点（本日） -->
              <g v-if="selectedPeriod === 'today'">
                <circle cx="70" cy="110" r="4" fill="#F5D76E" stroke="#fff" stroke-width="2"/>
                <circle cx="110" cy="85" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="150" cy="95" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="190" cy="70" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="230" cy="90" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="270" cy="75" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
              </g>
              
              <!-- 数据点（本周） -->
              <g v-if="selectedPeriod === 'week'">
                <circle cx="70" cy="100" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="110" cy="80" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="150" cy="105" r="4" fill="#F5D76E" stroke="#fff" stroke-width="2"/>
                <circle cx="190" cy="85" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="230" cy="95" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                <circle cx="270" cy="80" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
              </g>
              
              <!-- 单位标签 -->
              <text x="15" y="85" font-family="Arial" font-size="10" fill="#8B4513" transform="rotate(-90 15 85)">mmol/L</text>
            </svg>
          </view>
        </view>
      </view>
    </view>

    <!-- 雷达图卡片 -->
    <view class="child-radar-chart-card">
      <view class="child-chart-header">
        <text class="child-chart-title">🎯 健康评估</text>
        <view class="child-chart-period-selector">
          <text 
            v-for="(period, index) in chartPeriods" 
            :key="index"
            class="child-period-option"
            :class="{ 'child-period-active': selectedPeriod === period.value }"
            @tap="selectPeriod(period.value)"
          >{{ period.label }}</text>
        </view>
      </view>
      <view class="child-chart-container">
        <view class="child-radar-chart">
          <view class="child-radar-chart-svg">
            <svg viewBox="0 0 240 240" class="radar-chart-svg">
              <!-- 背景 -->
              <rect width="100%" height="100%" fill="#FFFEF7" rx="8"/>
              
              <!-- 雷达图背景网格 -->
              <g transform="translate(120,120)">
                <!-- 同心圆和刻度 -->
                <circle r="20" fill="none" stroke="#E3C7A4" stroke-width="1" opacity="0.4"/>
                <circle r="40" fill="none" stroke="#E3C7A4" stroke-width="1" opacity="0.4"/>
                <circle r="60" fill="none" stroke="#E3C7A4" stroke-width="1" opacity="0.4"/>
                <circle r="80" fill="none" stroke="#E3C7A4" stroke-width="2" opacity="0.6"/>
                
                <!-- 刻度数值 -->
                <g font-family="Arial" font-size="8" fill="#8B4513">
                  <text x="-5" y="-75" text-anchor="middle">5</text>
                  <text x="-5" y="-55" text-anchor="middle">4</text>
                  <text x="-5" y="-35" text-anchor="middle">3</text>
                  <text x="-5" y="-15" text-anchor="middle">2</text>
                </g>
                
                <!-- 辐射线 -->
                <line x1="0" y1="-80" x2="0" y2="80" stroke="#8B4513" stroke-width="1.5" opacity="0.6"/>
                <line x1="-80" y1="0" x2="80" y2="0" stroke="#8B4513" stroke-width="1.5" opacity="0.6"/>
                <line x1="-56.6" y1="-56.6" x2="56.6" y2="56.6" stroke="#8B4513" stroke-width="1.5" opacity="0.6"/>
                <line x1="56.6" y1="-56.6" x2="-56.6" y2="56.6" stroke="#8B4513" stroke-width="1.5" opacity="0.6"/>
                <line x1="-56.6" y1="56.6" x2="56.6" y2="-56.6" stroke="#8B4513" stroke-width="1.5" opacity="0.6"/>
                
                <!-- 数据区域（本日） -->
                <polygon v-if="selectedPeriod === 'today'"
                  points="0,-60 45,30 -30,50 -50,-20 -10,-70"
                  fill="#8CC152" 
                  fill-opacity="0.25" 
                  stroke="#8CC152" 
                  stroke-width="3"
                />
                
                <!-- 数据区域（本周） -->
                <polygon v-if="selectedPeriod === 'week'"
                  points="0,-65 50,25 -25,55 -55,-25 -15,-75"
                  fill="#8CC152" 
                  fill-opacity="0.25" 
                  stroke="#8CC152" 
                  stroke-width="3"
                />
                
                <!-- 数据点（本日） -->
                <g v-if="selectedPeriod === 'today'">
                  <circle cx="0" cy="-60" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                  <circle cx="45" cy="30" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                  <circle cx="-30" cy="50" r="4" fill="#F5D76E" stroke="#fff" stroke-width="2"/>
                  <circle cx="-50" cy="-20" r="4" fill="#FF9AAA" stroke="#fff" stroke-width="2"/>
                  <circle cx="-10" cy="-70" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                </g>
                
                <!-- 数据点（本周） -->
                <g v-if="selectedPeriod === 'week'">
                  <circle cx="0" cy="-65" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                  <circle cx="50" cy="25" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                  <circle cx="-25" cy="55" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                  <circle cx="-55" cy="-25" r="4" fill="#F5D76E" stroke="#fff" stroke-width="2"/>
                  <circle cx="-15" cy="-75" r="4" fill="#8CC152" stroke="#fff" stroke-width="2"/>
                </g>
                
                <!-- 标签 -->
                <g font-family="Arial" font-size="11" font-weight="bold" fill="#8B4513">
                  <text x="0" y="-95" text-anchor="middle">血糖控制</text>
                  <text x="70" y="8" text-anchor="middle">运动量</text>
                  <text x="43" y="75" text-anchor="middle">睡眠质量</text>
                  <text x="-43" y="75" text-anchor="middle">饮食规律</text>
                  <text x="-70" y="8" text-anchor="middle">心情状态</text>
                </g>
                
                <!-- 评分显示 -->
                <g v-if="selectedPeriod === 'today'" font-family="Arial" font-size="9" fill="#602F27">
                  <text x="8" y="-55" text-anchor="start">4.5</text>
                  <text x="50" y="35" text-anchor="start">4.2</text>
                  <text x="-25" y="60" text-anchor="start">3.5</text>
                  <text x="-60" y="-15" text-anchor="start">2.8</text>
                  <text x="-5" y="-75" text-anchor="start">4.8</text>
                </g>
                
                <g v-if="selectedPeriod === 'week'" font-family="Arial" font-size="9" fill="#602F27">
                  <text x="8" y="-60" text-anchor="start">4.8</text>
                  <text x="55" y="30" text-anchor="start">4.5</text>
                  <text x="-20" y="65" text-anchor="start">4.1</text>
                  <text x="-65" y="-20" text-anchor="start">3.2</text>
                  <text x="-10" y="-80" text-anchor="start">4.9</text>
                </g>
              </g>
            </svg>
          </view>
        </view>
      </view>
    </view>

    <!-- 小仓鼠的话 -->
    <view class="child-hamster-words-card">
      <view class="child-hamster-avatar-small">
        <image class="child-hamster-img" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
      </view>
      <view class="child-words-bubble">
        <text class="child-words-text">{{ hamsterWords }}</text>
        <view class="child-bubble-tail"></view>
      </view>
    </view>
    
    <view class="child-bottom-spacer"></view>
  </view>

  <!-- 成人/青少年模式 -->
  <view v-else class="dashboard-container" :style="{ backgroundColor: containerBgColor }">
    <!-- 顶部警报横幅 -->
    <view v-if="showAlertBanner" class="alert-banner" :class="alertBannerClass">
      <text class="alert-icon">{{ alertIcon }}</text>
      <text class="alert-text">{{ alertText }}</text>
    </view>

    <!-- 数据中断提示 -->
    <view v-if="!dataConnection.isConnected" class="connection-lost-banner">
      <text class="banner-icon">⚠️</text>
      <text class="banner-text">传感器信号丢失，数据不是实时的</text>
    </view>

    <!-- 当前状态区 -->
    <view class="status-zone" :class="statusZoneClass" @tap="showDetailCard">
      <view class="normal-mode">
        <!-- 正常模式：数值显示 -->
        <view class="status-header">
          <text class="status-label">当前状态</text>
          <text class="last-update">{{ lastUpdateText }}</text>
        </view>
        
        <view class="glucose-display">
          <text v-if="currentGlucose.value" class="glucose-value">{{ currentGlucose.value }}</text>
          <text v-else class="glucose-value placeholder">--.-</text>
          <text class="glucose-unit">mmol/L</text>
        </view>
        
        <view class="trend-display">
          <text class="trend-arrow">{{ trendArrow }}</text>
          <text class="trend-text">{{ trendText }}</text>
        </view>
      </view>
    </view>

    <!-- 目标区间指示器（仅非儿童模式） -->
    <view v-if="userRole !== 'child_under_12'" class="target-range-indicator">
      <text class="indicator-label">目标区间</text>
      <view class="range-bar">
        <view class="range-background">
          <view class="safe-zone" :style="safeZoneStyle"></view>
        </view>
        <view class="current-position" :style="currentPositionStyle">
          <view class="position-dot" :class="{ pulse: isPulseActive }"></view>
        </view>
      </view>
      <view class="range-labels">
        <text class="range-label">{{ targetRange.min }}</text>
        <text class="range-label">{{ targetRange.max }}</text>
      </view>
    </view>

    <!-- 实时曲线图（仅≥12岁和家属） -->
    <view v-if="showFullDashboard" class="chart-section">
      <view class="chart-header">
        <text class="chart-title">血糖趋势</text>
        <view class="time-tabs">
          <text 
            v-for="tab in timeTabs" 
            :key="tab.value"
            class="time-tab"
            :class="{ active: selectedTimeRange === tab.value }"
            @tap="selectTimeRange(tab.value)"
          >
            {{ tab.label }}
          </text>
        </view>
      </view>
      
      <view class="chart-container">
        <canvas 
          canvas-id="glucoseChart" 
          class="glucose-chart"
          @touchstart="handleChartTouchStart"
          @touchmove="handleChartTouchMove"
          @touchend="handleChartTouchEnd"
        ></canvas>
        
        <!-- 事件标记层 -->
        <view class="event-markers">
          <view 
            v-for="event in visibleEvents" 
            :key="event.id"
            class="event-marker"
            :style="{ left: event.position + '%' }"
            @tap="showEventDetail(event)"
          >
            <text class="event-icon">{{ event.icon }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 每日统计（仅≥12岁和家属） -->
    <view v-if="showFullDashboard" class="stats-section">
      <view class="stat-card">
        <text class="stat-label">TIR</text>
        <text class="stat-value">{{ stats.tir || '--' }}%</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">GMI</text>
        <text class="stat-value">{{ stats.gmi || '--' }}%</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">CV</text>
        <text class="stat-value">{{ stats.cv || '--' }}%</text>
      </view>
    </view>

    <!-- AI 建议区 -->
    <view class="suggestion-section" :class="suggestionClass">
      <view class="suggestion-header">
        <text class="suggestion-icon">{{ suggestionIcon }}</text>
        <text class="suggestion-title">{{ suggestionTitle }}</text>
      </view>
      <text class="suggestion-text">{{ currentSuggestion.text }}</text>
      
      <button 
        v-if="currentSuggestion.action" 
        class="action-button"
        :class="suggestionClass"
        @tap="handleSuggestionAction"
      >
        {{ actionButtonText }}
      </button>
    </view>

    <!-- 底部导航占位 -->
    <view class="bottom-spacer"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useDashboardStore } from '@/store/dashboard'
import { useGlucoseCurveStore } from '@/store/glucoseCurve'
import { storeToRefs } from 'pinia'
import { GlucoseChartHelper, generateMockData } from '@/utils/chartHelper'
import GlucoseCurveChart from '@/components/GlucoseCurveChart.vue'
import AddGlucoseRecord from '@/components/AddGlucoseRecord.vue'

const dashboardStore = useDashboardStore()
const { 
  currentGlucose, 
  targetRange, 
  stats, 
  userRole, 
  dataConnection,
  historyData,
  events
} = storeToRefs(dashboardStore)

// 儿童模式金币数量
const coinCount = ref(164)

const { 
  statusColor, 
  trendArrow, 
  showFullDashboard, 
  currentSuggestion 
} = dashboardStore

// 图表实例
let chartHelper = null

// 时间范围选项
const timeTabs = [
  { label: '1小时', value: '1h' },
  { label: '6小时', value: '6h' },
  { label: '24小时', value: '24h' }
]
const selectedTimeRange = ref('6h')

// 定时器
let refreshTimer = null
let connectionCheckTimer = null

// 容器背景色
const containerBgColor = computed(() => {
  if (currentGlucose.value.status === 'emergency') {
    return '#FEE2E2'
  }
  return '#F3F4F6'
})

// 警报横幅
const showAlertBanner = computed(() => {
  return currentGlucose.value.status === 'emergency' || currentGlucose.value.status === 'alert'
})

const alertBannerClass = computed(() => {
  return currentGlucose.value.status === 'emergency' ? 'emergency' : 'warning'
})

const alertIcon = computed(() => {
  return currentGlucose.value.status === 'emergency' ? '🚨' : '⚠️'
})

const alertText = computed(() => {
  if (currentGlucose.value.status === 'emergency') {
    return currentGlucose.value.value < 3.9 ? '紧急低血糖警报' : '紧急高血糖警报'
  }
  return '血糖异常，请注意'
})

// 状态区样式
const statusZoneClass = computed(() => {
  return `status-${currentGlucose.value.status}`
})

// ========== 儿童模式（奶酪仓鼠风格）相关 ==========

// 问候语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 11) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 每日星星数
const dailyStars = ref(3)

// 成就系统
const achievements = ref([
  { id: 1, name: '早起鸟儿', desc: '早上8点前测血糖', icon: '🐦', unlocked: true },
  { id: 2, name: '健康饮食', desc: '记录3次健康餐食', icon: '🥗', unlocked: true },
  { id: 3, name: '运动达人', desc: '完成30分钟运动', icon: '🏃', unlocked: false },
  { id: 4, name: '水分补充', desc: '喝够8杯水', icon: '💧', unlocked: false },
  { id: 5, name: '按时休息', desc: '晚上10点前睡觉', icon: '😴', unlocked: false }
])

const unlockedAchievements = computed(() => achievements.value.filter(a => a.unlocked).length)
const totalAchievements = computed(() => achievements.value.length)

// 健康数据
const healthData = ref({
  waterCount: 5,
  exerciseTime: 30,
  sleepQuality: '良好'
})

// 图表相关
const chartPeriods = [
  { label: '本日', value: 'today' },
  { label: '本周', value: 'week' }
]
const selectedPeriod = ref('today')
let childChart = null

// 今日日期
const todayDate = computed(() => {
  const today = new Date()
  return `${today.getMonth() + 1}月${today.getDate()}日`
})

// 小仓鼠的话
const hamsterWords = computed(() => {
  const messages = [
    '今天你表现得很棒哦！继续加油！',
    '记得多喝水，小仓鼠也要喝水呢~',
    '运动让我们更健康，一起动起来吧！',
    '按时吃饭很重要，营养要均衡哦~',
    '早睡早起身体好，小仓鼠也要休息呢！'
  ]
  const hour = new Date().getHours()
  if (hour < 9) return '早上好！新的一天开始啦~'
  if (hour < 12) return messages[1]
  if (hour < 15) return messages[3]
  if (hour < 18) return messages[2]
  if (hour < 21) return messages[0]
  return messages[4]
})

// 儿童状态样式类
const childStatusClass = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return 'status-danger'
  if (status === 'alert') return 'status-warning'
  return 'status-good'
})

// 是否开心状态
const isHappy = computed(() => currentGlucose.value.status === 'normal')
const isAlert = computed(() => currentGlucose.value.status === 'emergency' || currentGlucose.value.status === 'alert')

// 吉祥物表情
const mascotEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '🐹😰'
  if (status === 'alert') return '🐹😟'
  if (status === 'data_loss') return '🐹😴'
  return '🐹😊'
})

// 吉祥物消息
const mascotMessage = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') {
    return currentGlucose.value.value < 3.9 
      ? '能量不够啦！快吃点小零食补充能量吧~' 
      : '能量太多啦！我们去活动活动吧~'
  }
  if (status === 'alert') return '要注意一下哦，小仓鼠在关注你~'
  if (status === 'data_loss') return '信号断了，让爸爸妈妈帮忙看看~'
  return '太棒了！你的能量刚刚好，继续保持哦！'
})

// 儿童状态文本
const childStatusText = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '需要注意'
  if (status === 'alert') return '稍微注意'
  return '状态很好'
})

// 能量指针位置
const energyPointerPosition = computed(() => {
  if (!currentGlucose.value.value) return 50
  const value = currentGlucose.value.value
  // 映射到 0-100，3.9-10.0 为正常范围
  const minVal = 2.0
  const maxVal = 15.0
  const percentage = ((value - minVal) / (maxVal - minVal)) * 100
  return Math.max(5, Math.min(95, percentage))
})

// 指针表情
const pointerEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '😰'
  if (status === 'alert') return '😟'
  return '😊'
})

// 儿童任务列表
const childTasks = ref([
  { id: 1, name: '吃早餐', icon: '🍳', completed: true },
  { id: 2, name: '测血糖', icon: '💉', completed: true },
  { id: 3, name: '吃午餐', icon: '🍱', completed: true },
  { id: 4, name: '户外活动', icon: '🏃', completed: false },
  { id: 5, name: '吃晚餐', icon: '🍲', completed: false }
])

const completedTasks = computed(() => childTasks.value.filter(t => t.completed).length)
const totalTasks = computed(() => childTasks.value.length)

const toggleTask = (task) => {
  task.completed = !task.completed
  if (task.completed) {
    dailyStars.value++
    uni.showToast({ title: '获得一颗星星！⭐', icon: 'none' })
  }
}

// 奖励进度
const milestones = [
  { stars: 2, icon: '🍬', position: 20 },
  { stars: 4, icon: '🎮', position: 50 },
  { stars: 6, icon: '🎁', position: 80 }
]

const rewardProgress = computed(() => {
  return Math.min(100, (dailyStars.value / 6) * 100)
})

const starsToNextReward = computed(() => {
  for (const m of milestones) {
    if (dailyStars.value < m.stars) {
      return m.stars - dailyStars.value
    }
  }
  return 0
})

// 提示卡片
const tipCardClass = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return 'tip-danger'
  if (status === 'alert') return 'tip-warning'
  return 'tip-normal'
})

const tipIcon = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '🚨'
  if (status === 'alert') return '⚠️'
  return '💡'
})

const tipTitle = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '小仓鼠提醒'
  if (status === 'alert') return '温馨提示'
  return '小贴士'
})

const tipText = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') {
    return currentGlucose.value.value < 3.9 
      ? '快告诉爸爸妈妈，吃点糖果补充能量吧！' 
      : '能量太多了，去跑跑跳跳消耗一下吧！'
  }
  if (status === 'alert') return '注意观察，如果不舒服要告诉大人哦~'
  return '保持好心情，多喝水，按时吃饭，你是最棒的！'
})

const showTipAction = computed(() => {
  return currentGlucose.value.status === 'emergency'
})

const tipActionText = computed(() => {
  return currentGlucose.value.value < 3.9 ? '记录补糖' : '记录活动'
})

const handleTipAction = () => {
  uni.showToast({ title: '已通知家长', icon: 'success' })
}

// 快捷功能导航
const goToCalories = () => {
  uni.switchTab({ url: '/pages/calories/index' })
}

const goToCheckin = () => {
  uni.navigateTo({ url: '/pages/profile/daily-checkin' })
}

const goToVideo = () => {
  uni.switchTab({ url: '/pages/video/index' })
}

const goToCommunity = () => {
  uni.switchTab({ url: '/pages/community/companion' })
}

// ========== 原有儿童模式代码（保留兼容）==========
const characterEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '😰'
  if (status === 'alert') return '😟'
  if (status === 'data_loss') return '😴'
  return '😊'
})

const characterMessage = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '需要帮助！'
  if (status === 'alert') return '要注意哦'
  if (status === 'data_loss') return '信号断了'
  return '你做得很棒！'
})

const energyPercentage = computed(() => {
  if (!currentGlucose.value.value) return 50
  const { min, max } = targetRange.value
  const value = currentGlucose.value.value
  
  // 将血糖值映射到0-100的能量条
  const percentage = ((value - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, percentage))
})

const indicatorEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '🔴'
  if (status === 'alert') return '🟡'
  return '🟢'
})

// 趋势文本
const trendText = computed(() => {
  const { trend, trendRate } = currentGlucose.value
  if (trend === 'up') {
    return trendRate === 'fast' ? '快速上升' : '缓慢上升'
  } else if (trend === 'down') {
    return trendRate === 'fast' ? '快速下降' : '缓慢下降'
  }
  return '平稳'
})

// 最后更新时间
const lastUpdateText = computed(() => {
  if (!dataConnection.value.lastUpdateTime) return ''
  const now = new Date()
  const last = new Date(dataConnection.value.lastUpdateTime)
  const diff = Math.floor((now - last) / 1000 / 60)
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  return `${Math.floor(diff / 60)}小时前`
})

// 目标区间样式
const safeZoneStyle = computed(() => {
  const { min, max } = targetRange.value
  const totalRange = max - min
  return {
    left: '0%',
    width: '100%',
    backgroundColor: 'rgba(16, 185, 129, 0.2)'
  }
})

const currentPositionStyle = computed(() => {
  if (!currentGlucose.value.value) return { left: '50%' }
  
  const { min, max } = targetRange.value
  const value = currentGlucose.value.value
  const percentage = ((value - min) / (max - min)) * 100
  
  return {
    left: Math.max(0, Math.min(100, percentage)) + '%'
  }
})

const isPulseActive = computed(() => {
  return currentGlucose.value.status === 'emergency' || currentGlucose.value.status === 'alert'
})

// 可见事件
const visibleEvents = computed(() => {
  // TODO: 根据选中的时间范围过滤事件
  return events.value.map(event => ({
    ...event,
    position: 50, // 临时位置，实际需要根据时间计算
    icon: getEventIcon(event.type)
  }))
})

// 建议区样式
const suggestionClass = computed(() => {
  return `suggestion-${currentSuggestion.type}`
})

const suggestionIcon = computed(() => {
  const iconMap = {
    emergency: '🚨',
    warning: '⚠️',
    info: '💡'
  }
  return iconMap[currentSuggestion.type] || '💡'
})

const suggestionTitle = computed(() => {
  const titleMap = {
    emergency: '紧急建议',
    warning: '温馨提示',
    info: 'AI 洞察'
  }
  return titleMap[currentSuggestion.type] || 'AI 洞察'
})

const actionButtonText = computed(() => {
  const actionMap = {
    add_carbs: '记录补糖',
    retest: '重新测量',
    monitor: '继续监测',
    reconnect: '重新连接'
  }
  return actionMap[currentSuggestion.action] || '了解详情'
})

// 方法
const showDetailCard = () => {
  // TODO: 显示详细信息卡片
  console.log('显示详细信息')
}

const selectTimeRange = (range) => {
  selectedTimeRange.value = range
  drawChart()
}

const handleChartTouchStart = (e) => {
  // TODO: 处理图表触摸开始
}

const handleChartTouchMove = (e) => {
  // TODO: 处理图表触摸移动
}

const handleChartTouchEnd = (e) => {
  // TODO: 处理图表触摸结束
}

const showEventDetail = (event) => {
  // TODO: 显示事件详情
  console.log('事件详情:', event)
}

const handleSuggestionAction = () => {
  const action = currentSuggestion.action
  
  if (action === 'add_carbs') {
    // TODO: 跳转到记录页面
    uni.showToast({ title: '跳转到记录页面', icon: 'none' })
  } else if (action === 'retest') {
    // TODO: 提示重新测量
    uni.showToast({ title: '请重新测量血糖', icon: 'none' })
  } else if (action === 'reconnect') {
    // TODO: 尝试重新连接
    uni.showToast({ title: '正在重新连接...', icon: 'loading' })
  }
}

const getEventIcon = (type) => {
  const iconMap = {
    meal: '🍽️',
    exercise: '🏃',
    medication: '💊',
    sleep: '😴'
  }
  return iconMap[type] || '📌'
}

// 显示添加记录弹窗
const showAddRecordModal = () => {
  addRecordVisible.value = true
}

// 初始化图表
const initChart = async () => {
  if (!showFullDashboard) return
  
  await nextTick()
  
  try {
    // 获取canvas尺寸
    const query = uni.createSelectorQuery()
    query.select('.glucose-chart').boundingClientRect()
    query.exec((res) => {
      if (res[0]) {
        const { width, height } = res[0]
        chartHelper = new GlucoseChartHelper('glucoseChart', width, height)
        
        chartHelper.init().then(() => {
          drawChart()
        })
      }
    })
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

// 绘制图表
const drawChart = () => {
  if (!chartHelper) return
  
  // 获取对应时间范围的数据
  let data = historyData.value
  
  // 如果没有真实数据，使用模拟数据
  if (data.length === 0) {
    const hours = selectedTimeRange.value === '1h' ? 1 : (selectedTimeRange.value === '6h' ? 6 : 24)
    data = generateMockData(hours)
  }
  
  chartHelper.draw(data, {
    targetMin: targetRange.value.min,
    targetMax: targetRange.value.max,
    warningLow: targetRange.value.warningLow,
    warningHigh: targetRange.value.warningHigh
  })
}

// 模拟数据更新
const simulateDataUpdate = () => {
  // 生成模拟血糖值
  const mockValue = 3.9 + Math.random() * 6.1
  const mockTrend = Math.random() > 0.5 ? 'up' : (Math.random() > 0.5 ? 'down' : 'stable')
  const mockTrendRate = Math.random() > 0.7 ? 'fast' : 'normal'
  
  dashboardStore.updateGlucose({
    value: parseFloat(mockValue.toFixed(1)),
    trend: mockTrend,
    trendRate: mockTrendRate
  })
  
  // 添加到历史数据
  dashboardStore.addHistoryData({
    timestamp: new Date(),
    value: parseFloat(mockValue.toFixed(1))
  })
  
  // 更新图表
  if (chartHelper) {
    drawChart()
  }
}

// 选择图表时间范围
const selectPeriod = (period) => {
  selectedPeriod.value = period
  drawChildPieChart()
}

// 初始化儿童模式饼状图
const initChildPieChart = () => {
  // 先初始化模拟数据
  if (!mockDataCache.value) {
    mockDataCache.value = generateMoreMockData()
  }
  
  setTimeout(() => {
    drawChildPieChart()
  }, 300)
}

// 饼状图数据
const pieChartData = ref({
  goodPercentage: 0,
  lowPercentage: 0,
  highPercentage: 0,
  hasData: false
})

// 绘制儿童模式饼状图
const drawChildPieChart = () => {
  // 强制初始化模拟数据
  if (!mockDataCache.value) {
    mockDataCache.value = generateMoreMockData()
  }
  
  // 获取历史数据
  const historyData = getMockHistoryData(selectedPeriod.value)
  
  // 更新是否有数据标志
  hasData.value = historyData && historyData.length > 0
  
  // 如果没有数据，重置饼图数据
  if (!historyData || historyData.length === 0) {
    pieChartData.value = {
      goodPercentage: 0,
      lowPercentage: 0,
      highPercentage: 0,
      hasData: false
    }
    return
  }
  
  // 计算饼状图数据
  const targetMin = 4.4
  const targetMax = 8.0
  
  let goodCount = 0
  let lowCount = 0
  let highCount = 0
  
  historyData.forEach(item => {
    if (item.value < targetMin) {
      lowCount++
    } else if (item.value > targetMax) {
      highCount++
    } else {
      goodCount++
    }
  })
  
  const total = historyData.length
  
  // 更新响应式数据
  pieChartData.value = {
    goodPercentage: (goodCount / total) * 100,
    lowPercentage: (lowCount / total) * 100,
    highPercentage: (highCount / total) * 100,
    hasData: true
  }
}

// 计算饼图样式
const pieChartStyle = computed(() => {
  if (!pieChartData.value.hasData) {
    return {
      background: '#f0f0f0'
    }
  }
  
  const { goodPercentage, lowPercentage, highPercentage } = pieChartData.value
  
  let cumulativePercentage = 0
  let gradientStops = []
  
  if (goodPercentage > 0) {
    gradientStops.push(`#8CC152 ${cumulativePercentage}% ${cumulativePercentage + goodPercentage}%`)
    cumulativePercentage += goodPercentage
  }
  
  if (lowPercentage > 0) {
    gradientStops.push(`#F5D76E ${cumulativePercentage}% ${cumulativePercentage + lowPercentage}%`)
    cumulativePercentage += lowPercentage
  }
  
  if (highPercentage > 0) {
    gradientStops.push(`#FF9AAA ${cumulativePercentage}% ${cumulativePercentage + highPercentage}%`)
    cumulativePercentage += highPercentage
  }
  
  return {
    background: `conic-gradient(${gradientStops.join(', ')})`
  }
})

// 根据选择的时间段获取X轴标签
const getXLabels = (period, data) => {
  if (!data || data.length === 0) return []
  
  switch (period) {
    case 'today':
      // 显示小时
      return data.map(item => {
        const date = new Date(item.timestamp)
        return `${date.getHours()}:00`
      })
    case 'week':
      // 显示星期几
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return data.map(item => {
        const date = new Date(item.timestamp)
        return days[date.getDay()]
      })
    default:
      return []
  }
}

// 返回上一页
const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

// 生成更多模拟数据
const generateMoreMockData = () => {
  // 今天的数据 - 每3小时一个点，共8个点
  const todayData = []
  const now = new Date()
  for (let i = 0; i < 8; i++) {
    const hour = i * 3
    const timestamp = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, 0, 0)
    // 生成一个4.0-9.0之间的随机值，并加入一些波动
    let value = 6.5 + Math.sin(i / 8 * Math.PI * 2) * 1.5 + (Math.random() - 0.5) * 1.0
    // 确保值在合理范围内
    value = Math.max(3.0, Math.min(12.0, value))
    todayData.push({ timestamp, value: parseFloat(value.toFixed(1)) })
  }
  
  // 本周的数据 - 每天一个点，共7个点
  const weekData = []
  for (let i = 0; i < 7; i++) {
    const day = new Date()
    day.setDate(day.getDate() - day.getDay() + i) // 从本周日开始
    const timestamp = new Date(day.getFullYear(), day.getMonth(), day.getDate(), 12, 0, 0)
    // 生成一个4.0-9.0之间的随机值
    let value = 6.5 + Math.sin(i / 7 * Math.PI * 2) * 1.5 + (Math.random() - 0.5) * 1.0
    // 确保值在合理范围内
    value = Math.max(3.0, Math.min(12.0, value))
    weekData.push({ timestamp, value: parseFloat(value.toFixed(1)) })
  }
  
  return { todayData, weekData }
}

// 获取指定时间段的模拟数据
const getMockHistoryData = (period) => {
  if (!mockDataCache.value) {
    return []
  }
  
  const { todayData, weekData } = mockDataCache.value
  
  switch (period) {
    case 'today':
      return todayData
    case 'week':
      return weekData
    default:
      return todayData
  }
}

// 缓存生成的模拟数据
const mockDataCache = ref(null)

// 是否有数据显示
const hasData = ref(false)

// 页面显示时重新初始化图表
onShow(() => {
  // 重新生成模拟数据
  mockDataCache.value = generateMoreMockData()
  
  if (userRole.value === 'child_under_12') {
    // 重新初始化饼状图
    setTimeout(() => {
      initChildPieChart()
    }, 300)
  }
})

onMounted(() => {
  // 初始化数据
  simulateDataUpdate()
  
  // 生成并缓存模拟数据
  mockDataCache.value = generateMoreMockData()
  
  // 初始化图表
  setTimeout(() => {
    initChart()
    // 儿童模式下初始化饼状图
    if (userRole.value === 'child_under_12') {
      initChildPieChart()
      console.log('开始初始化儿童模式饼状图')
    }
  }, 1000) // 增加延时确保元素已经渲染
  
  // 设置定时刷新（每5秒模拟一次数据更新）
  refreshTimer = setInterval(() => {
    simulateDataUpdate()
    // 更新儿童模式饼状图
    if (userRole.value === 'child_under_12') {
      drawChildPieChart()
    }
  }, 5000)
  
  // 设置连接检查定时器
  connectionCheckTimer = setInterval(() => {
    dashboardStore.checkDataConnection()
  }, 60000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (connectionCheckTimer) clearInterval(connectionCheckTimer)
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  padding: 20rpx;
  transition: background-color 0.3s ease;
}

/* 警报横幅 */
.alert-banner {
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  animation: pulse 2s infinite;
}

.alert-banner.emergency {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
}

.alert-banner.warning {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white;
}

.alert-icon {
  font-size: 48rpx;
  margin-right: 16rpx;
}

.alert-text {
  font-size: 32rpx;
  font-weight: bold;
}

/* 数据中断横幅 */
.connection-lost-banner {
  background: #FEF3C7;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
}

.banner-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.banner-text {
  font-size: 28rpx;
  color: #92400E;
}

/* 状态区 */
.status-zone {
  background: white;
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.status-zone.status-emergency {
  border: 4rpx solid #EF4444;
  animation: shake 0.5s infinite;
}

.status-zone.status-alert {
  border: 4rpx solid #F59E0B;
}

.status-zone.status-normal {
  border: 4rpx solid #10B981;
}

/* 儿童模式 */
.child-mode {
  text-align: center;
}

.character-container {
  margin-bottom: 40rpx;
}

.character-emoji {
  font-size: 120rpx;
  display: block;
  margin-bottom: 20rpx;
}

.character-message {
  font-size: 36rpx;
  font-weight: bold;
  color: #374151;
}

.energy-bar-container {
  margin-top: 40rpx;
}

.energy-label {
  font-size: 28rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 16rpx;
}

.energy-bar {
  position: relative;
  height: 60rpx;
  background: linear-gradient(to right, #EF4444 0%, #F59E0B 25%, #10B981 50%, #F59E0B 75%, #EF4444 100%);
  border-radius: 30rpx;
  overflow: visible;
}

.energy-fill {
  height: 100%;
  border-radius: 30rpx;
  transition: width 0.5s ease;
}

.energy-indicator {
  position: absolute;
  top: -20rpx;
  transform: translateX(-50%);
  transition: left 0.5s ease;
}

.indicator-emoji {
  font-size: 60rpx;
  filter: drop-shadow(0 4rpx 8rpx rgba(0, 0, 0, 0.2));
}

.energy-range {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
}

.range-text {
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 正常模式 */
.normal-mode {
  text-align: center;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.status-label {
  font-size: 28rpx;
  color: #6B7280;
}

.last-update {
  font-size: 24rpx;
  color: #9CA3AF;
}

.glucose-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 20rpx;
}

.glucose-value {
  font-size: 120rpx;
  font-weight: bold;
  color: #1F2937;
}

.glucose-value.placeholder {
  color: #D1D5DB;
}

.glucose-unit {
  font-size: 32rpx;
  color: #6B7280;
  margin-left: 12rpx;
}

.trend-display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-arrow {
  font-size: 48rpx;
  margin-right: 12rpx;
}

.trend-text {
  font-size: 32rpx;
  color: #6B7280;
}

/* 目标区间指示器 */
.target-range-indicator {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.indicator-label {
  font-size: 28rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 16rpx;
}

.range-bar {
  position: relative;
  height: 40rpx;
  margin-bottom: 12rpx;
}

.range-background {
  height: 100%;
  background: #E5E7EB;
  border-radius: 20rpx;
  overflow: hidden;
}

.safe-zone {
  height: 100%;
  transition: all 0.3s ease;
}

.current-position {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: left 0.5s ease;
}

.position-dot {
  width: 32rpx;
  height: 32rpx;
  background: #3B82F6;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}

.position-dot.pulse {
  animation: pulse 1.5s infinite;
}

.range-labels {
  display: flex;
  justify-content: space-between;
}

.range-label {
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 儿童模式下的导航栏和历史数据折线图 */
.child-dashboard {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  width: 100%;
}

/* 顶部导航栏 */
.child-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  background: #FFFDF2;
  box-sizing: border-box;
  margin: 0;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #E3C7A4;
  position: relative;
  height: 100rpx;
}

.child-nav-left {
  display: flex;
  align-items: center;
  width: 60rpx;
}

.child-nav-back {
  width: 60rpx;
  height: 60rpx;
}

.child-nav-title {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 36rpx;
  font-weight: bold;
  color: #8B4513;
  white-space: nowrap;
  text-align: center;
  letter-spacing: 2rpx;
}

.child-nav-right {
  width: 60rpx;
}

.child-history-chart-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 30rpx;
  margin: 20rpx 4rpx 30rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  width: calc(100% - 8rpx);
  box-sizing: border-box;
}

.child-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.child-chart-title-container {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.child-chart-icon {
  width: 40rpx;
  height: 40rpx;
}

.child-chart-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.child-chart-period-selector {
  display: flex;
  gap: 16rpx;
}

.child-period-option {
  padding: 12rpx 28rpx;
  font-size: 26rpx;
  color: #8B4513;
  background: #F5E6D3;
  border-radius: 30rpx;
  transition: all 0.3s;
  margin-left: 10rpx;
  white-space: nowrap;
}

.child-period-active {
  background: #8CC152;
  color: #FFFFFF;
  font-weight: bold;
}

.child-chart-container {
  height: 380rpx;
  margin-bottom: 15rpx;
  position: relative;
  background-color: #FFFEF7;
  width: 100%;
  overflow: visible;
}

.child-chart-area {
  width: 100%;
  height: 100%;
  position: relative;
}

.child-no-data {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FFFEF7;
}

.child-no-data-text {
  font-size: 30rpx;
  color: #8B4513;
  opacity: 0.6;
}

.child-pie-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-data-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.no-data-text {
  font-size: 28rpx;
  color: #8B4513;
  opacity: 0.6;
}

.simple-pie-chart {
  position: relative;
  width: 150px;
  height: 150px;
}

.pie-slice {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: #FFFEF7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #E3C7A4;
}

.pie-text {
  font-size: 12px;
  font-weight: bold;
  color: #8B4513;
  text-align: center;
}

.child-chart-legend {
  display: flex;
  justify-content: center;
  gap: 30rpx;
  margin-top: 40rpx;
}

.child-legend-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.child-legend-color {
  width: 30rpx;
  height: 30rpx;
  border-radius: 50%;
}

.child-legend-good {
  background: #8CC152;
}

.child-legend-low {
  background: #F5D76E;
}

.child-legend-high {
  background-color: #FF9AAA;
}

/* 折线图卡片样式 */
.child-line-chart-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 30rpx;
  margin: 20rpx 4rpx 30rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  width: calc(100% - 8rpx);
  box-sizing: border-box;
}

/* 雷达图卡片样式 */
.child-radar-chart-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 30rpx;
  margin: 20rpx 4rpx 30rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  width: calc(100% - 8rpx);
  box-sizing: border-box;
}

/* 折线图容器 */
.child-line-chart {
  width: 100%;
  height: 350rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 雷达图容器 */
.child-radar-chart {
  width: 100%;
  height: 350rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* SVG图表样式 */
.child-line-chart-svg,
.child-radar-chart-svg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.line-chart-svg,
.radar-chart-svg {
  width: 100%;
  height: 100%;
  border-radius: 8rpx;
  background: #FFFEF7;
}

.child-legend-text {
  font-size: 28rpx;
  color: #602F27;
  font-weight: 500;
}

/* 小仓鼠的话 */
.child-hamster-words-card {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  margin: 30rpx 0;
  padding: 0 10rpx;
}

.child-hamster-avatar-small {
  width: 100rpx;
  height: 100rpx;
  flex-shrink: 0;
  background: #F6CD75;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #E3C7A4;
}

.child-hamster-img {
  width: 80rpx;
  height: 80rpx;
}

.child-words-bubble {
  position: relative;
  background: #FFFEF7;
  border: 3rpx solid #E3C7A4;
  border-radius: 20rpx;
  padding: 20rpx;
  flex: 1;
  box-shadow: 0 4rpx 12rpx rgba(96, 47, 39, 0.1);
}

.child-words-text {
  font-size: 28rpx;
  color: #602F27;
  line-height: 1.5;
}

.child-bubble-tail {
  position: absolute;
  left: -12rpx;
  top: 30rpx;
  width: 0;
  height: 0;
  border-top: 12rpx solid transparent;
  border-bottom: 12rpx solid transparent;
  border-right: 12rpx solid #E3C7A4;
}

.child-bubble-tail::after {
  content: '';
  position: absolute;
  left: 3rpx;
  top: -9rpx;
  width: 0;
  height: 0;
  border-top: 9rpx solid transparent;
  border-bottom: 9rpx solid transparent;
  border-right: 9rpx solid #FFFEF7;
}

.child-bottom-spacer {
  height: 100rpx;
}

/* 图表区 */
.chart-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.chart-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.time-tabs {
  display: flex;
  gap: 12rpx;
}

.time-tab {
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  color: #6B7280;
  background: #F3F4F6;
  border-radius: 12rpx;
}

.time-tab.active {
  color: white;
  background: #3B82F6;
}

.chart-container {
  position: relative;
  height: 400rpx;
}

.glucose-chart {
  width: 100%;
  height: 100%;
}

.event-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
}

.event-marker {
  position: absolute;
  top: 20rpx;
  transform: translateX(-50%);
  pointer-events: all;
}

.event-icon {
  font-size: 40rpx;
}

/* 统计区 */
.stats-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
}

.stat-label {
  font-size: 24rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
}

/* 建议区 */
.suggestion-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.suggestion-section.suggestion-emergency {
  background: #FEE2E2;
  border: 2rpx solid #EF4444;
}

.suggestion-section.suggestion-warning {
  background: #FEF3C7;
  border: 2rpx solid #F59E0B;
}

.suggestion-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.suggestion-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.suggestion-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.suggestion-text {
  font-size: 28rpx;
  color: #4B5563;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.action-button {
  width: 100%;
  padding: 24rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: bold;
  border: none;
}

.action-button.suggestion-emergency {
  background: #EF4444;
  color: white;
}

.action-button.suggestion-warning {
  background: #F59E0B;
  color: white;
}

.action-button.suggestion-info {
  background: #3B82F6;
  color: white;
}

/* 添加记录按钮 */
.add-record-btn {
  position: fixed;
  bottom: 100rpx;
  right: 40rpx;
  width: 140rpx;
  height: 140rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.4);
  z-index: 100;
}

.add-icon {
  font-size: 60rpx;
  color: white;
  font-weight: bold;
  line-height: 1;
}

.add-text {
  font-size: 20rpx;
  color: white;
  margin-top: 4rpx;
}

/* 底部占位 */
.bottom-spacer {
  height: 120rpx;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10rpx);
  }
  75% {
    transform: translateX(10rpx);
  }
}

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-dashboard {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 24rpx;
  padding-bottom: 40rpx;
}

/* 顶部区域 */
.child-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  margin-bottom: 24rpx;
}

.header-decoration {
  display: flex;
  gap: 8rpx;
}

.deco-star {
  font-size: 36rpx;
  animation: twinkle 2s ease-in-out infinite;
}

.deco-star.delay {
  animation-delay: 1s;
}

@keyframes twinkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.8); }
}

.greeting-section {
  text-align: center;
}

.greeting-text {
  font-size: 28rpx;
  color: #B8860B;
  display: block;
}

.child-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #8B4513;
  display: block;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  padding: 12rpx 20rpx;
  border-radius: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(255, 165, 0, 0.3);
}

.badge-icon {
  font-size: 32rpx;
}

.badge-count {
  font-size: 28rpx;
  font-weight: bold;
  color: white;
}

/* 主角色卡片 */
.mascot-card {
  position: relative;
  background: white;
  border-radius: 40rpx;
  padding: 40rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(139, 69, 19, 0.1);
  overflow: hidden;
  border: 4rpx solid #FFE4B5;
}

.mascot-card.status-good {
  border-color: #90EE90;
}

.mascot-card.status-warning {
  border-color: #FFD700;
}

.mascot-card.status-danger {
  border-color: #FF6B6B;
  animation: cardPulse 2s infinite;
}

@keyframes cardPulse {
  0%, 100% { box-shadow: 0 8rpx 32rpx rgba(255, 107, 107, 0.2); }
  50% { box-shadow: 0 8rpx 48rpx rgba(255, 107, 107, 0.4); }
}

.mascot-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.bg-circle.c1 {
  width: 200rpx;
  height: 200rpx;
  background: #FFD700;
  top: -50rpx;
  right: -50rpx;
}

.bg-circle.c2 {
  width: 150rpx;
  height: 150rpx;
  background: #FFA500;
  bottom: -30rpx;
  left: -30rpx;
}

.bg-circle.c3 {
  width: 100rpx;
  height: 100rpx;
  background: #FFE4B5;
  top: 50%;
  right: 20%;
}

.mascot-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.mascot-avatar {
  margin-bottom: 24rpx;
}

.mascot-avatar.bounce {
  animation: bounce 2s ease-in-out infinite;
}

.mascot-avatar.shake {
  animation: mascotShake 0.5s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}

@keyframes mascotShake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}

.avatar-emoji {
  font-size: 140rpx;
  display: block;
  filter: drop-shadow(0 8rpx 16rpx rgba(0, 0, 0, 0.1));
}

.mascot-speech {
  width: 100%;
}

.speech-bubble {
  background: linear-gradient(135deg, #FFF8E7 0%, #FFFBF0 100%);
  border: 3rpx solid #FFE4B5;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  position: relative;
}

.speech-bubble::before {
  content: '';
  position: absolute;
  top: -20rpx;
  left: 50%;
  transform: translateX(-50%);
  border-left: 20rpx solid transparent;
  border-right: 20rpx solid transparent;
  border-bottom: 20rpx solid #FFE4B5;
}

.speech-bubble::after {
  content: '';
  position: absolute;
  top: -16rpx;
  left: 50%;
  transform: translateX(-50%);
  border-left: 18rpx solid transparent;
  border-right: 18rpx solid transparent;
  border-bottom: 18rpx solid #FFF8E7;
}

.speech-text {
  font-size: 30rpx;
  color: #8B4513;
  text-align: center;
  line-height: 1.6;
}

.status-indicator-child {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-top: 24rpx;
}

.status-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
}

.status-dot.status-good {
  background: #4ADE80;
  box-shadow: 0 0 12rpx rgba(74, 222, 128, 0.5);
}

.status-dot.status-warning {
  background: #FBBF24;
  box-shadow: 0 0 12rpx rgba(251, 191, 36, 0.5);
}

.status-dot.status-danger {
  background: #F87171;
  box-shadow: 0 0 12rpx rgba(248, 113, 113, 0.5);
  animation: dotPulse 1s infinite;
}

@keyframes dotPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.status-text-child {
  font-size: 26rpx;
  color: #A0522D;
  font-weight: 500;
}

/* 能量仪表盘 */
.energy-dashboard {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(139, 69, 19, 0.08);
  border: 3rpx solid #FFE4B5;
}

.energy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.energy-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #8B4513;
}

.energy-time {
  font-size: 24rpx;
  color: #D2691E;
}

.energy-meter {
  position: relative;
  padding-bottom: 40rpx;
}

.meter-track {
  display: flex;
  height: 48rpx;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: inset 0 4rpx 8rpx rgba(0, 0, 0, 0.1);
}

.meter-zone {
  flex: 1;
}

.meter-zone.low-zone {
  background: linear-gradient(90deg, #FFA07A 0%, #FFD700 100%);
}

.meter-zone.good-zone {
  background: linear-gradient(90deg, #90EE90 0%, #98FB98 100%);
}

.meter-zone.high-zone {
  background: linear-gradient(90deg, #FFD700 0%, #FFA07A 100%);
}

.meter-pointer {
  position: absolute;
  top: -16rpx;
  transform: translateX(-50%);
  transition: left 0.5s ease;
  z-index: 10;
}

.pointer-head {
  background: white;
  border-radius: 50%;
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.2);
  border: 4rpx solid #FFD700;
}

.pointer-emoji {
  font-size: 40rpx;
}

.pointer-line {
  width: 4rpx;
  height: 20rpx;
  background: #FFD700;
  margin: 0 auto;
}

.meter-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
  padding: 0 8rpx;
}

.meter-label {
  font-size: 24rpx;
  color: #CD853F;
}

.meter-label.good {
  color: #228B22;
  font-weight: bold;
}

/* 今日任务卡片 */
.tasks-card {
  background: white;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(139, 69, 19, 0.08);
  border: 3rpx solid #FFE4B5;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.tasks-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #8B4513;
}

.tasks-progress {
  font-size: 28rpx;
  color: #D2691E;
  font-weight: 600;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 24rpx;
  background: #FFFBF0;
  border-radius: 20rpx;
  border: 2rpx solid #FFE4B5;
  transition: all 0.3s ease;
}

.task-item.completed {
  background: linear-gradient(135deg, #F0FFF0 0%, #E8FFE8 100%);
  border-color: #90EE90;
}

.task-check {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  font-size: 40rpx;
}

.check-empty {
  width: 40rpx;
  height: 40rpx;
  border: 4rpx solid #DEB887;
  border-radius: 50%;
  background: white;
}

.task-icon {
  font-size: 36rpx;
}

.task-name {
  flex: 1;
  font-size: 28rpx;
  color: #8B4513;
}

.task-item.completed .task-name {
  color: #228B22;
}

.task-star {
  font-size: 32rpx;
  animation: starPop 0.5s ease;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

/* 奖励进度卡片 */
.reward-card {
  background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%);
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(255, 215, 0, 0.2);
  border: 3rpx solid #FFD700;
}

.reward-header {
  margin-bottom: 24rpx;
}

.reward-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #B8860B;
}

.reward-progress {
  position: relative;
  margin-bottom: 20rpx;
}

.progress-track {
  height: 32rpx;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: inset 0 2rpx 6rpx rgba(0, 0, 0, 0.1);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
  border-radius: 16rpx;
  transition: width 0.5s ease;
}

.progress-milestones {
  position: absolute;
  top: -8rpx;
  left: 0;
  right: 0;
  height: 48rpx;
}

.milestone {
  position: absolute;
  transform: translateX(-50%);
  transition: all 0.3s ease;
}

.milestone-icon {
  font-size: 40rpx;
  filter: grayscale(0.8);
  opacity: 0.5;
}

.milestone.reached .milestone-icon {
  filter: grayscale(0);
  opacity: 1;
  animation: milestoneReached 0.5s ease;
}

@keyframes milestoneReached {
  0% { transform: scale(1); }
  50% { transform: scale(1.4); }
  100% { transform: scale(1); }
}

.reward-hint {
  font-size: 26rpx;
  color: #B8860B;
  text-align: center;
  display: block;
}

/* 提示卡片 */
.tip-card {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 28rpx;
  margin-bottom: 24rpx;
}

.tip-card.tip-normal {
  background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
  border: 3rpx solid #80DEEA;
}

.tip-card.tip-warning {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
  border: 3rpx solid #FFD54F;
}

.tip-card.tip-danger {
  background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
  border: 3rpx solid #EF9A9A;
  animation: tipPulse 2s infinite;
}

@keyframes tipPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

.tip-icon-wrap {
  width: 80rpx;
  height: 80rpx;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.tip-icon {
  font-size: 48rpx;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #5D4037;
  display: block;
  margin-bottom: 8rpx;
}

.tip-text {
  font-size: 26rpx;
  color: #795548;
  line-height: 1.5;
}

.tip-action {
  background: linear-gradient(135deg, #FF8A65 0%, #FF7043 100%);
  padding: 16rpx 28rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(255, 112, 67, 0.3);
}

.action-text {
  font-size: 26rpx;
  color: white;
  font-weight: 600;
}

/* 今日成就 */
.achievement-card {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
}

.achievement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.achievement-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.achievement-count {
  font-size: 24rpx;
  color: #A85835;
  background: #F6D387;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
}

.achievement-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
  border: 2rpx solid #E3C7A4;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.achievement-item.unlocked {
  opacity: 1;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-color: #F59E0B;
}

.achievement-icon-wrap {
  position: relative;
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.achievement-icon {
  font-size: 40rpx;
}

.unlock-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  font-size: 20rpx;
  animation: sparkle 2s infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.2) rotate(180deg); }
}

.achievement-info {
  flex: 1;
}

.achievement-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #602F27;
  display: block;
  margin-bottom: 4rpx;
}

.achievement-desc {
  font-size: 24rpx;
  color: #8E422F;
}

/* 健康数据卡片 */
.health-data-card {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
}

.health-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.health-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.health-date {
  font-size: 24rpx;
  color: #A85835;
}

.health-stats {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.health-stat-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
  border: 2rpx solid #E3C7A4;
}

.stat-icon-wrap {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrap.good {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
}

.stat-icon-wrap.warning {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
}

.stat-icon {
  font-size: 32rpx;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 24rpx;
  color: #8E422F;
  display: block;
  margin-bottom: 4rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #602F27;
}

/* 小仓鼠的话 */
.hamster-words-card {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.hamster-avatar-small {
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
}

.hamster-img {
  width: 100%;
  height: 100%;
}

.words-bubble {
  position: relative;
  background: #FFFEF7;
  border: 3rpx solid #E3C7A4;
  border-radius: 20rpx;
  padding: 20rpx;
  flex: 1;
  box-shadow: 0 4rpx 12rpx rgba(96, 47, 39, 0.1);
}

.words-text {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.5;
}

.bubble-tail {
  position: absolute;
  left: -12rpx;
  top: 24rpx;
  width: 0;
  height: 0;
  border-top: 12rpx solid transparent;
  border-bottom: 12rpx solid transparent;
  border-right: 12rpx solid #E3C7A4;
}

.bubble-tail::after {
  content: '';
  position: absolute;
  left: 3rpx;
  top: -9rpx;
  width: 0;
  height: 0;
  border-top: 9rpx solid transparent;
  border-bottom: 9rpx solid transparent;
  border-right: 9rpx solid #FFFEF7;
}

/* 快捷功能 */
.quick-actions-card {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
}

.actions-header {
  margin-bottom: 20rpx;
}

.actions-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx;
  background: #FAF6F0;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  transition: all 0.3s ease;
}

.action-item:active {
  transform: scale(0.95);
  background: #F6D387;
}

.action-icon-wrap {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  width: 48rpx;
  height: 48rpx;
}

.action-name {
  font-size: 24rpx;
  color: #602F27;
  font-weight: 500;
  text-align: center;
}

/* 底部装饰 */
.bottom-decoration {
  text-align: center;
  margin-top: 40rpx;
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.deco-cheese {
  font-size: 48rpx;
  animation: float 3s ease-in-out infinite;
  animation-delay: var(--delay, 0s);
}

.deco-cheese:nth-child(2) {
  --delay: 1s;
}

.deco-cheese:nth-child(3) {
  --delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}
</style>
