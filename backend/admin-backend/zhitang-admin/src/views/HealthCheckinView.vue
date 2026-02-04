<template>
  <div class="checkin-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">打卡管理</h1>
      <p class="page-description">管理用户的健康打卡记录和打卡类型</p>
    </div>

    <!-- 打卡类型管理 -->
    <el-card class="types-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">打卡类型管理</span>
          <div class="card-actions">
            <el-button type="primary" @click="showCreateTypeDialog">
              <el-icon><Plus /></el-icon>
              新建类型
            </el-button>
            <el-button @click="refreshTypes">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="checkinTypes"
        stripe
        v-loading="typesLoading"
        style="width: 100%"
      >
        <el-table-column prop="type_id" label="ID" width="80" />
        <el-table-column prop="type_name" label="类型名称" min-width="120" />
        <el-table-column prop="type_description" label="描述" min-width="150" />
        <el-table-column prop="checkin_cycle" label="打卡周期" width="100">
          <template #default="{ row }">
            <el-tag :type="getCycleTagType(row.checkin_cycle)">
              {{ getCycleLabel(row.checkin_cycle) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points_per_checkin" label="积分奖励" width="100" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" text @click="editType(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              size="small"
              text
              :type="row.is_active ? 'danger' : 'success'"
              @click="toggleTypeStatus(row)"
            >
              <el-icon><Switch /></el-icon>
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 打卡记录管理 -->
    <el-card class="records-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">打卡记录</span>
          <div class="card-actions">
            <el-select
              v-model="recordFilters.user_id"
              placeholder="选择用户"
              filterable
              remote
              :remote-method="searchUsers"
              :loading="userSearchLoading"
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.user_id"
                :label="`${user.username} (${user.nickname || '未设置昵称'})`"
                :value="user.user_id"
              />
            </el-select>
            <el-select
              v-model="recordFilters.type_id"
              placeholder="选择类型"
              clearable
              style="width: 150px"
            >
              <el-option
                v-for="type in checkinTypes"
                :key="type.type_id"
                :label="type.type_name"
                :value="type.type_id"
              />
            </el-select>
            <el-button @click="refreshRecords">
              <el-icon><Search /></el-icon>
              筛选
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="checkinRecords"
        stripe
        v-loading="recordsLoading"
        style="width: 100%"
      >
        <el-table-column prop="record_id" label="ID" width="80" />
        <el-table-column label="用户信息" min-width="150">
          <template #default="{ row }">
            <div class="user-info">
              <span class="username">{{ row.username }}</span>
              <span class="nickname">{{ row.nickname }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="checkin_type" label="打卡类型" min-width="120" />
        <el-table-column prop="checkin_value" label="打卡值" min-width="120" />
        <el-table-column prop="timestamp" label="打卡时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="recordPagination.current"
          v-model:page-size="recordPagination.size"
          :total="recordPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleRecordSizeChange"
          @current-change="handleRecordCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑打卡类型对话框 -->
    <el-dialog
      v-model="typeDialogVisible"
      :title="isEditType ? '编辑打卡类型' : '新建打卡类型'"
      width="500px"
    >
      <el-form :model="typeForm" :rules="typeRules" ref="typeFormRef" label-width="100px">
        <el-form-item label="类型名称" prop="type_name">
          <el-input v-model="typeForm.type_name" placeholder="请输入类型名称" />
        </el-form-item>
        <el-form-item label="类型描述" prop="type_description">
          <el-input
            v-model="typeForm.type_description"
            type="textarea"
            :rows="3"
            placeholder="请输入类型描述"
          />
        </el-form-item>
        <el-form-item label="打卡周期" prop="checkin_cycle">
          <el-select v-model="typeForm.checkin_cycle" placeholder="选择打卡周期">
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="typeForm.checkin_cycle === 'custom'"
          label="周期天数"
          prop="cycle_days"
        >
          <el-input-number
            v-model="typeForm.cycle_days"
            :min="1"
            :max="365"
            placeholder="请输入周期天数"
          />
        </el-form-item>
        <el-form-item label="积分奖励" prop="points_per_checkin">
          <el-input-number
            v-model="typeForm.points_per_checkin"
            :min="0"
            :max="1000"
            placeholder="请输入积分奖励"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="typeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTypeForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Edit,
  Switch,
  Search
} from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

// API接口
const api = {
  getCheckinTypes: () => fetch('/api/checkin/types').then(res => res.json()),
  createCheckinType: (data: any) => fetch('/api/checkin/types', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(res => res.json()),
  updateCheckinType: (typeId: number, data: any) => fetch(`/api/checkin/types/${typeId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(res => res.json()),
  deleteCheckinType: (typeId: number) => fetch(`/api/checkin/types/${typeId}`, {
    method: 'DELETE'
  }).then(res => res.json()),
  getCheckinRecords: (params: any) => fetch(`/api/checkin/records?${new URLSearchParams(params)}`).then(res => res.json())
}

// 响应式数据
const typesLoading = ref(false)
const recordsLoading = ref(false)
const checkinTypes = ref([])
const checkinRecords = ref([])
const userOptions = ref([])
const userSearchLoading = ref(false)

// 对话框状态
const typeDialogVisible = ref(false)
const isEditType = ref(false)

// 筛选条件
const recordFilters = reactive({
  user_id: '',
  type_id: ''
})

// 分页
const recordPagination = reactive({
  current: 1,
  size: 20,
  total: 0
})

// 表单数据
const typeForm = reactive({
  type_id: null,
  type_name: '',
  type_description: '',
  checkin_cycle: 'daily',
  cycle_days: 1,
  points_per_checkin: 10
})

// 表单验证规则
const typeRules = {
  type_name: [
    { required: true, message: '请输入类型名称', trigger: 'blur' },
    { min: 1, max: 50, message: '类型名称长度应在1-50个字符', trigger: 'blur' }
  ],
  checkin_cycle: [
    { required: true, message: '请选择打卡周期', trigger: 'change' }
  ],
  points_per_checkin: [
    { required: true, message: '请输入积分奖励', trigger: 'blur' }
  ]
}

// 获取周期标签类型
const getCycleTagType = (cycle: string) => {
  const types = {
    daily: 'info',
    weekly: 'warning',
    monthly: 'success',
    custom: ''
  }
  return types[cycle] || 'info'
}

// 获取周期标签文本
const getCycleLabel = (cycle: string) => {
  const labels = {
    daily: '每日',
    weekly: '每周',
    monthly: '每月',
    custom: '自定义'
  }
  return labels[cycle] || cycle
}

// 刷新打卡类型
const refreshTypes = async () => {
  typesLoading.value = true
  try {
    const response = await api.getCheckinTypes()
    if (response.types) {
      checkinTypes.value = response.types
    }
  } catch (error) {
    ElMessage.error('获取打卡类型失败')
    console.error(error)
  } finally {
    typesLoading.value = false
  }
}

// 刷新打卡记录
const refreshRecords = async () => {
  recordsLoading.value = true
  try {
    const params = {
      page: recordPagination.current,
      limit: recordPagination.size,
      ...recordFilters
    }

    const response = await api.getCheckinRecords(params)
    if (response.records) {
      checkinRecords.value = response.records
      recordPagination.total = response.total
    }
  } catch (error) {
    ElMessage.error('获取打卡记录失败')
    console.error(error)
  } finally {
    recordsLoading.value = false
  }
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

// 显示创建类型对话框
const showCreateTypeDialog = () => {
  isEditType.value = false
  Object.assign(typeForm, {
    type_id: null,
    type_name: '',
    type_description: '',
    checkin_cycle: 'daily',
    cycle_days: 1,
    points_per_checkin: 10
  })
  typeDialogVisible.value = true
}

// 编辑打卡类型
const editType = (type: any) => {
  isEditType.value = true
  Object.assign(typeForm, {
    type_id: type.type_id,
    type_name: type.type_name,
    type_description: type.type_description,
    checkin_cycle: type.checkin_cycle,
    cycle_days: type.cycle_days,
    points_per_checkin: type.points_per_checkin
  })
  typeDialogVisible.value = true
}

// 切换类型状态
const toggleTypeStatus = async (type: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要${type.is_active ? '禁用' : '启用'}打卡类型 "${type.type_name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 这里应该调用API更新状态
    ElMessage.success(`打卡类型${type.is_active ? '禁用' : '启用'}成功`)
    refreshTypes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 提交类型表单
const submitTypeForm = async () => {
  try {
    const typeFormRef = ref<FormInstance>()
    const valid = await typeFormRef.value?.validate()
    if (!valid) return

    if (isEditType.value) {
      const response = await api.updateCheckinType(typeForm.type_id, {
        type_name: typeForm.type_name,
        type_description: typeForm.type_description,
        checkin_cycle: typeForm.checkin_cycle,
        cycle_days: typeForm.cycle_days,
        points_per_checkin: typeForm.points_per_checkin
      })
      if (response.message) {
        ElMessage.success(response.message)
      }
    } else {
      const response = await api.createCheckinType({
        type_name: typeForm.type_name,
        type_description: typeForm.type_description,
        checkin_cycle: typeForm.checkin_cycle,
        cycle_days: typeForm.checkin_cycle === 'custom' ? typeForm.cycle_days : 1,
        points_per_checkin: typeForm.points_per_checkin
      })
      if (response.message) {
        ElMessage.success(response.message)
      }
    }

    typeDialogVisible.value = false
    refreshTypes()
  } catch (error) {
    ElMessage.error(isEditType.value ? '更新打卡类型失败' : '创建打卡类型失败')
    console.error(error)
  }
}

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 分页处理
const handleRecordSizeChange = (size: number) => {
  recordPagination.size = size
  recordPagination.current = 1
  refreshRecords()
}

const handleRecordCurrentChange = (page: number) => {
  recordPagination.current = page
  refreshRecords()
}

// 监听筛选条件变化
watch([() => recordFilters.user_id, () => recordFilters.type_id], () => {
  recordPagination.current = 1
  refreshRecords()
})

// 组件挂载时加载数据
onMounted(() => {
  refreshTypes()
  refreshRecords()
})
</script>

<style scoped>
.checkin-management-container {
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

.types-card {
  margin-bottom: 20px;
}

.records-card {
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

.nickname {
  font-size: 12px;
  color: #7f8c8d;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .checkin-management-container {
    padding: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .card-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .card-actions .el-select {
    width: 100% !important;
    margin-bottom: 8px;
  }
}
</style>
