import {createRouter, createWebHistory, type RouteRecordRaw} from 'vue-router'
import {isAuthenticated, isAdmin} from '../auth'
import {t} from '../i18n'


const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/calls' },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, titleKey: 'routes.login' }
  },
  {
    path: '/calls',
    name: 'Calls',
    component: () => import('../views/CallsView.vue'),
    meta: { titleKey: 'routes.calls' }
  },
  {
    path: '/call/:id',
    name: 'Call',
    component: () => import('../views/CallView.vue'),
    meta: { titleKey: 'routes.call' }
  },
  {
    path: '/calls/subjects',
    name: 'Subjects',
    component: () => import('../views/calls/SubjectsView.vue'),
    meta: { admin: true, titleKey: 'routes.subjects' }
  },
  {
    path: '/exercise',
    name: 'Exercise',
    component: () => import('../views/ExerciseView.vue'),
    meta: { admin: true, titleKey: 'routes.exercises' }
  },
  {
    path: '/youth',
    name: 'Youth Exercise',
    component: () => import('../views/YouthExerciseView.vue'),
    meta: { admin: true, titleKey: 'routes.youth' }
  },
  {
    path: '/members',
    name: 'Members',
    component: () => import('../views/MembersView.vue'),
    meta: { admin: true, titleKey: 'routes.members' }
  },
  {
    path: '/member/:id',
    name: 'Member',
    component: () => import('../views/MemberView.vue'),
    meta: { titleKey: 'routes.member' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/StatisticsView.vue'),
    meta: { titleKey: 'routes.statistics' }
  },
  {
    path: '/statistics/present',
    name: 'Presentation',
    component: () => import('../views/PresentationView.vue'),
    meta: { titleKey: 'routes.presentation' }
  },
  {
    path: '/theme',
    name: 'Theme',
    component: () => import('../views/Theme.vue'),
    meta: { titleKey: 'routes.theme' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { titleKey: 'routes.notFound' }
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
  const key = to.meta?.titleKey as string | undefined
  document.title = key ? `${t(key)} | ${t('app.name')}` : t('app.name')
})

export default router
