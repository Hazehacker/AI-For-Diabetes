<template>
  <div class="chat-history-container">
    <div class="page-header">
      <h1 class="page-title">对话记录</h1>
      <p class="page-description">查看用户与AI的对话记录</p>
    </div>
    
    <el-card shadow="never">
      <div class="coming-soon">
        <el-icon size="64" color="#409EFF">
          <ChatDotRound />
        </el-icon>
        <h2>功能开发中</h2>
        <p>对话记录管理功能正在开发中，敬请期待...</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound } from '@element-plus/icons-vue'
</script>

<style scoped>
.chat-history-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.coming-soon {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.coming-soon h2 {
  margin: 20px 0 12px 0;
  color: #2c3e50;
}

.coming-soon p {
  margin: 0;
  font-size: 16px;
}
</style>
