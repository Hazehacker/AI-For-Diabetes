// 环境配置
export const ENV_CONFIG = {
  // API基础URL
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://115.120.251.86:8900',
  
  // 应用信息
  APP_TITLE: import.meta.env.VITE_APP_TITLE || '智糖小助手管理后台',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  APP_DESCRIPTION: import.meta.env.VITE_APP_DESCRIPTION || '智糖小助手管理后台系统',
  
  // 开发模式
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
}
