<template>
  <el-container class="main-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon v-if="isCollapse" size="24" color="#409EFF">
            <Sugar />
          </el-icon>
          <span v-else class="logo-text">智糖小助手</span>
        </div>
        <el-button
          type="text"
          @click="toggleCollapse"
          class="collapse-btn"
        >
          <el-icon>
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
        </el-button>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        
        <el-sub-menu index="user">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users">用户列表</el-menu-item>
          <el-menu-item index="/users/profile">用户详情</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="chat">
          <template #title>
            <el-icon><ChatDotRound /></el-icon>
            <span>对话管理</span>
          </template>
          <el-menu-item index="/chat/history">对话记录</el-menu-item>
          <el-menu-item index="/chat/sessions">会话列表</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="health">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>健康管理</span>
          </template>
          <el-menu-item index="/health/checkin">打卡记录</el-menu-item>
          <el-menu-item index="/health/profile">用户画像</el-menu-item>
          <el-menu-item index="/health/tags">用户标签</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="knowledge">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>知识库管理</span>
          </template>
          <el-menu-item index="/knowledge/list">知识列表</el-menu-item>
          <el-menu-item index="/knowledge/upload">上传知识</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="coze">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>Coze管理</span>
          </template>
          <el-menu-item index="/coze/audio">音频记录</el-menu-item>
          <el-menu-item index="/coze/token">Token管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="user?.avatar_url">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ user?.nickname || user?.username }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  User,
  ChatDotRound,
  Monitor,
  Document,
  Sugar,
  Expand,
  Fold,
  ArrowDown,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前用户信息
const user = computed(() => authStore.user)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const breadcrumbList = matched.map(item => ({
    name: item.meta?.title as string,
    path: item.path,
  }))
  
  // 添加首页
  if (breadcrumbList.length > 0 && breadcrumbList[0].path !== '/') {
    breadcrumbList.unshift({ name: '首页', path: '/' })
  }
  
  return breadcrumbList
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 处理用户下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        authStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}

// 监听路由变化，更新面包屑
watch(
  () => route.path,
  () => {
    // 路由变化时的处理逻辑
  },
  { immediate: true }
)
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #434a50;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.logo-text {
  margin-left: 8px;
}

.collapse-btn {
  color: white;
  font-size: 16px;
}

.sidebar-menu {
  border: none;
  background-color: #304156;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background-color: #263445;
  color: #409EFF;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #409EFF;
  color: white;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #606266;
}

.dropdown-icon {
  font-size: 12px;
  color: #c0c4cc;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header {
    padding: 0 16px;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style>
