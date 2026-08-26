import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import {i18n} from './i18n'
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faAngleDown,
    faAngleUp,
    faArrowLeft,
    faArrowRight,
    faBoxArchive,
    faCalendarDays,
    faCheck,
    faChevronLeft,
    faChevronRight,
    faCircleCheck,
    faCircleExclamation,
    faDisplay,
    faMagnifyingGlass,
    faMoon,
    faPen,
    faPlus,
    faPowerOff,
    faRightFromBracket,
    faRotateLeft,
    faSun,
    faTrash,
    faUsers,
    faXmark
} from '@fortawesome/free-solid-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {initTheme} from './theme'
import {loadConfig} from './api/config'

library.add(faAngleDown, faAngleUp, faArrowLeft, faArrowRight, faBoxArchive, faCalendarDays, faCheck,
    faChevronLeft, faChevronRight, faCircleCheck, faCircleExclamation, faDisplay, faMagnifyingGlass,
    faMoon, faPen, faPlus, faPowerOff, faRightFromBracket, faRotateLeft, faSun, faTrash, faUsers, faXmark)

initTheme()
void loadConfig()

createApp(App)
    .use(router)
    .use(i18n)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
