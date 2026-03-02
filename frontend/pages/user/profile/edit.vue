<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <div class="d-flex flex-column align-center justify-center">
          <UserAvatar
            :key="avatarRefreshKey"
            :tooltip="false"
            size="96"
            :user-id="userCopy.id!"
          />
          <AppButtonUpload
            v-if="userCopy.id"
            class="my-1"
            file-name="profile"
            accept="image/*"
            :url="`/api/users/${userCopy.id}/image`"
            @uploaded="onAvatarUploaded"
          />
        </div>
      </template>
      <template #title>
        {{ $t("profile.user-settings") }}
      </template>
    </BasePageTitle>

    <section class="mt-5">
      <ToggleState tag="article">
        <template #activator="{ toggle, state }">
          <v-btn
            v-if="!state && $appInfo.allowPasswordLogin"
            color="info"
            class="mt-2 mb-n3"
            @click="toggle"
          >
            <v-icon start>
              {{ $globals.icons.lock }}
            </v-icon>
            {{ $t("settings.change-password") }}
          </v-btn>
          <v-btn
            v-else-if="$appInfo.allowPasswordLogin"
            color="info"
            class="mt-2 mb-n3"
            @click="toggle"
          >
            <v-icon start>
              {{ $globals.icons.user }}
            </v-icon>
            {{ $t("settings.profile") }}
          </v-btn>
        </template>
        <template #default="{ state }">
          <v-slide-x-transition
            leave-absolute
            hide-on-leave
          >
            <div
              v-if="!state"
              key="personal-info"
            >
              <BaseCardSectionTitle
                class="mt-10"
                :title="$t('profile.personal-information')"
              />
              <v-card
                tag="article"
                variant="outlined"
                style="border-color: lightgrey;"
              >
                <v-card-text class="pb-0">
                  <v-form ref="userUpdate">
                    <v-text-field
                      v-model="userCopy.username"
                      :label="$t('user.username')"
                      required
                      validate-on="blur"
                      density="comfortable"
                      variant="underlined"
                    />
                    <v-text-field
                      v-model="userCopy.fullName"
                      :label="$t('user.full-name')"
                      :disabled="locks.fullName"
                      required
                      validate-on="blur"
                      density="comfortable"
                      variant="underlined"
                      :hint="locks.fullName ? '全名已锁定，不可修改' : undefined"
                      persistent-hint
                    />
                    <v-text-field
                      v-model="userCopy.email"
                      :label="$t('user.email')"
                      validate-on="blur"
                      required
                      density="comfortable"
                      variant="underlined"
                    />
                    <v-text-field
                      v-if="isAdmin"
                      :model-value="adminGrade"
                      label="年级"
                      density="comfortable"
                      variant="underlined"
                      disabled
                      hint="管理员固定为该值"
                      persistent-hint
                    />
                    <v-select
                      v-else
                      v-model="profileExtra.grade"
                      :items="gradeOptions"
                      label="年级"
                      :disabled="locks.grade"
                      density="comfortable"
                      variant="underlined"
                      required
                      :hint="locks.grade ? '年级已锁定，仅允许修改一次' : undefined"
                      persistent-hint
                    />
                    <v-text-field
                      v-if="isAdmin"
                      :model-value="adminClassName"
                      label="班级"
                      density="comfortable"
                      variant="underlined"
                      disabled
                      hint="管理员固定为该值"
                      persistent-hint
                    />
                    <v-select
                      v-else
                      v-model="profileExtra.className"
                      :items="classOptions"
                      label="班级"
                      :disabled="locks.className"
                      density="comfortable"
                      variant="underlined"
                      required
                      :hint="locks.className ? '班级已锁定，仅允许修改一次' : undefined"
                      persistent-hint
                    />
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <BaseButton
                    update
                    @click="updateUser"
                  />
                </v-card-actions>
              </v-card>
            </div>
            <div
              v-else
              key="change-password"
            >
              <BaseCardSectionTitle
                class="mt-10"
                :title="$t('settings.change-password')"
              />
              <v-card variant="outlined" style="border-color: lightgrey;">
                <v-card-text class="pb-0">
                  <v-form ref="passChange">
                    <v-text-field
                      v-model="password.current"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.current-password')"
                      validate-on="blur"
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      :rules="[validators.minLength(1)]"
                      density="comfortable"
                      variant="underlined"
                      @click:append="showPassword = !showPassword"
                    />
                    <v-text-field
                      v-model="password.newOne"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.new-password')"
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      :rules="[validators.minLength(8)]"
                      density="comfortable"
                      variant="underlined"
                      @click:append="showPassword = !showPassword"
                    />
                    <v-text-field
                      v-model="password.newTwo"
                      :prepend-icon="$globals.icons.lock"
                      :label="$t('user.confirm-password')"
                      :rules="[password.newOne === password.newTwo || $t('user.password-must-match')]"
                      validate-on="blur"
                      :type="showPassword ? 'text' : 'password'"
                      :append-icon="showPassword ? $globals.icons.eye : $globals.icons.eyeOff"
                      density="comfortable"
                      variant="underlined"
                      @click:append="showPassword = !showPassword"
                    />
                    <UserPasswordStrength v-model="password.newOne" />
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <BaseButton
                    update
                    :disabled="!passwordsMatch || password.current.length < 0"
                    @click="updatePassword"
                  />
                </v-card-actions>
              </v-card>
            </div>
          </v-slide-x-transition>
        </template>
      </ToggleState>
    </section>
    <section>
      <BaseCardSectionTitle
        v-if="!isStudent"
        class="mt-10"
        :title="$t('profile.preferences')"
      />
      <v-card v-if="!isStudent" variant="outlined" style="border-color: lightgrey;">
        <v-card-text>
          <v-combobox
            v-model="selectedDefaultActivity"
            :label="$t('user.default-activity')"
            :items="activityOptions"
            :hint="$t('user.default-activity-hint')"
            density="comfortable"
            variant="underlined"
            validate-on="blur"
            persistent-hint
          />
          <v-checkbox
            v-model="userCopy.advanced"
            :label="$t('profile.show-advanced-description')"
            color="primary"
            @change="updateUser"
          />
        </v-card-text>
      </v-card>
      <nuxt-link
        v-if="!isStudent && isAdmin"
        class="mt-5 d-flex flex-column justify-center text-center"
        :to="`/group`"
      > {{
        $t('profile.looking-for-privacy-settings') }} </nuxt-link>
      <div class="d-flex flex-wrap justify-center mt-5">
        <v-btn
          variant="outlined"
          class="rounded-xl my-1 mx-1"
          :to="`/user/profile`"
          nuxt
          exact
        >
          <v-icon start>
            {{ $globals.icons.backArrow }}
          </v-icon>
          {{ $t('profile.back-to-profile') }}
        </v-btn>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";
