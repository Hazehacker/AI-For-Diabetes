<template>
  <!-- 儿童模式：奶酪仓鼠风格 -->
  <view v-if="userRole === 'child_under_12'" class="child-interaction">
    <!-- 顶部区域 -->
    <view class="child-inter-header">
      <view class="header-deco">
        <text class="deco-item">🎮</text>
        <text class="header-title">游乐园</text>
        <text class="deco-item">🎪</text>
      </view>
      <view class="points-badge">
        <text class="points-icon">⭐</text>
        <text class="points-num">{{ totalPoints }}</text>
      </view>
    </view>

    <!-- 吉祥物欢迎 -->
    <view class="mascot-welcome">
      <view class="mascot-avatar-inter">
        <text class="mascot-emoji-inter">🐹</text>
      </view>
      <view class="welcome-bubble">
        <text class="welcome-text">欢迎来到游乐园！选一个好玩的吧~</text>
      </view>
    </view>

    <!-- 游戏入口网格 -->
    <view class="games-grid">
      <view class="game-card breathing-game" @tap="goToBreathing">
        <view class="game-icon-wrap rainbow">
          <text class="game-icon">🌈</text>
        </view>
        <text class="game-name">吹云朵</text>
        <text class="game-desc">深呼吸放松</text>
        <view class="game-badge">
          <text>🔥 {{ sortedSessions.length }}次</text>
        </view>
      </view>

      <view class="game-card pet-game" @tap="goToPet">
        <view class="game-icon-wrap pet">
          <text class="game-icon">{{ currentPetStage.emoji }}</text>
        </view>
        <text class="game-name">糖小怪</text>
        <text class="game-desc">我的小伙伴</text>
        <view class="game-badge pet">
          <text>💕 {{ pet.streak_days }}天</text>
        </view>
      </view>

      <view class="game-card mini-game">
        <view class="game-icon-wrap mini">
          <text class="game-icon">🎯</text>
        </view>
        <text class="game-name">小游戏</text>
        <text class="game-desc">即将开放</text>
        <view class="coming-tag">敬请期待</view>
      </view>

      <view class="game-card learn-game">
        <view class="game-icon-wrap learn">
          <text class="game-icon">📚</text>
        </view>
        <text class="game-name">小知识</text>
        <text class="game-desc">即将开放</text>
        <view class="coming-tag">敬请期待</view>
      </view>
    </view>

    <!-- 我的奖章 -->
    <view v-if="unlockedBadges.length > 0" class="badges-card-inter">
      <view class="badges-header-inter">
        <text class="badges-title-inter">🏅 我的奖章</text>
        <text class="badges-count">{{ unlockedBadges.length }}枚</text>
      </view>
      <view class="badges-scroll">
        <view v-for="badge in unlockedBadges" :key="badge.id" class="badge-item-inter">
          <text class="badge-emoji-inter">{{ badge.icon }}</text>
          <text class="badge-name-inter">{{ badge.name }}</text>
        </view>
      </view>
    </view>

    <!-- 最近记录 -->
    <view v-if="sortedSessions.length > 0" class="recent-card">
      <view class="recent-header">
        <text class="recent-title">📝 最近玩的</text>
      </view>
      <view class="recent-list">
        <view v-for="session in sortedSessions.slice(0, 3)" :key="session.id" class="recent-item">
          <text class="recent-icon">🌈</text>
          <text class="recent-name">吹云朵</text>
          <text class="recent-time">{{ formatDate(session.completed_at) }}</text>
          <text class="recent-star">⭐+{{ session.reward_points }}</text>
        </view>
      </view>
    </view>

    <!-- 底部装饰 -->
    <view class="child-inter-footer">
      <text class="footer-item">🧀</text>
      <text class="footer-item">🎈</text>
      <text class="footer-item">🧀</text>
    </view>
  </view>

  <!-- 成人/青少年模式 -->
  <view v-else class="interaction-page">
    <!-- 顶部统计 -->
    <view class="stats-header">
      <view class="stat-item">
        <text class="stat-value">{{ totalPoints }}</text>
        <text class="stat-label">总积分</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ weeklySessionCount }}</text>
        <text class="stat-label">本周训练</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ unlockedBadges.length }}</text>
        <text class="stat-label">已获奖章</text>
      </view>
    </view>

    <!-- 功能卡片 -->
    <view class="features-section">
      <!-- 呼吸冥想训练 -->
      <view class="feature-card breathing" @tap="goToBreathing">
        <view class="card-background">
          <text class="cloud-emoji">☁️</text>
          <text class="cloud-emoji">☁️</text>
          <text class="cloud-emoji">☁️</text>
        </view>
        <view class="card-content">
          <view class="card-header">
            <text class="card-icon">🌈</text>
            <view class="card-badge">推荐</view>
          </view>
          <text class="card-title">呼吸 & 冥想训练</text>
          <text class="card-desc">吹走烦恼云，放松身心</text>
          <view class="card-stats">
            <text class="stat-text">🔥 已完成 {{ sortedSessions.length }} 次</text>
          </view>
        </view>
      </view>

      <!-- 电子宠物糖小怪 -->
      <view class="feature-card pet-card" @tap="goToPet">
        <view class="card-content">
          <view class="card-header">
            <text class="card-icon">{{ currentPetStage.emoji }}</text>
            <view class="card-badge pet">{{ currentPetStage.name }}</view>
          </view>
          <text class="card-title">电子宠物「糖小怪」</text>
          <text class="card-desc">陪伴你的健康管理</text>
          <view class="pet-stats">
            <view class="pet-stat-item">
              <text class="stat-label">连续</text>
              <text class="stat-value">{{ pet.streak_days }}天</text>
            </view>
            <view class="pet-stat-item">
              <text class="stat-label">进度</text>
              <text class="stat-value">{{ pet.progress }}%</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 其他功能占位 -->
      <view class="feature-card coming-soon">
        <view class="card-content">
          <view class="card-header">
            <text class="card-icon">🎮</text>
          </view>
          <text class="card-title">小游戏</text>
          <text class="card-desc">即将上线</text>
        </view>
      </view>

      <view class="feature-card coming-soon">
        <view class="card-content">
          <view class="card-header">
            <text class="card-icon">📚</text>
          </view>
          <text class="card-title">科普知识</text>
          <text class="card-desc">即将上线</text>
        </view>
      </view>

      <view class="feature-card coming-soon">
        <view class="card-content">
          <view class="card-header">
            <text class="card-icon">🎥</text>
          </view>
          <text class="card-title">视频学习</text>
          <text class="card-desc">即将上线</text>
        </view>
      </view>
    </view>

    <!-- 奖章展示 -->
    <view v-if="unlockedBadges.length > 0" class="badges-section">
      <text class="section-title">我的奖章</text>
      <view class="badges-grid">
        <view 
          v-for="badge in unlockedBadges" 
          :key="badge.id"
          class="badge-item"
        >
          <text class="badge-icon">{{ badge.icon }}</text>
          <text class="badge-name">{{ badge.name }}</text>
        </view>
      </view>
    </view>

    <!-- 训练历史 -->
    <view v-if="sortedSessions.length > 0" class="history-section">
      <text class="section-title">训练历史</text>
      <view class="history-list">
        <view 
          v-for="session in sortedSessions.slice(0, 5)" 
          :key="session.id"
          class="history-item"
        >
          <view class="history-icon">
            <text class="icon-emoji">🌈</text>
          </view>
          <view class="history-info">
            <text class="history-title">呼吸训练</text>
            <text class="history-time">{{ formatDate(session.completed_at) }}</text>
          </view>
          <view class="history-stats">
            <text class="stat-badge">节律 {{ session.rhythm_score }}</text>
            <text class="stat-badge points">+{{ session.reward_points }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useInteractionStore } from '@/store/interaction'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const interactionStore = useInteractionStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const { 
  totalPoints, 
  weeklySessionCount, 
  sortedSessions, 
  unlockedBadges,
  pet,
  currentPetStage
} = storeToRefs(interactionStore)

