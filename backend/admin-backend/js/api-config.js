// API配置和工具函数
const API_CONFIG = {
    BASE_URL: 'http://127.0.0.1:8900',
    ENDPOINTS: {
        // 认证
        LOGIN: '/api/login',
        
        // 用户管理
        USERS: '/api/users',
        USER_DETAIL: (id) => `/api/users/${id}`,
        USER_STATUS: (id) => `/api/users/${id}/status`,
        
        // FAQ管理
        FAQ_LIST: '/api/faq/list',
        FAQ_DETAIL: (id) => `/api/faq/${id}`,
        FAQ_CREATE: '/api/faq',
        FAQ_UPDATE: (id) => `/api/faq/${id}`,
        FAQ_DELETE: (id) => `/api/faq/${id}`,
        FAQ_BATCH: '/api/faq/batch',
        FAQ_KEYWORDS_SUGGEST: '/api/faq/keywords/suggest',
        FAQ_STATS: '/api/faq/stats',
        
        // 标签管理
        TAG_LIST: '/api/tag',
        TAG_SET: '/api/tag',
        TAG_DELETE: (key) => `/api/tag/${key}`,
        TAG_BATCH: '/api/tag/batch',
        TAG_CLEAR: '/api/tag/clear',
        TAG_DEFINITIONS: '/api/tag/definitions',
        TAG_HISTORY: '/api/tag/history',
        
        // 提示词管理
        PROMPT_TEMPLATES: '/api/prompt/templates',
        PROMPT_TEMPLATE_DETAIL: (id) => `/api/prompt/templates/${id}`,
        PROMPT_USER_SETTINGS: '/api/prompt/user-settings',
        PROMPT_USER_SETTING: (type) => `/api/prompt/user-settings/${type}`,
        
        // 消息记录
        CHAT_HISTORY: '/api/chat/history',
        CHAT_SESSIONS: '/api/chat/sessions',
        
        // 系统
        DB_POOL_STATUS: '/api/db-pool/status'
    }
};

// 获取Token
function getToken() {
    return localStorage.getItem('admin_token');
}

// 设置Token
function setToken(token) {
    localStorage.setItem('admin_token', token);
}

// 清除Token
function clearToken() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
}

// 获取完整API URL
function getApiUrl(endpoint) {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
}

// 通用API请求函数
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };
    
    try {
        const response = await fetch(getApiUrl(endpoint), finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            // 如果是401，清除token并跳转到登录页
            if (response.status === 401) {
                clearToken();
                window.location.href = '/admin/login.html';
                throw new Error('登录已过期，请重新登录');
            }
            throw new Error(data.message || `请求失败: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// GET请求
async function apiGet(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return apiRequest(url, { method: 'GET' });
}

// POST请求
async function apiPost(endpoint, data = {}) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT请求
async function apiPut(endpoint, data = {}) {
    return apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE请求
async function apiDelete(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return apiRequest(url, { method: 'DELETE' });
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transition = 'opacity 0.3s';
        setTimeout(() => {
            document.body.removeChild(messageDiv);
        }, 300);
    }, 3000);
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 分页工具
function createPagination(currentPage, totalPages, onPageChange) {
    const pagination = document.createElement('div');
    pagination.className = 'flex items-center justify-center space-x-2 mt-4';
    
    // 上一页
    const prevBtn = document.createElement('button');
    prevBtn.className = `px-4 py-2 rounded-lg ${
        currentPage <= 1 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-blue-500 text-white hover:bg-blue-600'
    }`;
    prevBtn.textContent = '上一页';
    prevBtn.disabled = currentPage <= 1;
    prevBtn.onclick = () => currentPage > 1 && onPageChange(currentPage - 1);
    pagination.appendChild(prevBtn);
    
    // 页码
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `px-4 py-2 rounded-lg ${
                i === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => onPageChange(i);
            pagination.appendChild(pageBtn);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'px-2 text-gray-500';
            ellipsis.textContent = '...';
            pagination.appendChild(ellipsis);
        }
    }
    
    // 下一页
    const nextBtn = document.createElement('button');
    nextBtn.className = `px-4 py-2 rounded-lg ${
        currentPage >= totalPages ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-blue-500 text-white hover:bg-blue-600'
    }`;
    nextBtn.textContent = '下一页';
    nextBtn.disabled = currentPage >= totalPages;
    nextBtn.onclick = () => currentPage < totalPages && onPageChange(currentPage + 1);
    pagination.appendChild(nextBtn);
    
    return pagination;
}

