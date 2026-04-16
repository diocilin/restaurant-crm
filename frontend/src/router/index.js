import { createRouter, createWebHistory } from 'vue-router'

/**
 * 设备检测：判断是否为移动端（手机竖屏）
 * 使用 UserAgent + 触摸能力 + 屏幕宽度综合判断
 */
function isMobileDevice() {
  if (typeof window === 'undefined') return false
  const ua = navigator.userAgent.toLowerCase()
  const hasTouchScreen = 'ontouchstart' in window || navigator.maxTouchPoints > 0
  const isPhoneUA = /android|webos|iphone|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const isNarrowScreen = window.innerWidth <= 768
  // iPad 横屏不算手机
  const isTablet = /ipad|tablet/i.test(ua) && window.innerWidth > 768
  return (isPhoneUA || (hasTouchScreen && isNarrowScreen)) && !isTablet
}

// 根据设备类型选择 Layout 组件
const LayoutComponent = isMobileDevice()
  ? () => import('../views/MobileLayout.vue')
  : () => import('../views/Layout.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: LayoutComponent,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页看板' }
      },
      {
        path: 'customers',
        name: 'CustomerList',
        component: () => import('../views/CustomerList.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('../views/CustomerDetail.vue'),
        meta: { title: '客户详情' }
      },
      {
        path: 'customers/create',
        name: 'CustomerCreate',
        component: () => import('../views/CustomerForm.vue'),
        meta: { title: '新建客户' }
      },
      {
        path: 'customers/:id/edit',
        name: 'CustomerEdit',
        component: () => import('../views/CustomerForm.vue'),
        meta: { title: '编辑客户' }
      },
      {
        path: 'dining',
        name: 'DiningList',
        component: () => import('../views/DiningList.vue'),
        meta: { title: '就餐记录' }
      },
      {
        path: 'dining/create',
        name: 'DiningCreate',
        component: () => import('../views/DiningForm.vue'),
        meta: { title: '新建就餐记录' }
      },
      {
        path: 'dining/:id/edit',
        name: 'DiningEdit',
        component: () => import('../views/DiningForm.vue'),
        meta: { title: '编辑就餐记录' }
      },
      {
        path: 'reservations',
        name: 'ReservationList',
        component: () => import('../views/ReservationList.vue'),
        meta: { title: '预订管理' }
      },
      {
        path: 'reservations/create',
        name: 'ReservationCreate',
        component: () => import('../views/ReservationForm.vue'),
        meta: { title: '新建预订' }
      },
      {
        path: 'reservations/:id/edit',
        name: 'ReservationEdit',
        component: () => import('../views/ReservationForm.vue'),
        meta: { title: '编辑预订' }
      },
      {
        path: 'reminders',
        name: 'ReminderList',
        component: () => import('../views/ReminderList.vue'),
        meta: { title: '提醒管理' }
      },
      {
        path: 'import',
        name: 'ExcelImport',
        component: () => import('../views/ExcelImport.vue'),
        meta: { title: '数据导入' }
      },
      {
        path: 'dish-stats',
        name: 'DishStats',
        component: () => import('../views/DishStats.vue'),
        meta: { title: '菜品分析' }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
