import {createRouter, createWebHistory, type RouteRecordRaw} from 'vue-router'


const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/calls' },
  {
    path: '/calls',
    name: 'calls',
    component: () => import('../views/CallsView.vue'),
  },
  {
    path: '/training',
    name: 'training',
    component: () => import('../views/TrainingView.vue'),
  },
  {
    path: '/youth',
    name: 'youth',
    component: () => import('../views/YouthView.vue'),
  },
  {
    path: '/members',
    name: 'members',
    component: () => import('../views/MembersView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
