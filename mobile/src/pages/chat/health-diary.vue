<template>
  <view class="diary-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">健康日志</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 日期选择 -->
    <view class="date-section">
      <picker mode="date" :value="selectedDate" @change="onDateChange">
        <view class="date-picker">
          <text class="date-icon">📅</text>
          <text class="date-text">{{ formatDate(selectedDate) }}</text>
          <text class="date-arrow">▼</text>
        </view>
      </picker>
    </view>

    <!-- 输入区域 -->
    <view class="input-section">
      <view class="input-card">
        <view class="input-header">
          <text class="input-title">📝 记录今日状况</text>
          <view class="voice-btn" :class="{ recording: isRecording }" @tap="toggleVoiceInput">
            <text class="voice-icon">{{ isRecording ? '⏹️' : '🎤' }}</text>
            <text class="voice-text">{{ isRecording ? '停止' : '语音' }}</text>
          </view>
        </view>
        
        <!-- 语音录制状态 -->
        <view v-if="isRecording" class="recording-status">
          <view class="recording-wave">
            <view class="wave-bar" v-for="i in 5" :key="i"></view>
          </view>
          <text class="recording-text">正在录音，请说话...</text>
        </view>
        
        <!-- 文本输入框 -->
        <textarea 
          class="diary-input"
          v-model="diaryText"
          placeholder="描述您今天的身体状况、饮食、运动等..."
          :placeholder-style="'color: #A0522D'"
          maxlength="500"
          @input="onTextInput"
        ></textarea>
        
        <view class="input-footer">
          <text class="char-count">{{ diaryText.length }}/500</text>
        </view>
      </view>
    </view>

    <!-- AI提取的关键词标签 -->
    <view v-if="extractedTags.length > 0" class="tags-section">
      <view class="tags-header">
        <text class="tags-title">🏷️ AI识别的关键信息</text>
        <text class="tags-hint">点击可编辑或删除</text>
      </view>
      <view class="tags-list">
        <view 
          v-for="(tag, index) in extractedTags" 
          :key="index" 
          class="tag-item"
          :class="tag.type"
          @tap="editTag(index)"
        >
          <text class="tag-icon">{{ getTagIcon(tag.type) }}</text>
          <text class="tag-text">{{ tag.text }}</text>
          <view class="tag-delete" @tap.stop="deleteTag(index)">✕</view>
        </view>
      </view>
    </view>

    <!-- 手动添加标签 -->
    <view class="add-tag-section">
      <view class="add-tag-btn" @tap="showAddTagModal">
        <text class="add-icon">+</text>
        <text class="add-text">手动添加标签</text>
      </view>
    </view>

    <!-- 添加标签弹窗 -->
    <view v-if="showTagModal" class="tag-modal-overlay" @tap="closeTagModal">
      <view class="tag-modal" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingTagIndex >= 0 ? '编辑标签' : '添加标签' }}</text>
          <view class="modal-close" @tap="closeTagModal">✕</view>
        </view>
        <view class="modal-body">
          <view class="form-field">
            <text class="field-label">标签类型</text>
            <view class="type-options">
              <view 
                v-for="t in tagTypes" 
                :key="t.value"
                class="type-option"
                :class="{ active: newTag.type === t.value, [t.value]: true }"
                @tap="newTag.type = t.value"
              >
                <text>{{ t.icon }} {{ t.label }}</text>
              </view>
            </view>
          </view>
          <view class="form-field">
            <text class="field-label">标签内容</text>
            <input class="field-input" v-model="newTag.text" placeholder="如：头晕、吃了20g巧克力" />
          </view>
        </view>
        <view class="modal-footer">
          <button class="cancel-btn" @tap="closeTagModal">取消</button>
          <button class="confirm-btn" @tap="confirmTag">确定</button>
        </view>
      </view>
    </view>

    <!-- 历史记录 -->
    <view class="history-section">
      <view class="history-header">
        <text class="history-title">📋 历史记录</text>
      </view>
      <view v-if="diaryHistory.length === 0" class="empty-history">
        <text class="empty-text">暂无记录</text>
      </view>
      <view v-else class="history-list">
        <view v-for="(record, index) in diaryHistory" :key="index" class="history-item">
          <view class="history-date">{{ record.date }}</view>
          <view class="history-content">{{ record.text }}</view>
          <view class="history-tags">
            <view v-for="(tag, tIndex) in record.tags" :key="tIndex" class="mini-tag" :class="tag.type">
              {{ tag.text }}
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <button 
        class="save-btn" 
        :class="{ disabled: !canSave }"
        :disabled="!canSave"
        @tap="saveToDashboard"
      >
        <text class="save-icon">✓</text>
        <text>确认存入仪表盘</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'

