<template>
  <v-app dark :class="{ 'cake-king-app': isCakeKingTheme }">
    <TheSnackbar />

    <AppHeader>
      <v-btn
        icon
        @click.stop="sidebar = !sidebar"
      >
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
    </AppHeader>

    <AppSidebar
      v-model="sidebar"
      absolute
      :top-link="topLinks"
      :user="{ data: true }"
      :secondary-header="$t('sidebar.developer')"
      :secondary-links="developerLinks"
    />

    <v-main>
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";
import AppSidebar from "@/components/Layout/LayoutParts/AppSidebar.vue";
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import type { SidebarLinks } from "~/types/application-types";
import { useGlobalI18n } from "~/composables/use-global-i18n";
import { useCakeKingTheme } from "~/composables/baking/use-cake-king-theme";

const i18n = useGlobalI18n();
const display = useDisplay();
const { $globals } = useNuxtApp();
const { isCakeKingTheme } = useCakeKingTheme();

const sidebar = ref<boolean>(false);
onMounted(() => {
  sidebar.value = display.lgAndUp.value;
});

const topLinks: SidebarLinks = [
  {
    icon: $globals.icons.cog,
    to: "/admin/site-settings",
    title: i18n.t("sidebar.site-settings"),
    restricted: true,
  },

  // {
  //   icon: $globals.icons.chart,
  //   to: "/admin/analytics",
  //   title: "Analytics",
  //   restricted: true,
  // },
  {
    icon: $globals.icons.user,
    to: "/admin/manage/users",
    title: i18n.t("user.users"),
    restricted: true,
  },
  {
    icon: $globals.icons.household,
    to: "/admin/manage/households",
    title: i18n.t("household.households"),
    restricted: true,
  },
  {
    icon: $globals.icons.group,
    to: "/admin/manage/groups",
    title: i18n.t("group.groups"),
    restricted: true,
  },
  {
    icon: $globals.icons.database,
    to: "/admin/backups",
    title: i18n.t("sidebar.backups"),
    restricted: true,
  },
];

const developerLinks: SidebarLinks = [
  {
    icon: $globals.icons.wrench,
    to: "/admin/maintenance",
    title: i18n.t("sidebar.maintenance"),
    restricted: true,
  },
  {
    icon: $globals.icons.robot,
    title: i18n.t("recipe.debug"),
    restricted: true,
    children: [
      {
        icon: $globals.icons.robot,
        to: "/admin/debug/openai",
        title: i18n.t("admin.openai"),
        restricted: true,
      },
      {
        icon: $globals.icons.slotMachine,
        to: "/admin/debug/parser",
        title: i18n.t("sidebar.parser"),
        restricted: true,
      },
    ],
  },
];
</script>

<style>
.cake-king-theme .cake-king-app {
  background:
    radial-gradient(circle at 12% 8%, rgba(255, 216, 102, 0.14), transparent 44%),
    radial-gradient(circle at 86% 2%, rgba(255, 232, 160, 0.12), transparent 48%),
    linear-gradient(180deg, rgba(255, 250, 235, 0.04), rgba(0, 0, 0, 0));
}

.cake-king-theme .v-toolbar,
.cake-king-theme .v-card {
  border-color: rgba(242, 201, 76, 0.32) !important;
  box-shadow: 0 0 0 1px rgba(242, 201, 76, 0.14), 0 6px 20px rgba(242, 201, 76, 0.14);
}
</style>
