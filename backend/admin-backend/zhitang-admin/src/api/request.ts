import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { API_CONFIG, HTTP_STATUS, ERROR_MESSAGES } from './config'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
})

// 请求拦截器
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证token
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳
    if (config.params) {
      config.params._t = Date.now()
    } else {
      config.params = { _t: Date.now() }
    }
    
    console.log('🚀 API请求:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
    })
    
    return config
  },
  (error) => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data, status } = response
    
    console.log('✅ API响应:', {
      status,
      url: response.config.url,
      data,
    })
    
    // 处理成功响应
    if (status === HTTP_STATUS.SUCCESS || status === HTTP_STATUS.CREATED) {
      return data
    }
    
    return response
  },
  (error) => {
    console.error('❌ API响应错误:', error)
    
    const { response } = error
    let message = ERROR_MESSAGES.UNKNOWN_ERROR
    
    if (!response) {
      // 网络错误
      if (error.code === 'ECONNABORTED') {
        message = ERROR_MESSAGES.TIMEOUT_ERROR
      } else {
        message = ERROR_MESSAGES.NETWORK_ERROR
      }
    } else {
      // HTTP状态码错误
      const { status, data } = response
      
      switch (status) {
        case HTTP_STATUS.UNAUTHORIZED:
          message = ERROR_MESSAGES.UNAUTHORIZED
          // 清除本地token并跳转到登录页
          const authStore = useAuthStore()
          authStore.logout()
          break
        case HTTP_STATUS.FORBIDDEN:
          message = ERROR_MESSAGES.FORBIDDEN
          break
        case HTTP_STATUS.NOT_FOUND:
          message = ERROR_MESSAGES.NOT_FOUND
          break
        case HTTP_STATUS.INTERNAL_SERVER_ERROR:
          message = ERROR_MESSAGES.SERVER_ERROR
          break
        default:
          message = data?.message || ERROR_MESSAGES.UNKNOWN_ERROR
      }
    }
    
    // 显示错误消息
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export default request
