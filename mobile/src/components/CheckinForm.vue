<template>
  <view v-if="visible" class="modal-overlay" @tap="handleClose">
    <view class="modal-content" :class="{ 'child-modal': isChildMode }" @tap.stop>
      <view class="modal-header" :class="{ 'child-header': isChildMode }">
        <view class="title-wrap">
          <image class="title-icon" src="/static/ch/ch_index_finish.png" mode="aspectFit"></image>
          <text class="title" :class="{ 'child-title': isChildMode }">今日打卡</text>
        </view>
        <view class="close-btn" @tap="handleClose">
          <text class="icon">✕</text>
        </view>
      </view>

      <view class="form-content">
        <view class="form-section">
          <text class="section-label">今天控糖状态如何？</text>
          <view class="status-options">
            <view 
              v-for="status in statusOptions" 
              :key="status.value"
              class="status-btn"
              :class="{ 'active': selectedStatus === status.value, 'child-status-btn': isChildMode, 'child-active': isChildMode && selectedStatus === status.value }"
              @tap="selectStatus(status.value)"
            >
              <text class="status-icon">{{ status.icon }}</text>
              <text class="status-text" :class="{ 'child-status-text': isChildMode }">{{ status.label }}</text>
            </view>
          </view>
        </view>

        <view class="form-section">
          <text class="section-label">分享一下你的感受（可选）</text>
          <textarea 
            class="feeling-input"
            v-model="feeling"
            placeholder="今天的感觉怎么样？有什么特别的经历或心得吗..."
            maxlength="200"
          />
          <text class="char-count">{{ feeling.length }}/200</text>
        </view>

        <button 
          class="submit-btn" 
          :class="{ 'child-submit-btn': isChildMode }"
          :disabled="!selectedStatus || submitting"
          @tap="handleSubmit"
        >
          <text v-if="!submitting">确认打卡</text>
          <text v-else>提交中...</text>
        </button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch, computed, inject } from 'vue'
import { useDashboardStore } from '@/store/dashboard'

const dashboardStore = useDashboardStore()
const isChildMode = computed(() => dashboardStore.userRole === 'child_under_12')

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['close', 'submit'])

const statusOptions = [
  { value: '一般', label: '一般', icon: '😐' },
  { value: '良好', label: '良好', icon: '😊' },
  { value: '好', label: '好', icon: '😄' }
]

const selectedStatus = ref('')
const feeling = ref('')
const submitting = ref(false)

watch(() => props.visible, (val) => {
  if (val) {
    selectedStatus.value = ''
    feeling.value = ''
    submitting.value = false
  }
})

const handleClose = () => {
  emit('close')
}

const selectStatus = (status) => {
  selectedStatus.value = status
}

const handleSubmit = async () => {
  if (!selectedStatus.value) {
    uni.showToast({
      title: '请选择控糖状态',
      icon: 'none'
    })
    return
  }

  submitting.value = true

  try {
    await emit('submit', {
      glucose_status: selectedStatus.value,
      feeling_text: feeling.value
    })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  width: 100%;
  max-width: 600rpx;
  max-height: 85vh;
  background: white;
  border-radius: 32rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.title-icon {
  width: 40rpx;
  height: 40rpx;
}

.title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn .icon {
  font-size: 32rpx;
  color: #6b7280;
}

.form-content {
  padding: 32rpx;
}

.form-section {
  margin-bottom: 32rpx;
}

.section-label {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 20rpx;
  font-weight: 500;
}

.status-options {
  display: flex;
  gap: 16rpx;
}

.status-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 16rpx;
  background: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 20rpx;
}

.status-btn.active {
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

.status-btn.active .status-text {
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
  box-sizing: border-box;
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
  margin-top: 16rpx;
}

.submit-btn:disabled {
  opacity: 0.6;
}

/* 儿童模式样式 */
.child-modal {
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 8rpx 24rpx rgba(203, 142, 84, 0.2);
}

.child-header {
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  border-bottom: 3rpx solid #E3C7A4;
}

.child-title {
  color: #602F27;
  font-weight: 800;
}

.child-status-btn {
  background: #FFFBF0;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5A874;
}

.child-status-btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.child-active {
  background: #F6D387 !important;
  border-color: #D5A874 !important;
  box-shadow: 0 4rpx 0 #CB8E54 !important;
}

.child-status-text {
  color: #602F27;
  font-weight: 600;
}

.child-active .child-status-text {
  color: #602F27 !important;
  font-weight: 700;
}

.child-submit-btn {
  background: #F6D387 !important;
  color: #602F27 !important;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874;
  font-weight: 700;
}

.child-submit-btn:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.child-submit-btn:disabled {
  background: #E5E7EB !important;
  color: #9CA3AF !important;
  border-color: #D1D5DB !important;
  box-shadow: 0 6rpx 0 #D1D5DB !important;
}
</style>
