import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录' },
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/UserListView.vue'),
          meta: { title: '用户管理' },
        },
        {
          path: 'users/:id',
          name: 'user-detail',
          component: () => import('@/views/UserDetailView.vue'),
          meta: { title: '用户详情' },
        },
        {
          path: 'chat/history',
          name: 'chat-history',
          component: () => import('@/views/ChatHistoryView.vue'),
          meta: { title: '对话记录' },
        },
        {
          path: 'chat/sessions',
          name: 'chat-sessions',
          component: () => import('@/views/ChatSessionsView.vue'),
          meta: { title: '会话列表' },
        },
        {
          path: 'health/checkin',
          name: 'health-checkin',
          component: () => import('@/views/HealthCheckinView.vue'),
          meta: { title: '打卡记录' },
        },
        {
          path: 'health/profile',
          name: 'health-profile',
          component: () => import('@/views/HealthProfileView.vue'),
          meta: { title: '用户画像' },
        },
        {
          path: 'health/tags',
          name: 'health-tags',
          component: () => import('@/views/HealthTagsView.vue'),
          meta: { title: '用户标签' },
        },
        {
          path: 'knowledge/list',
          name: 'knowledge-list',
          component: () => import('@/views/KnowledgeListView.vue'),
          meta: { title: '知识库列表' },
        },
        {
          path: 'knowledge/upload',
          name: 'knowledge-upload',
          component: () => import('@/views/KnowledgeUploadView.vue'),
          meta: { title: '上传知识' },
        },
        {
          path: 'coze/audio',
          name: 'coze-audio',
          component: () => import('@/views/CozeAudioView.vue'),
          meta: { title: '音频记录' },
        },
        {
          path: 'coze/token',
          name: 'coze-token',
          component: () => import('@/views/CozeTokenView.vue'),
          meta: { title: 'Token管理' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { title: '页面不存在' },
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 智糖小助手管理后台`
  }
  
  // 临时跳过认证检查（开发模式）
  // TODO: 在生产环境中需要启用认证
  if (import.meta.env.DEV) {
    // 开发模式：自动设置一个模拟的管理员用户
    if (!authStore.isLoggedIn) {
      authStore.user = {
        user_id: 1,
        username: 'admin',
        nickname: '系统管理员',
        phone_number: '',
        email: 'admin@zhitang.com',
        avatar_url: ''
      }
      authStore.token = 'dev-token-' + Date.now()
    }
    next()
    return
  }
  
  // 生产环境的认证检查
  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      next('/login')
      return
    }
  }
  
  // 如果已登录且访问登录页，重定向到首页
  if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
    return
  }
  
  next()
})

export default router
