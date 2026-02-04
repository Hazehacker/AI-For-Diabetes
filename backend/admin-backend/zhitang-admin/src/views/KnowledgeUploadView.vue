<template>
  <div class="knowledge-upload-container">
    <div class="page-header">
      <h1 class="page-title">上传知识</h1>
      <p class="page-description">向AI知识库添加新内容</p>
    </div>
    
    <el-card shadow="never">
      <div class="coming-soon">
        <el-icon size="64" color="#409EFF">
          <Document />
        </el-icon>
        <h2>功能开发中</h2>
        <p>知识上传功能正在开发中，敬请期待...</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'
</script>

<style scoped>
.knowledge-upload-container {
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
