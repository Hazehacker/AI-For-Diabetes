/**
 * 小游戏状态管理（配置缓存 / 历史记录 / 结果上报）
 */
import { defineStore } from 'pinia'
import { gamesApi } from '@/api'
import { useInteractionStore } from '@/store/interaction'

const STORAGE_KEYS = {
  gamesList: 'games_list_cache',
  configs: 'games_config_cache',
  historyPrefix: 'games_history_', // + game_id
  pending: 'games_pending_results'
}

function safeParse(json, fallback) {
  try {
    return JSON.parse(json)
  } catch (e) {
    return fallback
  }
}

function uuid() {
  // 简易UUID：足够用于 session_id 幂等
  const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1)
  return `${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`
}

export const useGamesStore = defineStore('games', {
  state: () => ({
    games: [],
    configs: {}, // game_id -> { version, ... }
    loading: false,
    lastError: '',
    pendingResults: [] // { game_id, payload, created_at }
  }),

  getters: {
    gameMap: (state) => {
      const map = {}
      state.games.forEach((g) => {
        map[g.game_id] = g
      })
      return map
    }
  },

  actions: {
    initFromCache() {
      const listCache = uni.getStorageSync(STORAGE_KEYS.gamesList)
      const cfgCache = uni.getStorageSync(STORAGE_KEYS.configs)
      const pending = uni.getStorageSync(STORAGE_KEYS.pending)

      if (listCache) this.games = safeParse(listCache, [])
      if (cfgCache) this.configs = safeParse(cfgCache, {})
      if (pending) this.pendingResults = safeParse(pending, [])

      // 如果缓存为空，填默认列表（离线可用）
      if (!this.games || this.games.length === 0) {
        this.games = this.getDefaultGames()
      }
    },

    getDefaultGames() {
      return [
        {
          game_id: 'runner',
          name: '糖值守护跑酷',
          cover: '',
          duration_hint: '2-3分钟',
          tags: ['反应', '饮食'],
          need_network: false,
          version: 'local'
        },
        {
          game_id: 'food_match',
          name: '食物拼拼乐',
          cover: '',
          duration_hint: '3分钟',
          tags: ['配对', '碳水'],
          need_network: false,
          version: 'local'
        }
      ]
    },

    async fetchGames(params = {}) {
      this.loading = true
      this.lastError = ''
      try {
        const res = await gamesApi.getGames(params)
        const list = res?.data?.games ?? res?.games ?? res?.data ?? []
        if (Array.isArray(list) && list.length > 0) {
          this.games = list
          uni.setStorageSync(STORAGE_KEYS.gamesList, JSON.stringify(this.games))
        } else if (!this.games || this.games.length === 0) {
          this.games = this.getDefaultGames()
        }
        return this.games
      } catch (e) {
        this.lastError = e?.message || '获取小游戏列表失败'
        if (!this.games || this.games.length === 0) {
          this.games = this.getDefaultGames()
        }
        return this.games
      } finally {
        this.loading = false
      }
    },

    getDefaultConfig(gameId) {
      if (gameId === 'runner') {
        return {
          game_id: 'runner',
          version: 'local',
          difficulty: { speed: 1.0, spawn_rate: 1.0 },
          hints: ['选择更健康的食物，血糖更稳哦', '运动前后记得关注身体感受'],
          foods: [
            { id: 'apple', type: 'good', emoji: '🍎', score: 10, delta: -2 },
            { id: 'broccoli', type: 'good', emoji: '🥦', score: 10, delta: -2 },
            { id: 'milk', type: 'good', emoji: '🥛', score: 8, delta: -1 },
            { id: 'cola', type: 'bad', emoji: '🥤', score: -5, delta: +6 },
            { id: 'candy', type: 'bad', emoji: '🍬', score: -5, delta: +6 },
            { id: 'fries', type: 'bad', emoji: '🍟', score: -4, delta: +4 },
            { id: 'trap', type: 'trap', emoji: '🕳️', score: 0, delta: 0 }
          ]
        }
      }

      if (gameId === 'food_match') {
        return {
          game_id: 'food_match',
          version: 'local',
          hints: ['学会看“碳水”更容易做出聪明选择', '不确定时可以问问家长/医生哦'],
          items: [
            { id: 'rice', name: '米饭', emoji: '🍚', carb: 'high' },
            { id: 'noodle', name: '面条', emoji: '🍜', carb: 'high' },
            { id: 'bread', name: '面包', emoji: '🍞', carb: 'high' },
            { id: 'banana', name: '香蕉', emoji: '🍌', carb: 'mid' },
            { id: 'apple', name: '苹果', emoji: '🍎', carb: 'mid' },
            { id: 'yogurt', name: '酸奶', emoji: '🥛', carb: 'mid' },
            { id: 'egg', name: '鸡蛋', emoji: '🥚', carb: 'low' },
            { id: 'fish', name: '鱼', emoji: '🐟', carb: 'low' },
            { id: 'broccoli', name: '西兰花', emoji: '🥦', carb: 'low' }
          ]
        }
      }

      return { game_id: gameId, version: 'local' }
    },

    async fetchConfig(gameId) {
      const cached = this.configs?.[gameId]
      const version = cached?.version
      try {
        const res = await gamesApi.getGameConfig(gameId, version ? { version } : {})
        const cfg = res?.data ?? res
        if (cfg && cfg.game_id) {
          this.configs[gameId] = cfg
          uni.setStorageSync(STORAGE_KEYS.configs, JSON.stringify(this.configs))
          return cfg
        }
        return cached || this.getDefaultConfig(gameId)
      } catch (e) {
        return cached || this.getDefaultConfig(gameId)
      }
    },

    getNewSessionId() {
      return uuid()
    },

    getLocalHistory(gameId) {
      const raw = uni.getStorageSync(`${STORAGE_KEYS.historyPrefix}${gameId}`)
      return raw ? safeParse(raw, []) : []
    },

    saveLocalHistory(gameId, record) {
      const list = this.getLocalHistory(gameId)
      list.unshift(record)
      uni.setStorageSync(`${STORAGE_KEYS.historyPrefix}${gameId}`, JSON.stringify(list.slice(0, 200)))
      return list
    },

    queuePending(gameId, payload) {
      this.pendingResults.push({ game_id: gameId, payload, created_at: Date.now() })
      uni.setStorageSync(STORAGE_KEYS.pending, JSON.stringify(this.pendingResults.slice(-200)))
    },

    async flushPending() {
      if (!this.pendingResults || this.pendingResults.length === 0) return
      const remain = []
      for (const item of this.pendingResults) {
        try {
          await gamesApi.submitGameResult(item.game_id, item.payload)
        } catch (e) {
          remain.push(item)
        }
      }
      this.pendingResults = remain
      uni.setStorageSync(STORAGE_KEYS.pending, JSON.stringify(remain))
    },

    /**
     * 上报成绩：优先走后端；失败则本地落库 + 入队重试
     * 返回统一结构：{ reward_points, new_badges, balance, hint }
     */
    async submitResult(gameId, result) {
      const payload = {
        session_id: result.session_id || this.getNewSessionId(),
        score: result.score || 0,
        duration: result.duration || 0,
        accuracy: result.accuracy,
        events: result.events,
        client_ts: new Date().toISOString()
      }

      // 先本地记录，避免用户感知丢失
      const localRecord = {
        session_id: payload.session_id,
        score: payload.score,
        duration: payload.duration,
        accuracy: payload.accuracy,
        created_at: new Date().toISOString(),
        reward_points: 0
      }
      this.saveLocalHistory(gameId, localRecord)

      try {
        const res = await gamesApi.submitGameResult(gameId, payload)
        const data = res?.data ?? res
        // 可选：用服务端奖励覆盖本地记录
        return data
      } catch (e) {
        // 离线奖励（本地策略）：按分数给少量积分
        const reward = Math.max(1, Math.min(30, Math.floor(payload.score / 200)))
        const hint = (this.configs?.[gameId]?.hints?.[0]) || '做得不错！记得选择更健康的食物哦～'

        // 更新本地记录奖励
        this.saveLocalHistory(gameId, { ...localRecord, reward_points: reward })

        // 互动页的积分展示（本地联动）
        try {
          const interaction = useInteractionStore()
          interaction.totalPoints += reward
        } catch (err) {
          // ignore
        }

        // 入队等待重试
        this.queuePending(gameId, payload)

        return {
          reward_points: reward,
          new_badges: [],
          balance: null,
          hint,
          offline: true
        }
      }
    }
  }
})


