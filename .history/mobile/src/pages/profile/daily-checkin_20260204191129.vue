<template>
  <view class="checkin-page">
    <view class="page-header">
      <text class="page-title">每日签到</text>
      <text class="page-subtitle">坚持打卡，赢取积分</text>
    </view>

    <view class="coming-soon">
      <text class="icon">✅</text>
      <text class="title">功能开发中</text>
      <text class="desc">每日签到积分系统即将上线</text>
      <view class="feature-list">
        <text class="feature-item">✓ 每日签到打卡</text>
        <text class="feature-item">✓ 连续签到奖励</text>
        <text class="feature-item">✓ 积分兑换商城</text>
        <text class="feature-item">✓ 会员服务特权</text>
      </view>
    </view>
  </view>
</template>

<script setup>
</script>

<style scoped>
.checkin-page {
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

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
  max-width: 500rpx;
}

.feature-item {
  padding: 20rpx 24rpx;
  background: white;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #374151;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
</style>
