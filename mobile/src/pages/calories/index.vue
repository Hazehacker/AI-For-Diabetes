<template>
  <!-- 儿童模式：奶酪仓鼠风格 -->
  <view v-if="userRole === 'child_under_12'" class="child-calories">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">热量记录与食谱推荐</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 吉祥物卡片 -->
    <view class="mascot-food-card">
      <image class="mascot-img-food" src="/static/ch/ch_index_welcome.png" mode="aspectFit"></image>
      <view class="food-summary">
        <view class="summary-bubble">
          <text class="bubble-text">{{ foodMessage }}</text>
        </view>
        <view class="energy-info">
          <text class="energy-label-child">今天吃了</text>
          <view class="energy-value-row">
            <text class="energy-num">{{ summary.total_calories || 0 }}</text>
            <text class="energy-unit-child">能量</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 快速记录 -->
    <view class="quick-record-child">
      <view class="record-header-child">
        <text class="record-title-child">📝 记录一下</text>
      </view>
      <view class="meal-buttons">
        <view 
          v-for="meal in childMeals" 
          :key="meal.value"
          class="meal-btn"
          :class="{ active: selectedMealType.value === meal.value }"
          @tap="selectMeal(meal)"
        >
          <text class="meal-icon">{{ meal.icon }}</text>
          <text class="meal-name">{{ meal.label }}</text>
        </view>
      </view>
      <view class="food-input-area">
        <input
          v-model="foodName"
          class="food-input-child"
          placeholder="吃了什么呀？"
        />
        <image class="add-btn-child" src="/static/ch/add.png" mode="aspectFit" @tap="quickAddFood"></image>
      </view>
    </view>

    <!-- 今日记录 -->
    <view class="today-food-card">
      <view class="food-card-header">
        <text class="food-card-title">🍽️ 今天吃的</text>
        <text class="food-count">{{ records.length }}样</text>
      </view>
      <view v-if="records.length === 0" class="empty-food">
        <text class="empty-emoji-food">🍴</text>
        <text class="empty-text-food">还没记录呢，吃了什么告诉小仓鼠吧~</text>
      </view>
      <view v-else class="food-list-child">
        <view v-for="item in records" :key="item.id" class="food-item-child">
          <text class="food-meal-icon">{{ getMealIcon(item.meal_type) }}</text>
          <text class="food-name-child">{{ item.food_name }}</text>
          <text class="food-cal-child">{{ item.calories }}能量</text>
        </view>
      </view>
    </view>

    <!-- 推荐食物 -->
    <view class="recommend-card-child">
      <view class="recommend-header">
        <text class="recommend-title">🥗 推荐</text>
      </view>
      <view class="recommend-list">
        <view v-for="food in childFoodTips" :key="food.name" class="recommend-item">
          <text class="recommend-icon">{{ food.icon }}</text>
          <view class="recommend-info">
            <text class="recommend-name">{{ food.name }}</text>
            <text class="recommend-tip">{{ food.tip }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部装饰 -->
    <view class="child-cal-footer">
      <text class="footer-deco">🧀</text>
      <text class="footer-deco">🍎</text>
      <text class="footer-deco">🧀</text>
    </view>
  </view>

  <!-- 成人/青少年模式 -->
  <view v-else class="calories-page">
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

    <!-- Tab 切换：热量记录 / 食谱推荐 / 数据联动 -->
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
      <view
        class="tab-item"
        :class="{ active: currentTab === 'analysis' }"
        @tap="switchTab('analysis')"
      >
        <text class="tab-title">数据联动</text>
      </view>
    </view>

    <!-- Tab 内容 -->
    <scroll-view class="tab-content" :scroll-y="true">
      <!-- 热量记录 -->
      <view v-if="currentTab === 'record'" class="record-tab">
        <!-- 餐次轴 -->
        <view class="meal-time-axis">
          <view
            v-for="meal in mealTypeOptions"
            :key="meal.value"
            class="meal-time-item"
            :class="{ 
              active: selectedMealType.value === meal.value,
              highlight: isCurrentMealTime(meal.value)
            }"
            @tap="selectMealType(meal)"
          >
            <text class="meal-time-icon">{{ meal.icon }}</text>
            <text class="meal-time-label">{{ meal.label }}</text>
          </view>
        </view>

        <!-- 智能录入区 -->
        <view class="smart-input-card">
          <view class="smart-input-header">
            <text class="smart-input-title">智能录入</text>
            <text class="smart-input-hint">拍照识别、条码扫描或手动搜索</text>
          </view>
          
          <!-- 大尺寸拍照识别按钮 -->
          <view class="input-methods">
            <view class="photo-recognize-btn" @tap="handlePhotoRecognize">
              <text class="photo-icon">📷</text>
              <text class="photo-text">拍照识别</text>
            </view>
            <view class="input-method-row">
              <view class="barcode-btn" @tap="handleBarcodeScan">
                <text class="method-icon">📱</text>
                <text class="method-text">条码扫描</text>
              </view>
              <view class="search-btn" @tap="handleManualSearch">
                <text class="method-icon">🔍</text>
                <text class="method-text">手动搜索</text>
              </view>
            </view>
          </view>

          <!-- 识别结果确认卡片 -->
          <view v-if="recognitionResult" class="recognition-result-card">
            <view class="result-header">
              <text class="result-title">识别结果</text>
              <text class="result-close" @tap="clearRecognitionResult">✕</text>
            </view>
            <view class="result-foods">
              <view
                v-for="(food, idx) in recognitionResult.foods"
                :key="idx"
                class="result-food-item"
                :class="{ selected: food.selected }"
                @tap="toggleFoodSelection(food)"
              >
                <text class="food-check">{{ food.selected ? '✓' : '' }}</text>
                <text class="food-name">{{ food.name }}</text>
                <text class="food-weight">{{ food.weight }}g</text>
              </view>
            </view>
            <view class="result-summary">
              <text class="summary-text">
                总碳水：{{ recognitionResult.total_carbs || 0 }}g
              </text>
            </view>
          </view>

          <!-- 手动输入表单 -->
          <view v-if="showManualForm" class="manual-form">
            <input
              v-model="foodName"
              class="manual-input"
              type="text"
              placeholder="搜索食物名称..."
              @input="handleFoodSearch"
            />
            <view v-if="searchResults.length > 0" class="search-results">
              <view
                v-for="item in searchResults"
                :key="item.id"
                class="search-result-item"
                @tap="selectFoodItem(item)"
              >
                <text class="result-food-name">{{ item.name }}</text>
                <text class="result-food-info">
                  {{ item.carbs }}g碳水 | GI:{{ item.gi_level }}
                </text>
              </view>
            </view>
          </view>
        </view>

        <!-- 辅助参数 -->
        <view v-if="selectedFoodItems.length > 0" class="auxiliary-params-card">
          <view class="params-header">
            <text class="params-title">补充信息</text>
          </view>
          
          <!-- 分量滑块 -->
          <view class="param-item">
            <text class="param-label">分量</text>
            <view class="portion-slider-wrapper">
              <slider
                :value="portionValue"
                min="0"
                max="200"
                step="10"
                activeColor="#6366f1"
                @change="onPortionChange"
              />
              <view class="portion-labels">
                <text class="portion-label">半碗</text>
                <text class="portion-label">一碗</text>
              </view>
            </view>
            <text class="portion-value">{{ portionText }}</text>
          </view>

          <!-- 进食感受 -->
          <view class="param-item">
            <text class="param-label">进食感受</text>
            <view class="feeling-chips">
              <view
                v-for="feeling in feelingOptions"
                :key="feeling.value"
                class="feeling-chip"
                :class="{ active: currentFeeling === feeling.value }"
                @tap="selectFeeling(feeling.value)"
              >
                <text class="feeling-icon">{{ feeling.icon }}</text>
                <text class="feeling-text">{{ feeling.label }}</text>
              </view>
            </view>
          </view>

          <!-- 特殊标签 -->
          <view class="param-item">
            <text class="param-label">特殊标签</text>
            <view class="tag-chips">
              <view
                v-for="tag in tagOptions"
                :key="tag.value"
                class="tag-chip"
                :class="{ active: selectedTags.includes(tag.value) }"
                @tap="toggleTag(tag.value)"
              >
                {{ tag.label }}
              </view>
            </view>
          </view>

          <!-- 保存按钮 -->
          <button
            class="save-record-btn"
            @tap="submitRecordWithParams"
          >
            保存记录
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
        <!-- 场景滤镜 -->
        <view class="scene-filter">
          <text class="filter-label">推荐场景</text>
          <view class="scene-filter-chips">
            <view
              v-for="opt in sceneFilterOptions"
              :key="opt.value"
              class="scene-filter-chip"
              :class="{ active: currentSceneFilter === opt.value }"
              @tap="changeSceneFilter(opt.value)"
            >
              <text class="filter-icon">{{ opt.icon }}</text>
              <text class="filter-text">{{ opt.label }}</text>
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
              @tap="showRecipeDetail(recipe)"
            >
              <!-- 红绿灯标签 -->
              <view class="recipe-gi-badge" :class="getGIBadgeClass(recipe.gi_level)">
                <text class="gi-badge-icon">{{ getGIBadgeIcon(recipe.gi_level) }}</text>
                <text class="gi-badge-text">{{ getGIBadgeText(recipe.gi_level) }}</text>
              </view>

              <view class="recipe-header">
                <text class="recipe-meal-tag">
                  {{ mealTypeText(recipe.meal_type) }}
                </text>
                <text class="recipe-title">{{ recipe.name }}</text>
              </view>
              <text class="recipe-desc">{{ recipe.description }}</text>
              
              <!-- 营养信息 -->
              <view class="recipe-nutrition">
                <view class="nutrition-item">
                  <text class="nutrition-label">热量</text>
                  <text class="nutrition-value">{{ recipe.total_calories }} kcal</text>
                </view>
                <view class="nutrition-item">
                  <text class="nutrition-label">碳水</text>
                  <text class="nutrition-value">{{ recipe.carbs_grams }}g</text>
                </view>
                <view class="nutrition-item">
                  <text class="nutrition-label">蛋白质</text>
                  <text class="nutrition-value">{{ recipe.protein_grams || 0 }}g</text>
                </view>
                <view class="nutrition-item">
                  <text class="nutrition-label">脂肪</text>
                  <text class="nutrition-value">{{ recipe.fat_grams || 0 }}g</text>
                </view>
              </view>

              <!-- 胰岛素注射建议 -->
              <view v-if="recipe.insulin_tip" class="insulin-tip">
                <text class="insulin-icon">💉</text>
                <text class="insulin-text">{{ recipe.insulin_tip }}</text>
              </view>

              <!-- 操作按钮 -->
              <view class="recipe-actions">
                <view class="action-btn favorite-btn" @tap.stop="toggleFavorite(recipe)">
                  <text class="action-icon">{{ recipe.is_favorite ? '❤️' : '🤍' }}</text>
                  <text class="action-text">收藏</text>
                </view>
                <view class="action-btn share-btn" @tap.stop="shareToFamily(recipe)">
                  <text class="action-icon">📤</text>
                  <text class="action-text">发送给家属</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 数据联动分析 Tab -->
      <view v-if="currentTab === 'analysis'" class="analysis-tab">
        <view class="analysis-section">
          <view class="section-header">
            <text class="section-title">饮食-血糖关联分析</text>
          </view>
          
          <!-- 双轴折线图 -->
          <view class="chart-container">
            <view class="chart-placeholder">
              <text class="chart-label">碳水摄入量 vs 血糖波动</text>
              <text class="chart-hint">图表加载中...</text>
            </view>
          </view>

          <!-- 归因分析 -->
          <view class="attribution-analysis">
            <view class="analysis-header">
              <text class="analysis-title">异常点归因分析</text>
            </view>
            <view v-if="attributionData.length === 0" class="empty-analysis">
              <text class="empty-text">暂无异常数据</text>
            </view>
            <view v-else class="attribution-list">
              <view
                v-for="item in attributionData"
                :key="item.id"
                class="attribution-item"
              >
                <view class="attribution-time">
                  <text class="time-text">{{ item.time }}</text>
                  <text class="glucose-value high">{{ item.glucose }} mmol/L</text>
                </view>
                <view class="attribution-reason">
                  <text class="reason-icon">🔍</text>
                  <text class="reason-text">{{ item.reason }}</text>
                </view>
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
import { useDashboardStore } from '@/store/dashboard'
import { caloriesApi } from '@/api'

