import en from './en.js'
import zhCN from './zh-CN.js'
import zhTW from './zh-TW.js'

export const messages = {
	en,
	'zh-CN': zhCN,
	'zh-TW': zhTW
}

export const supportedLocales = Object.keys(messages)