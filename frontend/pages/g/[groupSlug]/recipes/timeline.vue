<template>
  <div>
    <BasePageTitle class="mt-n4 pt-8">
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="150"
          src="/svgs/manage-members.svg"
        />
      </template>
      <template #title>
        我的时间轴制作表
      </template>
    </BasePageTitle>
    <v-sheet
      :class="$vuetify.display.smAndDown ? 'pa-0' : 'px-3 py-0'"
      style="background-color: transparent;"
    >
      <RecipeTimeline
        v-if="queryFilter"
        v-model="ready"
        show-recipe-cards
        :query-filter="queryFilter"
      />
    </v-sheet>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import RecipeTimeline from "~/components/Domain/Recipe/RecipeTimeline.vue";

export default defineNuxtComponent({
  components: { RecipeTimeline },
  middleware: ["group-only"],
  setup() {
    const i18n = useI18n();
    const api = useUserApi();
    const ready = ref<boolean>(false);

    useSeoMeta({
      title: "我的时间轴制作表",
    });

    const queryFilter = ref<string>("");
    async function fetchMyTimelineFilter() {
      const { data } = await api.users.getSelf();
      if (data?.id) {
        queryFilter.value = `user_id="${data.id}"`;
      }

      ready.value = true;
    }

    useAsyncData("my-timeline-filter", fetchMyTimelineFilter);

    return {
      queryFilter,
      ready,
    };
  },
});
</script>
