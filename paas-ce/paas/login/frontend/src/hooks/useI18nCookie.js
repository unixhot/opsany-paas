import { useCookies } from '@vueuse/integrations/useCookies'
import { computed } from 'vue'
import { supportedLocales } from '@/locales'

const COOKIE_NAME = 'opsany_language'
const DEFAULT_LANG = 'zh-CN'
const COOKIE_LANG_LIST = [
	{ key: 'chinese_simplified', value: 'zh-CN' },
	{ key: 'chinese_traditional', value: 'zh-TW' },
	{ key: 'english', value: 'en' }
]

export function useI18nCookie() {
	const cookies = useCookies(COOKIE_NAME)

	const cleanLegacyCookies = () => {
		const currentPath = window.location.pathname // 例如: "/login/"

		// 如果当前本身就是根路径，就没必要清理了，直接覆盖即可
		if (currentPath === '/') return

		const pathsToClean = [
			currentPath,                      // 情况 A: 比如 "/login/"
			currentPath.replace(/\/$/, ''),   // 情况 B: 去掉末尾斜杠，变成 "/login"
			currentPath + '/'                 // 情况 C: 加上末尾斜杠 (防止获取到的是无斜杠版本)
		]

		// 去重（防止 A 和 C 是一样的）
		const uniquePaths = [...new Set(pathsToClean)]

		uniquePaths.forEach(p => {
			// 只有当路径不为空且不是根路径时才删，防止误删全局配置
			if (p && p !== '/') {
				// 这里的 remove 不会报错，即使 cookie 不存在也只是操作无效
				cookies.remove(COOKIE_NAME, { path: p })
			}
		})
	}

	const locale = computed({
		get() {
			const val = cookies.get(COOKIE_NAME)
			return COOKIE_LANG_LIST.find(item => item.key === val)?.value || DEFAULT_LANG
		},
		set(val) {
			const cookieVal = COOKIE_LANG_LIST.find(item => item.value === val)?.key
			cleanLegacyCookies()

			// --- 设置过期时间为 1 天 ---
			const date = new Date()
			date.setDate(date.getDate() + 7)

			cookies.set(COOKIE_NAME, cookieVal, { path: '/', expires: date })
		}
	})

	return {
		locale,
		setLocale: (lang) => {
			if (supportedLocales.includes(lang)) {
				locale.value = lang
				window.location.reload()
			}
		}
	}
}