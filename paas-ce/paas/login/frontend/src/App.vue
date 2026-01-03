<template>
	<a-config-provider
		:theme="{
			token: {
				colorPrimary: '#0ba360',
				borderRadius: 2,
				colorText: 'rgba(0, 0, 0, 0.7)',
				colorLink: '#0ba360',
				colorLinkHover: '#34cb88',
				colorLinkActive: '#0ca763',
			},
			components: {
				Input: {
					borderRadius: 4,
				},
				Select: {
					borderRadius: 4,
				},
			},
		}">
		<a-app class="tw-h-full">
			<Login></Login>
		</a-app>
	</a-config-provider>
</template>

<script setup>
import Login from "./view/login/login.vue";
import { useTitle } from '@vueuse/core'
import { useI18n } from "vue-i18n";

const { t } = useI18n();
useTitle(t('document_title'));

</script>

<style scoped></style>
