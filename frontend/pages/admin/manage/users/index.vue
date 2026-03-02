<template>
  <v-container fluid>
    <UserInviteDialog v-model="inviteDialog" />
    <BaseDialog
      v-model="deleteDialog"
      :title="$t('general.confirm')"
      color="error"
      can-confirm
      @confirm="deleteUser(deleteTargetId)"
    >
      <template #activator />

      <v-card-text>
        <v-alert
          v-if="isUserOwnAccount"
          type="warning"
          :text="$t('general.confirm-delete-own-admin-account')"
          variant="outlined"
        />
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$t('user.user-management')" />
    <section>
      <v-toolbar
        color="transparent"
        flat
        class="justify-between"
      >
        <BaseButton
          to="/admin/manage/users/create"
          class="mr-2"
        >
          {{ $t("general.create") }}
        </BaseButton>
        <BaseButton
          v-if="$appInfo.allowPasswordLogin"
          class="mr-2"
          color="info"
          :icon="$globals.icons.link"
          @click="inviteDialog = true"
        >
          {{ $t("group.invite") }}
        </BaseButton>

        <BaseOverflowButton
          mode="event"
          variant="elevated"
          :items="ACTIONS_OPTIONS"
          @unlock-all-users="unlockAllUsers"
        />
      </v-toolbar>
      <v-data-table
        :headers="headers"
        :items="tableUsers || []"
        item-key="id"
        class="elevation-0"
        elevation="0"
        :items-per-page="-1"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="($event, { item }) => handleRowClick(item)"
      >
        <template #[`item.admin`]="{ item }">
          <v-icon
            end
            :color="item.admin ? 'success' : undefined"
          >
            {{ item.admin ? $globals.icons.checkboxMarkedCircle : $globals.icons.windowClose }}
          </v-icon>
        </template>
        <template #[`item.actions`]="{ item }">
          <v-btn
            icon
            :disabled="+item.id == 1"
            color="error"
            variant="text"
            @click.stop="
              deleteDialog = true;
              deleteTargetId = item.id;
            "
          >
            <v-icon>
              {{ $globals.icons.delete }}
            </v-icon>
          </v-btn>
        </template>
      </v-data-table>
      <v-divider />
    </section>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi, useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useUser, useAllUsers } from "~/composables/use-user";
import type { UserOut } from "~/lib/api/types/user";
import UserInviteDialog from "~/components/Domain/User/UserInviteDialog.vue";

export default defineNuxtComponent({
  components: {
    UserInviteDialog,
  },
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const api = useAdminApi();
    const userApi = useUserApi();
    const refUserDialog = ref();
    const inviteDialog = ref();
    const auth = useMealieAuth();

    const user = computed(() => auth.user.value);

    const i18n = useI18n();
    const { $globals } = useNuxtApp();

    const router = useRouter();

    const isUserOwnAccount = computed(() => {
      return state.deleteTargetId === user.value?.id;
    });

    const ACTIONS_OPTIONS = [
      {
        text: i18n.t("user.reset-locked-users"),
        icon: $globals.icons.lock,
        event: "unlock-all-users",
      },
    ];

    const state = reactive({
      deleteDialog: false,
      deleteTargetId: "",
      search: "",
      groups: [],
      households: [],
      sendTo: "",
    });
    const userDetailsMap = ref<Record<string, { grade: string; className: string }>>({});
    const userExperienceMap = ref<Record<string, number>>({});

    const { users, refreshAllUsers } = useAllUsers();
    const { loading, deleteUser: deleteUserMixin } = useUser(refreshAllUsers);

    async function loadUserDetailsForTable() {
      const list = users.value || [];
      const entries = await Promise.all(
        list.map(async (u) => {
          try {
            const { data } = await userApi.users.getUserDetailsAdmin(u.id);
            return [
              u.id,
              {
                grade: data?.grade || "-",
                className: data?.className || "-",
              },
            ] as const;
          } catch {
            return [
              u.id,
              {
                grade: "-",
                className: "-",
              },
            ] as const;
          }
        }),
      );
      userDetailsMap.value = Object.fromEntries(entries);
    }

    async function loadUserExperienceForTable() {
      const list = users.value || [];
      if (!list.length) {
        userExperienceMap.value = {};
        return;
      }

      try {
        const result = await userApi.baking.getUsersExperience(list.map(u => u.id));
        userExperienceMap.value = Object.fromEntries(
          (result.items || []).map(item => [item.userId, item.totalExp ?? 1]),
        );
      } catch {
        userExperienceMap.value = Object.fromEntries(list.map(u => [u.id, 1]));
      }
    }

    function deleteUser(id: string) {
      deleteUserMixin(id);

      if (isUserOwnAccount.value) {
        auth.refresh();
      }
    }

    function handleRowClick(item: UserOut) {
      router.push(`/admin/manage/users/${item.id}`);
    }

    // ==========================================================
    // Constants / Non-reactive

    const headers = [
      {
        title: i18n.t("user.user-id"),
        align: "start",
        value: "id",
      },
      { title: i18n.t("user.username"), value: "username" },
      { title: i18n.t("user.full-name"), value: "fullName" },
      { title: i18n.t("user.email"), value: "email" },
      { title: "年级", value: "grade" },
      { title: "班级", value: "className" },
      { title: "经验值", value: "totalExp" },
      { title: i18n.t("group.group"), value: "group" },
      { title: i18n.t("household.household"), value: "household" },
      { title: i18n.t("user.auth-method"), value: "authMethod" },
      { title: i18n.t("user.admin"), value: "admin" },
      { title: i18n.t("general.delete"), value: "actions", sortable: false, align: "center" },
    ];

    const tableUsers = computed(() => {
      const list = users.value || [];
      return list.map(u => ({
        ...u,
        grade: userDetailsMap.value[u.id]?.grade || "-",
        className: userDetailsMap.value[u.id]?.className || "-",
        totalExp: userExperienceMap.value[u.id] ?? 1,
      }));
    });

    async function unlockAllUsers(): Promise<void> {
      const { data } = await api.users.unlockAllUsers(true);

      if (data) {
        const unlocked = data.unlocked ?? 0;

        alert.success(`${unlocked} user(s) unlocked`);
        refreshAllUsers();
      }
    }

    useSeoMeta({
      title: i18n.t("sidebar.manage-users"),
    });

    watch(
      () => users.value,
      () => {
        loadUserDetailsForTable();
        loadUserExperienceForTable();
      },
      { immediate: true },
    );

    return {
      isUserOwnAccount,
      unlockAllUsers,
      ...toRefs(state),
      headers,
      deleteUser,
      loading,
      refUserDialog,
      inviteDialog,
      users,
      tableUsers,
      user,
      handleRowClick,
      ACTIONS_OPTIONS,
    };
  },
  head() {
    return {
      title: useI18n().t("sidebar.manage-users"),
    };
  },
});
</script>
