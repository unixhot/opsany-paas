
/**
 * 判断字符串是否为合法的 URL
 * @param {string} string - 需要检测的字符串
 * @returns {boolean} - 如果是合法 URL 返回 true，否则返回 false
 */
export const isValidUrl = (string) => {
	try {
		// new URL() 会尝试解析字符串，如果格式不正确会抛出 TypeError 错误
		new URL(string);
		return true;
	} catch (err) {
		return false;
	}
}