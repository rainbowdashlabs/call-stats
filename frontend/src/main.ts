import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import {createRouter, createWebHistory, RouteRecordRaw} from "vue-router";
import HomeView from "./components/views/home/HomeView.vue";
import CallsView from "./components/views/calls/CallsView.vue";
import CallView from "./components/views/call/CallView.vue";
import EditCallView from "./components/views/call/views/EditCallView.vue";
import CrewView from "./components/views/crew/CrewView.vue";
import ExerciseCrew from "./components/views/exercises/ExercisesView.vue";

const routes: RouteRecordRaw[] = [
    {path: "/", name: "home", component: HomeView},
    {path: "/calls", name: "calls", component: CallsView},
    {
        path: "/call/:id", name: "call", component: CallView,
        children: [
            {path: "edit", component: EditCallView}
        ]
    },
    {path: "/crew", name: "crew", component: CrewView},
    {path: "/exercises", name: "exercises", component: ExerciseCrew}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

createApp(App)
    .use(router)
    .mount('#app')
