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
          <el-select v-model="form.store" placeholder="选择门店" style="width: 100%;" @change="loadSeats">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预订日期" prop="reservation_date">
          <el-date-picker v-model="form.reservation_date" type="date" value-format="YYYY-MM-DD"
            placeholder="请选择预订日期" style="width: 100%;" @change="loadSeats" />
        </el-form-item>
        <el-form-item label="预订时间" prop="reservation_time">
          <el-time-picker v-model="form.reservation_time" value-format="HH:mm:ss"
            placeholder="请选择预订时间" style="width: 100%;" @change="loadSeats" />
        </el-form-item>
        <el-form-item label="预订人数">
          <el-input-number v-model="form.party_size" :min="1" :max="50" />
        </el-form-item>

        <!-- 座位类型（复选框，可同时选大厅和包间） -->
        <el-form-item label="座位类型">
          <el-checkbox-group v-model="selectedSeatTypes" @change="onSeatTypeChange">
            <el-checkbox label="hall">大堂</el-checkbox>
            <el-checkbox label="room">包间</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 未选门店/日期/时间时的提示 -->
        <el-form-item v-if="selectedSeatTypes.length > 0 && (!form.store || !form.reservation_date || !form.reservation_time)">
          <div class="seat-hint">
            <el-icon><InfoFilled /></el-icon>
            请先选择门店、预订日期和预订时间，以查看可用座位
          </div>
        </el-form-item>

        <!-- 加载中 -->
        <el-form-item v-if="selectedSeatTypes.length > 0 && form.store && form.reservation_date && form.reservation_time && seatsLoading">
          <div class="seat-hint">加载座位信息中...</div>
        </el-form-item>

        <!-- 大堂座位选择（多选） -->
        <el-form-item label="大堂桌号" v-if="showHall && seatData && !seatsLoading">
          <div v-if="hallSeats.length === 0 && hallOccupied.length === 0" class="seat-empty">
            暂无大堂座位信息
          </div>
          <div v-else-if="hallSeats.length === 0" class="seat-full">
            <el-icon><WarningFilled /></el-icon>
            大堂座位已满，需排队等待
          </div>
          <div v-else>
            <div class="seat-multi-hint">点击选择桌号（可多选，已选 {{ selectedHallNumbers.length }} 个）</div>
            <div class="seat-grid">
              <div
                v-for="seat in hallSeats"
                :key="seat.number"
                class="seat-item"
                :class="{ 'seat-selected': selectedHallNumbers.includes(seat.number) }"
                @click="toggleHallSeat(seat.number)"
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
          </div>
        </el-form-item>

        <!-- 包间选择（多选） -->
        <el-form-item label="包间" v-if="showRoom && seatData && !seatsLoading">
          <div v-if="roomSeats.length === 0 && roomOccupied.length === 0" class="seat-empty">
            暂无包间信息
          </div>
          <div v-else-if="roomSeats.length === 0" class="seat-full">
            <el-icon><WarningFilled /></el-icon>
            包间已满，需排队等待
          </div>
          <div v-else>
            <div class="seat-multi-hint">点击选择包间（可多选，已选 {{ selectedRoomIds.length }} 个）</div>
            <div class="seat-grid">
              <div
                v-for="room in roomSeats"
                :key="room.id"
                class="seat-item seat-room"
                :class="{ 'seat-selected': selectedRoomIds.includes(room.id) }"
                @click="toggleRoom(room)"
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
          </div>
        </el-form-item>

        <!-- 翻台提示 -->
        <el-form-item v-if="seatData && !seatsLoading">
          <div class="seat-turnover-hint">
            <el-icon><InfoFilled /></el-icon>
            座位锁定时段：预订时间前1小时至后2小时，超出时段可翻台预订
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
import { WarningFilled, InfoFilled } from '@element-plus/icons-vue'
import { createReservation } from '../api/reservation'
import { getCustomers, getStores } from '../api/customer'
import request from '../api/request'

const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const stores = ref([])
const customerOptions = ref([])
const seatData = ref(null)
const seatsLoading = ref(false)

// 座位类型复选（可同时选大厅和包间）
const selectedSeatTypes = ref([])
// 多选座位
const selectedHallNumbers = ref([])
const selectedRoomIds = ref([])

const showHall = computed(() => selectedSeatTypes.value.includes('hall'))
const showRoom = computed(() => selectedSeatTypes.value.includes('room'))

const form = reactive({
  customer: null, store: null, reservation_date: '', reservation_time: '',
  party_size: 1, notes: '',
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

function toggleHallSeat(number) {
  const idx = selectedHallNumbers.value.indexOf(number)
  if (idx >= 0) {
    selectedHallNumbers.value.splice(idx, 1)
  } else {
    selectedHallNumbers.value.push(number)
  }
}

function toggleRoom(room) {
  const idx = selectedRoomIds.value.indexOf(room.id)
  if (idx >= 0) {
    selectedRoomIds.value.splice(idx, 1)
  } else {
    selectedRoomIds.value.push(room.id)
  }
}

async function loadSeats() {
  seatData.value = null
  selectedHallNumbers.value = []
  selectedRoomIds.value = []

  if (form.store && form.reservation_date && form.reservation_time) {
    seatsLoading.value = true
    try {
      seatData.value = await request.get('/reservations/list/available_seats/', {
        params: {
          store: form.store,
          date: form.reservation_date,
          time: form.reservation_time,
        }
      })
    } catch (e) {
      // handled by interceptor
    } finally {
      seatsLoading.value = false
    }
  }
}

function onSeatTypeChange() {
  selectedHallNumbers.value = []
  selectedRoomIds.value = []
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 检查是否选了座位
  const needHall = selectedSeatTypes.value.includes('hall')
  const needRoom = selectedSeatTypes.value.includes('room')
  if (needHall && selectedHallNumbers.value.length === 0) {
    ElMessage.warning('请至少选择一个大堂桌号')
    return
  }
  if (needRoom && selectedRoomIds.value.length === 0) {
    ElMessage.warning('请至少选择一个包间')
    return
  }
  if (!needHall && !needRoom) {
    ElMessage.warning('请选择至少一种座位类型')
    return
  }

  saving.value = true
  try {
    let count = 0

    // 创建大堂预订
    if (needHall) {
      for (const number of selectedHallNumbers.value) {
        await createReservation({
          customer: form.customer,
          store: form.store,
          reservation_date: form.reservation_date,
          reservation_time: form.reservation_time,
          party_size: form.party_size,
          seat_type: 'hall',
          table_number: number,
          notes: form.notes,
        })
        count++
      }
    }

    // 创建包间预订
    if (needRoom) {
      for (const roomId of selectedRoomIds.value) {
        await createReservation({
          customer: form.customer,
          store: form.store,
          reservation_date: form.reservation_date,
          reservation_time: form.reservation_time,
          party_size: form.party_size,
          seat_type: 'room',
          table_area: roomId,
          notes: form.notes,
        })
        count++
      }
    }

    ElMessage.success(`预订创建成功（${count}个座位）`)
    router.push('/reservations')
  } catch (e) {
    // handled by interceptor
  } finally {
    saving.value = false
  }
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

.seat-multi-hint {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.seat-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

.seat-turnover-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
  font-size: 12px;
}

.seat-item {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  height: 40px;
  padding: 4px 12px;
  border: 2px solid #dcdfe6;
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
