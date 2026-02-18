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
    
    // 当前选中的分类（用于筛选）
    selectedCategory: null, // null表示显示全部
    
    // 好友列表
    friends: [],
    
    // 聊天记录
    chatMessages: {},
    
    // 帖子评论
    postComments: {},
    
    // 分类入口
    categories: [
      { id: 1, name: '每日打卡', icon: '/static/ch/ch_fr_beat.png', color: '#F6D387' },
      { id: 2, name: '减肥成绩单', icon: '/static/ch/ch_fr_report.png', color: '#F6D387' },
      { id: 3, name: '减肥求助', icon: '/static/ch/ch_fr_qu.png', color: '#F6D387' },
      { id: 4, name: 'GLP减重', icon: '/static/ch/ch_fr_GLP.png', color: '#F6D387' },
      { id: 5, name: '减肥杂谈', icon: '/static/ch/ch_fr_other.png', color: '#F6D387' }
    ]
  }),
  
  getters: {
    /**
     * 获取广场动态（按时间排序，支持分类筛选）
     */
    sortedPosts: (state) => {
      let posts = [...state.posts]
      
      // 如果选择了分类，进行筛选
      if (state.selectedCategory !== null) {
        posts = posts.filter(p => p.categoryId === state.selectedCategory)
      }
      
      // 按时间排序
      return posts.sort((a, b) => 
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
     * 设置分类筛选
     */
    setSelectedCategory(categoryId) {
      this.selectedCategory = categoryId
    },
    
    /**
     * 清除分类筛选
     */
    clearCategoryFilter() {
      this.selectedCategory = null
    },
    
    /**
     * 添加帖子（从发布页面调用）
     */
    addPost(postData) {
      const category = this.categories.find(c => c.id === postData.categoryId)
      
      const newPost = {
        id: Date.now(),
        author: {
          id: 'current_user',
          name: '我',
          avatar: '👤',
          tags: ['新手']
        },
        content: postData.content,
        images: postData.images || [],
        categoryId: postData.categoryId,
        categoryName: category ? category.name : '未分类',
        location: postData.location,
        topic: postData.topic,
        created_at: new Date(),
        likes: 0,
        comments: 0,
        liked: false
      }
      
      this.posts.unshift(newPost)
      return newPost
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
     * 添加评论
     */
    addComment(postId, comment) {
      if (!this.postComments[postId]) {
        this.postComments[postId] = []
      }
      this.postComments[postId].unshift(comment)
      
      // 更新帖子评论数
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        post.comments = (post.comments || 0) + 1
      }
    },
    
    /**
     * 获取帖子评论（action版本，用于组件调用）
     */
    getPostComments(postId) {
      return this.postComments[postId] || []
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
     * 获取聊天消息
     */
    getChatMessages(friendId) {
      return this.chatMessages[friendId] || []
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
          categoryId: 1,
          categoryName: '每日打卡',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000),
          likes: 128,
          comments: 3,
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
          categoryId: 2,
          categoryName: '减肥成绩单',
          created_at: new Date(Date.now() - 5 * 60 * 60 * 1000),
          likes: 89,
          comments: 2,
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
          categoryId: 3,
          categoryName: '减肥求助',
          created_at: new Date(Date.now() - 8 * 60 * 60 * 1000),
          likes: 56,
          comments: 2,
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
      
      // 生成模拟评论数据
      this.postComments = {
        1: [
          {
            id: 101,
            author: { id: 10, name: '健康达人', avatar: '👨' },
            content: '太棒了！坚持就是胜利💪',
            created_at: new Date(Date.now() - 1 * 60 * 60 * 1000),
            likes: 12,
            liked: false,
            replies: [
              { id: 1011, author: { name: '爱坚持的禾' }, replyTo: '健康达人', content: '谢谢鼓励！', created_at: new Date() }
            ]
          },
          {
            id: 102,
            author: { id: 11, name: '小糖豆', avatar: '👧' },
            content: '请问红薯干是自己做的吗？',
            created_at: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
            likes: 5,
            liked: false,
            replies: []
          },
          {
            id: 103,
            author: { id: 12, name: '控糖新手', avatar: '👦' },
            content: '爬楼1小时好厉害！我才能坚持20分钟',
            created_at: new Date(Date.now() - 2 * 60 * 60 * 1000),
            likes: 8,
            liked: true,
            replies: []
          }
        ],
        2: [
          {
            id: 201,
            author: { id: 13, name: '加油鸭', avatar: '🦆' },
            content: '说得对！记录是第一步',
            created_at: new Date(Date.now() - 3 * 60 * 60 * 1000),
            likes: 6,
            liked: false,
            replies: []
          },
          {
            id: 202,
            author: { id: 14, name: '减肥小能手', avatar: '💪' },
            content: '我也是从记录开始的，现在已经瘦了10斤！',
            created_at: new Date(Date.now() - 4 * 60 * 60 * 1000),
            likes: 15,
            liked: true,
            replies: []
          }
        ],
        3: [
          {
            id: 301,
            author: { id: 15, name: '南阳老乡', avatar: '👋' },
            content: '我也是南阳的！可以加个好友吗？',
            created_at: new Date(Date.now() - 5 * 60 * 60 * 1000),
            likes: 3,
            liked: false,
            replies: []
          },
          {
            id: 302,
            author: { id: 16, name: '控糖搭子', avatar: '🤝' },
            content: '一起加油！我也在找小伙伴',
            created_at: new Date(Date.now() - 6 * 60 * 60 * 1000),
            likes: 7,
            liked: false,
            replies: []
          }
        ]
      }
    }
  }
})
