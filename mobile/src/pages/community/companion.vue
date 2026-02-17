<template>
  <view class="companion-page">
    <!-- 顶部Tab切换 -->
    <view class="tab-bar">
      <view 
        class="tab-item"
        :class="{ active: currentTab === 'square' }"
        @tap="switchTab('square')"
      >
        <text class="tab-text">广场</text>
      </view>
      <view 
        class="tab-item"
        :class="{ active: currentTab === 'friends' }"
        @tap="switchTab('friends')"
      >
        <text class="tab-text">好友</text>
        <view v-if="unreadCount > 0" class="badge">{{ unreadCount }}</view>
      </view>
    </view>

    <!-- 广场页面 -->
    <view v-if="currentTab === 'square'" class="square-content">
      <!-- 分类入口 -->
      <view class="categories-section">
        <scroll-view class="categories-scroll" scroll-x>
          <view class="categories-list">
            <view 
              v-for="cat in categories" 
              :key="cat.id"
              class="category-item"
              :class="{ selected: selectedCategory === cat.id }"
              @tap="goToCategory(cat.id)"
            >
              <view class="category-icon" :style="{ background: cat.color }">
                <image class="icon-img" :src="cat.icon" mode="aspectFit"></image>
              </view>
              <text class="category-name">{{ cat.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 动态列表 -->
      <view class="posts-list">
        <view 
          v-for="post in sortedPosts" 
          :key="post.id"
          class="post-card"
          @tap="goToPostDetail(post.id)"
        >
          <!-- 作者信息 -->
          <view class="post-header">
            <view class="author-info">
              <text class="author-avatar">{{ post.author.avatar }}</text>
              <view class="author-details">
                <text class="author-name">{{ post.author.name }}</text>
                <view class="author-tags">
                  <text 
                    v-for="(tag, index) in post.author.tags" 
                    :key="index"
                    class="tag"
                  >
                    {{ tag }}
                  </text>
                </view>
              </view>
            </view>
            <text class="post-time">{{ formatTime(post.created_at) }}</text>
          </view>

          <!-- 动态内容 -->
          <view class="post-content">
            <text class="content-text">{{ post.content }}</text>
            
            <!-- 图片 -->
            <view v-if="post.images && post.images.length > 0" class="post-images">
              <text 
                v-for="(img, index) in post.images" 
                :key="index"
                class="post-image"
              >
                {{ img }}
              </text>
            </view>

            <!-- 分类标签 -->
            <view class="post-category">
              <text class="category-tag">#{{ post.categoryName }}</text>
            </view>
          </view>

          <!-- 互动区 -->
          <view class="post-actions">
            <view class="action-item" @tap="likePost(post.id)">
              <text class="action-icon" :class="{ liked: post.liked }">{{ post.liked ? '❤️' : '🤍' }}</text>
              <text class="action-text">{{ post.likes }}</text>
            </view>
            <view class="action-item">
              <text class="action-icon">💬</text>
              <text class="action-text">{{ post.comments }}</text>
            </view>
            <view class="action-item">
              <text class="action-icon">🔗</text>
              <text class="action-text">分享</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 发布按钮 -->
      <view class="fab" @tap="showPublishDialog">
        <image class="fab-icon" src="/static/ch/ch_fr_pencil.png" mode="aspectFit"></image>
      </view>
    </view>

    <!-- 好友页面 -->
    <view v-if="currentTab === 'friends'" class="friends-content">
      <view class="friends-list">
        <view 
          v-for="friend in friends" 
          :key="friend.id"
          class="friend-item"
          @tap="goToChat(friend)"
        >
          <view class="friend-avatar-wrapper">
            <text class="friend-avatar">{{ friend.avatar }}</text>
            <view v-if="friend.online" class="online-dot"></view>
          </view>
          
          <view class="friend-info">
            <view class="friend-header">
              <text class="friend-name">{{ friend.name }}</text>
              <text class="friend-time">{{ formatTime(friend.lastMessageTime) }}</text>
            </view>
            <text class="friend-signature">{{ friend.lastMessage || friend.signature }}</text>
          </view>

          <view v-if="friend.unreadCount > 0" class="unread-badge">
            {{ friend.unreadCount }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCompanionStore } from '@/store/companion'
import { storeToRefs } from 'pinia'

const companionStore = useCompanionStore()
const { currentTab, sortedPosts, friends, categories, unreadCount, selectedCategory } = storeToRefs(companionStore)

// 切换Tab
const switchTab = (tab) => {
  companionStore.setCurrentTab(tab)
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return ''
  
  const now = new Date()
  const time = new Date(date)
  const diff = now - time
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  const month = time.getMonth() + 1
  const day = time.getDate()
  return `${month}-${day}`
}

// 点赞动态
const likePost = (postId) => {
  companionStore.likePost(postId)
}

// 跳转到分类页面（实现分类筛选）
const goToCategory = (categoryId) => {
  if (companionStore.selectedCategory === categoryId) {
    // 如果点击的是当前选中的分类，则取消筛选
    companionStore.clearCategoryFilter()
  } else {
    // 否则设置新的分类筛选
    companionStore.setSelectedCategory(categoryId)
  }
}

// 跳转到发布页面
const showPublishDialog = () => {
  uni.navigateTo({
    url: '/pages/community/publish'
  })
}

// 跳转到帖子详情
const goToPostDetail = (postId) => {
  uni.navigateTo({
    url: `/pages/community/post-detail?postId=${postId}`
  })
}

// 分享帖子
const sharePost = (postId) => {
  uni.showToast({
    title: '分享功能开发中',
    icon: 'none'
  })
}

// 跳转到聊天页面
const goToChat = (friend) => {
  uni.navigateTo({
    url: `/pages/community/chat?friendId=${friend.id}&friendName=${friend.name}`
  })
}

onMounted(() => {
  // 生成模拟数据
  if (companionStore.posts.length === 0) {
    companionStore.generateMockData()
  }
})
</script>

<style scoped>
.companion-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
}

/* Tab栏 */
.tab-bar {
  display: flex;
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.tab-item {
  flex: 1;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.tab-item.active {
  color: #CB8E54;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background: #CB8E54;
  border-radius: 2rpx;
}

.tab-text {
  font-size: 32rpx;
  font-weight: 500;
}

.badge {
  position: absolute;
  top: 16rpx;
  right: 30%;
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  background: #EF4444;
  color: white;
  border-radius: 16rpx;
  font-size: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 广场内容 */
.square-content {
  padding-bottom: 120rpx;
}

/* 分类入口 */
.categories-section {
  background: #FFFEF7;
  padding: 24rpx 0;
  margin-bottom: 16rpx;
  border-bottom: 1rpx solid #E3C7A4;
}

.categories-scroll {
  white-space: nowrap;
}

.categories-list {
  display: inline-flex;
  padding: 0 24rpx;
  gap: 28rpx;
  justify-content: space-between;
  width: calc(100% - 48rpx);
}

.category-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  position: relative;
}

.category-item.selected .category-icon {
  transform: scale(1.1);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.category-item.selected .category-name {
  color: #CB8E54;
  font-weight: 600;
}

.category-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-img {
  width: 60rpx;
  height: 60rpx;
}

/* 减肥成绩单图标特殊尺寸 */
.category-item:nth-child(2) .icon-img {
  width: 75rpx;
  height: 75rpx;
}

.category-name {
  font-size: 24rpx;
  color: #6B7280;
  transition: all 0.3s ease;
}

/* 动态列表 */
.posts-list {
  padding: 0 20rpx;
}

.post-card {
  background: #FFFEF7;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.author-info {
  display: flex;
  gap: 16rpx;
}

.author-avatar {
  font-size: 60rpx;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.author-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #1F2937;
}

.author-tags {
  display: flex;
  gap: 8rpx;
}

.tag {
  padding: 4rpx 12rpx;
  background: #F3F4F6;
  color: #6B7280;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.post-time {
  font-size: 24rpx;
  color: #9CA3AF;
}

.post-content {
  margin-bottom: 20rpx;
}

.content-text {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.6;
  display: block;
  margin-bottom: 16rpx;
}

.post-images {
  display: flex;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.post-image {
  width: 200rpx;
  height: 200rpx;
  background: #F3F4F6;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80rpx;
}

.post-category {
  margin-top: 12rpx;
}

.category-tag {
  font-size: 24rpx;
  color: #CB8E54;
}

.post-actions {
  display: flex;
  gap: 48rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #F3F4F6;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.action-icon {
  font-size: 36rpx;
}

.action-icon.liked {
  animation: heartbeat 0.3s;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.action-text {
  font-size: 24rpx;
  color: #6B7280;
}

/* 好友列表 */
.friends-content {
  padding: 20rpx;
}

.friends-list {
  background: #FFFEF7;
  border-radius: 20rpx;
  overflow: hidden;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  border-bottom: 1rpx solid #E3C7A4;
  position: relative;
}

.friend-item:last-child {
  border-bottom: none;
}

.friend-avatar-wrapper {
  position: relative;
}

.friend-avatar {
  font-size: 80rpx;
}

.online-dot {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 20rpx;
  height: 20rpx;
  background: #10B981;
  border: 3rpx solid white;
  border-radius: 50%;
}

.friend-info {
  flex: 1;
}

.friend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.friend-name {
  font-size: 30rpx;
  font-weight: 500;
  color: #1F2937;
}

.friend-time {
  font-size: 22rpx;
  color: #9CA3AF;
}

.friend-signature {
  font-size: 26rpx;
  color: #6B7280;
}

.unread-badge {
  min-width: 36rpx;
  height: 36rpx;
  padding: 0 8rpx;
  background: #EF4444;
  color: white;
  border-radius: 18rpx;
  font-size: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* 发布按钮 */
.fab {
  position: fixed;
  bottom: 100rpx;
  right: 40rpx;
  width: 120rpx;
  height: 120rpx;
  background: rgba(246, 211, 135, 0.8);
  backdrop-filter: blur(20rpx);
  -webkit-backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8rpx 32rpx rgba(203, 142, 84, 0.2),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
  z-index: 100;
}

.fab-icon {
  width: 56rpx;
  height: 56rpx;
}
</style>
