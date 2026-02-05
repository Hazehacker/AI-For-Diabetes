<template>
  <view class="knowledge-page">
    <!-- 头部 -->
    <view class="header">
      <view class="header-text">
        <text class="title">科普小课堂</text>
        <text class="subtitle">用 2-3 分钟，学一点血糖小知识</text>
      </view>
    </view>

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
  background: linear-gradient(180deg, #22c55e 0%, #16a34a 26%, #F3F4F6 26%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.header {
  padding: 24rpx 8rpx 12rpx;
}

.title {
  display: block;
  font-size: 44rpx;
  font-weight: 800;
  color: #ecfdf5;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: rgba(240, 253, 250, 0.9);
}

.topic-tabs {
  margin-top: 8rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tab-pill {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(240, 253, 250, 0.2);
}

.tab-pill.active {
  background: #ecfdf5;
}

.tab-label {
  font-size: 24rpx;
  color: #ecfdf5;
}

.tab-pill.active .tab-label {
  color: #16a34a;
  font-weight: 600;
}

.featured-card {
  margin-top: 18rpx;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 32rpx rgba(22, 163, 74, 0.22);
}

.featured-tag {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #16a34a;
  background: rgba(22, 163, 74, 0.12);
  margin-bottom: 10rpx;
}

.featured-title {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #022c22;
}

.featured-desc {
  display: block;
  margin-top: 6rpx;
  font-size: 26rpx;
  color: #4b5563;
}

.featured-meta {
  margin-top: 14rpx;
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 24rpx;
  color: #065f46;
  background: rgba(5, 150, 105, 0.06);
  padding: 6rpx 12rpx;
  border-radius: 14rpx;
}

.list-scroll {
  margin-top: 18rpx;
  max-height: calc(100vh - 320rpx);
}

.list {
  padding-bottom: 40rpx;
}

.article-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 22rpx 20rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.06);
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
  color: #111827;
}

.badge-read {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #16a34a;
}

.article-summary {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #6b7280;
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
  background: #eff6ff;
  color: #2563eb;
}

.meta-text {
  font-size: 22rpx;
  color: #6b7280;
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


