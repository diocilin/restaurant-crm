<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <h2>客户详情</h2>
      <div>
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="$router.push(`/customers/${id}/edit`)">编辑</el-button>
      </div>
    </div>

    <template v-if="customer">
      <!-- 基本信息 -->
      <el-card style="margin-bottom: 16px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 600;">基本信息</span>
            <el-tag :type="customer.level === 'svip' ? 'danger' : customer.level === 'vip' ? 'warning' : 'info'">
              {{ customer.level === 'svip' ? 'SVIP' : customer.level === 'vip' ? 'VIP' : '普通客户' }}
            </el-tag>
          </div>
        </template>
        <!-- 桌面端描述列表 -->
        <el-descriptions :column="3" border class="desktop-desc">
          <el-descriptions-item label="姓名">{{ customer.name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ customer.phone }}</el-descriptions-item>
          <el-descriptions-item label="微信号">{{ customer.wechat || '-' }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ customer.gender === 'M' ? '男' : customer.gender === 'F' ? '女' : '未知' }}</el-descriptions-item>
          <el-descriptions-item label="生日">{{ customer.birthday || '-' }}</el-descriptions-item>
          <el-descriptions-item label="纪念日">{{ customer.anniversary || '-' }}</el-descriptions-item>
          <el-descriptions-item label="常去门店">{{ customer.store_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ customer.created_at }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">{{ customer.notes || '-' }}</el-descriptions-item>
        </el-descriptions>
        <!-- 移动端信息卡片 -->
        <div class="mobile-info-card">
          <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ customer.name }}</span></div>
          <div class="info-row"><span class="info-label">手机号</span><span class="info-value">{{ customer.phone }}</span></div>
          <div class="info-row" v-if="customer.wechat"><span class="info-label">微信号</span><span class="info-value">{{ customer.wechat }}</span></div>
          <div class="info-row"><span class="info-label">性别</span><span class="info-value">{{ customer.gender === 'M' ? '男' : customer.gender === 'F' ? '女' : '未知' }}</span></div>
          <div class="info-row" v-if="customer.birthday"><span class="info-label">生日</span><span class="info-value">{{ customer.birthday }}</span></div>
          <div class="info-row" v-if="customer.anniversary"><span class="info-label">纪念日</span><span class="info-value">{{ customer.anniversary }}</span></div>
          <div class="info-row" v-if="customer.store_name"><span class="info-label">常去门店</span><span class="info-value">{{ customer.store_name }}</span></div>
          <div class="info-row"><span class="info-label">创建时间</span><span class="info-value">{{ customer.created_at }}</span></div>
          <div class="info-row" v-if="customer.notes"><span class="info-label">备注</span><span class="info-value">{{ customer.notes }}</span></div>
        </div>
        <div style="margin-top: 12px;" v-if="customer.tags && customer.tags.length">
          <span style="color: #909399; margin-right: 8px;">标签：</span>
          <el-tag v-for="t in customer.tags" :key="t.id" :color="t.color" style="margin-right: 6px; color: #fff;">
            {{ t.name }}
          </el-tag>
        </div>
      </el-card>

      <!-- 消费统计 -->
      <el-row :gutter="12" style="margin-bottom: 16px;">
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">{{ customer.dining_count }}</div>
            <div class="stat-label">就餐次数</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">¥{{ customer.total_spent }}</div>
            <div class="stat-label">累计消费</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">¥{{ customer.avg_spent }}</div>
            <div class="stat-label">平均客单价</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 就餐记录 -->
      <el-card style="margin-bottom: 16px;">
        <template #header><span style="font-weight: 600;">就餐记录</span></template>
        <!-- 桌面端表格 -->
        <el-table :data="diningRecords" size="small" stripe class="desktop-table-detail">
          <el-table-column prop="dining_date" label="就餐时间" width="170" />
          <el-table-column prop="store_name" label="门店" width="120" />
          <el-table-column prop="party_size" label="人数" width="70" />
          <el-table-column prop="total_amount" label="消费金额" width="100" />
          <el-table-column prop="satisfaction" label="满意度" width="80">
            <template #default="{ row }">
              <span v-if="row.satisfaction">{{ '★'.repeat(row.satisfaction) }}{{ '☆'.repeat(5 - row.satisfaction) }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        </el-table>
        <!-- 移动端卡片 -->
        <div class="mobile-card-list-detail" v-if="diningRecords.length">
          <div v-for="row in diningRecords" :key="row.id" class="detail-card-item">
            <div class="detail-card-row">
              <span class="detail-card-name">{{ row.dining_date }}</span>
              <span class="detail-card-amount">¥{{ row.total_amount }}</span>
            </div>
            <div class="detail-card-row">
              <span class="detail-card-label">{{ row.store_name }} · {{ row.party_size }}人</span>
              <span v-if="row.satisfaction" style="color: #f7ba2a; font-size: 12px;">{{ '★'.repeat(row.satisfaction) }}</span>
            </div>
            <div v-if="row.notes" class="detail-card-notes">{{ row.notes }}</div>
          </div>
        </div>
        <el-empty v-if="!diningRecords.length" description="暂无就餐记录" :image-size="60" />
      </el-card>

      <!-- 预订记录 -->
      <el-card style="margin-bottom: 16px;">
        <template #header><span style="font-weight: 600;">预订记录</span></template>
        <!-- 桌面端表格 -->
        <el-table :data="reservations" size="small" stripe class="desktop-table-detail">
          <el-table-column prop="reservation_date" label="预订日期" width="120" />
          <el-table-column prop="reservation_time" label="时间" width="80" />
          <el-table-column prop="store_name" label="门店" width="120" />
          <el-table-column prop="party_size" label="人数" width="70" />
          <el-table-column prop="status_display" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ row.status_display }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        </el-table>
        <!-- 移动端卡片 -->
        <div class="mobile-card-list-detail" v-if="reservations.length">
          <div v-for="row in reservations" :key="row.id" class="detail-card-item">
            <div class="detail-card-row">
              <span class="detail-card-name">{{ row.reservation_date }} {{ row.reservation_time }}</span>
              <el-tag :type="statusType(row.status)" size="small">{{ row.status_display }}</el-tag>
            </div>
            <div class="detail-card-row">
              <span class="detail-card-label">{{ row.store_name }} · {{ row.party_size }}人</span>
            </div>
            <div v-if="row.notes" class="detail-card-notes">{{ row.notes }}</div>
          </div>
        </div>
        <el-empty v-if="!reservations.length" description="暂无预订记录" :image-size="60" />
      </el-card>

      <!-- 提醒记录 -->
      <el-card>
        <template #header><span style="font-weight: 600;">提醒记录</span></template>
        <!-- 桌面端表格 -->
        <el-table :data="reminders" size="small" stripe class="desktop-table-detail">
          <el-table-column prop="remind_date" label="提醒日期" width="120" />
          <el-table-column prop="remind_type_display" label="类型" width="80" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status_display" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'handled' ? 'success' : 'info'" size="small">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <!-- 移动端卡片 -->
        <div class="mobile-card-list-detail" v-if="reminders.length">
          <div v-for="row in reminders" :key="row.id" class="detail-card-item">
            <div class="detail-card-row">
              <span class="detail-card-name">{{ row.title }}</span>
              <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'handled' ? 'success' : 'info'" size="small">
                {{ row.status_display }}
              </el-tag>
            </div>
            <div class="detail-card-row">
              <span class="detail-card-label">{{ row.remind_date }} · {{ row.remind_type_display }}</span>
            </div>
          </div>
        </div>
        <el-empty v-if="!reminders.length" description="暂无提醒记录" :image-size="60" />
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getCustomer } from '../api/customer'
import { getDiningRecords } from '../api/dining'
import { getReservations } from '../api/reservation'
import { getReminders } from '../api/reminder'

