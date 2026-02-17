<template>
  <view class="custom-tabbar">
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
</style>
