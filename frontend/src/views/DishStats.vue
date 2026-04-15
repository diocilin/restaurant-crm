<template>
  <div class="page-container">
    <div class="page-header">
      <h2>菜品分析</h2>
    </div>

    <!-- 筛选 -->
    <el-card style="margin-bottom: 16px;">
      <el-form :inline="true">
        <el-form-item label="门店">
          <el-select v-model="storeId" placeholder="全部门店" clearable style="width: 200px;" @change="loadStats">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" @change="loadStats" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadStats">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 概览 -->
    <el-row :gutter="16" style="margin-bottom: 16px;" v-if="stats">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">¥{{ stats.total_amount }}</div>
          <div class="stat-label">总销售额</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total_orders }}</div>
          <div class="stat-label">总订单数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total_dishes }}</div>
          <div class="stat-label">菜品种类</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">¥{{ avgOrderAmount }}</div>
          <div class="stat-label">平均客单价</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 菜品排名 -->
    <el-card v-if="stats && stats.dish_ranking.length" style="margin-bottom: 16px;">
      <template #header><span>菜品销量排名 TOP{{ stats.dish_ranking.length }}</span></template>
      <el-table :data="stats.dish_ranking" size="small" stripe max-height="500">
        <el-table-column type="index" label="排名" width="60">
          <template #default="{ $index }">
            <el-tag v-if="$index < 3" :type="$index === 0 ? 'danger' : $index === 1 ? 'warning' : 'success'" size="small" round>{{ $index + 1 }}</el-tag>
            <span v-else>{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="菜品名称" min-width="120" />
        <el-table-column prop="qty" label="销量（份）" width="100" sortable />
        <el-table-column prop="amount" label="销售额（元）" width="120" sortable />
        <el-table-column prop="ratio" label="销售占比" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.ratio" :stroke-width="14" :text-inside="true" :format="() => row.ratio + '%'" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 每日趋势 -->
    <el-card v-if="stats && stats.daily_stats.length">
      <template #header><span>近30天销售趋势</span></template>
      <div class="trend-chart">
        <div v-for="day in stats.daily_stats" :key="day.date" class="trend-bar-wrap">
          <div class="trend-bar" :style="{ height: getBarHeight(day.amount) + 'px' }">
            <span class="trend-amount">¥{{ day.amount }}</span>
          </div>
          <span class="trend-date">{{ day.date }}</span>
          <span class="trend-count">{{ day.count }}单</span>
        </div>
      </div>
    </el-card>

    <el-empty v-if="stats && stats.total_orders === 0" description="暂无数据，请先导入美团收银Excel" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDishStats } from '../api/dining'
import { getStores } from '../api/customer'

const stores = ref([])
const storeId = ref(null)
const dateRange = ref(null)
const stats = ref(null)

const avgOrderAmount = computed(() => {
  if (!stats.value || stats.value.total_orders === 0) return '0'
  return (parseFloat(stats.value.total_amount) / stats.value.total_orders).toFixed(2)
})

const maxAmount = computed(() => {
  if (!stats.value || !stats.value.daily_stats.length) return 1
  return Math.max(...stats.value.daily_stats.map(d => parseFloat(d.amount)), 1)
})

function getBarHeight(amount) {
  return Math.max(4, (parseFloat(amount) / maxAmount.value) * 120)
}

async function loadStats() {
  try {
    const params = {}
    if (storeId.value) params.store = storeId.value
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    stats.value = await getDishStats(params)
  } catch (e) { /* handled */ }
}

onMounted(() => {
  getStores().then(d => { stores.value = d.results || d })
  loadStats()
})
</script>

<style scoped>
.stat-value { font-size: 24px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }

.trend-chart {
  display: flex; align-items: flex-end; gap: 4px; height: 180px;
  padding: 10px 0; overflow-x: auto;
}
.trend-bar-wrap {
  display: flex; flex-direction: column; align-items: center; min-width: 32px; flex: 1;
}
.trend-bar {
  width: 100%; background: linear-gradient(180deg, #409eff, #79bbff);
  border-radius: 3px 3px 0 0; position: relative; min-height: 4px;
  transition: height 0.3s;
}
.trend-amount {
  position: absolute; top: -18px; left: 50%; transform: translateX(-50%);
  font-size: 10px; color: #909399; white-space: nowrap;
}
.trend-date { font-size: 10px; color: #909399; margin-top: 4px; }
.trend-count { font-size: 9px; color: #c0c4cc; }
</style>
