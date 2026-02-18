<template>
  <view class="medicine-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <view class="nav-back" @tap="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">药品管理</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 添加药品按钮 -->
    <view class="add-section">
      <view class="add-card" @tap="scanMedicine">
        <text class="add-icon">📷</text>
        <view class="add-info">
          <text class="add-title">扫描药盒添加</text>
          <text class="add-hint">拍照识别药品名、规格、有效期</text>
        </view>
        <text class="add-arrow">›</text>
      </view>
    </view>

    <!-- OCR识别弹窗 -->
    <view v-if="showOcrModal" class="ocr-modal-overlay" @tap="closeOcrModal">
      <view class="ocr-modal" @tap.stop>
        <view class="ocr-header">
          <text class="ocr-title">📦 识别结果</text>
          <view class="ocr-close" @tap="closeOcrModal">✕</view>
        </view>
        
        <view v-if="ocrScanning" class="ocr-scanning">
          <text class="scanning-icon">🔍</text>
          <text class="scanning-text">正在识别中...</text>
        </view>
        
        <view v-else class="ocr-result">
          <view class="ocr-field">
            <text class="field-label">药品名称</text>
            <input class="field-input" v-model="ocrData.name" placeholder="请输入药品名称" />
          </view>
          <view class="ocr-field">
            <text class="field-label">规格</text>
            <input class="field-input" v-model="ocrData.spec" placeholder="如：0.5g*24片" />
          </view>
          <view class="ocr-field">
            <text class="field-label">生产批号</text>
            <input class="field-input" v-model="ocrData.batchNo" placeholder="请输入生产批号" />
          </view>
          <view class="ocr-field">
            <text class="field-label">有效期至</text>
            <picker mode="date" :value="ocrData.expiryDate" @change="onExpiryChange">
              <view class="field-input date-picker">
                <text>{{ ocrData.expiryDate || '请选择有效期' }}</text>
                <text class="picker-icon">📅</text>
              </view>
            </picker>
          </view>
          
          <view class="ocr-actions">
            <button class="cancel-btn" @tap="closeOcrModal">取消</button>
            <button class="confirm-btn" @tap="confirmAddMedicine">确认添加</button>
          </view>
        </view>
      </view>
    </view>

    <!-- 药品列表 -->
    <view class="medicine-list">
      <text class="list-title">💊 我的药箱</text>
      
      <view v-if="medicines.length === 0" class="empty-state">
        <text class="empty-icon">📦</text>
        <text class="empty-text">暂无药品记录</text>
        <text class="empty-hint">点击上方按钮添加药品</text>
      </view>
      
      <view v-else>
        <view 
          v-for="(med, index) in medicines" 
          :key="index" 
          class="medicine-card"
          :class="{ 'expiring-soon': med.expiringSoon, 'expired': med.expired }"
        >
          <view class="card-header" @tap="toggleExpand(index)">
            <view class="med-info">
              <view class="med-name-row">
                <text class="med-name">{{ med.name }}</text>
                <view v-if="med.expired" class="status-badge expired-badge">已过期</view>
                <view v-else-if="med.expiringSoon" class="status-badge warning-badge">即将过期</view>
              </view>
              <text class="med-spec">{{ med.spec }}</text>
              <text class="med-expiry">有效期至：{{ med.expiryDate }}</text>
            </view>
            <text class="expand-icon">{{ med.expanded ? '▼' : '▶' }}</text>
          </view>
          
          <!-- 展开的电子说明书 -->
          <view v-if="med.expanded" class="med-details">
            <!-- 用法用量 -->
            <view class="detail-panel">
              <view class="panel-header" @tap="togglePanel(index, 'usage')">
                <text class="panel-title">📋 用法用量</text>
                <text class="panel-arrow">{{ med.panels?.usage ? '▼' : '▶' }}</text>
              </view>
              <view v-if="med.panels?.usage" class="panel-content">
                <text>{{ med.usage || '口服，一次1片，一日3次，饭后服用。' }}</text>
              </view>
            </view>
            
            <!-- 禁忌事项 -->
            <view class="detail-panel">
              <view class="panel-header" @tap="togglePanel(index, 'contraindication')">
                <text class="panel-title">⚠️ 禁忌事项</text>
                <text class="panel-arrow">{{ med.panels?.contraindication ? '▼' : '▶' }}</text>
              </view>
              <view v-if="med.panels?.contraindication" class="panel-content warning">
                <text>{{ med.contraindication || '对本品过敏者禁用；孕妇及哺乳期妇女慎用；肝肾功能不全者慎用。' }}</text>
              </view>
            </view>
            
            <!-- 储存条件 -->
            <view class="detail-panel">
              <view class="panel-header" @tap="togglePanel(index, 'storage')">
                <text class="panel-title">🏠 储存条件</text>
                <text class="panel-arrow">{{ med.panels?.storage ? '▼' : '▶' }}</text>
              </view>
              <view v-if="med.panels?.storage" class="panel-content">
                <text>{{ med.storage || '密封，置阴凉干燥处保存（不超过25℃）。' }}</text>
              </view>
            </view>
            
            <!-- 删除按钮 -->
            <view class="delete-section">
              <button class="delete-btn" @tap="deleteMedicine(index)">删除此药品</button>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const showOcrModal = ref(false)
