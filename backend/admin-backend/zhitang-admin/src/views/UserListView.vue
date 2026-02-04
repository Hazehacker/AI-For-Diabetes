<template>
  <div class="user-list-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-description">管理系统中的所有用户信息</p>
    </div>
    
    <!-- 搜索和筛选 -->
    <el-card class="search-card" shadow="never">
      <div class="search-form">
        <el-form :model="searchForm" inline>
          <el-form-item label="搜索用户">
            <el-input
              v-model="searchForm.keyword"
              placeholder="请输入用户名或昵称"
              clearable
              style="width: 300px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="用户状态">
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              clearable
              style="width: 150px"
            >
              <el-option label="全部" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <!-- 用户列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="table-header">
          <span class="table-title">用户列表</span>
          <div class="table-actions">
            <el-button type="primary" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="userStore.loading"
        :data="userStore.users"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="user_id" label="用户ID" width="80" />
        
        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="40" :src="row.avatar_url">
                <el-icon><UserIcon /></el-icon>
              </el-avatar>
              <div class="user-details">
                <div class="username">{{ row.username }}</div>
                <div class="nickname">{{ row.nickname }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="phone_number" label="手机号" width="130">
          <template #default="{ row }">
            <span v-if="row.phone_number">{{ row.phone_number }}</span>
            <span v-else class="text-muted">未绑定</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="email" label="邮箱" min-width="180">
          <template #default="{ row }">
            <span v-if="row.email">{{ row.email }}</span>
            <span v-else class="text-muted">未绑定</span>
          </template>
        </el-table-column>

        <el-table-column label="用户标签" min-width="150">
          <template #default="{ row }">
            <div class="user-tags">
              <el-tag
                v-for="tag in row.tags || []"
                :key="tag.tag_id"
                size="small"
                class="tag-item"
              >
                {{ tag.tag_name }}
              </el-tag>
              <span v-if="!row.tags || row.tags.length === 0" class="text-muted">无标签</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="积分" width="120">
          <template #default="{ row }">
            <div class="points-info">
              <span class="points-number">{{ row.points_balance || 0 }}</span>
              <el-button size="small" text @click="viewUserPoints(row)">
                <el-icon><View /></el-icon>
                明细
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="registration_date" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.registration_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="last_login_date" label="最后登录" width="160">
          <template #default="{ row }">
            <span v-if="row.last_login_date">{{ formatDate(row.last_login_date) }}</span>
            <span v-else class="text-muted">从未登录</span>
          </template>
        </el-table-column>

        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '活跃' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleViewUser(row)"
            >
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="handleEditUser(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              <el-icon><Switch /></el-icon>
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="userStore.currentPage"
          v-model:page-size="userStore.pageSize"
          :total="userStore.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  User as UserIcon,
  View,
  Edit,
  Switch,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
})

// 选中的用户
const selectedUsers = ref<User[]>([])

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 搜索用户
const handleSearch = () => {
  userStore.currentPage = 1
  userStore.searchUsers(searchForm.keyword)
}

// 查看用户积分明细
const viewUserPoints = async (user: User) => {
  try {
    // 这里应该打开积分明细对话框或跳转到积分页面
    // 暂时显示简单消息
    ElMessage.info(`查看用户 ${user.username} 的积分明细功能开发中...`)

    // 获取用户积分信息
    const pointsResponse = await fetch(`/api/users/${user.user_id}/points`)
    if (pointsResponse.ok) {
      const pointsData = await pointsResponse.json()
      ElMessage.success(`用户 ${user.username} 当前积分为: ${pointsData.current_points}`)
    }
  } catch (error) {
    console.error('获取用户积分失败:', error)
  }
}

// 监听用户数据变化，获取标签和积分信息
const loadUserTagsAndPoints = async (users: User[]) => {
  for (const user of users) {
    try {
      // 获取用户标签
      const tagsResponse = await fetch(`/api/users/${user.user_id}/tags`)
      if (tagsResponse.ok) {
        const tagsData = await tagsResponse.json()
        user.tags = tagsData.tags || []
      }

      // 获取用户积分
      const pointsResponse = await fetch(`/api/users/${user.user_id}/points`)
      if (pointsResponse.ok) {
        const pointsData = await pointsResponse.json()
        user.points_balance = pointsData.current_points
      }
    } catch (error) {
      console.error(`获取用户 ${user.username} 的标签和积分失败:`, error)
    }
  }
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  userStore.currentPage = 1
  userStore.fetchUsers()
}

// 刷新列表
const handleRefresh = () => {
  userStore.refreshUsers()
}

// 查看用户详情
const handleViewUser = (user: User) => {
  router.push(`/users/${user.user_id}`)
}

// 编辑用户
const handleEditUser = (user: User) => {
  ElMessage.info('编辑用户功能开发中...')
}

// 切换用户状态
const handleToggleStatus = async (user: User) => {
  try {
    const action = user.is_active ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 这里应该调用API更新用户状态
    // 暂时只更新本地状态
    userStore.updateUserStatus(user.user_id, !user.is_active)
    
    ElMessage.success(`用户${action}成功`)
  } catch {
    // 用户取消操作
  }
}

// 处理选择变化
const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  userStore.changePageSize(size)
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  userStore.changePage(page)
}

// 监听用户数据变化
watch(() => userStore.users, async (newUsers) => {
  if (newUsers && newUsers.length > 0) {
    await loadUserTagsAndPoints(newUsers)
  }
}, { immediate: true })

// 组件挂载时加载数据
onMounted(() => {
  userStore.fetchUsers()
})
</script>

<style scoped>
.user-list-container {
  /* max-width: 1400px; */
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.search-form {
  padding: 16px 0;
}

.table-card {
  border-radius: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
}

.nickname {
  font-size: 12px;
  color: #7f8c8d;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 200px;
}

.tag-item {
  margin: 0;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.points-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.points-number {
  font-size: 16px;
  font-weight: 600;
  color: #e74c3c;
}

.text-muted {
  color: #c0c4cc;
  font-style: italic;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-form .el-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form .el-form-item {
    margin-right: 0;
    margin-bottom: 16px;
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .table-actions {
    justify-content: center;
  }
}
</style>
