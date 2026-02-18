<template>
  <view class="games-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">小游戏乐园</text>
      <view class="nav-placeholder"></view>
    </view>
    
    <view class="header" v-if="!isChildMode">
      <text class="subtitle">2-3分钟一局，开心学点小知识</text>
    </view>
    <view class="header-spacer" v-else></view>

    <view class="cards">
      <view
        v-for="g in games"
        :key="g.game_id"
        class="game-card"
        @tap="openGame(g.game_id)"
      >
        <view class="card-top">
          <image v-if="isChildMode && childIconMap[g.game_id]" class="game-icon" :src="childIconMap[g.game_id]" mode="aspectFit"></image>
          <text v-else class="emoji">{{ iconMap[g.game_id] || '🎮' }}</text>
          <view class="tags" :class="{ 'child-tags': isChildMode }">
            <text v-for="t in (g.tags || [])" :key="t" class="tag" :class="{ 'child-tag': isChildMode }">{{ t }}</text>
          </view>
        </view>
        <text class="name" :class="{ 'child-name': isChildMode }">{{ g.name }}</text>
        <text class="desc">{{ descMap[g.game_id] || '轻松好玩的小挑战' }}</text>
        <view class="meta" :class="{ 'child-meta': isChildMode }">
          <text class="meta-item" :class="{ 'child-meta-item': isChildMode }">⏱ {{ g.duration_hint || '2-3分钟' }}</text>
          <text class="meta-item" :class="{ 'child-meta-item child-meta-points': isChildMode }">✨ 赢积分</text>
        </view>
      </view>
    </view>

    <view class="tips-card">
      <text class="tips-title">小提醒</text>
      <text class="tips-text">游戏只是练习小常识，真实饮食/用药请听医生和家长的建议。</text>
    </view>
  </view>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useGamesStore } from '@/store/games'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const gamesStore = useGamesStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')
const games = ref([])

const iconMap = {
  runner: '🏃‍♂️',
  food_match: '🍽️'
}

const childIconMap = {
  runner: '/static/ch/ch_play_run.png',
  food_match: '/static/ch/ch_play_pu.png'
}

const descMap = {
  runner: '收集健康食物，躲开高糖“捣蛋鬼”！',
  food_match: '把食物送到正确的“碳水篮子”里！'
}

const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.navigateTo({ url: '/pages/interaction/index' })
  }
}

const openGame = (gameId) => {
  const map = {
    runner: '/pages/interaction/games/runner',
    food_match: '/pages/interaction/games/food-match'
  }
  uni.navigateTo({ url: map[gameId] || map.runner })
}

onMounted(async () => {
  gamesStore.initFromCache()
  games.value = await gamesStore.fetchGames({ age_group: 'child' })
  gamesStore.flushPending()
})
</script>

<style scoped>
.games-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
  padding-bottom: 120rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.nav-back-icon {
  width: 64rpx;
  height: 64rpx;
  display: block;
  padding: 10rpx;
  cursor: pointer;
  z-index: 100;
  position: relative;
}

.nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.nav-placeholder {
  width: 64rpx;
}

.header {
  padding: 24rpx;
}

.header-spacer {
  height: 20rpx;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #A85835;
}

.cards {
  margin: 0 24rpx;
}

.game-card {
  background: white;
  border-radius: 28rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.emoji {
  font-size: 52rpx;
}

.game-icon {
  width: 80rpx;
  height: 80rpx;
}

.tags {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.tag {
  font-size: 22rpx;
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  color: #CB8E54;
}

.name {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #602F27;
  margin-top: 6rpx;
}

.desc {
  display: block;
  font-size: 26rpx;
  color: #A85835;
  margin-top: 8rpx;
}

.meta {
  margin-top: 16rpx;
  display: flex;
  gap: 18rpx;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 24rpx;
  color: #CB8E54;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  padding: 8rpx 14rpx;
  border-radius: 14rpx;
}

.tips-card {
  margin: 12rpx 24rpx;
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: #602F27;
  margin-bottom: 8rpx;
}

.tips-text {
  display: block;
  font-size: 24rpx;
  color: #A85835;
  line-height: 1.6;
}

/* 儿童模式可爱风格 */
.child-tags {
  gap: 12rpx;
}

.child-tag {
  font-size: 24rpx;
  font-weight: 600;
  color: #fff;
  background: #6A332A;
  padding: 10rpx 18rpx;
  border-radius: 20rpx;
  border: 3rpx solid #5A2820;
  box-shadow: 0 4rpx 0 #4A1E18;
}

.child-meta {
  gap: 16rpx;
}

.child-meta-item {
  font-size: 26rpx;
  font-weight: 600;
  color: #6A332A;
  background: #F6CD75;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  border: 3rpx solid #E5BC64;
  box-shadow: 0 4rpx 0 #D4AB53;
}

.child-meta-points {
  background: #F6CD75;
  border-color: #E5BC64;
  box-shadow: 0 4rpx 0 #D4AB53;
}

.child-name {
  font-size: 40rpx;
  font-weight: 800;
  color: #8B4513;
  letter-spacing: 2rpx;
}
</style>


