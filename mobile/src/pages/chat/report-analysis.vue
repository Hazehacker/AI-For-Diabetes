<template>
  <view class="report-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">报告解读</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 上传区域 -->
    <view class="upload-section">
      <view class="upload-card" @tap="chooseImage">
        <view v-if="!imageUrl" class="upload-placeholder">
          <text class="upload-icon">📷</text>
          <text class="upload-text">点击上传报告图片</text>
          <text class="upload-hint">支持拍照或从相册选择</text>
        </view>
        <view v-else class="image-preview">
          <image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
          <view class="image-actions">
            <view class="action-btn reselect-btn" @tap.stop="chooseImage">
              <text>重新选择</text>
            </view>
            <view class="action-btn delete-btn" @tap.stop="deleteImage">
              <text>删除</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 分析按钮 -->
    <view class="analyze-section">
      <button 
        class="analyze-btn" 
        :class="{ disabled: !imageUrl || analyzing }"
        :disabled="!imageUrl || analyzing"
        @tap="analyzeReport"
      >
        <text v-if="analyzing" class="btn-loading">分析中...</text>
        <text v-else>🔍 开始分析</text>
      </button>
    </view>

    <!-- 分析结果 -->
    <view v-if="analysisResult" class="result-section">
      <view class="result-card">
        <view class="result-header">
          <text class="result-icon">📋</text>
          <text class="result-title">分析结果</text>
        </view>
        <view class="result-content">
          <text class="result-text">{{ analysisResult }}</text>
        </view>
      </view>
    </view>

    <!-- 使用提示 -->
    <view class="tips-section">
      <view class="tips-card">
        <text class="tips-title">📌 使用提示</text>
        <view class="tips-list">
          <text class="tip-item">• 支持血糖检测报告、糖化血红蛋白报告等</text>
          <text class="tip-item">• 请确保图片清晰，文字可辨认</text>
          <text class="tip-item">• AI解读仅供参考，不代替医生诊断</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const imageUrl = ref('')
const analyzing = ref(false)
const analysisResult = ref('')

const goBack = () => {
  uni.navigateBack()
}

const chooseImage = () => {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择'],
    success: (res) => {
      const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
      uni.chooseImage({
        count: 1,
        sourceType,
        success: (result) => {
          imageUrl.value = result.tempFilePaths[0]
          analysisResult.value = ''
        },
        fail: (err) => {
          if (err.errMsg !== 'chooseImage:fail cancel') {
            uni.showToast({ title: '选择图片失败', icon: 'none' })
          }
        }
      })
    }
  })
}

const deleteImage = () => {
  imageUrl.value = ''
  analysisResult.value = ''
}

const analyzeReport = async () => {
  if (!imageUrl.value || analyzing.value) return
  
  analyzing.value = true
  
  try {
    // 模拟AI分析过程（实际应调用后端API）
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟分析结果
    analysisResult.value = `📊 报告分析结果：

1. 空腹血糖：5.8 mmol/L（正常范围）
2. 餐后2小时血糖：7.2 mmol/L（正常范围）
3. 糖化血红蛋白：5.9%（控制良好）

💡 建议：
- 继续保持当前的饮食和运动习惯
- 定期监测血糖，建议每周至少测量3次
- 下次复查时间：3个月后

⚠️ 提示：此分析结果仅供参考，具体诊断请咨询专业医生。`
    
    uni.showToast({ title: '分析完成', icon: 'success' })
  } catch (error) {
    console.error('分析失败:', error)
    uni.showToast({ title: '分析失败，请重试', icon: 'none' })
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF8E1 0%, #FFFEF7 30%, #FFF5E6 100%);
  padding-bottom: 40rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx;
  padding-top: calc(env(safe-area-inset-top) + 20rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
}

.nav-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 48rpx;
  color: #8B4513;
}

.nav-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #8B4513;
}

.nav-placeholder {
  width: 60rpx;
}

.upload-section {
  padding: 32rpx;
}

.upload-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  border: 2rpx dashed #D2691E;
  min-height: 400rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 40rpx;
}

.upload-icon {
  font-size: 80rpx;
}

.upload-text {
  font-size: 32rpx;
  color: #8B4513;
  font-weight: 500;
}

.upload-hint {
  font-size: 24rpx;
  color: #A0522D;
}

.image-preview {
  width: 100%;
  position: relative;
}

.preview-image {
  width: 100%;
  max-height: 600rpx;
}

.image-actions {
  display: flex;
  justify-content: center;
  gap: 24rpx;
  padding: 24rpx;
  background: rgba(255, 254, 247, 0.9);
}

.action-btn {
  padding: 16rpx 32rpx;
  border-radius: 32rpx;
  font-size: 26rpx;
}

.reselect-btn {
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  color: white;
}

.delete-btn {
  background: #f3f4f6;
  color: #6b7280;
}

.analyze-section {
  padding: 0 32rpx;
  margin-bottom: 32rpx;
}

.analyze-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  color: white;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(203, 142, 84, 0.3);
}

.analyze-btn.disabled {
  opacity: 0.5;
}

.btn-loading {
  color: white;
}

.result-section {
  padding: 0 32rpx;
  margin-bottom: 32rpx;
}

.result-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 32rpx;
  border: 1rpx solid #E3C7A4;
  box-shadow: 0 4rpx 16rpx rgba(203, 142, 84, 0.1);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #E3C7A4;
}

.result-icon {
  font-size: 40rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
}

.result-content {
  padding: 16rpx;
  background: #FFF8E7;
  border-radius: 16rpx;
}

.result-text {
  font-size: 28rpx;
  color: #602F27;
  line-height: 1.8;
  white-space: pre-wrap;
}

.tips-section {
  padding: 0 32rpx;
}

.tips-card {
  background: rgba(255, 254, 247, 0.8);
  border-radius: 20rpx;
  padding: 28rpx;
  border: 1rpx solid #E3C7A4;
}

.tips-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 16rpx;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.tip-item {
  font-size: 24rpx;
  color: #A0522D;
  line-height: 1.6;
}
</style>
