import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserList, type User, type UserListResponse } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref<User[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 获取用户列表
  const fetchUsers = async (params?: {
    page?: number
    page_size?: number
    search?: string
  }) => {
    loading.value = true
    try {
      const response: UserListResponse = await getUserList({
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
        search: params?.search,
      })
      
      users.value = response.users
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取用户列表失败:', error)
      ElMessage.error('获取用户列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 刷新用户列表
  const refreshUsers = () => {
    return fetchUsers({
      page: currentPage.value,
      page_size: pageSize.value,
    })
  }

  // 搜索用户
  const searchUsers = (searchTerm: string) => {
    return fetchUsers({
      page: 1,
      page_size: pageSize.value,
      search: searchTerm,
    })
  }

  // 分页
  const changePage = (page: number) => {
    currentPage.value = page
    return fetchUsers({
      page,
      page_size: pageSize.value,
    })
  }

  // 改变页面大小
  const changePageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    return fetchUsers({
      page: 1,
      page_size: size,
    })
  }

  // 根据ID获取用户
  const getUserById = (userId: number): User | undefined => {
    return users.value.find(user => user.user_id === userId)
  }

  // 更新用户状态（本地）
  const updateUserStatus = (userId: number, isActive: boolean) => {
    const user = getUserById(userId)
    if (user) {
      user.is_active = isActive
    }
  }

  return {
    // 状态
    users,
    total,
    loading,
    currentPage,
    pageSize,
    
    // 方法
    fetchUsers,
    refreshUsers,
    searchUsers,
    changePage,
    changePageSize,
    getUserById,
    updateUserStatus,
  }
})