const caloriesStore = useCaloriesStore()
const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
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

// ========== 儿童模式相关 ==========
const childMeals = [
  { value: 'breakfast', label: '早餐', icon: '🌅' },
  { value: 'lunch', label: '午餐', icon: '☀️' },
  { value: 'dinner', label: '晚餐', icon: '🌙' },
  { value: 'snack', label: '零食', icon: '🍪' }
]

const childFoodTips = [
  { name: '多吃蔬菜', icon: '🥦', tip: '蔬菜让你更健康' },
  { name: '喝牛奶', icon: '🥛', tip: '帮助长高高' },
  { name: '吃水果', icon: '🍎', tip: '补充维生素' }
]

const foodMessage = computed(() => {
  const cal = summary.value.total_calories || 0
  if (cal === 0) return '今天还没吃东西呢，记得按时吃饭哦~'
  if (cal < 500) return '吃得有点少，要多吃点哦！'
  if (cal < 1200) return '吃得不错，继续保持！'
  return '今天吃得很丰盛呢！'
})

const selectMeal = (meal) => {
  selectedMealType.value = meal
}

const getMealIcon = (mealType) => {
  const icons = { breakfast: '🌅', lunch: '☀️', dinner: '🌙', snack: '🍪' }
  return icons[mealType] || '🍽️'
}

