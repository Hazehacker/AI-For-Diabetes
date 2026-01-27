/**
 * 通用工具函数
 */

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式 (default: 'YYYY-MM-DD HH:mm:ss')
 * @returns {string}
 */
export const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  const d = new Date(date)
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

/**
 * 防抖函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间(ms)
 * @returns {Function}
 */
export const debounce = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间(ms)
 * @returns {Function}
 */
export const throttle = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    if (timer) return
    timer = setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }
}

/**
 * 深拷贝
 * @param {any} obj - 要拷贝的对象
 * @returns {any}
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  
  const cloneObj = {}
  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloneObj[key] = deepClone(obj[key])
    }
  }
  return cloneObj
}

/**
 * 生成唯一ID
 * @returns {string}
 */
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 验证手机号
 * @param {string} phone - 手机号
 * @returns {boolean}
 */
export const validatePhone = (phone) => {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱
 * @returns {boolean}
 */
export const validateEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 * @returns {string}
 */
export const getFileExtension = (filename) => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2)
}

/**
 * 字节转换
 * @param {number} bytes - 字节数
 * @returns {string}
 */
export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

/**
 * 获取相对时间
 * @param {string|Date} date - 日期
 * @returns {string}
 */
export const getRelativeTime = (date) => {
  const now = new Date()
  const target = new Date(date)
  const diff = now - target
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day
  
  if (diff < minute) return '刚刚'
  if (diff < hour) return Math.floor(diff / minute) + '分钟前'
  if (diff < day) return Math.floor(diff / hour) + '小时前'
  if (diff < week) return Math.floor(diff / day) + '天前'
  if (diff < month) return Math.floor(diff / week) + '周前'
  return formatDate(date, 'YYYY-MM-DD')
}

/**
 * 打卡状态展示配置（与H5保持一致）
 * - 好: 😊 绿色
 * - 良好: 🙂 黄色
 * - 一般: 😐 灰色
 */
export const CHECKIN_STATUS_META = {
  '好': { emoji: '😊', level: 3 },
  '良好': { emoji: '🙂', level: 2 },
  '一般': { emoji: '😐', level: 1 }
}

/**
 * 归一化打卡日期Key：YYYY-MM-DD（用于“按天”统计/渲染）
 * @param {string|Date} date
 */
export const toDateKey = (date) => {
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/**
 * 同一天多条记录时，取“最好”的控糖状态（好 > 良好 > 一般）
 * @param {string} aStatus
 * @param {string} bStatus
 */
export const pickBetterCheckinStatus = (aStatus, bStatus) => {
  const a = CHECKIN_STATUS_META[aStatus] || CHECKIN_STATUS_META['好']
  const b = CHECKIN_STATUS_META[bStatus] || CHECKIN_STATUS_META['好']
  return a.level >= b.level ? (aStatus || '好') : (bStatus || '好')
}