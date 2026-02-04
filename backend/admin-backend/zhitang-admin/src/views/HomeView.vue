<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用智糖小助手管理后台</h1>
      <p class="welcome-subtitle">智能糖尿病管理系统的管理中心</p>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon user-icon">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon chat-icon">
            <el-icon size="32"><ChatDotRound /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.totalMessages }}</div>
            <div class="stat-label">总对话数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon health-icon">
            <el-icon size="32"><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.totalCheckins }}</div>
            <div class="stat-label">总打卡数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon knowledge-icon">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.totalKnowledge }}</div>
            <div class="stat-label">知识库条目</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <el-card class="action-card" shadow="hover" @click="navigateTo('/users')">
          <div class="action-content">
            <el-icon size="24" class="action-icon"><User /></el-icon>
            <div class="action-text">用户管理</div>
          </div>
        </el-card>
        
        <el-card class="action-card" shadow="hover" @click="navigateTo('/chat/history')">
          <div class="action-content">
            <el-icon size="24" class="action-icon"><ChatDotRound /></el-icon>
            <div class="action-text">对话记录</div>
          </div>
        </el-card>
        
        <el-card class="action-card" shadow="hover" @click="navigateTo('/health/checkin')">
          <div class="action-content">
            <el-icon size="24" class="action-icon"><Monitor /></el-icon>
            <div class="action-text">健康数据</div>
          </div>
        </el-card>
        
        <el-card class="action-card" shadow="hover" @click="navigateTo('/knowledge/list')">
          <div class="action-content">
            <el-icon size="24" class="action-icon"><Document /></el-icon>
            <div class="action-text">知识库</div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 最近活动 -->
    <div class="recent-activities">
      <h2 class="section-title">最近活动</h2>
      <el-card shadow="never">
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="activity.timestamp"
            :type="activity.type"
          >
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ activity.description }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  ChatDotRound,
  Monitor,
  Document,
} from '@element-plus/icons-vue'

const router = useRouter()

// 统计数据
const stats = ref({
  totalUsers: 0,
  totalMessages: 0,
  totalCheckins: 0,
  totalKnowledge: 0,
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '新用户注册',
    description: '用户 "张三" 注册了账号',
    timestamp: '2024-01-15 10:30',
    type: 'primary',
  },
  {
    id: 2,
    title: '知识库更新',
    description: '添加了新的糖尿病饮食知识',
    timestamp: '2024-01-15 09:15',
    type: 'success',
  },
  {
    id: 3,
    title: '用户打卡',
    description: '用户 "李四" 完成了血糖打卡',
    timestamp: '2024-01-15 08:45',
    type: 'warning',
  },
  {
    id: 4,
    title: '系统维护',
    description: '系统进行了例行维护',
    timestamp: '2024-01-14 23:00',
    type: 'info',
  },
])

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用实际的API获取统计数据
    // 暂时使用模拟数据
    stats.value = {
      totalUsers: 1256,
      totalMessages: 8934,
      totalCheckins: 4567,
      totalKnowledge: 234,
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.welcome-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  border-radius: 12px;
  border: none;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.health-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.knowledge-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.quick-actions {
  margin-bottom: 40px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.action-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  text-align: center;
}

.action-icon {
  color: #409EFF;
  margin-bottom: 12px;
}

.action-text {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.recent-activities {
  margin-bottom: 40px;
}

.activity-content {
  padding-left: 8px;
}

.activity-title {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.activity-description {
  font-size: 14px;
  color: #7f8c8d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>