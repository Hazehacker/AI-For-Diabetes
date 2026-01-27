<template>
  <view class="checkin-container">
    <!-- 打卡表单 -->
    <view class="checkin-form">
      <view class="form-title">
        <text class="title-icon">✅</text>
        <text class="title-text">今日打卡</text>
      </view>

      <!-- 控糖状态 -->
      <view class="form-section">
        <text class="section-label">今天控糖状态如何？</text>
        <view class="status-options">
          <view 
            v-for="status in statusOptions" 
            :key="status.value"
            class="status-btn"
            :class="{ 'status-active': checkinForm.glucose_status === status.value }"
            @tap="selectStatus(status.value)"
          >
            <text class="status-icon">{{ status.icon }}</text>
            <text class="status-text">{{ status.label }}</text>
          </view>
        </view>
      </view>

      <!-- 感受输入 -->
      <view class="form-section">
        <text class="section-label">分享一下你的感受（可选）</text>
        <textarea 
          class="feeling-input"
          v-model="checkinForm.feeling_text"
          placeholder="今天的感觉怎么样？有什么特别的经历或心得吗..."
          maxlength="200"
        />
        <text class="char-count">{{ checkinForm.feeling_text.length }}/200</text>
      </view>

      <!-- 提交按钮 -->
      <button 
        class="submit-btn" 
        :disabled="!checkinForm.glucose_status || loading"
        @tap="submitCheckin"
      >
        <text v-if="!loading">确认打卡</text>
        <text v-else>提交中...</text>
      </button>
    </view>

    <!-- 打卡记录 -->
    <view class="records-section">
      <view class="section-header">
        <text class="section-title">打卡记录</text>
        <text class="record-count">共 {{ records.length }} 条</text>
      </view>

      <view v-if="records.length === 0" class="empty-state">
        <text class="empty-icon">📝</text>
        <text class="empty-text">暂无打卡记录</text>
      </view>

      <view v-else class="record-list">
        <view 
          v-for="record in records" 
          :key="record.id"
          class="record-item"
        >
          <view class="record-header">
            <text class="record-date">{{ formatDate(record.checkin_time) }}</text>
            <view class="record-status" :class="'status-' + record.glucose_status">
              {{ record.glucose_status }}
            </view>
          </view>
          <text v-if="record.feeling_text" class="record-feeling">
            {{ record.feeling_text }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { checkinApi } from '@/api'

const checkinForm = ref({
  checkin_type: 'blood_glucose',
  checkin_value: '',
  glucose_status: '',
  feeling_text: ''
})

const loading = ref(false)
const records = ref([])

const statusOptions = [
  { value: '一般', label: '一般', icon: '😐' },
  { value: '良好', label: '良好', icon: '😊' },
  { value: '好', label: '好', icon: '😄' }
]

onMounted(() => {
  fetchRecords()
})

const selectStatus = (status) => {
  checkinForm.value.glucose_status = status
}

const submitCheckin = async () => {
  if (!checkinForm.value.glucose_status) {
    uni.showToast({
      title: '请选择控糖状态',
      icon: 'none'
    })
    return
  }

  loading.value = true

  try {
    const now = new Date()
    const timeStr = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
    
    await checkinApi.submitCheckin({
      ...checkinForm.value,
      checkin_value: `日常打卡 - ${timeStr}`
    })

    uni.showToast({
      title: '打卡成功',
      icon: 'success'
    })

    // 重置表单
    checkinForm.value = {
      checkin_type: 'blood_glucose',
      checkin_value: '',
      glucose_status: '',
      feeling_text: ''
    }

    // 刷新记录
    fetchRecords()
  } catch (error) {
    uni.showToast({
      title: '打卡失败，请重试',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

const fetchRecords = async () => {
  try {
    const res = await checkinApi.getCheckinRecords()
    if (res.data && Array.isArray(res.data)) {
      records.value = res.data
    }
  } catch (error) {
    console.error('获取打卡记录失败:', error)
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hour}:${minute}`
}
</script>

<style scoped>
.checkin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  padding: 40rpx;
}

.checkin-form {
  background: white;
  border-radius: 32rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.15);
}

.form-title {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.title-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.title-text {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
}

.form-section {
  margin-bottom: 40rpx;
}

.section-label {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 24rpx;
  font-weight: 500;
}

.status-options {
  display: flex;
  gap: 20rpx;
}

.status-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  transition: all 0.3s;
}

.status-active {
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  border-color: #5147FF;
}

.status-icon {
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.status-text {
  font-size: 26rpx;
  color: #6b7280;
}

.status-active .status-text {
  color: white;
}

.feeling-input {
  width: 100%;
  min-height: 200rpx;
  padding: 24rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
  font-size: 28rpx;
  line-height: 1.6;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 24rpx;
  color: #9ca3af;
  margin-top: 12rpx;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #969FFF 0%, #5147FF 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 30rpx rgba(150, 159, 255, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
}

.records-section {
  background: white;
  border-radius: 32rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 40rpx rgba(150, 159, 255, 0.15);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.record-count {
  font-size: 24rpx;
  color: #9ca3af;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.record-item {
  padding: 32rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  border: 2rpx solid #e5e7eb;
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.record-date {
  font-size: 26rpx;
  color: #6b7280;
}

.record-status {
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.status-一般 {
  background: #fef3c7;
  color: #92400e;
}

.status-良好 {
  background: #dbeafe;
  color: #1e40af;
}

.status-好 {
  background: #d1fae5;
  color: #065f46;
}

.record-feeling {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.6;
}
</style>
