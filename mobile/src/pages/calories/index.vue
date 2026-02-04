<template>
  <view class="calories-page">
    <!-- 顶部日期与总览 -->
    <view class="summary-card">
      <view class="summary-header">
        <view class="date-switcher">
          <text class="date-arrow" @tap="changeDate(-1)">‹</text>
          <text class="date-text">{{ displayDate }}</text>
          <text class="date-arrow" @tap="changeDate(1)">›</text>
        </view>
        <view
          class="status-chip"
          :class="{ 'status-over': isOverTarget }"
        >
          {{ summary.status_text }}
        </view>
      </view>

      <view class="summary-body">
        <view class="summary-main">
          <text class="summary-label">今日已摄入</text>
          <view class="summary-value-row">
            <text class="summary-value">{{ summary.total_calories || 0 }}</text>
            <text class="summary-unit">kcal</text>
          </view>
          <text
            v-if="summary.target_min || summary.target_max"
            class="summary-range"
          >
            目标区间：{{ summary.target_min }} - {{ summary.target_max }} kcal
          </text>
        </view>

        <view class="macro-grid">
          <view class="macro-item">
            <text class="macro-label">碳水</text>
            <text class="macro-value">{{ summary.carbs_grams || 0 }} g</text>
          </view>
          <view class="macro-item">
            <text class="macro-label">蛋白质</text>
            <text class="macro-value">{{ summary.protein_grams || 0 }} g</text>
          </view>
          <view class="macro-item">
            <text class="macro-label">脂肪</text>
            <text class="macro-value">{{ summary.fat_grams || 0 }} g</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Tab 切换：热量记录 / 食谱推荐 -->
    <view class="tab-bar">
      <view
        class="tab-item"
        :class="{ active: currentTab === 'record' }"
        @tap="switchTab('record')"
      >
        <text class="tab-title">热量记录</text>
      </view>
      <view
        class="tab-item"
        :class="{ active: currentTab === 'recipe' }"
        @tap="switchTab('recipe')"
      >
        <text class="tab-title">食谱推荐</text>
      </view>
    </view>

    <!-- Tab 内容 -->
    <scroll-view class="tab-content" :scroll-y="true">
      <!-- 热量记录 -->
      <view v-if="currentTab === 'record'" class="record-tab">
        <!-- 快速添加 -->
        <view class="quick-add-card">
          <view class="quick-add-header">
            <text class="quick-add-title">快速记录一顿饮食</text>
            <text class="quick-add-hint">支持在校、居家、外出场景</text>
          </view>
          <view class="quick-add-row">
            <picker
              mode="selector"
              :range="mealTypeOptions"
              range-key="label"
              @change="onMealTypeChange"
            >
              <view class="quick-select">
                <text class="select-label">
                  {{ selectedMealType.label }}
                </text>
              </view>
            </picker>
            <input
              v-model="foodName"
              class="quick-input"
              type="text"
              placeholder="吃了什么？例如：鸡腿饭"
              maxlength="30"
            />
          </view>
          <view class="quick-add-row">
            <input
              v-model="calories"
              class="quick-input"
              type="number"
              placeholder="估算热量（kcal）"
            />
            <picker
              mode="selector"
              :range="sceneOptions"
              range-key="label"
              @change="onSceneChange"
            >
              <view class="quick-select scene">
                <text class="select-label">
                  {{ currentScene.label }}
                </text>
              </view>
            </picker>
          </view>
          <button
            class="save-btn"
            :disabled="!canSubmit"
            @tap="submitRecord"
          >
            记一笔
          </button>
        </view>

        <!-- 记录列表 -->
        <view class="records-section">
          <view class="section-header">
            <text class="section-title">今日饮食记录</text>
            <text class="section-count">{{ records.length }} 条</text>
          </view>

          <view v-if="loadingSummary" class="loading-state">
            <text class="loading-text">加载中...</text>
          </view>

          <view v-else-if="records.length === 0" class="empty-state">
            <text class="empty-emoji">🍽️</text>
            <text class="empty-text">还没有记录，先从今天的第一顿开始吧</text>
          </view>

          <view v-else class="record-list">
            <view
              v-for="item in records"
              :key="item.id"
              class="record-item"
            >
              <view class="record-main">
                <view class="record-title-row">
                  <text class="record-meal-tag">
                    {{ mealTypeText(item.meal_type) }}
                  </text>
                  <text class="record-food">{{ item.food_name }}</text>
                </view>
                <text class="record-scene">
                  场景：{{ sceneText(item.scene) }}
                </text>
              </view>
              <view class="record-calories">
                <text class="record-value">{{ item.calories || 0 }}</text>
                <text class="record-unit">kcal</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 食谱推荐 -->
      <view v-else class="recipe-tab">
        <!-- 场景选择 -->
        <view class="scene-switcher">
          <text class="scene-label">推荐场景</text>
          <view class="scene-chips">
            <view
              v-for="opt in sceneOptions"
              :key="opt.value"
              class="scene-chip"
              :class="{ active: opt.value === scene }"
              @tap="changeScene(opt)"
            >
              {{ opt.label }}
            </view>
          </view>
        </view>

        <!-- 推荐列表 -->
        <view class="recipes-section">
          <view class="section-header">
            <text class="section-title">今日推荐食谱</text>
          </view>

          <view v-if="loadingRecipes" class="loading-state">
            <text class="loading-text">AI 正在为你挑选合适的食谱...</text>
          </view>

          <view v-else-if="recipes.length === 0" class="empty-state">
            <text class="empty-emoji">🥗</text>
            <text class="empty-text">暂时没有推荐，你可以先手动记录饮食</text>
          </view>

          <view v-else class="recipe-list">
            <view
              v-for="recipe in recipes"
              :key="recipe.id"
              class="recipe-card"
            >
              <view class="recipe-header">
                <text class="recipe-meal-tag">
                  {{ mealTypeText(recipe.meal_type) }}
                </text>
                <text class="recipe-title">{{ recipe.name }}</text>
              </view>
              <text class="recipe-desc">{{ recipe.description }}</text>
              <view class="recipe-meta">
                <text class="meta-tag">
                  {{ recipe.total_calories }} kcal
                </text>
                <text class="meta-tag">
                  碳水 {{ recipe.carbs_grams }} g
                </text>
                <text class="meta-tag">
                  适合：{{ sceneText(recipe.scene) }}
                </text>
              </view>
              <view
                v-if="recipe.glucose_tip"
                class="recipe-tip"
              >
                {{ recipe.glucose_tip }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCaloriesStore } from '@/store'

