<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon size="24"><Shop /></el-icon>
        <span v-show="!isCollapse" class="logo-text">餐饮CRM</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>首页看板</template>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <template #title>客户管理</template>
        </el-menu-item>
        <el-menu-item index="/dining">
          <el-icon><Food /></el-icon>
          <template #title>就餐记录</template>
        </el-menu-item>
        <el-menu-item index="/reservations">
          <el-icon><Calendar /></el-icon>
          <template #title>预订管理</template>
        </el-menu-item>
        <el-menu-item index="/reminders">
          <el-icon><Bell /></el-icon>
          <template #title>
            提醒管理
            <el-badge v-if="pendingCount > 0" :value="pendingCount" class="reminder-badge" />
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" size="20">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <span class="page-title">{{ $route.meta.title || '餐饮CRM' }}</span>
        </div>
        <div class="header-right">
          <el-badge :value="pendingCount" :hidden="pendingCount === 0" class="header-badge">
            <el-button :icon="Bell" circle size="small" @click="$router.push('/reminders')" />
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              {{ username }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import { getPendingReminders } from '../api/reminder'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const pendingCount = ref(0)
const username = ref(localStorage.getItem('username') || '管理员')

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/customers')) return '/customers'
  if (path.startsWith('/dining')) return '/dining'
  if (path.startsWith('/reservations')) return '/reservations'
  if (path.startsWith('/reminders')) return '/reminders'
  return path
})

function handleCommand(cmd) {
  if (cmd === 'logout') {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('username')
    router.push('/login')
  }
}

async function loadPendingCount() {
  try {
    const data = await getPendingReminders()
    pendingCount.value = Array.isArray(data) ? data.length : (data.results?.length || 0)
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadPendingCount()
  // 每5分钟刷新一次
  setInterval(loadPendingCount, 300000)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  border-bottom: 1px solid #3a4a5e;
}

.logo-text {
  white-space: nowrap;
}

.el-menu {
  border-right: none;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  cursor: pointer;
  color: #606266;
}

.collapse-btn:hover {
  color: #409EFF;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-badge {
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.main {
  background: #f5f7fa;
  overflow-y: auto;
}

.reminder-badge {
  margin-left: 8px;
}
</style>
