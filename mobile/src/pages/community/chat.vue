<template>
  <view class="chat-page">
    <!-- 自定义导航栏 -->
    <view class="custom-nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack" @error="onImageError"></image>
      <text class="nav-title">{{ friendName }}</text>
      <view class="nav-placeholder"></view>
    </view>
    
    <!-- 消息列表 -->
    <scroll-view 
      class="messages-container" 
      scroll-y 
      :scroll-into-view="scrollToView"
      scroll-with-animation
    >
      <view 
        v-for="msg in messages" 
        :key="msg.id"
        :id="'msg-' + msg.id"
        class="message-item"
        :class="msg.sender === 'me' ? 'message-right' : 'message-left'"
      >
        <view v-if="msg.sender === 'friend'" class="message-avatar">
          <text class="avatar-text">{{ friendAvatar }}</text>
        </view>
        
        <view class="message-bubble" :class="msg.sender === 'me' ? 'bubble-primary' : 'bubble-white'">
          <text class="message-text">{{ msg.content }}</text>
          <text class="message-time">{{ formatTime(msg.timestamp) }}</text>
        </view>

        <view v-if="msg.sender === 'me'" class="message-avatar">
          <text class="avatar-text">😊</text>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区 -->
    <view class="input-area">
      <input 
        class="message-input"
        v-model="inputText"
        placeholder="输入消息..."
        confirm-type="send"
        @confirm="sendMessage"
      />
      <view class="send-btn" @tap="sendMessage">
        <text class="send-text">发送</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useCompanionStore } from '@/store/companion'
import { onLoad } from '@dcloudio/uni-app'

const companionStore = useCompanionStore()

const friendId = ref(null)
const friendName = ref('')
const friendAvatar = ref('👤')
const inputText = ref('')
const scrollToView = ref('')

// 获取消息列表
const messages = computed(() => {
  return companionStore.getChatMessages(friendId.value)
})

// 格式化时间
const formatTime = (date) => {
  const time = new Date(date)
  const hours = time.getHours().toString().padStart(2, '0')
  const minutes = time.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 返回
const goBack = () => {
  uni.navigateBack()
}

// 图片加载错误处理
const onImageError = (e) => {
  console.log('Image load error:', e)
}

// 发送消息
const sendMessage = () => {
  if (!inputText.value.trim()) return
  
  const message = companionStore.sendMessage(friendId.value, inputText.value.trim())
  inputText.value = ''
  
  // 滚动到底部
  nextTick(() => {
    scrollToView.value = 'msg-' + message.id
  })
  
  // 模拟对方回复
  setTimeout(() => {
    const replies = [
      '收到！',
      '好的',
      '我也是这样想的',
      '加油！',
      '一起努力',
      '谢谢分享'
    ]
    const randomReply = replies[Math.floor(Math.random() * replies.length)]
    const replyMsg = companionStore.receiveMessage(friendId.value, randomReply)
    
    nextTick(() => {
      scrollToView.value = 'msg-' + replyMsg.id
    })
  }, 1000 + Math.random() * 2000)
}

onLoad((options) => {
  friendId.value = parseInt(options.friendId)
  friendName.value = options.friendName || '好友'
  
  // 设置导航栏标题
  uni.setNavigationBarTitle({
    title: friendName.value
  })
  
  // 标记消息已读
  companionStore.markMessagesAsRead(friendId.value)
  
  // 获取好友头像
  const friend = companionStore.friends.find(f => f.id === friendId.value)
  if (friend) {
    friendAvatar.value = friend.avatar
  }
  
  // 滚动到底部
  if (messages.value.length > 0) {
    nextTick(() => {
      scrollToView.value = 'msg-' + messages.value[messages.value.length - 1].id
    })
  }
})
</script>

<style scoped>
.chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
}

/* 自定义导航栏 */
.custom-nav-bar {
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

.messages-container {
  flex: 1;
  padding: 20rpx;
  overflow-y: auto;
  max-height: calc(100vh - 280rpx);
}

.message-item {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.message-item.message-right {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-text {
  font-size: 60rpx;
}

.message-bubble {
  max-width: 500rpx;
  padding: 20rpx 24rpx;
  border-radius: 16rpx;
  position: relative;
}

.bubble-white {
  background: #FFFEF7;
  border: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.bubble-primary {
  background: linear-gradient(135deg, #F6D387 0%, #CB8E54 100%);
  color: white;
}

.message-text {
  display: block;
  font-size: 28rpx;
  line-height: 1.5;
  word-wrap: break-word;
  margin-bottom: 8rpx;
}

.bubble-primary .message-text {
  color: white;
}

.message-time {
  display: block;
  font-size: 20rpx;
  color: #9CA3AF;
  text-align: right;
}

.bubble-primary .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.input-area {
  display: flex;
  gap: 16rpx;
  padding: 20rpx;
  background: #FFFEF7;
  border-top: 1rpx solid #E3C7A4;
  box-shadow: 0 -2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.message-input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  background: #F3F4F6;
  border-radius: 36rpx;
  font-size: 28rpx;
}

.send-btn {
  min-width: 120rpx;
  height: 60rpx;
  padding: 0 24rpx;
  background: rgba(246, 211, 135, 0.8);
  backdrop-filter: blur(20rpx);
  -webkit-backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 30rpx;
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
