<template>
  <view class="video-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">视频小课堂</text>
      <view class="nav-placeholder"></view>
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

    <!-- 学习概览 -->
    <view v-if="summary" class="summary-card">
      <view class="summary-row">
        <view class="summary-item">
          <text class="summary-value">{{ summary.total_completed || 0 }}</text>
          <text class="summary-label">已看完</text>
        </view>
        <view class="summary-item">
          <text class="summary-value">{{ summary.total_minutes || 0 }}</text>
          <text class="summary-label">累计分钟</text>
        </view>
        <view class="summary-item">
          <text class="summary-value">{{ summary.total_points || 0 }}</text>
          <text class="summary-label">累计积分</text>
        </view>
      </view>
    </view>

    <!-- 推荐视频 -->
    <view
      v-if="featured"
      class="featured-card"
      @tap="openVideo(featured)"
    >
      <view class="featured-tag">今日推荐</view>
      <text class="featured-title">{{ featured.title }}</text>
      <text class="featured-desc">{{ featured.summary }}</text>
      <view class="featured-meta">
        <text class="meta-item">🎥 {{ featured.duration_minutes || 3 }} 分钟</text>
        <text class="meta-item" v-if="featured.reward_points">✨ {{ featured.reward_points }} 积分</text>
      </view>
      <view class="progress-bar">
        <view
          class="progress-inner"
          :style="{ width: (featured.progress_percent || 0) + '%' }"
        />
      </view>
    </view>

    <!-- 列表 -->
    <scroll-view class="list-scroll" scroll-y>
      <view class="list">
        <view
          v-for="item in filteredVideos"
          :key="item.id"
          class="video-card"
          @tap="openVideo(item)"
        >
          <view class="card-main">
            <view class="thumb">
              <image
                class="thumb-image"
                :src="item.cover || defaultCover"
                mode="aspectFill"
              />
              <view class="thumb-overlay">
                <text class="play-icon">▶</text>
              </view>
              <view class="duration-chip">
                <text class="duration-text">{{ item.duration_minutes || 3 }} 分钟</text>
              </view>
            </view>

            <view class="info">
              <view class="card-title-row">
                <text class="video-title">{{ item.title }}</text>
                <text v-if="item.is_completed" class="badge-completed">已完成</text>
              </view>
              <text class="video-summary">{{ item.summary }}</text>
              <view class="card-meta">
                <text class="meta-chip">{{ item.topic_label || '综合' }}</text>
                <text class="meta-text" v-if="item.reward_points">+{{ item.reward_points }} 积分</text>
              </view>
            </view>
          </view>
        </view>

        <view
          v-if="!loading && filteredVideos.length === 0"
          class="empty"
        >
          <text class="empty-text">该分类下暂时没有视频，可以先看看其他主题～</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { videoApi } from '@/api'

const state = reactive({
  loading: false,
  videos: [],
  summary: null
})

const topics = [
  { value: 'all', label: '全部' },
  { value: 'basics', label: '血糖基础' },
  { value: 'diet', label: '饮食与碳水' },
  { value: 'exercise', label: '运动与低血糖' },
  { value: 'lifestyle', label: '生活小技巧' }
]

const activeTopic = ref('all')
const defaultCover =
  'https://dummyimage.com/600x400/22c55e/ffffff.png&text=%E8%A7%86%E9%A2%91%E5%B0%8F%E8%AF%BE%E5%A0%82'

const normalizeVideo = (raw) => ({
  id: raw.id ?? raw.video_id,
  title: raw.title,
  summary: raw.summary || raw.brief || '',
  topic: raw.topic || 'basics',
  topic_label: raw.topic_label || raw.topicName,
  duration_minutes: raw.duration_minutes || raw.duration || 3,
  cover: raw.cover || raw.thumbnail,
  reward_points: raw.reward_points ?? raw.points ?? 0,
  is_completed: raw.is_completed ?? raw.completed ?? false,
  progress_percent: raw.progress_percent ?? raw.progress ?? 0
})

const mockVideos = [
  {
    id: 1,
    title: '认识血糖：小朋友也能听懂的解释',
    summary: '用动画讲讲什么是血糖，为什么要关注它。',
    topic: 'basics',
    topic_label: '血糖基础',
    duration_minutes: 3,
    reward_points: 5,
    is_completed: false,
    progress_percent: 0
  },
  {
    id: 2,
    title: '一顿饭里的「碳水」有多少？',
    summary: '带着孩子一起数一数，饭菜里的碳水化合物。',
    topic: 'diet',
    topic_label: '饮食与碳水',
    duration_minutes: 4,
    reward_points: 5,
    is_completed: false,
    progress_percent: 0
  }
]

