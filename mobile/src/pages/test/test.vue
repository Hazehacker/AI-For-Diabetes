<template>
  <view class="test-container">
    <view class="test-header">
      <text class="title">调试测试页面</text>
    </view>

    <view class="test-section">
      <text class="section-title">1. 测试API连接</text>
      <button class="test-btn" @tap="testApi">测试登录API</button>
      <view class="result">{{ apiResult }}</view>
    </view>

    <view class="test-section">
      <text class="section-title">2. 测试Storage</text>
      <button class="test-btn" @tap="testStorage">测试存储</button>
      <view class="result">{{ storageResult }}</view>
    </view>

    <view class="test-section">
      <text class="section-title">3. 测试页面跳转</text>
      <button class="test-btn" @tap="testNavigate">跳转到对话页</button>
      <view class="result">{{ navigateResult }}</view>
    </view>

    <view class="test-section">
      <text class="section-title">4. 完整登录测试</text>
      <input 
        class="test-input" 
        v-model="testUsername" 
        placeholder="用户名"
      />
      <input 
        class="test-input" 
        v-model="testPassword" 
        type="password"
        placeholder="密码"
      />
      <button class="test-btn" @tap="testFullLogin">完整登录流程</button>
      <view class="result">{{ loginResult }}</view>
    </view>

    <view class="test-section">
      <text class="section-title">5. 环境信息</text>
      <view class="info-item">平台: {{ platform }}</view>
      <view class="info-item">Token: {{ token }}</view>
      <view class="info-item">UserId: {{ userId }}</view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { userApi } from '@/api'

const userStore = useUserStore()

const apiResult = ref('')
const storageResult = ref('')
const navigateResult = ref('')
const loginResult = ref('')
const testUsername = ref('13270860672')
const testPassword = ref('admin123')

const platform = ref(uni.getSystemInfoSync().platform)
const token = computed(() => userStore.token || '未设置')
const userId = computed(() => userStore.userId || '未设置')

// 测试API
const testApi = async () => {
  apiResult.value = '测试中...'
  try {
    const res = await userApi.login({
      username: testUsername.value,
      password: testPassword.value
    })
    apiResult.value = 'API测试成功:\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    apiResult.value = 'API测试失败:\n' + error.message
  }
}

// 测试Storage
const testStorage = () => {
  try {
    // 写入测试
    uni.setStorageSync('test_key', 'test_value')
    
    // 读取测试
    const value = uni.getStorageSync('test_key')
    
    // 清除测试
    uni.removeStorageSync('test_key')
    
    storageResult.value = `Storage测试成功\n写入: test_value\n读取: ${value}`
  } catch (error) {
    storageResult.value = 'Storage测试失败:\n' + error.message
  }
}

// 测试页面跳转
const testNavigate = () => {
  navigateResult.value = '准备跳转...'
  
  uni.navigateTo({
    url: '/pages/chat/chat',
    success: () => {
      navigateResult.value = '跳转成功'
    },
    fail: (err) => {
      navigateResult.value = '跳转失败:\n' + JSON.stringify(err)
      
      // 尝试使用reLaunch
      uni.reLaunch({
        url: '/pages/chat/chat',
        success: () => {
          navigateResult.value = 'reLaunch跳转成功'
        },
        fail: (err2) => {
          navigateResult.value = 'reLaunch也失败:\n' + JSON.stringify(err2)
        }
      })
    }
  })
}

// 完整登录测试
const testFullLogin = async () => {
  loginResult.value = '开始登录测试...'
  
  try {
    console.log('=== 开始完整登录测试 ===')
    console.log('用户名:', testUsername.value)
    
    // 步骤1: 调用登录API
    loginResult.value += '\n步骤1: 调用登录API...'
    const result = await userStore.login(testUsername.value, testPassword.value)
    console.log('登录结果:', result)
    
    if (result.success) {
      loginResult.value += '\n步骤2: 登录成功'
      loginResult.value += '\nToken: ' + userStore.token.substring(0, 20) + '...'
      loginResult.value += '\nUserId: ' + userStore.userId
      
      // 步骤3: 验证存储
      loginResult.value += '\n步骤3: 验证存储...'
      const storedToken = uni.getStorageSync('token')
      const storedUserId = uni.getStorageSync('userId')
      loginResult.value += '\n存储的Token: ' + (storedToken ? '已保存' : '未保存')
      loginResult.value += '\n存储的UserId: ' + (storedUserId || '未保存')
      
      // 步骤4: 跳转页面
      loginResult.value += '\n步骤4: 准备跳转...'
      
      setTimeout(() => {
        uni.redirectTo({
          url: '/pages/chat/chat',
          success: () => {
            console.log('跳转成功')
            loginResult.value += '\n步骤5: 跳转成功！'
          },
          fail: (err) => {
            console.error('跳转失败:', err)
            loginResult.value += '\n步骤5: 跳转失败 - ' + JSON.stringify(err)
          }
        })
      }, 1000)
    } else {
      loginResult.value += '\n登录失败: ' + result.message
    }
  } catch (error) {
    console.error('登录测试异常:', error)
    loginResult.value += '\n异常: ' + error.message
  }
}
</script>

<style scoped>
.test-container {
  padding: 40rpx;
  background: #f5f5f5;
  min-height: 100vh;
}

.test-header {
  text-align: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.test-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
}

.test-btn {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  color: white;
  border-radius: 16rpx;
  font-size: 28rpx;
  margin-bottom: 24rpx;
}

.test-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  font-size: 28rpx;
  margin-bottom: 24rpx;
}

.result {
  padding: 24rpx;
  background: #f9fafb;
  border-radius: 12rpx;
  font-size: 24rpx;
  color: #666;
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 100rpx;
}

.info-item {
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #666;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}
</style>
