import { createI18n } from 'vue-i18n'
import { messages } from '@/locales'
import { useI18nCookie } from '@/hooks/useI18nCookie'

export function setupI18n() {
	const { locale } = useI18nCookie()

	const i18n = createI18n({
		legacy: false,           // Composition API 模式
		locale: locale.value,
		fallbackLocale: 'zh-CN',
		messages
	})

	//初始同步
	i18n.global.locale.value = locale.value

	return i18n
}