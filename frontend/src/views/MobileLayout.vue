<template>
  <div class="mobile-layout">
    <!-- 顶部标题栏 -->
    <header class="mobile-header">
      <span class="mobile-title">{{ $route.meta.title || '大河有鱼' }}</span>
      <div class="mobile-header-right">
        <el-badge :value="pendingCount" :hidden="pendingCount === 0" :max="99">
          <el-icon class="header-icon" @click="$router.push('/reminders')"><Bell /></el-icon>
        </el-badge>
        <el-icon class="header-icon" @click="handleLogout"><SwitchButton /></el-icon>
      </div>
    </header>

    <!-- 内容区 -->
    <main class="mobile-main">
      <router-view />
    </main>

    <!-- 底部Tab栏 -->
    <nav class="mobile-tabbar">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        :class="['tab-item', { active: isActive(tab.path) }]"
        @click="$router.push(tab.path)"
      >
        <el-badge v-if="tab.path === '/reminders' && pendingCount > 0" :value="pendingCount" :max="99" class="tab-badge">
          <el-icon size="22"><component :is="tab.icon" /></el-icon>
        </el-badge>
        <el-icon v-else size="22"><component :is="tab.icon" /></el-icon>
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPendingReminders } from '../api/reminder'

const route = useRoute()
const router = useRouter()
const pendingCount = ref(0)

const tabs = [
  { path: '/dashboard', icon: 'DataAnalysis', label: '首页' },
  { path: '/customers', icon: 'User', label: '客户' },
  { path: '/dining', icon: 'Food', label: '就餐' },
  { path: '/reservations', icon: 'Calendar', label: '预订' },
  { path: '/reminders', icon: 'Bell', label: '提醒' },
]

function isActive(path) {
  return route.path.startsWith(path)
}

function handleLogout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('username')
  router.push('/login')
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
  setInterval(loadPendingCount, 300000)
})
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh; /* 动态视口高度，适配手机浏览器地址栏 */
  background: #f5f7fa;
  overflow: hidden;
}

/* 顶部标题栏 */
.mobile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
  z-index: 10;
}

.mobile-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.mobile-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
}

.header-icon:active {
  color: #409EFF;
}

