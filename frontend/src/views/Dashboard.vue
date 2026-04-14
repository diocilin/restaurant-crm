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
              <span style="font-weight: 600;">📋 今日预订</span>
              <el-button link type="primary" @click="$router.push('/reservations')">查看全部</el-button>
            </div>
          </template>
          <!-- 桌面端表格 -->
          <el-table :data="todayReservations" size="small" stripe v-if="todayReservations.length" class="desktop-table">
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
                <span class="dash-card-label">{{ row.reservation_time }} · {{ row.party_size }}人</span>
                <span class="dash-card-label">{{ row.notes || '-' }}</span>
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
          <span style="font-weight: 600;">🔔 待处理提醒</span>
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

/* 默认隐藏桌面表格，显示移动卡片 */
.desktop-table {
  display: none;
}
.mobile-card-list {
  display: block;
}

/* 移动端卡片条目 */
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

/* 桌面端 - 显示表格，隐藏卡片 */
@media (min-width: 768px) {
  .desktop-table {
    display: block;
    width: 100%;
  }
  .mobile-card-list {
    display: none;
  }
}

/* 竖屏手机优化 */
@media (max-width: 480px) {
  .stat-card {
    padding: 10px 4px;
  }
  .stat-card .el-icon {
    margin-bottom: 4px;
  }
  .stat-card .stat-value {
    font-size: 20px;
  }
  .stat-card .stat-label {
    font-size: 11px;
  }
  .dash-card-item {
    padding: 8px 0;
  }
  .dash-card-name {
    font-size: 13px;
  }
  .dash-card-label {
    font-size: 11px;
  }
  .dash-card-title {
    font-size: 12px;
  }
  .dash-card-actions .el-button {
    padding: 5px 10px;
    font-size: 12px;
  }
}
</style>
