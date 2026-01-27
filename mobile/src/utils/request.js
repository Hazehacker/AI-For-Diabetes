/**
 * HTTP请求封装
 */

const BASE_URL = 'https://chat.cmkjai.com/api'

/**
 * 封装的请求方法
 */
export const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取token（统一使用api_token）
    const token = uni.getStorageSync('api_token')
    
    // 构建完整URL
    let url = options.url
    if (!url.startsWith('http')) {
      url = BASE_URL + url
    }
    
    // 构建请求配置
    const config = {
      url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      timeout: 30000
    }
    
    // 添加token到请求头
    if (token) {
      config.header['Authorization'] = `Bearer ${token}`
    }
    
    // 处理GET请求参数
    if (config.method === 'GET' && config.data && Object.keys(config.data).length > 0) {
      const params = Object.keys(config.data)
        .map(key => `${key}=${encodeURIComponent(config.data[key])}`)
        .join('&')
      config.url += (config.url.includes('?') ? '&' : '?') + params
      config.data = undefined
    }
    
    console.log('🚀 发起请求:', {
      url: config.url,
      method: config.method,
      data: config.data,
      hasToken: !!token
    })
    
    // 发送请求
    uni.request({
      ...config,
      success: (res) => {
        const { statusCode, data } = res
        
        console.log('✅ 请求响应:', {
          url: config.url,
          status: statusCode,
          data
        })
        
        if (statusCode === 200) {
          // 请求成功
          resolve(data)
        } else if (statusCode === 401) {
          // Token过期，跳转登录
          console.warn('⚠️ Token过期，清除登录信息')
          uni.removeStorageSync('api_token')
          uni.removeStorageSync('userInfo')
          uni.removeStorageSync('userId')
          uni.showToast({
            title: '登录已过期',
            icon: 'none'
          })
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/login/login'
            })
          }, 1500)
          reject(new Error('未授权，请重新登录'))
        } else {
          // 其他错误
          console.error('❌ 请求错误:', statusCode, data)
          reject(new Error(data.message || `请求失败 (${statusCode})`))
        }
      },
      fail: (err) => {
        console.error('❌ 请求失败:', err)
        let errorMessage = '网络请求失败'
        if (err.errMsg) {
          if (err.errMsg.includes('timeout')) {
            errorMessage = '请求超时，请检查网络'
          } else if (err.errMsg.includes('fail')) {
            errorMessage = '网络连接失败，请检查网络设置'
          }
        }
        reject(new Error(errorMessage))
      }
    })
  })
}

export default request
