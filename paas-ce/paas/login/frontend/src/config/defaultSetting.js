const isDev = import.meta.env.DEV
const code = 'login'
const serverUrl = 'https://192.168.0.111/'


export default {
	code: code,
	title: 'Template',
	isDev,
	isProd: !isDev,
	baseUrl: isDev ? serverUrl : window.location.origin + '/',
	baseUrlOfImg: isDev ? serverUrl : window.location.origin + '/',
}