const route = useRoute()
const id = route.params.id
const loading = ref(true)
const customer = ref(null)
const diningRecords = ref([])
const reservations = ref([])
const reminders = ref([])

function statusType(status) {
  const map = { pending: 'warning', confirmed: 'primary', arrived: 'success', cancelled: 'info', noshow: 'danger' }
  return map[status] || 'info'
}

onMounted(async () => {
  try {
    const [custData, diningData, resData, remData] = await Promise.all([
      getCustomer(id),
      getDiningRecords({ customer: id, page_size: 10 }),
      getReservations({ customer: id, page_size: 10 }),
      getReminders({ customer: id, page_size: 10 }),
    ])
    customer.value = custData
    diningRecords.value = diningData.results || diningData
    reservations.value = resData.results || resData
    reminders.value = remData.results || remData
  } catch (e) {
    // handled by interceptor
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* 消费统计卡片 */
.stat-card {
  text-align: center;
  padding: 12px 8px;
}
.stat-card .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
}
.stat-card .stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 桌面端：显示桌面元素，隐藏移动端 */
.desktop-desc { display: block; }
.desktop-table-detail { display: block; width: 100%; }
.mobile-info-card { display: none; }
.mobile-card-list-detail { display: none; }

/* 移动端信息卡片（MobileLayout :deep() 控制显示） */
.mobile-info-card {
  display: flex;
  flex-direction: column;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.info-row:last-child {
  border-bottom: none;
}
.info-label {
  color: #909399;
  flex-shrink: 0;
}
.info-value {
  color: #303133;
  text-align: right;
  word-break: break-all;
}

/* 移动端详情卡片（MobileLayout :deep() 控制显示） */
.detail-card-item {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}
.detail-card-item:last-child {
  border-bottom: none;
}
.detail-card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.detail-card-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}
.detail-card-amount {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
}
.detail-card-label {
  font-size: 12px;
  color: #909399;
}
.detail-card-notes {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
  line-height: 1.4;
}
</style>