const quickAddFood = async () => {
  if (!foodName.value) {
    uni.showToast({ title: '请输入食物名称', icon: 'none' })
    return
  }
  await caloriesStore.addRecord({
    meal_type: selectedMealType.value.value,
    food_name: foodName.value,
    calories: 200, // 儿童模式简化，默认200卡
    scene: 'home'
  })
  foodName.value = ''
  uni.showToast({ title: '记录成功！⭐', icon: 'none' })
}

// 餐次选项（带图标）
const mealTypeOptions = [
  { value: 'breakfast', label: '早餐', icon: '🌅' },
  { value: 'lunch', label: '午餐', icon: '☀️' },
  { value: 'dinner', label: '晚餐', icon: '🌙' },
  { value: 'snack', label: '加餐', icon: '🍪' }
]

// 场景选项
const sceneOptions = [
  { value: 'school', label: '在校' },
  { value: 'home', label: '居家' },
  { value: 'outing', label: '外出聚餐' }
]

// 场景滤镜选项（食谱推荐用）
const sceneFilterOptions = [
  { value: 'school', label: '校园餐', icon: '🏫' },
  { value: 'home', label: '家常菜', icon: '🏠' },
  { value: 'outing', label: '外出聚餐', icon: '🍽️' },
  { value: 'festival', label: '节日特供', icon: '🎉' }
]

