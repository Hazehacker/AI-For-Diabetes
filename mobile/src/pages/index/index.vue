<template>
  <view class="page-container">
  <!-- 儿童模式：奶酪仓鼠风格 -->
  <view v-if="userRole === 'child_under_12'" class="child-home">
    <!-- 顶部装饰背景 -->
    <view class="child-header-bg">
      <view class="header-clouds">
        <text class="cloud c1">☁️</text>
        <text class="cloud c2">☁️</text>
      </view>
    </view>
    
    <!-- 顶部区域 -->
    <view class="child-header">
      <view class="welcome-image-wrapper">
        <image class="welcome-image" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
      </view>
      <view class="header-content">
        <view class="welcome-text-center">
          <text class="child-greeting">{{ greetingText }}</text>
          <text class="child-name">{{ userInfo.nickname || '小朋友' }}</text>
        </view>
        <view class="header-right">
          <view class="pot-image-wrapper">
            <image class="pot-image" src="/static/ch/ch_index_pot.png" mode="aspectFit"></image>
          </view>
          <view class="star-badge">
            <image class="star-icon" src="/static/ch/ch_index_star.png" mode="aspectFit"></image>
            <text class="star-count">{{ dailyStars }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 吉祥物主卡片 -->
    <view class="mascot-main-card" :class="childStatusClass">
      <!-- 装饰元素 -->
      <view class="cute-decoration">
        <text class="cute-star s1">⭐</text>
        <text class="cute-star s2">✨</text>
        <text class="cute-heart">💕</text>
        <text class="cute-sparkle">🌟</text>
      </view>
      
      <!-- 三只猫咪图片 -->
      <view class="three-cats-wrapper">
        <image class="three-cats-image" src="/static/ch/ch_index_3cat.png" mode="aspectFit"></image>
      </view>
      
      <!-- 可爱的消息气泡 -->
      <view class="cute-message-bubble">
        <view class="bubble-tail"></view>
        <text class="bubble-text">{{ mascotMessage }}</text>
      </view>
      
      <!-- 状态徽章 -->
      <view class="cute-status-badge" :class="childStatusClass">
        <view class="status-icon"></view>
        <text class="status-text">{{ childStatusText }}</text>
      </view>
    </view>

    <!-- 能量仪表盘卡片 -->
    <view class="energy-dashboard-card">
      <!-- 装饰元素 -->
      <view class="dashboard-decoration">
        <text class="dash-star d1">⚡</text>
        <text class="dash-star d2">✨</text>
      </view>
      
      <view class="dashboard-header">
        <view class="dashboard-title">
          <image class="energy-icon" src="/static/ch/ch_index_battery&cat.png" mode="aspectFit"></image>
          <text class="energy-text">我的能量</text>
        </view>
        <text class="dashboard-time">{{ currentTime }}</text>
      </view>
      
      <!-- Ant Design 风格仪表盘 -->
      <view class="ant-gauge">
        <view class="gauge-content">
          <view class="gauge-wrapper">
          <!-- SVG 仪表盘 -->
          <svg class="gauge-svg" viewBox="0 0 200 120">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#30BF78;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#FAAD14;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#F4664A;stop-opacity:1" />
              </linearGradient>
              <!-- 指针阴影滤镜 -->
              <filter id="pointerShadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#333333" flood-opacity="0.3"/>
              </filter>
              <!-- 轴心阴影滤镜 -->
              <filter id="pinShadow" x="-100%" y="-100%" width="300%" height="300%">
                <feDropShadow dx="2" dy="2" stdDeviation="4" flood-color="#333333" flood-opacity="0.4"/>
              </filter>
            </defs>
            <!-- 背景弧线 -->
            <path 
              class="gauge-bg"
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#E8E8E8"
              stroke-width="18"
              stroke-linecap="round"
            />
            <!-- 进度弧线 -->
            <path 
              class="gauge-progress"
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="url(#gaugeGradient)"
              stroke-width="18"
              stroke-linecap="round"
              :stroke-dasharray="gaugeCircumference"
              :stroke-dashoffset="gaugeOffset"
            />
            <!-- 指针 (Ant Design 风格) -->
            <g :transform="`rotate(${gaugePointerAngle}, 100, 100)`" filter="url(#pointerShadow)">
              <!-- 指针主体 -->
              <polygon 
                points="100,28 97,95 100,100 103,95"
                fill="#c5c5c5"
                stroke="#c5c5c5"
                stroke-width="1"
                stroke-linejoin="round"
              />
            </g>
            <!-- 轴心 (Ant Design 风格) -->
            <g filter="url(#pinShadow)">
              <circle cx="100" cy="100" r="10" fill="#d5d5d5" stroke="#d5d5d5" stroke-width="2"/>
              <circle cx="100" cy="100" r="5" fill="#ffffff"/>
            </g>
          </svg>
          </view>
          
          <!-- 右侧颜色条图例 -->
          <view class="gauge-color-bar">
            <view class="color-bar-item">
              <view class="color-bar-segment" style="background: #F4664A;"></view>
              <text class="color-bar-label">能量高</text>
            </view>
            <view class="color-bar-item">
              <view class="color-bar-segment" style="background: #FAAD14;"></view>
              <text class="color-bar-label">刚刚好</text>
            </view>
            <view class="color-bar-item">
              <view class="color-bar-segment" style="background: #30BF78;"></view>
              <text class="color-bar-label">能量低</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 今日任务 -->
    <view class="tasks-card-child">
      <view class="tasks-card-header">
        <view class="tasks-title">
          <image class="tasks-title-icon" src="/static/ch/ch_index_plan.png" mode="aspectFit"></image>
          <text class="tasks-title-text">今日小任务</text>
        </view>
        <text class="tasks-count">{{ completedTasks }}/{{ totalTasks }}</text>
      </view>
      <view class="tasks-list-child">
        <view 
          v-for="task in childTasks" 
          :key="task.id"
          class="task-item-child"
          :class="{ done: task.completed }"
          @tap="toggleTask(task)"
        >
          <view class="task-checkbox">
            <image v-if="task.completed" class="task-finish-icon" src="/static/ch/ch_index_finish.png" mode="aspectFit"></image>
            <view v-else class="checkbox-empty"></view>
          </view>
          <image class="task-icon-img" src="/static/ch/ch_index_plan.png" mode="aspectFit"></image>
          <text class="task-text">{{ task.name }}</text>
          <image v-if="task.completed" class="task-reward-img" src="/static/ch/ch_index_star.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="child-menu-grid">
      <view class="child-menu-item" @tap="goToCompanion">
        <view class="menu-icon-wrap companion">
          <image class="menu-icon-img" src="/static/ch/ch_index_friend.png" mode="aspectFit"></image>
        </view>
        <text class="menu-name">找朋友</text>
      </view>
      <view class="child-menu-item" @tap="goToInteraction">
        <view class="menu-icon-wrap game">
          <image class="menu-icon-img" src="/static/ch/ch_index_play.png" mode="aspectFit"></image>
        </view>
        <text class="menu-name">游乐园</text>
      </view>
      <view class="child-menu-item" @tap="goToCalories">
        <view class="menu-icon-wrap food">
          <image class="menu-icon-img" src="/static/ch/ch_index_eat.png" mode="aspectFit"></image>
        </view>
        <text class="menu-name">吃什么</text>
      </view>
      <view class="child-menu-item" @tap="goToDashboard">
        <view class="menu-icon-wrap chart">
          <image class="menu-icon-img" src="/static/ch/ch_index_bar.png" mode="aspectFit"></image>
        </view>
        <text class="menu-name">看数据</text>
      </view>
    </view>

    <!-- 提示卡片 -->
    <view class="tip-card-child" :class="tipClass">
      <view class="tip-content-child">
        <text class="tip-title-child">{{ tipTitle }}</text>
        <text class="tip-text-child">{{ tipText }}</text>
      </view>
    </view>

    <!-- 底部装饰 -->
    <view class="child-footer-deco">
      <image class="footer-cat-cloud" src="/static/ch/ch_index_cat&cloud.png" mode="aspectFit"></image>
    </view>
    
    <view class="bottom-spacer"></view>
  </view>

  <!-- 家长模式：现代简洁风格 -->
  <view v-else-if="userRole === 'guardian'" class="guardian-home">
    <!-- 顶部欢迎区 -->
    <view class="guardian-header">
      <view class="guardian-welcome">
        <view class="guardian-avatar-wrapper">
          <image class="guardian-avatar" src="/static/logo.png" mode="aspectFit"></image>
        </view>
        <view class="guardian-welcome-text">
          <text class="guardian-greeting">{{ greetingText }}</text>
          <text class="guardian-name">{{ userInfo.nickname ? userInfo.nickname + '家长' : '家长' }}</text>
        </view>
      </view>
    </view>

    <!-- 任务提醒卡片 -->
    <view class="guardian-notification-card">
      <view class="notification-icon-wrapper">
        <text class="notification-icon">📋</text>
      </view>
      <view class="notification-content">
        <text class="notification-title">孩子有 {{ todayTasksCount }} 个任务待处理</text>
        <text class="notification-desc">查看今日健康计划</text>
      </view>
    </view>

    <!-- 仪表盘核心区域 -->
    <view class="guardian-dashboard-section">
      <!-- 当前血糖状态 -->
      <view class="guardian-glucose-card" :class="statusColor">
        <view class="guardian-status-header">
          <text class="guardian-status-label">孩子当前血糖</text>
          <text class="guardian-status-time">{{ currentTime }}</text>
        </view>
        <view class="guardian-status-value-area">
          <text class="guardian-glucose-value">{{ currentGlucose.value }}</text>
          <text class="guardian-glucose-unit">mmol/L</text>
        </view>
        <text class="guardian-status-text">{{ statusText }}</text>
      </view>

      <!-- 血糖曲线图 -->
      <view class="guardian-chart-card">
        <view class="guardian-card-header">
          <text class="guardian-card-title">孩子今日血糖趋势</text>
          <text class="guardian-view-more" @tap="goToDashboard">查看详情 →</text>
        </view>
        <GlucoseCurveChart canvas-id="guardianGlucoseChart" :compact="true" />
      </view>

      <!-- 每日统计 -->
      <view class="guardian-stats-grid">
        <view class="guardian-stat-item">
          <text class="guardian-stat-value">{{ stats.avgGlucose }}</text>
          <text class="guardian-stat-label">孩子平均值</text>
        </view>
        <view class="guardian-stat-item">
          <text class="guardian-stat-value">{{ stats.timeInRange }}%</text>
          <text class="guardian-stat-label">孩子达标率</text>
        </view>
        <view class="guardian-stat-item">
          <text class="guardian-stat-value">{{ stats.measureCount }}</text>
          <text class="guardian-stat-label">孩子测量次数</text>
        </view>
      </view>
    </view>

    <!-- 健康计划卡片 -->
    <view class="guardian-projects-section">
      <view class="guardian-section-header">
        <text class="guardian-section-title">孩子的健康计划</text>
        <text class="guardian-see-all" @tap="goToHealthPlan">查看全部 >></text>
      </view>
      <view class="guardian-project-card" @tap="goToHealthPlan">
        <view class="guardian-project-content">
          <text class="guardian-project-title">孩子血糖管理计划</text>
          <text class="guardian-project-subtitle">日常监测</text>
        </view>
        <view class="guardian-project-progress">
          <view class="guardian-progress-ring">
            <text class="guardian-progress-text">57%</text>
          </view>
        </view>
        <view class="guardian-project-members">
          <view class="guardian-member-avatar"></view>
          <view class="guardian-member-avatar"></view>
          <view class="guardian-member-avatar guardian-member-more">+5</view>
        </view>
      </view>
    </view>

    

    <!-- 底部占位 -->
    <view class="bottom-spacer"></view>
  </view>

  <!-- 青少年模式 -->
  <view v-else class="home-page">
    <!-- 顶部欢迎区 -->
    <view class="welcome-header">
      <view class="welcome-text">
        <text class="greeting">{{ greetingText }}</text>
        <text class="username">{{ userInfo.nickname || '用户' }}</text>
      </view>
      <view class="role-badge" :class="'role-' + userRole">
        <text class="role-text">{{ roleText }}</text>
      </view>
    </view>

    <!-- 仪表盘核心区域 -->
    <view class="dashboard-section">
      <!-- 当前血糖状态 -->
      <view class="glucose-status-card" :class="statusColor">
        <view class="status-header">
          <text class="status-label">当前血糖</text>
          <text class="status-time">{{ currentTime }}</text>
        </view>
        <view class="status-value-area">
          <text class="glucose-value">{{ currentGlucose.value }}</text>
          <text class="glucose-unit">mmol/L</text>
        </view>
        <text class="status-text">{{ statusText }}</text>
      </view>

      <!-- 血糖曲线图 -->
      <view class="chart-card">
        <view class="card-header">
          <text class="card-title">今日血糖趋势</text>
          <text class="view-more" @tap="goToDashboard">查看详情 →</text>
        </view>
        <GlucoseCurveChart canvas-id="homeGlucoseChart" :compact="true" />
      </view>

      <!-- 每日统计 -->
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ stats.avgGlucose }}</text>
          <text class="stat-label">平均值</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.timeInRange }}%</text>
          <text class="stat-label">达标率</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.measureCount }}</text>
          <text class="stat-label">测量次数</text>
        </view>
      </view>
    </view>

    <!-- 同伴板块入口 -->
    <view class="section-card companion-card" @tap="goToCompanion">
      <view class="card-icon-area">
        <text class="card-icon">👥</text>
      </view>
      <view class="card-content">
        <text class="card-title">同伴板块</text>
        <text class="card-desc">与小伙伴一起分享经验</text>
        <view class="preview-tags">
          <text class="preview-tag">3条新动态</text>
          <text class="preview-tag">5人在线</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 互动板块入口 -->
    <view class="section-card interaction-card" @tap="goToInteraction">
      <view class="card-icon-area">
        <text class="card-icon">🎮</text>
      </view>
      <view class="card-content">
        <text class="card-title">互动板块</text>
        <text class="card-desc">参与挑战，赢取奖励</text>
        <view class="preview-tags">
          <text class="preview-tag">2个新挑战</text>
          <text class="preview-tag">积分排行</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 热量板块入口 -->
    <view class="section-card calories-card" @tap="goToCalories">
      <view class="card-icon-area">
        <text class="card-icon">🍱</text>
      </view>
      <view class="card-content">
        <text class="card-title">热量板块</text>
        <text class="card-desc">记录饮食，智能推荐食谱</text>
        <view class="preview-tags">
          <text class="preview-tag">热量记录</text>
          <text class="preview-tag">食谱推荐</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-spacer"></view>
  </view>
  
  <!-- 自定义 TabBar -->
  <CustomTabBar :current="0" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { useGlucoseCurveStore } from '@/store/glucoseCurve'
