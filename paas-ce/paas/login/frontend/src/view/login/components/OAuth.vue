<template>
	<div class="w-full flex items-center flex-col max-h-[400px] overflow-auto">
		<ErrorAlert v-if="authData.auth_type == async_auth_type" :message="async_error_msg" />
		<template v-if="authData.account.length == 1">
			<div class="w-full overflow-hidden">
				<img class="mt-6 mx-auto w-[50px]!" :src="config.baseUrlOfImg + authData.account[0].auth_icon?.url" alt="" />
				<div class="text-lg font-bold mt-3 truncate text-center" :title="authData.account[0].domain">
					{{ authData.account[0].domain || "--" }}
				</div>
			</div>
			<div class="mt-12 mb-10 w-full">
				<a-button class="w-full" type="primary" size="large" shape="round" @click="handleLogin(authData.account[0])">
					{{ $t("login_btn") }}
				</a-button>
			</div>
		</template>
		<template v-else-if="authData.account.length > 1">
			<div
				v-for="item in authData.account"
				:key="item.id"
				class="w-full flex items-center justify-between bg-[#f5f6f7] px-3 py-2 my-2 rounded-sm">
				<div class="flex items-center flex-1 overflow-hidden">
					<img class="w-6" :src="config.baseUrlOfImg + item.auth_icon?.url" alt="" />
					<span class="flex-1 truncate ml-1.5 mr-2">{{ item.domain || "--" }}</span>
				</div>
				<a-button class="flex! items-center" size="small" type="link" @click="handleLogin(item)"
					>{{ $t("login_btn_sm") }}<ArrowRightOutlined class="text-xs" />
				</a-button>
			</div>
		</template>
		<a-empty v-else class="mt-4"></a-empty>
	</div>
</template>

<script setup>
import { nextTick, onMounted, ref, watchEffect } from "vue";
import config from "@/config/defaultSetting";
import ErrorAlert from "./ErrorAlert.vue";

const { authData } = defineProps({
	authData: {
		type: Object,
		default: () => ({
			account: [],
		}),
	},
});

const async_auth_type = ref("");
const async_error_msg = ref("");

const handleLogin = item => {
	const url = item.auth_login_url;
	window.location.href = url;
};

onMounted(() => {
	async_auth_type.value = window.OPS_AUTH_TYPE;
	async_error_msg.value = window.OPS_ERROR;
});
</script>
<style scoped lang="less"></style>