const caloriesStore = useCaloriesStore()
const {
  currentTab,
  selectedDate,
  dailySummary,
  records,
  recipes,
  scene,
  loadingSummary,
  loadingRecipes,
  isOverTarget
} = storeToRefs(caloriesStore)

// 快速添加表单
const mealTypeOptions = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '加餐/零食' }
]

const sceneOptions = [
  { value: 'school', label: '在校' },
  { value: 'home', label: '居家' },
  { value: 'outing', label: '外出聚餐' }
]

const selectedMealType = ref(mealTypeOptions[0])
const currentScene = ref(sceneOptions[1])
const foodName = ref('')
const calories = ref('')

const summary = computed(() => dailySummary.value || {})

const displayDate = computed(() => {
  if (!selectedDate.value) return ''
  const [year, month, day] = selectedDate.value.split('-')
  return `${Number(month)}月${Number(day)}日`
})

const canSubmit = computed(() => {
  return foodName.value && calories.value
})

const switchTab = (tab) => {
  caloriesStore.setTab(tab)
  if (tab === 'record') {
    caloriesStore.fetchDailyCalories()
  } else {
    caloriesStore.fetchRecipes()
  }
}

const changeDate = (offset) => {
  caloriesStore.shiftDate(offset)
}

const onMealTypeChange = (e) => {
  const index = Number(e.detail.value || 0)
  selectedMealType.value = mealTypeOptions[index]
}

const onSceneChange = (e) => {
  const index = Number(e.detail.value || 0)
  const opt = sceneOptions[index]
  currentScene.value = opt
}

const changeScene = (opt) => {
  currentScene.value = opt
  caloriesStore.setScene(opt.value)
  caloriesStore.fetchRecipes()
}

const mealTypeText = (value) => {
  const map = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return map[value] || '其他'
}

const sceneText = (value) => {
  const map = {
    school: '在校',
    home: '居家',
    outing: '外出聚餐'
  }
  return map[value] || '通用'
}

const submitRecord = async () => {
  if (!canSubmit.value) return
  await caloriesStore.addRecord({
    meal_type: selectedMealType.value.value,
    food_name: foodName.value,
    calories: Number(calories.value),
    scene: currentScene.value.value
  })
  // 清空部分表单
  foodName.value = ''
  calories.value = ''
}

onMounted(() => {
  caloriesStore.initToday()
  caloriesStore.fetchDailyCalories()
  if (recipes.value.length === 0) {
    caloriesStore.fetchRecipes()
  }
})
</script>

<style scoped>
.calories-page {
  min-height: 100vh;
  background: #f3f4f6;
  padding: 24rpx;
  box-sizing: border-box;
}

