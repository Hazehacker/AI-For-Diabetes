<template>
  <!-- 儿童模式底部栏 -->
  <view v-if="isChildMode" class="custom-tabbar child-tabbar">
    <!-- 弧形背景 -->
    <view class="tabbar-bg">
      <view class="tabbar-curve"></view>
    </view>
    
    <!-- 左侧 - 首页 -->
    <view class="tab-item" :class="{ active: currentTab === 0 }" @tap="switchTab(0)">
      <image class="tab-icon" :src="currentTab === 0 ? homeSelectedIcon : homeNormalIcon" mode="aspectFit"></image>
      <text class="tab-text">首页</text>
    </view>
    
    <!-- 中间 - 问答（凸起） -->
    <view class="tab-item center-tab" @tap="switchTab(1)">
      <image class="center-icon" :src="currentTab === 1 ? chatSelectedIcon : chatNormalIcon" mode="aspectFit"></image>
      <text class="tab-text center-text">问答</text>
    </view>
    
    <!-- 右侧 - 我的 -->
    <view class="tab-item" :class="{ active: currentTab === 2 }" @tap="switchTab(2)">
      <image class="tab-icon" :src="currentTab === 2 ? profileSelectedIcon : profileNormalIcon" mode="aspectFit"></image>
      <text class="tab-text">我的</text>
    </view>
  </view>

  <!-- 家长模式底部栏 - 现代简洁风格 -->
  <view v-else-if="isGuardianMode" class="custom-tabbar guardian-tabbar">
    <!-- 左侧 - 首页 -->
    <view class="guardian-tab-item" :class="{ active: currentTab === 0 }" @tap="switchTab(0)">
      <text class="guardian-tab-icon" :class="{ active: currentTab === 0 }">🏠</text>
      <text class="guardian-tab-text" :class="{ active: currentTab === 0 }">首页</text>
    </view>
    
    <!-- 中间 - 问答（大圆形按钮） -->
    <view class="guardian-tab-item guardian-center-tab" :class="{ active: currentTab === 1 }" @tap="switchTab(1)">
      <view class="guardian-center-button" :class="{ active: currentTab === 1 }">
        <text class="guardian-center-icon">💬</text>
      </view>
      <text class="guardian-tab-text guardian-center-text" :class="{ active: currentTab === 1 }">问答</text>
    </view>
    
    <!-- 右侧 - 我的 -->
    <view class="guardian-tab-item" :class="{ active: currentTab === 2 }" @tap="switchTab(2)">
      <text class="guardian-tab-icon" :class="{ active: currentTab === 2 }">👤</text>
      <text class="guardian-tab-text" :class="{ active: currentTab === 2 }">我的</text>
    </view>
  </view>

  <!-- 青少年模式底部栏 -->
  <view v-else class="custom-tabbar">
    <!-- 弧形背景 -->
    <view class="tabbar-bg">
      <view class="tabbar-curve"></view>
    </view>
    
    <!-- 左侧 - 首页 -->
    <view class="tab-item" :class="{ active: currentTab === 0 }" @tap="switchTab(0)">
      <image class="tab-icon" :src="currentTab === 0 ? homeSelectedIcon : homeNormalIcon" mode="aspectFit"></image>
      <text class="tab-text">首页</text>
    </view>
    
    <!-- 中间 - 问答（凸起） -->
    <view class="tab-item center-tab" @tap="switchTab(1)">
      <image class="center-icon" :src="currentTab === 1 ? chatSelectedIcon : chatNormalIcon" mode="aspectFit"></image>
      <text class="tab-text center-text">问答</text>
    </view>
    
    <!-- 右侧 - 我的 -->
    <view class="tab-item" :class="{ active: currentTab === 2 }" @tap="switchTab(2)">
      <image class="tab-icon" :src="currentTab === 2 ? profileSelectedIcon : profileNormalIcon" mode="aspectFit"></image>
      <text class="tab-text">我的</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const props = defineProps({
  current: {
    type: Number,
    default: 0
  }
})

const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)

// 页面路径
const tabPages = [
  '/pages/index/index',
  '/pages/chat/chat-complete',
  '/pages/profile/profile'
]

