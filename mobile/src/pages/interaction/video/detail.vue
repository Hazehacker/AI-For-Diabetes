<template>
  <view class="detail-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">视频学习</text>
      <view class="nav-placeholder"></view>
    </view>
    
    <view class="video-wrapper">
      <!-- 这里使用原生 video 组件；实际 src 由后端返回 -->
      <video
        class="video-player"
        :src="video.play_url"
        :poster="video.cover"
        controls
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
      />
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <view class="video-header">
        <text class="topic-chip">{{ video.topic_label || '视频学习' }}</text>
        <text class="video-title">{{ video.title }}</text>
        <view class="video-meta">
          <text class="meta-text">🎥 {{ video.duration_minutes || 3 }} 分钟</text>
          <text
            v-if="video.reward_points"
            class="meta-text"
          >
            ✨ 完成可得 {{ video.reward_points }} 积分
          </text>
        </view>
      </view>

      <view
        class="key-points"
        v-if="video.key_points && video.key_points.length"
      >
        <text class="section-title">本集要点</text>
        <view
          class="point-item"
          v-for="(p, idx) in video.key_points"
          :key="idx"
        >
          <text class="point-bullet">•</text>
          <text class="point-text">{{ p }}</text>
        </view>
      </view>

      <view v-if="video.description" class="desc-card">
        <text class="section-title">简介</text>
        <text class="desc-text">{{ video.description }}</text>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <view class="progress-hint">
        <text
          v-if="video.is_completed"
          class="progress-text done"
        >
          已完成学习，积分已发放
        </text>
        <text v-else class="progress-text">
          建议完整看完本集，再点击按钮领取积分奖励
        </text>
      </view>
      <button
        class="action-btn"
        :class="{ disabled: submitting || video.is_completed }"
        :disabled="submitting || video.is_completed"
        @tap="completeVideo"
      >
        <text v-if="video.is_completed">已完成</text>
        <text v-else>完成本集并领取积分</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { videoApi } from '@/api'

const videoId = ref(null)
const submitting = ref(false)

const video = reactive({
  id: null,
  title: '',
  description: '',
  topic: '',
  topic_label: '',
  duration_minutes: 3,
  reward_points: 0,
  cover: '',
  play_url: '',
  key_points: [],
  is_completed: false
})

const mockDetail = {
  id: 1,
  title: '认识血糖：小朋友也能听懂的解释',
  description: '通过简单的动画，和孩子一起了解什么是血糖、为什么要检测血糖。',
  topic: 'basics',
  topic_label: '血糖基础',
  duration_minutes: 3,
  reward_points: 5,
  cover: '',
  play_url: '',
  is_completed: false,
  key_points: [
    '血糖就像身体的“能量小火车”，要保持不高也不太低。',
    '定期测量血糖，可以帮助家长和医生了解最近的控制情况。',
    '出现不舒服时，测一测血糖，比“猜”要安全得多。'
  ]
}

const normalizeDetail = (raw) => ({
  id: raw.id ?? raw.video_id,
  title: raw.title,
  description: raw.description || raw.brief || '',
  topic: raw.topic || '',
  topic_label: raw.topic_label || raw.topicName || '',
  duration_minutes: raw.duration_minutes || raw.duration || 3,
  reward_points: raw.reward_points ?? raw.points ?? 0,
  cover: raw.cover || raw.thumbnail || '',
  play_url: raw.play_url || raw.url || '',
  key_points: raw.key_points || raw.keyPoints || [],
  is_completed: raw.is_completed ?? raw.completed ?? false
})

const loadDetail = async () => {
  if (!videoId.value) return
  try {
    const res = await videoApi.getVideoDetail(videoId.value)
    const raw = res?.data?.video ?? res?.video ?? res?.data ?? res
    const data = raw && raw.title ? normalizeDetail(raw) : mockDetail
    Object.assign(video, data)
  } catch (e) {
    console.warn('获取视频详情失败，使用本地示例：', e?.message || e)
    Object.assign(video, mockDetail)
  }
}

const completeVideo = async () => {
  if (!video.id || video.is_completed || submitting.value) return
  submitting.value = true
  try {
    const res = await videoApi.completeVideo(video.id, {
      progress_percent: 100
    })
    const data = res?.data ?? res ?? {}
    const points = data.reward_points ?? data.points ?? video.reward_points ?? 0
    video.is_completed = true
    if (points > 0) {
      uni.showToast({
        title: `已完成学习 +${points}积分`,
        icon: 'success'
      })
    } else {
      uni.showToast({
        title: '已记录完成',
        icon: 'success'
      })
    }
  } catch (e) {
    uni.showToast({
      title: e?.message || '领取失败，请稍后重试',
      icon: 'none'
    })
  } finally {
    submitting.value = false
  }
}

const onTimeUpdate = (e) => {
  // 预留：将来可以在此上报中途进度，如 video.currentTime / duration
  // 这里先不调用接口，仅为后端预留字段
}

const onEnded = () => {
  // 可以在视频播放结束时自动触发完成逻辑（当前仍需用户点击按钮以与其他内容保持一致）
}

const goBack = () => {
  uni.navigateBack()
}

onLoad((options) => {
  videoId.value = options?.id || null
})

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding-bottom: 120rpx;
  width: 100%;
  box-sizing: border-box;
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

.video-wrapper {
  width: 100%;
  background: #000000;
}

.video-player {
  width: 100%;
  height: 420rpx;
  background: #000000;
}

.content-scroll {
  flex: 1;
  padding: 18rpx;
  padding-bottom: 160rpx;
  width: calc(100% - 36rpx);
  box-sizing: border-box;
}

.video-header {
  margin-bottom: 24rpx;
}

.topic-chip {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  color: #CB8E54;
  font-size: 22rpx;
  margin-bottom: 10rpx;
}

.video-title {
  display: block;
  font-size: 40rpx;
  font-weight: 800;
  color: #602F27;
  line-height: 1.4;
}

.video-meta {
  margin-top: 10rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.meta-text {
  font-size: 24rpx;
  color: #A85835;
}

.key-points {
  margin-bottom: 24rpx;
  padding: 20rpx;
  background: white;
  border-radius: 28rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
  width: 100%;
  box-sizing: border-box;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #602F27;
  margin-bottom: 10rpx;
}

.point-item {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
  margin-bottom: 6rpx;
}

.point-bullet {
  font-size: 26rpx;
  color: #CB8E54;
  line-height: 1.6;
}

.point-text {
  flex: 1;
  font-size: 24rpx;
  color: #A85835;
  line-height: 1.6;
}

.desc-card {
  padding: 20rpx;
  background: white;
  border-radius: 28rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
  width: 100%;
  box-sizing: border-box;
}

.desc-text {
  display: block;
  font-size: 24rpx;
  color: #602F27;
  line-height: 1.7;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12rpx 24rpx 32rpx;
  background: linear-gradient(180deg, rgba(255, 248, 231, 0.9), #FFFEF7);
  box-shadow: 0 -4rpx 16rpx rgba(203, 142, 84, 0.15);
}

.progress-hint {
  margin-bottom: 10rpx;
}

.progress-text {
  font-size: 22rpx;
  color: #A85835;
}

.progress-text.done {
  color: #CB8E54;
}

.action-btn {
  width: 100%;
  height: 92rpx;
  border-radius: 46rpx;
  background: #F6D387;
  color: #602F27;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874;
}

.action-btn:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.action-btn.disabled {
  background: #E5E7EB;
  color: #9CA3AF;
  border-color: #D1D5DB;
  box-shadow: 0 6rpx 0 #D1D5DB;
}
</style>