/* 内容区 */
.mobile-main {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 底部Tab栏 */
.mobile-tabbar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 56px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  flex-shrink: 0;
  padding-bottom: env(safe-area-inset-bottom); /* 适配iPhone底部安全区 */
  z-index: 10;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex: 1;
  height: 100%;
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.tab-item.active {
  color: #409EFF;
}

.tab-item:active {
  color: #409EFF;
}

.tab-label {
  font-size: 10px;
  line-height: 1;
}

.tab-badge {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Element Plus Badge 在 Tab 中的位置修正 */
.tab-badge :deep(.el-badge__content) {
  top: -6px;
  right: -8px;
}

/* 内容区内部页面容器适配 */
.mobile-main :deep(.page-container) {
  padding: 12px;
}

.mobile-main :deep(.page-header) {
  margin-bottom: 12px;
}

.mobile-main :deep(.page-header h2) {
  font-size: 17px;
}

/* 筛选栏适配 */
.mobile-main :deep(.filter-bar) {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.mobile-main :deep(.filter-bar .el-input),
.mobile-main :deep(.filter-bar .el-select),
.mobile-main :deep(.filter-bar .el-date-picker) {
  width: 100% !important;
}

/* 卡片列表适配 */
.mobile-main :deep(.mobile-card-list) {
  display: block;
}

.mobile-main :deep(.desktop-table) {
  display: none;
}

/* 卡片样式 */
.mobile-main :deep(.customer-card),
.mobile-main :deep(.dining-card),
.mobile-main :deep(.res-card),
.mobile-main :deep(.mobile-card) {
  margin-bottom: 10px;
}

.mobile-main :deep(.customer-card .el-card__body),
.mobile-main :deep(.dining-card .el-card__body),
.mobile-main :deep(.res-card .el-card__body),
.mobile-main :deep(.mobile-card .el-card__body) {
  padding: 12px;
}

/* 卡片行 */
.mobile-main :deep(.card-row) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
  font-size: 14px;
  line-height: 1.5;
}

.mobile-main :deep(.card-label) {
  color: #909399;
  flex-shrink: 0;
  margin-right: 12px;
}

.mobile-main :deep(.card-value) {
  color: #303133;
  text-align: right;
  word-break: break-all;
}

/* 卡片头部 */
.mobile-main :deep(.card-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.mobile-main :deep(.card-name),
.mobile-main :deep(.name-text) {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

/* 卡片操作按钮 */
.mobile-main :deep(.card-actions) {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.mobile-main :deep(.card-actions .el-button) {
  flex: 1;
}

/* 分页 */
.mobile-main :deep(.pagination-wrapper),
.mobile-main :deep(.pagination-wrap) {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}

.mobile-main :deep(.el-pagination) {
  flex-wrap: wrap;
  justify-content: center;
}

.mobile-main :deep(.el-pagination .el-pagination__total),
.mobile-main :deep(.el-pagination .el-pagination__sizes) {
  display: none;
}

/* Dashboard 统计卡片 */
.mobile-main :deep(.stat-card) {
  text-align: center;
  padding: 12px 6px;
}

.mobile-main :deep(.stat-card .stat-value) {
  font-size: 22px;
  font-weight: 700;
}

.mobile-main :deep(.stat-card .stat-label) {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Dashboard 卡片列表（非表格） */
.mobile-main :deep(.desktop-table) {
  display: none;
}

.mobile-main :deep(.mobile-card-list) {
  display: block;
}

.mobile-main :deep(.dash-card-item) {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.mobile-main :deep(.dash-card-item:last-child) {
  border-bottom: none;
}

.mobile-main :deep(.dash-card-row) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.mobile-main :deep(.dash-card-name) {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.mobile-main :deep(.dash-card-label) {
  font-size: 12px;
  color: #909399;
}

.mobile-main :deep(.dash-card-title) {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.mobile-main :deep(.dash-card-actions) {
  display: flex;
  gap: 8px;
}

/* CustomerDetail 信息卡片 */
.mobile-main :deep(.desktop-desc) {
  display: none;
}

.mobile-main :deep(.desktop-table-detail) {
  display: none;
}

.mobile-main :deep(.mobile-info-card) {
  display: block;
}

.mobile-main :deep(.mobile-card-list-detail) {
  display: block;
}

.mobile-main :deep(.info-row) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.mobile-main :deep(.info-label) {
  color: #909399;
  flex-shrink: 0;
}

.mobile-main :deep(.info-value) {
  color: #303133;
  text-align: right;
  word-break: break-all;
}

.mobile-main :deep(.detail-card-item) {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.mobile-main :deep(.detail-card-item:last-child) {
  border-bottom: none;
}

.mobile-main :deep(.detail-card-row) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.mobile-main :deep(.detail-card-name) {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.mobile-main :deep(.detail-card-amount) {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
}

.mobile-main :deep(.detail-card-label) {
  font-size: 12px;
  color: #909399;
}

.mobile-main :deep(.detail-card-notes) {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

/* 对话框适配 */
.mobile-main :deep(.el-dialog) {
  width: 92% !important;
  margin: 4vh auto !important;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.mobile-main :deep(.el-dialog__body) {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 表单适配 */
.mobile-main :deep(.el-form-item__label) {
  font-size: 13px;
}

.mobile-main :deep(.customer-form),
.mobile-main :deep(.dining-form),
.mobile-main :deep(.reservation-form),
.mobile-main :deep(.edit-dialog .el-form),
.mobile-main :deep(.create-dialog .el-form) {
  max-width: 100% !important;
}

.mobile-main :deep(.customer-form .el-form-item__label),
.mobile-main :deep(.dining-form .el-form-item__label),
.mobile-main :deep(.reservation-form .el-form-item__label),
.mobile-main :deep(.edit-dialog .el-form-item__label),
.mobile-main :deep(.create-dialog .el-form-item__label) {
  width: 70px !important;
  min-width: 70px !important;
}

.mobile-main :deep(.el-form .el-input),
.mobile-main :deep(.el-form .el-select),
.mobile-main :deep(.el-form .el-date-editor),
.mobile-main :deep(.el-form .el-textarea) {
  width: 100% !important;
}

/* Tag 紧凑 */
.mobile-main :deep(.el-tag--small) {
  padding: 2px 6px;
  font-size: 11px;
}

/* 消息提示 */
.mobile-main :deep(.el-message) {
  min-width: auto !important;
  max-width: 85vw;
}
</style>
