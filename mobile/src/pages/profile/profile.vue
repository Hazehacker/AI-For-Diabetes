<template>
  <view class="page-container" :class="{ 'child-mode': userRole === 'child_under_12' }">
  <!-- 儿童模式：奶酪仓鼠风格 -->
  <view v-if="userRole === 'child_under_12'" class="child-profile">
    <!-- 顶部装饰已移除 -->

    <!-- 个人卡片 -->
    <view class="child-avatar-card">
      <view class="avatar-area">
        <view class="avatar-circle">
          <image class="avatar-img" src="/static/ch/ch_home_avatar.png" mode="aspectFit"></image>
        </view>
        <view class="avatar-badge">
          <text class="badge-star">⭐</text>
        </view>
      </view>
      <text class="child-nickname">{{ userStore.nickname || '小勇士' }}</text>
      <text class="child-title">健康小达人</text>
      <view class="stats-row">
        <view class="stat-item-child">
          <text class="stat-num">{{ childStats.days }}</text>
          <text class="stat-label-child">坚持天数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item-child">
          <text class="stat-num">{{ childStats.stars }}</text>
          <text class="stat-label-child">获得星星</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item-child">
          <text class="stat-num">{{ childStats.badges }}</text>
          <text class="stat-label-child">勋章数</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="child-menu-card">
      <view class="menu-title-child">
        <image class="menu-icon-img target-icon" src="/static/ch/ch_home_target.png" mode="aspectFit"></image>
        <text class="menu-text">我的功能</text>
      </view>
      <view class="menu-grid-child">
        <view class="menu-item-child" @tap="goToHealthPlan">
          <view class="item-icon-wrap plan">
            <image class="item-icon-img" src="/static/ch/ch_home_plan.png" mode="aspectFit"></image>
          </view>
          <text class="item-name">建任务</text>
        </view>
        <view class="menu-item-child" @tap="goToDashboard">
          <view class="item-icon-wrap chart">
            <image class="item-icon-img" src="/static/ch/ch_home_reg.png" mode="aspectFit"></image>
          </view>
          <text class="item-name">看数据</text>
        </view>
        <view class="menu-item-child" @tap="goToDailyCheckin">
          <view class="item-icon-wrap checkin">
            <image class="item-icon-img" src="/static/ch/ch_index_finish.png" mode="aspectFit"></image>
          </view>
          <text class="item-name">打卡</text>
        </view>
        <view class="menu-item-child" @tap="goToRoleSwitcher">
          <view class="item-icon-wrap switch">
            <image class="item-icon-img" src="/static/ch/ch_home_change.png" mode="aspectFit"></image>
          </view>
          <text class="item-name">切换</text>
        </view>
      </view>
    </view>

    <!-- 成就展示 -->
    <view class="achievement-card">
      <view class="achievement-header">
        <image class="achievement-icon-img" src="/static/ch/ch_home_win.png" mode="aspectFit"></image>
        <text class="achievement-title">我的成就</text>
      </view>
      <view class="achievement-list">
        <view class="achievement-item">
          <text class="achievement-icon">🌟</text>
          <text class="achievement-name">健康新星</text>
        </view>
        <view class="achievement-item">
          <text class="achievement-icon">💪</text>
          <text class="achievement-name">坚持达人</text>
        </view>
        <view class="achievement-item locked">
          <text class="achievement-icon">🎖️</text>
          <text class="achievement-name">待解锁</text>
        </view>
      </view>
    </view>

    <!-- 底部装饰 -->
    <view class="child-footer-deco">
      <image class="footer-cat-cloud" src="/static/ch/ch_index_cat&cloud.png" mode="aspectFit"></image>
    </view>
  </view>

  <!-- 成人/青少年模式 -->
  <view v-else class="profile-container">
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
  
  <!-- 自定义 TabBar -->
  <CustomTabBar :current="2" />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'
import CustomTabBar from '@/components/CustomTabBar.vue'

const userStore = useUserStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)

// 儿童模式统计数据
const childStats = ref({
  days: 7,
  stars: 23,
  badges: 2
})

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

const goToGlucoseReport = () => {
  uni.navigateTo({
    url: '/pages/profile/glucose-report'
  })
}

const goToBasicInfo = () => {
  uni.navigateTo({
    url: '/pages/profile/basic-info'
  })
}

