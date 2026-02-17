<template>
  <view class="detail-page">
    <scroll-view class="content-scroll" scroll-y>
      <view class="article-header">
        <text class="topic-chip">{{ article.topic_label || '科普知识' }}</text>
        <text class="article-title">{{ article.title }}</text>
        <view class="article-meta">
          <text class="meta-text">⏱ {{ article.read_minutes || 3 }} 分钟阅读</text>
          <text v-if="article.reward_points" class="meta-text">✨ 完成可得 {{ article.reward_points }} 积分</text>
        </view>
      </view>

      <view class="key-points" v-if="article.key_points && article.key_points.length">
        <text class="section-title">本篇要点</text>
        <view class="point-item" v-for="(p, idx) in article.key_points" :key="idx">
          <text class="point-bullet">•</text>
          <text class="point-text">{{ p }}</text>
        </view>
      </view>

      <view class="article-body">
        <text
          v-for="(para, idx) in paragraphs"
          :key="idx"
          class="paragraph"
        >
          {{ para }}
        </text>
      </view>

      <view class="summary-card" v-if="article.summary">
        <text class="summary-title">小结</text>
        <text class="summary-text">{{ article.summary }}</text>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <view class="progress-hint">
        <text v-if="article.is_completed" class="progress-text done">
          已完成阅读，积分已发放
        </text>
        <text v-else class="progress-text">
          阅读完后点击按钮领取本篇积分奖励
        </text>
      </view>
      <button
        class="action-btn"
        :class="{ disabled: submitting || article.is_completed }"
        :disabled="submitting || article.is_completed"
        @tap="completeArticle"
      >
        <text v-if="article.is_completed">已完成</text>
        <text v-else>完成阅读并领取积分</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { knowledgeApi } from '@/api'

const articleId = ref(null)
const submitting = ref(false)

const article = reactive({
  id: null,
  title: '',
  summary: '',
  topic: '',
  topic_label: '',
  read_minutes: 3,
  reward_points: 0,
  content: '',
  key_points: [],
  is_completed: false
})

const mockDetail = {
  id: 1,
  title: '什么是低血糖？出现时该怎么办',
  summary: '低血糖并不可怕，关键是尽早发现，并学会向大人求助与正确补糖。',
  topic: 'basics',
  topic_label: '血糖基础',
  read_minutes: 3,
  reward_points: 5,
  is_completed: false,
  key_points: [
    '低血糖常见表现包括：手抖、出汗、肚子饿、脸色发白、头晕等。',
    '一旦怀疑低血糖，要立刻告诉家长或老师，不要一个人忍着。',
    '在大人指导下，可以喝含糖饮料或吃含糖食物，10-15 分钟后再复测血糖。'
  ],
  content:
    '低血糖是指血液中的葡萄糖水平过低，身体和大脑暂时“缺少燃料”。\n\n' +
    '很多孩子一开始只觉得有点累、想睡觉，或者突然心跳很快、出汗，这些都有可能是低血糖的信号。\n\n' +
    '遇到这些情况时，最重要的不是责怪自己，而是尽快告诉身边的大人，让他们帮你一起判断和处理。'
}

const paragraphs = ref([])

const normalizeDetail = (raw) => ({
  id: raw.id ?? raw.article_id,
  title: raw.title,
  summary: raw.summary || '',
  topic: raw.topic || '',
  topic_label: raw.topic_label || raw.topicName || '',
  read_minutes: raw.read_minutes || raw.duration || 3,
  reward_points: raw.reward_points ?? raw.points ?? 0,
  content: raw.content || '',
  key_points: raw.key_points || raw.keyPoints || [],
  is_completed: raw.is_completed ?? raw.is_read ?? false
})

const loadDetail = async () => {
  if (!articleId.value) return
  try {
    const res = await knowledgeApi.getArticleDetail(articleId.value)
    const raw = res?.data?.article ?? res?.article ?? res?.data ?? res
    const data = raw && raw.title ? normalizeDetail(raw) : mockDetail
    Object.assign(article, data)
  } catch (e) {
    console.warn('获取科普文章详情失败，使用本地示例：', e?.message || e)
    Object.assign(article, mockDetail)
  }

  const text = article.content && article.content.trim().length > 0 ? article.content : mockDetail.content
  paragraphs.value = text.split(/\n+/).filter((p) => p.trim().length > 0)
}

const completeArticle = async () => {
  if (!article.id || article.is_completed || submitting.value) return
  submitting.value = true
  try {
    const res = await knowledgeApi.completeArticle(article.id, {})
    const data = res?.data ?? res ?? {}
    const points = data.reward_points ?? data.points ?? article.reward_points ?? 0
    article.is_completed = true
    if (points > 0) {
      uni.showToast({
        title: `已完成阅读 +${points}积分`,
        icon: 'success'
      })
    } else {
      uni.showToast({
        title: '已记录阅读完成',
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

onLoad((options) => {
  articleId.value = options?.id || null
})

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.content-scroll {
  flex: 1;
  padding: 24rpx 24rpx 140rpx;
}

.article-header {
  margin-bottom: 24rpx;
}

.topic-chip {
  display: inline-flex;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  background: #ecfdf5;
  color: #16a34a;
  font-size: 22rpx;
  margin-bottom: 10rpx;
}

.article-title {
  display: block;
  font-size: 40rpx;
  font-weight: 800;
  color: #111827;
  line-height: 1.4;
}

.article-meta {
  margin-top: 10rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.meta-text {
  font-size: 24rpx;
  color: #6b7280;
}

.key-points {
  margin-bottom: 24rpx;
  margin-right: 45rpx;
  padding: 20rpx 18rpx;
  background: #eff6ff;
  border-radius: 18rpx;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #1f2937;
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
  color: #3b82f6;
  line-height: 1.6;
}

.point-text {
  flex: 1;
  font-size: 24rpx;
  color: #374151;
  line-height: 1.6;
}

.article-body {
  background: #ffffff;
  border-radius: 18rpx;
  margin-right: 45rpx;
  padding: 22rpx 18rpx;
  box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.05);
}

.paragraph {
  display: block;
  font-size: 26rpx;
  color: #111827;
  line-height: 1.7;
  margin-bottom: 18rpx;
}

.summary-card {
  margin-top: 22rpx;
  margin-right: 45rpx;
  padding: 20rpx 18rpx;
  background: #fef3c7;
  border-radius: 18rpx;
}

.summary-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: #92400e;
  margin-bottom: 8rpx;
}

.summary-text {
  display: block;
  font-size: 24rpx;
  color: #92400e;
  line-height: 1.7;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12rpx 24rpx 32rpx;
  background: linear-gradient(180deg, rgba(243, 244, 246, 0.9), #f3f4f6);
  box-shadow: 0 -4rpx 16rpx rgba(15, 23, 42, 0.08);
}

.progress-hint {
  margin-bottom: 10rpx;
}

.progress-text {
  font-size: 22rpx;
  color: #6b7280;
}

.progress-text.done {
  color: #16a34a;
}

.action-btn {
  width: 100%;
  height: 92rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.action-btn.disabled {
  background: #e5e7eb;
  color: #9ca3af;
}
</style>


