import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  getChatHistory, 
  getCozeChatHistory, 
  getChatSessions,
  type ChatMessage, 
  type ChatHistoryResponse,
  type ChatSession,
  type ChatSessionsResponse
} from '@/api/chat'
import { ElMessage } from 'element-plus'

export const useChatStore = defineStore('chat', () => {
  // 聊天记录状态
  const messages = ref<ChatMessage[]>([])
  const messagesTotal = ref(0)
  const messagesLoading = ref(false)
  const messagesCurrentPage = ref(1)
  const messagesPageSize = ref(20)

  // 聊天会话状态
  const sessions = ref<ChatSession[]>([])
  const sessionsTotal = ref(0)
  const sessionsLoading = ref(false)
  const sessionsCurrentPage = ref(1)
  const sessionsPageSize = ref(20)

  // 当前选中的用户ID
  const selectedUserId = ref<number | null>(null)

  // 获取聊天记录
  const fetchChatHistory = async (params?: {
    user_id?: number
    page?: number
    page_size?: number
    start_date?: string
    end_date?: string
  }) => {
    messagesLoading.value = true
    try {
      const response: ChatHistoryResponse = await getChatHistory({
        user_id: params?.user_id || selectedUserId.value,
        page: params?.page || messagesCurrentPage.value,
        page_size: params?.page_size || messagesPageSize.value,
        start_date: params?.start_date,
        end_date: params?.end_date,
      })
      
      messages.value = response.messages
      messagesTotal.value = response.total
      messagesCurrentPage.value = response.page
      messagesPageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取聊天记录失败:', error)
      ElMessage.error('获取聊天记录失败')
      throw error
    } finally {
      messagesLoading.value = false
    }
  }

  // 获取Coze聊天记录
  const fetchCozeChatHistory = async (params?: {
    user_id?: number
    page?: number
    page_size?: number
    start_date?: string
    end_date?: string
  }) => {
    messagesLoading.value = true
    try {
      const response: ChatHistoryResponse = await getCozeChatHistory({
        user_id: params?.user_id || selectedUserId.value,
        page: params?.page || messagesCurrentPage.value,
        page_size: params?.page_size || messagesPageSize.value,
        start_date: params?.start_date,
        end_date: params?.end_date,
      })
      
      messages.value = response.messages
      messagesTotal.value = response.total
      messagesCurrentPage.value = response.page
      messagesPageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取Coze聊天记录失败:', error)
      ElMessage.error('获取Coze聊天记录失败')
      throw error
    } finally {
      messagesLoading.value = false
    }
  }

  // 获取聊天会话列表
  const fetchChatSessions = async (params?: {
    user_id?: number
    page?: number
    page_size?: number
  }) => {
    sessionsLoading.value = true
    try {
      const response: ChatSessionsResponse = await getChatSessions({
        user_id: params?.user_id || selectedUserId.value,
        page: params?.page || sessionsCurrentPage.value,
        page_size: params?.page_size || sessionsPageSize.value,
      })
      
      sessions.value = response.sessions
      sessionsTotal.value = response.total
      sessionsCurrentPage.value = response.page
      sessionsPageSize.value = response.page_size
      
      return response
    } catch (error) {
      console.error('获取聊天会话失败:', error)
      ElMessage.error('获取聊天会话失败')
      throw error
    } finally {
      sessionsLoading.value = false
    }
  }

  // 设置选中的用户ID
  const setSelectedUserId = (userId: number | null) => {
    selectedUserId.value = userId
    // 清空当前数据
    messages.value = []
    sessions.value = []
    messagesTotal.value = 0
    sessionsTotal.value = 0
  }

  // 刷新聊天记录
  const refreshMessages = () => {
    return fetchChatHistory({
      user_id: selectedUserId.value,
      page: messagesCurrentPage.value,
      page_size: messagesPageSize.value,
    })
  }

  // 刷新聊天会话
  const refreshSessions = () => {
    return fetchChatSessions({
      user_id: selectedUserId.value,
      page: sessionsCurrentPage.value,
      page_size: sessionsPageSize.value,
    })
  }

  // 分页 - 聊天记录
  const changeMessagesPage = (page: number) => {
    messagesCurrentPage.value = page
    return fetchChatHistory({
      user_id: selectedUserId.value,
      page,
      page_size: messagesPageSize.value,
    })
  }

  // 分页 - 聊天会话
  const changeSessionsPage = (page: number) => {
    sessionsCurrentPage.value = page
    return fetchChatSessions({
      user_id: selectedUserId.value,
      page,
      page_size: sessionsPageSize.value,
    })
  }

  // 根据会话ID获取消息
  const getMessagesBySessionId = (sessionId: string): ChatMessage[] => {
    return messages.value.filter(message => 
      message.message_content.includes(sessionId)
    )
  }

  // 获取用户的消息统计
  const getUserMessageStats = (userId: number) => {
    const userMessages = messages.value.filter(msg => msg.user_id === userId)
    const userMessageCount = userMessages.length
    const aiMessageCount = userMessages.filter(msg => msg.sender === 'ai').length
    const voiceMessageCount = userMessages.filter(msg => msg.message_type === 'voice').length
    
    return {
      total: userMessageCount,
      user: userMessageCount - aiMessageCount,
      ai: aiMessageCount,
      voice: voiceMessageCount,
    }
  }

  return {
    // 聊天记录状态
    messages,
    messagesTotal,
    messagesLoading,
    messagesCurrentPage,
    messagesPageSize,
    
    // 聊天会话状态
    sessions,
    sessionsTotal,
    sessionsLoading,
    sessionsCurrentPage,
    sessionsPageSize,
    
    // 当前选中用户
    selectedUserId,
    
    // 方法
    fetchChatHistory,
    fetchCozeChatHistory,
    fetchChatSessions,
    setSelectedUserId,
    refreshMessages,
    refreshSessions,
    changeMessagesPage,
    changeSessionsPage,
    getMessagesBySessionId,
    getUserMessageStats,
  }
})
