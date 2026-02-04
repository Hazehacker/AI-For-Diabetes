<template>
  <view class="create-plan-page">
    <!-- 步骤指示器 -->
    <view class="steps-indicator">
      <view 
        v-for="(step, index) in steps" 
        :key="index"
        class="step-item"
        :class="{ active: currentStep >= index + 1, completed: currentStep > index + 1 }"
      >
        <view class="step-circle">
          <text v-if="currentStep > index + 1" class="step-check">✓</text>
          <text v-else class="step-number">{{ index + 1 }}</text>
        </view>
        <text class="step-label">{{ step }}</text>
      </view>
    </view>

    <!-- 步骤1: 数据原料选择 -->
    <view v-if="currentStep === 1" class="step-content">
      <view class="step-header">
        <text class="step-title">选择数据原料</text>
        <text class="step-subtitle">选择用于生成计划的数据来源</text>
      </view>

      <view class="data-cards">
        <!-- 血糖趋势 -->
        <view 
          class="data-card"
          :class="{ selected: selectedData.glucoseTrend }"
          @tap="toggleData('glucoseTrend')"
        >
          <view class="card-header">
            <text class="card-icon">📊</text>
            <view class="card-checkbox" :class="{ checked: selectedData.glucoseTrend }">
              <text v-if="selectedData.glucoseTrend" class="check-icon">✓</text>
            </view>
          </view>
          <text class="card-title">血糖趋势</text>
          <text class="card-desc">近7天 CGM 数据</text>
          <view v-if="selectedData.glucoseTrend" class="card-preview">
            <text class="preview-label">TIR: 78%</text>
            <text class="preview-label">平均: 6.2 mmol/L</text>
          </view>
        </view>

        <!-- 医嘱/病历 -->
        <view 
          class="data-card"
          :class="{ selected: selectedData.medicalRecords.length > 0 }"
          @tap="selectMedicalRecords"
        >
          <view class="card-header">
            <text class="card-icon">📋</text>
            <view class="card-checkbox" :class="{ checked: selectedData.medicalRecords.length > 0 }">
              <text v-if="selectedData.medicalRecords.length > 0" class="check-icon">✓</text>
            </view>
          </view>
          <text class="card-title">医嘱/病历</text>
          <text class="card-desc">最新诊断记录</text>
          <view v-if="selectedData.medicalRecords.length > 0" class="card-preview">
            <text class="preview-label">已选择 {{ selectedData.medicalRecords.length }} 条</text>
          </view>
        </view>

        <!-- 基础档案 -->
        <view 
          class="data-card"
          :class="{ selected: selectedData.baseProfile }"
          @tap="toggleData('baseProfile')"
        >
          <view class="card-header">
            <text class="card-icon">👤</text>
            <view class="card-checkbox" :class="{ checked: selectedData.baseProfile }">
              <text v-if="selectedData.baseProfile" class="check-icon">✓</text>
            </view>
          </view>
          <text class="card-title">基础档案</text>
          <text class="card-desc">用药清单、饮食偏好</text>
        </view>
      </view>

      <!-- 目标选择 -->
      <view class="goal-section">
        <text class="section-title">您的目标是什么？</text>
        <view class="goal-tags">
          <text 
            v-for="goal in goalOptions" 
            :key="goal"
            class="goal-tag"
            :class="{ selected: selectedGoal === goal }"
            @tap="selectedGoal = goal"
          >
            {{ goal }}
          </text>
        </view>
      </view>

      <button class="btn-next" @tap="nextStep" :disabled="!selectedGoal">
        下一步：AI 生成计划
      </button>
    </view>

    <!-- 步骤2: AI 生成预览 -->
    <view v-if="currentStep === 2" class="step-content">
      <view class="step-header">
        <text class="step-title">AI 计划草稿</text>
        <text class="step-subtitle">AI 正在为您生成个性化计划</text>
      </view>

      <!-- 生成中 -->
      <view v-if="generating" class="generating-state">
        <view class="loading-animation">
          <view class="loading-dot"></view>
          <view class="loading-dot"></view>
          <view class="loading-dot"></view>
        </view>
        <text class="loading-text">AI 思考中...</text>
        <text class="loading-hint">正在分析您的数据</text>
      </view>

      <!-- 生成完成 -->
      <view v-else-if="aiDraft" class="draft-preview">
        <!-- 计划标题 -->
        <view class="draft-header">
          <input 
            class="draft-title-input"
            v-model="aiDraft.target_goal"
            placeholder="计划标题"
          />
          <text class="edit-icon">✏️</text>
        </view>

        <!-- 计划类型 -->
        <view class="draft-meta">
          <text class="meta-label">计划类型</text>
          <text class="meta-value">{{ getPlanTypeText(aiDraft.plan_type) }}</text>
        </view>

        <view class="draft-meta">
          <text class="meta-label">持续时间</text>
          <text class="meta-value">{{ aiDraft.duration_days }} 天</text>
        </view>

        <!-- 任务列表 -->
        <view class="tasks-list">
          <text class="list-title">任务清单</text>
          
          <view 
            v-for="task in aiDraft.task_items" 
            :key="task.id"
            class="task-item"
          >
            <view class="task-time-badge">{{ task.time }}</view>
            <view class="task-content-area">
              <text class="task-content">{{ task.content }}</text>
              <text class="task-reminder">提醒: {{ task.reminder_text }}</text>
              <view class="task-level-selector">
                <text class="level-label">提醒级别:</text>
                <view class="level-options">
                  <text 
                    v-for="level in [1, 2, 3]" 
                    :key="level"
                    class="level-option"
                    :class="{ selected: task.reminder_level === level }"
                    @tap="updateTaskLevel(task.id, level)"
                  >
                    {{ getLevelText(level) }}
                  </text>
                </view>
              </view>
            </view>
            <view class="task-actions">
              <text class="action-icon" @tap="editTask(task)">✏️</text>
              <text class="action-icon delete" @tap="deleteTask(task.id)">🗑️</text>
            </view>
          </view>

          <!-- 添加自定义任务 -->
          <view class="add-task-btn" @tap="showAddTaskDialog">
            <text class="add-icon">+</text>
            <text class="add-text">添加自定义任务</text>
          </view>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-back" @tap="prevStep">上一步</button>
        <button class="btn-next" @tap="nextStep" :disabled="!aiDraft">
          下一步：微调发布
        </button>
      </view>
    </view>

    <!-- 步骤3: 微调与发布 -->
    <view v-if="currentStep === 3" class="step-content">
      <view class="step-header">
        <text class="step-title">最后确认</text>
        <text class="step-subtitle">检查并发布您的健康计划</text>
      </view>

      <view class="summary-card">
        <text class="summary-title">{{ aiDraft.target_goal }}</text>
        <text class="summary-type">{{ getPlanTypeText(aiDraft.plan_type) }}</text>
        
        <view class="summary-stats">
          <view class="stat-item">
            <text class="stat-value">{{ aiDraft.task_items.length }}</text>
            <text class="stat-label">个任务</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ aiDraft.duration_days }}</text>
            <text class="stat-label">天</text>
          </view>
        </view>

        <!-- 冲突检测结果 -->
        <view v-if="conflicts.length > 0" class="conflicts-warning">
          <text class="warning-icon">⚠️</text>
          <view class="warning-content">
            <text class="warning-title">检测到冲突</text>
            <text 
              v-for="(conflict, index) in conflicts" 
              :key="index"
              class="warning-item"
            >
              • {{ conflict }}
            </text>
          </view>
        </view>

        <!-- 安全提示 -->
        <view class="safety-notice">
          <text class="notice-icon">ℹ️</text>
          <text class="notice-text">
            本计划仅提供行为建议，不包含具体用药剂量调整。如需调整用药，请咨询医生。
          </text>
        </view>
      </view>

      <view class="step-actions">
        <button class="btn-back" @tap="prevStep">上一步</button>
        <button 
          class="btn-publish" 
          @tap="publishPlan"
          :disabled="conflicts.length > 0 || publishing"
        >
          {{ publishing ? '发布中...' : '发布计划' }}
        </button>
      </view>
    </view>

    <!-- 添加任务弹窗 -->
    <view v-if="showAddTask" class="modal-overlay" @tap.self="showAddTask = false">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">添加自定义任务</text>
          <text class="modal-close" @tap="showAddTask = false">✕</text>
        </view>

        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">时间</text>
            <input 
              class="form-input"
              v-model="newTask.time"
              placeholder="例如: 15:00"
            />
          </view>

          <view class="form-item">
            <text class="form-label">任务内容</text>
            <input 
              class="form-input"
              v-model="newTask.content"
              placeholder="例如: 快走20分钟"
            />
          </view>

          <view class="form-item">
            <text class="form-label">提醒文案</text>
            <input 
              class="form-input"
              v-model="newTask.reminder_text"
              placeholder="例如: 该去散步啦"
            />
          </view>
        </view>

        <view class="modal-footer">
          <button class="btn-cancel" @tap="showAddTask = false">取消</button>
          <button class="btn-confirm" @tap="addCustomTask">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHealthPlanStore } from '@/store/healthPlan'
