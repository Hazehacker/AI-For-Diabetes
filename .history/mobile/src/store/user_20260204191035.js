/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { userApi } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('api_token') || '',
    userId: uni.getStorageSync('userId') || '',
    userInfo: uni.getStorageSync('userInfo') || null,
    nickname: '',
    
    // 基础信息
    basicInfo: {
      age: null,
      gender: '',
      height: null,
      weight: null,
      bmi: null,
      waistline: null,
      diagnosisDate: null,
      diseaseYears: 0,
      complications: [],
      familyHistory: false,
      monitoringLevel: ''
    },
    
    // 签到积分系统
    checkin: {
      totalDays: 0,
      continuousDays: 0,
      lastCheckinDate: null,
      totalPoints: 0,
      monthlyCheckins: []
    }
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    nickname: (state) => state.userInfo?.nickname || state.userInfo?.username || '用户'
  },
  
  actions: {
    // 登录
    async login(username, password) {
      try {
        console.log('📱 Store: 调用登录API...', { username })
        const res = await userApi.login({ username, password })
        
        console.log('📱 Store: 登录响应:', res)
        
        // 检查响应数据结构
        if (res && res.data && res.data.token) {
          this.token = res.data.token
          this.userId = String(res.data.user_id)
          this.userInfo = {
            user_id: res.data.user_id,
            username: res.data.username,
            nickname: res.data.nickname || res.data.username,
            phone: res.data.phone || username
          }
          
          // 持久化存储（统一使用api_token）
          uni.setStorageSync('api_token', this.token)
          uni.setStorageSync('userId', this.userId)
          uni.setStorageSync('userInfo', this.userInfo)
          uni.setStorageSync('username', res.data.username)
          uni.setStorageSync('nickname', res.data.nickname || res.data.username)
          
          console.log('✅ Store: 登录成功，已保存数据')
          console.log('   Token:', this.token.substring(0, 20) + '...')
          console.log('   UserId:', this.userId)
          console.log('   Username:', res.data.username)
          
          return { success: true }
        } else {
          console.error('❌ Store: 响应数据格式错误:', res)
          return { success: false, message: res.message || '登录失败：数据格式错误' }
        }
      } catch (error) {
        console.error('❌ Store: 登录失败:', error)
        return { success: false, message: error.message || '登录失败' }
      }
    },
    
    // 退出登录
    logout() {
      console.log('📱 Store: 退出登录')
      
      this.token = ''
      this.userId = ''
      this.userInfo = null
      
      // 清除所有存储
      uni.removeStorageSync('api_token')
      uni.removeStorageSync('userId')
      uni.removeStorageSync('userInfo')
      uni.removeStorageSync('username')
      uni.removeStorageSync('nickname')
      uni.removeStorageSync('conversationId')
      uni.removeStorageSync('selectedRobot')
      
      uni.reLaunch({
        url: '/pages/login/login'
      })
    },
    
    // 获取用户信息
    async fetchUserInfo() {
      if (!this.userId) {
        console.warn('⚠️ Store: 无userId，跳过获取用户信息')
        return
      }
      
      try {
        console.log('📱 Store: 获取用户信息...', this.userId)
        const res = await userApi.getUserProfile(this.userId)
        
        if (res.data) {
          this.userInfo = {
            ...this.userInfo,
            ...res.data
          }
          uni.setStorageSync('userInfo', this.userInfo)
          console.log('✅ Store: 用户信息已更新')
        }
      } catch (error) {
        console.error('❌ Store: 获取用户信息失败:', error)
      }
    }
  }
})
