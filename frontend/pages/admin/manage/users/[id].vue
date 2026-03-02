<template>
  <v-container
    v-if="user"
    class="narrow-container"
  >
    <BasePageTitle>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          src="/svgs/manage-profile.svg"
        />
      </template>
      <template #title>
        {{ $t("user.admin-user-management") }}
      </template>
      {{ $t("user.changes-reflected-immediately") }}
    </BasePageTitle>
    <AppToolbar back />
    <v-form
      v-if="!userError"
      ref="refNewUserForm"
      @submit.prevent="handleSubmit"
    >
      <v-card
        variant="outlined"
        style="border-color: lightgrey;"
      >
        <v-sheet class="pt-4">
          <v-card-text>
            <div class="d-flex">
              <p> {{ $t("user.user-id-with-value", { id: user.id }) }}</p>
            </div>
            <!-- This is disabled since we can't properly handle changing the user's group in most scenarios -->

            <v-row>
              <v-col cols="6">
                <v-select
                  v-if="groups"
                  v-model="user.group"
                  disabled
                  :items="groups"
                  variant="solo-filled"
                  flat
                  item-title="name"
                  item-value="name"
                  :return-object="false"
                  :label="$t('group.user-group')"
                  :rules="[validators.required]"
                />
              </v-col>
              <v-col cols="6">
                <v-select
                  v-if="households"
                  v-model="user.household"
                  :items="households"
                  variant="solo-filled"
                  flat
                  item-title="name"
                  item-value="name"
                  :return-object="false"
                  :label="$t('household.user-household')"
                  :rules="[validators.required]"
                />
              </v-col>
            </v-row>
            <div class="d-flex py-2 pr-2">
              <BaseButton
                type="button"
                :loading="generatingToken"
                create
                @click.prevent="handlePasswordReset"
              >
                {{ $t("user.generate-password-reset-link") }}
              </BaseButton>
            </div>

            <div
              v-if="resetUrl"
              class="mb-2"
            >
              <v-card-text>
                <p class="text-center pb-0">
                  {{ resetUrl }}
                </p>
              </v-card-text>
              <v-card-actions
                class="align-center pt-0"
                style="gap: 4px"
              >
                <BaseButton
                  cancel
                  @click="resetUrl = ''"
                >
                  {{ $t("general.close") }}
                </BaseButton>
                <v-spacer />
                <BaseButton
                  v-if="user.email"
                  color="info"
                  class="mr-1"
                  @click="sendResetEmail"
                >
                  <template #icon>
                    {{ $globals.icons.email }}
                  </template>
                  {{ $t("user.email") }}
                </BaseButton>
                <AppButtonCopy
                  :icon="false"
                  color="info"
                  :copy-text="resetUrl"
                />
              </v-card-actions>
            </div>

            <AutoForm
              v-model="user"
              :items="userForm"
              update-mode
              :disabled-fields="disabledFields"
            />
            <v-divider class="my-4" />
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="profileExtra.grade"
                  :items="gradeOptions"
                  :disabled="!!user?.admin"
                  label="年级"
                  variant="solo-filled"
                  flat
                  :rules="[validators.required]"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="profileExtra.className"
                  :items="classOptions"
                  :disabled="!!user?.admin"
                  label="班级"
                  variant="solo-filled"
                  flat
                  :rules="[validators.required]"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="experienceValue"
                  type="number"
                  min="1"
                  step="1"
                  label="经验值"
                  variant="solo-filled"
                  flat
                  :rules="[
                    validators.required,
                    v => Number.isInteger(Number(v)) || '经验值必须是整数',
                    v => Number(v) >= 1 || '经验值最小为 1',
                  ]"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-sheet>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton
          type="submit"
          edit
          class="ml-auto"
        >
          {{ $t("general.update") }}
        </BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi, useUserApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";
