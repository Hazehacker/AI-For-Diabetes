<template>
  <view class="login-container">
    <!-- Logo区域 -->
    <view class="logo-section">
      <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
      <text class="app-name">智糖小助手</text>
      <text class="app-slogan">您的智能糖尿病管理伙伴</text>
    </view>

    <!-- 登录表单 -->
    <view class="form-section">
      <view class="input-group">
        <text class="input-label">手机号</text>
        <view class="input-wrapper">
          <input 
            class="input-field" 
            type="text" 
            v-model="formData.username"
            placeholder="请输入手机号"
            maxlength="11"
          />
          <text class="input-icon">📱</text>
        </view>
      </view>

      <view class="input-group">
        <text class="input-label">密码</text>
        <view class="input-wrapper">
          <input 
            class="input-field" 
            :type="showPassword ? 'text' : 'password'"
            v-model="formData.password"
            placeholder="请输入密码"
          />
          <text class="input-icon" @tap="togglePassword">
            {{ showPassword ? '👁️' : '🔒' }}
          </text>
        </view>
      </view>

      <button 
        class="login-btn" 
        :disabled="loading"
        @tap="handleLogin"
      >
        <text v-if="!loading">登录</text>
        <text v-else>登录中...</text>
      </button>

      <view class="debug-link" @tap="goToTest">
        <text class="debug-text">遇到问题？点击这里进行调试测试</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const formData = ref({
  username: '',
  password: ''
})

const showPassword = ref(false)
const loading = ref(false)

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  if (!formData.value.username) {
    uni.showToast({
      title: '请输入手机号',
      icon: 'none'
    })
    return
  }

  if (!formData.value.password) {
    uni.showToast({
      title: '请输入密码',
      icon: 'none'
    })
    return
  }

  loading.value = true

  try {
    console.log('开始登录...', formData.value.username)
    
    const result = await userStore.login(
      formData.value.username,
      formData.value.password
    )

    console.log('登录结果:', result)

    if (result.success) {
      uni.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      })

      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        console.log('准备跳转到对话页面...')
        uni.redirectTo({
          url: '/pages/chat/chat-complete',
          success: () => {
            console.log('跳转成功')
          },
          fail: (err) => {
            console.error('跳转失败:', err)
            // 如果redirectTo失败，尝试使用reLaunch
            uni.reLaunch({
              url: '/pages/chat/chat-complete'
            })
          }
        })
      }, 1500)
    } else {
      uni.showToast({
        title: result.message || '登录失败',
        icon: 'none',
        duration: 2000
      })
    }
  } catch (error) {
    console.error('登录异常:', error)
    uni.showToast({
      title: error.message || '登录失败，请重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    loading.value = false
  }
}

const goToTest = () => {
  uni.navigateTo({
    url: '/pages/test/test'
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  padding: 60rpx 40rpx;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 100rpx;
}

.logo {
  width: 180rpx;
  height: 180rpx;
  margin-bottom: 40rpx;
  border-radius: 40rpx;
  background: white;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.2);
}

.app-name {
  font-size: 48rpx;
  font-weight: bold;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16rpx;
}

.app-slogan {
  font-size: 28rpx;
  color: #6b7280;
}

.form-section {
  background: white;
  border-radius: 32rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.15);
}

.input-group {
  margin-bottom: 40rpx;
}

.input-label {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-field {
  flex: 1;
  height: 96rpx;
  padding: 0 100rpx 0 32rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 24rpx;
  font-size: 30rpx;
}

.input-field:focus {
  border-color: #969FFF;
  background: white;
}

.input-icon {
  position: absolute;
  right: 32rpx;
  font-size: 40rpx;
}

.login-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 40rpx;
  box-shadow: 0 8rpx 30rpx rgba(150, 159, 255, 0.3);
}

.login-btn:disabled {
  opacity: 0.6;
}

.debug-link {
  margin-top: 40rpx;
  text-align: center;
}

.debug-text {
  font-size: 24rpx;
  color: #969FFF;
  text-decoration: underline;
}
</style>
