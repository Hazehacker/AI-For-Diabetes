<template>
  <view class="profile-container">
    <!-- 头部信息 -->
    <view class="profile-header">
      <image class="avatar" src="/static/logo.png" mode="aspectFit"></image>
      <text class="nickname">{{ userStore.nickname }}</text>
      <text class="username">@{{ userStore.userInfo?.username || 'user' }}</text>
    </view>

    <!-- 个人信息 -->
    <view class="info-section">
      <view class="section-title">
        <text class="title-icon">👤</text>
        <text class="title-text">个人信息</text>
      </view>

      <view class="info-item">
        <text class="info-label">昵称</text>
        <input 
          class="info-input" 
          v-model="editForm.nickname"
          placeholder="请输入昵称"
        />
      </view>

      <view class="info-item">
        <text class="info-label">生日</text>
        <picker 
          mode="date" 
          :value="editForm.birthday"
          @change="onBirthdayChange"
        >
          <view class="info-input">
            {{ editForm.birthday || '请选择生日' }}
          </view>
        </picker>
      </view>

      <view class="info-item">
        <text class="info-label">手机号</text>
        <text class="info-value">{{ userStore.userInfo?.username || '未设置' }}</text>
      </view>

      <button class="save-btn" @tap="saveProfile">
        <text class="btn-icon">💾</text>
        <text>保存修改</text>
      </button>
    </view>

    <!-- 健康管理 -->
    <view class="function-section">
      <view class="section-title">
        <text class="title-icon">💊</text>
        <text class="title-text">健康管理</text>
      </view>

      <view class="function-item" @tap="goToGlucoseReport">
        <text class="function-icon">📈</text>
        <text class="function-text">血糖管理报告</text>
        <text class="function-arrow">›</text>
      </view>

      <view class="function-item" @tap="goToHealthPlan">
        <text class="function-icon">📋</text>
        <text class="function-text">健康计划</text>
        <text class="function-arrow">›</text>
      </view>

      <view class="function-item" @tap="goToCreatePlan">
        <text class="function-icon">➕</text>
        <text class="function-text">创建计划</text>
        <text class="function-arrow">›</text>
      </view>

      <view class="function-item" @tap="goToDashboard">
        <text class="function-icon">📊</text>
        <text class="function-text">健康仪表盘</text>
        <text class="function-arrow">›</text>
      </view>
    </view>

    <!-- 个人资料 -->
    <view class="function-section">
      <view class="section-title">
        <text class="title-icon">📝</text>
        <text class="title-text">个人资料</text>
      </view>

      <view class="function-item" @tap="goToBasicInfo">
        <text class="function-icon">🏥</text>
        <text class="function-text">基础信息</text>
        <text class="function-arrow">›</text>
      </view>

      <view class="function-item" @tap="goToDailyCheckin">
        <text class="function-icon">✅</text>
        <text class="function-text">每日签到</text>
        <text class="function-arrow">›</text>
      </view>
    </view>

    <!-- 系统设置 -->
    <view class="function-section">
      <view class="section-title">
        <text class="title-icon">⚙️</text>
        <text class="title-text">系统设置</text>
      </view>

      <view class="function-item" @tap="goToRoleSwitcher">
        <text class="function-icon">🔄</text>
        <text class="function-text">角色切换</text>
        <text class="function-arrow">›</text>
      </view>

      <view class="function-item" @tap="goToCheckin">
        <text class="function-icon">📅</text>
        <text class="function-text">打卡记录</text>
        <text class="function-arrow">›</text>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @tap="handleLogout">
        <text class="btn-icon">🚪</text>
        <text>退出登录</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const editForm = ref({
  nickname: '',
  birthday: ''
})

onMounted(() => {
  editForm.value.nickname = userStore.nickname
  editForm.value.birthday = userStore.userInfo?.birthday || ''
})

const onBirthdayChange = (e) => {
  editForm.value.birthday = e.detail.value
}

const saveProfile = () => {
  // 保存用户信息
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

const goToHealthPlan = () => {
  uni.navigateTo({
    url: '/pages/health-plan/index'
  })
}

const goToCreatePlan = () => {
  uni.navigateTo({
    url: '/pages/health-plan/create'
  })
}

const goToDashboard = () => {
  uni.navigateTo({
    url: '/pages/dashboard/dashboard'
  })
}

const goToRoleSwitcher = () => {
  uni.navigateTo({
    url: '/pages/dashboard/role-switcher'
  })
}

const goToCheckin = () => {
  uni.navigateTo({
    url: '/pages/checkin/checkin'
  })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  padding: 40rpx;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
  background: white;
  border-radius: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.15);
}

.avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 80rpx;
  margin-bottom: 32rpx;
  border: 6rpx solid #969FFF;
}

.nickname {
  font-size: 40rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12rpx;
}

.username {
  font-size: 28rpx;
  color: #6b7280;
}

.info-section,
.function-section {
  background: white;
  border-radius: 32rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.15);
}

.section-title {
  display: flex;
  align-items: center;
  margin-bottom: 32rpx;
}

.title-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.title-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.info-item:last-of-type {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: #6b7280;
  width: 160rpx;
}

.info-input {
  flex: 1;
  font-size: 28rpx;
  color: #1f2937;
  text-align: right;
}

.info-value {
  flex: 1;
  font-size: 28rpx;
  color: #9ca3af;
  text-align: right;
}

.save-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  margin-top: 32rpx;
  box-shadow: 0 8rpx 30rpx rgba(150, 159, 255, 0.3);
}

.btn-icon {
  font-size: 32rpx;
}

.function-item {
  display: flex;
  align-items: center;
  padding: 32rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.function-item:last-child {
  border-bottom: none;
}

.function-icon {
  font-size: 40rpx;
  margin-right: 24rpx;
}

.function-text {
  flex: 1;
  font-size: 30rpx;
  color: #1f2937;
}

.function-arrow {
  font-size: 48rpx;
  color: #d1d5db;
}

.logout-section {
  padding: 0 0 40rpx;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  width: 100%;
  height: 88rpx;
  background: white;
  color: #ef4444;
  border-radius: 24rpx;
  font-size: 30rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 40rpx rgba(239, 68, 68, 0.15);
}
</style>
