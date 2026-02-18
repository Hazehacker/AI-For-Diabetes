/**
 * 热量记录与食谱推荐状态管理
 * 功能：记录饮食、推荐食谱、关联血糖/胰岛素等数据做饮食决策
 */
import { defineStore } from 'pinia'
import { caloriesApi } from '@/api'

export const useCaloriesStore = defineStore('calories', {
  state: () => ({
    // 当前 Tab：record-热量记录，recipe-食谱推荐，analysis-数据联动
    currentTab: 'record',

    // 当前选中的日期（字符串：YYYY-MM-DD）
    selectedDate: '',

    // 当日热量统计
    dailySummary: {
      total_calories: 0,
      target_min: 0,
      target_max: 0,
      carbs_grams: 0,
      protein_grams: 0,
      fat_grams: 0,
      status_text: '还没有记录，快来添加今天的第一顿吧～'
    },

    // 当日饮食记录列表
    records: [],

    // 推荐食谱列表
    recipes: [],

    // 当前推荐场景：school / home / outing
    scene: 'home',

    // 加载状态
    loadingSummary: false,
    loadingRecipes: false
  }),

  getters: {
    /**
     * 是否已超出目标区间
     */
    isOverTarget: (state) => {
      if (!state.dailySummary?.target_max) return false
      return state.dailySummary.total_calories > state.dailySummary.target_max
    },

    /**
     * 按餐次分组的记录
     */
    recordsByMeal: (state) => {
      const groups = {
        breakfast: [],
        lunch: [],
        dinner: [],
        snack: []
      }
      state.records.forEach((r) => {
        const key = r.meal_type || 'snack'
        if (!groups[key]) groups[key] = []
        groups[key].push(r)
      })
      return groups
    }
  },

  actions: {
    setTab(tab) {
      this.currentTab = tab
    },

    setScene(scene) {
      this.scene = scene
    },

    /**
     * 初始化日期为今天
     */
    initToday() {
      if (this.selectedDate) return
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      const d = String(now.getDate()).padStart(2, '0')
      this.selectedDate = `${y}-${m}-${d}`
    },

    /**
     * 切换日期（相对天数偏移）
     */
    shiftDate(days) {
      if (!this.selectedDate) {
        this.initToday()
      }
      const current = new Date(this.selectedDate)
      current.setDate(current.getDate() + days)
      const y = current.getFullYear()
      const m = String(current.getMonth() + 1).padStart(2, '0')
      const d = String(current.getDate()).padStart(2, '0')
      this.selectedDate = `${y}-${m}-${d}`
      this.fetchDailyCalories()
    },

    /**
     * 从后端获取当日热量统计 + 记录
     */
    async fetchDailyCalories() {
      try {
        this.loadingSummary = true
        this.initToday()
        const res = await caloriesApi.getDailySummary({
          date: this.selectedDate
        })

        // 允许后端返回 { data: { summary, records } } 或直接 { summary, records }
        const payload = res?.data || res || {}
        this.dailySummary = {
          ...this.dailySummary,
          ...(payload.summary || {})
        }
        this.records = Array.isArray(payload.records) ? payload.records : []
      } catch (error) {
        console.error('获取热量统计失败:', error)
        // 失败时给出一个温和的提示文案，但不打断流程
        uni.showToast({
          title: '暂时获取不到热量数据',
          icon: 'none'
        })
      } finally {
        this.loadingSummary = false
      }
    },

    /**
     * 新增一条饮食记录
     */
    async addRecord(record) {
      // record: { meal_type, food_name, calories, carbs_grams, scene, remark }
      try {
        const payload = {
          ...record,
          date: this.selectedDate
        }
        const res = await caloriesApi.createRecord(payload)
        const saved = res?.data || payload
        if (!saved.id) {
          saved.id = Date.now()
        }
        this.records.unshift(saved)

        // 更新统计（简单累加，本地兜底；后端也会在下次刷新时返回准确值）
        const addCalories = Number(saved.calories) || 0
        this.dailySummary.total_calories += addCalories

        uni.showToast({
          title: '已添加到今日饮食',
          icon: 'success'
        })
      } catch (error) {
        console.error('添加饮食记录失败:', error)
        uni.showToast({
          title: '添加失败，请稍后重试',
          icon: 'none'
        })
      }
    },

    /**
     * 拉取推荐食谱
     */
    async fetchRecipes(context = {}) {
      try {
        this.loadingRecipes = true
        this.initToday()
        const res = await caloriesApi.getRecipeRecommendations({
          date: this.selectedDate,
          scene: this.scene,
          ...context
        })

        const list = res?.data || res || []
        this.recipes = Array.isArray(list) ? list : []
      } catch (error) {
        console.error('获取食谱推荐失败:', error)
        uni.showToast({
          title: '暂时获取不到推荐食谱',
          icon: 'none'
        })
      } finally {
        this.loadingRecipes = false
      }
    }
  }
})


