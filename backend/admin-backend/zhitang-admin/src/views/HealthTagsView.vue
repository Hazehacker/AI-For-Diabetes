<template>
  <div class="tags-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">用户标签管理</h1>
      <p class="page-description">管理系统中的用户标签，支持层级结构</p>
    </div>

    <!-- 标签树形结构 -->
    <el-card class="tree-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">标签结构</span>
          <div class="card-actions">
            <el-button type="primary" @click="showCreateDialog">
              <el-icon><Plus /></el-icon>
              新建标签
            </el-button>
            <el-button @click="refreshTags">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-tree
        ref="tagTree"
        :data="tagTreeData"
        :props="treeProps"
        node-key="tag_id"
        :expand-on-click-node="false"
        :default-expanded-keys="expandedKeys"
        @node-contextmenu="handleContextMenu"
        v-loading="loading"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <el-icon class="node-icon">
              <component :is="getNodeIcon(data)" />
            </el-icon>
            <span class="node-label">{{ data.tag_name }}</span>
            <div class="node-actions">
              <el-button size="small" text @click="editTag(data)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" text @click="deleteTag(data)" type="danger">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>

    <!-- 用户标签分配 -->
    <el-card class="assignment-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">用户标签分配</span>
          <div class="card-actions">
            <el-select
              v-model="selectedUserId"
              placeholder="选择用户"
              filterable
              remote
              :remote-method="searchUsers"
              :loading="userSearchLoading"
              style="width: 200px"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.user_id"
                :label="`${user.username} (${user.nickname || '未设置昵称'})`"
                :value="user.user_id"
              />
            </el-select>
            <el-button type="primary" @click="assignTagToUser" :disabled="!selectedUserId">
              分配标签
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="selectedUserId" class="user-tag-info">
        <div class="user-info">
          <h3>用户标签</h3>
          <div class="user-tags">
            <el-tag
              v-for="tag in userTags"
              :key="tag.tag_id"
              closable
              @close="removeTagFromUser(tag.tag_id)"
            >
              {{ tag.tag_name }}
            </el-tag>
            <el-button v-if="userTags.length === 0" text @click="showAssignDialog">
              点击分配标签
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 创建/编辑标签对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑标签' : '新建标签'"
      width="500px"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="80px">
        <el-form-item label="标签名称" prop="tag_name">
          <el-input v-model="tagForm.tag_name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签描述" prop="tag_description">
          <el-input
            v-model="tagForm.tag_description"
            type="textarea"
            :rows="3"
            placeholder="请输入标签描述"
          />
        </el-form-item>
        <el-form-item label="父标签" prop="parent_tag_id">
          <el-select v-model="tagForm.parent_tag_id" placeholder="选择父标签（可选）" clearable>
            <el-option
              v-for="tag in availableParentTags"
              :key="tag.tag_id"
              :label="`${'　'.repeat(tag.tag_level - 1)}${tag.tag_name}`"
              :value="tag.tag_id"
              :disabled="tag.tag_id === tagForm.tag_id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTagForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 分配标签对话框 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="分配标签"
      width="500px"
    >
      <el-tree
        ref="assignTree"
        :data="tagTreeData"
        :props="treeProps"
        node-key="tag_id"
        show-checkbox
        check-strictly
        :default-checked-keys="assignedTagIds"
      />

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="assignDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAssignTags">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <el-menu
      v-if="contextMenuVisible"
      :style="{ position: 'fixed', left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      @click="handleContextMenuAction"
    >
      <el-menu-item index="edit">
        <el-icon><Edit /></el-icon>
        编辑标签
      </el-menu-item>
      <el-menu-item index="delete">
        <el-icon><Delete /></el-icon>
        删除标签
      </el-menu-item>
      <el-menu-item index="add-child">
        <el-icon><Plus /></el-icon>
        添加子标签
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Edit,
  Delete,
  Monitor,
  Folder,
  FolderOpened
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

