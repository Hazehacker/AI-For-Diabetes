<template>
  <view class="role-switcher-page">
    <view class="header">
      <text class="title">角色切换测试</text>
      <text class="subtitle">选择不同角色查看仪表盘效果</text>
    </view>

    <view class="role-cards">
      <view 
        v-for="role in roles" 
        :key="role.value"
        class="role-card"
        :class="{ active: currentRole === role.value }"
        @tap="switchRole(role.value)"
      >
        <text class="role-icon">{{ role.icon }}</text>
        <text class="role-name">{{ role.name }}</text>
        <text class="role-desc">{{ role.description }}</text>
        <view v-if="currentRole === role.value" class="check-mark">✓</view>
      </view>
    </view>

    <view class="features-preview">
      <text class="preview-title">当前角色可见功能：</text>
      <view class="feature-list">
        <view 
          v-for="feature in currentFeatures" 
          :key="feature"
          class="feature-item"
        >
          <text class="feature-icon">✓</text>
          <text class="feature-text">{{ feature }}</text>
        </view>
      </view>
    </view>

    <button class="view-dashboard-btn" @tap="goToDashboard">
      查看仪表盘
    </button>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/store/dashboard'

const dashboardStore = useDashboardStore()

const roles = [
  {
    value: 'child_under_12',
    name: '儿童模式',
    icon: '👶',
    description: '适合12岁以下患者',
    features: [
      '卡通形象显示',
      '能量条可视化',
      '简化的状态提示',
      '家长监护提醒'
    ]
  },
  {
    value: 'teen_above_12',
    name: '青少年模式',
    icon: '👦',
    description: '适合12岁及以上患者',
    features: [
      '完整血糖数值',
      '实时趋势曲线',
      '统计指标（TIR/GMI/CV）',
      '详细建议与操作',
      '事件标记功能'
    ]
  },
  {
    value: 'guardian',
    name: '家属模式',
    icon: '👨‍👩‍👧',
    description: '适合患者家属',
    features: [
      '全部数据访问',
      '警报配置权限',
      '历史数据导出',
      '远程监护功能',
      '多患者管理'
    ]
  }
]

const currentRole = ref(dashboardStore.userRole)

const currentFeatures = computed(() => {
  const role = roles.find(r => r.value === currentRole.value)
  return role ? role.features : []
})

const switchRole = (roleValue) => {
  currentRole.value = roleValue
  dashboardStore.setUserRole(roleValue)
  
  uni.showToast({
    title: `已切换到${roles.find(r => r.value === roleValue).name}`,
    icon: 'success'
  })
}

const goToDashboard = () => {
  uni.navigateTo({
    url: '/pages/dashboard/dashboard'
  })
}
</script>

<style scoped>
.role-switcher-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx;
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
  padding-top: 40rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 16rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.role-cards {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 60rpx;
}

.role-card {
  position: relative;
  background: white;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.role-card.active {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  transform: scale(1.02);
}

.role-card.active .role-name,
.role-card.active .role-desc {
  color: white;
}

.role-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.role-name {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 12rpx;
}

.role-desc {
  display: block;
  font-size: 28rpx;
  color: #6B7280;
}

.check-mark {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  width: 60rpx;
  height: 60rpx;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  color: #10B981;
  font-weight: bold;
}

.features-preview {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
}

.preview-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 24rpx;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.feature-item {
  display: flex;
  align-items: center;
}

.feature-icon {
  width: 40rpx;
  height: 40rpx;
  background: #10B981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.feature-text {
  font-size: 28rpx;
  color: #4B5563;
}

.view-dashboard-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.4);
}
</style>
