<template>
  <div class="page-container">
    <div class="page-header">
      <h2>提醒管理</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建提醒</el-button>
    </div>
    <div class="filter-bar">
      <el-select v-model="filters.status" placeholder="提醒状态" clearable style="width: 130px" @change="loadData">
        <el-option label="待处理" value="pending" />
        <el-option label="已处理" value="handled" />
        <el-option label="已忽略" value="ignored" />
      </el-select>
      <el-select v-model="filters.type" placeholder="提醒类型" clearable style="width: 130px" @change="loadData">
        <el-option label="生日" value="birthday" />
        <el-option label="纪念日" value="anniversary" />
        <el-option label="自定义" value="custom" />
      </el-select>
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>
    <el-table :data="reminders" v-loading="loading" stripe border>
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="remind_date" label="提醒日期" width="120" sortable />
      <el-table-column prop="remind_type_display" label="类型" width="90">
        <template #default="{ row }">
          <el-tag :type="row.remind_type === 'birthday' ? 'danger' : row.remind_type === 'anniversary' ? 'warning' : 'info'" size="small">
            {{ row.remind_type_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="message" label="内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status_display" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'handled' ? 'success' : 'info'" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button link type="success" size="small" @click="handleHandle(row.id)">处理</el-button>
            <el-button link type="info" size="small" @click="handleIgnore(row.id)">忽略</el-button>
          </template>
          <span v-else style="color: #909399; font-size: 12px;">{{ row.status_display }}</span>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="loadData" @current-change="loadData" />
    </div>

    <!-- 新建提醒对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建提醒" width="500px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="客户" prop="customer">
          <el-select v-model="createForm.customer" filterable remote :remote-method="searchCustomers"
            placeholder="搜索客户" style="width: 100%;">
            <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="提醒日期" prop="remind_date">
          <el-date-picker v-model="createForm.remind_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="createForm.remind_type" style="width: 100%;">
            <el-option label="自定义" value="custom" />
            <el-option label="生日" value="birthday" />
            <el-option label="纪念日" value="anniversary" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" placeholder="提醒标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="createForm.message" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getReminders, createReminder, handleReminder, ignoreReminder } from '../api/reminder'
import { getCustomers } from '../api/customer'

const reminders = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ status: '', type: '' })
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const customerOptions = ref([])

const createForm = reactive({
  customer: null, remind_date: '', remind_type: 'custom', title: '', message: '',
})

const createRules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  remind_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.status) params.status = filters.status
    if (filters.type) params.remind_type = filters.type
    const data = await getReminders(params)
    reminders.value = data.results || data
    total.value = data.count || reminders.value.length
  } finally { loading.value = false }
}

async function handleHandle(id) { await handleReminder(id); ElMessage.success('已标记处理'); loadData() }
async function handleIgnore(id) { await ignoreReminder(id); ElMessage.success('已忽略'); loadData() }

function searchCustomers(query) {
  if (query) {
    getCustomers({ search: query, page_size: 20 }).then(d => { customerOptions.value = d.results || d })
  }
}

async function handleCreate() {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await createReminder(createForm)
    ElMessage.success('提醒创建成功')
    showCreateDialog.value = false
    Object.assign(createForm, { customer: null, remind_date: '', remind_type: 'custom', title: '', message: '' })
    loadData()
  } finally { creating.value = false }
}

onMounted(() => { loadData() })
</script>
