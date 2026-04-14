<template>
  <div class="page-container">
    <div class="page-header">
      <h2>就餐记录</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/dining/create')">新建记录</el-button>
    </div>
    <div class="filter-bar">
      <el-input v-model="filters.search" placeholder="搜索客户姓名/手机号" clearable class="filter-search"
        @keyup.enter="loadData" />
      <el-select v-model="filters.store" placeholder="选择门店" clearable class="filter-store" @change="loadData">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
        end-placeholder="结束日期" value-format="YYYY-MM-DD" class="filter-date" @change="loadData" />
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>

    <!-- 桌面端：表格 -->
    <el-table :data="records" v-loading="loading" stripe border class="desktop-table">
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="store_name" label="门店" width="120" />
      <el-table-column prop="dining_date" label="就餐时间" width="170" sortable />
      <el-table-column prop="party_size" label="人数" width="70" />
      <el-table-column prop="table_number" label="桌号" width="80" />
      <el-table-column prop="total_amount" label="消费金额" width="100" sortable>
        <template #default="{ row }">¥{{ row.total_amount }}</template>
      </el-table-column>
      <el-table-column prop="satisfaction" label="满意度" width="120">
        <template #default="{ row }">
          <span v-if="row.satisfaction" style="color: #f7ba2a;">{{ '★'.repeat(row.satisfaction) }}{{ '☆'.repeat(5 - row.satisfaction) }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button link type="primary" size="small" @click="$router.push(`/customers/${row.customer}`)">查看客户</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端：卡片列表 -->
    <div v-loading="loading" class="mobile-card-list">
      <el-card v-for="row in records" :key="row.id" class="dining-card" shadow="hover">
        <div class="card-header">
          <div class="card-name">
            <span class="name-text">{{ row.customer_name }}</span>
            <span class="store-text">{{ row.store_name }}</span>
          </div>
          <span class="amount-text">¥{{ row.total_amount }}</span>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="card-label">就餐时间</span>
            <span class="card-value">{{ row.dining_date || '-' }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">人数 / 桌号</span>
            <span class="card-value">{{ row.party_size }}人 / {{ row.table_number || '-' }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">满意度</span>
            <span class="card-value">
              <span v-if="row.satisfaction" style="color: #f7ba2a;">{{ '★'.repeat(row.satisfaction) }}{{ '☆'.repeat(5 - row.satisfaction) }}</span>
              <span v-else>-</span>
            </span>
          </div>
          <div class="card-row" v-if="row.notes">
            <span class="card-label">备注</span>
            <span class="card-value">{{ row.notes }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button type="primary" size="small" plain @click="$router.push(`/customers/${row.customer}`)">查看客户</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" size="small" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </el-card>
    </div>

    <div class="pagination-wrapper">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="loadData" @current-change="loadData" />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑就餐记录" class="edit-dialog">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="客户">
          <el-input :value="editForm.customer_name" disabled />
        </el-form-item>
        <el-form-item label="就餐时间">
          <el-date-picker v-model="editForm.dining_date" type="datetime" placeholder="选择时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="就餐人数">
          <el-input-number v-model="editForm.party_size" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="桌号">
          <el-input v-model="editForm.table_number" placeholder="如：A01" />
        </el-form-item>
        <el-form-item label="消费金额">
          <el-input-number v-model="editForm.total_amount" :min="0" :precision="2" :step="10" />
        </el-form-item>
        <el-form-item label="满意度">
          <el-rate v-model="editForm.satisfaction" :max="5" show-text />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getDiningRecords, deleteDiningRecord, updateDiningRecord } from '../api/dining'
import { getStores } from '../api/customer'

const records = ref([])
const stores = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ search: '', store: null, dateRange: null })

// 编辑相关
const editDialogVisible = ref(false)
const saving = ref(false)
const editForm = reactive({
  id: null,
  customer_name: '',
  dining_date: '',
  party_size: 1,
  table_number: '',
  total_amount: 0,
  satisfaction: null,
  notes: '',
})

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.search) params.search = filters.search
    if (filters.store) params.store = filters.store
    if (filters.dateRange) {
      params.dining_date_after = filters.dateRange[0]
      params.dining_date_before = filters.dateRange[1]
    }
    const data = await getDiningRecords(params)
    records.value = data.results || data
    total.value = data.count || records.value.length
  } finally { loading.value = false }
}