const ocrScanning = ref(false)
const ocrData = reactive({
  name: '',
  spec: '',
  batchNo: '',
  expiryDate: ''
})

const medicines = ref([])

onMounted(() => {
  // 从本地存储加载药品列表
  const saved = uni.getStorageSync('medicineBox')
  if (saved) {
    medicines.value = JSON.parse(saved).map(med => ({
      ...med,
      expanded: false,
      panels: {},
      ...checkExpiry(med.expiryDate)
    }))
  }
})

const goBack = () => {
  uni.navigateBack()
}

const scanMedicine = () => {
  uni.showActionSheet({
    itemList: ['拍照识别', '从相册选择'],
    success: (res) => {
      const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
      uni.chooseImage({
        count: 1,
        sourceType,
        success: (result) => {
          // 显示OCR弹窗并开始识别
          showOcrModal.value = true
          ocrScanning.value = true
          
          // 模拟OCR识别过程
          setTimeout(() => {
            ocrScanning.value = false
            // 模拟识别结果
            ocrData.name = '二甲双胍缓释片'
            ocrData.spec = '0.5g×30片'
            ocrData.batchNo = 'B20250115'
            ocrData.expiryDate = '2027-01-15'
          }, 1500)
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

const closeOcrModal = () => {
  showOcrModal.value = false
  ocrScanning.value = false
  // 重置表单
  ocrData.name = ''
  ocrData.spec = ''
  ocrData.batchNo = ''
  ocrData.expiryDate = ''
}

const onExpiryChange = (e) => {
  ocrData.expiryDate = e.detail.value
}

const checkExpiry = (expiryDate) => {
  if (!expiryDate) return { expiringSoon: false, expired: false }
  
  const expiry = new Date(expiryDate)
  const today = new Date()
  const diffDays = Math.floor((expiry - today) / (1000 * 60 * 60 * 24))
  
  return {
    expired: diffDays < 0,
    expiringSoon: diffDays >= 0 && diffDays <= 30
  }
}

const confirmAddMedicine = () => {
  if (!ocrData.name) {
    uni.showToast({ title: '请输入药品名称', icon: 'none' })
    return
  }
  
  const newMedicine = {
    name: ocrData.name,
    spec: ocrData.spec,
    batchNo: ocrData.batchNo,
    expiryDate: ocrData.expiryDate,
    expanded: false,
    panels: {},
    ...checkExpiry(ocrData.expiryDate)
  }
  
  medicines.value.unshift(newMedicine)
  saveMedicines()
  closeOcrModal()
  
  uni.showToast({ title: '添加成功', icon: 'success' })
}

const toggleExpand = (index) => {
  medicines.value[index].expanded = !medicines.value[index].expanded
}

const togglePanel = (index, panel) => {
  if (!medicines.value[index].panels) {
    medicines.value[index].panels = {}
  }
  medicines.value[index].panels[panel] = !medicines.value[index].panels[panel]
}

const deleteMedicine = (index) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除"${medicines.value[index].name}"吗？`,
    success: (res) => {
      if (res.confirm) {
        medicines.value.splice(index, 1)
        saveMedicines()
        uni.showToast({ title: '已删除', icon: 'success' })
      }
    }
  })
}

const saveMedicines = () => {
  const toSave = medicines.value.map(({ expanded, panels, expiringSoon, expired, ...rest }) => rest)
  uni.setStorageSync('medicineBox', JSON.stringify(toSave))
}
</script>

<style scoped>
.medicine-page {
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

.add-section {
  padding: 32rpx;
}

.add-card {
  display: flex;
  align-items: center;
  background: #FFFEF7;
  border-radius: 24rpx;
  padding: 32rpx;
  border: 2rpx dashed #D2691E;
  gap: 20rpx;
}

.add-icon {
  font-size: 56rpx;
}

.add-info {
  flex: 1;
}

.add-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 8rpx;
}

.add-hint {
  display: block;
  font-size: 24rpx;
  color: #A0522D;
}

.add-arrow {
  font-size: 40rpx;
  color: #D2691E;
}

/* OCR弹窗 */
.ocr-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 40rpx;
}

.ocr-modal {
  width: 100%;
  max-width: 640rpx;
  background: #FFFEF7;
  border-radius: 32rpx;
  overflow: hidden;
}

.ocr-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
}

.ocr-title {
  font-size: 32rpx;
  font-weight: 600;
  color: white;
}

.ocr-close {
  font-size: 32rpx;
  color: white;
  padding: 8rpx;
}

.ocr-scanning {
  padding: 80rpx 40rpx;
  text-align: center;
}

.scanning-icon {
  display: block;
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.scanning-text {
  font-size: 28rpx;
  color: #8B4513;
}

.ocr-result {
  padding: 32rpx;
}

.ocr-field {
  margin-bottom: 24rpx;
}

.field-label {
  display: block;
  font-size: 26rpx;
  color: #8B4513;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.field-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background: #FFF8E7;
  border: 1rpx solid #E3C7A4;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #602F27;
  box-sizing: border-box;
}

.date-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.picker-icon {
  font-size: 32rpx;
}

.ocr-actions {
  display: flex;
  gap: 24rpx;
  margin-top: 32rpx;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.cancel-btn {
  background: #f3f4f6;
  color: #6b7280;
}

.confirm-btn {
  background: linear-gradient(135deg, #D2691E 0%, #CD853F 100%);
  color: white;
}

/* 药品列表 */
.medicine-list {
  padding: 0 32rpx;
}

.list-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
  margin-bottom: 24rpx;
}

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
  background: #FFFEF7;
  border-radius: 24rpx;
  border: 1rpx solid #E3C7A4;
}

.empty-icon {
  display: block;
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.empty-text {
  display: block;
  font-size: 30rpx;
  color: #8B4513;
  margin-bottom: 8rpx;
}

.empty-hint {
  display: block;
  font-size: 24rpx;
  color: #A0522D;
}

.medicine-card {
  background: #FFFEF7;
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E3C7A4;
  overflow: hidden;
}

.medicine-card.expiring-soon {
  border-color: #F59E0B;
  background: linear-gradient(135deg, #FFFEF7 0%, #FEF3C7 100%);
}

.medicine-card.expired {
  border-color: #EF4444;
  background: linear-gradient(135deg, #FFFEF7 0%, #FEE2E2 100%);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 28rpx;
}

.med-info {
  flex: 1;
}

.med-name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.med-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #8B4513;
}

.status-badge {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: 500;
}

.warning-badge {
  background: #FEF3C7;
  color: #D97706;
}

.expired-badge {
  background: #FEE2E2;
  color: #DC2626;
}

.med-spec {
  display: block;
  font-size: 26rpx;
  color: #A0522D;
  margin-bottom: 4rpx;
}

.med-expiry {
  display: block;
  font-size: 24rpx;
  color: #6b7280;
}

.expand-icon {
  font-size: 24rpx;
  color: #A0522D;
}

/* 展开详情 */
.med-details {
  padding: 0 28rpx 28rpx;
  border-top: 1rpx solid #E3C7A4;
}

.detail-panel {
  margin-top: 20rpx;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background: #FFF8E7;
  border-radius: 12rpx;
}

.panel-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #8B4513;
}

.panel-arrow {
  font-size: 20rpx;
  color: #A0522D;
}

.panel-content {
  padding: 20rpx;
  background: #FFFEF7;
  border: 1rpx solid #E3C7A4;
  border-top: none;
  border-radius: 0 0 12rpx 12rpx;
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.6;
}

.panel-content.warning {
  background: #FEF3C7;
  border-color: #FDE68A;
  color: #92400E;
}

.delete-section {
  margin-top: 24rpx;
  text-align: center;
}

.delete-btn {
  background: transparent;
  color: #EF4444;
  font-size: 26rpx;
  border: 1rpx solid #EF4444;
  border-radius: 32rpx;
  padding: 16rpx 40rpx;
}
</style>
