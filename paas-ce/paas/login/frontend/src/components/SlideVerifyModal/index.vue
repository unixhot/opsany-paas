<template>
	<a-modal v-model:open="visible" width="400px" :footer="null" centered @cancel="onCancel">
		<div class="flex justify-around my-4">
			<SlideVerify
				ref="SlideVerifyRef"
				slider-text="滑动滑块验证"
				:imgs="[
					require('@/assets/verify/1.jpg'),
					require('@/assets/verify/2.jpg'),
					require('@/assets/verify/3.jpg'),
					require('@/assets/verify/4.jpg'),
					require('@/assets/verify/5.jpg'),
					require('@/assets/verify/6.jpg'),
					require('@/assets/verify/7.jpg'),
					require('@/assets/verify/8.jpg'),
					require('@/assets/verify/9.jpg'),
					require('@/assets/verify/10.jpg'),
					require('@/assets/verify/11.jpg'),
					require('@/assets/verify/12.jpg'),
				]"
				@success="onSuccess"
				@fail="onFail"></SlideVerify>
		</div>
	</a-modal>
</template>

<script setup>
import SlideVerify from "vue3-slide-verify";
import "vue3-slide-verify/dist/style.css";

const emit = defineEmits(["success", "fail"]);
const visible = ref(false);
const SlideVerifyRef = useTemplateRef("SlideVerifyRef");

const showModal = () => {
	visible.value = true;
	nextTick(() => {
		refresh();
	});
};
const refresh = () => {
	SlideVerifyRef.value.refresh();
};
const onSuccess = () => {
	visible.value = false;
	emit("success");
	refresh();
};
const onFail = () => {
	emit("fail");
};
const onCancel = () => {
	visible.value = false;
	onFail();
};

onMounted(() => {
	nextTick(() => {
		refresh();
	});
});

defineExpose({
	showModal,
	refreshValidate: refresh,
});
</script>
<style scoped lang="less"></style>
