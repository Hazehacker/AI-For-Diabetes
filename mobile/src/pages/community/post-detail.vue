<template>
  <view class="post-detail-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack" @error="onImageError"></image>
      <text class="nav-title">帖子详情</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 帖子内容 -->
    <view v-if="post" class="post-content">
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

      <!-- 帖子正文 -->
      <view class="post-body">
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
        <view class="action-item" @tap="likePost">
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

    <!-- 评论区 -->
    <view class="comments-section">
      <view class="section-header">
        <text class="section-title">评论 ({{ comments.length }})</text>
      </view>

      <!-- 评论列表 -->
      <view v-if="comments.length > 0" class="comments-list">
        <view 
          v-for="comment in comments" 
          :key="comment.id"
          class="comment-item"
        >
          <text class="comment-avatar">{{ comment.author.avatar }}</text>
          <view class="comment-content">
            <view class="comment-header">
              <text class="comment-author">{{ comment.author.name }}</text>
              <text class="comment-time">{{ formatTime(comment.created_at) }}</text>
            </view>
            <text class="comment-text">{{ comment.content }}</text>
            
            <!-- 回复按钮 -->
            <view class="comment-actions">
              <text class="reply-btn" @tap="replyTo(comment)">回复</text>
              <view class="like-btn" @tap="likeComment(comment.id)">
                <text>{{ comment.liked ? '❤️' : '🤍' }}</text>
                <text class="like-count">{{ comment.likes }}</text>
              </view>
            </view>

            <!-- 子评论 -->
            <view v-if="comment.replies && comment.replies.length > 0" class="replies-list">
              <view 
                v-for="reply in comment.replies" 
                :key="reply.id"
                class="reply-item"
              >
                <text class="reply-author">{{ reply.author.name }}</text>
                <text v-if="reply.replyTo" class="reply-to">回复 {{ reply.replyTo }}</text>
                <text class="reply-text">：{{ reply.content }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 暂无评论 -->
      <view v-else class="no-comments">
        <text class="no-comments-icon">💬</text>
        <text class="no-comments-text">暂无评论，快来抢沙发吧~</text>
      </view>
    </view>

    <!-- 底部评论输入框 -->
    <view class="comment-input-bar">
      <view class="input-wrapper">
        <input
          v-model="commentText"
          class="comment-input"
          :placeholder="replyPlaceholder"
          @confirm="submitComment"
        />
      </view>
      <view class="send-btn" @tap="submitComment">
        <text class="send-text">发送</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCompanionStore } from '@/store/companion'

const companionStore = useCompanionStore()

// 获取帖子ID
const postId = ref(null)
const post = ref(null)
const comments = ref([])
const commentText = ref('')
const replyTarget = ref(null)

// 回复占位符
const replyPlaceholder = computed(() => {
  if (replyTarget.value) {
    return `回复 ${replyTarget.value.author.name}...`
  }
  return '写下你的评论...'
})

// 返回
const goBack = () => {
  uni.navigateBack()
}

// 图片加载错误处理
const onImageError = (e) => {
  console.log('Image load error:', e)
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

// 点赞帖子
const likePost = () => {
  if (post.value) {
    companionStore.likePost(post.value.id)
    // 更新本地状态
    post.value.liked = !post.value.liked
    post.value.likes += post.value.liked ? 1 : -1
  }
}

// 点赞评论
const likeComment = (commentId) => {
  const comment = comments.value.find(c => c.id === commentId)
  if (comment) {
    comment.liked = !comment.liked
    comment.likes += comment.liked ? 1 : -1
  }
}

// 回复评论
const replyTo = (comment) => {
  replyTarget.value = comment
}

// 提交评论
const submitComment = () => {
  if (!commentText.value.trim()) {
    uni.showToast({
      title: '请输入评论内容',
      icon: 'none'
    })
    return
  }

  const newComment = {
    id: Date.now(),
    author: {
      id: 'current_user',
      name: '我',
      avatar: '👤'
    },
    content: commentText.value,
    created_at: new Date(),
    likes: 0,
    liked: false,
    replies: []
  }

  if (replyTarget.value) {
    // 添加为回复
    const targetComment = comments.value.find(c => c.id === replyTarget.value.id)
    if (targetComment) {
      if (!targetComment.replies) {
        targetComment.replies = []
      }
      targetComment.replies.push({
        id: Date.now(),
        author: newComment.author,
        replyTo: replyTarget.value.author.name,
        content: commentText.value,
        created_at: new Date()
      })
    }
    replyTarget.value = null
  } else {
    // 添加为新评论
    comments.value.unshift(newComment)
  }

  // 更新store中的评论数
  companionStore.addComment(postId.value, newComment)

  commentText.value = ''
  
  uni.showToast({
    title: '评论成功',
    icon: 'success'
  })
}

// 加载帖子数据
const loadPost = () => {
  const foundPost = companionStore.posts.find(p => p.id === postId.value)
  if (foundPost) {
    post.value = { ...foundPost }
    // 加载评论（从store的postComments中获取）
    const storedComments = companionStore.postComments[postId.value] || []
    comments.value = [...storedComments]
  }
}

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = currentPage.$page?.options || currentPage.options || {}
  
  postId.value = parseInt(options.postId)
  loadPost()
})
</script>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding-bottom: 120rpx;
}

