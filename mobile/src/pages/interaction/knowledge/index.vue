<template>
  <view class="knowledge-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">科普小课堂</text>
      <view class="nav-placeholder"></view>
    </view>
    
    <!-- 头部 -->
    <view class="header" v-if="!isChildMode">
      <view class="header-text">
        <text class="subtitle">用 2-3 分钟，学一点血糖小知识</text>
      </view>
    </view>
    <view class="header-spacer" v-else></view>

    <!-- 主题标签 -->
    <view class="topic-tabs">
      <view
        v-for="t in topics"
        :key="t.value"
        class="tab-pill"
        :class="{ active: activeTopic === t.value }"
        @tap="changeTopic(t.value)"
      >
        <text class="tab-label">{{ t.label }}</text>
      </view>
    </view>

    <!-- 推荐卡片 -->
    <view v-if="featured" class="featured-card" @tap="openArticle(featured)">
      <view class="featured-tag">今日推荐</view>
      <text class="featured-title">{{ featured.title }}</text>
      <text class="featured-desc">{{ featured.summary }}</text>
      <view class="featured-meta">
        <text class="meta-item">📖 {{ featured.read_minutes || 3 }} 分钟</text>
        <text class="meta-item">✨ {{ featured.reward_points || 5 }} 积分</text>
      </view>
    </view>

    <!-- 列表 -->
    <scroll-view class="list-scroll" scroll-y>
      <view class="list">
        <view
          v-for="item in filteredArticles"
          :key="item.id"
          class="article-card"
          @tap="openArticle(item)"
        >
          <view class="card-main">
            <view class="card-title-row">
              <text class="article-title">{{ item.title }}</text>
              <text v-if="item.is_read" class="badge-read">已读</text>
            </view>
            <text class="article-summary">{{ item.summary }}</text>
            <view class="card-meta">
              <text class="meta-chip">{{ item.topic_label || '综合' }}</text>
              <text class="meta-text">⏱ {{ item.read_minutes || 3 }} 分钟</text>
              <text class="meta-text" v-if="item.reward_points">+{{ item.reward_points }} 积分</text>
            </view>
          </view>
        </view>

        <view v-if="!loading && filteredArticles.length === 0" class="empty">
          <text class="empty-text">该分类下暂时没有内容，可先看看其他主题～</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { knowledgeApi } from '@/api'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')

const state = reactive({
  loading: false,
  articles: []
})

const topics = [
  { value: 'all', label: '全部' },
  { value: 'basics', label: '血糖基础' },
  { value: 'diet', label: '饮食与碳水' },
  { value: 'exercise', label: '运动与低血糖' },
  { value: 'lifestyle', label: '生活小技巧' },
  { value: 'mood', label: '情绪与心理' }
]

const activeTopic = ref('all')

const normalizeArticle = (raw) => ({
  id: raw.id ?? raw.article_id,
  title: raw.title,
  summary: raw.summary || raw.brief || '',
  topic: raw.topic || 'basics',
  topic_label: raw.topic_label || raw.topicName,
  read_minutes: raw.read_minutes || raw.duration || 3,
  is_read: raw.is_read ?? raw.read ?? false,
  reward_points: raw.reward_points ?? raw.points ?? 0
})

const mockArticles = [
  {
    id: 1,
    title: '什么是低血糖？出现时该怎么办',
    summary: '认识低血糖的常见表现，学会向家长和老师求助。',
    topic: 'basics',
    topic_label: '血糖基础',
    read_minutes: 3,
    is_read: false,
    reward_points: 5
  },
  {
    id: 2,
    title: '一张图看懂「碳水化合物」',
    summary: '主食、水果、零食里的碳水，有什么不一样？',
    topic: 'diet',
    topic_label: '饮食与碳水',
    read_minutes: 2,
    is_read: false,
    reward_points: 5
  },
  {
    id: 3,
    title: '运动前后，血糖要注意什么？',
    summary: '运动前怎么准备小零食，运动后要不要加餐？',
    topic: 'exercise',
    topic_label: '运动与低血糖',
    read_minutes: 3,
    is_read: false,
    reward_points: 5
  }
]

const featured = computed(() => {
  if (!state.articles || state.articles.length === 0) return null
  return state.articles[0]
})

const filteredArticles = computed(() => {
  if (activeTopic.value === 'all') return state.articles
  return state.articles.filter((a) => a.topic === activeTopic.value)
})

const changeTopic = (val) => {
  activeTopic.value = val
}

const goBack = () => {
  uni.navigateBack({ delta: 1 })
}

const openArticle = (item) => {
  if (!item?.id) return
  uni.navigateTo({
    url: `/pages/interaction/knowledge/detail?id=${item.id}`
  })
}

const loadArticles = async () => {
  state.loading = true
  try {
    const res = await knowledgeApi.getArticles()
    const list = res?.data?.articles ?? res?.articles ?? res?.data ?? []
    if (Array.isArray(list) && list.length > 0) {
      state.articles = list.map(normalizeArticle)
    } else {
      state.articles = mockArticles
    }
  } catch (e) {
    console.warn('获取科普文章列表失败，使用本地示例：', e?.message || e)
    state.articles = mockArticles
  } finally {
    state.loading = false
  }
}

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
  padding-bottom: 40rpx;
  display: flex;
  flex-direction: column;
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

.header {
  padding: 24rpx;
}

.header-spacer {
  height: 20rpx;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #A85835;
}

.topic-tabs {
  margin: 0 24rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tab-pill {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: white;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5A874;
}

.tab-pill:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.tab-pill.active {
  background: #F6D387;
  border-color: #D5A874;
  box-shadow: 0 4rpx 0 #CB8E54;
}

.tab-label {
  font-size: 24rpx;
  color: #602F27;
  font-weight: 500;
}

.tab-pill.active .tab-label {
  color: #602F27;
  font-weight: 700;
}

.featured-card {
  margin: 18rpx 24rpx;
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.featured-tag {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #CB8E54;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  margin-bottom: 10rpx;
}

.featured-title {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #602F27;
}

.featured-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 26rpx;
  color: #A85835;
}

.featured-meta {
  margin-top: 14rpx;
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 24rpx;
  color: #CB8E54;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  padding: 6rpx 12rpx;
  border-radius: 14rpx;
}

.list-scroll {
  flex: 1;
  margin-top: 18rpx;
  padding: 0;
  padding-bottom: 40rpx;
}

.list {
  padding: 0 24rpx;
  padding-bottom: 40rpx;
}


.article-card {
  background: white;
  border-radius: 20rpx;
  padding: 22rpx 20rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(96, 47, 39, 0.06);
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.article-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #602F27;
}

.badge-read {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  color: #CB8E54;
}

.article-summary {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #A85835;
}

.card-meta {
  margin-top: 12rpx;
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
  align-items: center;
}

.meta-chip {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  color: #CB8E54;
}

.meta-text {
  font-size: 22rpx;
  color: #A85835;
}

.empty {
  padding: 32rpx 12rpx;
}

.empty-text {
  font-size: 24rpx;
  color: #9ca3af;
  text-align: center;
}
</style>


