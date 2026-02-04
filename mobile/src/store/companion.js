/**
 * 同伴板块状态管理
 */
import { defineStore } from 'pinia'

export const useCompanionStore = defineStore('companion', {
  state: () => ({
    // 当前Tab
    currentTab: 'square', // square: 广场, friends: 好友
    
    // 广场动态列表
    posts: [],
    
    // 好友列表
    friends: [],
    
    // 聊天记录
    chatMessages: {},
    
    // 分类入口
    categories: [
      { id: 'checkin', name: '每日打卡', icon: '📅', color: '#FFD93D' },
      { id: 'challenge', name: '减肥成绩单', icon: '💪', color: '#6BCF7F' },
      { id: 'help', name: '减肥求助', icon: '🤝', color: '#4D96FF' },
      { id: 'glp', name: 'GLP减重', icon: '💉', color: '#FF6B9D' },
      { id: 'chat', name: '减肥杂谈', icon: '💬', color: '#C77DFF' }
    ]
  }),
  
  getters: {
    /**
     * 获取广场动态（按时间排序）
     */
    sortedPosts: (state) => {
      return [...state.posts].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      )
    },
    
    /**
     * 获取在线好友
     */
    onlineFriends: (state) => {
      return state.friends.filter(f => f.online)
    },
    
    /**
     * 获取与某个好友的聊天记录
     */
    getChatMessages: (state) => (friendId) => {
      return state.chatMessages[friendId] || []
    },
    
    /**
     * 获取未读消息数
     */
    unreadCount: (state) => {
      return state.friends.reduce((sum, friend) => sum + (friend.unreadCount || 0), 0)
    }
  },
  
  actions: {
    /**
     * 切换Tab
     */
    setCurrentTab(tab) {
      this.currentTab = tab
    },
    
    /**
     * 发布动态
     */
    publishPost(post) {
      const newPost = {
        id: Date.now(),
        ...post,
        created_at: new Date(),
        likes: 0,
        comments: 0,
        liked: false
      }
      
      this.posts.unshift(newPost)
      return newPost
    },
    
    /**
     * 点赞动态
     */
    likePost(postId) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        if (post.liked) {
          post.likes--
          post.liked = false
        } else {
          post.likes++
          post.liked = true
        }
      }
    },
    
    /**
     * 添加好友
     */
    addFriend(friend) {
      const newFriend = {
        id: Date.now(),
        ...friend,
        online: false,
        unreadCount: 0,
        lastMessage: null,
        lastMessageTime: null
      }
      
      this.friends.push(newFriend)
      this.chatMessages[newFriend.id] = []
      return newFriend
    },
    
    /**
     * 发送消息
     */
    sendMessage(friendId, content) {
      if (!this.chatMessages[friendId]) {
        this.chatMessages[friendId] = []
      }
      
      const message = {
        id: Date.now(),
        content,
        sender: 'me',
        timestamp: new Date(),
        read: false
      }
      
      this.chatMessages[friendId].push(message)
      
      // 更新好友最后消息
      const friend = this.friends.find(f => f.id === friendId)
      if (friend) {
        friend.lastMessage = content
        friend.lastMessageTime = new Date()
      }
      
      return message
    },
    
    /**
     * 接收消息（模拟）
     */
    receiveMessage(friendId, content) {
      if (!this.chatMessages[friendId]) {
        this.chatMessages[friendId] = []
      }
      
      const message = {
        id: Date.now(),
        content,
        sender: 'friend',
        timestamp: new Date(),
        read: false
      }
      
      this.chatMessages[friendId].push(message)
      
      // 更新好友信息
      const friend = this.friends.find(f => f.id === friendId)
      if (friend) {
        friend.lastMessage = content
        friend.lastMessageTime = new Date()
        friend.unreadCount = (friend.unreadCount || 0) + 1
      }
      
      return message
    },
    
    /**
     * 标记消息已读
     */
    markMessagesAsRead(friendId) {
      const messages = this.chatMessages[friendId]
      if (messages) {
        messages.forEach(msg => {
          if (msg.sender === 'friend') {
            msg.read = true
          }
        })
      }
      
      const friend = this.friends.find(f => f.id === friendId)
      if (friend) {
        friend.unreadCount = 0
      }
    },
    
    /**
     * 生成模拟数据
     */
    generateMockData() {
      // 生成模拟动态
      const mockPosts = [
        {
          id: 1,
          author: {
            id: 1,
            name: '爱坚持的禾',
            avatar: '👧',
            tags: ['健身党', 'BMI 20.3']
          },
          content: '午餐 鸡蛋蒸麦粥 碎牛 两包红薯干 160g 500卡 爬楼1h 200卡 晚餐 豌豆夹 300克 100卡',
          images: ['🍳', '🥗', '🏃'],
          category: 'checkin',
          categoryName: '每日打卡',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000),
          likes: 128,
          comments: 23,
          liked: false
        },
        {
          id: 2,
          author: {
            id: 2,
            name: '你王哥还是吃',
            avatar: '👦',
            tags: ['控糖新手']
          },
          content: '坚持记录，连最简单的记录都做不到就不要提减肥啦',
          images: [],
          category: 'challenge',
          categoryName: '减肥成绩单',
          created_at: new Date(Date.now() - 5 * 60 * 60 * 1000),
          likes: 89,
          comments: 15,
          liked: false
        },
        {
          id: 3,
          author: {
            id: 3,
            name: '小女子',
            avatar: '👧',
            tags: ['南阳', '大基数']
          },
          content: '寻找控糖搭子，一起加油！有没有同城的小伙伴？',
          images: [],
          category: 'help',
          categoryName: '控糖求助',
          created_at: new Date(Date.now() - 8 * 60 * 60 * 1000),
          likes: 56,
          comments: 34,
          liked: true
        }
      ]
      
      this.posts = mockPosts
      
      // 生成模拟好友
      const mockFriends = [
        {
          id: 101,
          name: '小糖豆',
          avatar: '👧',
          signature: '每天进步一点点',
          online: true,
          unreadCount: 2,
          lastMessage: '今天血糖控制得不错哦',
          lastMessageTime: new Date(Date.now() - 10 * 60 * 1000)
        },
        {
          id: 102,
          name: '健康小助手',
          avatar: '🤖',
          signature: '我是你的健康管家',
          online: true,
          unreadCount: 0,
          lastMessage: '记得按时测血糖',
          lastMessageTime: new Date(Date.now() - 2 * 60 * 60 * 1000)
        },
        {
          id: 103,
          name: '控糖达人',
          avatar: '👨',
          signature: '糖尿病管理5年经验',
          online: false,
          unreadCount: 0,
          lastMessage: '加油！',
          lastMessageTime: new Date(Date.now() - 24 * 60 * 60 * 1000)
        }
      ]
      
      this.friends = mockFriends
      
      // 生成模拟聊天记录
      this.chatMessages = {
        101: [
          {
            id: 1,
            content: '你好，我也在控糖',
            sender: 'friend',
            timestamp: new Date(Date.now() - 30 * 60 * 1000),
            read: true
          },
          {
            id: 2,
            content: '你好！很高兴认识你',
            sender: 'me',
            timestamp: new Date(Date.now() - 25 * 60 * 1000),
            read: true
          },
          {
            id: 3,
            content: '今天血糖控制得不错哦',
            sender: 'friend',
            timestamp: new Date(Date.now() - 10 * 60 * 1000),
            read: false
          }
        ],
        102: [
          {
            id: 1,
            content: '记得按时测血糖',
            sender: 'friend',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
            read: true
          }
        ],
        103: []
      }
    }
  }
})