import UserPasswordStrength from "~/components/Domain/User/UserPasswordStrength.vue";
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";
import { useUserActivityPreferences } from "~/composables/use-users/preferences";
import useDefaultActivity from "~/composables/use-default-activity";
import { ActivityKey } from "~/lib/api/types/activity";
import { alert } from "~/composables/use-toast";

export default defineNuxtComponent({
  components: {
    UserAvatar,
    UserPasswordStrength,
  },
  setup() {
    const i18n = useI18n();
    const auth = useMealieAuth();
    const { getDefaultActivityLabels, getActivityLabel, getActivityKey } = useDefaultActivity();
    const user = computed(() => auth.user.value);
    const isAdmin = computed(() => user.value?.admin === true);
    const isStudent = computed(() => !!user.value && !user.value.admin);

    useSeoMeta({
      title: i18n.t("settings.profile"),
    });

    const activityPreferences = useUserActivityPreferences();
    const activityOptions = getDefaultActivityLabels(i18n);
    const selectedDefaultActivity = ref(getActivityLabel(i18n, activityPreferences.value.defaultActivity));
    watch(selectedDefaultActivity, () => {
      activityPreferences.value.defaultActivity = getActivityKey(i18n, selectedDefaultActivity.value) ?? ActivityKey.RECIPES;
    });

    watch(user, () => {
      userCopy.value = { ...user.value };
    });

    const userCopy = ref({ ...user.value });
    const avatarRefreshKey = ref(0);
    const profileExtra = reactive({
      grade: "",
      className: "",
    });
    const locks = reactive({
      fullName: false,
      grade: false,
      className: false,
    });
    const lockedValues = reactive({
      grade: "",
      className: "",
    });
    const adminGrade = "管理员";
    const adminClassName = "老师";
    const gradeOptions = ["23春", "23秋", "24春", "24秋", "25春", "25秋", "26春", "26秋"];
    const classOptions = ["1班", "2班", "3班", "4班", "5班", "6班", "7班", "普1", "普2", "胖专", "中巴"];

    const api = useUserApi();

    const domUpdatePassword = ref<VForm | null>(null);
    const password = reactive({
      current: "",
      newOne: "",
      newTwo: "",
    });

    const passwordsMatch = computed(() => password.newOne === password.newTwo && password.newOne.length > 0);

    async function updateUser() {
      if (!userCopy.value?.id) return;
      if (locks.fullName && user.value?.fullName) {
        userCopy.value.fullName = user.value.fullName;
      }
      if (locks.grade) {
        profileExtra.grade = lockedValues.grade;
      }
      if (locks.className) {
        profileExtra.className = lockedValues.className;
      }

      if (isAdmin.value) {
        profileExtra.grade = adminGrade;
        profileExtra.className = adminClassName;
      } else {
        if (!gradeOptions.includes(profileExtra.grade)) {
          alert.warning("请选择有效的年级");
          return;
        }
        if (!classOptions.includes(profileExtra.className)) {
          alert.warning("请选择有效的班级");
          return;
        }
      }

      const { response } = await api.users.updateOne(userCopy.value.id, userCopy.value);
      if (response?.status === 200) {
        const className = profileExtra.className.trim();
        await upsertUserDetails();

        // 班级信息同步到 baking 班级接口（兼容已有功能）
        await api.baking.updateMyClass({
          className: className || undefined,
        });
        if (!locks.fullName && (userCopy.value.fullName || "").trim().length > 0) {
          locks.fullName = true;
        }
        if (!isAdmin.value) {
          if (!locks.grade && profileExtra.grade.trim().length > 0) {
            locks.grade = true;
            lockedValues.grade = profileExtra.grade.trim();
          }
          if (!locks.className && profileExtra.className.trim().length > 0) {
            locks.className = true;
            lockedValues.className = profileExtra.className.trim();
          }
        }
        auth.refresh();
        alert.success("个人资料已保存");
      }
    }

    async function upsertUserDetails(avatarUrl?: string) {
      if (!userCopy.value?.id) return;
      const realName = (userCopy.value.fullName || "").trim();
      const grade = (isAdmin.value ? adminGrade : profileExtra.grade).trim();
      const className = (isAdmin.value ? adminClassName : profileExtra.className).trim();
      const fallbackAvatarUrl = api.users.userProfileImage(userCopy.value.id) || undefined;
      const finalAvatarUrl = avatarUrl || fallbackAvatarUrl;

      const updateResult = await api.users.updateSelfDetails({
        realName: realName || undefined,
        grade: grade || undefined,
        className: className || undefined,
        avatarUrl: finalAvatarUrl,
      });
      const updateStatus = updateResult.response?.status ?? updateResult.error?.response?.status;

      if (updateStatus === 200) {
        return;
      }

      // 兼容首次没有 details 记录的场景
      if (updateStatus === 404 && realName && grade && className && finalAvatarUrl) {
        const completeResult = await api.users.completeProfile({
          realName,
          grade,
          className,
          avatarUrl: finalAvatarUrl,
        });
        if (completeResult.response?.status === 201 || completeResult.response?.status === 200) {
          return;
        }
      }

      if (updateStatus === 404) {
        const missingFields = [
          !realName ? "真实姓名" : null,
          !grade ? "年级" : null,
          !className ? "班级" : null,
          !finalAvatarUrl ? "头像" : null,
        ].filter(Boolean);
        if (missingFields.length > 0) {
          throw new Error(`请先完善以下信息：${missingFields.join("、")}`);
        }
      }

      const detail = (updateResult.error as any)?.response?.data?.detail || "资料保存失败";
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    async function onAvatarUploaded(payload: unknown) {
      if (!payload) {
        alert.error("头像上传失败，请重试");
        return;
      }
      if (!userCopy.value?.id) {
        alert.error("未获取到用户信息，请刷新后重试");
        return;
      }
      const avatarUrl = api.users.userProfileImage(userCopy.value.id);
      try {
        // 上传成功后同步 user_details.avatar_url，避免提交作品被“资料未完善”拦截
        await upsertUserDetails(avatarUrl || undefined);
      } catch (error: any) {
        console.error("同步头像到用户资料失败:", error);
        alert.warning(error?.response?.data?.detail || "头像已上传，但资料同步失败，请点击保存资料后重试提交作品");
      }
      avatarRefreshKey.value += 1;
      auth.refresh();
      alert.success("头像上传成功");
    }

    onMounted(async () => {
      try {
        const { data: details } = await api.users.getUserDetails();
        if (details) {
          profileExtra.grade = details.grade || "";
          profileExtra.className = details.className || "";
        }
      } catch {
        // ignore
      }

      if (!profileExtra.className && !isAdmin.value) {
        try {
          const myClass = await api.baking.getMyClass();
          profileExtra.className = myClass?.className || "";
        } catch {
          // ignore
        }
      }
      if (isAdmin.value) {
        profileExtra.grade = adminGrade;
        profileExtra.className = adminClassName;
        locks.grade = true;
        locks.className = true;
        lockedValues.grade = adminGrade;
        lockedValues.className = adminClassName;
      } else {
        const gradeValue = (profileExtra.grade || "").trim();
        const classValue = (profileExtra.className || "").trim();
        locks.grade = gradeValue.length > 0;
        locks.className = classValue.length > 0;
        lockedValues.grade = gradeValue;
        lockedValues.className = classValue;
      }
      locks.fullName = (userCopy.value?.fullName || "").trim().length > 0;
    });

    async function updatePassword() {
      if (!userCopy.value?.id) {
        return;
      }
      const { response } = await api.users.changePassword({
        currentPassword: password.current,
        newPassword: password.newOne,
      });

      if (response?.status === 200) {
        console.log("Password Changed");
      }
    }

    const state = reactive({
      hideImage: false,
      passwordLoading: false,
      showPassword: false,
      loading: false,
    });

    return {
      ...toRefs(state),
      updateUser,
      updatePassword,
      userCopy,
      profileExtra,
      locks,
      adminGrade,
      adminClassName,
      gradeOptions,
      classOptions,
      avatarRefreshKey,
      onAvatarUploaded,
      selectedDefaultActivity,
      activityOptions,
      password,
      domUpdatePassword,
      passwordsMatch,
      validators,
      auth,
      isAdmin,
      isStudent,
    };
  },
});
</script>