.summary-card {
  background: linear-gradient(135deg, #f97316, #fb7185);
  border-radius: 28rpx;
  padding: 32rpx;
  color: #fff;
  box-shadow: 0 18rpx 40rpx rgba(249, 115, 22, 0.35);
  margin-bottom: 24rpx;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.date-switcher {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 28rpx;
}

.date-arrow {
  width: 48rpx;
  height: 48rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.15);
  text-align: center;
  line-height: 48rpx;
}

.date-text {
  font-size: 30rpx;
  font-weight: 500;
}

.status-chip {
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  font-size: 22rpx;
}

.status-chip.status-over {
  background: rgba(248, 250, 252, 0.18);
  border: 2rpx solid rgba(248, 250, 252, 0.9);
}

.summary-body {
  display: flex;
  justify-content: space-between;
  gap: 32rpx;
}

.summary-main {
  flex: 2;
}

.summary-label {
  font-size: 26rpx;
  opacity: 0.9;
}

.summary-value-row {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
  margin: 12rpx 0;
}

.summary-value {
  font-size: 56rpx;
  font-weight: 700;
}

.summary-unit {
  font-size: 26rpx;
}

.summary-range {
  font-size: 22rpx;
  opacity: 0.9;
}

.macro-grid {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.macro-item {
  padding: 10rpx 14rpx;
  border-radius: 14rpx;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
}

.macro-value {
  font-weight: 500;
}

.tab-bar {
  display: flex;
  background: #ffffff;
  border-radius: 999rpx;
  padding: 6rpx;
  margin-bottom: 20rpx;
}

.tab-item {
  flex: 1;
  height: 72rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: #6b7280;
}

.tab-item.active {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #ffffff;
  box-shadow: 0 10rpx 24rpx rgba(129, 140, 248, 0.35);
}

.tab-content {
  max-height: calc(100vh - 320rpx);
}

.record-tab,
.recipe-tab {
  padding-bottom: 40rpx;
}

.quick-add-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.06);
}

.quick-add-header {
  margin-bottom: 16rpx;
}

.quick-add-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.quick-add-hint {
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #9ca3af;
}

.quick-add-row {
  margin-top: 16rpx;
  display: flex;
  gap: 16rpx;
}

.quick-input {
  flex: 1;
  height: 76rpx;
  border-radius: 20rpx;
  padding: 0 24rpx;
  background: #f9fafb;
  font-size: 26rpx;
}

.quick-select {
  width: 200rpx;
  height: 76rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #ede9fe, #e0f2fe);
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-select.scene {
  width: 220rpx;
}

.select-label {
  font-size: 26rpx;
  color: #111827;
}

.save-btn {
  margin-top: 22rpx;
  width: 100%;
  height: 84rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 500;
  box-shadow: 0 10rpx 30rpx rgba(79, 70, 229, 0.35);
}

.save-btn:disabled {
  opacity: 0.6;
}

.records-section,
.recipes-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.section-count {
  font-size: 24rpx;
  color: #9ca3af;
}

.loading-state {
  padding: 40rpx 0;
  align-items: center;
  justify-content: center;
}

.loading-text {
  font-size: 26rpx;
  color: #6b7280;
}

.empty-state {
  padding: 60rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.empty-emoji {
  font-size: 72rpx;
}

.empty-text {
  font-size: 26rpx;
  color: #9ca3af;
}

.record-list {
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 20rpx;
  border-radius: 20rpx;
  background: #f9fafb;
}

.record-main {
  flex: 1;
}

.record-title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 6rpx;
}

.record-meal-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 22rpx;
}

.record-food {
  font-size: 28rpx;
  color: #111827;
}

.record-scene {
  font-size: 24rpx;
  color: #6b7280;
}

.record-calories {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.record-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #fb923c;
}

.record-unit {
  font-size: 22rpx;
  color: #6b7280;
}

.scene-switcher {
  margin-bottom: 16rpx;
}

.scene-label {
  font-size: 26rpx;
  color: #6b7280;
}

.scene-chips {
  margin-top: 12rpx;
  display: flex;
  gap: 12rpx;
}

.scene-chip {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  font-size: 24rpx;
  color: #4b5563;
}

.scene-chip.active {
  background: linear-gradient(135deg, #34d399, #22c55e);
  color: #ffffff;
}

.recipe-list {
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.recipe-card {
  padding: 20rpx;
  border-radius: 20rpx;
  background: #f9fafb;
}

.recipe-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.recipe-meal-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 22rpx;
}

.recipe-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #111827;
}

.recipe-desc {
  font-size: 24rpx;
  color: #4b5563;
  margin-bottom: 10rpx;
}

.recipe-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 8rpx;
}

.meta-tag {
  padding: 6rpx 14rpx;
  border-radius: 999rpx;
  background: #e5e7eb;
  font-size: 22rpx;
  color: #374151;
}

.recipe-tip {
  font-size: 22rpx;
  color: #059669;
  background: #ecfdf5;
  border-radius: 12rpx;
  padding: 8rpx 12rpx;
}
</style>