// 格式化日期
const formatDate = (date) => {
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  const month = d.getMonth() + 1
  const day = d.getDate()
  return `${month}-${day}`
}

// 跳转到呼吸训练
const goToBreathing = () => {
  uni.navigateTo({
    url: '/pages/interaction/breathing-setup'
  })
}

// 跳转到电子宠物
const goToPet = () => {
  uni.navigateTo({
    url: '/pages/interaction/pet'
  })
}

onMounted(() => {
  // 生成模拟数据
  if (interactionStore.sessions.length === 0) {
    interactionStore.generateMockData()
  }
  
  // 调试：检查宠物数据
  console.log('=== 互动板块数据检查 ===')
  console.log('宠物数据:', pet.value)
  console.log('当前阶段:', currentPetStage.value)
  console.log('总积分:', totalPoints.value)
})
</script>

<style scoped>
.interaction-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f093fb 0%, #f5576c 30%, #F3F4F6 30%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 统计头部 */
.stats-header {
  display: flex;
  gap: 16rpx;
  margin-bottom: 32rpx;
  padding: 20rpx 0;
}

.stat-item {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10rpx);
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #f5576c;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 功能卡片 */
.features-section {
  margin-bottom: 32rpx;
}

.feature-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.feature-card.breathing {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 280rpx;
}

