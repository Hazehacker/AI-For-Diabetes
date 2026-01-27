<template>
  <view v-if="visible" class="drawer-overlay" @tap="handleClose">
    <view class="drawer-content" @tap.stop :class="{ 'show': visible }">
      <!-- 头部 -->
      <view class="drawer-header">
        <view class="header-top">
          <text class="header-title">个人中心</text>
          <view class="close-btn" @tap="handleClose">
            <text class="icon">✕</text>
          </view>
        </view>
        <view class="user-info">
          <image class="avatar" :src="userAvatar" mode="aspectFill"></image>
          <view class="info">
            <text class="nickname">{{ nickname }}</text>
            <text class="username">@{{ username }}</text>
          </view>
        </view>
      </view>

      <!-- 个人信息 -->
      <view class="info-section">
        <view class="section-header">
          <text class="icon">👤</text>
          <text class="title">个人信息</text>
        </view>
        
        <view class="form-item">
          <text class="label">昵称</text>
          <input 
            class="input" 
            v-model="editForm.nickname"
            placeholder="请输入昵称"
          />
        </view>

        <view class="form-item">
          <text class="label">生日</text>
          <picker 
            mode="date" 
            :value="editForm.birthday"
            @change="onBirthdayChange"
          >
            <view class="input picker">
              {{ editForm.birthday || '请选择生日' }}
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">手机号</text>
          <text class="value">{{ phone || '未设置' }}</text>
        </view>

        <button class="save-btn" @tap="handleSave">
          <text class="icon">💾</text>
          <text>保存修改</text>
        </button>
      </view>

      <!-- 快速功能 -->
      <view class="function-section">
        <view class="section-header">
          <text class="icon">⚡</text>
          <text class="title">快速功能</text>
        </view>
        
        <view class="function-item" @tap="goToCheckin">
          <text class="icon">📅</text>
          <text class="text">打卡记录</text>
          <text class="arrow">›</text>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="logout-section">
        <button class="logout-btn" @tap="handleLogout">
          <text class="icon">🚪</text>
          <text>退出登录</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '@/store/user'

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['close', 'logout', 'checkin'])

const userStore = useUserStore()

const editForm = ref({
  nickname: '',
  birthday: ''
})

// 个人中心头像与聊天页保持一致
const userAvatar = computed(() => 'https://s.coze.cn/image/es6fUICmNgw/')
const nickname = computed(() => userStore.nickname)
const username = computed(() => userStore.userInfo?.username || 'user')
const phone = computed(() => userStore.userInfo?.phone || userStore.userInfo?.username)

watch(() => props.visible, (val) => {
  if (val) {
    editForm.value.nickname = userStore.nickname
    editForm.value.birthday = userStore.userInfo?.birthday || ''
  }
})

const handleClose = () => {
  emit('close')
}

const onBirthdayChange = (e) => {
  editForm.value.birthday = e.detail.value
}

const handleSave = () => {
  const updatedInfo = {
    ...userStore.userInfo,
    nickname: editForm.value.nickname,
    birthday: editForm.value.birthday
  }
  
  uni.setStorageSync('userInfo', updatedInfo)
  userStore.userInfo = updatedInfo

  uni.showToast({
    title: '保存成功',
    icon: 'success'
  })
}

const goToCheckin = () => {
  // 由外层页面决定如何展示打卡记录（例如弹出日历弹窗）
  handleClose()
  emit('checkin')
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        emit('logout')
      }
    }
  })
}
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  /* 调低层级，避免遮挡内置 date picker 弹出的选择面板（uni H5 picker 默认 z-index 约为 999） */
  z-index: 900;
}

.drawer-content {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 600rpx;
  background: white;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
}

.drawer-content.show {
  transform: translateX(0);
}

.drawer-header {
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  padding: 48rpx 32rpx;
  color: white;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
}

.close-btn {
  width: 56rpx;
  height: 56rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn .icon {
  font-size: 32rpx;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
}

.info {
  flex: 1;
}

.nickname {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.username {
  display: block;
  font-size: 26rpx;
  opacity: 0.9;
}

.info-section,
.function-section {
  padding: 32rpx;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.section-header .icon {
  font-size: 32rpx;
}

.section-header .title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
}

.form-item {
  margin-bottom: 24rpx;
}

.label {
  display: block;
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 12rpx;
}

.input {
  width: 100%;
  padding: 24rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  font-size: 28rpx;
}

.value {
  display: block;
  padding: 24rpx;
  background: #f3f4f6;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #9ca3af;
}

.save-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-top: 32rpx;
}

.function-item {
  display: flex;
  align-items: center;
  padding: 32rpx 24rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
}

.function-item .icon {
  font-size: 40rpx;
  margin-right: 24rpx;
}

.function-item .text {
  flex: 1;
  font-size: 30rpx;
  color: #1f2937;
}

.function-item .arrow {
  font-size: 48rpx;
  color: #d1d5db;
}

.logout-section {
  padding: 0 32rpx 48rpx;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  background: #fef2f2;
  color: #ef4444;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}
</style>
