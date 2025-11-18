import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import {library} from "@fortawesome/fontawesome-svg-core";
import { far } from '@fortawesome/free-regular-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Add the icon packs you use to the library
library.add(far, fas)

createApp(App)
    .use(router)
    .component('font-awesome-icon', FontAwesomeIcon)
    .mount('#app')
