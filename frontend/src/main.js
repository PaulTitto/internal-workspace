// frontend/src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import { initializeMsal } from './auth/msalAuth';
import './assets/tailwind.css';

async function bootstrap() {
  await initializeMsal();
  const app = createApp(App);
  app.mount('#app');
}

bootstrap();