<template>
  <div class="page-container">
    <div class="page-header">
      <h2>美团收银数据导入</h2>
    </div>

    <el-card class="import-card">
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px;">
        <template #title>
          从美团管家后台导出Excel文件后上传即可。系统自动通过桌号匹配预订记录并关联客户。
        </template>
        <div style="margin-top: 6px; font-size: 13px; color: #666;">
          导出路径：美团管家 → 报表中心 → 营业报表 → 店内订单明细 → 导出Excel
        </div>
      </el-alert>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item label="门店">
          <el-select v-model="storeId" placeholder="选择门店" style="width: 200px;">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
          >
            <el-button type="primary">选择Excel文件</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="selectedFile">
          <span style="color: #67c23a;">{{ selectedFile.name }}</span>
          <el-button type="success" :loading="importing" @click="handleImport" style="margin-left: 10px;">
            开始导入
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 导入结果 -->
    <el-card v-if="importResult" style="margin-top: 16px;">
      <template #header>
        <span>导入结果</span>
      </template>
      <el-descriptions :column="4" border size="small">
        <el-descriptions-item label="成功">{{ importResult.success }}条</el-descriptions-item>
        <el-descriptions-item label="跳过（重复）">{{ importResult.skipped }}条</el-descriptions-item>
        <el-descriptions-item label="错误">{{ importResult.errors.length }}条</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ importResult.total_amount }}</el-descriptions-item>
      </el-descriptions>

      <!-- 订单明细结果 -->
      <el-table v-if="importResult.type !== 'dish_sales' && importResult.records.length" :data="importResult.records" size="small" stripe style="margin-top: 12px;" max-height="400">
        <el-table-column prop="order_no" label="订单号" width="140" />
        <el-table-column prop="table" label="桌号" width="80" />
        <el-table-column prop="customer" label="匹配客户" width="100">
          <template #default="{ row }">
            <el-tag :type="row.customer === '散客(未匹配)' ? 'info' : 'success'" size="small">{{ row.customer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="80" />
        <el-table-column prop="time" label="时间" />
      </el-table>

      <!-- 菜品统计结果 -->
      <el-table v-if="importResult.type === 'dish_sales' && importResult.records.length" :data="importResult.records" size="small" stripe style="margin-top: 12px;" max-height="400">
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="name" label="菜品名称" />
        <el-table-column prop="qty" label="销量" width="80" />
        <el-table-column prop="amount" label="销售额" width="100" />
      </el-table>

      <!-- 错误信息 -->
      <div v-if="importResult.errors.length" style="margin-top: 12px;">
        <el-alert type="warning" :closable="false" :title="`错误信息（${importResult.errors.length}条）`">
          <div v-for="(err, i) in importResult.errors" :key="i" style="font-size: 12px; color: #e6a23c;">{{ err }}</div>
        </el-alert>
      </div>
    </el-card>

    <!-- 历史导入记录 -->
    <el-card style="margin-top: 16px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>导入记录</span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" size="small" @change="loadLogs" />
        </div>
      </template>
      <el-table :data="logs" size="small" stripe v-loading="logsLoading">
        <el-table-column prop="dining_date" label="就餐时间" width="160" />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column prop="store_name" label="门店" width="120" />
        <el-table-column prop="table_number" label="桌号" width="80" />
        <el-table-column prop="total_amount" label="金额" width="80" />
        <el-table-column prop="order_no" label="订单号" width="140" />
        <el-table-column prop="source_display" label="来源" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { importExcel, getImportLogs } from '../api/dining'
import { getStores } from '../api/customer'

const stores = ref([])
const storeId = ref(null)
const selectedFile = ref(null)
const importing = ref(false)
const importResult = ref(null)
const logs = ref([])
const logsLoading = ref(false)
const dateRange = ref(null)

function handleFileChange(file) {
  selectedFile.value = file.raw
}

async function handleImport() {
  if (!storeId.value) { ElMessage.warning('请选择门店'); return }
  if (!selectedFile.value) { ElMessage.warning('请选择Excel文件'); return }

  importing.value = true
  importResult.value = null
  try {
    const res = await importExcel(selectedFile.value, storeId.value)
    importResult.value = res
    ElMessage.success(res.message)
    selectedFile.value = null
    loadLogs()
  } catch (e) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

async function loadLogs() {
  logsLoading.value = true
  try {
    const params = { page_size: 50, source: 'meituan' }
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await getImportLogs(params)
    logs.value = res.results || res
  } catch (e) { /* handled */ }
  finally { logsLoading.value = false }
}

onMounted(() => {
  getStores().then(d => { stores.value = d.results || d })
  loadLogs()
})
</script>

<style scoped>
.import-card { max-width: 800px; }
</style>