// 根据当前页面路径自动判断选中状态
const currentTab = computed(() => {
  const pages = getCurrentPages()
  if (pages.length > 0) {
    const currentPage = pages[pages.length - 1]
    const route = '/' + currentPage.route
    const index = tabPages.findIndex(path => route === path)
    return index >= 0 ? index : props.current
  }
  return props.current
})

// 根据用户角色选择图标
const isChildMode = computed(() => userRole.value === 'child_under_12')
const isGuardianMode = computed(() => userRole.value === 'guardian')

// 首页图标
const homeNormalIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_index_normal.png' : '/static/tabbar/home.png'
)
const homeSelectedIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_index_selected.png' : '/static/tabbar/home-active.png'
)

// 问答图标
const chatNormalIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_que_normal.png' : '/static/tabbar/chat.png'
)
const chatSelectedIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_que_selected.png' : '/static/tabbar/chat-active.png'
)

// 我的图标
const profileNormalIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_home_normal.png' : '/static/tabbar/profile.png'
)
const profileSelectedIcon = computed(() => 
  isChildMode.value ? '/static/ch/ch_home_selected.png' : '/static/tabbar/profile-active.png'
)

const switchTab = (index) => {
  if (currentTab.value === index) return
  uni.switchTab({
    url: tabPages[index]
  })
}

onMounted(() => {
  // 隐藏原生 tabBar
  uni.hideTabBar()
})
</script>

<style scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120rpx;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 999;
}

.tabbar-bg {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background: #D5A874;
  border-radius: 30rpx 30rpx 0 0;
}

.tabbar-curve {
  position: absolute;
  top: -35rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 140rpx;
  height: 70rpx;
  background: #D5A874;
  border-radius: 70rpx 70rpx 0 0;
}

.tabbar-curve::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: -30rpx;
  width: 30rpx;
  height: 30rpx;
  background: transparent;
  border-bottom-right-radius: 30rpx;
  box-shadow: 10rpx 10rpx 0 #D5A874;
}

.tabbar-curve::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: -30rpx;
  width: 30rpx;
  height: 30rpx;
  background: transparent;
  border-bottom-left-radius: 30rpx;
  box-shadow: -10rpx 10rpx 0 #D5A874;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100rpx;
  position: relative;
  z-index: 10;
}

.tab-icon {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 6rpx;
}

.tab-text {
  font-size: 22rpx;
  color: #7A7E83;
}

.tab-item.active .tab-text {
  color: #602F27;
  font-weight: 500;
}

/* 中间凸起按钮 */
.center-tab {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.center-icon {
  width: 100rpx;
  height: 100rpx;
  margin-top: -60rpx;
}

.center-text {
  font-size: 22rpx;
  color: #602F27;
}

/* ========== 家长模式底部栏 - 现代简洁风格 ========== */
.guardian-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background: white;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-bottom: env(safe-area-inset-bottom);
  padding-top: 10rpx;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.08);
  z-index: 999;
}

.guardian-tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  position: relative;
  padding-bottom: 8rpx;
}

.guardian-tab-icon {
  font-size: 40rpx;
  transition: all 0.3s ease;
  color: #9CA3AF;
}

.guardian-tab-icon.active {
  color: #3B82F6;
}

.guardian-tab-text {
  font-size: 22rpx;
  color: #9CA3AF;
  transition: all 0.3s ease;
}

.guardian-tab-text.active {
  color: #3B82F6;
  font-weight: 600;
}

/* 中间大圆形按钮 */
.guardian-center-tab {
  position: relative;
  margin-bottom: -20rpx;
}

.guardian-center-button {
  width: 90rpx;
  height: 90rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
  margin-bottom: 8rpx;
}

.guardian-center-button.active {
  background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
  box-shadow: 0 6rpx 20rpx rgba(59, 130, 246, 0.5);
  transform: scale(1.05);
}

.guardian-center-icon {
  font-size: 44rpx;
  color: white;
}

.guardian-center-text {
  margin-bottom: 10px;
  color: #3B82F6;
  font-weight: 600;
}
</style>
