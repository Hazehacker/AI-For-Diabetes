<template>
  <view class="interaction-page">
    <view class="page-header">
      <text class="page-title">互动板块</text>
      <text class="page-subtitle">参与挑战，赢取奖励</text>
    </view>

    <view class="coming-soon">
      <text class="icon">🎮</text>
      <text class="title">功能开发中</text>
      <text class="desc">互动板块即将上线，敬请期待！</text>
      <button class="btn-back" @tap="goBack">返回首页</button>
    </view>
  </view>
</template>

<script setup>
const goBack = () => {
  uni.navigateBack()
}
</script>

<style scoped>
.interaction-page {
  min-height: 100vh;
  background: #F3F4F6;
  padding: 20rpx;
}

.page-header {
  padding: 40rpx 20rpx;
  text-align: center;
}

.page-title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.page-subtitle {
  display: block;
  font-size: 28rpx;
  color: #6B7280;
}

.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 40rpx;
}

.icon {
  font-size: 120rpx;
  margin-bottom: 32rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.desc {
  font-size: 28rpx;
  color: #6B7280;
  margin-bottom: 48rpx;
  text-align: center;
}

.btn-back {
  width: 400rpx;
  height: 88rpx;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}
</style>
