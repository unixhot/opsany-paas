<template>
	<div class="w-full flex items-center flex-col">
		<a-alert
			v-if="async_auth_type == authData.auth_type && async_error_msg"
			class="mt-1! mb-4! w-full"
			type="warning"
			show-icon
			:message="async_error_msg" />
		<img class="mt-6 w-[50px]!" :src="require('@/assets/qywx.png')" :alt="$t('wecom')" />
		<div class="text-lg font-bold mt-3">{{ $t("wecom") }}</div>
		<div class="mt-12 mb-10 w-full">
			<a-button class="w-full" type="primary" size="large" shape="round" @click="visible = true">{{ $t("login_btn") }}</a-button>
		</div>
		<a-modal v-model:open="visible" @ok="visible = false" :footer="null" :bodyStyle="{ padding: 0 }" centered>
			<div v-if="isError" class="text-gray-500 text-center my-20">{{ $t("wecom_err") }}</div>
			<div v-else id="wwlogin" class="mt-4 flex items-center justify-center"></div>
		</a-modal>
	</div>
</template>

<script setup>
import { nextTick, onMounted, ref, watchEffect } from "vue";

const { authData } = defineProps({
	authData: {
		type: Object,
		default: () => ({
			account: [],
		}),
	},
});

const visible = ref(false);
const isError = ref(false);
const async_auth_type = ref("");
const async_error_msg = ref("");
watchEffect(() => {
	if (visible.value) {
		nextTick(() => {
			initQYWX();
		});
	}
});

const initQYWX = () => {
	const data = authData.account[0] || {};
	const { corp_id, agent_id, domain } = data;
	if (!corp_id || !agent_id || !domain) {
		isError.value = true;
		return;
	}
	const url = encodeURIComponent(`${window.location.origin}${window.location.pathname}?auth_type=3&domain=${domain}`);
	window.WwLogin({
		id: "wwlogin",
		appid: corp_id, //企业微信的cropID，在 企业微信管理端->我的企业中查看 -
		agentid: agent_id, //企业微信当前应用ID -
		redirect_uri: url,
	});
};

onMounted(() => {
	async_auth_type.value = window.OPS_AUTH_TYPE;
	async_error_msg.value = window.OPS_ERROR;
});
</script>
<style scoped lang="less"></style>
