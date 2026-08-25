import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import {i18n} from './i18n'
import {library} from "@fortawesome/fontawesome-svg-core";
import {faAngleDown, faAngleUp, faArrowLeft, faArrowRight} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faAngleDown, faAngleUp, faArrowLeft, faArrowRight)

createApp(App)
    .use(router)
    .use(i18n)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