function openEditDialog(row) {
  editForm.id = row.id
  editForm.customer_name = row.customer_name
  editForm.dining_date = row.dining_date
  editForm.party_size = row.party_size
  editForm.table_number = row.table_number || ''
  editForm.total_amount = parseFloat(row.total_amount) || 0
  editForm.satisfaction = row.satisfaction
  editForm.notes = row.notes || ''
  editDialogVisible.value = true
}

async function handleSaveEdit() {
  saving.value = true
  try {
    await updateDiningRecord(editForm.id, {
      dining_date: editForm.dining_date,
      party_size: editForm.party_size,
      table_number: editForm.table_number,
      total_amount: editForm.total_amount,
      satisfaction: editForm.satisfaction || null,
      notes: editForm.notes,
    })
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  await deleteDiningRecord(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  getStores().then(d => { stores.value = d.results || d })
})
</script>

<style scoped>
/* 筛选栏默认（移动端）：纵向排列 */
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.filter-search,
.filter-store,
.filter-date {
  width: 100% !important;
}

/* 桌面端筛选栏：横向排列 */
@media (min-width: 768px) {
  .filter-bar {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
  }
  .filter-search {
    width: 220px !important;
  }
  .filter-store {
    width: 160px !important;
  }
  .filter-date {
    width: 260px !important;
  }
}

/* 桌面端：显示表格，隐藏卡片 */
.desktop-table {
  display: none;
}
.mobile-card-list {
  display: block;
}

@media (min-width: 768px) {
  .desktop-table {
    display: block;
    width: 100%;
  }
  .mobile-card-list {
    display: none;
  }
}

/* 移动端卡片样式 */
.dining-card {
  margin-bottom: 12px;
}
.dining-card :deep(.el-card__body) {
  padding: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}
.card-name {
  display: flex;
  align-items: center;
  gap: 8px;
}
.name-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.store-text {
  font-size: 13px;
  color: #909399;
}
.amount-text {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}
.card-body {
  margin-bottom: 10px;
}
.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.5;
}
.card-label {
  color: #909399;
  flex-shrink: 0;
  margin-right: 12px;
}
.card-value {
  color: #303133;
  text-align: right;
  word-break: break-all;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

/* 分页 */
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 767px) {
  .pagination-wrapper {
    justify-content: center;
  }
  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}

/* 竖屏手机进一步优化 */
@media (max-width: 480px) {
  .dining-card {
    margin-bottom: 8px;
  }
  .dining-card :deep(.el-card__body) {
    padding: 10px;
  }
  .card-header {
    margin-bottom: 8px;
    padding-bottom: 6px;
  }
  .name-text {
    font-size: 15px;
  }
  .amount-text {
    font-size: 18px;
  }
  .card-body {
    margin-bottom: 8px;
  }
  .card-row {
    padding: 3px 0;
    font-size: 13px;
  }
  .card-actions {
    gap: 6px;
    padding-top: 6px;
  }
  .card-actions .el-button {
    padding: 6px 8px;
    font-size: 12px;
  }

  /* 编辑对话框竖屏适配 */
  .edit-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 2vh auto !important;
  }
  .edit-dialog :deep(.el-form-item__label) {
    width: 70px !important;
    min-width: 70px !important;
    font-size: 13px;
  }
  .edit-dialog :deep(.el-form-item__content) {
    flex: 1;
  }
  .edit-dialog :deep(.el-input),
  .edit-dialog :deep(.el-select),
  .edit-dialog :deep(.el-date-editor),
  .edit-dialog :deep(.el-textarea) {
    width: 100% !important;
  }
}
</style>
