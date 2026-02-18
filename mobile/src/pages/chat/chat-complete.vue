<template>
  <view class="page-container">
  <view class="chat-page" :class="{ 'child-mode': isChildMode }">
    <!-- 顶部导航栏 -->
    <view class="chat-header">
      <view class="header-left" @tap="toggleProfileDrawer">
        <image class="user-avatar" :src="userAvatar" mode="aspectFill"></image>
      </view>
      
      <view class="header-center">
        <view class="title-row">
          <image class="robot-avatar-mini" :src="currentRobot.avatar" mode="aspectFill"></image>
          <text class="chat-title">{{ currentRobot.name }}</text>
          <view class="robot-switch-icon" @tap="showRobotSelector">
            <text class="icon-text">▼</text>
          </view>
        </view>
        <view class="online-status">
          <view class="status-dot"></view>
          <text class="status-text">在线</text>
        </view>
      </view>
      
      <view class="header-right" @tap="showCheckinCalendar">
        <view class="calendar-btn">
          <image class="calendar-icon" src="/static/ch/ch_index_finish.png" mode="aspectFit"></image>
        </view>
        <view v-if="todayCheckinCount > 0" class="checkin-badge">
          {{ todayCheckinCount }}
        </view>
      </view>
    </view>

    <!-- 消息列表 -->
    <scroll-view 
      class="message-list" 
      :scroll-y="true"
      :scroll-into-view="scrollTarget"
      :scroll-with-animation="true"
      :show-scrollbar="false"
      @scrolltoupper="loadMoreHistory"
    >
      <!-- 快捷入口按钮 - 儿童模式 -->
      <view v-if="isChildMode" class="shortcuts-bar">
        <view class="shortcut-item" @tap="goToSpecialistScene('report')">
          <image class="shortcut-icon" src="/static/ch/ch_que_report.png" mode="aspectFit"></image>
          <text class="shortcut-name">报告解读</text>
        </view>
        <view class="shortcut-divider"></view>
        <view class="shortcut-item" @tap="goToSpecialistScene('drug')">
          <image class="shortcut-icon" src="/static/ch/ch_que_med.png" mode="aspectFit"></image>
          <text class="shortcut-name">药品管理</text>
        </view>
        <view class="shortcut-divider"></view>
        <view class="shortcut-item" @tap="goToSpecialistScene('diary')">
          <image class="shortcut-icon" src="/static/ch/ch_que_log.png" mode="aspectFit"></image>
          <text class="shortcut-name">健康日志</text>
        </view>
        <view class="shortcut-divider"></view>
        <view class="shortcut-item" @tap="goToSpecialistScene('knowledge')">
          <image class="shortcut-icon" src="/static/ch/ch_que_kn.png" mode="aspectFit"></image>
          <text class="shortcut-name">知识问答</text>
        </view>
      </view>

      <!-- 快捷入口按钮 - 青少年/家长模式 -->
      <view v-else class="specialist-shortcuts">
        <text class="shortcuts-title">🏥 AI专科对话</text>
        <view class="shortcuts-grid">
          <view class="shortcut-item-default" @tap="goToSpecialistScene('report')">
            <text class="shortcut-icon-emoji">📊</text>
            <text class="shortcut-name-default">报告解读</text>
          </view>
          <view class="shortcut-item-default" @tap="goToSpecialistScene('drug')">
            <text class="shortcut-icon-emoji">💊</text>
            <text class="shortcut-name-default">药品管理</text>
          </view>
          <view class="shortcut-item-default" @tap="goToSpecialistScene('diary')">
            <text class="shortcut-icon-emoji">📝</text>
            <text class="shortcut-name-default">健康日志</text>
          </view>
          <view class="shortcut-item-default" @tap="goToSpecialistScene('knowledge')">
            <text class="shortcut-icon-emoji">💡</text>
            <text class="shortcut-name-default">知识问答</text>
          </view>
        </view>
      </view>

      <!-- 糖糖问答每日判断题 - 青少年/家长模式（内嵌卡片） -->
      <view v-if="dailyQuestion && !isChildMode" class="daily-question-card">
        <view class="question-header">
          <text class="question-icon">🍬</text>
          <text class="question-title">糖糖问答</text>
          <text class="question-badge">每日一题</text>
        </view>

        <text class="question-text">{{ dailyQuestion.question }}</text>

        <!-- 未答题：显示选择按钮 -->
        <view v-if="!hasAnswered" class="answer-buttons">
          <view class="answer-btn true-btn" @tap="submitAnswer(true)">
            <text class="btn-text">✓ 真的</text>
          </view>
          <view class="answer-btn false-btn" @tap="submitAnswer(false)">
            <text class="btn-text">✗ 假的</text>
          </view>
        </view>

        <!-- 已答题：显示结果和解析 -->
        <view v-else class="answer-result">
          <view class="stats-bar">
            <view class="stat-item">
              <text class="stat-label">真的</text>
              <view class="stat-progress">
                <view class="stat-fill true-fill" :style="{ width: answerStats.truePercent + '%' }"></view>
              </view>
              <text class="stat-percent">{{ answerStats.truePercent }}%</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">假的</text>
              <view class="stat-progress">
                <view class="stat-fill false-fill" :style="{ width: answerStats.falsePercent + '%' }"></view>
              </view>
              <text class="stat-percent">{{ answerStats.falsePercent }}%</text>
            </view>
          </view>

          <view class="correct-answer">
            <text class="answer-label">正确答案：</text>
            <text class="answer-value" :class="dailyQuestion.correctAnswer ? 'correct-true' : 'correct-false'">
              {{ dailyQuestion.correctAnswer ? '✓ 真的' : '✗ 假的' }}
            </text>
          </view>

          <view class="explanation">
            <text class="explanation-text">{{ dailyQuestion.explanation }}</text>
          </view>
        </view>
      </view>

      <!-- 加载更多提示 -->
      <view v-if="loadingHistory" class="loading-more">
        <view class="loading-spinner"></view>
        <text class="loading-text">加载历史消息...</text>
      </view>

      <!-- 消息项 -->
      <view 
        v-for="(msg, index) in messages" 
        :key="msg.id"
        :id="'msg-' + msg.id"
        class="message-item"
        :class="msg.role === 'assistant' ? 'message-item-ai' : 'message-item-user'"
      >
        <!-- AI消息 -->
        <view v-if="msg.role === 'assistant'" class="message-ai">
          <image class="ai-avatar" :src="currentRobot.avatar" mode="aspectFill"></image>
          <view class="message-content">
            <view class="message-bubble bubble-ai">
              <view class="message-text markdown-content">
                <rich-text :nodes="formatMarkdown(msg.content)"></rich-text>
              </view>
              <text class="message-time message-time-ai">{{ formatTime(msg.timestamp) }}</text>
            </view>
            <view class="message-footer">
              <view class="voice-play-btn" @tap="playVoice(msg)" v-if="msg.content">
                <text class="play-icon">{{ playingMsgId === msg.id ? '⏸' : '🔊' }}</text>
                <text class="play-text">播放</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 用户消息 -->
        <view v-else class="message-user">
          <image class="user-chat-avatar" :src="userAvatar" mode="aspectFill"></image>
          <view class="message-content message-content-user">
            <view class="message-bubble bubble-user">
              <text class="message-text">{{ msg.content }}</text>
              <text class="message-time message-time-user">{{ formatTime(msg.timestamp) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- AI输入中 -->
      <view v-if="isTyping" class="typing-indicator">
        <image class="typing-avatar" :src="currentRobot.avatar" mode="aspectFill"></image>
        <view class="typing-content">
          <view class="typing-dots">
            <view class="dot"></view>
            <view class="dot"></view>
            <view class="dot"></view>
          </view>
          <text class="typing-text">{{ currentRobot.name }}正在思考...</text>
        </view>
      </view>

      <!-- 底部锚点：用于 scroll-into-view 精确滚动到最底部 -->
      <view id="chat-bottom-anchor" style="height: 1rpx;"></view>
    </scroll-view>

    <!-- 输入区域（对齐 H5 P-CHAT 布局与样式） -->
    <view class="input-area">
      <!-- 快捷打卡 -->
      <view class="quick-actions">
        <button class="quick-checkin-btn" @tap="quickCheckin" style="margin-left: 15px;">
          <image class="checkin-icon" src="/static/ch/ch_index_finish.png" mode="aspectFit"></image>
          <text class="btn-text">今日打卡</text>
        </button>
      </view>

      <!-- 底部输入卡片：整体是一个大圆角白色条，内部左侧是图标，右侧是输入框 -->
      <view class="input-container">
        <!-- 左侧图标区 -->
        <view class="input-icons">
          <!-- 语音输入按钮 -->
          <view
            class="voice-btn"
            @tap="toggleVoiceRecording"
            :class="{ recording: isRecording }"
          >
            <text class="fa-solid fa-microphone voice-icon"></text>
          </view>

          <!-- TTS 语音播报开关 -->
          <view 
            class="tts-btn" 
            @tap="toggleTTS"
            :class="{ active: ttsEnabled }"
          >
            <text :class="['fa-solid', ttsEnabled ? 'fa-volume-high' : 'fa-volume-xmark', 'icon']"></text>
          </view>
        </view>

        <!-- 右侧输入框区域 -->
        <view class="input-wrapper">
          <textarea 
            class="text-input"
            v-model="inputText"
            placeholder="输入您的问题..."
            :auto-height="true"
            :maxlength="500"
            @confirm="sendMessage"
          />
          <view 
            class="send-btn" 
            @tap="sendMessage"
            :class="{ disabled: !canSend }"
          >
            <text class="fa-solid fa-paper-plane icon"></text>
          </view>
        </view>
      </view>
    </view>

    <!-- 个人中心抽屉 -->
    <ProfileDrawer 
      :visible="showProfile"
      @close="toggleProfileDrawer"
      @logout="handleLogout"
      @checkin="handleDrawerCheckin"
    />

    <!-- 机器人选择器 -->
    <RobotSelector
      :visible="showRobotModal"
      :robots="robots"
      :current="currentRobot"
      @close="hideRobotSelector"
      @select="selectRobot"
    />

    <!-- 打卡日历 -->
    <CheckinCalendar
      :visible="showCalendar"
      :records="checkinRecords"
      @close="hideCheckinCalendar"
    />

    <!-- 今日打卡弹窗 -->
    <CheckinForm
      :visible="showCheckinForm"
      @close="hideCheckinForm"
      @submit="submitCheckin"
    />

    <!-- 儿童模式 - 糖糖问答弹窗 -->
    <view v-if="showDailyQuestionPopup && isChildMode" class="question-popup-overlay" @tap="closeDailyQuestionPopup">
      <view class="question-popup-modal" @tap.stop>
        <view class="question-header">
          <text class="question-icon">🍬</text>
          <text class="question-title">糖糖问答</text>
          <text class="question-badge">每日一题</text>
        </view>

        <text class="question-text">{{ dailyQuestion?.question }}</text>

        <view class="answer-buttons">
          <view class="answer-btn true-btn" @tap="submitAnswerAndClose(true)">
            <text class="btn-text">✓ 真的</text>
          </view>
          <view class="answer-btn false-btn" @tap="submitAnswerAndClose(false)">
            <text class="btn-text">✗ 假的</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 录音状态 -->
    <view v-if="isRecording" class="recording-overlay">
      <view class="recording-modal">
        <view class="recording-icon">🎤</view>
        <text class="recording-time">{{ recordingTime }}s</text>
        <view class="recording-actions">
          <button class="action-btn cancel-btn" @tap="cancelRecording">
            <text class="icon">✕</text>
            <text>取消</text>
          </button>
          <button class="action-btn send-btn" @tap="stopRecording">
            <text class="icon">✓</text>
            <text>发送</text>
          </button>
        </view>
        <text class="recording-hint">正在录音中...</text>
      </view>
    </view>
  </view>
  
  <!-- 自定义 TabBar -->
  <CustomTabBar :current="1" />
  </view>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { useChatStore } from '@/store/chat'
import { useDashboardStore } from '@/store/dashboard'
import { chatApi, checkinApi, ttsApi } from '@/api'
import ProfileDrawer from '@/components/ProfileDrawer.vue'
import RobotSelector from '@/components/RobotSelector.vue'
import CheckinCalendar from '@/components/CheckinCalendar.vue'
import CustomTabBar from '@/components/CustomTabBar.vue'
import CheckinForm from '@/components/CheckinForm.vue'

const userStore = useUserStore()
const chatStore = useChatStore()
const dashboardStore = useDashboardStore()

// 用户角色检测
const isChildMode = computed(() => dashboardStore.userRole === 'child_under_12')

// 顶部与状态
const showProfile = ref(false)
const showRobotModal = ref(false)
const showCalendar = ref(false)
const showCheckinForm = ref(false)
const showDailyQuestionPopup = ref(false)
const todayCheckinCount = ref(0)

// 聊天相关
const inputText = ref('')
const scrollTarget = ref('')
const isTyping = ref(false)
const isRecording = ref(false)
const recordingTime = ref(0)
const loadingHistory = ref(false)
const historyPage = ref(1)
const hasMoreHistory = ref(true)
const ttsEnabled = computed(() => chatStore.enableTTS)
const messages = computed(() => chatStore.messages)

// 糖糖问答相关
const dailyQuestion = computed(() => chatStore.dailyQuestion)
const hasAnswered = computed(() => chatStore.hasAnswered)
const answerStats = computed(() => chatStore.getAnswerStats())

const submitAnswer = (choice) => {
  chatStore.submitAnswer(choice)
}

// 儿童模式 - 弹窗提交答案并关闭
const submitAnswerAndClose = (choice) => {
  chatStore.submitAnswer(choice)
  showDailyQuestionPopup.value = false
  uni.showToast({
    title: choice === chatStore.dailyQuestion?.correctAnswer ? '回答正确！' : '回答错误',
    icon: choice === chatStore.dailyQuestion?.correctAnswer ? 'success' : 'none'
  })
}

// 关闭每日问答弹窗
const closeDailyQuestionPopup = () => {
  showDailyQuestionPopup.value = false
}

// 检查是否需要显示每日问答弹窗（儿童模式且今天未答题）
const checkDailyQuestionPopup = () => {
  if (isChildMode.value && dailyQuestion.value && !hasAnswered.value) {
    showDailyQuestionPopup.value = true
  }
}

// 用户头像（根据角色选择不同头像）
const userAvatar = computed(() => {
  if (isChildMode.value) {
    return '/static/ch/ch_home_avatar.png'
  }
  return 'https://s.coze.cn/image/es6fUICmNgw/'
})

// 机器人配置（根据角色选择不同头像）
const robots = computed(() => {
  if (isChildMode.value) {
    return [
      {
        id: 'xiaojing',
        name: '小助手1',
        voiceId: '601012',
        avatar: '/static/ch/ch_que_fe.png',
        description: '温柔可爱的女生好朋友'
      },
      {
        id: 'zhimeng',
        name: '小助手2',
        voiceId: '101015',
        avatar: '/static/ch/ch_que_ma.png',
        description: '聪明理性的男生好朋友'
      }
    ]
  }
  return [
    {
      id: 'xiaojing',
      name: '小助手1',
      voiceId: '601012',
      avatar: '/static/nvsheng.png',
      description: '温柔可爱的女生好朋友'
    },
    {
      id: 'zhimeng',
      name: '小助手2',
      voiceId: '101015',
      avatar: '/static/nansheng.png',
      description: '聪明理性的男生好朋友'
    }
  ]
})
const currentRobot = ref(null)

// 初始化当前机器人
watch(robots, (newRobots) => {
  if (newRobots.length > 0 && !currentRobot.value) {
    currentRobot.value = newRobots[0]
  }
}, { immediate: true })

// 录音 & 播放
const recordingTimer = ref(null)
const recordingOverlayTimer = ref(null)
let audioContext = null
const playingMsgId = ref(null)

// 打卡记录
const checkinRecords = ref([])

const canSend = computed(() => !!inputText.value.trim())

// 安全转换时间戳为 ISO 字符串
const toISOStringSafe = (ts) => {
  if (!ts) return new Date().toISOString()
  const d = new Date(ts)
  if (Number.isNaN(d.getTime())) return new Date().toISOString()
  return d.toISOString()
}

// 加载对话历史（参考 H5 前端）
const loadChatHistory = async (page = 1, append = false) => {
  if (!userStore.userId || !chatStore.conversationId) return
  if (loadingHistory.value) return

  loadingHistory.value = true
  try {
    const pageSize = 20
    const res = await chatApi.getHistory({
      user_id: userStore.userId,
      conversation_id: chatStore.conversationId,
      page,
      page_size: pageSize
    })

    // 接口返回结构：{ success, data: { turns: [...] } }
    if (res && res.success && res.data) {
      const turns = Array.isArray(res.data)
        ? res.data
        : (Array.isArray(res.data.turns) ? res.data.turns : [])

      const historyMessages = []

      turns.forEach((turn, index) => {
        const baseId = `h-${page}-${index}`

        if (turn.query) {
          historyMessages.push({
            id: `${baseId}-u`,
            role: 'user',
            content: turn.query,
            timestamp: toISOStringSafe(turn.created_at)
          })
        }

        if (turn.ai_content) {
          historyMessages.push({
            id: `${baseId}-a`,
            role: 'assistant',
            content: turn.ai_content,
            timestamp: toISOStringSafe(turn.ai_created_at || turn.created_at)
          })
        }
      })

      if (append) {
        // 追加更早的历史到顶部
        chatStore.messages = [...historyMessages, ...chatStore.messages]
      } else {
        // 首次加载或刷新，直接替换
        chatStore.messages = historyMessages
      }

      hasMoreHistory.value = historyMessages.length === pageSize * 2 || turns.length === pageSize
      historyPage.value = page

      if (!append) {
        // 首次加载后滚动到底部（多触发一次，避免在 H5 上因为渲染时机导致没有滚到底）
        scrollToBottom()
        setTimeout(() => {
          scrollToBottom()
        }, 300)
      }
    }
  } catch (e) {
    console.error('加载对话历史失败:', e)
  } finally {
    loadingHistory.value = false
  }
}

// 上拉触顶加载更早历史
const loadMoreHistory = async () => {
  if (!hasMoreHistory.value) return
  const nextPage = historyPage.value + 1
  await loadChatHistory(nextPage, true)
}

onMounted(async () => {
  // 登录校验
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }

  // 会话ID
  await chatStore.fetchLatestSession(userStore.userId)

  // 加载历史对话记录
  await loadChatHistory()

  // 今日打卡次数 & 记录
  await loadCheckinRecords()
  await loadTodayCheckinCount()
  
  // 生成每日题目
  chatStore.generateDailyQuestion()

  // 恢复选择的机器人
  // 默认使用“小助手1”；如果你希望记住上次选择，把下面这一段取消注释即可
  // const savedRobotId = uni.getStorageSync('selectedRobot')
  // if (savedRobotId) {
  //   const robot = robots.value.find(r => r.id === savedRobotId)
  //   if (robot) currentRobot.value = robot
  // }
})

// 页面每次显示（包括从其他页面返回、微信小程序前后台切换等）时，自动滚动到最新消息
onShow(() => {
  scrollToBottom()
  setTimeout(() => {
    scrollToBottom()
  }, 300)
  
  // 儿童模式：检查是否需要显示每日问答弹窗
  setTimeout(() => {
    checkDailyQuestionPopup()
  }, 500)
})

onUnmounted(() => {
  stopAudio()
  if (recordingTimer.value) clearInterval(recordingTimer.value)
})

// ========== 聊天逻辑 ==========
const sendMessage = async () => {
  if (!canSend.value) return

  const content = inputText.value.trim()
  inputText.value = ''

  chatStore.addMessage({ role: 'user', content })
  scrollToBottom()

  isTyping.value = true
  let assistantMsgId = null
  try {
    const payload = {
      user_id: userStore.userId,
      message_content: content,
      enable_tts: ttsEnabled.value,
      ...(chatStore.conversationId ? { conversation_id: chatStore.conversationId } : {})
    }

    let lastScrollAt = 0
    let hasFirstDelta = false

    await chatApi.streamMessage(payload, {
      onConversationId: (cid) => {
        if (cid && cid !== chatStore.conversationId) chatStore.setConversationId(cid)
      },
      onDelta: (delta) => {
        if (!delta) return

        // 首次收到增量时再创建AI气泡，避免提前插入“空内容”气泡
        if (!assistantMsgId) {
          assistantMsgId = chatStore.addMessage({ role: 'assistant', content: '' })
        }

        // 收到首个增量后，就可以关闭“正在思考”指示，避免出现两个气泡
        if (!hasFirstDelta) {
          hasFirstDelta = true
          isTyping.value = false
        }

        chatStore.appendMessageContent(assistantMsgId, delta)

        // 轻量节流，避免每个chunk都触发滚动导致卡顿
        const now = Date.now()
        if (now - lastScrollAt > 200) {
          lastScrollAt = now
          scrollToBottom()
        }
      },
      onDone: () => {
        // done 在 SSE 中可能早于网络 close，先标记UI状态
        isTyping.value = false
      }
    })

    // 流结束后，确保至少滚动一次，并结束输入状态
    isTyping.value = false

    // 如果最终还是空内容，给一个兜底提示，避免出现“只剩时间气泡”
    if (assistantMsgId) {
      const finalMsg = chatStore.messages.find((m) => m.id === assistantMsgId)
      if (!finalMsg?.content) {
        chatStore.setMessageContent(assistantMsgId, '抱歉，我暂时没有收到回复，请稍后重试。')
      }
    } else {
      // 完全没有任何增量且未创建气泡，补一条错误提示
      assistantMsgId = chatStore.addMessage({
        role: 'assistant',
        content: '抱歉，我暂时没有收到回复，请稍后重试。'
      })
    }
    scrollToBottom()
  } catch (error) {
    isTyping.value = false
    if (assistantMsgId) {
      chatStore.setMessageContent(assistantMsgId, '发送失败，请重试。')
    }
    uni.showToast({ title: '发送失败，请重试', icon: 'none' })
  }
}

const scrollToBottom = () => {
  // H5 端：直接参考 smart-sugar-assistant-main 的实现，用原生 DOM 滚动到底部
  // 避免某些情况下 scroll-into-view 不触发的问题
  // #ifdef H5
  try {
    nextTick(() => {
      const anchor = document.getElementById('chat-bottom-anchor')
      if (anchor && typeof anchor.scrollIntoView === 'function') {
        anchor.scrollIntoView({ behavior: 'smooth', block: 'end' })
        return
      }

      const container = document.querySelector('.message-list')
      if (container) {
        container.scrollTop = container.scrollHeight
        return
      }
    })
  } catch (e) {
    console.warn('H5 scrollToBottom fallback error:', e)
  }
  // #endif

  // 非 H5 端：使用固定锚点 + scroll-into-view
  nextTick(() => {
    // 先重置，再设置真正的目标 id，强制触发 scroll-into-view
    scrollTarget.value = ''
    nextTick(() => {
      scrollTarget.value = 'chat-bottom-anchor'
    })
  })
}

// 无论是刷新页面加载历史消息，还是重新进入页面（Pinia 中已有消息），
// 只要“非历史追加场景”下消息数量增加，就自动滚动到底部，确保始终看到最新一条。
// 注意：在上滑加载历史记录时（append=true），不应强制滚到底部，以免打断用户查看旧消息。
watch(
  () => messages.value.length,
  (newLen, oldLen) => {
    // 没有消息，无需滚动
    if (!newLen) return

    // 正在加载历史记录（上滑加载更多）时，不自动滚动到底部
    if (loadingHistory.value) return

    // 只有在消息条数“增加”时才自动滚动；减少或相等都忽略
    if (newLen <= oldLen) return

    scrollToBottom()
    setTimeout(() => {
      scrollToBottom()
    }, 300)
  }
)

const escapeHtml = (unsafe) => {
  return String(unsafe)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

// 将后端可能返回的富文本HTML（如 <strong style="...">）归一化为“纯文本 + 轻量Markdown标记”。
// 目的：避免在不同端 rich-text 对复杂HTML/内联样式解析不一致，导致标签被当作文本显示。
const decodeHtmlEntities = (s) => {
  if (!s) return ''
  return String(s)
    .replace(/&nbsp;/gi, ' ')
    .replace(/&quot;/gi, '"')
    .replace(/&#039;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&amp;/gi, '&')
}

const normalizeIncomingContent = (content) => {
  if (!content) return ''
  let s = String(content)

  // 先解一次实体，防止出现 &lt;strong&gt; 这种“二次转义”的内容
  s = decodeHtmlEntities(s)

  // 换行与块级分隔
  s = s
    .replace(/<\s*br\s*\/?\s*>/gi, '\n')
    .replace(/<\/\s*(p|div|section|article)\s*>/gi, '\n')

  // 列表：尽量转成 markdown 列表，保持语义
  s = s
    .replace(/<\s*li[^>]*>/gi, '\n- ')
    .replace(/<\/\s*li\s*>/gi, '')
    .replace(/<\/\s*(ul|ol)\s*>/gi, '\n')

  // 强调：把 HTML strong/em 转回 markdown 标记
  // 注意：这里不尝试保留 style，只保留语义
  s = s
    .replace(/<\s*(strong|b)[^>]*>/gi, '**')
    .replace(/<\/\s*(strong|b)\s*>/gi, '**')
    .replace(/<\s*(em|i)[^>]*>/gi, '*')
    .replace(/<\/\s*(em|i)\s*>/gi, '*')

  // 移除剩余HTML标签（包括 <p ...>、<span ...> 等）
  s = s.replace(/<[^>]+>/g, '')

  // 清理多余空白/空行
  s = s
    .replace(/\r\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

  return s
}

// 轻量 Markdown 转 rich-text nodes（对象结构），避免不同端对 HTML 字符串解析不一致导致标签被当作文本展示。
const formatMarkdown = (content) => {
  if (!content) return []

  // 先把后端HTML归一化，避免标签被 escape 后直接展示出来
  const src = normalizeIncomingContent(content)

  const textNode = (text) => ({ type: 'text', text: String(text ?? '') })
  const el = (name, attrs = {}, children = []) => ({ name, attrs, children })

  const parseInline = (text, depth = 0) => {
    // 防止递归过深
    if (depth > 4) return [textNode(text)]
    const s = String(text ?? '')
    const out = []
    let i = 0

    const pushText = (t) => {
      if (!t) return
      out.push(textNode(t))
    }

    const findNext = (needle, from) => s.indexOf(needle, from)

    while (i < s.length) {
      // inline code: `code`
      if (s[i] === '`') {
        const j = findNext('`', i + 1)
        if (j !== -1) {
          const code = s.slice(i + 1, j)
          out.push(el('code', {}, [textNode(code)]))
          i = j + 1
          continue
        }
      }

      // link: [text](url)
      if (s[i] === '[') {
        const closeBracket = findNext('](', i + 1)
        if (closeBracket !== -1) {
          const endParen = findNext(')', closeBracket + 2)
          if (endParen !== -1) {
            const label = s.slice(i + 1, closeBracket)
            const url = s.slice(closeBracket + 2, endParen)
            out.push(el('a', { href: url }, [textNode(label)]))
            i = endParen + 1
            continue
          }
        }
      }

      // bold: **text**
      if (s.startsWith('**', i)) {
        const j = findNext('**', i + 2)
        if (j !== -1) {
          const inner = s.slice(i + 2, j)
          out.push(el('strong', {}, parseInline(inner, depth + 1)))
          i = j + 2
          continue
        }
      }

      // italic: *text*
      if (s[i] === '*') {
        const j = findNext('*', i + 1)
        // 避免把 ** 的第二个 * 当作 italic
        if (j !== -1 && s[i + 1] !== '*') {
          const inner = s.slice(i + 1, j)
          out.push(el('em', {}, parseInline(inner, depth + 1)))
          i = j + 1
          continue
        }
      }

      // plain text chunk
      const nextSpecialCandidates = [
        s.indexOf('`', i),
        s.indexOf('[', i),
        s.indexOf('*', i)
      ].filter(idx => idx !== -1)
      const nextSpecial = nextSpecialCandidates.length ? Math.min(...nextSpecialCandidates) : -1
      if (nextSpecial === -1) {
        pushText(s.slice(i))
        break
      } else if (nextSpecial > i) {
        pushText(s.slice(i, nextSpecial))
        i = nextSpecial
      } else {
        // 当前字符是特殊字符但未命中任何规则，按普通字符输出
        pushText(s[i])
        i += 1
      }
    }

    return out
  }

  const nodes = []
  let listMode = null // 'ul' | 'ol' | null
  let listItems = []  // array<children[]>

  const flushList = () => {
    if (!listMode) return
    const listChildren = listItems.map((children) => el('li', {}, children))
    nodes.push(el(listMode, {}, listChildren))
    listMode = null
    listItems = []
  }

  const lines = src.split('\n')

  for (const rawLine of lines) {
    const line = String(rawLine ?? '').trimEnd()

    // 空行：作为段落分隔
    if (!line.trim()) {
      flushList()
      nodes.push(el('br'))
      continue
    }

    // hr
    if (/^\s*---\s*$/.test(line)) {
      flushList()
      nodes.push(el('hr'))
      continue
    }

    // blockquote
    const bq = line.match(/^\s*>\s?(.*)$/)
    if (bq) {
      flushList()
      nodes.push(el('blockquote', {}, parseInline(bq[1])))
      continue
    }

    // headings: 用 p + strong 代替 h1/h2/h3，兼容更多端
    const h = line.match(/^(#{1,3})\s+(.*)$/)
    if (h) {
      flushList()
      nodes.push(el('p', {}, [el('strong', {}, parseInline(h[2]))]))
      continue
    }

    // unordered list
    const ul = line.match(/^\s*[-*]\s+(.*)$/)
    if (ul) {
      if (listMode && listMode !== 'ul') flushList()
      listMode = 'ul'
      listItems.push(parseInline(ul[1]))
      continue
    }

    // ordered list
    const ol = line.match(/^\s*\d+\.\s+(.*)$/)
    if (ol) {
      if (listMode && listMode !== 'ol') flushList()
      listMode = 'ol'
      listItems.push(parseInline(ol[1]))
      continue
    }

    // normal paragraph
    flushList()
    nodes.push(el('p', {}, parseInline(line)))
  }

  flushList()
  return nodes
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return ''
  const y = date.getFullYear()
  const mo = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${mo}-${d} ${h}:${m}`
}

// ========== TTS 播放 ==========
const playVoice = async (msg) => {
  if (playingMsgId.value === msg.id) {
    stopAudio()
    return
  }

  try {
    playingMsgId.value = msg.id
    const res = await ttsApi.textToSpeech({
      text: msg.content,
      voice_id: currentRobot.value.voiceId,
      speed: uni.getStorageSync('robotSpeed') || 1.0,
      use_cache: true
    })

    if (res.data && res.data.audio_url) {
      audioContext = uni.createInnerAudioContext()
      audioContext.src = res.data.audio_url
      audioContext.onEnded(() => { playingMsgId.value = null })
      audioContext.onError(() => {
        playingMsgId.value = null
        uni.showToast({ title: '播放失败', icon: 'none' })
      })
      audioContext.play()
    }
  } catch (e) {
    playingMsgId.value = null
    uni.showToast({ title: '语音生成失败', icon: 'none' })
  }
}

const stopAudio = () => {
  if (audioContext) {
    audioContext.stop()
    audioContext.destroy()
    audioContext = null
  }
  playingMsgId.value = null
}

const toggleTTS = () => {
  chatStore.toggleTTS()
  uni.showToast({
    title: ttsEnabled.value ? '已开启语音播报' : '已关闭语音播报',
    icon: 'none',
    duration: 1500
  })
}

// ========== 录音 UI（暂不真正录音） ==========
const toggleVoiceRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  recordingTime.value = 0
  recordingTimer.value = setInterval(() => {
    recordingTime.value += 1
  }, 1000)
}

const stopRecording = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
  isRecording.value = false
  recordingTime.value = 0
  uni.showToast({ title: '语音功能开发中', icon: 'none' })
}

const cancelRecording = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
  isRecording.value = false
  recordingTime.value = 0
}

// ========== 个人中心 & 机器人 & 打卡 UI ==========
const toggleProfileDrawer = () => {
  showProfile.value = !showProfile.value
}

const handleLogout = () => {
  showProfile.value = false
  userStore.logout()
}

const showRobotSelector = () => {
  showRobotModal.value = true
}

const hideRobotSelector = () => {
  showRobotModal.value = false
}

const selectRobot = (robot) => {
  currentRobot.value = robot
  uni.setStorageSync('selectedRobot', robot.id)
  uni.showToast({ title: `已切换到${robot.name}`, icon: 'success', duration: 1500 })
}

const showCheckinCalendar = async () => {
  await loadCheckinRecords()
  showCalendar.value = true
}

const goToSpecialistScene = (sceneId) => {
  // 直接跳转到对应功能页面
  const routes = {
    report: '/pages/chat/report-analysis',        // 报告解读 -> 拍照上传分析
    drug: '/pages/chat/medicine-box',             // 药品管理 -> OCR识别药盒
    diary: '/pages/chat/health-diary',            // 健康日志 -> 语音/文字记录
    knowledge: '/pages/chat/quiz-history'         // 知识问答 -> 糖糖问答记录
  }
  
  const url = routes[sceneId]
  if (url) {
    uni.navigateTo({ url })
  }
}

const hideCheckinCalendar = () => {
  showCalendar.value = false
}

const quickCheckin = () => {
  showCheckinForm.value = true
}

const hideCheckinForm = () => {
  showCheckinForm.value = false
}

const submitCheckin = async ({ glucose_status, feeling_text }) => {
  try {
    // 点击“确认打卡”后立即关闭弹窗，不等待请求返回，提升交互流畅度
    showCheckinForm.value = false

    const now = new Date()
    const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

    await checkinApi.submitCheckin({
      checkin_type: 'blood_glucose',
      checkin_value: `日常打卡 - ${timeStr}`,
      glucose_status,
      feeling_text
    })

    uni.showToast({ title: '打卡成功', icon: 'success' })
    await loadCheckinRecords()
    await loadTodayCheckinCount()
  } catch (e) {
    // 如果是 400，提示“今天已经打卡过了”这类业务文案，并让小助手在对话中回复你给的那句话
    if (e && e.statusCode === 400) {
      const msg =
        '您今天已经打卡过了！继续保持哦 💪 每种类型每天只能打卡一次~'
      // 在聊天窗口中追加一条小助手消息
      chatStore.addMessage({
        role: 'assistant',
        content: msg
      })
      scrollToBottom()

      // 视为“打卡已完成”，关闭打卡面板
      showCheckinForm.value = false
      uni.showToast({ title: '今天已打卡', icon: 'none' })
    } else {
      uni.showToast({ title: '打卡失败，请重试', icon: 'none' })
    }
  }
}

const syncCheckins = async () => {
  // 这里预留离线同步逻辑，目前直接重新拉取
  await loadCheckinRecords()
  uni.showToast({ title: '已同步最新打卡记录', icon: 'success' })
}

// 从个人中心点击“打卡记录”时触发：关闭抽屉并打开日历弹窗
const handleDrawerCheckin = async () => {
  showProfile.value = false
  await loadCheckinRecords()
  showCalendar.value = true
}

const loadCheckinRecords = async () => {
  try {
    const res = await checkinApi.getCheckinRecords()
    if (Array.isArray(res.data)) {
      checkinRecords.value = res.data
    }
  } catch (e) {
    console.error('获取打卡记录失败:', e)
  }
}

const loadTodayCheckinCount = async () => {
  try {
    const res = await checkinApi.getCheckinRecords()
    if (Array.isArray(res.data)) {
      const today = new Date().toDateString()
      todayCheckinCount.value = res.data.filter(r => {
        const d = new Date(r.checkin_time).toDateString()
        return d === today
      }).length
    }
  } catch (e) {
    console.error('获取打卡次数失败:', e)
  }
}
</script>

<style scoped>
/* 引入 Font Awesome，使移动端底部按钮图标与 H5 一致 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  /* 默认背景 - 青少年/家长模式 */
  background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 50%, #faf5ff 100%);
  padding-top: calc(env(safe-area-inset-top) + 120rpx);
}

/* 儿童模式背景 */
.chat-page.child-mode {
  background: linear-gradient(180deg, #FFF8E1 0%, #FFFEF7 30%, #FFF5E6 100%);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  /* 默认样式 - 青少年/家长模式 */
  background: #ffffff;
  box-shadow: 0 4rpx 20rpx rgba(150, 159, 255, 0.1);
  position: fixed;
  top: env(safe-area-inset-top);
  left: 0;
  right: 0;
  z-index: 100;
}

/* 儿童模式头部 */
.child-mode .chat-header {
  padding: 16rpx 32rpx;
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.header-left .user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
}

.header-center {
  flex: 1;
  margin: 0 10rpx 0 137rpx;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.robot-avatar-mini {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
}

.chat-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.robot-switch-icon {
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  margin-left: 8rpx;
}

.icon-text {
  font-size: 20rpx;
  color: #6b7280;
}

.online-status {
  display: flex;
  align-items: center;
  margin-top: 8rpx;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  background: #10b981;
  border-radius: 50%;
  margin-right: 8rpx;
}

.status-text {
  font-size: 24rpx;
  color: #10b981;
}

.header-right {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  background: rgba(246, 211, 135, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.2);
}

.calendar-icon {
  width: 50rpx;
  height: 50rpx;
}

.checkin-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  background: #ef4444;
  color: #ffffff;
  font-size: 20rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.message-list {
  flex: 1;
  padding: 16rpx 24rpx 20rpx;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 快捷入口按钮 */
.shortcuts-bar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 24rpx 16rpx;
  margin-bottom: 16rpx;
  background: transparent;
}

.shortcut-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 8rpx;
  background: transparent;
  transition: all 0.3s;
}

.shortcut-item:active {
  transform: scale(0.95);
  opacity: 0.8;
}

.shortcut-divider {
  width: 2rpx;
  height: 60rpx;
  background: #D2691E;
}

.shortcut-icon {
  width: 64rpx;
  height: 64rpx;
}

.shortcut-name {
  font-size: 22rpx;
  color: #602F27;
  text-align: center;
  font-weight: 500;
}

/* 青少年/家长模式 - 专科场景快捷入口 */
.specialist-shortcuts {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.shortcuts-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 16rpx;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.shortcut-item-default {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 8rpx;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10rpx);
  border-radius: 16rpx;
  transition: all 0.3s;
}

.shortcut-item-default:active {
  transform: scale(0.95);
  background: rgba(255, 255, 255, 0.3);
}

.shortcut-icon-emoji {
  font-size: 48rpx;
}

.shortcut-name-default {
  font-size: 22rpx;
  color: white;
  text-align: center;
}

/* 糖糖问答卡片 - 默认样式（青少年/家长模式） */
.daily-question-card {
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
  border-radius: 32rpx;
  padding: 40rpx 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(59, 130, 246, 0.15);
}

/* 儿童模式糖糖问答卡片 */
.child-mode .daily-question-card {
  background: linear-gradient(135deg, #FFF8E7 0%, #F5E6D3 100%);
  box-shadow: 0 8rpx 32rpx rgba(203, 142, 84, 0.15);
  border: 2rpx solid #E3C7A4;
}

.question-header {
  text-align: center;
  margin-bottom: 32rpx;
}

.question-icon {
  font-size: 64rpx;
  display: block;
  margin-bottom: 12rpx;
}

/* 默认样式 - 青少年/家长模式 */
.question-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #1E40AF;
  display: block;
  margin-bottom: 8rpx;
}

.question-badge {
  display: inline-block;
  padding: 8rpx 20rpx;
  background: rgba(255, 255, 255, 0.8);
  color: #1E40AF;
  font-size: 24rpx;
  border-radius: 16rpx;
  font-weight: 600;
}

.question-text {
  display: block;
  font-size: 32rpx;
  color: #1F2937;
  line-height: 1.8;
  margin-bottom: 32rpx;
  padding: 32rpx;
  background: white;
  border-radius: 24rpx;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

/* 儿童模式样式 */
.child-mode .question-title {
  color: #8B4513;
}

.child-mode .question-badge {
  background: rgba(246, 211, 135, 0.8);
  color: #602F27;
  border: 1rpx solid #E3C7A4;
}

.child-mode .question-text {
  color: #602F27;
  background: #FFFEF7;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.1);
  border: 1rpx solid #E3C7A4;
}

/* 儿童模式 - 每日问答弹窗 */
.question-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.question-popup-modal {
  width: 85%;
  max-width: 600rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F5E6D3 100%);
  border-radius: 32rpx;
  padding: 40rpx 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(203, 142, 84, 0.3);
  border: 2rpx solid #E3C7A4;
}

.question-popup-modal .question-header {
  text-align: center;
  margin-bottom: 32rpx;
}

.question-popup-modal .question-icon {
  font-size: 64rpx;
  display: block;
  margin-bottom: 12rpx;
}

.question-popup-modal .question-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #8B4513;
  display: block;
  margin-bottom: 8rpx;
}

.question-popup-modal .question-badge {
  display: inline-block;
  padding: 8rpx 20rpx;
  background: rgba(246, 211, 135, 0.8);
  color: #602F27;
  font-size: 24rpx;
  border-radius: 16rpx;
  font-weight: 600;
  border: 1rpx solid #E3C7A4;
}

.question-popup-modal .question-text {
  display: block;
  font-size: 32rpx;
  color: #602F27;
  line-height: 1.8;
  margin-bottom: 32rpx;
  padding: 32rpx;
  background: #FFFEF7;
  border-radius: 24rpx;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.1);
  border: 1rpx solid #E3C7A4;
}

.question-popup-modal .answer-buttons {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 24rpx;
}

.answer-btn {
  height: 88rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: bold;
  box-shadow: 0 6rpx 18rpx rgba(0, 0, 0, 0.1);
}

.true-btn {
  background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
  color: white;
}

.false-btn {
  background: linear-gradient(135deg, #F87171 0%, #EF4444 100%);
  color: white;
}

/* 儿童模式答题按钮 */
.child-mode .answer-btn {
  border-radius: 30rpx;
  height: 88rpx;
  box-shadow: none;
  font-size: 32rpx;
  font-weight: bold;
  transform: scale(1);
  transition: transform 0.2s;
}

.child-mode .answer-btn:active {
  transform: scale(0.98);
}

.child-mode .true-btn {
  background: #AED581;
  color: #FFFFFF;
  border: 2rpx solid #8BC34A;
  font-size: 32rpx;
  font-weight: bold;
}

.child-mode .false-btn {
  background: #F5D76E;
  color: #8A6D3B;
  border: none;
}

.answer-buttons {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.answer-btn {
  width: 100%;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.12);
}

.answer-btn:active {
  transform: scale(0.97);
}

/* 默认按钮样式 - 青少年/家长模式 */
.true-btn {
  background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
  color: white;
}

.false-btn {
  background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%);
  color: white;
}

/* 儿童模式按钮样式 */
.child-mode .true-btn {
  background: linear-gradient(135deg, #30BF78 0%, #22A366 100%);
}

.child-mode .false-btn {
  background: linear-gradient(135deg, #F6D387 0%, #D2691E 100%);
}

.answer-result {
  margin-top: 24rpx;
}

.stats-bar {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.stat-label {
  width: 80rpx;
  font-size: 26rpx;
  color: #6B7280;
  font-weight: 500;
}

.stat-progress {
  flex: 1;
  height: 32rpx;
  background: #F3F4F6;
  border-radius: 16rpx;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.true-fill {
  background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

.false-fill {
  background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
}

.stat-percent {
  width: 80rpx;
  text-align: right;
  font-size: 26rpx;
  font-weight: bold;
  color: #374151;
}

.correct-answer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  background: white;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.answer-label {
  font-size: 28rpx;
  color: #6B7280;
  font-weight: 500;
}

.answer-value {
  font-size: 34rpx;
  font-weight: bold;
}

.correct-true {
  color: #10B981;
}

.correct-false {
  color: #EF4444;
}

.explanation {
  padding: 32rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24rpx;
  position: relative;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.explanation::before {
  content: '💡';
  font-size: 40rpx;
  position: absolute;
  top: 24rpx;
  left: 24rpx;
}

.explanation-text {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
  padding-left: 60rpx;
}

.message-item {
  margin-bottom: 24rpx;
  display: flex;
  width: 100%;
}

.message-item-ai {
  justify-content: flex-start;
}

.message-item-user {
  justify-content: flex-end;
}

.message-ai {
  display: flex;
}

.ai-avatar,
.typing-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
  margin-right: 16rpx;
}

.message-content {
  max-width: 80%;
}

.message-content-user {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: 80%;
}

.message-bubble {
  position: relative;
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.bubble-ai {
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.05);
  border-radius: 36rpx 36rpx 36rpx 8rpx; /* 对齐H5：18px 18px 18px 4px */
}

.message-user {
  display: flex;
  align-items: flex-start;
  flex-direction: row-reverse; /* 用户头像在右侧 */
  margin-right: 30rpx;
  gap: 16rpx;
}

/* 默认用户消息气泡 - 青少年/家长模式 */
.message-user .message-bubble {
  background: linear-gradient(135deg, #969fff 0%, #5147ff 100%);
  color: #ffffff;
  margin-left: auto;
  border-radius: 36rpx 36rpx 8rpx 36rpx;
}

/* 儿童模式用户消息 */
.child-mode .message-user {
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
}

.child-mode .message-user .message-bubble {
  background: #F6CD75;
  color: #602F27;
  border: 3rpx solid #E5BC64;
  border-radius: 28rpx 28rpx 8rpx 28rpx;
  box-shadow: 0 4rpx 0 #D4AB53;
  padding: 24rpx 28rpx;
}

.child-mode .message-user .message-text {
  color: #602F27;
  font-weight: 500;
}

.child-mode .message-user .message-time {
  color: #8B5A3C;
}

.message-text {
  font-size: 28rpx;
  line-height: 1.6;
}

.markdown-content {
  line-height: 1.8;
  color: #374151;
}

.bubble-user .message-text,
.bubble-user .markdown-content {
  color: #ffffff;
}

.message-footer {
  margin-top: 12rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.voice-play-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eff6ff;
}

.message-time {
  font-size: 22rpx;
  color: #9ca3af;
  align-self: flex-end;
}

.message-time-ai {
  position: static;
}

.message-time-user {
  position: static;
  color: rgba(255, 255, 255, 0.85);
}

.user-chat-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
}

.typing-indicator {
  display: flex;
  align-items: center;
  margin-top: 8rpx;
}

.typing-content {
  margin-left: 16rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 16rpx 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.05);
}

.typing-dots {
  display: flex;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #9ca3af;
  animation: blink 1.5s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.typing-text {
  font-size: 24rpx;
  color: #6b7280;
}

.input-area {
  /* 固定在底部，为 TabBar 留出空间 */
  position: fixed;
  bottom: 90rpx;
  left: 0;
  right: 0;
  margin-top: 10px;
  background-color: transparent;
  z-index: 50;
}

.quick-actions {
  padding: 0 0 12rpx;
  display: flex;
  justify-content: flex-start;
}

/* 默认快捷打卡按钮 - 青少年/家长模式 */
.quick-checkin-btn {
  min-width: 220rpx;
  max-width: 340rpx;
  height: 66rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 30rpx rgba(150, 159, 255, 0.3);
}

/* 儿童模式快捷打卡按钮 */
.child-mode .quick-checkin-btn {
  background: #F6D387;
  color: #602F27;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5A874;
}

.btn-icon {
  font-size: 32rpx;
  margin-right: 4rpx;
}

.checkin-icon {
  width: 36rpx;
  height: 36rpx;
  margin-right: 8rpx;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 15rpx;
  margin-top: 4rpx;
  padding: 15rpx 24rpx;
  background-color: #ffffff;
  width: 100%;
  box-sizing: border-box;
}

.input-icons {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.voice-btn,
.tts-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: 999rpx;
  /* H5：语音按钮 bg-gray-100，TTS 默认 bg-gray-300，这里先用较浅底色，下面再单独覆盖 TTS */
  background: #f3f4f6; /* 等效 bg-gray-100 */
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 18rpx rgba(15, 23, 42, 0.08);
}

.voice-btn.recording {
  background: #fee2e2;
}

/* 默认TTS激活状态 - 青少年/家长模式 */
.tts-btn.active {
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
}

/* 儿童模式TTS激活状态 */
.child-mode .tts-btn.active {
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
}

/* TTS 默认关闭态：略深的灰色，接近 H5 的 bg-gray-300 效果 */
.tts-btn {
  background: #e5e7eb;
}

.icon {
  font-size: 34rpx;
}

.voice-icon {
  font-size: 32rpx; /* 等效 text-lg */
  color: #4b5563;  /* text-gray-600 */
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.text-input {
  width: 100%;
  min-height: 50rpx;
  max-height: 140rpx;
  font-size: 28rpx;
  padding: 15rpx 60rpx 15rpx 20rpx;
  background-color: #f9fafb;
  border-radius: 24rpx;
  border: 1rpx solid #e5e7eb;
  box-sizing: border-box;
}

/* 默认发送按钮 - 青少年/家长模式 */
.send-btn {
  position: absolute;
  right: 12rpx;
  top: 50%;
  transform: translateY(-50%);
  width: 56rpx;
  height: 56rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 儿童模式发送按钮 */
.child-mode .send-btn {
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
}

.send-btn.disabled {
  opacity: 0.4;
}

.recording-overlay {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.recording-modal {
  width: 520rpx;
  padding: 32rpx 32rpx 28rpx;
  background: rgba(31, 41, 55, 0.96);
  border-radius: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.recording-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 48rpx;
  background: #10b981;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  color: #ffffff;
}

.recording-time {
  font-size: 32rpx;
  color: #ffffff;
}

.recording-actions {
  display: flex;
  width: 100%;
  justify-content: space-between;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 28rpx;
  color: #ffffff;
}

.cancel-btn {
  background: #ef4444;
}

.send-btn.action-btn {
  background: #10b981;
}

.recording-hint {
  font-size: 24rpx;
  color: #e5e7eb;
}
</style>
