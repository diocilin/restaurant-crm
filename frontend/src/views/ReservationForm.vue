<template>
  <div class="page-container">
    <div class="page-header">
      <h2>新建预订</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="reservation-form" style="max-width: 600px;">
        <el-form-item label="客户" prop="customer">
          <el-select v-model="form.customer" filterable remote :remote-method="searchCustomers"
            placeholder="搜索客户姓名或手机号" style="width: 100%;">
            <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="门店" prop="store">
          <el-select v-model="form.store" placeholder="选择门店" style="width: 100%;" @change="onStoreOrDateChange">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预订日期" prop="reservation_date">
          <el-date-picker v-model="form.reservation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" @change="onStoreOrDateChange" />
        </el-form-item>
        <el-form-item label="预订时间" prop="reservation_time">
          <el-time-picker v-model="form.reservation_time" value-format="HH:mm:ss" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="预订人数">
          <el-input-number v-model="form.party_size" :min="1" :max="50" />
        </el-form-item>

        <!-- 座位类型选择 -->
        <el-form-item label="座位类型" v-if="seatData" prop="seat_type">
          <el-radio-group v-model="form.seat_type" @change="onSeatTypeChange">
            <el-radio-button value="hall">大堂</el-radio-button>
            <el-radio-button value="room">包间</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 大堂座位选择 -->
        <el-form-item label="大堂桌号" v-if="seatData && form.seat_type === 'hall'" prop="table_number">
          <div v-if="hallSeats.length === 0 && hallOccupied.length === 0" class="seat-empty">
            暂无大堂座位信息
          </div>
          <div v-else-if="hallSeats.length === 0" class="seat-full">
            <el-icon><WarningFilled /></el-icon>
            该类型座位已满，需排队等待
          </div>
          <div v-else class="seat-grid">
            <div
              v-for="seat in hallSeats"
              :key="seat.number"
              class="seat-item"
              :class="{ 'seat-selected': form.table_number === seat.number }"
              @click="form.table_number = seat.number"
            >
              {{ seat.number }}号
            </div>
            <div
              v-for="seat in hallOccupied"
              :key="'occ-' + seat.number"
              class="seat-item seat-occupied"
            >
              {{ seat.number }}号
            </div>
          </div>
        </el-form-item>

        <!-- 包间选择 -->
        <el-form-item label="包间" v-if="seatData && form.seat_type === 'room'" prop="table_area">
          <div v-if="roomSeats.length === 0 && roomOccupied.length === 0" class="seat-empty">
            暂无包间信息
          </div>
          <div v-else-if="roomSeats.length === 0" class="seat-full">
            <el-icon><WarningFilled /></el-icon>
            该类型座位已满，需排队等待
          </div>
          <div v-else class="seat-grid">
            <div
              v-for="room in roomSeats"
              :key="room.id"
              class="seat-item seat-room"
              :class="{ 'seat-selected': form.table_area === room.name }"
              @click="form.table_area = room.name"
            >
              <div class="room-name">{{ room.name }}</div>
              <div class="room-capacity">{{ room.capacity }}人</div>
            </div>
            <div
              v-for="room in roomOccupied"
              :key="'occ-' + room.id"
              class="seat-item seat-room seat-occupied"
            >
              <div class="room-name">{{ room.name }}</div>
              <div class="room-capacity">{{ room.capacity }}人</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'
import { createReservation, getAvailableSeats } from '../api/reservation'
import { getCustomers, getStores } from '../api/customer'

const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const stores = ref([])
const customerOptions = ref([])
const seatData = ref(null)
const seatsLoading = ref(false)

const form = reactive({
  customer: null, store: null, reservation_date: '', reservation_time: '',
  party_size: 1, seat_type: '', table_number: '', table_area: '', notes: '',
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  store: [{ required: true, message: '请选择门店', trigger: 'change' }],
  reservation_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  reservation_time: [{ required: true, message: '请选择时间', trigger: 'change' }],
}

const hallSeats = computed(() => seatData.value?.hall?.available || [])
const hallOccupied = computed(() => seatData.value?.hall?.occupied || [])
const roomSeats = computed(() => seatData.value?.rooms?.available || [])
const roomOccupied = computed(() => seatData.value?.rooms?.occupied || [])

function searchCustomers(query) {
  if (query) {
    getCustomers({ search: query, page_size: 20 }).then(d => { customerOptions.value = d.results || d })
  }
}

async function onStoreOrDateChange() {
  // 重置座位相关字段
  form.seat_type = ''
  form.table_number = ''
  form.table_area = ''
  seatData.value = null

  if (form.store && form.reservation_date) {
    seatsLoading.value = true
    try {
      seatData.value = await getAvailableSeats(form.store, form.reservation_date)
    } catch (e) {
      // handled by interceptor
    } finally {
      seatsLoading.value = false
    }
  }
}

function onSeatTypeChange() {
  form.table_number = ''
  form.table_area = ''
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = { ...form }
    // 清理不需要的字段
    if (payload.seat_type === 'hall') {
      payload.table_area = ''
    } else if (payload.seat_type === 'room') {
      payload.table_number = ''
    }
    await createReservation(payload)
    ElMessage.success('预订创建成功')
    router.push('/reservations')
  } finally { saving.value = false }
}

onMounted(() => { getStores().then(d => { stores.value = d.results || d }) })
</script>

<style scoped>
.seat-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
}

.seat-item {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  height: 40px;
  padding: 4px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  color: #303133;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.seat-item:hover {
  border-color: #409eff;
  color: #409eff;
}

.seat-item.seat-selected {
  background-color: #409eff;
  border-color: #409eff;
  color: #fff;
}

.seat-item.seat-occupied {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

.seat-item.seat-room {
  flex-direction: column;
  min-width: 80px;
  height: auto;
  padding: 6px 12px;
}

.room-name {
  font-size: 14px;
  font-weight: 500;
}

.room-capacity {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.seat-item.seat-room.seat-selected .room-capacity {
  color: rgba(255, 255, 255, 0.8);
}

.seat-empty {
  color: #909399;
  font-size: 14px;
}

.seat-full {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e6a23c;
  font-size: 14px;
}
</style>
