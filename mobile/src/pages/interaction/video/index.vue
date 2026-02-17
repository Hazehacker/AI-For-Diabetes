<template>
  <view class="video-page">
    <!-- 头部 -->
    <view class="header">
      <view class="header-text">
        <text class="title">视频小课堂</text>
        <text class="subtitle">看一小会视频，学一大点知识</text>
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
              <view class="small-progress">
                <view
                  class="small-progress-inner"
                  :style="{ width: (item.progress_percent || 0) + '%' }"
                />
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
  background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 26%, #f3f4f6 26%);
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
  color: #e0f2fe;
}

.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: rgba(224, 242, 254, 0.9);
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
  background: rgba(224, 242, 254, 0.2);
}

.tab-pill.active {
  background: #e0f2fe;
}

.tab-label {
  font-size: 24rpx;
  color: #e0f2fe;
}

.tab-pill.active .tab-label {
  color: #0369a1;
  font-weight: 600;
}

.summary-card {
  margin-top: 18rpx;
  background: rgba(15, 23, 42, 0.75);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
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
  color: #e0f2fe;
}

.summary-label {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  color: #bae6fd;
}

.featured-card {
  margin-top: 18rpx;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 32rpx rgba(8, 47, 73, 0.22);
}

.featured-tag {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #0369a1;
  background: rgba(56, 189, 248, 0.16);
  margin-bottom: 10rpx;
}

.featured-title {
  display: block;
  font-size: 34rpx;
  font-weight: 800;
  color: #0f172a;
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
  color: #0f172a;
  background: rgba(8, 47, 73, 0.06);
  padding: 6rpx 12rpx;
  border-radius: 14rpx;
}

.progress-bar {
  margin-top: 16rpx;
  width: 100%;
  height: 10rpx;
  border-radius: 999rpx;
  background: #e5e7eb;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #38bdf8, #22c55e);
}

.list-scroll {
  margin-top: 18rpx;
  max-height: calc(100vh - 360rpx);
}

.list {
  padding-bottom: 40rpx;
}

.video-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 18rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.06);
}

.card-main {
  display: flex;
  gap: 16rpx;
}

.thumb {
  width: 260rpx;
  height: 160rpx;
  border-radius: 18rpx;
  overflow: hidden;
  position: relative;
}

.thumb-image {
  width: 100%;
  height: 100%;
}

.thumb-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.25), rgba(15, 23, 42, 0.5));
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon {
  font-size: 40rpx;
  color: #f9fafb;
}

.duration-chip {
  position: absolute;
  right: 10rpx;
  bottom: 8rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: rgba(15, 23, 42, 0.8);
}

.duration-text {
  font-size: 22rpx;
  color: #f9fafb;
}

.info {
  flex: 1;
  min-width: 0;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.video-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #111827;
}

.badge-completed {
  font-size: 22rpx;
  padding: 4rpx 10rpx;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #16a34a;
}

.video-summary {
  display: block;
  margin-top: 6rpx;
  font-size: 24rpx;
  color: #6b7280;
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
  background: #eff6ff;
  color: #2563eb;
}

.meta-text {
  font-size: 22rpx;
  color: #6b7280;
}

.small-progress {
  margin-top: 8rpx;
  width: 100%;
  height: 8rpx;
  border-radius: 999rpx;
  background: #e5e7eb;
  overflow: hidden;
}

.small-progress-inner {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #38bdf8, #22c55e);
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


