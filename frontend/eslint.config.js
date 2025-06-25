// eslint.config.js
import pluginVue from "eslint-plugin-vue";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";
import eslintConfigPrettier from "@vue/eslint-config-prettier";

export default defineConfigWithVueTs(
  // Vue 基本規則
  pluginVue.configs["flat/essential"],

  // TypeScript 推薦規則
  vueTsConfigs.recommended,

  // 自定義規則 (小型專案精簡版)
  {
    rules: {
      // Vue 相關
      "vue/multi-word-component-names": "off", // 允許單字組件名
      "vue/no-unused-vars": "error",

      // TypeScript 相關
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "warn",

      // 一般規則
      "no-console": "warn", // 生產環境時改為 'error'
      "no-debugger": "warn",
    },
  },

  // 忽略文件
  {
    ignores: ["dist/", "node_modules/", "*.d.ts"],
  },
  eslintConfigPrettier,
);
