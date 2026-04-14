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
              <span style="font-weight: 600;">🎂 即将到来的生日/纪念日</span>
              <el-button link type="primary" @click="$router.push('/reminders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="upcomingDates" size="small" stripe v-if="upcomingDates.length">
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
          <el-empty v-else description="暂无即将到来的生日/纪念日" :image-size="60" />
        </el-card>
      </el-col>

      <!-- 今日预订 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">📋 今日预订</span>
              <el-button link type="primary" @click="$router.push('/reservations')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="todayReservations" size="small" stripe v-if="todayReservations.length">
            <el-table-column prop="customer_name" label="客户" width="80" />
            <el-table-column prop="reservation_time" label="时间" width="70" />
            <el-table-column prop="party_size" label="人数" width="60" />
            <el-table-column prop="status_display" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'confirmed' ? 'primary' : 'success'" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="今日暂无预订" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理提醒 -->
    <el-card style="margin-top: 16px;" v-if="pendingReminders.length">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 600;">🔔 待处理提醒</span>
          <el-button link type="primary" @click="$router.push('/reminders')">管理提醒</el-button>
        </div>
      </template>
      <el-table :data="pendingReminders.slice(0, 10)" size="small" stripe>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCustomerStats } from '../api/customer'
import { getTodayReservations } from '../api/reservation'
import { getUpcomingReminders, handleReminder, ignoreReminder } from '../api/reminder'

const stats = ref({})
const todayReservations = ref([])
const pendingReminders = ref([])
const upcomingDates = ref([])

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

async function handleHandle(id) { await handleReminder(id); ElMessage.success('已处理'); loadDashboard() }
async function handleIgnore(id) { await ignoreReminder(id); ElMessage.success('已忽略'); loadDashboard() }

onMounted(() => { loadDashboard() })
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
</style>
