<template>
  <v-container :class="isMobile ? 'px-2' : ''">
    <BasePageTitle title="我的作品空间" />

    <v-card class="mb-4">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="8">
            <v-text-field
              v-model="keyword"
              clearable
              variant="outlined"
              density="compact"
              prepend-inner-icon="$globals.icons.magnify"
              label="搜索我的作品（配方名/简介/心得）"
              @click:clear="keyword = ''"
            />
          </v-col>
          <v-col cols="12" md="4" class="d-flex justify-end">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="排序"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-row v-if="loading">
      <v-col v-for="idx in 6" :key="idx" :cols="isMobile ? 6 : 12" sm="6" md="4" lg="3">
        <v-skeleton-loader type="image, article" />
      </v-col>
    </v-row>

    <v-row v-else-if="works.length > 0">
      <v-col
        v-for="work in works"
        :key="work.id"
        :cols="isMobile ? (display.width.value < 380 ? 6 : 4) : 12"
        sm="6"
        md="4"
        lg="3"
      >
        <BakingWorkCard
          :work="work"
          :show-vote-actions="false"
          :show-excellent-action="!!auth.user.value?.admin"
          :excellent-loading="markExcellentLoadingId === work.id"
          @mark-excellent="handleMarkExcellent"
        />
      </v-col>
    </v-row>

    <v-card v-else>
      <v-card-text class="text-center py-8 text-medium-emphasis">
        暂无匹配作品
      </v-card-text>
    </v-card>

    <v-pagination
      v-if="pagination.pages > 1"
      v-model="page"
      :length="pagination.pages"
      :total-visible="isMobile ? 5 : 7"
      class="mt-4"
    />
  </v-container>
</template>

<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core";
import { useUserApi } from "~/composables/api/api-client";
import { useMealieAuth } from "~/composables/use-mealie-auth";
import { alert } from "~/composables/use-toast";
import type { BakingRecord } from "~/lib/api/user/baking";
import BakingWorkCard from "~/components/Domain/Baking/BakingWorkCard.vue";

definePageMeta({
  layout: "default",
});

const api = useUserApi();
const auth = useMealieAuth();
const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);

const loading = ref(false);
const works = ref<BakingRecord[]>([]);
const page = ref(1);
const perPage = 12;
const keyword = ref("");
const sortBy = ref("created_at");
const pagination = ref({ total: 0, pages: 0 });
const markExcellentLoadingId = ref("");

const sortOptions = [
  { title: "最新", value: "created_at" },
  { title: "鲜花最多", value: "flower_count" },
  { title: "鸡蛋最多", value: "egg_count" },
];

async function loadMyWorks() {
  if (!auth.user.value?.id) {
    works.value = [];
    pagination.value = { total: 0, pages: 0 };
    return;
  }

  loading.value = true;
  try {
    const result = await api.baking.getBakingRecords({
      userId: auth.user.value.id,
      keyword: keyword.value.trim() || undefined,
      sortBy: sortBy.value,
      order: "desc",
      page: page.value,
      perPage,
    });
    works.value = result.items || [];
    pagination.value = {
      total: result.total || 0,
      pages: result.pages || 0,
    };
  } catch (error) {
    console.error("加载我的作品空间失败:", error);
    works.value = [];
    pagination.value = { total: 0, pages: 0 };
  } finally {
    loading.value = false;
  }
}

async function handleMarkExcellent(workId: string) {
  if (markExcellentLoadingId.value) return;
  const confirmed = window.confirm("确认将该作品设为精华吗？作者将一次性获得 +30 经验。");
  if (!confirmed) return;
  try {
    markExcellentLoadingId.value = workId;
    await api.baking.markBakingRecordExcellent(workId);
    const target = works.value.find(work => work.id === workId);
    if (target) {
      target.isExcellent = true;
    }
    alert.success("已设为精华，作者已获得 +30 经验");
    await loadMyWorks();
  } catch (error: any) {
    console.error("设为精华失败:", error);
    alert.warning(error?.response?.data?.detail || "设为精华失败，请稍后重试");
  } finally {
    markExcellentLoadingId.value = "";
  }
}

const debouncedReload = useDebounceFn(() => {
  page.value = 1;
  loadMyWorks();
}, 300);

watch(keyword, () => {
  debouncedReload();
});

watch(sortBy, () => {
  page.value = 1;
  loadMyWorks();
});

watch(page, () => {
  loadMyWorks();
});

onMounted(() => {
  loadMyWorks();
});
</script>