import { storeToRefs } from 'pinia'

const healthPlanStore = useHealthPlanStore()
const { wizard } = storeToRefs(healthPlanStore)

const steps = ['选择数据', 'AI生成', '确认发布']
const currentStep = computed(() => wizard.value.step)
const selectedData = computed(() => wizard.value.selectedData)
const aiDraft = computed(() => wizard.value.aiDraft)
const generating = computed(() => wizard.value.generating)

// 目标选项
const goalOptions = ['血糖优化', '用药管理', '饮食调整', '运动计划', '复查提醒']
const selectedGoal = ref('')

// 冲突检测
const conflicts = ref([])

// 发布状态
const publishing = ref(false)

// 添加任务
const showAddTask = ref(false)
const newTask = ref({
  time: '',
  content: '',
  reminder_text: ''
})

// 切换数据选择
const toggleData = (key) => {
  const current = selectedData.value[key]
  healthPlanStore.updateSelectedData({ [key]: !current })
}

// 选择医嘱记录
const selectMedicalRecords = () => {
  uni.showModal({
    title: '选择医嘱记录',
    content: '此功能将调取病历档案',
    showCancel: false
  })
  
  // TODO: 实际实现选择逻辑
  healthPlanStore.updateSelectedData({
    medicalRecords: ['HbA1c 7.5%', '复查建议']
  })
}

