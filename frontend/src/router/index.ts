import {createRouter, createWebHistory, type RouteRecordRaw} from 'vue-router'


const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/calls' },
  {
    path: '/calls',
    name: 'Calls',
    component: () => import('../views/CallsView.vue'),
  },
  {
    path: '/calls/subjects',
    name: 'Subjects',
    component: () => import('../views/calls/SubjectsView.vue'),
  },
  {
    path: '/exercise',
    name: 'Exercise',
    component: () => import('../views/ExerciseView.vue'),
  },
  {
    path: '/youth',
    name: 'Youth Exercise',
    component: () => import('../views/YouthExerciseView.vue'),
  },
  {
    path: '/members',
    name: 'Members',
    component: () => import('../views/MembersView.vue'),
  },
  {
    path: '/member/:id',
    name: 'Member',
    component: () => import('../views/MemberView.vue'),
  },
  {
    path: '/theme',
    name: 'Theme',
    component: () => import('../views/Theme.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
