import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";
import i18n from "astro-i18n-aut/integration";

import { defaultLocale, locales } from "./src/i18n";

export default defineConfig({
  prefetch: true,
  output: "static",
  // Deployment target. When the real domain (manastirea-saharna.md) goes live,
  // set SITE to it and BASE to "/" — nothing else needs to change.
  site: process.env.SITE_URL || "https://49shamans7.github.io",
  base: process.env.BASE_PATH || "/manastirea-saharna",

  integrations: [
    i18n({
      locales,
      defaultLocale,
    }),
  ],

  vite: {
    plugins: [tailwindcss()],
  },
});
