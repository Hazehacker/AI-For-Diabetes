// 通用布局组件
function createHeader(currentPage = '') {
    const user = JSON.parse(localStorage.getItem('admin_user') || '{}');
    
    return `
        <header class="bg-white shadow-lg px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 gradient-primary rounded-full flex items-center justify-center">
                    <i class="fas fa-cog text-white"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold gradient-text">智糖小助手管理后台</h1>
                    <p class="text-sm text-gray-600">${currentPage || '独立管理服务'}</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-600">
                    <span class="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                    服务运行中
                </div>
                <div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-user text-gray-600"></i>
                    </div>
                    <span class="text-sm font-medium text-gray-700">${user.username || '管理员'}</span>
                </div>
                <button id="logout-btn" class="px-3 py-1 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors">
                    <i class="fas fa-sign-out-alt mr-1"></i>退出
                </button>
            </div>
        </header>
    `;
}

function createSidebar(activeItem = '') {
    const menuItems = [
        { id: 'dashboard', icon: 'fa-home', label: '仪表板', href: 'dashboard.html' },
        { id: 'users', icon: 'fa-users', label: '用户管理', href: 'user-management.html' },
        { id: 'tags', icon: 'fa-tags', label: '标签管理', href: 'tag-management.html' },
        { id: 'faq', icon: 'fa-question-circle', label: 'FAQ管理', href: 'faq-management.html' },
        { id: 'prompt', icon: 'fa-comments', label: '提示词管理', href: 'prompt-management.html' },
        { id: 'chat', icon: 'fa-comments', label: '消息记录', href: 'chat-history.html' },
        { id: 'knowledge', icon: 'fa-database', label: '知识文档', href: 'knowledge-management.html' }
    ];
    
    let sidebarHtml = '<nav class="sidebar-gradient w-64 min-h-screen p-4">';
    sidebarHtml += '<div class="mb-8">';
    sidebarHtml += '<div class="text-white text-xl font-bold mb-2">菜单</div>';
    sidebarHtml += '<div class="h-1 bg-white/20 rounded"></div>';
    sidebarHtml += '</div>';
    
    sidebarHtml += '<ul class="space-y-2">';
    menuItems.forEach(item => {
        const isActive = activeItem === item.id;
        sidebarHtml += `
            <li>
                <a href="${item.href}" 
                   class="sidebar-item flex items-center space-x-3 px-4 py-3 rounded-lg text-white ${isActive ? 'active' : ''}">
                    <i class="fas ${item.icon} w-5"></i>
                    <span>${item.label}</span>
                </a>
            </li>
        `;
    });
    sidebarHtml += '</ul>';
    sidebarHtml += '</nav>';
    
    return sidebarHtml;
}

function initCommonLayout(activeItem = '') {
    // 检查登录状态
    const token = getToken();
    if (!token && !window.location.pathname.includes('login.html')) {
        window.location.href = 'login.html';
        return;
    }
    
    // 创建布局
    const layout = `
        ${createHeader()}
        <div class="flex">
            ${createSidebar(activeItem)}
            <main class="flex-1 p-6">
                <div id="main-content"></div>
            </main>
        </div>
    `;
    
    document.body.innerHTML = layout;
    
    // 绑定退出按钮
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if (confirm('确定要退出登录吗？')) {
                clearToken();
                window.location.href = 'login.html';
            }
        });
    }
}

// 通用样式
const COMMON_STYLES = `
    <style>
        .gradient-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .gradient-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .gradient-success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .gradient-warning {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        .gradient-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .glass-effect {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .card-hover {
            transition: all 0.3s ease;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .sidebar-gradient {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        .sidebar-item {
            transition: all 0.3s ease;
        }
        .sidebar-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }
        .sidebar-item.active {
            background-color: rgba(255, 255, 255, 0.2);
            border-right: 3px solid #fff;
        }
        .modal-backdrop {
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
        }
        .modal-content {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }
        .table-container {
            overflow-x: auto;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        .table th {
            background-color: #f3f4f6;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
        }
        .table td {
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }
        .table tr:hover {
            background-color: #f9fafb;
        }
        .btn {
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            cursor: pointer;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn-success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        .input {
            padding: 10px 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            width: 100%;
            transition: all 0.3s;
        }
        .input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success {
            background-color: #10b981;
            color: white;
        }
        .badge-danger {
            background-color: #ef4444;
            color: white;
        }
        .badge-warning {
            background-color: #f59e0b;
            color: white;
        }
        .badge-info {
            background-color: #3b82f6;
            color: white;
        }
    </style>
`;

