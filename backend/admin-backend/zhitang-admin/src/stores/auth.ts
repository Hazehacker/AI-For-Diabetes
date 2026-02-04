import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, type LoginRequest, type LoginResponse } from '@/api/auth'
import { ElMessage } from 'element-plus'

export interface User {
  user_id: number
  username: string
  nickname: string
  phone_number?: string
  email?: string
  avatar_url?: string
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 登录
  const loginAction = async (loginData: LoginRequest): Promise<boolean> => {
    try {
      const response: LoginResponse = await login(loginData)
      
      // 保存token和用户信息
      token.value = response.token
      user.value = response.user
      
      // 持久化存储
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    ElMessage.success('已退出登录')
  }

  // 初始化用户信息
  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        logout()
      }
    }
  }

  // 更新用户信息
  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  // 检查token是否有效
  const checkToken = (): boolean => {
    if (!token.value) return false
    
    try {
      // 简单的JWT token检查（实际项目中可能需要更复杂的验证）
      const payload = JSON.parse(atob(token.value.split('.')[1]))
      const now = Math.floor(Date.now() / 1000)
      
      if (payload.exp && payload.exp < now) {
        logout()
        return false
      }
      
      return true
    } catch (error) {
      console.error('Token验证失败:', error)
      logout()
      return false
    }
  }

  return {
    // 状态
    token,
    user,
    isLoggedIn,
    
    // 方法
    loginAction,
    logout,
    initUser,
    updateUser,
    checkToken,
  }
}, {
  persist: {
    key: 'auth-store',
    storage: localStorage,
    paths: ['token', 'user'],
  }
})