import { useUserStore } from '@/store/user'
import { storeToRefs } from 'pinia'
import GlucoseCurveChart from '@/components/GlucoseCurveChart.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'

const dashboardStore = useDashboardStore()
const glucoseCurveStore = useGlucoseCurveStore()
const userStore = useUserStore()

const { currentGlucose, stats, userRole } = storeToRefs(dashboardStore)
const { userInfo } = storeToRefs(userStore)
const { statusColor, trendArrow } = dashboardStore

// 当前时间
const currentTime = ref('')

// 问候语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 角色文本
const roleText = computed(() => {
  const map = {
    'child_under_12': '儿童模式',
    'teen_above_12': '青少年模式',
    'guardian': '家属模式'
  }
  return map[userRole.value] || '用户'
})

// 状态文本
const statusText = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9) return '血糖偏低，请注意'
  if (value > 10.0) return '血糖偏高，请注意'
  if (value > 7.8) return '血糖略高'
  return '血糖正常'
})

// ========== 儿童模式相关 ==========
const dailyStars = ref(3)

// 儿童状态类
const childStatusClass = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return 'status-danger'
  if (value < 4.4 || value > 9.0) return 'status-warning'
  return 'status-good'
})

const isGoodStatus = computed(() => childStatusClass.value === 'status-good')
const isBadStatus = computed(() => childStatusClass.value === 'status-danger')

