<template>
  <view class="chat-page">
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
          <text class="calendar-icon">📅</text>
        </view>
        <view v-if="todayCheckinCount > 0" class="checkin-badge">
          {{ todayCheckinCount }}
        </view>
      </view>
    </view>

    <!-- 消息列表 -->
    <scroll-view 
      class="message-list" 
      scroll-y 
      :scroll-into-view="scrollTarget"
      scroll-with-animation
      :show-scrollbar="false"
      @scrolltoupper="loadMoreHistory"
    >
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
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-area">
      <!-- 快捷打卡 -->
      <view class="quick-actions">
        <button class="quick-checkin-btn" @tap="quickCheckin">
          <text class="btn-icon">✅</text>
          <text class="btn-text">今日打卡</text>
        </button>
      </view>

      <view class="input-container">
        <!-- 语音按钮 -->
        <view 
          class="voice-btn" 
          @tap="toggleVoiceRecording"
          :class="{ 'recording': isRecording }"
        >
          <text class="icon">{{ isRecording ? '🔴' : '🎤' }}</text>
        </view>

        <!-- TTS开关 -->
        <view 
          class="tts-btn" 
          @tap="toggleTTS"
          :class="{ 'active': ttsEnabled }"
        >
          <text class="icon">{{ ttsEnabled ? '🔊' : '🔇' }}</text>
        </view>

        <!-- 输入框 -->
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
            :class="{ 'disabled': !canSend }"
          >
            <text class="icon">📤</text>
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
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useChatStore } from '@/store/chat'
import { chatApi, checkinApi, ttsApi } from '@/api'
import ProfileDrawer from '@/components/ProfileDrawer.vue'
import RobotSelector from '@/components/RobotSelector.vue'
import CheckinCalendar from '@/components/CheckinCalendar.vue'
import CheckinForm from '@/components/CheckinForm.vue'

const userStore = useUserStore()
const chatStore = useChatStore()

// 顶部与状态
const showProfile = ref(false)
const showRobotModal = ref(false)
const showCalendar = ref(false)
const showCheckinForm = ref(false)
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

// 统一用户头像（使用提供的插画图片）
const USER_AVATAR_URL = 'https://s.coze.cn/image/es6fUICmNgw/'
const userAvatar = computed(() => USER_AVATAR_URL)

// 机器人配置（参考 smart-sugar-assistant-main，实现男女小助手区分头像）
const robots = ref([
  {
    id: 'xiaojing',
    name: '小助手1',
    voiceId: '601012',
    avatar: '/static/nansheng.png',
    description: '阳光开朗的男生助手'
  },
  {
    id: 'zhimeng',
    name: '小助手2',
    voiceId: '101015',
    avatar: '/static/nvsheng.png',
    description: '温柔细心的女生助手'
  }
])
const currentRobot = ref(robots.value[0])

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
        // 首次加载后滚动到底部
        scrollToBottom()
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

  // 恢复选择的机器人
  const savedRobotId = uni.getStorageSync('selectedRobot')
  if (savedRobotId) {
    const robot = robots.value.find(r => r.id === savedRobotId)
    if (robot) currentRobot.value = robot
  }
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
  nextTick(() => {
    const last = messages.value[messages.value.length - 1]
    if (last) {
      scrollTarget.value = 'msg-' + last.id
    }
  })
}

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
    const now = new Date()
    const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`

    await checkinApi.submitCheckin({
      checkin_type: 'blood_glucose',
      checkin_value: `日常打卡 - ${timeStr}`,
      glucose_status,
      feeling_text
    })

    uni.showToast({ title: '打卡成功', icon: 'success' })
    showCheckinForm.value = false
    await loadCheckinRecords()
    await loadTodayCheckinCount()
  } catch (e) {
    uni.showToast({ title: '打卡失败，请重试', icon: 'none' })
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
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  /* 背景对齐 H5：bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 */
  background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 50%, #faf5ff 100%);
  /* 为固定头部预留空间：safe-area + 头部高度 */
  padding-top: calc(env(safe-area-inset-top) + 120rpx);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  background: #ffffff;
  box-shadow: 0 4rpx 20rpx rgba(150, 159, 255, 0.1);
  position: fixed;
  top: env(safe-area-inset-top);
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left .user-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
}

.header-center {
  flex: 1;
  margin: 0 24rpx;
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
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(148, 163, 184, 0.5);
}

.calendar-icon {
  font-size: 40rpx;
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
  padding: 24rpx 24rpx 160rpx; /* 额外底部内边距，避免被底部输入栏遮挡 */
  /* scroll-view 在部分端不会透出父级背景，需直接给滚动区域设置背景 */
  background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 50%, #faf5ff 100%);
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
  gap: 16rpx;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, #969fff 0%, #5147ff 100%);
  color: #ffffff;
  margin-left: auto;
  border-radius: 36rpx 36rpx 8rpx 36rpx; /* 对齐H5：18px 18px 4px 18px */
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
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16rpx 24rpx 32rpx;
  background: #ffffff;
  box-shadow: 0 -4rpx 20rpx rgba(15, 23, 42, 0.05);
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  z-index: 50;
}

.quick-actions {
  margin-bottom: 16rpx;
}

.quick-checkin-btn {
  width: 260rpx;
  height: 88rpx;
  border-radius: 44rpx;
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 20rpx rgba(16, 185, 129, 0.35);
}

.btn-icon {
  font-size: 32rpx;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  margin-top: 8rpx;
}

.voice-btn,
.tts-btn {
  width: 88rpx;
  height: 88rpx;
  border-radius: 44rpx;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 18rpx rgba(15, 23, 42, 0.08);
}

.voice-btn.recording {
  background: #fee2e2;
}

.tts-btn.active {
  background: #e0f2fe;
}

.icon {
  font-size: 34rpx;
}

.input-wrapper {
  flex: 1;
  background: #f9fafb;
  border-radius: 999rpx;
  padding: 8rpx 12rpx 8rpx 24rpx;
  display: flex;
  align-items: center;
  box-shadow: inset 0 0 0 1rpx #e5e7eb;
}

.text-input {
  flex: 1;
  min-height: 68rpx;
  max-height: 160rpx;
  font-size: 28rpx;
}

.send-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, #969fff 0%, #5147ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8rpx;
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