const goToDailyCheckin = () => {
  uni.navigateTo({
    url: '/pages/profile/daily-checkin'
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

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-profile {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 24rpx;
  padding-bottom: 120rpx;
  position: relative;
}

.child-profile-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  background: linear-gradient(180deg, #F2E5D3 0%, #FEF7ED 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.header-clouds {
  position: absolute;
  top: 40rpx;
  left: 0;
  right: 0;
}

.cloud {
  position: absolute;
  font-size: 50rpx;
  opacity: 0.5;
  animation: floatCloud 4s ease-in-out infinite;
  left: 15%;
}

.cloud.c2 {
  right: 20%;
  left: auto;
  animation-delay: 2s;
}

@keyframes floatCloud {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15rpx); }
}

/* 个人卡片 */
.child-avatar-card {
  position: relative;
  background: #FFFEF7;
  border-radius: 40rpx;
  padding: 80rpx 32rpx 32rpx;
  margin-top: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(96, 47, 39, 0.12);
  border: 4rpx solid #E3C7A4;
  text-align: center;
  z-index: 10;
}

.avatar-area {
  position: absolute;
  top: -60rpx;
  left: 50%;
  transform: translateX(-50%);
}

.avatar-circle {
  width: 140rpx;
  height: 140rpx;
  background: linear-gradient(135deg, #D5A874 0%, #CB8E54 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 6rpx solid white;
  box-shadow: 0 6rpx 20rpx rgba(203, 142, 84, 0.4);
}

.avatar-emoji {
  font-size: 80rpx;
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
}

.avatar-badge {
  position: absolute;
  bottom: -8rpx;
  right: -8rpx;
  width: 48rpx;
  height: 48rpx;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.badge-star {
  font-size: 32rpx;
}

.child-nickname {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #602F27;
  margin-bottom: 8rpx;
}

.child-title {
  display: block;
  font-size: 26rpx;
  color: #A85835;
  margin-bottom: 24rpx;
}

.stats-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border-radius: 20rpx;
}

.stat-item-child {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20rpx;
}

.stat-num {
  font-size: 40rpx;
  font-weight: bold;
  color: #C07240;
}

.stat-label-child {
  font-size: 22rpx;
  color: #74362C;
}

.stat-divider {
  width: 2rpx;
  height: 50rpx;
  background: #E3C7A4;
}

/* 功能菜单 */
.child-menu-card {
  background: #FFFEF7;
  border-radius: 32rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.menu-title-child {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.menu-icon {
  font-size: 32rpx;
}

.menu-text {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.menu-grid-child {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.menu-item-child {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx;
}

.item-icon-wrap {
  width: 100rpx;
  height: 100rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.1);
}

.item-icon-wrap.plan,
.item-icon-wrap.chart,
.item-icon-wrap.checkin,
.item-icon-wrap.switch {
  background: #F6D387;
  box-shadow: 
    0 6rpx 16rpx rgba(246, 211, 135, 0.4),
    0 2rpx 4rpx rgba(0, 0, 0, 0.1);
}

.item-icon {
  font-size: 44rpx;
}

.item-icon-img {
  width: 75rpx;
  height: 75rpx;
}

.item-icon-wrap.plan .item-icon-img {
  margin-left: 6rpx;
}

.menu-icon-img {
  width: 48rpx;
  height: 48rpx;
}

.target-icon {
  width: 48rpx;
  height: 48rpx;
  overflow: hidden;
  object-position: top;
}

.achievement-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.achievement-icon-img {
  width: 48rpx;
  height: 48rpx;
}

.item-name {
  font-size: 24rpx;
  color: #602F27;
}

/* 成就卡片 */
.achievement-card {
  background: #FFFEF7;
  border-radius: 32rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #E3C7A4;
}


.achievement-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.achievement-list {
  display: flex;
  gap: 16rpx;
}

.achievement-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx;
  background: white;
  border-radius: 20rpx;
  border: 2rpx solid #D5A874;
}

.achievement-item.locked {
  opacity: 0.5;
  border-color: #E5E7EB;
}

.achievement-icon {
  font-size: 48rpx;
}

.achievement-name {
  font-size: 24rpx;
  color: #8E422F;
}

.achievement-item.locked .achievement-name {
  color: #9CA3AF;
}

/* 底部装饰 */
.child-footer-deco {
  display: flex;
  justify-content: flex-end;
  margin-top: 24rpx;
  overflow: hidden;
  position: relative;
  height: 108rpx;
}

.footer-cat-cloud {
  width: 180rpx;
  height: 180rpx;
  margin-top: -72rpx;
  animation: moveLeftRight 10s ease-in-out infinite;
}

@keyframes moveLeftRight {
  0% {
    transform: translateX(0) scaleX(1);
  }
  48% {
    transform: translateX(-600rpx) scaleX(1);
  }
  50% {
    transform: translateX(-600rpx) scaleX(-1);
  }
  98% {
    transform: translateX(0) scaleX(-1);
  }
  100% {
    transform: translateX(0) scaleX(1);
  }
}

/* ========== 儿童模式样式覆盖（成人布局） ========== */
.page-container.child-mode {
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
}

.child-mode .profile-header {
  background: #FFFEF7 !important;
  border: 4rpx solid #E3C7A4 !important;
  box-shadow: 0 6rpx 0 #D5A874 !important;
}

.child-mode .avatar {
  border-color: #E3C7A4 !important;
}

.child-mode .nickname {
  color: #602F27 !important;
}

.child-mode .username {
  color: #A85835 !important;
}

.child-mode .info-section,
.child-mode .function-section {
  background: #FFFEF7 !important;
  border: 3rpx solid #E3C7A4 !important;
  box-shadow: 0 4rpx 0 #D5A874 !important;
}

.child-mode .section-title .title-text {
  color: #602F27 !important;
}

.child-mode .info-item {
  border-bottom-color: #F2E5D3 !important;
}

.child-mode .info-label {
  color: #A85835 !important;
}

.child-mode .info-input {
  color: #602F27 !important;
}

.child-mode .info-value {
  color: #CB8E54 !important;
}

.child-mode .save-btn {
  background: #F6CD75 !important;
  color: #602F27 !important;
  border: 4rpx solid #E5BC64 !important;
  box-shadow: 0 6rpx 0 #D4AB53 !important;
}

.child-mode .function-item {
  border-bottom-color: #F2E5D3 !important;
}

.child-mode .function-text {
  color: #602F27 !important;
}

.child-mode .function-arrow {
  color: #CB8E54 !important;
}

.child-mode .logout-btn {
  background: #FFFEF7 !important;
  color: #A85835 !important;
  border: 3rpx solid #E3C7A4 !important;
  box-shadow: 0 4rpx 0 #D5C4B0 !important;
}
</style>
