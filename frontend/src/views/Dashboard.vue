<template>
  <div class="page-container">
    <div class="page-header">
      <h2>首页看板</h2>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <el-icon size="32" color="#409EFF"><User /></el-icon>
          <div class="stat-value">{{ stats.total_customers || 0 }}</div>
          <div class="stat-label">客户总数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <el-icon size="32" color="#67C23A"><UserFilled /></el-icon>
          <div class="stat-value">{{ stats.new_this_week || 0 }}</div>
          <div class="stat-label">本周新增</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <el-icon size="32" color="#E6A23C"><Calendar /></el-icon>
          <div class="stat-value">{{ todayReservations.length }}</div>
          <div class="stat-label">今日预订</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <el-icon size="32" color="#F56C6C"><Bell /></el-icon>
          <div class="stat-value">{{ pendingReminders.length }}</div>
          <div class="stat-label">待处理提醒</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 即将到来的生日/纪念日 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">即将到来的生日/纪念日</span>
              <el-button link type="primary" @click="$router.push('/reminders')">查看全部</el-button>
            </div>
          </template>
          <!-- 桌面端表格 -->
          <el-table :data="upcomingDates" size="small" stripe v-if="upcomingDates.length" class="desktop-table">
            <el-table-column prop="name" label="客户" width="80" />
            <el-table-column prop="phone" label="手机号" width="120" />
            <el-table-column label="日期" width="80">
              <template #default="{ row }">{{ row.birthday }}</template>
            </el-table-column>
            <el-table-column label="倒计时" width="80">
              <template #default="{ row }">
                <el-tag :type="row.days_until === 0 ? 'danger' : row.days_until <= 3 ? 'warning' : 'info'" size="small">
                  {{ row.days_until === 0 ? '今天' : row.days_until + '天后' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <!-- 移动端卡片 -->
          <div class="mobile-card-list" v-if="upcomingDates.length">
            <div v-for="row in upcomingDates" :key="row.name" class="dash-card-item">
              <div class="dash-card-row">
                <span class="dash-card-name">{{ row.name }}</span>
                <el-tag :type="row.days_until === 0 ? 'danger' : row.days_until <= 3 ? 'warning' : 'info'" size="small">
                  {{ row.days_until === 0 ? '今天' : row.days_until + '天后' }}
                </el-tag>
              </div>
              <div class="dash-card-row">
                <span class="dash-card-label">{{ row.phone }}</span>
                <span class="dash-card-label">{{ row.birthday }}</span>
              </div>
            </div>
          </div>
          <el-empty v-if="!upcomingDates.length" description="暂无即将到来的生日/纪念日" :image-size="60" />
        </el-card>
      </el-col>

      <!-- 今日预订 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">今日预订</span>
              <el-button link type="primary" @click="$router.push('/reservations')">查看全部</el-button>
            </div>
          </template>
          <!-- 桌面端表格 -->
          <el-table :data="todayReservations" size="small" stripe v-if="todayReservations.length" class="desktop-table">
            <el-table-column prop="customer_name" label="客户" width="80" />
            <el-table-column prop="customer_phone" label="电话" width="120" />
            <el-table-column prop="reservation_time" label="时间" width="70" />
            <el-table-column prop="party_size" label="人数" width="60" />
            <el-table-column prop="seat_info" label="座位" min-width="160" show-overflow-tooltip />
            <el-table-column prop="status_display" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'confirmed' ? 'primary' : 'success'" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
          </el-table>
          <!-- 移动端卡片 -->
          <div class="mobile-card-list" v-if="todayReservations.length">
            <div v-for="row in todayReservations" :key="row.id" class="dash-card-item">
              <div class="dash-card-row">
                <span class="dash-card-name">{{ row.customer_name }}</span>
                <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'confirmed' ? 'primary' : 'success'" size="small">
                  {{ row.status_display }}
                </el-tag>
              </div>
              <div class="dash-card-row">
                <span class="dash-card-label">{{ row.customer_phone }}</span>
              </div>
              <div class="dash-card-row">
                <span class="dash-card-label">{{ row.reservation_time }} · {{ row.party_size }}人</span>
              </div>
              <div class="dash-card-row" v-if="row.seat_info">
                <span class="dash-card-label">座位：{{ row.seat_info }}</span>
              </div>
              <div class="dash-card-row" v-if="row.notes">
                <span class="dash-card-label">{{ row.notes }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="今日暂无预订" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理提醒 -->
    <el-card style="margin-top: 16px;" v-if="pendingReminders.length">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">待处理提醒</span>
          <el-button link type="primary" @click="$router.push('/reminders')">管理提醒</el-button>
        </div>
      </template>
      <!-- 桌面端表格 -->
      <el-table :data="pendingReminders.slice(0, 10)" size="small" stripe class="desktop-table">
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column prop="remind_date" label="日期" width="110" />
        <el-table-column prop="remind_type_display" label="类型" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="success" size="small" @click="handleHandle(row.id)">处理</el-button>
            <el-button link type="info" size="small" @click="handleIgnore(row.id)">忽略</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 移动端卡片 -->
      <div class="mobile-card-list">
        <div v-for="row in pendingReminders.slice(0, 10)" :key="row.id" class="dash-card-item">
          <div class="dash-card-row">
            <span class="dash-card-name">{{ row.customer_name }}</span>
            <el-tag :type="row.remind_type === 'birthday' ? 'danger' : row.remind_type === 'anniversary' ? 'warning' : 'info'" size="small">
              {{ row.remind_type_display }}
            </el-tag>
          </div>
          <div class="dash-card-row">
            <span class="dash-card-label">{{ row.remind_date }}</span>
          </div>
          <div class="dash-card-title">{{ row.title }}</div>
          <div class="dash-card-actions">
            <el-button type="success" size="small" @click="handleHandle(row.id)">处理</el-button>
            <el-button type="info" size="small" plain @click="handleIgnore(row.id)">忽略</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 未来10天预订概览 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">未来10天预订概览</span>
          <el-button link type="primary" @click="$router.push('/reservations')">查看全部</el-button>
        </div>
      </template>
      <div v-loading="overviewLoading">
        <!-- 桌面端表格 -->
        <el-table :data="overviewData" size="small" stripe class="desktop-table" v-if="overviewData.length">
          <el-table-column label="日期" width="100">
            <template #default="{ row }">
              <div :class="{ 'overview-today': row.is_today }">
                <div class="overview-date">{{ row.date_short }}</div>
                <div class="overview-weekday">{{ row.weekday }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="预订详情" min-width="300">
            <template #default="{ row }">
              <div v-if="row.stores && row.stores.length" class="overview-stores">
                <div v-for="store in row.stores" :key="store.store_name" class="overview-store-row">
                  <span class="overview-store-name">{{ store.store_name }}</span>
                  <span class="overview-seats">
                    <span class="overview-seat-item" :class="getSeatColorClass(store.booked_rooms, store.total_rooms)">
                      包间 {{ store.booked_rooms }}/{{ store.total_rooms }}
                    </span>
                    <span class="overview-seat-item" :class="getSeatColorClass(store.booked_hall, store.total_hall)">
                      大堂 {{ store.booked_hall }}/{{ store.total_hall }}
                    </span>
                  </span>
                </div>
              </div>
              <span v-else class="overview-no-data">暂无数据</span>
            </template>
          </el-table-column>
          <el-table-column label="总计" width="80">
            <template #default="{ row }">
              <span v-if="row.stores && row.stores.length">
                {{ row.stores.reduce((sum, s) => sum + (s.total_reservations || 0), 0) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 移动端卡片 -->
        <div class="mobile-card-list">
          <div v-for="day in overviewData" :key="day.date" class="overview-card">
            <div class="overview-card-header" :class="{ 'overview-today': day.is_today }">
              <div class="overview-card-date">
                <span class="overview-date">{{ day.date_short }}</span>
                <span class="overview-weekday">{{ day.weekday }}</span>
              </div>
              <el-tag v-if="day.is_today" type="danger" size="small">今天</el-tag>
            </div>
            <div v-if="day.stores && day.stores.length" class="overview-card-body">
              <div v-for="store in day.stores" :key="store.store_name" class="overview-store-row">
                <span class="overview-store-name">{{ store.store_name }}</span>
                <div class="overview-seat-tags">
                  <span class="overview-seat-item" :class="getSeatColorClass(store.booked_rooms, store.total_rooms)">
                    包间 {{ store.booked_rooms }}/{{ store.total_rooms }}
                  </span>
                  <span class="overview-seat-item" :class="getSeatColorClass(store.booked_hall, store.total_hall)">
                    大堂 {{ store.booked_hall }}/{{ store.total_hall }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="overview-no-data">暂无数据</div>
          </div>
          <el-empty v-if="!overviewLoading && overviewData.length === 0" description="暂无概览数据" :image-size="60" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCustomerStats } from '../api/customer'
import { getTodayReservations, getReservationOverview } from '../api/reservation'
import { getUpcomingReminders, handleReminder, ignoreReminder } from '../api/reminder'

const stats = ref({})
const todayReservations = ref([])
const pendingReminders = ref([])
const upcomingDates = ref([])
const overviewData = ref([])
const overviewLoading = ref(false)

function getSeatColorClass(booked, total) {
  if (!total || total === 0) return 'seat-empty'
  if (booked >= total) return 'seat-full'
  if (booked / total > 0.5) return 'seat-busy'
  if (booked > 0) return 'seat-some'
  return 'seat-empty'
}

async function loadDashboard() {
  try {
    const [statsData, todayRes, upcomingRem] = await Promise.all([
      getCustomerStats(),
      getTodayReservations(),
      getUpcomingReminders(),
    ])
    stats.value = statsData
    todayReservations.value = todayRes.results || todayRes || []
    pendingReminders.value = upcomingRem.results || upcomingRem || []
    upcomingDates.value = statsData.upcoming_birthdays || []
  } catch (e) {
    // handled by interceptor
  }
}

async function loadOverview() {
  overviewLoading.value = true
  try {
    const data = await getReservationOverview()
    overviewData.value = data || []
  } catch (e) {
    // handled by interceptor
  } finally {
    overviewLoading.value = false
  }
}

async function handleHandle(id) { await handleReminder(id); ElMessage.success('已处理'); loadDashboard() }
async function handleIgnore(id) { await ignoreReminder(id); ElMessage.success('已忽略'); loadDashboard() }

onMounted(() => {
  loadDashboard()
  loadOverview()
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 16px 8px;
  cursor: default;
}

.stat-card .el-icon {
  margin-bottom: 8px;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-card .stat-label {
  font-size: 13px;
  color: #909399;
}

/* 桌面端：显示表格，隐藏卡片 */
.desktop-table {
  display: block;
  width: 100%;
}
.mobile-card-list {
  display: none;
}

/* 卡片样式（MobileLayout :deep() 控制显示） */
.dash-card-item {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}
.dash-card-item:last-child {
  border-bottom: none;
}
.dash-card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.dash-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.dash-card-label {
  font-size: 12px;
  color: #909399;
}
.dash-card-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}
.dash-card-actions {
  display: flex;
  gap: 8px;
}

/* 预订概览样式 */
.overview-today {
  font-weight: 700;
  color: #f56c6c;
}

.overview-date {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.overview-today .overview-date {
  color: #f56c6c;
}

.overview-weekday {
  font-size: 12px;
  color: #909399;
}

.overview-stores {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overview-store-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.overview-store-name {
  font-size: 13px;
  color: #606266;
  min-width: 60px;
  flex-shrink: 0;
}

.overview-seats {
  display: flex;
  gap: 8px;
}

.overview-seat-item {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
}

/* 座位颜色状态 */
.seat-full {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.seat-busy {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #f5dab1;
}

.seat-some {
  background-color: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.seat-empty {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #e9e9eb;
}

.overview-no-data {
  color: #c0c4cc;
  font-size: 13px;
}

/* 移动端概览卡片 */
.overview-card {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.overview-card:last-child {
  border-bottom: none;
}

.overview-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.overview-card-date {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.overview-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.overview-seat-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
