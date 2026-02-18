<template>
  <view class="quiz-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">知识问答</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-section">
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ quizStats.total }}</text>
          <text class="stat-label">总答题</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value correct">{{ quizStats.correct }}</text>
          <text class="stat-label">答对</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ quizStats.accuracy }}%</text>
          <text class="stat-label">正确率</text>
        </view>
      </view>
    </view>

    <!-- 历史记录列表 -->
    <view class="history-section">
      <text class="section-title">📋 糖糖问答记录</text>
      
      <view v-if="quizHistory.length === 0" class="empty-state">
        <text class="empty-icon">🍬</text>
        <text class="empty-text">暂无答题记录</text>
        <text class="empty-hint">去问答页面完成每日糖糖问答吧~</text>
      </view>
      
      <view v-else class="history-list">
        <view 
          v-for="record in quizHistory" 
          :key="record.id" 
          class="quiz-record"
          :class="{ correct: record.isCorrect, wrong: !record.isCorrect }"
          @tap="toggleRecordExpand(record.id)"
        >
          <view class="record-header">
            <view class="record-status">
              <text class="status-icon">{{ record.isCorrect ? '✓' : '✗' }}</text>
            </view>
            <view class="record-info">
              <text class="record-date">{{ formatDate(record.date) }}</text>
              <text class="record-question">{{ record.question }}</text>
            </view>
            <text class="expand-icon">{{ expandedRecords.includes(record.id) ? '▼' : '▶' }}</text>
          </view>
          
          <!-- 展开详情 -->
          <view v-if="expandedRecords.includes(record.id)" class="record-detail">
            <view class="answer-row">
              <text class="answer-label">你的答案：</text>
              <text class="answer-value" :class="record.isCorrect ? 'correct' : 'wrong'">
                {{ record.userAnswer ? '✓ 正确' : '✗ 错误' }}
              </text>
            </view>
            <view class="answer-row">
              <text class="answer-label">正确答案：</text>
              <text class="answer-value correct">
                {{ record.correctAnswer ? '✓ 正确' : '✗ 错误' }}
              </text>
            </view>
            <view class="explanation-box">
              <text class="explanation-title">💡 解析</text>
              <text class="explanation-text">{{ record.explanation }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '@/store/chat'

const chatStore = useChatStore()

// 糖糖问答历史
const quizHistory = computed(() => chatStore.quizHistory || [])
const expandedRecords = ref([])

// 答题统计
const quizStats = computed(() => {
  const history = quizHistory.value
  const total = history.length
  const correct = history.filter(r => r.isCorrect).length
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0
  return { total, correct, accuracy }
})

const goBack = () => {
  uni.navigateBack()
}

// 切换展开记录
const toggleRecordExpand = (id) => {
  const index = expandedRecords.value.indexOf(id)
  if (index >= 0) {
    expandedRecords.value.splice(index, 1)
  } else {
    expandedRecords.value.push(id)
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<style scoped>
.quiz-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E1 0%, #FFFEF7 30%, #FFF5E6 100%);
  padding-bottom: 40rpx;
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

/* 统计卡片 */
.stats-section {
  padding: 32rpx;
}

.stats-card {
  display: flex;
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 32rpx 20rpx;
  border: 1rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.1);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  color: #8B4513;
}

.stat-value.correct {
  color: #30BF78;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #A0522D;
  margin-top: 8rpx;
}

.stat-divider {
  width: 1rpx;
  background: #E3C7A4;
}

/* 历史记录 */
.history-section {
  padding: 0 32rpx;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 20rpx;
}

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
  background: #FFFEF7;
  border-radius: 24rpx;
  border: 1rpx solid #E3C7A4;
}

.empty-icon {
  display: block;
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  display: block;
  font-size: 30rpx;
  color: #8B4513;
  margin-bottom: 12rpx;
}

.empty-hint {
  display: block;
  font-size: 26rpx;
  color: #A0522D;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.quiz-record {
  background: #FFFEF7;
  border-radius: 20rpx;
  overflow: hidden;
  border: 1rpx solid #E3C7A4;
  border-left: 8rpx solid #E3C7A4;
}

.quiz-record.correct {
  border-left-color: #30BF78;
}

.quiz-record.wrong {
  border-left-color: #EF4444;
}

.record-header {
  display: flex;
  align-items: center;
  padding: 24rpx;
  gap: 16rpx;
}

.record-status {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-record.correct .record-status {
  background: #D1FAE5;
}

.quiz-record.wrong .record-status {
  background: #FEE2E2;
}

.status-icon {
  font-size: 32rpx;
  font-weight: 700;
}

.quiz-record.correct .status-icon {
  color: #30BF78;
}

.quiz-record.wrong .status-icon {
  color: #EF4444;
}

.record-info {
  flex: 1;
}

.record-date {
  display: block;
  font-size: 24rpx;
  color: #A0522D;
  margin-bottom: 6rpx;
}

.record-question {
  display: block;
  font-size: 28rpx;
  color: #602F27;
  line-height: 1.5;
}

.expand-icon {
  font-size: 22rpx;
  color: #A0522D;
}

/* 展开详情 */
.record-detail {
  padding: 0 24rpx 24rpx;
  border-top: 1rpx solid #E3C7A4;
}

.answer-row {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
}

.answer-label {
  font-size: 26rpx;
  color: #A0522D;
  width: 160rpx;
}

.answer-value {
  font-size: 28rpx;
  font-weight: 600;
}

.answer-value.correct {
  color: #30BF78;
}

.answer-value.wrong {
  color: #EF4444;
}

.explanation-box {
  margin-top: 16rpx;
  padding: 24rpx;
  background: #FFF8E7;
  border-radius: 16rpx;
  border: 1rpx solid #F6D387;
}

.explanation-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 12rpx;
}

.explanation-text {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.7;
}
</style>
