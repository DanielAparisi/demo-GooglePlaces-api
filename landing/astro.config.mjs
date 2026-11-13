// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { SITIO } from './src/config.ts';

export default defineConfig({
  site: SITIO.url,
  vite: { plugins: [tailwindcss()] },
});
