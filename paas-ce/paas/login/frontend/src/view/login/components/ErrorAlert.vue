<template>
	<a-alert v-if="message" class="mt-1! mb-4! w-full" type="warning" show-icon>
		<template #message>
			<a-tooltip :title="message">
				<div class="line-clamp-3">{{ message }}</div>
			</a-tooltip>
		</template>
	</a-alert>
</template>
<script setup>
const props = defineProps({
	message: {
		type: String,
		default: "",
	},
});
</script>