// 进食感受选项
const feelingOptions = [
  { value: 'full', label: '吃饱', icon: '😋' },
  { value: 'seven', label: '七分饱', icon: '😊' },
  { value: 'half', label: '半饱', icon: '😐' }
]

// 特殊标签选项
const tagOptions = [
  { value: 'sugar_free', label: '无糖' },
  { value: 'honey', label: '含蜂蜜' },
  { value: 'low_gi', label: '低GI' },
  { value: 'high_fiber', label: '高纤维' }
]

const selectedMealType = ref(mealTypeOptions[0])
const currentScene = ref(sceneOptions[1])
const currentSceneFilter = ref('home')
const foodName = ref('')
const calories = ref('')

// 识别结果
const recognitionResult = ref(null)
const showManualForm = ref(false)
const searchResults = ref([])

// 选中的食物项
const selectedFoodItems = ref([])

// 辅助参数
const portionValue = ref(100) // 0-200，对应半碗到一碗
const currentFeeling = ref('')
const selectedTags = ref([])

// 归因分析数据
const attributionData = ref([])

const summary = computed(() => dailySummary.value || {})

const displayDate = computed(() => {
  if (!selectedDate.value) return ''
  const [year, month, day] = selectedDate.value.split('-')
  return `${Number(month)}月${Number(day)}日`
})

const canSubmit = computed(() => {
  return foodName.value && calories.value
})

// 根据当前时间判断当前餐次
const isCurrentMealTime = (mealType) => {
  const hour = new Date().getHours()
  if (mealType === 'breakfast' && hour >= 6 && hour < 10) return true
  if (mealType === 'lunch' && hour >= 11 && hour < 14) return true
  if (mealType === 'dinner' && hour >= 17 && hour < 21) return true
  if (mealType === 'snack' && (hour < 6 || hour >= 21)) return true
  return false
}

// 选择餐次
const selectMealType = (meal) => {
  selectedMealType.value = meal
}