// API接口
const api = {
  getTags: () => fetch('/api/tags').then(res => res.json()),
  createTag: (data: any) => fetch('/api/tags', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(res => res.json()),
  updateTag: (tagId: number, data: any) => fetch(`/api/tags/${tagId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteTag: (tagId: number) => fetch(`/api/tags/${tagId}`, {
    method: 'DELETE'
  }).then(res => res.json()),
  getUserTags: (userId: number) => fetch(`/api/users/${userId}/tags`).then(res => res.json()),
  assignUserTag: (userId: number, tagId: number) => fetch(`/api/users/${userId}/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag_id: tagId })
  }).then(res => res.json()),
  removeUserTag: (userId: number, tagId: number) => fetch(`/api/users/${userId}/tags/${tagId}`, {
    method: 'DELETE'
  }).then(res => res.json())
}

// 响应式数据
const loading = ref(false)
const tagTreeData = ref([])
const expandedKeys = ref([])
const selectedUserId = ref('')
const userOptions = ref([])
const userTags = ref([])
const userSearchLoading = ref(false)
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const isEdit = ref(false)
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuTagId = ref(0)
const assignedTagIds = ref([])

// 表单数据
const tagForm = reactive({
  tag_id: null,
  tag_name: '',
  tag_description: '',
  parent_tag_id: null
})

// 表单验证规则
const tagRules = {
  tag_name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '标签名称长度应在1-50个字符', trigger: 'blur' }
  ]
}

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'tag_name'
}

// 计算属性
const availableParentTags = computed(() => {
  return tagTreeData.value.filter(tag => tag.tag_id !== tagForm.tag_id)
})

// 获取节点图标
const getNodeIcon = (data: any) => {
  return data.children && data.children.length > 0 ? FolderOpened : Folder
}

