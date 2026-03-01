<template>
  <v-dialog v-model="dialog" max-width="600" persistent :close-on-back="false" :close-on-content-click="false">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon color="warning" class="mr-2">mdi-alert</v-icon>
        <span>完善个人资料</span>
      </v-card-title>
      <v-card-text>
        <v-alert type="warning" class="mb-4">
          请完善以下必填信息才能使用社区功能：
          <ul class="mt-2">
            <li v-for="field in missingFields" :key="field">
              {{ fieldNames[field] || field }}
            </li>
          </ul>
        </v-alert>
        
        <v-form ref="formRef" @submit.prevent="submit">
          <v-text-field
            v-model="form.real_name"
            label="真实姓名 *"
            :rules="[rules.required, rules.minLength]"
            hint="请输入真实姓名，不允许使用昵称或假名"
            persistent-hint
          />
          
          <v-text-field
            v-model="form.grade"
            label="年级 *"
            :rules="[rules.required]"
            hint="如：2024级"
            persistent-hint
          />
          
          <v-text-field
            v-model="form.class_name"
            label="班级 *"
            :rules="[rules.required]"
            hint="如：烘焙1班"
            persistent-hint
          />
          
          <v-file-input
            v-model="avatarFile"
            label="上传头像 *"
            accept="image/*"
            prepend-icon="mdi-account"
            :rules="[rules.avatarRequired]"
            @change="handleAvatarChange"
          />
          
          <v-avatar v-if="avatarPreview" size="100" class="mt-2">
            <v-img :src="avatarPreview" />
          </v-avatar>
          
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
        <v-btn
          color="primary"
          :loading="submitting"
          :disabled="!canSubmit"
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
import type { UserDetailsCompleteCheck } from "~/lib/api/user/user-details";

const props = defineProps<{
  modelValue: boolean;
  checkResult: UserDetailsCompleteCheck | null;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  completed: [];
}>();

const api = useUserApi();
const formRef = ref();
const avatarFile = ref<File[]>([]);
const avatarPreview = ref<string | null>(null);
const submitting = ref(false);
const error = ref<string | null>(null);

const form = reactive({
  real_name: "",
  grade: "",
  class_name: "",
  avatar_url: "",
});

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const missingFields = computed(() => props.checkResult?.missing_fields || []);
const fieldNames: Record<string, string> = {
  real_name: "真实姓名",
  grade: "年级",
  class_name: "班级",
  avatar_url: "头像",
};

const canSubmit = computed(() => {
  return (
    form.real_name.trim().length >= 2 &&
    form.grade.trim().length > 0 &&
    form.class_name.trim().length > 0 &&
    avatarFile.value.length > 0
  );
});

const rules = {
  required: (v: any) => !!v || "此字段为必填项",
  minLength: (v: string) => (v && v.length >= 2) || "至少需要2个字符",
  avatarRequired: (v: File[]) => (v && v.length > 0) || "请上传头像",
};

function handleAvatarChange() {
  if (avatarFile.value && avatarFile.value.length > 0) {
    const file = avatarFile.value[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  } else {
    avatarPreview.value = null;
  }
}

async function submit() {
  if (!formRef.value) return;
  
  const valid = await formRef.value.validate();
  if (!valid.valid) return;
  
  if (!canSubmit.value) {
    error.value = "请填写所有必填字段";
    return;
  }
  
  submitting.value = true;
  error.value = null;
  
  try {
    // 上传头像
    let avatarUrl = "";
    if (avatarFile.value && avatarFile.value.length > 0) {
      const file = avatarFile.value[0];
      // 转换为 base64（临时方案）
      avatarUrl = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const base64 = e.target?.result as string;
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }
    
    // 完善资料
    await api.users.completeProfile({
      real_name: form.real_name.trim(),
      grade: form.grade.trim(),
      class_name: form.class_name.trim(),
      avatar_url: avatarUrl,
    });
    
    emit("completed");
    dialog.value = false;
  } catch (err: any) {
    console.error("完善资料失败:", err);
    error.value = err.response?.data?.detail || err.message || "提交失败，请重试";
  } finally {
    submitting.value = false;
  }
}

watch(() => props.checkResult, (newVal) => {
  if (newVal && !newVal.is_complete) {
    // 预填充已有数据
    // 这里可以从 checkResult 中获取已有数据（如果有的话）
  }
}, { immediate: true });
</script>