.feature-card.pet-card {
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  min-height: 240rpx;
}

.feature-card.pet-card .card-title {
  color: #78350F;
}

.feature-card.pet-card .card-desc {
  color: rgba(120, 53, 15, 0.8);
}

.feature-card.coming-soon {
  opacity: 0.6;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  opacity: 0.2;
}

.cloud-emoji {
  font-size: 100rpx;
  animation: float 3s ease-in-out infinite;
}

.cloud-emoji:nth-child(2) {
  animation-delay: 1s;
}

.cloud-emoji:nth-child(3) {
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}

.card-content {
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-icon {
  font-size: 64rpx;
}

.card-badge {
  padding: 8rpx 16rpx;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10rpx);
  border-radius: 12rpx;
  font-size: 22rpx;
  color: white;
  font-weight: bold;
}

.card-title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 12rpx;
}

.feature-card.coming-soon .card-title {
  color: #1F2937;
}

.card-desc {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20rpx;
}

.feature-card.coming-soon .card-desc {
  color: #6B7280;
}

.card-stats {
  display: flex;
  gap: 16rpx;
}

.stat-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 奖章区 */
.badges-section,
.history-section {
  margin-bottom: 32rpx;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 20rpx;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.badge-item {
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.badge-icon {
  display: block;
  font-size: 60rpx;
  margin-bottom: 8rpx;
}

.badge-name {
  display: block;
  font-size: 22rpx;
  color: #6B7280;
}

/* 历史记录 */
.history-list {
  background: white;
  border-radius: 16rpx;
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
}

.history-item:last-child {
  border-bottom: none;
}

.history-icon {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-emoji {
  font-size: 48rpx;
}

.history-info {
  flex: 1;
}

.history-title {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.history-time {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
}

.history-stats {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  align-items: flex-end;
}

.stat-badge {
  padding: 4rpx 12rpx;
  background: #EFF6FF;
  color: #3B82F6;
  border-radius: 8rpx;
  font-size: 22rpx;
}

.stat-badge.points {
  background: #FEF3C7;
  color: #F59E0B;
}

/* 宠物统计 */
.pet-stats {
  display: flex;
  gap: 24rpx;
  margin-top: 16rpx;
}

.pet-stat-item {
  flex: 1;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10rpx);
  border-radius: 12rpx;
  padding: 16rpx;
  text-align: center;
}

.pet-stat-item .stat-label {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8rpx;
}

.pet-stat-item .stat-value {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: white;
}

.card-badge.pet {
  background: rgba(255, 255, 255, 0.4);
}

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-interaction {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 24rpx;
  padding-bottom: 120rpx;
}

.child-inter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.header-deco {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.header-deco .deco-item {
  font-size: 36rpx;
}

.header-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #602F27;
}

.points-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: linear-gradient(135deg, #D5A874 0%, #CB8E54 100%);
  padding: 12rpx 20rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(203, 142, 84, 0.3);
}

.points-icon {
  font-size: 28rpx;
}

.points-num {
  font-size: 28rpx;
  font-weight: bold;
  color: white;
}

/* 吉祥物欢迎 */
.mascot-welcome {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.1);
  border: 3rpx solid #E3C7A4;
}

.mascot-avatar-inter {
  flex-shrink: 0;
}

.mascot-emoji-inter {
  font-size: 64rpx;
  display: block;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10rpx); }
}