// 刷新标签树
const refreshTags = async () => {
  loading.value = true
  try {
    const response = await api.getTags()
    if (response.tags) {
      tagTreeData.value = buildTagTree(response.tags)
      expandedKeys.value = tagTreeData.value.map(tag => tag.tag_id)
    }
  } catch (error) {
    ElMessage.error('获取标签列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 构建标签树结构
const buildTagTree = (tags: any[]) => {
  const tagMap = new Map()
  const roots = []

  // 首先将所有标签放入map中
  tags.forEach(tag => {
    tag.children = []
    tagMap.set(tag.tag_id, tag)
  })

  // 构建树形结构
  tags.forEach(tag => {
    if (tag.parent_tag_id && tagMap.has(tag.parent_tag_id)) {
      const parent = tagMap.get(tag.parent_tag_id)
      parent.children.push(tag)
    } else {
      roots.push(tag)
    }
  })

  return roots
}

// 搜索用户
const searchUsers = async (query: string) => {
  if (query !== '') {
    userSearchLoading.value = true
    try {
      // 这里应该调用搜索用户的API
      // 暂时使用模拟数据
      userOptions.value = [
        { user_id: 1, username: 'admin', nickname: '管理员' },
        { user_id: 2, username: 'user1', nickname: '用户1' }
      ].filter(user =>
        user.username.includes(query) || (user.nickname && user.nickname.includes(query))
      )
    } catch (error) {
      console.error(error)
    } finally {
      userSearchLoading.value = false
    }
  } else {
    userOptions.value = []
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  Object.assign(tagForm, {
    tag_id: null,
    tag_name: '',
    tag_description: '',
    parent_tag_id: null
  })
  dialogVisible.value = true
}

// 编辑标签
const editTag = (tag: any) => {
  isEdit.value = true
  Object.assign(tagForm, {
    tag_id: tag.tag_id,
    tag_name: tag.tag_name,
    tag_description: tag.tag_description,
    parent_tag_id: tag.parent_tag_id
  })
  dialogVisible.value = true
}

// 删除标签
const deleteTag = async (tag: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.tag_name}" 吗？删除后不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await api.deleteTag(tag.tag_id)
    if (response.message) {
      ElMessage.success(response.message)
      refreshTags()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除标签失败')
      console.error(error)
    }
  }
}

// 提交标签表单
const submitTagForm = async () => {
  try {
    const tagFormRef = ref<FormInstance>()
    const valid = await tagFormRef.value?.validate()
    if (!valid) return

    if (isEdit.value) {
      const response = await api.updateTag(tagForm.tag_id, {
        tag_name: tagForm.tag_name,
        tag_description: tagForm.tag_description
      })
      if (response.message) {
        ElMessage.success(response.message)
      }
    } else {
      const response = await api.createTag({
        tag_name: tagForm.tag_name,
        tag_description: tagForm.tag_description,
        parent_tag_id: tagForm.parent_tag_id
      })
      if (response.message) {
        ElMessage.success(response.message)
      }
    }

    dialogVisible.value = false
    refreshTags()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新标签失败' : '创建标签失败')
    console.error(error)
  }
}

// 获取用户标签
const loadUserTags = async () => {
  if (!selectedUserId.value) return

  try {
    const response = await api.getUserTags(selectedUserId.value)
    if (response.tags) {
      userTags.value = response.tags
      assignedTagIds.value = response.tags.map(tag => tag.tag_id)
    }
  } catch (error) {
    ElMessage.error('获取用户标签失败')
    console.error(error)
  }
}

// 分配标签给用户
const assignTagToUser = () => {
  if (!selectedUserId.value) return
  assignDialogVisible.value = true
}

// 移除用户标签
const removeTagFromUser = async (tagId: number) => {
  try {
    const response = await api.removeUserTag(selectedUserId.value, tagId)
    if (response.message) {
      ElMessage.success(response.message)
      loadUserTags()
    }
  } catch (error) {
    ElMessage.error('移除标签失败')
    console.error(error)
  }
}

// 确认分配标签
const confirmAssignTags = async () => {
  const assignTree = ref()
  const checkedKeys = assignTree.value?.getCheckedKeys() || []

  try {
    for (const tagId of checkedKeys) {
      if (!assignedTagIds.value.includes(tagId)) {
        await api.assignUserTag(selectedUserId.value, tagId)
      }
    }

    // 移除不再分配的标签
    for (const tagId of assignedTagIds.value) {
      if (!checkedKeys.includes(tagId)) {
        await api.removeUserTag(selectedUserId.value, tagId)
      }
    }

    ElMessage.success('标签分配完成')
    assignDialogVisible.value = false
    loadUserTags()
  } catch (error) {
    ElMessage.error('分配标签失败')
    console.error(error)
  }
}

// 处理右键菜单
const handleContextMenu = (event: any, data: any) => {
  event.preventDefault()
  contextMenuVisible.value = true
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuTagId.value = data.tag_id
}

// 处理右键菜单动作
const handleContextMenuAction = (action: string) => {
  contextMenuVisible.value = false

  switch (action) {
    case 'edit':
      editTag({ tag_id: contextMenuTagId.value })
      break
    case 'delete':
      deleteTag({ tag_id: contextMenuTagId.value })
      break
    case 'add-child':
      showCreateDialog()
      // 设置父标签ID
      tagForm.parent_tag_id = contextMenuTagId.value
      break
  }
}

// 监听用户选择变化
watch(selectedUserId, () => {
  if (selectedUserId.value) {
    loadUserTags()
  } else {
    userTags.value = []
    assignedTagIds.value = []
  }
})

// 组件挂载时加载数据
onMounted(() => {
  refreshTags()
})
</script>

<style scoped>
.tags-management-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.tree-card {
  margin-bottom: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.node-icon {
  color: #409EFF;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.assignment-card {
  margin-bottom: 20px;
}

.user-tag-info {
  padding: 20px;
}

.user-info h3 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 16px;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tags .el-tag {
  margin: 0;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tags-management-container {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .card-actions {
    justify-content: center;
  }

  .tree-node {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .node-actions {
    opacity: 1;
    text-align: center;
  }
}
</style>
