import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
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
        path: 'reminders',
        name: 'ReminderList',
        component: () => import('../views/ReminderList.vue'),
        meta: { title: '提醒管理' }
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