// 下一步
const nextStep = async () => {
  if (currentStep.value === 1) {
    // 生成 AI 草稿
    try {
      await healthPlanStore.generateAIDraft(selectedGoal.value)
    } catch (error) {
      uni.showToast({
        title: '生成失败，请重试',
        icon: 'none'
      })
    }
  } else if (currentStep.value === 2) {
    // 进入确认步骤，执行冲突检测
    conflicts.value = healthPlanStore.detectConflicts(aiDraft.value.task_items)
    healthPlanStore.setWizardStep(3)
  }
}

// 上一步
const prevStep = () => {
  healthPlanStore.setWizardStep(currentStep.value - 1)
}

// 更新任务提醒级别
const updateTaskLevel = (taskId, level) => {
  healthPlanStore.updateDraftTask(taskId, { reminder_level: level })
}

// 编辑任务
const editTask = (task) => {
  uni.showModal({
    title: '编辑任务',
    editable: true,
    placeholderText: task.content,
    success: (res) => {
      if (res.confirm && res.content) {
        healthPlanStore.updateDraftTask(task.id, { content: res.content })
      }
    }
  })
}

// 删除任务
const deleteTask = (taskId) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这个任务吗？',
    success: (res) => {
      if (res.confirm) {
        healthPlanStore.removeDraftTask(taskId)
      }
    }
  })
}

// 显示添加任务对话框
const showAddTaskDialog = () => {
  showAddTask.value = true
  newTask.value = {
    time: '',
    content: '',
    reminder_text: ''
  }
}

// 添加自定义任务
const addCustomTask = () => {
  if (!newTask.value.time || !newTask.value.content) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    })
    return
  }
  
  healthPlanStore.addCustomTask(newTask.value)
  showAddTask.value = false
}

