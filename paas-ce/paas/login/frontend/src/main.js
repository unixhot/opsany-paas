import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import Antd from 'ant-design-vue';
import App from './App.vue'
import './style.css'
import 'ant-design-vue/dist/reset.css';
import { setupI18n } from './plugins/i18n'

const app = createApp(App)
const i18n = setupI18n()

app.use(Antd)
app.use(i18n)
app.mount('#app')
