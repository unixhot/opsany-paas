# CLAUDE.md

## Project Overview

OpsAny 数字化运维平台 (Digital Operations Platform) — Login frontend. A single-page login application serving as the authentication gateway for the OpsAny platform.

- **Stack**: Vue 3.5 (Composition API + `<script setup>`) · Vite 7 · Ant Design Vue 4.2 · TailwindCSS 4
- **Node requirement**: v20.20.0+

## Commands

```bash
npm install          # Install dependencies
npm run serve        # Start dev server (port 8000, host 0.0.0.0, auto-opens browser)
npm run dev          # Alias for serve
npm run build        # Production build → dist/
npm run preview      # Preview production build
```

## Architecture

This is a **single-page login application** — no vue-router, no Pinia. The entire app is one view (`src/view/login/login.vue`) that dynamically renders auth method tabs (Password, LDAP, SSO, OAuth, AD, IAM, IDaaS, QYWX, DingTalk, Feishu) based on the server's configured auth methods.

### Key Files

```
src/
├── main.js              # App bootstrap: createApp, Antd, i18n
├── App.vue              # Root: Antd ConfigProvider (theme), Login wrapper
├── style.css            # Global: @import "tailwindcss"
├── api/login.js         # Auth API calls (getAuthConfig, doLogin, getQywx, getSession)
├── config/defaultSetting.js  # baseUrl config (dev: hardcoded IP, prod: origin)
├── plugins/i18n.js      # i18n setup (legacy: false, fallback: zh-CN)
├── hooks/useI18nCookie.js    # Language persistence via opsany_language cookie (7-day expiry)
├── locales/             # i18n messages (zh-CN.js, zh-TW.js, en.js)
├── utils/
│   ├── request.js       # Axios instance + interceptors (code-based error handling)
│   └── util.js          # isValidUrl helper
├── components/SlideVerifyModal/  # vue3-slide-verify modal (shown on repeat failed login)
└── view/login/
    ├── login.vue        # Main login page: auth tabs, layout, locale switcher
    └── components/      # Per-auth-type login forms and MFA components
        ├── Password.vue, LDAP.vue, AD.vue, OAuth.vue, SSO.vue
        ├── IAM.vue, IDaaS.vue, QYWX.vue, DingTalk.vue, Feishu.vue
        ├── BindMfa.vue  # Google Authenticator MFA binding wizard
        └── ValiMfa.vue  # MFA code verification
```

### Data Flow

1. **Startup**: `login.vue` calls `getAuthConfig({ auth_type: "all" })` to fetch enabled auth types
2. **Auth type selection**: User picks a tab → the corresponding component renders inside `<component :is="...">`
3. **Login**: Form component calls `doLogin()` → on success: redirect to `c_url`; on MFA-required: emit `switchLoginMode` with `google_auth_type`
4. **MFA flow**: `start_bind_google_auth` → BindMfa wizard · `bind_google_auth` → BindMfa with cache_token · `verify_google_auth` → ValiMfa code entry
5. **Slide verify**: If a user's previous login for the same username+auth_type failed, a slide-captcha modal is shown before next login attempt

### Build Output & Deployment

Production build outputs to `dist/`:
- `dist/index.html` → copy to `/paas/login/templates/login/`, rename to `login.html`
- `dist/vite-static/` → copy to `/paas/login/static/` (delete existing `vite-static/` first)
- `dist/favicon.ico` → copy to `/paas/login/static/`

The production `base` path is `/login/static/` (configured in `vite.config.js`). The Django backend serves this at runtime via the `login.html` template.

## Technology Notes

### Auto-imports (unplugin)

- **Vue APIs** (`ref`, `computed`, `onMounted`, `nextTick`, `useTemplateRef`, `shallowRef`, etc.) are auto-imported — no need for explicit `import { ref } from 'vue'`
- **Ant Design Vue components** are auto-registered via `unplugin-vue-components` with `AntDesignVueResolver` (icons included)
- The generated eslint globals file is at `.eslintrc-auto-import.json`

### `require()` in ESM

Despite being an ESM project (`"type": "module"`), the codebase uses `require()` for dynamic image/asset imports (e.g., `require("@/assets/verify/1.jpg")`). This is handled by `vite-plugin-require-transform` (for `.js` and `.vue` files) and `vite-plugin-commonjs`. When adding new assets, follow this pattern.

### Path Alias

`@` → `src/` (configured in both Vite and works for imports)

### Styling

- **TailwindCSS 4**: Global via `@import "tailwindcss"` in `style.css`. Use utility classes directly (no `@apply` needed). Prefix with `tw-` if conflicts arise.
- **Ant Design**: Component-level theming via `<a-config-provider>` in `App.vue` (primary color: `#0ba360`). Custom overrides use `:deep()` in scoped Less.
- **Less**: Available for component `<style scoped lang="less">` blocks.

### Axios / Request Layer

- `src/utils/request.js` exports a pre-configured Axios instance with `withCredentials: true`
- Response interceptor checks `response.data.code === 200` for success; otherwise shows `message.warning`
- `showMessage: false` in the per-request config suppresses the automatic warning message
- `createAxiosInstance()` provides a fresh instance with its own `cancelSource` for cancellation scenarios
- Unhandled promise rejections are silently caught via a global `unhandledrejection` listener

### i18n

- Composition API mode (`legacy: false`), fallback to `zh-CN`
- Language persisted in `opsany_language` cookie (values: `chinese_simplified`, `chinese_traditional`, `english`)
- Changing language triggers `window.location.reload()` to refresh the entire page

### Build: Manual Chunks

Rollup `manualChunks` splits third-party deps by package name, with `vue` and `ant-design-vue` kept in the main bundle (not split).

## Relevant Backend Context

- The backend is Django, serving this frontend's `login.html` template
- Template variables `{{auth_type}}` and `{{error}}` are injected into `window.OPS_AUTH_TYPE` and `window.OPS_ERROR` in `index.html`
- API prefix: `login/api/v3/` for auth endpoints
- WeChat Work (企业微信) SSO JS loaded from `rescdn.qqmail.com`