/* 导航栏 */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.nav-back-icon {
  width: 80rpx;
  height: 80rpx;
  display: block;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.nav-placeholder {
  width: 80rpx;
}

/* 帖子内容 */
.post-content {
  background: #FFFEF7;
  padding: 32rpx;
  margin-bottom: 16rpx;
  border-radius: 20rpx;
  margin: 16rpx 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.author-info {
  display: flex;
  gap: 16rpx;
}

.author-avatar {
  font-size: 80rpx;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.author-name {
  font-size: 32rpx;
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
  font-size: 22rpx;
}

.post-time {
  font-size: 24rpx;
  color: #9CA3AF;
}

.post-body {
  margin-bottom: 24rpx;
}

.content-text {
  font-size: 30rpx;
  color: #374151;
  line-height: 1.8;
  display: block;
  margin-bottom: 20rpx;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
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
  margin-top: 16rpx;
}

.category-tag {
  font-size: 26rpx;
  color: #CB8E54;
}

.post-actions {
  display: flex;
  gap: 48rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid #F3F4F6;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.action-icon {
  font-size: 40rpx;
}

.action-icon.liked {
  animation: heartbeat 0.3s;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.action-text {
  font-size: 26rpx;
  color: #6B7280;
}

/* 评论区 */
.comments-section {
  background: #FFFEF7;
  padding: 32rpx;
  border-radius: 20rpx;
  margin: 16rpx 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.section-header {
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #1F2937;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.comment-item {
  display: flex;
  gap: 16rpx;
}

.comment-avatar {
  font-size: 60rpx;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.comment-author {
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2937;
}

.comment-time {
  font-size: 22rpx;
  color: #9CA3AF;
}

.comment-text {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.6;
  display: block;
  margin-bottom: 12rpx;
}

.comment-actions {
  display: flex;
  gap: 32rpx;
  align-items: center;
}

.reply-btn {
  font-size: 24rpx;
  color: #CB8E54;
}

.like-btn {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 24rpx;
}

.like-count {
  color: #9CA3AF;
}

/* 回复列表 */
.replies-list {
  background: #F9FAFB;
  border-radius: 12rpx;
  padding: 16rpx;
  margin-top: 12rpx;
}

.reply-item {
  font-size: 26rpx;
  line-height: 1.6;
  margin-bottom: 8rpx;
}

.reply-item:last-child {
  margin-bottom: 0;
}

.reply-author {
  color: #CB8E54;
  font-weight: 500;
}

.reply-to {
  color: #9CA3AF;
}

.reply-text {
  color: #374151;
}

/* 暂无评论 */
.no-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.no-comments-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.no-comments-text {
  font-size: 28rpx;
  color: #9CA3AF;
}

/* 底部评论输入框 */
.comment-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 32rpx;
  background: #FFFEF7;
  border-top: 1rpx solid #E3C7A4;
  box-shadow: 0 -4rpx 12rpx rgba(203, 142, 84, 0.1);
}

.input-wrapper {
  flex: 1;
  background: #F3F4F6;
  border-radius: 36rpx;
  padding: 0 24rpx;
}

.comment-input {
  height: 72rpx;
  font-size: 28rpx;
  color: #1F2937;
}

.send-btn {
  min-width: 120rpx;
  height: 72rpx;
  padding: 0 32rpx;
  background: rgba(246, 211, 135, 0.8);
  backdrop-filter: blur(20rpx);
  -webkit-backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8rpx 32rpx rgba(203, 142, 84, 0.2),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
}

.send-text {
  font-size: 28rpx;
  color: #602F27;
  font-weight: 500;
}
</style>
