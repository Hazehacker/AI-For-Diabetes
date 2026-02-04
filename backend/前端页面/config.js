/**
 * 智糖小助手 - 统一配置文件
 * 自动适配本地开发和生产环境
 */

(function(window) {
    'use strict';

    // 环境检测
    const hostname = window.location.hostname;
    const protocol = window.location.protocol; // 自动检测协议 (http: 或 https:)
    const port = window.location.port; // 获取端口号
    const isDevelopment = hostname === 'localhost' || hostname === '127.0.0.1';
    const isProduction = hostname === 'chat.cmkjai.com' || hostname === 'www.cmkjai.com' || hostname === 'cmkjai.com';
    
    // 检测是否为IP地址（生产环境的IP访问）
    const isIPAddress = /^\d+\.\d+\.\d+\.\d+$/.test(hostname);
    const isProductionIP = isIPAddress && (hostname === '115.120.251.86' || port === '8900');

    // 配置对象
    const AppConfig = {
        // 环境标识
        ENV: isDevelopment ? 'development' : 'production',
        IS_DEV: isDevelopment,
        IS_PROD: isProduction,

        // 基础路径配置
        BASE_PATH: isProduction ? '' : '', // 生产环境使用根路径
        
        // API配置
        API: {
            // 开发环境：使用 localhost
            // 生产环境：使用当前地址（自动适配 http/https 和端口）
            BASE_URL: (() => {
                if (isDevelopment) {
                    return 'http://localhost:8900';
                }
                
                // 生产环境：使用当前访问地址
                let url = `${protocol}//${hostname}`;
                
                // 处理端口号
                // HTTPS默认443，HTTP默认80，这些端口不需要显式添加
                // 其他端口需要添加
                if (port && port !== '80' && port !== '443' && port !== '') {
                    url += `:${port}`;
                }
                
                return url;
            })(),
            TIMEOUT: 30000,
            RETRY_TIMES: 3
        },

        // TTS配置
        TTS: {
            ENABLED_DEFAULT: false,
            MAX_TEXT_LENGTH: 200,
            VOICE_ID: '7426720361753903141',
            SPEED: 1.2,
            SAMPLE_RATE: 16000,
            FORMAT: 'wav'
        },

        // 路由配置
        ROUTES: {
            LOGIN: '/login',
            HOME: '/home',
            CHAT: '/chat',
            CHECKIN: '/checkin',
            PROFILE: '/user',
            SETTINGS: '/settings'
        },

        // 存储键名
        STORAGE_KEYS: {
            TOKEN: 'api_token',  // 统一使用api_token
            USER_ID: 'user_id',
            USERNAME: 'username',
            CONVERSATION_ID: 'conversation_id',
            TTS_ENABLED: 'ttsEnabled'
        }
    };

    /**
     * 获取完整路径
     * @param {string} path - 相对路径
     * @returns {string} 完整路径
     */
    AppConfig.getPath = function(path) {
        // 确保路径以 / 开头
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        return this.BASE_PATH + path;
    };

    /**
     * 获取API完整URL
     * @param {string} endpoint - API端点
     * @returns {string} 完整URL
     */
    AppConfig.getApiUrl = function(endpoint) {
        // 确保端点以 / 开头
        if (!endpoint.startsWith('/')) {
            endpoint = '/' + endpoint;
        }
        return this.API.BASE_URL + endpoint;
    };

    /**
     * 页面跳转
     * @param {string} path - 目标路径
     */
    AppConfig.navigate = function(path) {
        window.location.href = this.getPath(path);
    };

    /**
     * 获取存储的token
     * @returns {string|null}
     */
    AppConfig.getToken = function() {
        return localStorage.getItem(this.STORAGE_KEYS.TOKEN);
    };

    /**
     * 保存token
     * @param {string} token
     */
    AppConfig.setToken = function(token) {
        console.log('💾 AppConfig.setToken 被调用, token:', token, '类型:', typeof token);
        if (!token || token === 'undefined' || token === undefined) {
            console.error('❌ 拒绝保存无效token:', token);
            return;
        }
        localStorage.setItem(this.STORAGE_KEYS.TOKEN, token);
        console.log('✅ Token已保存到localStorage');
    };

    /**
     * 清除token
     */
    AppConfig.clearToken = function() {
        localStorage.removeItem(this.STORAGE_KEYS.TOKEN);
    };

    /**
     * 检查是否已登录
     * @returns {boolean}
     */
    AppConfig.isLoggedIn = function() {
        return !!this.getToken();
    };

    /**
     * 打印配置信息
     */
    AppConfig.printConfig = function() {
        console.log('%c[AppConfig] 当前配置:', 'color: #5147FF; font-weight: bold;');
        console.log('环境:', this.ENV);
        console.log('主机名:', hostname);
        console.log('协议:', protocol);
        console.log('端口:', port || '(默认)');
        console.log('基础路径:', this.BASE_PATH);
        console.log('API地址:', this.API.BASE_URL);
        console.log('登录状态:', this.isLoggedIn());
    };

    // 导出到全局
    window.AppConfig = AppConfig;

    // 打印配置信息（开发和生产环境都打印，方便调试）
    console.log('%c智糖小助手 配置已加载', 'color: #5147FF; font-weight: bold; font-size: 14px;');
    AppConfig.printConfig();

})(window);

