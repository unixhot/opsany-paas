<template>
	<div class="w-[580px] min-h-[390px]">
		<header class="px-5 py-3 border-b border-gray-200 flex items-center">
			<span class="font-bold mr-2 text-[15px]">{{ $t("bindmfa_title") }} </span>
			<a-alert class="py-1! text-[12px]! flex-1!" :message="$t('bind_mfa_title_tip')" type="info" show-icon banner />
		</header>
		<div class="px-5 pt-6">
			<a-timeline>
				<a-timeline-item color="green">
					<div class="font-bold">{{ $t("bind_mfa_step1_title") }}</div>
					<div>
						<div class="mt-3 mb-1 text-[#333333]">{{ $t("bind_mfa_step1_action1_title") }}</div>
						<div class="bg-[#f4f7f9] p-3 rounded-sm leading-6">
							<div>{{ $t("bind_mfa_step1_action1_content1") }}</div>
							<div>{{ $t("bind_mfa_step1_action1_content2") }}</div>
							<div>{{ $t("bind_mfa_step1_action1_content3") }}</div>
						</div>
					</div>
					<div>
						<div class="mt-3 mb-1 text-[#333333] flex items-center">
							<div class="mr-1">{{ $t("bind_mfa_step1_action2_title") }}</div>
							<img src="~@/assets/tuijian.png" alt="" />
						</div>
						<div class="bg-[#f4f7f9] p-3 rounded-sm leading-6">
							<div>{{ $t("bind_mfa_step1_action2_content1") }}</div>
							<div>{{ $t("bind_mfa_step1_action2_content2") }}</div>
						</div>
					</div>
				</a-timeline-item>
				<a-timeline-item color="green">
					<div class="font-bold">{{ $t("bind_mfa_step2_title") }}</div>
					<div class="flex items-center py-3">
						<div class="w-[120px]! h-[120px] p-2 mr-4">
							<img class="w-full h-full" :src="loginFormData.google_auth_url" :alt="$t('bind_mfa_step2_qrcode')" />
						</div>
						<div class="flex-1">
							<div class="text-[#666666] mb-1">{{ $t("bind_mfa_step2_content1") }}</div>
							<div class="text-[#666666] mb-1">
								<span class="mr-1">{{ $t("bind_mfa_step2_username") }}</span>
								<span class="text-[#333333]">{{ loginFormData.google_auth_username }}</span>
							</div>
							<div class="text-[#666666] flex">
								<span class="mr-1">{{ $t("bind_mfa_step2_secret") }}</span>
								<div class="flex-1 text-[#333333]">
									<span>{{ loginFormData.secret }}</span>
									<a type="link" size="small" class="font-[12px] ml-2" @click="handleCopy"> {{ $t("bind_mfa_copy") }} </a>
								</div>
							</div>
						</div>
					</div>
				</a-timeline-item>
				<a-timeline-item color="green">
					<div class="flex items-center">
						<div class="font-bold mr-2">{{ $t("bind_mfa_step3_title") }}</div>
						<a-input class="flex-1" :placeholder="$t('bind_mfa_step3_verify_code_pl')" v-model:value="verify_code"></a-input>
					</div>
				</a-timeline-item>
			</a-timeline>
		</div>
		<footer class="px-5 py-3 border-t border-gray-200 text-right">
			<span class="text-[12px] text-gray-600 mr-2">{{ $t("bind_mfa_bottom_tip") }}</span>
			<a-button type="primary" @click="handleClick" :loading="loading">{{ $t("bind_mfa_bottom_bottom") }}</a-button>
		</footer>
	</div>
</template>

<script setup>
import useClipboard from "vue-clipboard3";
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
const verify_code = ref(undefined);
const loading = ref(false);
const { t } = useI18n();
const handleCopy = async () => {
	const { toClipboard } = useClipboard();
	try {
		await toClipboard(loginFormData.secret);
		message.success(t("bind_mfa_copy_success"));
	} catch (error) {
		message.error(t("bind_mfa_copy_fail"));
	}
};
const handleClick = async () => {
	if (!verify_code.value) {
		return message.error(t("bind_mfa_step3_verify_code_pl"));
	}
	const params = {
		...loginFormData,
		verify_code: verify_code.value,
	};
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
