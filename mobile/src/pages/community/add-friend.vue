<template>
  <!-- 儿童模式 -->
  <view v-if="userRole === 'child_under_12'" class="child-add-friend">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">添加朋友</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 搜索区域 -->
    <view class="search-section">
      <view class="search-card">
        <view class="search-header">
          <image class="search-icon" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
          <text class="search-title">找朋友</text>
        </view>
        <view class="search-input-area">
          <input 
            v-model="searchText" 
            class="search-input" 
            placeholder="输入朋友的用户名或ID"
            @input="onSearchInput"
          />
          <view class="search-btn" @tap="searchFriend">
            <image class="search-btn-icon" src="/static/ch/ch_play_watch.png" mode="aspectFit"></image>
          </view>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view v-if="searchResults.length > 0" class="results-section">
      <view class="results-header">
        <text class="results-title">🔍 找到了</text>
      </view>
      <view class="results-list">
        <view 
          v-for="user in searchResults" 
          :key="user.id"
          class="user-card"
        >
          <image class="user-avatar" :src="user.avatar" mode="aspectFit"></image>
          <view class="user-info">
            <text class="user-name">{{ user.name }}</text>
            <text class="user-desc">{{ user.signature || '这个人很神秘，什么都没写~' }}</text>
          </view>
          <view 
            class="add-btn" 
            :class="{ 'added': user.friendStatus === 'added', 'pending': user.friendStatus === 'pending' }"
            @tap="addFriend(user)"
          >
            <text class="add-text">{{ getFriendButtonText(user.friendStatus) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 推荐朋友 -->
    <view class="recommend-section">
      <view class="recommend-header">
        <text class="recommend-title">🌟 推荐朋友</text>
      </view>
      <view class="recommend-list">
        <view 
          v-for="user in recommendedFriends" 
          :key="user.id"
          class="user-card"
        >
          <image class="user-avatar" :src="user.avatar" mode="aspectFit"></image>
          <view class="user-info">
            <text class="user-name">{{ user.name }}</text>
            <text class="user-desc">{{ user.signature || '一起加油吧！' }}</text>
          </view>
          <view 
            class="add-btn" 
            :class="{ 'added': user.friendStatus === 'added', 'pending': user.friendStatus === 'pending' }"
            @tap="addFriend(user)"
          >
            <text class="add-text">{{ getFriendButtonText(user.friendStatus) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>

  <!-- 成人/青少年模式 -->
  <view v-else class="adult-add-friend">
    <!-- 导航栏 -->
    <view class="nav-bar-adult">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title-adult">添加朋友</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 搜索区域 -->
    <view class="search-section-adult">
      <view class="search-bar">
        <image class="search-icon-adult" src="/static/icons/search.png" mode="aspectFit"></image>
        <input 
          v-model="searchText" 
          class="search-input-adult" 
          placeholder="搜索用户名、手机号或ID"
          @input="onSearchInput"
        />
        <view class="search-btn-adult" @tap="searchFriend">
          <text class="search-btn-text">搜索</text>
        </view>
      </view>
    </view>

    <!-- 快速添加方式 -->
    <view class="quick-add-section">
      <text class="section-title">快速添加</text>
      <view class="quick-add-options">
        <view class="quick-option" @tap="scanQRCode">
          <view class="option-icon">
            <image src="/static/icons/qr-scan.png" mode="aspectFit"></image>
          </view>
          <text class="option-text">扫一扫</text>
        </view>
        <view class="quick-option" @tap="showMyQRCode">
          <view class="option-icon">
            <image src="/static/icons/qr-code.png" mode="aspectFit"></image>
          </view>
          <text class="option-text">我的二维码</text>
        </view>
        <view class="quick-option" @tap="addByPhone">
          <view class="option-icon">
            <image src="/static/icons/phone.png" mode="aspectFit"></image>
          </view>
          <text class="option-text">手机联系人</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view v-if="searchResults.length > 0" class="results-section-adult">
      <text class="section-title">搜索结果</text>
      <view class="results-list-adult">
        <view 
          v-for="user in searchResults" 
          :key="user.id"
          class="user-item-adult"
        >
          <image class="user-avatar-adult" :src="user.avatar" mode="aspectFit"></image>
          <view class="user-info-adult">
            <text class="user-name-adult">{{ user.name }}</text>
            <text class="user-desc-adult">{{ user.signature || '暂无个性签名' }}</text>
          </view>
          <view 
            class="add-btn-adult" 
            :class="{ 'added': user.friendStatus === 'added', 'pending': user.friendStatus === 'pending' }"
            @tap="addFriend(user)"
          >
            <text class="add-text-adult">{{ getFriendButtonText(user.friendStatus) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 推荐朋友 -->
    <view class="recommend-section-adult">
      <text class="section-title">可能认识的人</text>
      <view class="recommend-list-adult">
        <view 
          v-for="user in recommendedFriends" 
          :key="user.id"
          class="user-item-adult"
        >
          <image class="user-avatar-adult" :src="user.avatar" mode="aspectFit"></image>
          <view class="user-info-adult">
            <text class="user-name-adult">{{ user.name }}</text>
            <text class="user-desc-adult">{{ user.signature || '暂无个性签名' }}</text>
          </view>
          <view 
            class="add-btn-adult" 
            :class="{ 'added': user.friendStatus === 'added', 'pending': user.friendStatus === 'pending' }"
            @tap="addFriend(user)"
          >
            <text class="add-text-adult">{{ getFriendButtonText(user.friendStatus) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { useCompanionStore } from '@/store/companion'
import { storeToRefs } from 'pinia'

const dashboardStore = useDashboardStore()
const companionStore = useCompanionStore()
const { userRole } = storeToRefs(dashboardStore)

// 搜索相关
const searchText = ref('')
const searchResults = ref([])
const recommendedFriends = ref([])
const isSearching = ref(false)

// 模拟推荐朋友数据
const mockRecommendedFriends = [
  {
    id: 'rec1',
    name: '健康小助手',
    avatar: '/static/ch/ch_index_welcome.png',
    signature: '一起健康生活，科学管理血糖！',
    friendStatus: 'none'
  },
  {
    id: 'rec2', 
    name: '糖友阳光',
    avatar: '/static/ch/ch_index_welcome.png',
    signature: '积极面对，健康每一天',
    friendStatus: 'none'
  },
  {
    id: 'rec3',
    name: '运动达人',
    avatar: '/static/ch/ch_index_welcome.png', 
    signature: '运动是最好的良药',
    friendStatus: 'none'
  }
]

// 搜索输入处理
const onSearchInput = () => {
  if (searchText.value.length === 0) {
    searchResults.value = []
  }
}

// 搜索朋友
const searchFriend = async () => {
  if (!searchText.value.trim()) {
    uni.showToast({
      title: '请输入搜索内容',
      icon: 'none'
    })
    return
  }

  isSearching.value = true
  
  try {
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟搜索结果
    const mockResults = [
      {
        id: 'search1',
        name: searchText.value.includes('test') ? 'TestUser' : '糖友' + searchText.value,
        avatar: '/static/ch/ch_index_welcome.png',
        signature: '大家好，我是' + searchText.value,
        friendStatus: 'none'
      }
    ]
    
    searchResults.value = mockResults
    
    if (mockResults.length === 0) {
      uni.showToast({
        title: '未找到相关用户',
        icon: 'none'
      })
    }
  } catch (error) {
    uni.showToast({
      title: '搜索失败，请重试',
      icon: 'none'
    })
  } finally {
    isSearching.value = false
  }
}

// 添加朋友
const addFriend = async (user) => {
  if (user.friendStatus === 'added') {
    uni.showToast({
      title: '已经是好友了',
      icon: 'none'
    })
    return
  }
  
  if (user.friendStatus === 'pending') {
    uni.showToast({
      title: '已发送好友请求',
      icon: 'none'
    })
    return
  }

  try {
    // 模拟添加好友API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新用户状态
    user.friendStatus = 'pending'
    
    uni.showToast({
      title: userRole.value === 'child_under_12' ? '好友请求已发送！' : '已发送好友申请',
      icon: 'success'
    })
  } catch (error) {
    uni.showToast({
      title: '添加失败，请重试',
      icon: 'none'
    })
  }
}

// 获取按钮文本
const getFriendButtonText = (status) => {
  switch (status) {
    case 'added':
      return '已添加'
    case 'pending':
      return '已发送'
    default:
      return '添加'
  }
}

// 扫描二维码
const scanQRCode = () => {
  uni.scanCode({
    success: (res) => {
      uni.showToast({
        title: '扫码功能开发中',
        icon: 'none'
      })
    },
    fail: () => {
      uni.showToast({
        title: '扫码失败',
        icon: 'none'
      })
    }
  })
}

// 显示我的二维码
const showMyQRCode = () => {
  uni.showToast({
    title: '二维码功能开发中',
    icon: 'none'
  })
}

// 通过手机联系人添加
const addByPhone = () => {
  uni.showToast({
    title: '通讯录功能开发中',
    icon: 'none'
  })
}

// 返回上一页
const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

onMounted(() => {
  // 加载推荐朋友
  recommendedFriends.value = [...mockRecommendedFriends]
})
</script>

<style scoped>
/* ========== 儿童模式样式 ========== */
.child-add-friend {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
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
  padding: 10rpx;
  cursor: pointer;
}

.nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.nav-placeholder {
  width: 64rpx;
}

.search-section {
  padding: 24rpx;
}

.search-card {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
}

.search-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.search-icon {
  width: 60rpx;
  height: 60rpx;
}

.search-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #602F27;
}

.search-input-area {
  display: flex;
  gap: 12rpx;
}

.search-input {
  flex: 1;
  height: 80rpx;
  background: #FAF6F0;
  border: 2rpx solid #E3C7A4;
  border-radius: 20rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #602F27;
}

.search-btn {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #F6D387 0%, #E5BC64 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(246, 211, 135, 0.4);
}

.search-btn-icon {
  width: 40rpx;
  height: 40rpx;
}

.results-section, .recommend-section {
  padding: 0 24rpx 24rpx;
}

.results-header, .recommend-header {
  margin-bottom: 16rpx;
}

.results-title, .recommend-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.results-list, .recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #FFFEF7;
  border-radius: 20rpx;
  padding: 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(96, 47, 39, 0.08);
}

.user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #F6D387;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #602F27;
  margin-bottom: 6rpx;
}

.user-desc {
  display: block;
  font-size: 24rpx;
  color: #8E422F;
}

.add-btn {
  padding: 12rpx 24rpx;
  background: #AED581;
  border-radius: 30rpx;
  border: 2rpx solid #8BC34A;
  box-shadow: none;
  transform: scale(1);
  transition: transform 0.2s;
}

.add-btn:active {
  transform: scale(0.98);
}

.add-btn.pending {
  background: #E5E7EB;
  box-shadow: none;
}

.add-btn.added {
  background: #D1FAE5;
  box-shadow: none;
}

.add-text {
  font-size: 26rpx;
  color: #FFFFFF;
  font-weight: bold;
}

.add-btn.pending .add-text,
.add-btn.added .add-text {
  color: #6B7280;
}

/* ========== 成人/青少年模式样式 ========== */
.adult-add-friend {
  min-height: 100vh;
  background: #f8fafc;
}

.nav-bar-adult {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #ffffff;
  border-bottom: 1rpx solid #e2e8f0;
  box-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.1);
}

.nav-title-adult {
  font-size: 36rpx;
  font-weight: 600;
  color: #1e293b;
}

.search-section-adult {
  padding: 24rpx;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 16rpx 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #e2e8f0;
}

.search-icon-adult {
  width: 32rpx;
  height: 32rpx;
  margin-right: 12rpx;
}

.search-input-adult {
  flex: 1;
  font-size: 28rpx;
  color: #334155;
}

.search-btn-adult {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 16rpx;
  margin-left: 12rpx;
}

.search-btn-text {
  font-size: 26rpx;
  color: #ffffff;
  font-weight: 500;
}

.quick-add-section {
  padding: 0 24rpx 24rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16rpx;
}

.quick-add-options {
  display: flex;
  gap: 16rpx;
}

.quick-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #e2e8f0;
}

.option-icon {
  width: 64rpx;
  height: 64rpx;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-icon image {
  width: 32rpx;
  height: 32rpx;
}

.option-text {
  font-size: 24rpx;
  color: #64748b;
}

.results-section-adult, .recommend-section-adult {
  padding: 0 24rpx 24rpx;
}

.results-list-adult, .recommend-list-adult {
  background: #ffffff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid #e2e8f0;
}

.user-item-adult {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.user-item-adult:last-child {
  border-bottom: none;
}

.user-avatar-adult {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #f1f5f9;
}

.user-info-adult {
  flex: 1;
}

.user-name-adult {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 6rpx;
}

.user-desc-adult {
  display: block;
  font-size: 24rpx;
  color: #64748b;
}

.add-btn-adult {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 16rpx;
  box-shadow: 0 2rpx 4rpx rgba(16, 185, 129, 0.2);
}

.add-btn-adult.pending {
  background: #f1f5f9;
  box-shadow: none;
}

.add-btn-adult.added {
  background: #dcfce7;
  box-shadow: none;
}

.add-text-adult {
  font-size: 24rpx;
  color: #ffffff;
  font-weight: 500;
}

.add-btn-adult.pending .add-text-adult,
.add-btn-adult.added .add-text-adult {
  color: #64748b;
}
</style>
