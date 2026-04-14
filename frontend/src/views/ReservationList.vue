<template>
  <div class="page-container">
    <div class="page-header">
      <h2>预订管理</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/reservations/create')">新建预订</el-button>
    </div>
    <div class="filter-bar">
      <el-date-picker v-model="filters.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD"
        style="width: 160px" @change="loadData" />
      <el-select v-model="filters.status" placeholder="预订状态" clearable style="width: 130px" @change="loadData">
        <el-option label="待确认" value="pending" />
        <el-option label="已确认" value="confirmed" />
        <el-option label="已到店" value="arrived" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="filters.store" placeholder="选择门店" clearable style="width: 160px" @change="loadData">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>
    <el-table :data="reservations" v-loading="loading" stripe border>
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="customer_phone" label="电话" width="130" />
      <el-table-column prop="store_name" label="门店" width="120" />
      <el-table-column prop="reservation_date" label="预订日期" width="120" sortable />
      <el-table-column prop="reservation_time" label="时间" width="80" />
      <el-table-column prop="party_size" label="人数" width="70" />
      <el-table-column prop="table_number" label="桌号" width="80" />
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
    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
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