// 吉祥物消息
const mascotMessage = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9) return '能量不够啦！快吃点小零食补充能量吧~'
  if (value > 10.0) return '能量太多啦！我们去活动活动吧~'
  if (value < 4.4 || value > 9.0) return '要注意一下哦，小仓鼠在关注你~'
  return '太棒了！你的能量刚刚好，继续保持哦！'
})

// 儿童状态文本
const childStatusText = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return '需要注意'
  if (value < 4.4 || value > 9.0) return '稍微注意'
  return '状态很好'
})

// 能量位置
const energyPosition = computed(() => {
  const value = currentGlucose.value.value || 6
  const minVal = 2.0
  const maxVal = 15.0
  const percentage = ((value - minVal) / (maxVal - minVal)) * 100
  return Math.max(5, Math.min(95, percentage))
})

// Ant Design Gauge 相关计算属性
const gaugeCircumference = computed(() => {
  // 半圆弧长 = π * r = 3.14159 * 80 ≈ 251
  return 251
})

const gaugeOffset = computed(() => {
  // 根据能量位置计算偏移量
  const progress = energyPosition.value / 100
  return gaugeCircumference.value * (1 - progress)
})

const gaugePointerAngle = computed(() => {
  // 将能量位置映射到 -90° 到 90° 的范围
  const progress = energyPosition.value / 100
  return -90 + (progress * 180)
})

