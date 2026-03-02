<template>
  <v-dialog v-model="dialog" max-width="600" persistent>
    <v-card>
      <v-card-title>
        <span>提交作品</span>
        <v-spacer />
        <v-btn :icon="$globals.icons.close" variant="text" @click="close" />
      </v-card-title>
      <v-card-text>
        <v-form ref="formRef" @submit.prevent="submit">
          <v-file-input
            v-model="imageFile"
            label="上传成品图片"
            accept="image/*"
            :prepend-icon="$globals.icons.fileImage"
            :rules="[rules.required, rules.image]"
            @change="handleImageChange"
          />
          
          <v-img
            v-if="imagePreview"
            :src="imagePreview"
            max-height="300"
            class="mb-4"
            cover
          />
          
          <v-textarea
            v-model="form.notes"
            label="制作心得（可选）"
            rows="4"
            placeholder="分享你的制作过程和感受..."
          />
          
          <v-alert
            v-if="error"
            type="error"
            class="mt-4"
            dismissible
            @click:close="error = null"
          >
            {{ error }}
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="close">取消</v-btn>
        <v-btn
          color="primary"
          :loading="submitting"
          :disabled="!imageFile"
          @click="submit"
        >
          提交
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";

const props = defineProps<{
  modelValue: boolean;
  recipeId: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  submitted: [];
}>();

const api = useUserApi();
const formRef = ref();
const imageFile = ref<File[]>([]);
const imagePreview = ref<string | null>(null);
const submitting = ref(false);
const error = ref<string | null>(null);

const form = reactive({
  notes: "",
});

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const rules = {
  required: (v: any) => !!v || "请上传图片",
  image: (v: File[]) => {
    if (!v || v.length === 0) return true;
    const file = v[0];
    if (!file.type.startsWith("image/")) {
      return "请选择图片文件";
    }
    if (file.size > 10 * 1024 * 1024) {
      return "图片大小不能超过 10MB";
    }
    return true;
  },
};

function handleImageChange() {
  if (imageFile.value && imageFile.value.length > 0) {
    const file = imageFile.value[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  } else {
    imagePreview.value = null;
  }
}

async function submit() {
  if (!formRef.value) return;
  
  const valid = await formRef.value.validate();
  if (!valid.valid) return;
  
  if (!imageFile.value || imageFile.value.length === 0) {
    error.value = "请上传图片";
    return;
  }
  
  submitting.value = true;
  error.value = null;
  
  try {
    // 将图片转换为 base64 编码（临时方案，后续可以改为上传到服务器）
    const file = imageFile.value[0];
    const imageUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target?.result as string;
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    
    // 创建作品记录
    await api.baking.createBakingRecord({
      recipeId: props.recipeId,
      imageUrl,
      notes: form.notes || undefined,
    });
    
    // 重置表单
    imageFile.value = [];
    imagePreview.value = null;
    form.notes = "";
    error.value = null;
    
    emit("submitted");
    if (process.client) {
      window.dispatchEvent(new CustomEvent("baking-work-submitted", {
        detail: { recipeId: props.recipeId },
      }));
    }
    close();
  } catch (err: any) {
    console.error("提交作品失败:", err);
    const detail = err?.response?.data?.detail;
    const errorMessage = detail || err.message || "提交失败，请重试";
    error.value = errorMessage;
    
    // 如果是重复提交的错误，显示特殊提示
    if (errorMessage.includes("已经对该配方提交过作品") || errorMessage.includes("只能提交一次")) {
      error.value = "您已经对该配方提交过作品，每个配方只能提交一次";
    } else if (err?.response?.status === 403) {
      if (typeof detail === "string") {
        error.value = detail;
      } else if (detail && typeof detail === "object" && detail.message) {
        error.value = detail.message;
      } else {
        error.value = "请先完善个人资料（真实姓名、年级、班级、头像）后再提交作品";
      }
    }
  } finally {
    submitting.value = false;
  }
}

function close() {
  dialog.value = false;
}

watch(dialog, (newVal) => {
  if (!newVal) {
    // 关闭时重置表单
    imageFile.value = [];
    imagePreview.value = null;
    form.notes = "";
    error.value = null;
  }
});
</script>