const selectedDate = ref(formatDateValue(new Date()))
const diaryText = ref('')
const extractedTags = ref([])
const isRecording = ref(false)
const showTagModal = ref(false)
const editingTagIndex = ref(-1)
const diaryHistory = ref([])

const newTag = reactive({
  type: 'symptom',
  text: ''
})

const tagTypes = [
  { value: 'symptom', label: '症状', icon: '🩺' },
  { value: 'food', label: '饮食', icon: '🍽️' },
  { value: 'exercise', label: '运动', icon: '🏃' },
  { value: 'medication', label: '用药', icon: '💊' },
  { value: 'mood', label: '心情', icon: '😊' }
]

const canSave = computed(() => {
  return diaryText.value.trim().length > 0 || extractedTags.value.length > 0
})

onMounted(() => {
  // 加载历史记录
  const saved = uni.getStorageSync('healthDiaryHistory')
  if (saved) {
    diaryHistory.value = JSON.parse(saved)
  }
})

// 监听文本变化，自动提取关键词
watch(diaryText, (newText) => {
  if (newText.length > 5) {
    extractKeywords(newText)
  }
})

function formatDateValue(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${date.getMonth() + 1}月${date.getDate()}日 ${weekDays[date.getDay()]}`
}

const goBack = () => {
  uni.navigateBack()
}

const onDateChange = (e) => {
  selectedDate.value = e.detail.value
}

const toggleVoiceInput = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  
  // 模拟语音识别流式输出
  const mockText = '今天早上起来感觉有点头晕，血糖测了一下是6.2，中午吃了20g巧克力，下午散步了30分钟'
  let currentIndex = 0
  
  const streamInterval = setInterval(() => {
    if (currentIndex < mockText.length && isRecording.value) {
      diaryText.value += mockText[currentIndex]
      currentIndex++
    } else {
      clearInterval(streamInterval)
      if (isRecording.value) {
        isRecording.value = false
      }
    }
  }, 80)
}

const stopRecording = () => {
  isRecording.value = false
}

const onTextInput = () => {
  // 文本输入时的处理
}

// AI关键词提取（模拟）
const extractKeywords = (text) => {
  const keywords = []
  
  // 症状关键词
  const symptoms = ['头晕', '头痛', '恶心', '乏力', '心慌', '出汗', '手抖', '视物模糊']
  symptoms.forEach(s => {
    if (text.includes(s) && !extractedTags.value.find(t => t.text === s)) {
      keywords.push({ type: 'symptom', text: s })
    }
  })
  
  // 饮食关键词（匹配数量+食物）
  const foodPattern = /(\d+[g克]?\s*[巧克力|糖果|饼干|米饭|面包|水果|蛋糕]+)/g
  const foodMatches = text.match(foodPattern)
  if (foodMatches) {
    foodMatches.forEach(f => {
      if (!extractedTags.value.find(t => t.text === f)) {
        keywords.push({ type: 'food', text: f })
      }
    })
  }
  
  // 运动关键词
  const exercisePattern = /(散步|跑步|游泳|骑车|健身|瑜伽|太极).*?(\d+分钟|\d+小时)?/g
  const exerciseMatches = text.match(exercisePattern)
  if (exerciseMatches) {
    exerciseMatches.forEach(e => {
      if (!extractedTags.value.find(t => t.text === e)) {
        keywords.push({ type: 'exercise', text: e })
      }
    })
  }
  
  // 血糖数值
  const glucosePattern = /血糖.*?(\d+\.?\d*)/g
  const glucoseMatch = text.match(glucosePattern)
  if (glucoseMatch) {
    glucoseMatch.forEach(g => {
      if (!extractedTags.value.find(t => t.text.includes('血糖'))) {
        keywords.push({ type: 'symptom', text: g })
      }
    })
  }
  
  // 合并新提取的关键词
  if (keywords.length > 0) {
    extractedTags.value = [...extractedTags.value, ...keywords]
  }
}

const getTagIcon = (type) => {
  const icons = {
    symptom: '🩺',
    food: '🍽️',
    exercise: '🏃',
    medication: '💊',
    mood: '😊'
  }
  return icons[type] || '🏷️'
}

const editTag = (index) => {
  editingTagIndex.value = index
  newTag.type = extractedTags.value[index].type
  newTag.text = extractedTags.value[index].text
  showTagModal.value = true
}

const deleteTag = (index) => {
  extractedTags.value.splice(index, 1)
}

const showAddTagModal = () => {
  editingTagIndex.value = -1
  newTag.type = 'symptom'
  newTag.text = ''
  showTagModal.value = true
}

const closeTagModal = () => {
  showTagModal.value = false
  editingTagIndex.value = -1
}

const confirmTag = () => {
  if (!newTag.text.trim()) {
    uni.showToast({ title: '请输入标签内容', icon: 'none' })
    return
  }
  
  if (editingTagIndex.value >= 0) {
    extractedTags.value[editingTagIndex.value] = { ...newTag }
  } else {
    extractedTags.value.push({ ...newTag })
  }
  
  closeTagModal()
}

const saveToDashboard = () => {
  if (!canSave.value) return
  
  const record = {
    date: selectedDate.value,
    text: diaryText.value,
    tags: [...extractedTags.value],
    timestamp: Date.now()
  }
  
  // 保存到历史记录
  diaryHistory.value.unshift(record)
  uni.setStorageSync('healthDiaryHistory', JSON.stringify(diaryHistory.value))
  
  // 同步到仪表盘时间轴（存储到全局状态）
  const timelineEvents = uni.getStorageSync('dashboardTimeline') || '[]'
  const events = JSON.parse(timelineEvents)
  events.unshift({
    id: Date.now(),
    date: selectedDate.value,
    type: 'diary',
    title: '健康日志',
    content: diaryText.value,
    tags: extractedTags.value
  })
  uni.setStorageSync('dashboardTimeline', JSON.stringify(events))
  
  uni.showToast({ title: '已存入仪表盘', icon: 'success' })
  
  // 清空当前输入
  diaryText.value = ''
  extractedTags.value = []
}
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E1 0%, #FFFEF7 30%, #FFF5E6 100%);
  padding-bottom: 140rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 20rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
}

.nav-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 48rpx;
  color: #8B4513;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #8B4513;
}

.nav-placeholder {
  width: 60rpx;
}

/* 日期选择 */
.date-section {
  padding: 24rpx 32rpx;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #FFFEF7;
  padding: 20rpx 28rpx;
  border-radius: 16rpx;
  border: 1rpx solid #E3C7A4;
}

.date-icon {
  font-size: 32rpx;
}

.date-text {
  flex: 1;
  font-size: 30rpx;
  color: #8B4513;
  font-weight: 500;
}

.date-arrow {
  font-size: 20rpx;
  color: #A0522D;
}

/* 输入区域 */
.input-section {
  padding: 0 32rpx;
}

.input-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 28rpx;
  border: 1rpx solid #E3C7A4;
}

.input-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.input-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #8B4513;
}

.voice-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  border-radius: 32rpx;
}

.voice-btn.recording {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.voice-icon {
  font-size: 28rpx;
}

.voice-text {
  font-size: 24rpx;
  color: white;
}

/* 录音状态 */
.recording-status {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #FEF3C7;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
}

.recording-wave {
  display: flex;
  align-items: center;
  gap: 4rpx;
  height: 40rpx;
}

.wave-bar {
  width: 6rpx;
  background: #D97706;
  border-radius: 3rpx;
  animation: wave 0.5s ease-in-out infinite alternate;
}

.wave-bar:nth-child(1) { height: 20rpx; animation-delay: 0s; }
.wave-bar:nth-child(2) { height: 30rpx; animation-delay: 0.1s; }
.wave-bar:nth-child(3) { height: 40rpx; animation-delay: 0.2s; }
.wave-bar:nth-child(4) { height: 30rpx; animation-delay: 0.3s; }
.wave-bar:nth-child(5) { height: 20rpx; animation-delay: 0.4s; }

@keyframes wave {
  from { height: 10rpx; }
  to { height: 40rpx; }
}

.recording-text {
  font-size: 26rpx;
  color: #92400E;
}

.diary-input {
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  background: #FFF8E7;
  border: 1rpx solid #E3C7A4;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #602F27;
  line-height: 1.6;
  box-sizing: border-box;
}

.input-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12rpx;
}

.char-count {
  font-size: 24rpx;
  color: #A0522D;
}

/* 标签区域 */
.tags-section {
  padding: 24rpx 32rpx;
}

.tags-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.tags-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #8B4513;
}

.tags-hint {
  font-size: 22rpx;
  color: #A0522D;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  border-radius: 32rpx;
  background: #FFF8E7;
  border: 1rpx solid #E3C7A4;
}

.tag-item.symptom {
  background: #FEE2E2;
  border-color: #FECACA;
}

.tag-item.food {
  background: #FEF3C7;
  border-color: #FDE68A;
}

.tag-item.exercise {
  background: #D1FAE5;
  border-color: #A7F3D0;
}

.tag-item.medication {
  background: #DBEAFE;
  border-color: #BFDBFE;
}

.tag-item.mood {
  background: #F3E8FF;
  border-color: #E9D5FF;
}

.tag-icon {
  font-size: 24rpx;
}

.tag-text {
  font-size: 26rpx;
  color: #602F27;
}

.tag-delete {
  font-size: 20rpx;
  color: #9CA3AF;
  padding: 4rpx;
}

/* 添加标签 */
.add-tag-section {
  padding: 0 32rpx;
}

.add-tag-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 20rpx;
  background: transparent;
  border: 2rpx dashed #D2691E;
  border-radius: 16rpx;
}

.add-icon {
  font-size: 32rpx;
  color: #D2691E;
}

.add-text {
  font-size: 26rpx;
  color: #D2691E;
}

/* 标签弹窗 */
.tag-modal-overlay {
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
  padding: 40rpx;
}

.tag-modal {
  width: 100%;
  max-width: 600rpx;
  background: #FFFEF7;
  border-radius: 32rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx;
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: white;
}

.modal-close {
  font-size: 32rpx;
  color: white;
  padding: 8rpx;
}

.modal-body {
  padding: 32rpx;
}

.form-field {
  margin-bottom: 24rpx;
}

.field-label {
  display: block;
  font-size: 26rpx;
  color: #8B4513;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.type-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.type-option {
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  background: #f3f4f6;
  color: #6b7280;
}

.type-option.active {
  color: white;
}

.type-option.active.symptom { background: #EF4444; }
.type-option.active.food { background: #F59E0B; }
.type-option.active.exercise { background: #10B981; }
.type-option.active.medication { background: #3B82F6; }
.type-option.active.mood { background: #8B5CF6; }

.field-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background: #FFF8E7;
  border: 1rpx solid #E3C7A4;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #602F27;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  gap: 24rpx;
  padding: 0 32rpx 32rpx;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.cancel-btn {
  background: #f3f4f6;
  color: #6b7280;
}

.confirm-btn {
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  color: white;
}

/* 历史记录 */
.history-section {
  padding: 24rpx 32rpx;
}

.history-header {
  margin-bottom: 16rpx;
}

.history-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #8B4513;
}

.empty-history {
  text-align: center;
  padding: 40rpx;
  background: #FFFEF7;
  border-radius: 16rpx;
  border: 1rpx solid #E3C7A4;
}

.empty-text {
  font-size: 26rpx;
  color: #A0522D;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.history-item {
  background: #FFFEF7;
  border-radius: 16rpx;
  padding: 20rpx;
  border: 1rpx solid #E3C7A4;
}

.history-date {
  font-size: 24rpx;
  color: #A0522D;
  margin-bottom: 8rpx;
}

.history-content {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.5;
  margin-bottom: 12rpx;
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.mini-tag {
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
}

.mini-tag.symptom { background: #FEE2E2; color: #DC2626; }
.mini-tag.food { background: #FEF3C7; color: #D97706; }
.mini-tag.exercise { background: #D1FAE5; color: #059669; }
.mini-tag.medication { background: #DBEAFE; color: #2563EB; }
.mini-tag.mood { background: #F3E8FF; color: #7C3AED; }

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 32rpx;
  padding-bottom: calc(env(safe-area-inset-bottom) + 20rpx);
  background: #FFFEF7;
  border-top: 1rpx solid #E3C7A4;
}

.save-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  height: 88rpx;
  background: linear-gradient(135deg, #30BF78 0%, #22A366 100%);
  color: white;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 44rpx;
  box-shadow: 0 8rpx 24rpx rgba(48, 191, 120, 0.3);
}

.save-btn.disabled {
  opacity: 0.5;
}

.save-icon {
  font-size: 32rpx;
}
</style>