const gaugeColor = computed(() => {
  const pos = energyPosition.value
  if (pos < 30) return '#F4664A'
  if (pos < 70) return '#FAAD14'
  return '#30BF78'
})

// 能量状态文本
const energyStatus = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return '需要注意'
  if (value < 4.4 || value > 9.0) return '稍微注意'
  return '状态良好'
})

// 指针表情
const pointerFace = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return '😰'
  if (value < 4.4 || value > 9.0) return '😟'
  return '😊'
})

// 儿童任务
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

// 提示卡片
const tipClass = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return 'tip-danger'
  if (value < 4.4 || value > 9.0) return 'tip-warning'
  return 'tip-normal'
})

const tipIcon = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return '🚨'
  if (value < 4.4 || value > 9.0) return '⚠️'
  return '💡'
})

const tipTitle = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9 || value > 10.0) return '小仓鼠提醒'
  if (value < 4.4 || value > 9.0) return '温馨提示'
  return '小贴士'
})

const tipText = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9) return '快告诉爸爸妈妈，吃点糖果补充能量吧！'
  if (value > 10.0) return '能量太多了，去跑跑跳跳消耗一下吧！'
  if (value < 4.4 || value > 9.0) return '注意观察，如果不舒服要告诉大人哦~'
  return '保持好心情，多喝水，按时吃饭，你是最棒的！'
})