.welcome-bubble {
  flex: 1;
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border: 2rpx solid #E3C7A4;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  position: relative;
}

.welcome-bubble::before {
  content: '';
  position: absolute;
  left: -12rpx;
  top: 50%;
  transform: translateY(-50%);
  border-top: 10rpx solid transparent;
  border-bottom: 10rpx solid transparent;
  border-right: 12rpx solid #E3C7A4;
}

.welcome-text {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.5;
}

/* 游戏网格 */
.games-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.game-card {
  background: white;
  border-radius: 28rpx;
  padding: 28rpx;
  text-align: center;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
  transition: transform 0.2s;
}

.game-card:active {
  transform: scale(0.96);
}

.game-icon-wrap {
  width: 100rpx;
  height: 100rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16rpx;
}

.game-icon-wrap.rainbow {
  background: linear-gradient(135deg, #E3C7A4 0%, #D5A874 50%, #CB8E54 100%);
}

.game-icon-wrap.pet {
  background: linear-gradient(135deg, #D5A874 0%, #CB8E54 100%);
}

.game-icon-wrap.mini {
  background: linear-gradient(135deg, #CB8E54 0%, #C07240 100%);
}

.game-icon-wrap.learn {
  background: linear-gradient(135deg, #8E422F 0%, #A85835 100%);
}

.game-icon {
  font-size: 56rpx;
}

.game-name {
  display: block;
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
  margin-bottom: 8rpx;
}

.game-desc {
  display: block;
  font-size: 24rpx;
  color: #A85835;
  margin-bottom: 12rpx;
}

.game-badge {
  display: inline-block;
  background: linear-gradient(135deg, #F2E5D3 0%, #D5A874 100%);
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  color: #602F27;
}

.game-badge.pet {
  background: linear-gradient(135deg, #E3C7A4 0%, #D5A874 100%);
}

.coming-tag {
  display: inline-block;
  background: #E5E7EB;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  color: #9CA3AF;
}

.mini-game, .learn-game {
  opacity: 0.6;
}

/* 奖章卡片 */
.badges-card-inter {
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.badges-header-inter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.badges-title-inter {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.badges-count {
  font-size: 26rpx;
  color: #A85835;
}

.badges-scroll {
  display: flex;
  gap: 16rpx;
  overflow-x: auto;
  padding-bottom: 8rpx;
}

.badge-item-inter {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 20rpx;
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border-radius: 16rpx;
  border: 2rpx solid #D5A874;
}

.badge-emoji-inter {
  font-size: 48rpx;
  margin-bottom: 8rpx;
}

.badge-name-inter {
  font-size: 22rpx;
  color: #8E422F;
  white-space: nowrap;
}

/* 最近记录 */
.recent-card {
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.recent-header {
  margin-bottom: 16rpx;
}

.recent-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
}

.recent-icon {
  font-size: 32rpx;
}

.recent-name {
  font-size: 26rpx;
  color: #602F27;
  flex: 1;
}

.recent-time {
  font-size: 22rpx;
  color: #A85835;
}

.recent-star {
  font-size: 24rpx;
  color: #CB8E54;
  font-weight: bold;
}

/* 底部装饰 */
.child-inter-footer {
  display: flex;
  justify-content: center;
  gap: 48rpx;
  padding: 20rpx 0;
  opacity: 0.5;
}

.footer-item {
  font-size: 48rpx;
  animation: float 3s ease-in-out infinite;
}

.footer-item:nth-child(2) {
  animation-delay: 1s;
}

.footer-item:nth-child(3) {
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16rpx); }
}
</style>
