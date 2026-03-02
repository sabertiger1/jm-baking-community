<template>
  <v-container>
    <BasePageTitle :title="$t('baking.settings')" />
    
    <!-- 个人资料编辑 -->
    <v-card class="mb-4">
      <v-card-title>个人资料</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveProfile">
          <v-text-field
            v-model="profileForm.realName"
            label="真实姓名 *"
            placeholder="请输入真实姓名"
            prepend-icon="$globals.icons.account"
            :rules="[v => !!v || '真实姓名不能为空']"
            required
          />
          
          <v-text-field
            v-model="profileForm.grade"
            label="年级"
            placeholder="如：2024级"
            prepend-icon="$globals.icons.school"
            class="mt-4"
          />

          <v-text-field
            v-model="profileForm.className"
            label="班级"
            placeholder="如：烘焙1班"
            prepend-icon="$globals.icons.school"
            class="mt-4"
          />

          <!-- 头像上传 -->
          <div class="mt-4">
            <v-label>头像</v-label>
            <div class="d-flex align-center mt-2">
              <v-avatar size="80" class="mr-4">
                <img v-if="profileForm.avatarUrl" :src="profileForm.avatarUrl" />
                <v-icon v-else size="40">$globals.icons.account</v-icon>
              </v-avatar>
              <v-file-input
                v-model="avatarFile"
                label="选择头像"
                accept="image/*"
                prepend-icon="$globals.icons.image"
                @change="handleAvatarChange"
              />
            </div>
          </div>

          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            class="mt-4"
          >
            保存
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 班级和小组信息 -->
    <v-card>
      <v-card-title>班级和小组信息</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveSettings">
          <v-text-field
            v-model="form.className"
            label="班级"
            placeholder="如：2024级烘焙1班"
            prepend-icon="$globals.icons.school"
          />
          
          <v-text-field
            v-model="form.groupName"
            label="小组"
            placeholder="如：第1组"
            prepend-icon="$globals.icons.accountGroup"
            class="mt-4"
          />

          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            class="mt-4"
          >
            保存
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api/api-client";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const loading = ref(false);

const profileForm = reactive({
  realName: "",
  grade: "",
  className: "",
  avatarUrl: "",
});

const form = reactive({
  className: "",
  groupName: "",
});

const avatarFile = ref<File[]>([]);

async function handleAvatarChange() {
  if (avatarFile.value && avatarFile.value.length > 0) {
    const file = avatarFile.value[0];
    // 将图片转换为 base64
    const reader = new FileReader();
    reader.onload = (e) => {
      profileForm.avatarUrl = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

async function loadSettings() {
  try {
    // 加载用户详细资料
    const details = await api.users.getUserDetails();
    if (details) {
      profileForm.realName = details.realName;
      profileForm.grade = details.grade || "";
      profileForm.className = details.className || "";
      profileForm.avatarUrl = details.avatarUrl || "";
    }

    // 加载班级和小组信息
    const myClass = await api.baking.getMyClass();
    if (myClass) {
      form.className = myClass.className || "";
      form.groupName = myClass.groupName || "";
    }
  } catch (error) {
    console.error("加载设置失败:", error);
  }
}

async function saveProfile() {
  loading.value = true;
  try {
    await api.users.updateSelfDetails({
      realName: profileForm.realName,
      grade: profileForm.grade || undefined,
      className: profileForm.className || undefined,
      avatarUrl: profileForm.avatarUrl || undefined,
    });
    // 显示成功提示
  } catch (error) {
    console.error("保存个人资料失败:", error);
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  loading.value = true;
  try {
    await api.baking.updateMyClass({
      className: form.className || undefined,
      groupName: form.groupName || undefined,
    });
    // 显示成功提示
  } catch (error) {
    console.error("保存设置失败:", error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>
