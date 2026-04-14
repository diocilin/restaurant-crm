<template>
  <div class="page-container">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑客户' : '新建客户' }}</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="customer-form" style="max-width: 600px;">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="微信号" prop="wechat">
          <el-input v-model="form.wechat" placeholder="请输入微信号（选填）" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="M">男</el-radio>
            <el-radio value="F">女</el-radio>
            <el-radio value="">不填</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="生日">
          <el-date-picker v-model="form.birthday" type="date" placeholder="选择生日" value-format="YYYY-MM-DD"
            style="width: 100%;" />
        </el-form-item>
        <el-form-item label="纪念日">
          <el-date-picker v-model="form.anniversary" type="date" placeholder="选择纪念日" value-format="YYYY-MM-DD"
            style="width: 100%;" />
        </el-form-item>
        <el-form-item label="常去门店">
          <el-select v-model="form.store" placeholder="选择门店" clearable style="width: 100%;">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户等级">
          <el-select v-model="form.level" style="width: 100%;">
            <el-option label="普通" value="normal" />
            <el-option label="VIP" value="vip" />
            <el-option label="SVIP" value="svip" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签" style="width: 100%;">
            <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="备注信息（选填）" />
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCustomer, createCustomer, updateCustomer, getStores, getTags } from '../api/customer'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const saving = ref(false)
const stores = ref([])
const tags = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  phone: '',
  wechat: '',
  gender: '',
  birthday: '',
  anniversary: '',
  store: null,
  level: 'normal',
  tag_ids: [],
  notes: '',
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // 将空字符串转为null，避免日期字段校验失败
  const payload = {
    ...form,
    birthday: form.birthday || null,
    anniversary: form.anniversary || null,
    store: form.store || null,
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await updateCustomer(route.params.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createCustomer(payload)
      ElMessage.success('创建成功')
    }
    router.push('/customers')
  } catch (e) {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [storesData, tagsData] = await Promise.all([
    getStores(),
    getTags(),
  ])
  stores.value = storesData.results || storesData
  tags.value = tagsData.results || tagsData

  if (isEdit.value) {
    const data = await getCustomer(route.params.id)
    Object.assign(form, {
      name: data.name,
      phone: data.phone,
      wechat: data.wechat || '',
      gender: data.gender || '',
      birthday: data.birthday || '',
      anniversary: data.anniversary || '',
      store: data.store,
      level: data.level,
      tag_ids: data.tags ? data.tags.map(t => t.id) : [],
      notes: data.notes || '',
    })
  }
})
</script>

<style scoped>
</style>
