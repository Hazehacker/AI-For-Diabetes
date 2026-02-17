<template>
  <view class="games-page">
    <view class="header">
      <text class="title">小游戏乐园</text>
      <text class="subtitle">2-3分钟一局，开心学点小知识</text>
    </view>

    <view class="cards">
      <view
        v-for="g in games"
        :key="g.game_id"
        class="game-card"
        @tap="openGame(g.game_id)"
      >
        <view class="card-top">
          <text class="emoji">{{ iconMap[g.game_id] || '🎮' }}</text>
          <view class="tags">
            <text v-for="t in (g.tags || [])" :key="t" class="tag">{{ t }}</text>
          </view>
        </view>
        <text class="name">{{ g.name }}</text>
        <text class="desc">{{ descMap[g.game_id] || '轻松好玩的小挑战' }}</text>
        <view class="meta">
          <text class="meta-item">⏱ {{ g.duration_hint || '2-3分钟' }}</text>
          <text class="meta-item">✨ 赢积分</text>
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
import { onMounted, ref } from 'vue'
import { useGamesStore } from '@/store/games'

const gamesStore = useGamesStore()
const games = ref([])

const iconMap = {
  runner: '🏃‍♂️',
  food_match: '🍽️'
}

const descMap = {
  runner: '收集健康食物，躲开高糖“捣蛋鬼”！',
  food_match: '把食物送到正确的“碳水篮子”里！'
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
  background: linear-gradient(180deg, #f093fb 0%, #f5576c 24%, #F3F4F6 24%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.header {
  padding: 24rpx 12rpx 16rpx;
}

.title {
  display: block;
  font-size: 44rpx;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1rpx;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

.cards {
  margin-top: 8rpx;
}

.game-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10rpx);
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
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
  background: rgba(245, 87, 108, 0.12);
  color: #f5576c;
}

.name {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #111827;
  margin-top: 6rpx;
}

.desc {
  display: block;
  font-size: 26rpx;
  color: #6B7280;
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
  color: #374151;
  background: rgba(17, 24, 39, 0.06);
  padding: 8rpx 14rpx;
  border-radius: 14rpx;
}

.tips-card {
  margin-top: 12rpx;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 24rpx;
  padding: 24rpx;
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: #111827;
  margin-bottom: 8rpx;
}

.tips-text {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.6;
}
</style>


