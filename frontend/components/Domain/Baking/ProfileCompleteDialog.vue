<template>
  <v-dialog v-model="dialog" max-width="600" :close-on-content-click="false">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon :icon="$globals.icons.alert" color="warning" class="mr-2" />
        <span>完善个人资料</span>
        <v-spacer />
        <v-btn
          :icon="$globals.icons.close"
          variant="text"
          size="small"
          @click="closeDialog"
        />
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
            :prepend-icon="$globals.icons.user"
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
        <v-btn variant="text" @click="closeDialog">
          暂不完善
        </v-btn>
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
const auth = useMealieAuth();
const formRef = ref();
const avatarFile = ref<File | File[] | null>(null);
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

function closeDialog() {
  dialog.value = false;
}

const missingFields = computed(() => props.checkResult?.missingFields || []);
const fieldNames: Record<string, string> = {
  real_name: "真实姓名",
  grade: "年级",
  class_name: "班级",
  avatar_url: "头像",
};

function getSelectedFile(): File | null {
  if (!avatarFile.value) {
    return null;
  }
  if (Array.isArray(avatarFile.value)) {
    return avatarFile.value[0] || null;
  }
  return avatarFile.value;
}

const canSubmit = computed(() => {
  return (
    form.real_name.trim().length >= 2 &&
    form.grade.trim().length > 0 &&
    form.class_name.trim().length > 0 &&
    !!getSelectedFile()
  );
});

const rules = {
  required: (v: any) => !!v || "此字段为必填项",
  minLength: (v: string) => (v && v.length >= 2) || "至少需要2个字符",
  avatarRequired: () => !!getSelectedFile() || "请上传头像",
};

function handleAvatarChange() {
  const file = getSelectedFile();
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  } else {
    avatarPreview.value = null;
  }
}

async function uploadAvatar(file: File): Promise<string> {
  const userId = auth.user.value?.id;
  if (!userId) {
    throw new Error("未获取到用户信息，请重新登录后重试");
  }

  const formData = new FormData();
  // 与现有个人资料页保持一致，后端按该字段名接收头像文件
  formData.append("profile", file);
  await api.upload.file(`/api/users/${userId}/image`, formData);

  return api.users.userProfileImage(userId) || "";
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
    const file = getSelectedFile();
    if (!file) {
      throw new Error("请上传头像");
    }

    // 先上传头像文件，再将头像地址写入资料详情
    const avatarUrl = await uploadAvatar(file);

    await api.users.completeProfile({
      realName: form.real_name.trim(),
      grade: form.grade.trim(),
      className: form.class_name.trim(),
      avatarUrl,
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
  if (newVal && !newVal.isComplete) {
    // 预填充已有数据
    // 这里可以从 checkResult 中获取已有数据（如果有的话）
  }
}, { immediate: true });
</script>
