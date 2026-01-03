<template>
	<div class="mt-4">
		<a-alert v-if="loginErrorMsg" class="mt-1! mb-4!" type="warning" show-icon :message="loginErrorMsg" />
		<a-form name="loginForm" :model="formData" :rules="formDataRules" @finish="onFinish">
			<a-form-item name="domain">
				<a-select name="organization" autocomplete="organization" v-model:value="formData.domain" :placeholder="$t('login_domain_pl')">
					<a-select-option v-for="item in authData.account || []" :key="item.domain" :value="item.domain">
						{{ item.domain }}
					</a-select-option>
				</a-select>
				<GlobalOutlined class="text-[#8b8b8b]! select_icon" />
			</a-form-item>
			<a-form-item name="username">
				<a-input
					class="py-1.5!"
					name="username"
					autocomplete="username"
					v-model:value.trim="formData.username"
					:placeholder="$t('login_username_pl')">
					<template #prefix>
						<user-outlined class="text-[#8b8b8b]!" />
					</template>
				</a-input>
			</a-form-item>
			<a-form-item name="password">
				<a-input-password
					class="py-1.5!"
					name="password"
					autocomplete="current-password"
					v-model:value.trim="formData.password"
					:placeholder="$t('login_pwd_pl')">
					<template #prefix>
						<lock-outlined class="text-[#8b8b8b]!" />
					</template>
				</a-input-password>
			</a-form-item>
			<a-form-item>
				<a-button class="w-full mt-6!" html-type="submit" size="large" type="primary" shape="round" :loading="loading">
					{{ $t("login_btn") }}
				</a-button>
			</a-form-item>
		</a-form>
		<SlideVerifyModal ref="SlideVerifyModalRef" @success="onSuccess"></SlideVerifyModal>
	</div>
</template>

<script setup>
import SlideVerifyModal from "@/components/SlideVerifyModal/index.vue";
import { getAuthConfig, doLogin } from "@/api/login.js";
import config from "@/config/defaultSetting";
import { useStorage, useUrlSearchParams } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { isValidUrl } from "@/utils/util.js";

const { authData } = defineProps({
	authData: {
		type: Object,
		default: () => ({}),
	},
});
const emit = defineEmits(["switchLoginMode"]);
const { t } = useI18n();
const loading = ref(false);
const loginErrorMsg = ref("");
const SlideVerifyModalRef = useTemplateRef("SlideVerifyModalRef");
const storageUserLoginSetting = useStorage("OPS_userLoginSetting", []);
// const storageAccessToken = useStorage("OPS_accessToken", "");
const formData = ref({
	domain: undefined,
	username: "",
	password: "",
});
const formDataRules = ref({
	domain: [{ required: true, message: t("login_domain_pl"), trigger: "change" }],
	username: [{ required: true, message: t("login_username_pl"), trigger: "change" }],
	password: [{ required: true, message: t("login_pwd_pl"), trigger: "change" }],
});
watchEffect(() => {
	if (authData.account && authData.account.length == 1) {
		formData.value.domain = authData.account[0]?.domain;
	}
});

const onFinish = values => {
	try {
		const activeUserLoginSetting = storageUserLoginSetting.value.find(
			item => item.auth_type == authData.auth_type && item.username == formData.value.username && item.domain == formData.value.domain
		);
		const showVerifyCode = activeUserLoginSetting ? activeUserLoginSetting.show_verify_code : false;
		showVerifyCode ? SlideVerifyModalRef.value.showModal() : onSuccess();
	} catch (error) {
		console.log(error);
	}
};
const onSuccess = async () => {
	try {
		loading.value = true;
		const { c_url } = useUrlSearchParams("history");
		const params = {
			...formData.value,
			auth_type: authData.auth_type,
			c_url: c_url,
		};
		const { data = {} } = await doLogin(params, { showMessage: false });
		handleUserLoginSetting(false); //成功登录后,关闭验证
		if (["start_bind_google_auth", "bind_google_auth", "verify_google_auth"].includes(data.google_auth_type)) {
			emit("switchLoginMode", {
				google_auth_type: data.google_auth_type,
				cache_token: data.cache_token,
				google_auth_url: config.baseUrlOfImg + data.google_auth_url,
				google_auth_username: data.google_auth_username,
				secret: data.secret,
				...params,
			});
		} else {
			// storageAccessToken.value = data.access_token;
			// getAuthConfig({ auth_type: "all" });
			const url = isValidUrl(data.c_url) ? data.c_url : config.baseUrl + (data.c_url == "/" ? "" : data.c_url);
			window.location.href = url;
		}
	} catch (error) {
		loginErrorMsg.value = error.message;
		handleUserLoginSetting(error.show_verify_code);
	} finally {
		loading.value = false;
	}
};
const handleUserLoginSetting = show_verify_code => {
	const activeUserLoginSetting = storageUserLoginSetting.value.find(
		item => item.auth_type == authData.auth_type && item.username == formData.value.username && item.domain == formData.value.domain
	);
	if (activeUserLoginSetting) {
		activeUserLoginSetting.show_verify_code = show_verify_code;
	} else {
		storageUserLoginSetting.value.push({
			auth_type: authData.auth_type,
			username: formData.value.username,
			show_verify_code: show_verify_code,
			domain: formData.value.domain,
		});
	}
};

onMounted(() => {
	loginErrorMsg.value = "";
});
</script>
<style scoped lang="less">
.select_icon {
	position: absolute;
	top: 12px;
	left: 12px;
}
:deep(.ant-select-single.ant-select-show-arrow .ant-select-selection-item) {
	padding-left: 20px;
	line-height: 34px;
}
:deep(.ant-select-single:not(.ant-select-customize-input) .ant-select-selector) {
	height: 36px !important;
}
:deep(.ant-select-single .ant-select-selector .ant-select-selection-placeholder) {
	line-height: 36px !important;
	padding-left: 18px;
}
</style>
