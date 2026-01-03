<template>
	<div class="page-content" :style="{ background: 'url(' + config.baseUrlOfImg + 'uploads/login/img/bg_image.png' + ') no-repeat' }">
		<header class="h-[50px] bg-white flex justify-between items-center shadow-sm">
			<img class="h-[50px] ml-[200px]" :src="config.baseUrlOfImg + 'uploads/login/img/bk_login.png'" alt="" />
			<div class="mr-[100px]">
				<a class="text-[#666666]! mr-3" href="/docs/">{{ $t("header_help") }}</a>
				<a-dropdown>
					<a class="text-[#666666]!" @click.prevent>
						{{ menuList.find(item => item.key == locale)?.title }}
						<DownOutlined class="text-xs" />
					</a>
					<template #overlay>
						<a-menu @click="changeLocale">
							<a-menu-item v-for="item in menuList" :key="item.key">
								<div class="flex items-center">
									<img class="w-[18px] h-[18px] mr-1" :src="item.img" :alt="item.title" />
									<span>{{ item.title }}</span>
								</div>
							</a-menu-item>
						</a-menu>
					</template>
				</a-dropdown>
			</div>
		</header>
		<div>
			<div class="ml-[20%]">
				<img class="w-[540px] mt-[11%]" :src="config.baseUrlOfImg + 'uploads/login/img/home_top_word.png'" alt="" />
				<img class="w-[540px] mt-[30px]" :src="config.baseUrlOfImg + 'uploads/login/img/home_page_picture.png'" alt="" />
			</div>
			<div
				v-if="!loginFormData.google_auth_type || ['verify_google_auth'].includes(loginFormData.google_auth_type)"
				class="px-[30px] py-[30px] mt-[6%] shadow-xl rounded-lg bg-white w-[380px] min-h-[390px] absolute top-[12%] left-[57%]">
				<template v-if="loginFormData.google_auth_type == 'verify_google_auth'">
					<ValiMfa :loginFormData="loginFormData" />
				</template>
				<template v-else>
					<div class="text-xl font-bold mb-3 mt-2">
						<a-skeleton-input v-if="loading" :active="true" />
						<div v-else>{{ loginTitle || $t("login_welcome") }}</div>
					</div>
					<a-card :loading="loading" :bordered="false" :bodyStyle="{ padding: 0 }">
						<a-tabs class="mt-2" v-model:activeKey="activeLoginKey" destroyInactiveTabPane>
							<a-tab-pane v-for="item in authList" :key="item.auth_type" :tab="item.auth_show_name">
								<component :is="item.componentKey" :authData="item" @switchLoginMode="switchLoginMode"></component>
							</a-tab-pane>
						</a-tabs>
					</a-card>
				</template>
			</div>
			<div
				v-else-if="['start_bind_google_auth', 'bind_google_auth'].includes(loginFormData.google_auth_type)"
				class="shadow-xl rounded-lg bg-white absolute top-[12%] left-[57%]">
				<BindMfa :loginFormData="loginFormData" />
			</div>
		</div>
	</div>
</template>

<script setup>
import Password from "./components/Password.vue";
import QYWX from "./components/QYWX.vue";
import LDAP from "./components/LDAP.vue";
import SSO from "./components/SSO.vue";
import IDaaS from "./components/IDaaS.vue";
import OAuth from "./components/OAuth.vue";
import AD from "./components/AD.vue";
import IAM from "./components/IAM.vue";
import BindMfa from "./components/BindMfa.vue";
import ValiMfa from "./components/ValiMfa.vue";
import { useUrlSearchParams } from "@vueuse/core";
import { getAuthConfig } from "@/api/login.js";
import config from "@/config/defaultSetting";
import { useI18nCookie } from "@/hooks/useI18nCookie";
import { useCookies } from "@vueuse/integrations/useCookies";

const { locale, setLocale } = useI18nCookie();
const loginTitle = ref("");
const loading = ref(false);
const loginFormData = ref({});
const menuList = ref([
	{ key: "zh-CN", title: "简体中文", img: require("@/assets/zh_CN.png") },
	{ key: "zh-TW", title: "繁體中文", img: require("@/assets/zh_TW.png") },
	{ key: "en", title: "English", img: require("@/assets/en.png") },
]);
const loginTypeList = shallowRef([
	{ title: "密码登录", key: "1", componentKey: Password },
	{ title: "LDAP", key: "2", componentKey: LDAP },
	{ title: "企业微信", key: "3", componentKey: QYWX },
	{ title: "OAuth", key: "6", componentKey: OAuth },
	{ title: "AD", key: "7", componentKey: AD },
	{ title: "SSO", key: "8", componentKey: SSO },
	{ title: "IDaaS", key: "9", componentKey: IDaaS },
	{ title: "IAM", key: "10", componentKey: IAM },
]);
const authList = shallowRef([]);
const activeLoginKey = ref("1");

const getAuthList = async () => {
	try {
		loading.value = true;
		const { data = [] } = await getAuthConfig({ auth_type: "all" });
		data.forEach(item => {
			if (loginTypeList.value.find(i => i.key == item.auth_type)) {
				item.componentKey = loginTypeList.value.find(i => i.key == item.auth_type).componentKey;
			}
		});
		authList.value = data;
		loginTitle.value = data[0] && data[0].title;
		const params = useUrlSearchParams("history");
		const auth_type = params.auth_type;
		if (authList.value.find(i => i.auth_type == auth_type)) return;
		activeLoginKey.value = data[0]?.auth_type || "1";
	} catch (error) {
		console.log(error);
	} finally {
		loading.value = false;
	}
};
const switchLoginMode = val => {
	//google_auth_type:
	//start_bind_google_auth: 开始绑定
	//bind_google_auth: 绑定并登录
	//verify_google_auth: 验证MFA

	loginFormData.value = val;
};
const changeLocale = ({ key }) => {
	setLocale(key);
};
const setDefaultLocale = () => {
	const cookies = useCookies(["opsany_language"]);
	const currentCookie = cookies.get("opsany_language");
	if (!currentCookie) {
		setLocale("zh-CN");
	}
};

onMounted(() => {
	setDefaultLocale();
	const params = useUrlSearchParams("history");
	const auth_type = params.auth_type;
	if (loginTypeList.value.find(i => i.key == auth_type)) {
		activeLoginKey.value = auth_type;
	}
	getAuthList();
});
</script>
<style scoped lang="less">
.page-content {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	overflow: auto;
	background-size: 100% 100% !important;
}

:deep(.ant-tabs-top > .ant-tabs-nav::before),
:deep(.ant-tabs-top > div > .ant-tabs-nav::before) {
	border: none;
}
:deep(.ant-card:not(.ant-card-bordered)) {
	box-shadow: none;
}
:deep(.ant-tabs-tab) {
	padding: 8px 0;
}
</style>