// 发布计划
const publishPlan = async () => {
  publishing.value = true
  
  try {
    await healthPlanStore.publishPlan()
    
    uni.showToast({
      title: '计划已发布',
      icon: 'success'
    })
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    uni.showToast({
      title: error.message || '发布失败',
      icon: 'none'
    })
  } finally {
    publishing.value = false
  }
}

// 计划类型文本
const getPlanTypeText = (type) => {
  const map = {
    1: '用药计划',
    2: '复查计划',
    3: '饮食计划',
    4: '运动计划'
  }
  return map[type] || '健康计划'
}

// 提醒级别文本
const getLevelText = (level) => {
  const map = {
    1: '普通',
    2: '重要',
    3: '紧急'
  }
  return map[level] || '普通'
}

onMounted(() => {
  healthPlanStore.startWizard()
})
</script>

<style scoped>
.create-plan-page {
  min-height: 100vh;
  background: #F3F4F6;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  justify-content: space-between;
  padding: 40rpx 20rpx;
  margin-bottom: 32rpx;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-item::after {
  content: '';
  position: absolute;
  top: 24rpx;
  left: 50%;
  right: -50%;
  height: 2rpx;
  background: #E5E7EB;
  z-index: 0;
}

.step-item:last-child::after {
  display: none;
}

.step-item.active::after {
  background: #3B82F6;
}

.step-circle {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12rpx;
  position: relative;
  z-index: 1;
}

.step-item.active .step-circle {
  background: #3B82F6;
}

.step-item.completed .step-circle {
  background: #10B981;
}

.step-number,
.step-check {
  font-size: 24rpx;
  color: white;
  font-weight: bold;
}

.step-label {
  font-size: 22rpx;
  color: #9CA3AF;
}

.step-item.active .step-label {
  color: #3B82F6;
  font-weight: 500;
}

/* 步骤内容 */
.step-content {
  padding: 20rpx;
}

.step-header {
  margin-bottom: 32rpx;
}

.step-title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.step-subtitle {
  display: block;
  font-size: 28rpx;
  color: #6B7280;
}

/* 数据卡片 */
.data-cards {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.data-card {
  padding: 32rpx;
  background: white;
  border-radius: 16rpx;
  border: 2rpx solid #E5E7EB;
  transition: all 0.3s;
}

.data-card.selected {
  border-color: #3B82F6;
  background: #EFF6FF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-icon {
  font-size: 48rpx;
}

.card-checkbox {
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #D1D5DB;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-checkbox.checked {
  background: #3B82F6;
  border-color: #3B82F6;
}

.check-icon {
  color: white;
  font-size: 24rpx;
  font-weight: bold;
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.card-desc {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

.card-preview {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #E5E7EB;
  display: flex;
  gap: 16rpx;
}

.preview-label {
  font-size: 22rpx;
  color: #3B82F6;
  background: white;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

/* 目标选择 */
.goal-section {
  margin-bottom: 32rpx;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #374151;
  margin-bottom: 16rpx;
}

.goal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.goal-tag {
  padding: 16rpx 32rpx;
  background: white;
  border: 2rpx solid #E5E7EB;
  border-radius: 24rpx;
  font-size: 28rpx;
  color: #6B7280;
}

.goal-tag.selected {
  background: #3B82F6;
  border-color: #3B82F6;
  color: white;
}

/* 生成状态 */
.generating-state {
  text-align: center;
  padding: 120rpx 20rpx;
}

.loading-animation {
  display: flex;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.loading-dot {
  width: 16rpx;
  height: 16rpx;
  background: #3B82F6;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-text {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.loading-hint {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 草稿预览 */
.draft-preview {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
}

.draft-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.draft-title-input {
  flex: 1;
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
  border: none;
  outline: none;
}

.edit-icon {
  font-size: 32rpx;
}

.draft-meta {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
}

.meta-label {
  font-size: 24rpx;
  color: #6B7280;
}

.meta-value {
  font-size: 24rpx;
  color: #1F2937;
  font-weight: 500;
}

/* 任务列表 */
.tasks-list {
  margin-top: 32rpx;
}

.list-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.task-item {
  display: flex;
  gap: 16rpx;
  padding: 24rpx;
  background: #F9FAFB;
  border-radius: 12rpx;
  margin-bottom: 12rpx;
}

.task-time-badge {
  padding: 8rpx 16rpx;
  background: #3B82F6;
  color: white;
  border-radius: 8rpx;
  font-size: 22rpx;
  font-weight: bold;
  height: fit-content;
}

.task-content-area {
  flex: 1;
}

.task-content {
  display: block;
  font-size: 28rpx;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.task-reminder {
  display: block;
  font-size: 22rpx;
  color: #6B7280;
  margin-bottom: 12rpx;
}

.task-level-selector {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.level-label {
  font-size: 22rpx;
  color: #6B7280;
}

.level-options {
  display: flex;
  gap: 8rpx;
}

.level-option {
  padding: 4rpx 12rpx;
  background: white;
  border: 1rpx solid #E5E7EB;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: #6B7280;
}

.level-option.selected {
  background: #3B82F6;
  border-color: #3B82F6;
  color: white;
}

.task-actions {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.action-icon {
  font-size: 32rpx;
  padding: 8rpx;
}

.action-icon.delete {
  color: #EF4444;
}

.add-task-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  background: #F3F4F6;
  border: 2rpx dashed #D1D5DB;
  border-radius: 12rpx;
  margin-top: 12rpx;
}

.add-icon {
  font-size: 32rpx;
  color: #3B82F6;
}

.add-text {
  font-size: 28rpx;
  color: #3B82F6;
}

/* 总结卡片 */
.summary-card {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
}

.summary-title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.summary-type {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  margin-bottom: 24rpx;
}

.summary-stats {
  display: flex;
  gap: 32rpx;
  padding: 24rpx 0;
  border-top: 1rpx solid #F3F4F6;
  border-bottom: 1rpx solid #F3F4F6;
  margin-bottom: 24rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #3B82F6;
}

.stat-label {
  font-size: 22rpx;
  color: #6B7280;
}

/* 冲突警告 */
.conflicts-warning {
  display: flex;
  gap: 16rpx;
  padding: 20rpx;
  background: #FEF3C7;
  border-radius: 12rpx;
  margin-bottom: 24rpx;
}

.warning-icon {
  font-size: 40rpx;
}

.warning-content {
  flex: 1;
}

.warning-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #92400E;
  margin-bottom: 8rpx;
}

.warning-item {
  display: block;
  font-size: 24rpx;
  color: #92400E;
  margin-bottom: 4rpx;
}

/* 安全提示 */
.safety-notice {
  display: flex;
  gap: 12rpx;
  padding: 20rpx;
  background: #EFF6FF;
  border-radius: 12rpx;
}

.notice-icon {
  font-size: 32rpx;
}

.notice-text {
  flex: 1;
  font-size: 24rpx;
  color: #1E40AF;
  line-height: 1.6;
}

/* 按钮 */
.step-actions {
  display: flex;
  gap: 16rpx;
}

.btn-next,
.btn-back,
.btn-publish {
  flex: 1;
  height: 88rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.btn-next,
.btn-publish {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
}

.btn-next:disabled,
.btn-publish:disabled {
  background: #D1D5DB;
  color: #9CA3AF;
}

.btn-back {
  background: #F3F4F6;
  color: #6B7280;
}

/* 弹窗 */
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
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 600rpx;
  background: white;
  border-radius: 24rpx;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1rpx solid #E5E7EB;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.modal-close {
  font-size: 48rpx;
  color: #9CA3AF;
}

.modal-body {
  padding: 32rpx;
}

.form-item {
  margin-bottom: 24rpx;
}

.form-label {
  display: block;
  font-size: 24rpx;
  color: #374151;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.modal-footer {
  display: flex;
  gap: 16rpx;
  padding: 32rpx;
  border-top: 1rpx solid #E5E7EB;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  height: 80rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: bold;
  border: none;
}

.btn-cancel {
  background: #F3F4F6;
  color: #6B7280;
}

.btn-confirm {
  background: #3B82F6;
  color: white;
}
</style>
