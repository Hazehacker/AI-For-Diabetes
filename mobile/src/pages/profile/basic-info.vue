<template>
  <view class="basic-info-page">
    <view class="page-header">
      <text class="page-title">基础信息</text>
      <text class="page-subtitle">完善您的健康档案</text>
    </view>

    <view class="coming-soon">
      <text class="icon">🏥</text>
      <text class="title">功能开发中</text>
      <text class="desc">基础信息收集功能即将上线</text>
      <view class="feature-list">
        <text class="feature-item">✓ 个人基本信息</text>
        <text class="feature-item">✓ 疾病史记录</text>
        <text class="feature-item">✓ 家族病史</text>
        <text class="feature-item">✓ 血糖监测水平</text>
      </view>
    </view>
  </view>
</template>

<script setup>
</script>

<style scoped>
.basic-info-page {
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
