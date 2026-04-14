<template>
  <div class="page-container">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/customers/create')">新建客户</el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="filters.search" placeholder="搜索姓名/手机号/微信" clearable class="filter-search"
        :prefix-icon="Search" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="filters.store" placeholder="选择门店" clearable class="filter-store" @change="loadData">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filters.level" placeholder="客户等级" clearable class="filter-level" @change="loadData">
        <el-option label="普通" value="normal" />
        <el-option label="VIP" value="vip" />
        <el-option label="SVIP" value="svip" />
      </el-select>
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>

    <!-- 桌面端：客户表格 -->
    <el-table :data="customers" v-loading="loading" stripe border class="desktop-table">
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="gender" label="性别" width="70">
        <template #default="{ row }">
          {{ row.gender === 'M' ? '男' : row.gender === 'F' ? '女' : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="80">
        <template #default="{ row }">
          <el-tag :type="row.level === 'svip' ? 'danger' : row.level === 'vip' ? 'warning' : 'info'" size="small">
            {{ row.level === 'svip' ? 'SVIP' : row.level === 'vip' ? 'VIP' : '普通' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="store_name" label="常去门店" width="120" />
      <el-table-column prop="birthday" label="生日" width="110">
        <template #default="{ row }">{{ row.birthday || '-' }}</template>
      </el-table-column>
      <el-table-column prop="tag_names" label="标签" min-width="150">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tag_names" :key="tag" size="small" style="margin-right: 4px; margin-bottom: 2px;">
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" sortable />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="$router.push(`/customers/${row.id}`)">详情</el-button>
          <el-button link type="primary" size="small" @click="$router.push(`/customers/${row.id}/edit`)">编辑</el-button>
          <el-popconfirm title="确定删除该客户吗？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端：卡片列表 -->
    <div v-loading="loading" class="mobile-card-list">
      <el-card v-for="row in customers" :key="row.id" class="customer-card" shadow="hover">
        <div class="card-header">
          <div class="card-name">
            <span class="name-text">{{ row.name }}</span>
            <el-tag :type="row.level === 'svip' ? 'danger' : row.level === 'vip' ? 'warning' : 'info'" size="small">
              {{ row.level === 'svip' ? 'SVIP' : row.level === 'vip' ? 'VIP' : '普通' }}
            </el-tag>
            <span class="gender-text">{{ row.gender === 'M' ? '男' : row.gender === 'F' ? '女' : '-' }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="card-label">手机号</span>
            <span class="card-value">{{ row.phone || '-' }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">常去门店</span>
            <span class="card-value">{{ row.store_name || '-' }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">生日</span>
            <span class="card-value">{{ row.birthday || '-' }}</span>
          </div>
          <div class="card-row" v-if="row.tag_names && row.tag_names.length">
            <span class="card-label">标签</span>
            <span class="card-value">
              <el-tag v-for="tag in row.tag_names" :key="tag" size="small" style="margin-right: 4px; margin-bottom: 2px;">
                {{ tag }}
              </el-tag>
            </span>
          </div>
          <div class="card-row">
            <span class="card-label">创建时间</span>
            <span class="card-value">{{ row.created_at || '-' }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button type="primary" size="small" @click="$router.push(`/customers/${row.id}`)">详情</el-button>
          <el-button type="primary" size="small" plain @click="$router.push(`/customers/${row.id}/edit`)">编辑</el-button>
          <el-popconfirm title="确定删除该客户吗？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" size="small" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </el-card>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCustomers, deleteCustomer, getStores } from '../api/customer'

const customers = ref([])
const stores = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({
  search: '',
  store: null,
  level: '',
})

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.search) params.search = filters.search
    if (filters.store) params.store = filters.store
    if (filters.level) params.level = filters.level
    const data = await getCustomers(params)
    customers.value = data.results || data
    total.value = data.count || customers.value.length
  } catch (e) {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteCustomer(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // handled by interceptor
  }
}

onMounted(() => {
  loadData()
  getStores().then(data => { stores.value = data.results || data })
})
</script>

<style scoped>
/* 筛选栏默认（移动端）：纵向排列 */
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.filter-search,
.filter-store,
.filter-level {
  width: 100% !important;
}

/* 桌面端筛选栏：横向排列 */
@media (min-width: 768px) {
  .filter-bar {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
  }
  .filter-search {
    width: 240px !important;
  }
  .filter-store {
    width: 160px !important;
  }
  .filter-level {
    width: 120px !important;
  }
}

/* 桌面端：显示表格，隐藏卡片 */
.desktop-table {
  display: none;
}
.mobile-card-list {
  display: block;
}

@media (min-width: 768px) {
  .desktop-table {
    display: block;
    width: 100%;
  }
  .mobile-card-list {
    display: none;
  }
}

/* 移动端卡片样式 */
.customer-card {
  margin-bottom: 12px;
}
.customer-card :deep(.el-card__body) {
  padding: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}
.card-name {
  display: flex;
  align-items: center;
  gap: 6px;
}
.name-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.gender-text {
  font-size: 13px;
  color: #909399;
}
.card-body {
  margin-bottom: 10px;
}
.card-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.5;
}
.card-label {
  color: #909399;
  flex-shrink: 0;
  margin-right: 12px;
}
.card-value {
  color: #303133;
  text-align: right;
  word-break: break-all;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

/* 分页 */
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 767px) {
  .pagination-wrapper {
    justify-content: center;
  }
  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}

/* 竖屏手机进一步优化 */
@media (max-width: 480px) {
  .customer-card {
    margin-bottom: 8px;
  }
  .customer-card :deep(.el-card__body) {
    padding: 10px;
  }
  .card-header {
    margin-bottom: 8px;
    padding-bottom: 6px;
  }
  .name-text {
    font-size: 15px;
  }
  .card-body {
    margin-bottom: 8px;
  }
  .card-row {
    padding: 3px 0;
    font-size: 13px;
  }
  .card-actions {
    gap: 6px;
    padding-top: 6px;
  }
  .card-actions .el-button {
    padding: 6px 8px;
    font-size: 12px;
  }
}
</style>
