import axios from 'axios';
import config from '@/config/defaultSetting';
import { message, notification } from "ant-design-vue";
import { useStorage, } from "@vueuse/core";

axios.defaults.withCredentials = true; //让ajax携带cookie

const createAxiosInstance = () => {
	const cancelSource = axios.CancelToken.source();

	const request = axios.create({
		baseURL: config.baseUrl,
		// timeout: 5000, // Set a timeout value if needed
		cancelToken: cancelSource.token,
	});

	// 异常拦截处理器
	const errorHandler = (error) => {
		if (error.response) {
			notification.error({
				message: '错误',
				description: error.response.statusText
			})
		}
		return Promise.reject(error)
	}

	// request interceptor
	request.interceptors.request.use(config => {
		// const storageAccessToken = useStorage("OPS_accessToken", "");
		// const token = storageAccessToken.value
		// if (token) {
		// 	config.headers['Authorization'] = 'Bearer ' + token
		// }
		return config
	}, errorHandler)

	// response interceptor
	request.interceptors.response.use((response) => {
		const showMessage = response.config.showMessage == undefined ? true : response.config.showMessage
		const { code } = response.data;
		if (code == 200) {
			return response.data
		} else {
			showMessage && message.warning({
				content: response.data.message
			})
			return Promise.reject(response.data)
		}
	}, errorHandler)

	return {
		request,
		cancelSource
	}
}



window.addEventListener('unhandledrejection', function (event) {
	// 获取事件类型
	const eventType = event.constructor;
	// 检查是否为 PromiseRejectionEvent
	if (eventType === PromiseRejectionEvent) {
		// 阻止默认的Promise错误处理行为
		event.preventDefault();
		// 阻止错误继续传播到全局错误处理机制
		event.stopPropagation();
	}
});
const request = createAxiosInstance().request
export default request;

export {
	request as axios,
	createAxiosInstance
}
