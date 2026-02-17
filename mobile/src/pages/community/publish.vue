<template>
  <view class="publish-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="nav-title">发布动态</text>
      <view class="nav-publish-btn" @tap="publishPost">
        <text class="nav-publish-text">发布</text>
      </view>
    </view>

    <!-- 内容编辑区 -->
    <view class="content-area">
      <textarea
        v-model="content"
        class="content-input"
        placeholder="分享你的减肥心得、饮食记录或运动成果..."
        :maxlength="500"
        :auto-height="true"
      />
      <view class="char-count">{{ content.length }}/500</view>
    </view>

    <!-- 图片上传区 -->
    <view class="images-section">
      <view class="images-grid">
        <view 
          v-for="(img, index) in images" 
          :key="index"
          class="image-item"
        >
          <image :src="img" class="preview-image" mode="aspectFill" />
          <view class="delete-btn" @tap="deleteImage(index)">
            <text class="delete-icon">×</text>
          </view>
        </view>
        
        <view v-if="images.length < 9" class="add-image-btn" @tap="chooseImage">
          <text class="add-icon">+</text>
          <text class="add-text">添加图片</text>
        </view>
      </view>
    </view>

    <!-- 分类选择 -->
    <view class="category-section">
      <view class="section-title">选择分类</view>
      <view class="category-list">
        <view 
          v-for="cat in categories" 
          :key="cat.id"
          class="category-option"
          :class="{ selected: selectedCategory === cat.id }"
          @tap="selectCategory(cat.id)"
        >
          <text class="category-icon">{{ cat.icon }}</text>
          <text class="category-name">{{ cat.name }}</text>
        </view>
      </view>
    </view>

    <!-- 其他选项 -->
    <view class="options-section">
      <view class="option-item" @tap="toggleLocation">
        <text class="option-icon">📍</text>
        <text class="option-text">添加位置</text>
        <text v-if="location" class="option-value">{{ location }}</text>
      </view>
      
      <view class="option-item" @tap="toggleTopic">
        <text class="option-icon">#</text>
        <text class="option-text">添加话题</text>
        <text v-if="topic" class="option-value">{{ topic }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useCompanionStore } from '@/store/companion'

const companionStore = useCompanionStore()

// 表单数据
const content = ref('')
const images = ref([])
const selectedCategory = ref(1) // 默认选择第一个分类
const location = ref('')
const topic = ref('')

// 分类列表
const categories = ref([
  { id: 1, name: '每日打卡', icon: '📅' },
  { id: 2, name: '减肥成绩单', icon: '💪' },
  { id: 3, name: '减肥求助', icon: '🤝' },
  { id: 4, name: 'GLP减重', icon: '💉' },
  { id: 5, name: '减肥杂谈', icon: '💊' }
])

// 返回
const goBack = () => {
  if (content.value || images.value.length > 0) {
    uni.showModal({
      title: '提示',
      content: '确定要放弃编辑吗？',
      success: (res) => {
        if (res.confirm) {
          uni.navigateBack()
        }
      }
    })
  } else {
    uni.navigateBack()
  }
}

// 选择图片
const chooseImage = () => {
  uni.chooseImage({
    count: 9 - images.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      images.value = [...images.value, ...res.tempFilePaths]
    }
  })
}

// 删除图片
const deleteImage = (index) => {
  images.value.splice(index, 1)
}

// 选择分类
const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId
}

// 添加位置
const toggleLocation = () => {
  uni.showToast({
    title: '位置功能开发中',
    icon: 'none'
  })
}

// 添加话题
const toggleTopic = () => {
  uni.showToast({
    title: '话题功能开发中',
    icon: 'none'
  })
}

// 发布动态
const publishPost = () => {
  if (!content.value.trim()) {
    uni.showToast({
      title: '请输入内容',
      icon: 'none'
    })
    return
  }

  if (!selectedCategory.value) {
    uni.showToast({
      title: '请选择分类',
      icon: 'none'
    })
    return
  }

  // 构建帖子数据
  const postData = {
    content: content.value,
    images: images.value,
    categoryId: selectedCategory.value,
    location: location.value,
    topic: topic.value
  }

  // 调用store方法发布
  companionStore.addPost(postData)

  uni.showToast({
    title: '发布成功',
    icon: 'success'
  })

  setTimeout(() => {
    uni.navigateBack()
  }, 1500)
}
</script>

<style scoped>
.publish-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
}

/* 导航栏 */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.nav-back-icon {
  width: 80rpx;
  height: 80rpx;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.nav-publish-btn {
  min-width: 120rpx;
  height: 60rpx;
  padding: 0 24rpx;
  background: rgba(246, 211, 135, 0.8);
  backdrop-filter: blur(20rpx);
  -webkit-backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 8rpx 32rpx rgba(203, 142, 84, 0.2),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
}

.nav-publish-text {
  font-size: 28rpx;
  color: #602F27;
  font-weight: 500;
}

/* 内容编辑区 */
.content-area {
  background: #FFFEF7;
  padding: 32rpx;
  margin: 16rpx 20rpx;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.content-input {
  width: 100%;
  min-height: 300rpx;
  font-size: 30rpx;
  line-height: 1.6;
  color: #1F2937;
}

.char-count {
  text-align: right;
  font-size: 24rpx;
  color: #9CA3AF;
  margin-top: 16rpx;
}

/* 图片上传区 */
.images-section {
  background: #FFFEF7;
  padding: 32rpx;
  margin: 16rpx 20rpx;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.image-item {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
}

.preview-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 12rpx;
}

.delete-btn {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 40rpx;
  height: 40rpx;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-icon {
  color: white;
  font-size: 32rpx;
  line-height: 1;
}

.add-image-btn {
  width: 100%;
  padding-bottom: 100%;
  position: relative;
  background: #F3F4F6;
  border-radius: 12rpx;
  border: 2rpx dashed #D1D5DB;
}

.add-image-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.add-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -70%);
  font-size: 56rpx;
  color: #9CA3AF;
}

.add-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, 30%);
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 分类选择 */
.category-section {
  background: #FFFEF7;
  padding: 32rpx;
  margin: 16rpx 20rpx;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2937;
  margin-bottom: 24rpx;
}

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 24rpx;
  background: #F3F4F6;
  border-radius: 24rpx;
  border: 2rpx solid transparent;
}

.category-option.selected {
  background: #FEF7ED;
  border-color: #CB8E54;
}

.category-icon {
  font-size: 32rpx;
}

.category-name {
  font-size: 26rpx;
  color: #374151;
}

.category-option.selected .category-name {
  color: #CB8E54;
  font-weight: 500;
}

/* 其他选项 */
.options-section {
  background: #FFFEF7;
  padding: 0 32rpx;
  margin: 16rpx 20rpx;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.08);
}

.option-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 32rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
}

.option-item:last-child {
  border-bottom: none;
}

.option-icon {
  font-size: 36rpx;
}

.option-text {
  flex: 1;
  font-size: 28rpx;
  color: #374151;
}

.option-value {
  font-size: 26rpx;
  color: #CB8E54;
}
</style>
