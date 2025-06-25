// prettier.config.js
export default {
  // 基本格式
  semi: false,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'es5',

  // Vue 特定
  vueIndentScriptAndStyle: false,
  // Tailwind CSS automatically sorts classes
  plugins: ['prettier-plugin-tailwindcss'],
}
