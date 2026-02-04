import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  getKnowledgeList,
  uploadKnowledge,
  deleteKnowledge,
  type KnowledgeItem,
  type KnowledgeListResponse,
  type UploadKnowledgeRequest,
  type DeleteKnowledgeRequest
} from '@/api/coze'
import { ElMessage } from 'element-plus'

export const useKnowledgeStore = defineStore('knowledge', () => {
  // 知识库状态
  const knowledgeItems = ref<KnowledgeItem[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  
  // 搜索和筛选状态
  const searchKeyword = ref('')
  const selectedCategory = ref('')

  // 获取知识库列表
  const fetchKnowledgeList = async (params?: {
    category?: string
    search?: string
    page?: number
    page_size?: number
  }) => {
    loading.value = true
    try {
      const response: KnowledgeListResponse = await getKnowledgeList({
        category: params?.category || selectedCategory.value,
        search: params?.search || searchKeyword.value,
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
      })
      
      knowledgeItems.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取知识库列表失败:', error)
      ElMessage.error('获取知识库列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 上传知识
  const uploadKnowledgeItem = async (data: UploadKnowledgeRequest): Promise<boolean> => {
    try {
      const response = await uploadKnowledge(data)
      ElMessage.success('知识上传成功')
      
      // 刷新列表
      await refreshKnowledgeList()
      
      return true
    } catch (error) {
      console.error('知识上传失败:', error)
      ElMessage.error('知识上传失败')
      return false
    }
  }

  // 删除知识
  const deleteKnowledgeItem = async (data: DeleteKnowledgeRequest): Promise<boolean> => {
    try {
      await deleteKnowledge(data)
      ElMessage.success('知识删除成功')
      
      // 刷新列表
      await refreshKnowledgeList()
      
      return true
    } catch (error) {
      console.error('知识删除失败:', error)
      ElMessage.error('知识删除失败')
      return false
    }
  }

  // 刷新知识库列表
  const refreshKnowledgeList = () => {
    return fetchKnowledgeList({
      category: selectedCategory.value,
      search: searchKeyword.value,
      page: currentPage.value,
      page_size: pageSize.value,
    })
  }

  // 搜索知识
  const searchKnowledge = (keyword: string) => {
    searchKeyword.value = keyword
    currentPage.value = 1
    return fetchKnowledgeList({
      category: selectedCategory.value,
      search: keyword,
      page: 1,
      page_size: pageSize.value,
    })
  }

  // 按分类筛选
  const filterByCategory = (category: string) => {
    selectedCategory.value = category
    currentPage.value = 1
    return fetchKnowledgeList({
      category,
      search: searchKeyword.value,
      page: 1,
      page_size: pageSize.value,
    })
  }

  // 清除筛选
  const clearFilters = () => {
    searchKeyword.value = ''
    selectedCategory.value = ''
    currentPage.value = 1
    return fetchKnowledgeList({
      page: 1,
      page_size: pageSize.value,
    })
  }

  // 分页
  const changePage = (page: number) => {
    currentPage.value = page
    return fetchKnowledgeList({
      category: selectedCategory.value,
      search: searchKeyword.value,
      page,
      page_size: pageSize.value,
    })
  }

  // 改变页面大小
  const changePageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    return fetchKnowledgeList({
      category: selectedCategory.value,
      search: searchKeyword.value,
      page: 1,
      page_size: size,
    })
  }

  // 根据ID获取知识项
  const getKnowledgeById = (kbId: number): KnowledgeItem | undefined => {
    return knowledgeItems.value.find(item => item.kb_id === kbId)
  }

  // 获取所有分类
  const getAllCategories = (): string[] => {
    const categories = new Set<string>()
    knowledgeItems.value.forEach(item => {
      if (item.category) {
        categories.add(item.category)
      }
    })
    return Array.from(categories).sort()
  }

  // 获取分类统计
  const getCategoryStats = () => {
    const stats: Record<string, number> = {}
    knowledgeItems.value.forEach(item => {
      const category = item.category || '未分类'
      stats[category] = (stats[category] || 0) + 1
    })
    return stats
  }

  // 获取关键词统计
  const getKeywordStats = () => {
    const keywordStats: Record<string, number> = {}
    knowledgeItems.value.forEach(item => {
      item.keywords.forEach(keyword => {
        keywordStats[keyword] = (keywordStats[keyword] || 0) + 1
      })
    })
    return keywordStats
  }

  // 批量删除知识
  const batchDeleteKnowledge = async (kbIds: number[]): Promise<boolean> => {
    try {
      const deletePromises = kbIds.map(kbId => deleteKnowledge({ kb_id: kbId }))
      await Promise.all(deletePromises)
      
      ElMessage.success(`成功删除 ${kbIds.length} 条知识`)
      
      // 刷新列表
      await refreshKnowledgeList()
      
      return true
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
      return false
    }
  }

  return {
    // 状态
    knowledgeItems,
    total,
    currentPage,
    pageSize,
    loading,
    searchKeyword,
    selectedCategory,
    
    // 方法
    fetchKnowledgeList,
    uploadKnowledgeItem,
    deleteKnowledgeItem,
    refreshKnowledgeList,
    searchKnowledge,
    filterByCategory,
    clearFilters,
    changePage,
    changePageSize,
    getKnowledgeById,
    getAllCategories,
    getCategoryStats,
    getKeywordStats,
    batchDeleteKnowledge,
  }
})
