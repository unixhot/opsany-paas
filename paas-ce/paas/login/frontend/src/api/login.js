import request, { createAxiosInstance } from '@/utils/request';

//获取列表
//示例代码 示例使用cancelSource
export const getSession = (data = {}, config = { showMessage: true, useCancelToken: false }) => {
	const axiosConfig = { url: "session/", method: "get", params: data }
	const { request: axios, cancelSource } = createAxiosInstance();
	return config.useCancelToken ? {
		request: () => axios(axiosConfig),
		cancelSource
	} : request(axiosConfig)
}


//获取auth列表
export const getAuthConfig = (data = {}) => {
	const axiosConfig = { url: "login/api/v3/auth-config/", method: "get", params: data }
	return request(axiosConfig)
}


//登录接口
export const doLogin = (data = {}, config = { showMessage: true }) => {
	const axiosConfig = { url: "login/api/v3/login/", method: "post", data, ...config }
	return request(axiosConfig)
}

//获取企业微信二维码数据相关
export const getQywx = (data = {}) => {
	const axiosConfig = { url: "login/api/v3/qywx/", method: "get", params: data }
	return request(axiosConfig)
}