import { useUserForm } from "~/composables/use-users";
import { validators } from "~/composables/use-validators";
import type { UserOut } from "~/lib/api/types/user";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const { userForm } = useUserForm();
    const { groups } = useGroups();
    const { useHouseholdsInGroup } = useAdminHouseholds();
    const i18n = useI18n();
    const route = useRoute();

    const userId = route.params.id as string;

    // ==============================================
    // New User Form

    const refNewUserForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const user = ref<UserOut | null>(null);
    const profileExtra = reactive({
      grade: "",
      className: "",
    });
    const experienceValue = ref<number>(1);
    const adminGrade = "管理员";
    const adminClassName = "老师";
    const gradeOptions = ["23春", "23秋", "24春", "24秋", "25春", "25秋", "26春", "26秋", adminGrade];
    const classOptions = ["1班", "2班", "3班", "4班", "5班", "6班", "7班", "普1", "普2", "胖专", "中巴", adminClassName];
    const households = useHouseholdsInGroup(computed(() => user.value?.groupId || ""));

    const disabledFields = computed(() => {
      return user.value?.authMethod !== "Mealie" ? ["admin"] : [];
    });

    const userError = ref(false);

    const resetUrl = ref<string | null>(null);
    const generatingToken = ref(false);

    onMounted(async () => {
      const { data, error } = await adminApi.users.getOne(userId);

      if (error?.response?.status === 404) {
        alert.error(i18n.t("user.user-not-found"));
        userError.value = true;
      }

      if (data) {
        user.value = data;
      }

      const detailsResult = await userApi.users.getUserDetailsAdmin(userId);
      if (detailsResult.data) {
        profileExtra.grade = detailsResult.data.grade || "";
        profileExtra.className = detailsResult.data.className || "";
      }
      if (user.value?.admin) {
        profileExtra.grade = adminGrade;
        profileExtra.className = adminClassName;
      }

      const experienceResult = await userApi.baking.getUsersExperience([userId]);
      const currentExp = experienceResult.items?.[0]?.totalExp;
      experienceValue.value = currentExp && currentExp >= 1 ? currentExp : 1;
    });

    async function handleSubmit() {
      if (!refNewUserForm.value?.validate() || user.value === null) return;

      const { response, data } = await adminApi.users.updateOne(user.value.id, user.value);

      if (response?.status === 200 && data) {
        user.value = data;
      }

      if (user.value?.admin) {
        profileExtra.grade = adminGrade;
        profileExtra.className = adminClassName;
      }

      const detailsPayload = {
        grade: profileExtra.grade,
        className: profileExtra.className,
      };
      await userApi.users.updateUserDetailsAdmin(userId, detailsPayload);
      await userApi.baking.updateUserExperience(userId, Number(experienceValue.value) || 1);
      alert.success("用户资料与经验值已更新");
    }

    async function handlePasswordReset() {
      if (user.value === null) return;
      generatingToken.value = true;

      const { response, data } = await adminApi.users.generatePasswordResetToken({ email: user.value.email });

      if (response?.status === 201 && data) {
        const token: string = data.token;
        resetUrl.value = `${window.location.origin}/reset-password/?token=${token}`;
      }

      generatingToken.value = false;
    }

    const userApi = useUserApi();
    async function sendResetEmail() {
      if (!user.value?.email) return;
      const { response } = await userApi.email.sendForgotPassword({ email: user.value.email });
      if (response && response.status === 200) {
        alert.success(i18n.t("profile.email-sent"));
      }
      else {
        alert.error(i18n.t("profile.error-sending-email"));
      }
    }

    watch(
      () => user.value?.admin,
      (isAdmin) => {
        if (isAdmin) {
          profileExtra.grade = adminGrade;
          profileExtra.className = adminClassName;
        }
      },
      { immediate: true },
    );

    return {
      user,
      disabledFields,
      userError,
      userForm,
      refNewUserForm,
      handleSubmit,
      profileExtra,
      experienceValue,
      gradeOptions,
      classOptions,
      groups,
      households,
      validators,
      handlePasswordReset,
      resetUrl,
      generatingToken,
      sendResetEmail,
    };
  },
});
</script>
