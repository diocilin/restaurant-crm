<template>
  <div class="page-container">
    <div class="page-header">
      <h2>新建就餐记录</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="dining-form" style="max-width: 600px;">
        <el-form-item label="客户" prop="customer">
          <el-select v-model="form.customer" filterable remote :remote-method="searchCustomers"
            placeholder="搜索客户姓名或手机号" style="width: 100%;">
            <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="门店" prop="store">
          <el-select v-model="form.store" placeholder="选择门店" style="width: 100%;">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="就餐时间" prop="dining_date">
          <el-date-picker v-model="form.dining_date" type="datetime" placeholder="选择时间"
            value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="就餐人数">
          <el-input-number v-model="form.party_size" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="桌号">
          <el-input v-model="form.table_number" placeholder="如：A01" />
        </el-form-item>
        <el-form-item label="消费金额">
          <el-input-number v-model="form.total_amount" :min="0" :precision="2" :step="10" />
        </el-form-item>
        <el-form-item label="满意度">
          <el-rate v-model="form.satisfaction" :max="5" show-text />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createDiningRecord } from '../api/dining'
import { getCustomers, getStores } from '../api/customer'

const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const stores = ref([])
const customerOptions = ref([])

const form = reactive({
  customer: null, store: null, dining_date: '', party_size: 1,
  table_number: '', total_amount: 0, satisfaction: null, notes: '',
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  store: [{ required: true, message: '请选择门店', trigger: 'change' }],
  dining_date: [{ required: true, message: '请选择就餐时间', trigger: 'change' }],
}

function searchCustomers(query) {
  if (query) {
    getCustomers({ search: query, page_size: 20 }).then(d => { customerOptions.value = d.results || d })
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await createDiningRecord(form)
    ElMessage.success('保存成功')
    router.push('/dining')
  } finally { saving.value = false }
}

onMounted(() => { getStores().then(d => { stores.value = d.results || d }) })
</script>

<style scoped>
</style>