const switchTab = (tab) => {
  caloriesStore.setTab(tab)
  if (tab === 'record') {
    caloriesStore.fetchDailyCalories()
  } else if (tab === 'recipe') {
    caloriesStore.fetchRecipes()
  } else if (tab === 'analysis') {
    fetchLinkageAnalysis()
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

// 改变场景滤镜
const changeSceneFilter = (sceneValue) => {
  currentSceneFilter.value = sceneValue
  caloriesStore.setScene(sceneValue)
  caloriesStore.fetchRecipes()
}

// GI标签相关
const getGIBadgeClass = (giLevel) => {
  if (giLevel === 'low' || giLevel === 1) return 'gi-low'
  if (giLevel === 'medium' || giLevel === 2) return 'gi-medium'
  return 'gi-high'
}

const getGIBadgeIcon = (giLevel) => {
  if (giLevel === 'low' || giLevel === 1) return '🟢'
  if (giLevel === 'medium' || giLevel === 2) return '🟡'
  return '🔴'
}

const getGIBadgeText = (giLevel) => {
  if (giLevel === 'low' || giLevel === 1) return '放心吃'
  if (giLevel === 'medium' || giLevel === 2) return '适量吃'
  return '谨慎吃'
}

// 显示食谱详情
const showRecipeDetail = async (recipe) => {
  try {
    const detail = await caloriesApi.getRecipeDetail(recipe.id)
    // 可以打开详情弹窗或跳转详情页
    uni.showModal({
      title: recipe.name,
      content: `食材：${detail.data?.ingredients?.join('、') || '暂无'}\n${recipe.insulin_tip || ''}`,
      showCancel: false
    })
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

// 收藏/取消收藏
const toggleFavorite = async (recipe) => {
  try {
    await caloriesApi.toggleRecipeFavorite(recipe.id, {
      is_favorite: !recipe.is_favorite
    })
    recipe.is_favorite = !recipe.is_favorite
    uni.showToast({
      title: recipe.is_favorite ? '已收藏' : '已取消收藏',
      icon: 'success'
    })
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

// 发送给家属
const shareToFamily = async (recipe) => {
  try {
    await caloriesApi.shareRecipeToFamily(recipe.id, {})
    uni.showToast({ title: '已发送给家属', icon: 'success' })
  } catch (error) {
    console.error('分享失败:', error)
    uni.showToast({ title: '分享失败', icon: 'none' })
  }
}

// 获取关联分析数据
const fetchLinkageAnalysis = async () => {
  try {
    caloriesStore.initToday()
    const result = await caloriesApi.getLinkageAnalysis({
      date: selectedDate.value || new Date().toISOString().split('T')[0]
    })
    attributionData.value = result.data?.attributions || []
  } catch (error) {
    console.error('获取关联分析失败:', error)
  }
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

const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

// 拍照识别
const handlePhotoRecognize = async () => {
  try {
    uni.chooseImage({
      count: 1,
      sourceType: ['camera', 'album'],
      success: async (res) => {
        const tempFilePath = res.tempFilePaths[0]
        uni.showLoading({ title: '识别中...' })
        
        try {
          // 将图片转为base64或上传
          const fileSystemManager = uni.getFileSystemManager()
          const base64 = await new Promise((resolve, reject) => {
            fileSystemManager.readFile({
              filePath: tempFilePath,
              encoding: 'base64',
              success: (res) => resolve(res.data),
              fail: reject
            })
          })
          
          const result = await caloriesApi.recognizeFoodImage({
            image: base64,
            meal_type: selectedMealType.value.value
          })
          
          recognitionResult.value = {
            foods: (result.data?.foods || []).map(f => ({
              ...f,
              selected: true
            })),
            total_carbs: result.data?.total_carbs || 0
          }
          
          uni.hideLoading()
          uni.showToast({ title: '识别成功', icon: 'success' })
        } catch (error) {
          uni.hideLoading()
          console.error('识别失败:', error)
          uni.showToast({ title: '识别失败，请重试', icon: 'none' })
        }
      },
      fail: (err) => {
        console.error('选择图片失败:', err)
      }
    })
  } catch (error) {
    console.error('拍照识别错误:', error)
  }
}

// 条码扫描
const handleBarcodeScan = () => {
  uni.scanCode({
    success: async (res) => {
      try {
        uni.showLoading({ title: '识别中...' })
        const result = await caloriesApi.scanBarcode({
          barcode: res.result
        })
        
        if (result.data) {
          selectedFoodItems.value = [result.data]
          uni.hideLoading()
          uni.showToast({ title: '识别成功', icon: 'success' })
        }
      } catch (error) {
        uni.hideLoading()
        console.error('条码识别失败:', error)
        uni.showToast({ title: '识别失败', icon: 'none' })
      }
    },
    fail: (err) => {
      console.error('扫描失败:', err)
    }
  })
}

// 手动搜索
const handleManualSearch = () => {
  showManualForm.value = true
}

// 食物搜索
const handleFoodSearch = async (e) => {
  const keyword = e.detail.value
  if (!keyword || keyword.length < 1) {
    searchResults.value = []
    return
  }
  
  try {
    const result = await caloriesApi.searchFoods({ keyword })
    searchResults.value = result.data || []
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 选择食物项
const selectFoodItem = (item) => {
  selectedFoodItems.value = [item]
  foodName.value = item.name
  showManualForm.value = false
  searchResults.value = []
}

// 切换食物选择
const toggleFoodSelection = (food) => {
  food.selected = !food.selected
  updateRecognitionSummary()
}

// 更新识别结果汇总
const updateRecognitionSummary = () => {
  if (!recognitionResult.value) return
  const selected = recognitionResult.value.foods.filter(f => f.selected)
  recognitionResult.value.total_carbs = selected.reduce((sum, f) => sum + (f.carbs || 0), 0)
}

// 清除识别结果
const clearRecognitionResult = () => {
  recognitionResult.value = null
  selectedFoodItems.value = []
}

// 分量变化
const onPortionChange = (e) => {
  portionValue.value = e.detail.value
}

const portionText = computed(() => {
  if (portionValue.value < 50) return '半碗'
  if (portionValue.value < 150) return '大半碗'
  return '一碗'
})

// 选择进食感受
const selectFeeling = (feeling) => {
  currentFeeling.value = feeling
}

// 切换标签
const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag)
  }
}

// 提交记录（带参数）
const submitRecordWithParams = async () => {
  if (selectedFoodItems.value.length === 0 && !foodName.value && (!recognitionResult.value || recognitionResult.value.foods.filter(f => f.selected).length === 0)) {
    uni.showToast({ title: '请选择或输入食物', icon: 'none' })
    return
  }
  
  try {
    caloriesStore.initToday()
    const foods = recognitionResult.value?.foods.filter(f => f.selected) || selectedFoodItems.value || [{ name: foodName.value }]
    
    for (const food of foods) {
      await caloriesStore.addRecord({
        meal_type: selectedMealType.value.value,
        food_name: food.name || foodName.value,
        calories: food.calories || Number(calories.value) || 0,
        carbs_grams: food.carbs || 0,
        weight: food.weight || portionValue.value,
        feeling: currentFeeling.value,
        tags: selectedTags.value,
        scene: currentScene.value.value,
        source_type: recognitionResult.value ? 'ocr' : (selectedFoodItems.value.length > 0 ? 'barcode' : 'manual')
      })
    }
    
    // 清空表单
    clearRecognitionResult()
    foodName.value = ''
    calories.value = ''
    portionValue.value = 100
    currentFeeling.value = ''
    selectedTags.value = []
    showManualForm.value = false
    
    uni.showToast({ title: '记录已保存', icon: 'success' })
  } catch (error) {
    console.error('保存失败:', error)
    uni.showToast({ title: '保存失败，请重试', icon: 'none' })
  }
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
  // 根据当前时间自动选择餐次
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 10) {
    selectedMealType.value = mealTypeOptions.find(m => m.value === 'breakfast') || mealTypeOptions[0]
  } else if (hour >= 11 && hour < 14) {
    selectedMealType.value = mealTypeOptions.find(m => m.value === 'lunch') || mealTypeOptions[1]
  } else if (hour >= 17 && hour < 21) {
    selectedMealType.value = mealTypeOptions.find(m => m.value === 'dinner') || mealTypeOptions[2]
  } else {
    selectedMealType.value = mealTypeOptions.find(m => m.value === 'snack') || mealTypeOptions[3]
  }
  
  if (recipes.value.length === 0 && currentTab.value === 'recipe') {
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

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-calories {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 24rpx;
  padding-top: 0;
  padding-bottom: 120rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
  margin: -24rpx -24rpx 24rpx -24rpx;
  width: calc(100% + 48rpx);
  box-sizing: border-box;
}

.nav-back-icon {
  width: 64rpx;
  height: 64rpx;
  display: block;
  padding: 10rpx;
  cursor: pointer;
  z-index: 100;
  position: relative;
}

.nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.nav-placeholder {
  width: 64rpx;
}

/* 吉祥物卡片 */
.mascot-food-card {
  display: flex;
  gap: 20rpx;
  background: #FFFEF7;
  border-radius: 32rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
  border: 3rpx solid #E3C7A4;
}

.mascot-img-food {
  width: 120rpx;
  height: 120rpx;
  flex-shrink: 0;
}

.food-summary {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.summary-bubble {
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border: 2rpx solid #E3C7A4;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  position: relative;
}

.summary-bubble::before {
  content: '';
  position: absolute;
  left: -12rpx;
  top: 50%;
  transform: translateY(-50%);
  border-top: 10rpx solid transparent;
  border-bottom: 10rpx solid transparent;
  border-right: 12rpx solid #E3C7A4;
}

.bubble-text {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.5;
}

.energy-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.energy-label-child {
  font-size: 26rpx;
  color: #74362C;
}

.energy-value-row {
  display: flex;
  align-items: baseline;
  gap: 6rpx;
}

.energy-num {
  font-size: 48rpx;
  font-weight: bold;
  color: #C07240;
}

.energy-unit-child {
  font-size: 24rpx;
  color: #A85835;
}

/* 快速记录 */
.quick-record-child {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.record-header-child {
  margin-bottom: 20rpx;
}

.record-title-child {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.meal-buttons {
  display: flex;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.meal-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 12rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
  border: 2rpx solid #E3C7A4;
  transition: all 0.3s ease;
}

.meal-btn.active {
  background: linear-gradient(135deg, #D5A874 0%, #CB8E54 100%);
  border-color: #CB8E54;
}

.meal-icon {
  font-size: 32rpx;
}

.meal-name {
  font-size: 24rpx;
  color: #602F27;
}

.meal-btn.active .meal-name {
  color: white;
}

.food-input-area {
  display: flex;
  gap: 12rpx;
}

.food-input-child {
  flex: 1;
  height: 80rpx;
  background: #FAF6F0;
  border: 2rpx solid #E3C7A4;
  border-radius: 20rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  color: #602F27;
}

.add-btn-child {
  width: 80rpx;
  height: 80rpx;
  cursor: pointer;
}

/* 今日记录 */
.today-food-card {
  background: #FFFEF7;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.food-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.food-card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.food-count {
  font-size: 26rpx;
  color: #A85835;
}

.empty-food {
  text-align: center;
  padding: 40rpx 20rpx;
}

.empty-emoji-food {
  font-size: 60rpx;
  display: block;
  margin-bottom: 12rpx;
}

.empty-text-food {
  font-size: 26rpx;
  color: #74362C;
}

.food-list-child {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.food-item-child {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx;
  background: #FAF6F0;
  border-radius: 16rpx;
}

.food-meal-icon {
  font-size: 32rpx;
}

.food-name-child {
  flex: 1;
  font-size: 28rpx;
  color: #602F27;
}

.food-cal-child {
  font-size: 24rpx;
  color: #C07240;
  font-weight: 500;
}

/* 推荐卡片 */
.recommend-card-child {
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #D5A874;
}

.recommend-header {
  margin-bottom: 20rpx;
}

.recommend-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.recommend-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: white;
  border-radius: 16rpx;
}

.recommend-icon {
  font-size: 40rpx;
}

.recommend-info {
  flex: 1;
}

.recommend-name {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #74362C;
}

.recommend-tip {
  display: block;
  font-size: 24rpx;
  color: #8E422F;
}

/* 底部装饰 */
.child-cal-footer {
  display: flex;
  justify-content: center;
  gap: 48rpx;
  padding: 20rpx 0;
  opacity: 0.5;
}

.footer-deco {
  font-size: 48rpx;
  animation: float 3s ease-in-out infinite;
}

.footer-deco:nth-child(2) {
  animation-delay: 1s;
}

.footer-deco:nth-child(3) {
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16rpx); }
}

/* ========== 新增功能样式 ========== */

/* 餐次轴 */
.meal-time-axis {
  display: flex;
  justify-content: space-around;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 20rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.05);
}

.meal-time-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.meal-time-item.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #ffffff;
}

.meal-time-item.highlight {
  border: 2rpx solid #fbbf24;
  background: #fef3c7;
}

.meal-time-icon {
  font-size: 36rpx;
}

.meal-time-label {
  font-size: 24rpx;
}

.meal-time-item.active .meal-time-label {
  color: #ffffff;
  font-weight: 600;
}

/* 智能录入区 */
.smart-input-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.06);
}

.smart-input-header {
  margin-bottom: 20rpx;
}

.smart-input-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
  display: block;
  margin-bottom: 6rpx;
}

.smart-input-hint {
  font-size: 24rpx;
  color: #9ca3af;
}

.input-methods {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.photo-recognize-btn {
  width: 100%;
  height: 160rpx;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 10rpx 30rpx rgba(99, 102, 241, 0.35);
}

.photo-icon {
  font-size: 56rpx;
}

.photo-text {
  font-size: 28rpx;
  color: #ffffff;
  font-weight: 500;
}

.input-method-row {
  display: flex;
  gap: 16rpx;
}

.barcode-btn,
.search-btn {
  flex: 1;
  height: 100rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border: 2rpx solid #e5e7eb;
}

.method-icon {
  font-size: 36rpx;
}

.method-text {
  font-size: 24rpx;
  color: #4b5563;
}

/* 识别结果卡片 */
.recognition-result-card {
  margin-top: 20rpx;
  padding: 20rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  border: 2rpx solid #e5e7eb;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.result-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #111827;
}

.result-close {
  font-size: 32rpx;
  color: #9ca3af;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-foods {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.result-food-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 12rpx;
  background: #ffffff;
  border-radius: 12rpx;
  border: 2rpx solid #e5e7eb;
}

.result-food-item.selected {
  border-color: #6366f1;
  background: #eef2ff;
}

.food-check {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  background: #6366f1;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
}

.food-name {
  flex: 1;
  font-size: 26rpx;
  color: #111827;
}

.food-weight {
  font-size: 24rpx;
  color: #6b7280;
}

.result-summary {
  padding-top: 16rpx;
  border-top: 1rpx solid #e5e7eb;
}

.summary-text {
  font-size: 26rpx;
  color: #111827;
  font-weight: 500;
}

/* 手动搜索表单 */
.manual-form {
  margin-top: 20rpx;
}

.manual-input {
  width: 100%;
  height: 76rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  padding: 0 24rpx;
  font-size: 26rpx;
  border: 2rpx solid #e5e7eb;
}

.search-results {
  margin-top: 12rpx;
  max-height: 400rpx;
  overflow-y: auto;
}

.search-result-item {
  padding: 16rpx;
  background: #ffffff;
  border-radius: 12rpx;
  margin-bottom: 8rpx;
  border: 1rpx solid #e5e7eb;
}

.result-food-name {
  font-size: 26rpx;
  color: #111827;
  display: block;
  margin-bottom: 6rpx;
}

.result-food-info {
  font-size: 22rpx;
  color: #6b7280;
}

/* 辅助参数卡片 */
.auxiliary-params-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.06);
}

.params-header {
  margin-bottom: 20rpx;
}

.params-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.param-item {
  margin-bottom: 28rpx;
}

.param-label {
  font-size: 26rpx;
  color: #4b5563;
  display: block;
  margin-bottom: 16rpx;
}

.portion-slider-wrapper {
  margin-bottom: 12rpx;
}

.portion-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8rpx;
}

.portion-label {
  font-size: 22rpx;
  color: #9ca3af;
}

.portion-value {
  font-size: 24rpx;
  color: #6366f1;
  font-weight: 500;
}

.feeling-chips,
.tag-chips {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.feeling-chip,
.tag-chip {
  padding: 12rpx 20rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  border: 2rpx solid #e5e7eb;
  font-size: 24rpx;
  color: #4b5563;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.feeling-chip.active,
.tag-chip.active {
  background: #eef2ff;
  border-color: #6366f1;
  color: #6366f1;
}

.feeling-icon {
  font-size: 28rpx;
}

.save-record-btn {
  width: 100%;
  height: 84rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 500;
  margin-top: 20rpx;
  box-shadow: 0 10rpx 30rpx rgba(79, 70, 229, 0.35);
}

/* 场景滤镜 */
.scene-filter {
  margin-bottom: 20rpx;
}

.filter-label {
  font-size: 26rpx;
  color: #6b7280;
  display: block;
  margin-bottom: 12rpx;
}

.scene-filter-chips {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.scene-filter-chip {
  padding: 12rpx 24rpx;
  border-radius: 999rpx;
  background: #f3f4f6;
  border: 2rpx solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.scene-filter-chip.active {
  background: linear-gradient(135deg, #34d399, #22c55e);
  border-color: #22c55e;
  color: #ffffff;
}

.filter-icon {
  font-size: 24rpx;
}

.filter-text {
  font-size: 24rpx;
}

/* 食谱卡片增强 */
.recipe-gi-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
}

.recipe-gi-badge.gi-low {
  background: #dcfce7;
  color: #166534;
}

.recipe-gi-badge.gi-medium {
  background: #fef3c7;
  color: #92400e;
}

.recipe-gi-badge.gi-high {
  background: #fee2e2;
  color: #991b1b;
}

.gi-badge-icon {
  font-size: 20rpx;
}

.gi-badge-text {
  font-weight: 500;
}

.recipe-card {
  position: relative;
  padding: 20rpx;
  border-radius: 20rpx;
  background: #f9fafb;
  margin-bottom: 18rpx;
}

.recipe-nutrition {
  display: flex;
  gap: 16rpx;
  margin: 16rpx 0;
  flex-wrap: wrap;
}

.nutrition-item {
  flex: 1;
  min-width: 120rpx;
  padding: 12rpx;
  background: #ffffff;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.nutrition-label {
  font-size: 22rpx;
  color: #6b7280;
}

.nutrition-value {
  font-size: 24rpx;
  color: #111827;
  font-weight: 600;
}

.insulin-tip {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx;
  background: #eff6ff;
  border-radius: 12rpx;
  margin-top: 12rpx;
}

.insulin-icon {
  font-size: 24rpx;
}

.insulin-text {
  font-size: 24rpx;
  color: #1e40af;
}

.recipe-actions {
  display: flex;
  gap: 12rpx;
  margin-top: 16rpx;
}

.action-btn {
  flex: 1;
  padding: 12rpx;
  border-radius: 12rpx;
  background: #ffffff;
  border: 1rpx solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.action-icon {
  font-size: 24rpx;
}

.action-text {
  font-size: 22rpx;
  color: #4b5563;
}

/* 数据联动分析 */
.analysis-tab {
  padding-bottom: 40rpx;
}

.analysis-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 30rpx rgba(15, 23, 42, 0.05);
}

.chart-container {
  margin: 24rpx 0;
  height: 400rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.chart-label {
  font-size: 26rpx;
  color: #111827;
  font-weight: 500;
}

.chart-hint {
  font-size: 24rpx;
  color: #9ca3af;
}

.attribution-analysis {
  margin-top: 32rpx;
}

.analysis-header {
  margin-bottom: 20rpx;
}

.analysis-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #111827;
}

.empty-analysis {
  padding: 40rpx 0;
  text-align: center;
}

.attribution-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.attribution-item {
  padding: 16rpx;
  background: #f9fafb;
  border-radius: 12rpx;
  border-left: 4rpx solid #ef4444;
}

.attribution-time {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.time-text {
  font-size: 24rpx;
  color: #6b7280;
}

.glucose-value {
  font-size: 26rpx;
  font-weight: 600;
}

.glucose-value.high {
  color: #ef4444;
}

.attribution-reason {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
}

.reason-icon {
  font-size: 24rpx;
}

.reason-text {
  flex: 1;
  font-size: 24rpx;
  color: #4b5563;
  line-height: 1.5;
}
</style>


