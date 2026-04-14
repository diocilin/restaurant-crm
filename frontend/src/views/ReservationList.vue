<template>
  <div class="page-container">
    <div class="page-header">
      <h2>预订管理</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/reservations/create')">新建预订</el-button>
    </div>
    <div class="filter-bar">
      <el-date-picker v-model="filters.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD"
        class="filter-date" @change="loadData" />
      <el-select v-model="filters.status" placeholder="预订状态" clearable class="filter-status" @change="loadData">
        <el-option label="待确认" value="pending" />
        <el-option label="已确认" value="confirmed" />
        <el-option label="已到店" value="arrived" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="filters.store" placeholder="选择门店" clearable class="filter-store" @change="loadData">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>

    <!-- 桌面端表格 -->
    <el-table :data="reservations" v-loading="loading" stripe border class="desktop-table">
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="customer_phone" label="电话" width="130" />
      <el-table-column prop="store_name" label="门店" width="120" />
      <el-table-column prop="reservation_date" label="预订日期" width="120" sortable />
      <el-table-column prop="reservation_time" label="时间" width="80" />
      <el-table-column prop="party_size" label="人数" width="70" />
      <el-table-column label="座位" width="120">
        <template #default="{ row }">
          {{ formatSeatDisplay(row) }}
        </template>
      </el-table-column>
      <el-table-column prop="status_display" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="notes" label="备注" show-overflow-tooltip />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" link type="success" size="small" @click="handleConfirm(row.id)">确认</el-button>
          <el-button v-if="row.status === 'confirmed'" link type="primary" size="small" @click="handleArrive(row.id)">到店</el-button>
          <el-button v-if="row.status !== 'arrived' && row.status !== 'cancelled'" link type="warning" size="small" @click="handleCancel(row.id)">取消</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片列表 -->
    <div class="mobile-card-list" v-loading="loading">
      <el-card v-for="row in reservations" :key="row.id" class="res-card" shadow="hover">
        <div class="card-header">
          <span class="card-name">{{ row.customer_name }}</span>
          <el-tag :type="statusType(row.status)" size="small">{{ row.status_display }}</el-tag>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="card-label">电话</span>
            <span class="card-value">{{ row.customer_phone }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">日期</span>
            <span class="card-value">{{ row.reservation_date }} {{ row.reservation_time }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">门店</span>
            <span class="card-value">{{ row.store_name || '-' }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">人数/座位</span>
            <span class="card-value">{{ row.party_size }}人{{ formatSeatDisplay(row) ? ' / ' + formatSeatDisplay(row) : '' }}</span>
          </div>
          <div class="card-row" v-if="row.notes">
            <span class="card-label">备注</span>
            <span class="card-value">{{ row.notes }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleConfirm(row.id)">确认</el-button>
          <el-button v-if="row.status === 'confirmed'" type="primary" size="small" @click="handleArrive(row.id)">到店</el-button>
          <el-button v-if="row.status !== 'arrived' && row.status !== 'cancelled'" type="warning" size="small" plain @click="handleCancel(row.id)">取消</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" size="small" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </el-card>
      <el-empty v-if="!loading && reservations.length === 0" description="暂无预订" />
    </div>

    <div class="pagination-wrap">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="loadData" @current-change="loadData" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getReservations, deleteReservation, confirmReservation, cancelReservation, arriveReservation } from '../api/reservation'
import { getStores } from '../api/customer'

const router = useRouter()

const reservations = ref([])
const stores = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ date: '', status: '', store: null })

function statusType(s) {
  return { pending: 'warning', confirmed: 'primary', arrived: 'success', cancelled: 'info', noshow: 'danger' }[s] || 'info'
}

function formatSeatDisplay(row) {
  return row.seat_info || row.table_numbers || '-'
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.date) params.reservation_date = filters.date
    if (filters.status) params.status = filters.status
    if (filters.store) params.store = filters.store
    const data = await getReservations(params)
    reservations.value = data.results || data
    total.value = data.count || reservations.value.length
  } finally { loading.value = false }
}

async function handleConfirm(id) { await confirmReservation(id); ElMessage.success('已确认'); loadData() }
async function handleArrive(id) {
  const res = await arriveReservation(id)
  loadData()
  if (res.dining_record_id) {
    ElMessage.success('已标记到店，就餐记录已自动创建')
  } else {
    ElMessage.success('已标记到店')
  }
}
async function handleCancel(id) { await cancelReservation(id); ElMessage.success('已取消'); loadData() }
async function handleDelete(id) { await deleteReservation(id); ElMessage.success('已删除'); loadData() }

onMounted(() => {
  loadData()
  getStores().then(d => { stores.value = d.results || d })
})
</script>

<style scoped>
/* 筛选栏 - 桌面端横向排列 */
.filter-bar {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.filter-date { width: 160px !important; }
.filter-status { width: 130px !important; }
.filter-store { width: 160px !important; }

/* 分页 */
.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 桌面端：显示表格，隐藏卡片 */
.desktop-table { display: block; width: 100%; }
.mobile-card-list { display: none; }

/* 卡片样式（MobileLayout :deep() 控制显示） */
.res-card { margin-bottom: 12px; }
.res-card :deep(.el-card__body) { padding: 12px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}
.card-name { font-size: 16px; font-weight: 600; color: #303133; }
.card-body { display: flex; flex-direction: column; gap: 6px; }
.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  line-height: 1.6;
}
.card-label { color: #909399; flex-shrink: 0; }
.card-value { color: #303133; text-align: right; word-break: break-all; }
.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}
.card-actions .el-button { flex: 1; }
</style>