// 更新时间
const updateTime = () => {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

// 跳转到完整仪表盘
const goToDashboard = () => {
  uni.navigateTo({
    url: '/pages/dashboard/dashboard'
  })
}

// 跳转到同伴板块
const goToCompanion = () => {
  uni.navigateTo({
    url: '/pages/community/companion'
  })
}

// 跳转到互动板块
const goToInteraction = () => {
  uni.navigateTo({
    url: '/pages/community/interaction'
  })
}

// 跳转到热量板块
const goToCalories = () => {
  uni.navigateTo({
    url: '/pages/calories/index'
  })
}

// 跳转到健康计划
const goToHealthPlan = () => {
  uni.navigateTo({
    url: '/pages/health-plan/index'
  })
}

// 家长模式任务数量
const todayTasksCount = ref(2)

onMounted(() => {
  updateTime()
  setInterval(updateTime, 60000)
  
  // 生成模拟数据
  dashboardStore.generateMockData()
  
  // 同步数据到血糖曲线组件
  glucoseCurveStore.syncFromDashboard()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 50%, #F3F4F6 50%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 欢迎区 */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 20rpx;
}

.welcome-text {
  display: flex;
  flex-direction: column;
}

.greeting {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8rpx;
}

.username {
  font-size: 40rpx;
  font-weight: bold;
  color: white;
}

.role-badge {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10rpx);
}

.role-text {
  font-size: 24rpx;
  color: white;
}

/* 仪表盘区域 */
.dashboard-section {
  margin-bottom: 32rpx;
}

/* 血糖状态卡片 */
.glucose-status-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.glucose-status-card.status-normal {
  border-left: 8rpx solid #10B981;
}

.glucose-status-card.status-warning {
  border-left: 8rpx solid #F59E0B;
}

.glucose-status-card.status-danger {
  border-left: 8rpx solid #EF4444;
}

.status-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.status-label {
  font-size: 28rpx;
  color: #6B7280;
}

.status-time {
  font-size: 24rpx;
  color: #9CA3AF;
}

.status-value-area {
  display: flex;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.glucose-value {
  font-size: 80rpx;
  font-weight: bold;
  color: #1F2937;
  line-height: 1;
}

.glucose-unit {
  font-size: 28rpx;
  color: #6B7280;
  margin-left: 12rpx;
}

.trend-arrow {
  font-size: 48rpx;
  margin-left: 16rpx;
}

.status-text {
  font-size: 28rpx;
  color: #6B7280;
}

/* 图表卡片 */
.chart-card {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.view-more {
  font-size: 24rpx;
  color: #3B82F6;
}

/* 统计网格 */
.stats-grid {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.stat-item {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #3B82F6;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 功能入口卡片 */
.section-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: white;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.section-card:active {
  transform: scale(0.98);
}

.card-icon-area {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.interaction-card .card-icon-area {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon {
  font-size: 60rpx;
}

.card-content {
  flex: 1;
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.card-desc {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  margin-bottom: 12rpx;
}

.preview-tags {
  display: flex;
  gap: 12rpx;
}

.preview-tag {
  padding: 4rpx 12rpx;
  background: #EFF6FF;
  color: #3B82F6;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.card-arrow {
  font-size: 48rpx;
  color: #D1D5DB;
}

/* 底部占位 */
.bottom-spacer {
  height: 40rpx;
}

/* ========== 家长模式 - 现代简洁风格 ========== */
.guardian-home {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 家长模式顶部 */
.guardian-header {
  padding: 40rpx 20rpx 30rpx;
}

.guardian-welcome {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.guardian-avatar-wrapper {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.guardian-avatar {
  width: 90rpx;
  height: 90rpx;
  border-radius: 50%;
}

.guardian-welcome-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.guardian-greeting {
  font-size: 28rpx;
  color: #6B7280;
  margin-bottom: 8rpx;
}

.guardian-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #1F2937;
}

/* 任务提醒卡片 */
.guardian-notification-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

.notification-icon-wrapper {
  width: 60rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon {
  font-size: 36rpx;
}

.notification-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.notification-title {
  font-size: 30rpx;
  font-weight: 600;
  color: white;
  margin-bottom: 6rpx;
}

.notification-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 仪表盘区域 */
.guardian-dashboard-section {
  margin-bottom: 32rpx;
}

/* 血糖状态卡片 */
.guardian-glucose-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.guardian-glucose-card.status-normal {
  border-left: 8rpx solid #10B981;
}

.guardian-glucose-card.status-warning {
  border-left: 8rpx solid #F59E0B;
}

.guardian-glucose-card.status-danger {
  border-left: 8rpx solid #EF4444;
}

.guardian-status-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.guardian-status-label {
  font-size: 28rpx;
  color: #6B7280;
}

.guardian-status-time {
  font-size: 24rpx;
  color: #9CA3AF;
}

.guardian-status-value-area {
  display: flex;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.guardian-glucose-value {
  font-size: 80rpx;
  font-weight: bold;
  color: #1F2937;
  line-height: 1;
}

.guardian-glucose-unit {
  font-size: 28rpx;
  color: #6B7280;
  margin-left: 12rpx;
}

.guardian-status-text {
  font-size: 28rpx;
  color: #6B7280;
}

/* 图表卡片 */
.guardian-chart-card {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.guardian-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.guardian-card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.guardian-view-more {
  font-size: 24rpx;
  color: #3B82F6;
}

/* 统计网格 */
.guardian-stats-grid {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.guardian-stat-item {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.guardian-stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #3B82F6;
  margin-bottom: 8rpx;
}

.guardian-stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 健康计划区域 */
.guardian-projects-section {
  margin-bottom: 32rpx;
}

.guardian-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  padding: 0 4rpx;
}

.guardian-section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.guardian-see-all {
  font-size: 24rpx;
  color: #3B82F6;
}

/* 项目卡片 */
.guardian-project-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

.guardian-project-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.guardian-project-title {
  font-size: 32rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 8rpx;
}

.guardian-project-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

.guardian-project-progress {
  display: flex;
  align-items: center;
  justify-content: center;
}

.guardian-progress-ring {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 6rpx solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
}

.guardian-progress-text {
  font-size: 24rpx;
  font-weight: bold;
  color: white;
}

.guardian-project-members {
  display: flex;
  align-items: center;
  gap: -10rpx;
}

.guardian-member-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 2rpx solid white;
  margin-left: -10rpx;
}

.guardian-member-avatar:first-child {
  margin-left: 0;
}

.guardian-member-more {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  color: white;
  font-weight: 600;
}

/* 任务区域 */
.guardian-tasks-section {
  margin-bottom: 32rpx;
}

.guardian-task-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.guardian-task-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.guardian-task-icon {
  width: 60rpx;
  height: 60rpx;
  background: #EFF6FF;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
}

.guardian-task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.guardian-task-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 6rpx;
}

.guardian-task-meta {
  font-size: 24rpx;
  color: #6B7280;
}

.guardian-task-badge {
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.guardian-task-done {
  background: #D1FAE5;
  color: #059669;
}

.guardian-task-progress {
  background: #DBEAFE;
  color: #2563EB;
}

.guardian-task-badge-text {
  font-size: 22rpx;
}

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-home {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 24rpx;
  padding-bottom: 120rpx;
  position: relative;
}

/* 顶部背景装饰 */
.child-header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300rpx;
  background: linear-gradient(180deg, #F2E5D3 0%, #FEF7ED 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.header-clouds {
  position: absolute;
  top: 40rpx;
  left: 0;
  right: 0;
}

.cloud {
  position: absolute;
  font-size: 60rpx;
  opacity: 0.6;
  animation: floatCloud 4s ease-in-out infinite;
}

.cloud.c1 { left: 10%; animation-delay: 0s; }
.cloud.c2 { right: 15%; animation-delay: 2s; }

@keyframes floatCloud {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}

/* 顶部区域 */
.child-header {
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 10 10rpx;
  z-index: 10;
}

.welcome-image-wrapper {
  width: 250rpx;
  height: 250rpx;
  flex-shrink: 0;
  margin-bottom: -80rpx;
}

.welcome-image {
  width: 250rpx;
  height: 250rpx;
}

.header-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-left: 20rpx;
  padding-bottom: 20rpx;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.child-greeting {
  font-size: 28rpx;
  color: #A85835;
  margin-bottom: 8rpx;
}

.child-name {
  font-size: 44rpx;
  font-weight: bold;
  color: #602F27;
}

.star-badge {
  position: absolute;
  right: 40rpx;
  bottom: 120rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: linear-gradient(145deg, #E8C48A 0%, #D5A874 50%, #C19660 100%);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  box-shadow: 
    0 4rpx 8rpx rgba(168, 88, 53, 0.3),
    inset 0 2rpx 4rpx rgba(255, 255, 255, 0.4),
    inset 0 -2rpx 4rpx rgba(168, 88, 53, 0.2);
  border: 1rpx solid rgba(168, 88, 53, 0.3);
  z-index: 16;
}

.star-icon {
  width: 36rpx;
  height: 36rpx;
}

.star-count {
  font-size: 24rpx;
  font-weight: bold;
  color: white;
}

.welcome-text-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  padding-left: 0;
  margin-left: 2rpx;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16rpx;
}

.pot-image-wrapper {
  position: absolute;
  right: 24rpx;
  bottom: 0rpx;
  width: 110rpx;
  height: 110rpx;
  flex-shrink: 0;
  z-index: 15;
}

.pot-image {
  width: 110rpx;
  height: 110rpx;
}

/* 吉祥物主卡片 - 可爱手绘风格 */
.mascot-main-card {
  position: relative;
  background: #FFFEF7;
  border-radius: 40rpx;
  padding: 40rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(96, 47, 39, 0.12);
  overflow: hidden;
  z-index: 10;
  min-height: 200rpx;
}

.mascot-main-card.status-danger {
  animation: cardShake 0.5s ease-in-out infinite;
}

@keyframes cardShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4rpx); }
  75% { transform: translateX(4rpx); }
}

/* 可爱装饰元素 */
.cute-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.cute-star, .cute-heart, .cute-sparkle {
  position: absolute;
  font-size: 24rpx;
  animation: float 3s ease-in-out infinite;
}

.cute-star.s1 {
  top: 20rpx;
  right: 30rpx;
  animation-delay: 0s;
}

.cute-star.s2 {
  top: 60rpx;
  left: 20rpx;
  animation-delay: 1s;
}

.cute-heart {
  bottom: 30rpx;
  right: 20rpx;
  animation-delay: 2s;
}

.cute-sparkle {
  top: 40rpx;
  right: 60rpx;
  animation-delay: 1.5s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10rpx) rotate(5deg); }
}

/* 三只猫咪图片 */
.three-cats-wrapper {
  position: absolute;
  bottom: 10rpx;
  left: 20rpx;
  width: 120rpx;
  height: 120rpx;
  z-index: 2;
}

.three-cats-image {
  width: 120rpx;
  height: 120rpx;
}

/* 可爱消息气泡 */
.cute-message-bubble {
  position: relative;
  background: linear-gradient(135deg, #FFE4E1 0%, #FFF0F5 100%);
  border-radius: 25rpx;
  padding: 20rpx 30rpx;
  margin: 20rpx 160rpx 20rpx 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(255, 182, 193, 0.3);
  border: 2rpx solid #FFB6C1;
  z-index: 3;
}

.bubble-tail {
  position: absolute;
  bottom: -12rpx;
  left: 40rpx;
  width: 0;
  height: 0;
  border-left: 15rpx solid transparent;
  border-right: 15rpx solid transparent;
  border-top: 15rpx solid #FFE4E1;
}

.bubble-text {
  font-size: 28rpx;
  color: #8B4B8C;
  font-weight: 500;
  line-height: 1.4;
  text-align: center;
  display: block;
}

/* 可爱状态徽章 */
.cute-status-badge {
  position: absolute;
  bottom: 20rpx;
  right: 20rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: linear-gradient(135deg, #E8EDB9 0%, #E8EDB9 100%);
  padding: 12rpx 20rpx;
  border-radius: 25rpx;
  box-shadow: 0 3rpx 8rpx rgba(232, 237, 185, 0.4);
  border: 2rpx solid #E8EDB9;
  z-index: 3;
}

.status-icon {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #32CD32;
  animation: pulse 2s ease-in-out infinite;
}

.status-text {
  font-size: 24rpx;
  color: #602F27;
  font-weight: 600;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.mascot-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.deco-item {
  position: absolute;
  font-size: 40rpx;
  opacity: 0.3;
}

.deco-item.d1 { top: 20rpx; right: 30rpx; }
.deco-item.d2 { bottom: 40rpx; left: 20rpx; }
.deco-item.d3 { top: 50%; right: 60rpx; }

.mascot-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.mascot-avatar-large {
  margin-bottom: 24rpx;
}

.mascot-avatar-large.happy {
  animation: bounce 2s ease-in-out infinite;
}

.mascot-avatar-large.worried {
  animation: worry 0.5s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-16rpx) scale(1.05); }
}

@keyframes worry {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-3deg); }
  75% { transform: rotate(3deg); }
}

.mascot-emoji {
  font-size: 160rpx;
  display: block;
  filter: drop-shadow(0 8rpx 16rpx rgba(0, 0, 0, 0.15));
}

.mascot-message-box {
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border: 3rpx solid #E3C7A4;
  border-radius: 24rpx;
  padding: 24rpx 32rpx;
  width: 100%;
  position: relative;
}

.mascot-message-box::before {
  content: '';
  position: absolute;
  top: -16rpx;
  left: 50%;
  transform: translateX(-50%);
  border-left: 16rpx solid transparent;
  border-right: 16rpx solid transparent;
  border-bottom: 16rpx solid #E3C7A4;
}

.message-text {
  font-size: 30rpx;
  color: #602F27;
  text-align: center;
  line-height: 1.6;
  display: block;
}

.status-badge-child {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-top: 24rpx;
}

.badge-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
}

.status-good .badge-dot {
  background: #4ADE80;
  box-shadow: 0 0 12rpx rgba(74, 222, 128, 0.6);
}

.status-warning .badge-dot {
  background: #CB8E54;
  box-shadow: 0 0 12rpx rgba(203, 142, 84, 0.6);
}

.status-danger .badge-dot {
  background: #F87171;
  box-shadow: 0 0 12rpx rgba(248, 113, 113, 0.6);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

.badge-text {
  font-size: 26rpx;
  color: #74362C;
  font-weight: 500;
}

/* 能量仪表盘卡片 - 可爱手绘风格 */
.energy-dashboard-card {
  position: relative;
  background: #FFFEF7;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
  overflow: hidden;
}

/* 仪表盘装饰元素 */
.dashboard-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.dash-star, .dash-heart {
  position: absolute;
  font-size: 20rpx;
  animation: sparkle 2s ease-in-out infinite;
}

.dash-star.d1 {
  top: 15rpx;
  right: 25rpx;
  animation-delay: 0s;
}

.dash-star.d2 {
  bottom: 25rpx;
  left: 15rpx;
  animation-delay: 1s;
}

.dash-heart {
  top: 20rpx;
  left: 30rpx;
  animation-delay: 0.5s;
}

@keyframes sparkle {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 仪表盘头部 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
  z-index: 2;
  position: relative;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.energy-icon {
  width: 50rpx;
  height: 50rpx;
}

.energy-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #8B4513;
}

.dashboard-time {
  font-size: 26rpx;
  color: #D2691E;
  font-weight: 500;
}

/* Ant Design 风格仪表盘 */
.ant-gauge {
  position: relative;
  width: 100%;
  padding: 20rpx 0 30rpx;
}

.gauge-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
}

.gauge-wrapper {
  position: relative;
  width: 420rpx;
  height: 240rpx;
}

/* 右侧颜色条图例 */
.gauge-color-bar {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.color-bar-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.color-bar-segment {
  width: 8rpx;
  height: 40rpx;
  border-radius: 4rpx;
}

.color-bar-label {
  font-size: 22rpx;
  color: #595959;
}

.gauge-svg {
  width: 100%;
  height: 100%;
}

.gauge-bg {
  transition: all 0.3s ease;
}

.gauge-progress {
  transition: stroke-dashoffset 0.5s ease;
}

.gauge-value-container {
  text-align: center;
  margin-top: -10rpx;
}

.gauge-value {
  display: block;
  font-size: 64rpx;
  font-weight: bold;
  color: #262626;
  line-height: 1.2;
  font-weight: 400;
}

/* 仪表盘文字显示 */
.gauge-text {
  position: absolute;
  bottom: -10rpx;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  z-index: 5;
}

.percentage-text {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #FFFFFF;
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.5);
  margin-bottom: 4rpx;
}

.status-text {
  display: block;
  font-size: 22rpx;
  color: #E3C7A4;
  font-weight: 500;
}

/* 图例样式 */
.energy-legend {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-top: 40rpx;
  padding: 0 20rpx;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.legend-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.optimal-dot {
  background: #90EE90;
}

.legend-text {
  font-size: 22rpx;
  color: #FFFFFF;
  font-weight: 500;
}

/* 底部图例样式 */
.gauge-legend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30rpx;
  padding: 0 20rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-dot.low {
  background: #D2691E;
}

.legend-dot.normal {
  background: #CD853F;
}

.legend-dot.high {
  background: #DEB887;
}

.legend-dot.optimal {
  background: #90EE90;
}

.legend-text {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.legend-label {
  font-size: 24rpx;
  color: #FFFFFF;
  font-weight: 500;
}

.legend-value {
  font-size: 28rpx;
  color: #FFFFFF;
  font-weight: bold;
}

/* 新标签样式 */

.label-item {
  font-size: 24rpx;
  font-weight: 500;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #F0F8FF 0%, #E6F3FF 100%);
  border: 2rpx solid #B0E0E6;
  box-shadow: 0 2rpx 4rpx rgba(176, 224, 230, 0.3);
}

.label-item.low {
  color: #CD5C5C;
  border-color: #FFB6C1;
  background: linear-gradient(135deg, #FFE4E1 0%, #FFF0F5 100%);
}

.label-item.good {
  color: #32CD32;
  border-color: #98FB98;
  background: linear-gradient(135deg, #F0FFF0 0%, #F5FFFA 100%);
  font-weight: bold;
}

.label-item.high {
  color: #FF8C00;
  border-color: #FFE4B5;
  background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%);
}

.energy-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.energy-time {
  font-size: 26rpx;
  color: #A85835;
}

.energy-display {
  position: relative;
}

.energy-bar-track {
  display: flex;
  height: 48rpx;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: inset 0 4rpx 8rpx rgba(0, 0, 0, 0.1);
  position: relative;
}

.energy-zone {
  flex: 1;
}

.zone-low {
  background: linear-gradient(90deg, #C07240 0%, #D5A874 100%);
}

.zone-good {
  background: linear-gradient(90deg, #90EE90 0%, #98FB98 100%);
}

.zone-high {
  background: linear-gradient(90deg, #D5A874 0%, #C07240 100%);
}

.energy-pointer {
  position: absolute;
  top: -20rpx;
  transform: translateX(-50%);
  transition: left 0.5s ease;
  z-index: 10;
}

.pointer-face {
  font-size: 56rpx;
  display: block;
  filter: drop-shadow(0 4rpx 8rpx rgba(0, 0, 0, 0.2));
}

.energy-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
  padding: 0 8rpx;
}

.energy-label {
  font-size: 24rpx;
  color: #8E422F;
}

.energy-label.good {
  color: #228B22;
  font-weight: bold;
}

/* 任务卡片 */
.tasks-card-child {
  background: #FFFEF7;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.tasks-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.tasks-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.tasks-title-icon {
  width: 40rpx;
  height: 40rpx;
}

.tasks-title-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.tasks-count {
  font-size: 28rpx;
  color: #A85835;
  font-weight: 600;
}

.tasks-list-child {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-item-child {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 24rpx;
  background: #FAF6F0;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  transition: all 0.3s ease;
}

.task-item-child.done {
  background: linear-gradient(135deg, #E8EDB9 0%, #E8EDB9 100%);
  border-color: #A0BF52;
}

.task-checkbox {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-checkbox text {
  font-size: 40rpx;
}

.task-finish-icon {
  width: 42rpx;
  height: 42rpx;
}

.checkbox-empty {
  width: 40rpx;
  height: 40rpx;
  border: 4rpx solid #D5A874;
  border-radius: 50%;
  background: white;
}

.task-icon-img {
  width: 36rpx;
  height: 36rpx;
}

.task-text {
  flex: 1;
  font-size: 28rpx;
  color: #602F27;
}

.task-item-child.done .task-text {
  color: #228B22;
}

.task-reward-img {
  width: 45rpx;
  height: 45rpx;
  animation: starPop 0.5s ease, starBounce 2s ease-in-out infinite 0.5s;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.4); }
  100% { transform: scale(1); }
}

@keyframes starBounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-6rpx) scale(1.1); }
}

/* 功能菜单网格 */
.child-menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.child-menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.menu-icon-wrap {
  width: 100rpx;
  height: 100rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.1);
}

.menu-icon-wrap.companion,
.menu-icon-wrap.game,
.menu-icon-wrap.food,
.menu-icon-wrap.chart {
  background: #F6D387;
  box-shadow: 
    0 6rpx 16rpx rgba(246, 211, 135, 0.4),
    inset 0 2rpx 4rpx rgba(255, 255, 255, 0.8),
    inset 0 -2rpx 4rpx rgba(0, 0, 0, 0.1);
  border: 2rpx solid rgba(255, 255, 255, 0.6);
}

.menu-icon {
  font-size: 52rpx;
}

.menu-icon-img {
  width: 70rpx;
  height: 70rpx;
  display: block;
}

/* 特定按钮的图片尺寸调整 */
.menu-icon-wrap.food .menu-icon-img,
.menu-icon-wrap.chart .menu-icon-img {
  width: 75rpx;
  height: 75rpx;
}

.menu-name {
  font-size: 24rpx;
  color: #602F27;
  font-weight: 500;
}

/* 提示卡片 */
.tip-card-child {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 20rpx;
  padding: 0;
  border-radius: 28rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
}

.tip-card-child.tip-normal,
.tip-card-child.tip-warning,
.tip-card-child.tip-danger {
  background-image: url('/static/ch/ch_index_pin.png');
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
  min-height: 340rpx;
  width: 100%;
}

.tip-icon-child {
  font-size: 48rpx;
  margin: 0;
  padding: 20rpx;
}

.tip-content-child {
  flex: 1;
  padding: 90rpx 20rpx 20rpx 80rpx;
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
}

.tip-title-child {
  font-size: 28rpx;
  font-weight: bold;
  color: #602F27;
  display: block;
  margin-bottom: 8rpx;
}

.tip-text-child {
  font-size: 26rpx;
  color: #74362C;
  line-height: 1.5;
}

/* 底部装饰 */
.child-footer-deco {
  display: flex;
  justify-content: flex-end;
  margin-top: 24rpx;
  overflow: hidden;
  position: relative;
  height: 108rpx;
}

.footer-cat-cloud {
  width: 180rpx;
  height: 180rpx;
  margin-top: -72rpx;
  animation: moveLeftRight 10s ease-in-out infinite;
}

@keyframes moveLeftRight {
  0% {
    transform: translateX(0) scaleX(1);
  }
  48% {
    transform: translateX(-600rpx) scaleX(1);
  }
  50% {
    transform: translateX(-600rpx) scaleX(-1);
  }
  98% {
    transform: translateX(0) scaleX(-1);
  }
  100% {
    transform: translateX(0) scaleX(1);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16rpx); }
}
</style>
