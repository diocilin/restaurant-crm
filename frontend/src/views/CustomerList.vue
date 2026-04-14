<template>
  <div class="page-container">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/customers/create')">新建客户</el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="filters.search" placeholder="搜索姓名/手机号/微信" clearable style="width: 240px"
        :prefix-icon="Search" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="filters.store" placeholder="选择门店" clearable style="width: 160px" @change="loadData">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filters.level" placeholder="客户等级" clearable style="width: 120px" @change="loadData">
        <el-option label="普通" value="normal" />
        <el-option label="VIP" value="vip" />
        <el-option label="SVIP" value="svip" />
      </el-select>
      <el-button :icon="Search" @click="loadData">搜索</el-button>
    </div>

    <!-- 客户表格 -->
    <el-table :data="customers" v-loading="loading" stripe border style="width: 100%">
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

    <!-- 分页 -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
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