const featured = computed(() => {
  if (!state.videos || state.videos.length === 0) return null
  return state.videos[0]
})

const filteredVideos = computed(() => {
  if (activeTopic.value === 'all') return state.videos
  return state.videos.filter((v) => v.topic === activeTopic.value)
})

const summary = computed(() => state.summary)

const changeTopic = (val) => {
  activeTopic.value = val
}

const goBack = () => {
  uni.navigateBack()
}

const openVideo = (item) => {
  if (!item?.id) return
  uni.navigateTo({
    url: `/pages/interaction/video/detail?id=${item.id}`
  })
}

const loadVideos = async () => {
  state.loading = true
  try {
    const res = await videoApi.getVideos()
    const list = res?.data?.videos ?? res?.videos ?? res?.data ?? []
    if (Array.isArray(list) && list.length > 0) {
      state.videos = list.map(normalizeVideo)
    } else {
      state.videos = mockVideos
    }
  } catch (e) {
    console.warn('获取视频列表失败，使用本地示例：', e?.message || e)
    state.videos = mockVideos
  } finally {
    state.loading = false
  }
}

const loadSummary = async () => {
  try {
    const res = await videoApi.getSummary()
    const raw = res?.data ?? res ?? null
    state.summary = raw
  } catch (e) {
    console.warn('获取视频学习概览失败：', e?.message || e)
  }
}

onMounted(() => {
  loadVideos()
  loadSummary()
})
</script>

<style scoped>
.video-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
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
}

.nav-back-icon {
  width: 64rpx;
  height: 64rpx;
  display: block;
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

.subtitle {
  display: block;
  font-size: 26rpx;
  color: #A85835;
}

.topic-tabs {
  margin: 24rpx 24rpx 0 24rpx;
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

.summary-card {
  margin: 18rpx 24rpx;
  background: white;
  border-radius: 28rpx;
  padding: 20rpx 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.summary-row {
  display: flex;
  justify-content: space-between;
}

.summary-item {
  flex: 1;
  align-items: center;
  text-align: center;
}

.summary-value {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #CB8E54;
}

.summary-label {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  color: #A85835;
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

.progress-bar {
  margin-top: 16rpx;
  width: 100%;
  height: 10rpx;
  border-radius: 999rpx;
  background: #E3C7A4;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #F6D387, #CB8E54);
}

.list-scroll {
  margin-top: 18rpx;
  max-height: calc(100vh - 360rpx);
  padding: 0;
}

.list {
  padding-bottom: 40rpx;
}

.video-card {
  background: white;
  border-radius: 20rpx;
  padding: 18rpx;
  margin: 0 24rpx 16rpx 24rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(96, 47, 39, 0.06);
  width: calc(100% - 48rpx);
  box-sizing: border-box;
}

.card-main {
  display: flex;
  gap: 16rpx;
  width: 100%;
  box-sizing: border-box;
}

.thumb {
  width: 200rpx;
  height: 160rpx;
  border-radius: 18rpx;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.thumb-image {
  width: 100%;
  height: 100%;
}

.thumb-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(96, 47, 39, 0.25), rgba(96, 47, 39, 0.5));
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon {
  font-size: 40rpx;
  color: white;
}

.duration-chip {
  position: absolute;
  right: 10rpx;
  bottom: 8rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: rgba(96, 47, 39, 0.8);
}

.duration-text {
  font-size: 22rpx;
  color: white;
}

.info {
  flex: 1;
  min-width: 0;
  min-height: 160rpx;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  overflow: hidden;
  width: calc(100% - 216rpx);
}

.card-title-row {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
}

.video-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #602F27;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-word;
}

.badge-completed {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  color: #CB8E54;
}

.video-summary {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #A85835;
  line-height: 1.4;
  word-break: break-word;
}

.card-meta {
  margin-top: 10rpx;
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

.small-progress {
  margin-top: 8rpx;
  width: 100%;
  height: 8rpx;
  border-radius: 999rpx;
  background: #E3C7A4;
  overflow: hidden;
}

.small-progress-inner {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #F6D387, #CB8E54);
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


