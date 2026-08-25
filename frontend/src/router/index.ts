import {createRouter, createWebHistory, type RouteRecordRaw} from 'vue-router'
import {isAuthenticated, isAdmin} from '../auth'


const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/calls' },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, title: 'Login' }
  },
  {
    path: '/calls',
    name: 'Calls',
    component: () => import('../views/CallsView.vue'),
    meta: { title: 'Alarme' }
  },
  {
    path: '/call/:id',
    name: 'Call',
    component: () => import('../views/CallView.vue'),
    meta: { title: 'Alarm' }
  },
  {
    path: '/calls/subjects',
    name: 'Subjects',
    component: () => import('../views/calls/SubjectsView.vue'),
    meta: { admin: true, title: 'Stichwoerter' }
  },
  {
    path: '/exercise',
    name: 'Exercise',
    component: () => import('../views/ExerciseView.vue'),
    meta: { admin: true, title: 'Uebungen' }
  },
  {
    path: '/youth',
    name: 'Youth Exercise',
    component: () => import('../views/YouthExerciseView.vue'),
    meta: { admin: true, title: 'Jugenduebungen' }
  },
  {
    path: '/members',
    name: 'Members',
    component: () => import('../views/MembersView.vue'),
    meta: { admin: true, title: 'Mitglieder' }
  },
  {
    path: '/member/:id',
    name: 'Member',
    component: () => import('../views/MemberView.vue'),
    meta: { title: 'Mitglied' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/StatisticsView.vue'),
    meta: { title: 'Statistiken' }
  },
  {
    path: '/theme',
    name: 'Theme',
    component: () => import('../views/Theme.vue'),
    meta: { title: 'Theme' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: 'Nicht gefunden' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _, next) => {
  if (to.meta?.public) {
    next()
  } else if (!isAuthenticated()) {
    next({name: 'Login'})
  } else if (to.meta?.admin && !isAdmin()) {
    next({name: 'Calls'})
  } else {
    next()
  }
})

router.afterEach((to) => {
  const title = to.meta?.title as string | undefined
  document.title = title ? `${title} | CallStats` : 'CallStats'
})

export default router
