<template>
  <view class="add-glucose-modal" v-if="visible" @tap.self="close">
    <view class="modal-content" @tap.stop>
      <view class="modal-header">
        <text class="modal-title">记录血糖</text>
        <text class="close-btn" @tap="close">✕</text>
      </view>

      <view class="modal-body">
        <!-- 血糖值输入 -->
        <view class="form-item">
          <text class="form-label">血糖值 (mmol/L)</text>
          <input 
            class="form-input"
            type="digit"
            v-model="formData.glucose_value"
            placeholder="请输入血糖值"
            :maxlength="4"
          />
        </view>

        <!-- 测量时间 -->
        <view class="form-item">
          <text class="form-label">测量时间</text>
          <view class="datetime-picker" @tap="showDateTimePicker">
            <text class="datetime-text">{{ formattedDateTime }}</text>
            <text class="picker-icon">📅</text>
          </view>
        </view>

        <!-- 备注（可选） -->
        <view class="form-item">
          <text class="form-label">备注（可选）</text>
          <textarea 
            class="form-textarea"
            v-model="formData.note"
            placeholder="如：餐前、餐后、运动后等"
            :maxlength="100"
          />
        </view>

        <!-- 快捷时间标签 -->
        <view class="quick-tags">
          <text class="tag-label">快捷标签：</text>
          <view class="tags-list">
            <text 
              v-for="tag in quickTags" 
              :key="tag"
              class="tag-item"
              @tap="addTag(tag)"
            >
              {{ tag }}
            </text>
          </view>
        </view>

        <!-- 状态提示 -->
        <view v-if="glucoseStatus" class="status-hint" :class="statusClass">
          <text class="status-icon">{{ statusIcon }}</text>
          <text class="status-text">{{ statusText }}</text>
        </view>
      </view>

      <view class="modal-footer">
        <button class="btn btn-cancel" @tap="close">取消</button>
        <button class="btn btn-confirm" @tap="confirm" :disabled="!isValid">保存</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGlucoseCurveStore } from '@/store/glucoseCurve'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])

const glucoseCurveStore = useGlucoseCurveStore()

// 表单数据
const formData = ref({
  glucose_value: '',
  measure_time: new Date(),
  note: ''
})

// 快捷标签
const quickTags = ['餐前', '餐后', '运动前', '运动后', '睡前', '夜间']

// 格式化日期时间
const formattedDateTime = computed(() => {
  const date = formData.value.measure_time
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
})

// 血糖状态判断
const glucoseStatus = computed(() => {
  const value = parseFloat(formData.value.glucose_value)
  if (isNaN(value) || value <= 0) return null
  
  const { min, max } = glucoseCurveStore.referenceRange
  
  if (value < min) {
    return 'low'
  } else if (value > max) {
    return 'high'
  } else {
    return 'normal'
  }
})

const statusClass = computed(() => {
  return `status-${glucoseStatus.value}`
})

const statusIcon = computed(() => {
  const map = {
    low: '⚠️',
    high: '⚠️',
    normal: '✓'
  }
  return map[glucoseStatus.value] || ''
})

const statusText = computed(() => {
  const map = {
    low: '血糖偏低，请注意',
    high: '血糖偏高，请注意',
    normal: '血糖在正常范围内'
  }
  return map[glucoseStatus.value] || ''
})

// 表单验证
const isValid = computed(() => {
  const value = parseFloat(formData.value.glucose_value)
  return !isNaN(value) && value > 0 && value < 30
})

// 显示日期时间选择器
const showDateTimePicker = () => {
  uni.showModal({
    title: '提示',
    content: '请使用系统日期时间选择器（此处为演示）',
    showCancel: false
  })
  
  // TODO: 实际项目中使用 uni.showDateTimePicker 或第三方组件
}

// 添加快捷标签
const addTag = (tag) => {
  if (formData.value.note) {
    formData.value.note += ` ${tag}`
  } else {
    formData.value.note = tag
  }
}

// 关闭弹窗
const close = () => {
  emit('close')
}

// 确认保存
const confirm = () => {
  if (!isValid.value) {
    uni.showToast({
      title: '请输入有效的血糖值',
      icon: 'none'
    })
    return
  }
  
  const record = {
    glucose_value: parseFloat(formData.value.glucose_value),
    measure_time: formData.value.measure_time,
    note: formData.value.note,
    source: 'manual'
  }
  
  glucoseCurveStore.addGlucoseRecord(record)
  
  uni.showToast({
    title: '记录成功',
    icon: 'success'
  })
  
  emit('confirm', record)
  
  // 重置表单
  formData.value = {
    glucose_value: '',
    measure_time: new Date(),
    note: ''
  }
  
  close()
}

// 监听弹窗显示，重置表单
watch(() => props.visible, (val) => {
  if (val) {
    formData.value = {
      glucose_value: '',
      measure_time: new Date(),
      note: ''
    }
  }
})
</script>

<style scoped>
.add-glucose-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 600rpx;
  background: white;
  border-radius: 24rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #E5E7EB;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
}

.close-btn {
  font-size: 48rpx;
  color: #9CA3AF;
  line-height: 1;
}

.modal-body {
  padding: 32rpx;
  max-height: 60vh;
  overflow-y: auto;
}

.form-item {
  margin-bottom: 32rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 12rpx;
  font-size: 32rpx;
  color: #1F2937;
}

.form-input:focus {
  border-color: #3B82F6;
  background: white;
}

.datetime-picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 88rpx;
  padding: 0 24rpx;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 12rpx;
}

.datetime-text {
  font-size: 32rpx;
  color: #1F2937;
}

.picker-icon {
  font-size: 40rpx;
}

.form-textarea {
  width: 100%;
  min-height: 120rpx;
  padding: 16rpx 24rpx;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #1F2937;
}

.quick-tags {
  margin-bottom: 32rpx;
}

.tag-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  margin-bottom: 12rpx;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag-item {
  padding: 8rpx 20rpx;
  background: #EFF6FF;
  color: #3B82F6;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.status-hint {
  padding: 20rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.status-hint.status-low,
.status-hint.status-high {
  background: #FEF3C7;
  border: 2rpx solid #F59E0B;
}

.status-hint.status-normal {
  background: #D1FAE5;
  border: 2rpx solid #10B981;
}

.status-icon {
  font-size: 40rpx;
}

.status-text {
  font-size: 28rpx;
  color: #374151;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  gap: 16rpx;
  padding: 32rpx;
  border-top: 1rpx solid #E5E7EB;
}

.btn {
  flex: 1;
  height: 88rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.btn-cancel {
  background: #F3F4F6;
  color: #6B7280;
}

.btn-confirm {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
}

.btn-confirm:disabled {
  background: #D1D5DB;
  color: #9CA3AF;
}
</style>
