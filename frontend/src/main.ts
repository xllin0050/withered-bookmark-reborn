import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { DynamicScroller } from "vue-virtual-scroller";

import "vue-virtual-scroller/dist/vue-virtual-scroller.css";
import "./style.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.component("DynamicScroller", DynamicScroller);
app.mount("#app");
