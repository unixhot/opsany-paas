<template>
	<div>
		<div class="flex flex-col items-center">
			<img src="~@/assets/valimfa.png" alt="" />
			<div class="text-[#888888] my-4 text-[15px]">{{ $t("vali_mfa_title") }}</div>
		</div>
		<div class="text-[#333333] mb-4">
			<div class="text-[15px]">{{ $t("vali_mfa_step1_title") }}</div>
			<div>{{ $t("vali_mfa_step1_content") }}</div>
		</div>
		<div class="text-[#333333] mb-3">
			<div class="text-[15px]">{{ $t("vali_mfa_step2_title") }}</div>
			<div>{{ $t("vali_mfa_step2_content") }}</div>
		</div>
		<div>
			<a-input v-model:value.trim="verify_code" :placeholder="$t('vali_mfa_verify_code_pl')"></a-input>
			<a-checkbox v-if="loginFormData.show_mfa_days" class="mt-4!" v-model:checked="checked">
				{{ $t("vali_mfa_seven_checked") }}
			</a-checkbox>
		</div>
		<div class="mt-4">
			<a-button class="w-full" size="large" type="primary" :loading="loading" @click="handleSubmit">{{ $t("submit") }}</a-button>
			<div class="text-xs text-[#888888] mt-2">{{ $t("vali_mfa_bottom_tip") }}</div>
		</div>
	</div>
</template>

<script setup>
import { message } from "ant-design-vue";
import { doLogin } from "@/api/login.js";
import config from "@/config/defaultSetting";
import { useI18n } from "vue-i18n";

const { loginFormData } = defineProps({
	loginFormData: {
		type: Object,
		default: () => ({}),
	},
});
const { t } = useI18n();
const verify_code = ref(undefined);
const checked = ref(false);
const loading = ref(false);

const handleSubmit = async () => {
	if (!verify_code.value) {
		return message.error(t('vali_mfa_verify_code_pl'));
	}
	const params = {
		...loginFormData,
		verify_code: verify_code.value,
	};
	if (loginFormData.show_mfa_days) {
		params.seven_days_free = checked.value ? 1 : 0;
	}
	params.google_auth_url = undefined;
	try {
		loading.value = true;
		const { data = {} } = await doLogin(params);
		window.location.href = config.baseUrl + (data.c_url == "/" ? "" : data.c_url);
	} catch (error) {
		console.log(error);
	} finally {
		loading.value = false;
	}
};
</script>
<style scoped lang="less"></style>
