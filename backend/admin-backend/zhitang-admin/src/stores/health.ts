import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  getHealthData,
  getCheckinRecords,
  getUserTags,
  getUserProfile,
  type CheckinRecord,
  type UserTag,
  type UserProfile,
  type HealthDataResponse
} from '@/api/health'
import { ElMessage } from 'element-plus'

export const useHealthStore = defineStore('health', () => {
  // 健康数据状态
  const healthData = ref<HealthDataResponse | null>(null)
  const checkinRecords = ref<CheckinRecord[]>([])
  const userTags = ref<UserTag[]>([])
  const userProfile = ref<UserProfile | null>(null)
  
  // 分页状态
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  
  // 当前选中的用户ID
  const selectedUserId = ref<number | null>(null)

  // 获取健康数据
  const fetchHealthData = async (params?: {
    user_id?: number
    start_date?: string
    end_date?: string
  }) => {
    loading.value = true
    try {
      const response: HealthDataResponse = await getHealthData({
        user_id: params?.user_id || selectedUserId.value,
        start_date: params?.start_date,
        end_date: params?.end_date,
      })
      
      healthData.value = response
      checkinRecords.value = response.checkin_records
      userTags.value = response.user_tags
      userProfile.value = response.user_profile
      
      return response
    } catch (error) {
      console.error('获取健康数据失败:', error)
      ElMessage.error('获取健康数据失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取打卡记录
  const fetchCheckinRecords = async (params?: {
    user_id?: number
    checkin_type?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) => {
    loading.value = true
    try {
      const response = await getCheckinRecords({
        user_id: params?.user_id || selectedUserId.value,
        checkin_type: params?.checkin_type,
        start_date: params?.start_date,
        end_date: params?.end_date,
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
      })
      
      checkinRecords.value = response.records
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取打卡记录失败:', error)
      ElMessage.error('获取打卡记录失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取用户标签
  const fetchUserTags = async (params?: {
    user_id?: number
  }) => {
    try {
      const response = await getUserTags({
        user_id: params?.user_id || selectedUserId.value,
      })
      
      userTags.value = response.tags
      return response
    } catch (error) {
      console.error('获取用户标签失败:', error)
      ElMessage.error('获取用户标签失败')
      throw error
    }
  }

  // 获取用户画像
  const fetchUserProfile = async (params?: {
    user_id?: number
  }) => {
    try {
      const response = await getUserProfile({
        user_id: params?.user_id || selectedUserId.value,
      })
      
      userProfile.value = response.profile
      return response
    } catch (error) {
      console.error('获取用户画像失败:', error)
      ElMessage.error('获取用户画像失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 设置选中的用户ID
  const setSelectedUserId = (userId: number | null) => {
    selectedUserId.value = userId
    // 清空当前数据
    healthData.value = null
    checkinRecords.value = []
    userTags.value = []
    userProfile.value = null
    total.value = 0
  }

  // 刷新数据
  const refreshData = () => {
    return fetchHealthData({
      user_id: selectedUserId.value,
    })
  }

  // 分页
  const changePage = (page: number) => {
    currentPage.value = page
    return fetchCheckinRecords({
      user_id: selectedUserId.value,
      page,
      page_size: pageSize.value,
    })
  }

  // 改变页面大小
  const changePageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    return fetchCheckinRecords({
      user_id: selectedUserId.value,
      page: 1,
      page_size: size,
    })
  }

  // 获取打卡类型统计
  const getCheckinTypeStats = () => {
    const stats = {
      blood_glucose: 0,
      diet: 0,
      exercise: 0,
      medication: 0,
    }
    
    checkinRecords.value.forEach(record => {
      if (record.checkin_type in stats) {
        stats[record.checkin_type as keyof typeof stats]++
      }
    })
    
    return stats
  }

  // 获取用户积分统计
  const getUserPointsStats = () => {
    if (!healthData.value) return { total: 0, earned: 0 }
    
    return {
      total: healthData.value.total_points,
      earned: healthData.value.total_checkins * 10, // 假设每次打卡10分
    }
  }

  // 获取标签统计
  const getTagStats = () => {
    const tagStats: Record<string, number> = {}
    
    userTags.value.forEach(tag => {
      const category = tag.tag_name.split('-')[0] || '其他'
      tagStats[category] = (tagStats[category] || 0) + 1
    })
    
    return tagStats
  }

  // 获取最近打卡记录
  const getRecentCheckins = (limit: number = 10) => {
    return checkinRecords.value
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit)
  }

  return {
    // 状态
    healthData,
    checkinRecords,
    userTags,
    userProfile,
    total,
    currentPage,
    pageSize,
    loading,
    selectedUserId,
    
    // 方法
    fetchHealthData,
    fetchCheckinRecords,
    fetchUserTags,
    fetchUserProfile,
    setSelectedUserId,
    refreshData,
    changePage,
    changePageSize,
    getCheckinTypeStats,
    getUserPointsStats,
    getTagStats,
    getRecentCheckins,
  }
})
